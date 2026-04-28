"""
Unit tests for DataCollector class.

Tests cover:
- Successful data fetching
- Error handling and retry logic
- Multiple stock fetching
- Edge cases (invalid symbols, empty data)

Requirements: 1.4
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.data_collector import DataCollector


class TestDataCollector:
    """Test suite for DataCollector class."""
    
    def test_initialization(self):
        """Test DataCollector initialization with default and custom parameters."""
        # Default initialization
        collector = DataCollector()
        assert collector.max_retries == 3
        
        # Custom max_retries
        collector = DataCollector(max_retries=5)
        assert collector.max_retries == 5
    
    @patch('src.data_collector.collector.yf.Ticker')
    def test_fetch_stock_data_success(self, mock_ticker):
        """Test successful stock data fetching."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=5),
            'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'High': [105.0, 106.0, 107.0, 108.0, 109.0],
            'Low': [99.0, 100.0, 101.0, 102.0, 103.0],
            'Close': [102.0, 103.0, 104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000, 1300000, 1400000]
        })
        mock_data = mock_data.set_index('Date')
        
        # Configure mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        collector = DataCollector()
        result = collector.fetch_stock_data(
            'AAPL',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5)
        )
        
        # Assertions
        assert not result.empty
        assert len(result) == 5
        assert list(result.columns) == ['date', 'open', 'high', 'low', 'close', 'volume']
        assert result['close'].iloc[0] == 102.0
        assert result['volume'].iloc[0] == 1000000
    
    @patch('src.data_collector.collector.yf.Ticker')
    def test_fetch_stock_data_empty_response(self, mock_ticker):
        """Test handling of empty data response."""
        # Configure mock to return empty DataFrame
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        collector = DataCollector(max_retries=2)
        result = collector.fetch_stock_data('INVALID')
        
        # Should return empty DataFrame after retries
        assert result.empty
        assert list(result.columns) == ['date', 'open', 'high', 'low', 'close', 'volume']
    
    @patch('src.data_collector.collector.yf.Ticker')
    @patch('src.data_collector.collector.time.sleep')
    def test_fetch_stock_data_retry_logic(self, mock_sleep, mock_ticker):
        """Test retry logic with exponential backoff."""
        # Configure mock to fail twice then succeed
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=1),
                'Open': [100.0],
                'High': [105.0],
                'Low': [99.0],
                'Close': [102.0],
                'Volume': [1000000]
            }).set_index('Date')
        ]
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        collector = DataCollector(max_retries=3)
        result = collector.fetch_stock_data('AAPL')
        
        # Assertions
        assert not result.empty
        assert len(result) == 1
        
        # Verify exponential backoff: 1s, 2s
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # First retry: 2^0 = 1
        mock_sleep.assert_any_call(2)  # Second retry: 2^1 = 2
    
    @patch('src.data_collector.collector.yf.Ticker')
    @patch('src.data_collector.collector.time.sleep')
    def test_fetch_stock_data_all_retries_fail(self, mock_sleep, mock_ticker):
        """Test behavior when all retry attempts fail."""
        # Configure mock to always fail
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = Exception("Persistent error")
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        collector = DataCollector(max_retries=3)
        result = collector.fetch_stock_data('AAPL')
        
        # Should return empty DataFrame
        assert result.empty
        
        # Verify all retries were attempted (3 attempts = 2 sleeps)
        assert mock_sleep.call_count == 2
    
    @patch('src.data_collector.collector.yf.Ticker')
    def test_fetch_stock_data_default_dates(self, mock_ticker):
        """Test that default date range is set correctly (1 year)."""
        mock_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=1),
            'Open': [100.0],
            'High': [105.0],
            'Low': [99.0],
            'Close': [102.0],
            'Volume': [1000000]
        }).set_index('Date')
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Test without providing dates
        collector = DataCollector()
        result = collector.fetch_stock_data('AAPL')
        
        # Verify history was called with dates
        assert mock_ticker_instance.history.called
        call_kwargs = mock_ticker_instance.history.call_args[1]
        assert 'start' in call_kwargs
        assert 'end' in call_kwargs
        
        # Verify date range is approximately 1 year
        start = call_kwargs['start']
        end = call_kwargs['end']
        assert (end - start).days >= 360  # Allow some flexibility
    
    @patch('src.data_collector.collector.yf.Ticker')
    def test_fetch_multiple_stocks_success(self, mock_ticker):
        """Test fetching data for multiple stocks."""
        # Setup mock to return different data for each symbol
        def mock_history(*args, **kwargs):
            return pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=3),
                'Open': [100.0, 101.0, 102.0],
                'High': [105.0, 106.0, 107.0],
                'Low': [99.0, 100.0, 101.0],
                'Close': [102.0, 103.0, 104.0],
                'Volume': [1000000, 1100000, 1200000]
            }).set_index('Date')
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = mock_history
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        collector = DataCollector()
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        results = collector.fetch_multiple_stocks(symbols)
        
        # Assertions
        assert len(results) == 3
        assert all(symbol in results for symbol in symbols)
        assert all(not df.empty for df in results.values())
        assert all(len(df) == 3 for df in results.values())
    
    @patch('src.data_collector.collector.yf.Ticker')
    def test_fetch_multiple_stocks_partial_failure(self, mock_ticker):
        """Test that partial failures don't stop processing of other symbols."""
        # Setup mock to fail for second symbol
        call_count = [0]
        
        def mock_history(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] in [2, 3, 4]:  # Fail for second symbol (3 attempts)
                raise Exception("API error")
            return pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=2),
                'Open': [100.0, 101.0],
                'High': [105.0, 106.0],
                'Low': [99.0, 100.0],
                'Close': [102.0, 103.0],
                'Volume': [1000000, 1100000]
            }).set_index('Date')
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = mock_history
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        collector = DataCollector(max_retries=3)
        symbols = ['AAPL', 'INVALID', 'MSFT']
        results = collector.fetch_multiple_stocks(symbols)
        
        # Assertions
        assert len(results) == 3
        assert not results['AAPL'].empty
        assert results['INVALID'].empty  # Failed symbol
        assert not results['MSFT'].empty
    
    @patch('src.data_collector.collector.yf.Ticker')
    def test_fetch_stock_data_column_mapping(self, mock_ticker):
        """Test that columns are correctly renamed to match schema."""
        mock_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=1),
            'Open': [100.0],
            'High': [105.0],
            'Low': [99.0],
            'Close': [102.0],
            'Volume': [1000000],
            'Dividends': [0.0],  # Extra column that should be filtered out
            'Stock Splits': [0.0]  # Extra column that should be filtered out
        }).set_index('Date')
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        collector = DataCollector()
        result = collector.fetch_stock_data('AAPL')
        
        # Verify only required columns are present
        expected_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        assert list(result.columns) == expected_columns
        
        # Verify data types
        assert result['open'].dtype in [float, 'float64']
        assert result['volume'].dtype in [int, 'int64', float, 'float64']
