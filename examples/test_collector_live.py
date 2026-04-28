"""
Live integration test for DataCollector.

This script demonstrates the DataCollector functionality with real API calls.
Run this manually to verify the collector works with actual yfinance API.

Note: This requires internet connection and may take a few seconds to complete.
"""

import logging
from datetime import date, timedelta
from src.data_collector import DataCollector

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_single_stock():
    """Test fetching data for a single stock."""
    logger.info("=" * 60)
    logger.info("Test 1: Fetching single stock (AAPL)")
    logger.info("=" * 60)
    
    collector = DataCollector()
    
    # Fetch last 30 days of data for Apple
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    data = collector.fetch_stock_data('AAPL', start_date, end_date)
    
    if not data.empty:
        logger.info(f"✓ Successfully fetched {len(data)} records for AAPL")
        logger.info(f"Date range: {data['date'].min()} to {data['date'].max()}")
        logger.info(f"Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        logger.info(f"\nFirst 3 records:\n{data.head(3)}")
    else:
        logger.error("✗ Failed to fetch data for AAPL")


def test_multiple_stocks():
    """Test fetching data for multiple stocks."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Fetching multiple stocks")
    logger.info("=" * 60)
    
    collector = DataCollector()
    
    # Fetch data for multiple tech stocks
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    results = collector.fetch_multiple_stocks(symbols, start_date, end_date)
    
    logger.info("\nResults summary:")
    for symbol, data in results.items():
        if not data.empty:
            logger.info(
                f"  ✓ {symbol}: {len(data)} records, "
                f"latest close: ${data['close'].iloc[-1]:.2f}"
            )
        else:
            logger.info(f"  ✗ {symbol}: Failed to fetch data")


def test_indian_stocks():
    """Test fetching data for Indian stocks (NSE)."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Fetching Indian stocks (NSE)")
    logger.info("=" * 60)
    
    collector = DataCollector()
    
    # Fetch data for Indian stocks (add .NS suffix for NSE)
    symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    results = collector.fetch_multiple_stocks(symbols, start_date, end_date)
    
    logger.info("\nResults summary:")
    for symbol, data in results.items():
        if not data.empty:
            logger.info(
                f"  ✓ {symbol}: {len(data)} records, "
                f"latest close: ₹{data['close'].iloc[-1]:.2f}"
            )
        else:
            logger.info(f"  ✗ {symbol}: Failed to fetch data")


def test_error_handling():
    """Test error handling with invalid symbol."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Error handling (invalid symbol)")
    logger.info("=" * 60)
    
    collector = DataCollector(max_retries=2)  # Reduce retries for faster test
    
    # Try to fetch data for an invalid symbol
    data = collector.fetch_stock_data('INVALID_SYMBOL_XYZ')
    
    if data.empty:
        logger.info("✓ Error handling works correctly - returned empty DataFrame")
    else:
        logger.warning("✗ Unexpected: Got data for invalid symbol")


if __name__ == '__main__':
    logger.info("Starting DataCollector live integration tests")
    logger.info("Note: These tests make real API calls and require internet connection\n")
    
    try:
        test_single_stock()
        test_multiple_stocks()
        test_indian_stocks()
        test_error_handling()
        
        logger.info("\n" + "=" * 60)
        logger.info("All tests completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
