"""
Unit tests for data processor module.

Tests data cleaning functionality including:
- Missing value handling
- Numeric field validation
- Duplicate removal
- Date format conversion
- Invalid record logging

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
import pandas as pd
from datetime import date
from src.data_processor import DataProcessor


class TestDataProcessor:
    """Test suite for DataProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a DataProcessor instance for testing."""
        return DataProcessor()
    
    def test_clean_data_valid_data(self, processor):
        """Test cleaning with all valid data."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            'open': [100.0, 101.0, 102.0],
            'high': [105.0, 106.0, 107.0],
            'low': [99.0, 100.0, 101.0],
            'close': [103.0, 104.0, 105.0],
            'volume': [1000, 2000, 3000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        assert len(result) == 3
        assert list(result.columns) == ['date', 'open', 'high', 'low', 'close', 'volume']
        assert result['open'].iloc[0] == 100.0
    
    def test_clean_data_removes_duplicates(self, processor):
        """Test that duplicate dates are removed."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 1), date(2024, 1, 2)],
            'open': [100.0, 100.5, 101.0],
            'high': [105.0, 105.5, 106.0],
            'low': [99.0, 99.5, 100.0],
            'close': [103.0, 103.5, 104.0],
            'volume': [1000, 1500, 2000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        # Should keep only first occurrence
        assert len(result) == 2
        assert result['open'].iloc[0] == 100.0  # First duplicate kept
    
    def test_clean_data_handles_missing_values(self, processor):
        """Test forward-fill for missing values."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            'open': [100.0, None, 102.0],
            'high': [105.0, 106.0, 107.0],
            'low': [99.0, 100.0, 101.0],
            'close': [103.0, 104.0, 105.0],
            'volume': [1000, 2000, 3000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        # Missing value should be forward-filled
        assert len(result) == 3
        assert result['open'].iloc[1] == 100.0  # Forward-filled from previous
    
    def test_clean_data_removes_invalid_numeric_values(self, processor):
        """Test that negative and zero values are removed."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)],
            'open': [100.0, -50.0, 102.0, 103.0],
            'high': [105.0, 106.0, 0, 108.0],
            'low': [99.0, 100.0, 101.0, 102.0],
            'close': [103.0, 104.0, 105.0, 106.0],
            'volume': [1000, 2000, 3000, 4000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        # Should remove rows with negative open and zero high
        assert len(result) == 2
        assert result['date'].iloc[0] == date(2024, 1, 1)
        assert result['date'].iloc[1] == date(2024, 1, 4)
    
    def test_clean_data_converts_date_format(self, processor):
        """Test that dates are converted to ISO 8601 format."""
        data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'open': [100.0, 101.0, 102.0],
            'high': [105.0, 106.0, 107.0],
            'low': [99.0, 100.0, 101.0],
            'close': [103.0, 104.0, 105.0],
            'volume': [1000, 2000, 3000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        assert len(result) == 3
        # Check that dates are date objects
        assert isinstance(result['date'].iloc[0], date)
        assert result['date'].iloc[0] == date(2024, 1, 1)
    
    def test_clean_data_removes_integrity_violations(self, processor):
        """Test that records with high < low are removed."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            'open': [100.0, 101.0, 102.0],
            'high': [105.0, 100.0, 107.0],  # Day 2: high < low
            'low': [99.0, 105.0, 101.0],
            'close': [103.0, 104.0, 105.0],
            'volume': [1000, 2000, 3000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        # Should remove row with integrity violation
        assert len(result) == 2
        assert result['date'].iloc[0] == date(2024, 1, 1)
        assert result['date'].iloc[1] == date(2024, 1, 3)
    
    def test_clean_data_empty_dataframe(self, processor):
        """Test handling of empty DataFrame."""
        data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        
        result = processor.clean_data(data, 'TEST')
        
        assert len(result) == 0
        assert list(result.columns) == ['date', 'open', 'high', 'low', 'close', 'volume']
    
    def test_clean_data_sorts_by_date(self, processor):
        """Test that data is sorted by date."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 3), date(2024, 1, 1), date(2024, 1, 2)],
            'open': [102.0, 100.0, 101.0],
            'high': [107.0, 105.0, 106.0],
            'low': [101.0, 99.0, 100.0],
            'close': [105.0, 103.0, 104.0],
            'volume': [3000, 1000, 2000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        assert len(result) == 3
        assert result['date'].iloc[0] == date(2024, 1, 1)
        assert result['date'].iloc[1] == date(2024, 1, 2)
        assert result['date'].iloc[2] == date(2024, 1, 3)


class TestFinancialMetrics:
    """Test suite for financial metrics calculation methods."""
    
    @pytest.fixture
    def processor(self):
        """Create a DataProcessor instance for testing."""
        return DataProcessor()
    
    # Daily Return Tests
    
    def test_calculate_daily_return_basic(self, processor):
        """Test basic daily return calculation."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            'close': [100.0, 105.0, 102.0]
        })
        
        result = processor.calculate_daily_return(data)
        
        assert 'daily_return' in result.columns
        assert pd.isna(result['daily_return'].iloc[0])  # First row should be NaN
        assert result['daily_return'].iloc[1] == pytest.approx(5.0, rel=0.01)  # (105-100)/100 * 100
        assert result['daily_return'].iloc[2] == pytest.approx(-2.857, rel=0.01)  # (102-105)/105 * 100
    
    def test_calculate_daily_return_single_record(self, processor):
        """Test daily return with single record (should have NaN)."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1)],
            'close': [100.0]
        })
        
        result = processor.calculate_daily_return(data)
        
        assert len(result) == 1
        assert pd.isna(result['daily_return'].iloc[0])
    
    def test_calculate_daily_return_empty_dataframe(self, processor):
        """Test daily return with empty DataFrame."""
        data = pd.DataFrame(columns=['date', 'close'])
        
        result = processor.calculate_daily_return(data)
        
        assert 'daily_return' in result.columns
        assert len(result) == 0
    
    def test_calculate_daily_return_missing_close_column(self, processor):
        """Test daily return when close column is missing."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2)],
            'open': [100.0, 101.0]
        })
        
        result = processor.calculate_daily_return(data)
        
        assert 'daily_return' in result.columns
        assert result['daily_return'].iloc[0] is None
    
    def test_calculate_daily_return_negative_change(self, processor):
        """Test daily return with price decrease."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2)],
            'close': [100.0, 90.0]
        })
        
        result = processor.calculate_daily_return(data)
        
        assert result['daily_return'].iloc[1] == pytest.approx(-10.0, rel=0.01)  # (90-100)/100 * 100
    
    def test_calculate_daily_return_no_change(self, processor):
        """Test daily return with no price change."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2)],
            'close': [100.0, 100.0]
        })
        
        result = processor.calculate_daily_return(data)
        
        assert result['daily_return'].iloc[1] == pytest.approx(0.0, rel=0.01)
    
    # Moving Average Tests
    
    def test_calculate_moving_average_basic(self, processor):
        """Test basic 7-day moving average calculation."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 11)],
            'close': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0]
        })
        
        result = processor.calculate_moving_average(data, window=7)
        
        assert 'moving_avg_7d' in result.columns
        # First 6 rows should be NaN (not enough data for 7-day window)
        for i in range(6):
            assert pd.isna(result['moving_avg_7d'].iloc[i])
        # 7th row should be average of first 7 days
        assert result['moving_avg_7d'].iloc[6] == pytest.approx(103.0, rel=0.01)  # (100+101+...+106)/7
        # 8th row should be average of days 2-8
        assert result['moving_avg_7d'].iloc[7] == pytest.approx(104.0, rel=0.01)  # (101+102+...+107)/7
    
    def test_calculate_moving_average_insufficient_data(self, processor):
        """Test moving average with less than window size data."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 6)],
            'close': [100.0, 101.0, 102.0, 103.0, 104.0]
        })
        
        result = processor.calculate_moving_average(data, window=7)
        
        # All rows should be NaN since we have less than 7 days
        assert result['moving_avg_7d'].isna().all()
    
    def test_calculate_moving_average_custom_window(self, processor):
        """Test moving average with custom window size."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 6)],
            'close': [100.0, 102.0, 104.0, 106.0, 108.0]
        })
        
        result = processor.calculate_moving_average(data, window=3)
        
        assert 'moving_avg_7d' in result.columns
        # First 2 rows should be NaN
        assert pd.isna(result['moving_avg_7d'].iloc[0])
        assert pd.isna(result['moving_avg_7d'].iloc[1])
        # 3rd row should be average of first 3 days
        assert result['moving_avg_7d'].iloc[2] == pytest.approx(102.0, rel=0.01)  # (100+102+104)/3
    
    def test_calculate_moving_average_empty_dataframe(self, processor):
        """Test moving average with empty DataFrame."""
        data = pd.DataFrame(columns=['date', 'close'])
        
        result = processor.calculate_moving_average(data, window=7)
        
        assert 'moving_avg_7d' in result.columns
        assert len(result) == 0
    
    def test_calculate_moving_average_missing_close_column(self, processor):
        """Test moving average when close column is missing."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 8)],
            'open': [100.0 + i for i in range(7)]
        })
        
        result = processor.calculate_moving_average(data, window=7)
        
        assert 'moving_avg_7d' in result.columns
        assert result['moving_avg_7d'].iloc[0] is None
    
    # 52-Week Stats Tests
    
    def test_calculate_52_week_stats_basic(self, processor):
        """Test basic 52-week statistics calculation."""
        # Create 365 days of data
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(365)],
            'close': [100.0 + i * 0.5 for i in range(365)]  # Gradually increasing prices
        })
        
        result = processor.calculate_52_week_stats(data)
        
        assert '52_week_high' in result
        assert '52_week_low' in result
        assert 'avg_close' in result
        
        # Should use last 364 days
        assert result['52_week_high'] == pytest.approx(282.0, rel=0.01)  # 100 + 364*0.5
        assert result['52_week_low'] == pytest.approx(100.5, rel=0.01)   # 100 + 1*0.5 (skips first day)
        assert result['avg_close'] is not None
    
    def test_calculate_52_week_stats_less_than_year(self, processor):
        """Test 52-week stats with less than a year of data."""
        # Create 30 days of data
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 31)],
            'close': [100.0 + i for i in range(30)]
        })
        
        result = processor.calculate_52_week_stats(data)
        
        # Should still calculate stats using available data
        assert result['52_week_high'] == pytest.approx(129.0, rel=0.01)
        assert result['52_week_low'] == pytest.approx(100.0, rel=0.01)
        assert result['avg_close'] == pytest.approx(114.5, rel=0.01)
    
    def test_calculate_52_week_stats_empty_dataframe(self, processor):
        """Test 52-week stats with empty DataFrame."""
        data = pd.DataFrame(columns=['date', 'close'])
        
        result = processor.calculate_52_week_stats(data)
        
        assert result['52_week_high'] is None
        assert result['52_week_low'] is None
        assert result['avg_close'] is None
    
    def test_calculate_52_week_stats_missing_close_column(self, processor):
        """Test 52-week stats when close column is missing."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 31)],
            'open': [100.0 + i for i in range(30)]
        })
        
        result = processor.calculate_52_week_stats(data)
        
        assert result['52_week_high'] is None
        assert result['52_week_low'] is None
        assert result['avg_close'] is None
    
    def test_calculate_52_week_stats_single_record(self, processor):
        """Test 52-week stats with single record."""
        data = pd.DataFrame({
            'date': [date(2024, 1, 1)],
            'close': [100.0]
        })
        
        result = processor.calculate_52_week_stats(data)
        
        assert result['52_week_high'] == pytest.approx(100.0, rel=0.01)
        assert result['52_week_low'] == pytest.approx(100.0, rel=0.01)
        assert result['avg_close'] == pytest.approx(100.0, rel=0.01)
    
    def test_calculate_52_week_stats_volatile_prices(self, processor):
        """Test 52-week stats with volatile price movements."""
        # Create data with high volatility
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(100)],
            'close': [100.0 if i % 2 == 0 else 200.0 for i in range(100)]
        })
        
        result = processor.calculate_52_week_stats(data)
        
        assert result['52_week_high'] == pytest.approx(200.0, rel=0.01)
        assert result['52_week_low'] == pytest.approx(100.0, rel=0.01)
        assert result['avg_close'] == pytest.approx(150.0, rel=0.01)
    
    # Volatility Score Tests
    
    def test_calculate_volatility_score_basic(self, processor):
        """Test basic volatility score calculation with 30-day window."""
        # Create 40 days of data with varying returns
        daily_returns = [1.5, -0.8, 2.1, -1.2, 0.5, 1.8, -0.3, 2.5, -1.5, 0.9,
                        1.2, -0.6, 1.9, -1.1, 0.7, 1.6, -0.9, 2.2, -1.3, 0.8,
                        1.4, -0.7, 2.0, -1.0, 0.6, 1.7, -0.4, 2.3, -1.4, 1.0,
                        1.3, -0.5, 2.1, -1.2, 0.8, 1.5, -0.8, 2.4, -1.6, 1.1]
        
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(40)],
            'daily_return': daily_returns
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        assert 'volatility_score' in result.columns
        # First 6 rows should be NaN (need minimum 7 days)
        for i in range(6):
            assert pd.isna(result['volatility_score'].iloc[i])
        # Row 7 onwards should have valid scores
        assert pd.notna(result['volatility_score'].iloc[6])
        # Scores should be between 0 and 100
        valid_scores = result['volatility_score'].dropna()
        assert (valid_scores >= 0).all()
        assert (valid_scores <= 100).all()
    
    def test_calculate_volatility_score_insufficient_data(self, processor):
        """Test volatility score with less than 7 days of data."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 6)],
            'daily_return': [1.5, -0.8, 2.1, -1.2, 0.5]
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        assert 'volatility_score' in result.columns
        # All rows should be None since we have less than 7 days
        assert result['volatility_score'].iloc[0] is None
    
    def test_calculate_volatility_score_exactly_7_days(self, processor):
        """Test volatility score with exactly 7 days of data (minimum)."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 8)],
            'daily_return': [1.5, -0.8, 2.1, -1.2, 0.5, 1.8, -0.3]
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        assert 'volatility_score' in result.columns
        # First 6 rows should be NaN
        for i in range(6):
            assert pd.isna(result['volatility_score'].iloc[i])
        # 7th row should have a valid score
        assert pd.notna(result['volatility_score'].iloc[6])
        assert 0 <= result['volatility_score'].iloc[6] <= 100
    
    def test_calculate_volatility_score_high_volatility(self, processor):
        """Test volatility score with high price fluctuations."""
        # Create data with high volatility (large swings)
        daily_returns = [5.0, -4.5, 6.2, -5.8, 4.9, 5.5, -4.2, 6.8, -5.3, 5.1,
                        5.3, -4.8, 6.0, -5.5, 5.2, 5.7, -4.6, 6.5, -5.1, 5.4,
                        5.6, -4.4, 6.3, -5.6, 5.0, 5.8, -4.7, 6.1, -5.4, 5.5,
                        5.4, -4.9, 6.4, -5.2, 5.3]
        
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(35)],
            'daily_return': daily_returns
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        # High volatility should result in higher scores
        valid_scores = result['volatility_score'].dropna()
        assert len(valid_scores) > 0
        # The maximum score should be 100 (normalized)
        assert valid_scores.max() == pytest.approx(100.0, rel=0.01)
    
    def test_calculate_volatility_score_low_volatility(self, processor):
        """Test volatility score with low price fluctuations."""
        # Create data with low volatility (small changes)
        daily_returns = [0.1, -0.05, 0.08, -0.06, 0.09, 0.07, -0.04, 0.11, -0.08, 0.06,
                        0.08, -0.05, 0.10, -0.07, 0.09, 0.06, -0.04, 0.12, -0.06, 0.07,
                        0.09, -0.05, 0.08, -0.06, 0.10, 0.07, -0.04, 0.11, -0.07, 0.08,
                        0.10, -0.06, 0.09, -0.05, 0.07]
        
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(35)],
            'daily_return': daily_returns
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        # Low volatility should result in lower scores
        valid_scores = result['volatility_score'].dropna()
        assert len(valid_scores) > 0
        # Scores should be relatively low (but still normalized to max=100)
        assert valid_scores.max() == pytest.approx(100.0, rel=0.01)
    
    def test_calculate_volatility_score_custom_window(self, processor):
        """Test volatility score with custom window size."""
        daily_returns = [1.5, -0.8, 2.1, -1.2, 0.5, 1.8, -0.3, 2.5, -1.5, 0.9,
                        1.2, -0.6, 1.9, -1.1, 0.7, 1.6, -0.9, 2.2, -1.3, 0.8]
        
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 21)],
            'daily_return': daily_returns
        })
        
        result = processor.calculate_volatility_score(data, window=10)
        
        assert 'volatility_score' in result.columns
        # First 6 rows should be NaN (minimum 7 days)
        for i in range(6):
            assert pd.isna(result['volatility_score'].iloc[i])
        # Row 7 onwards should have valid scores
        assert pd.notna(result['volatility_score'].iloc[6])
    
    def test_calculate_volatility_score_empty_dataframe(self, processor):
        """Test volatility score with empty DataFrame."""
        data = pd.DataFrame(columns=['date', 'daily_return'])
        
        result = processor.calculate_volatility_score(data, window=30)
        
        assert 'volatility_score' in result.columns
        assert len(result) == 0
    
    def test_calculate_volatility_score_missing_daily_return_column(self, processor):
        """Test volatility score when daily_return column is missing."""
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 31)],
            'close': [100.0 + i for i in range(30)]
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        assert 'volatility_score' in result.columns
        assert result['volatility_score'].iloc[0] is None
    
    def test_calculate_volatility_score_with_nan_returns(self, processor):
        """Test volatility score with NaN values in daily returns."""
        daily_returns = [1.5, None, 2.1, -1.2, 0.5, 1.8, -0.3, 2.5, -1.5, 0.9,
                        1.2, -0.6, 1.9, -1.1, 0.7, 1.6, -0.9, 2.2, -1.3, 0.8,
                        1.4, -0.7, 2.0, -1.0, 0.6, 1.7, -0.4, 2.3, -1.4, 1.0,
                        1.3, -0.5, 2.1, -1.2, 0.8]
        
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(35)],
            'daily_return': daily_returns
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        assert 'volatility_score' in result.columns
        # Should handle NaN values gracefully
        # First row with NaN should not break calculation
        valid_scores = result['volatility_score'].dropna()
        assert len(valid_scores) > 0
    
    def test_calculate_volatility_score_zero_volatility(self, processor):
        """Test volatility score when all returns are identical (zero volatility)."""
        # All returns are the same (no volatility)
        daily_returns = [1.0] * 35
        
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(35)],
            'daily_return': daily_returns
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        assert 'volatility_score' in result.columns
        # When std dev is 0, max_volatility is 0, should return None
        assert result['volatility_score'].iloc[0] is None
    
    def test_calculate_volatility_score_normalization(self, processor):
        """Test that volatility scores are properly normalized to 0-100."""
        # Create data with varying volatility levels
        daily_returns = [1.0, -0.5, 1.5, -1.0, 0.8, 1.2, -0.6, 1.8, -1.2, 0.9,
                        2.0, -1.5, 2.5, -2.0, 1.5, 2.2, -1.8, 2.8, -2.2, 1.8,
                        3.0, -2.5, 3.5, -3.0, 2.5, 3.2, -2.8, 3.8, -3.2, 2.8,
                        4.0, -3.5, 4.5, -4.0, 3.5, 4.2, -3.8, 4.8, -4.2, 3.8]
        
        data = pd.DataFrame({
            'date': [date(2024, 1, 1) + pd.Timedelta(days=i) for i in range(40)],
            'daily_return': daily_returns
        })
        
        result = processor.calculate_volatility_score(data, window=30)
        
        valid_scores = result['volatility_score'].dropna()
        # Maximum score should be exactly 100
        assert valid_scores.max() == pytest.approx(100.0, rel=0.01)
        # All scores should be between 0 and 100
        assert (valid_scores >= 0).all()
        assert (valid_scores <= 100).all()
        # Should have a range of scores (not all the same)
        assert valid_scores.std() > 0
