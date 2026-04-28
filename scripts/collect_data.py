#!/usr/bin/env python3
"""
End-to-end data collection script for Stock Data Intelligence Dashboard.

This script integrates the data collector, processor, and storage modules to:
1. Fetch stock data from external APIs (yfinance)
2. Clean and process the data
3. Calculate financial metrics (daily return, moving average, volatility)
4. Store processed data in the database

Usage:
    python scripts/collect_data.py

Environment Variables:
    DATABASE_URL: Database connection string (default: sqlite:///./stock_dashboard.db)
    LOG_LEVEL: Logging level (default: INFO)

Requirements: 1.2, 1.4, 18.5
"""

import asyncio
import logging
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_collector.collector import AsyncDataCollector
from src.data_processor.processor import DataProcessor
from src.storage import store_stock_data
from src.models.connection import get_database, init_database

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Default stock symbols to collect (Indian stocks with .NS suffix for NSE)
DEFAULT_SYMBOLS = [
    'RELIANCE.NS',  # Reliance Industries
    'TCS.NS',       # Tata Consultancy Services
    'INFY.NS',      # Infosys
    'HDFCBANK.NS',  # HDFC Bank
    'ICICIBANK.NS', # ICICI Bank
    'HINDUNILVR.NS',# Hindustan Unilever
    'ITC.NS',       # ITC Limited
    'SBIN.NS',      # State Bank of India
    'BHARTIARTL.NS',# Bharti Airtel
    'KOTAKBANK.NS', # Kotak Mahindra Bank
]


async def collect_and_store_data(
    symbols: list[str],
    start_date: date = None,
    end_date: date = None
) -> dict:
    """
    Collect, process, and store stock data for multiple symbols.
    
    This function orchestrates the complete data pipeline:
    1. Fetch data concurrently using AsyncDataCollector
    2. Clean and validate data using DataProcessor
    3. Calculate financial metrics (daily return, moving average, volatility)
    4. Store processed data in database
    
    Args:
        symbols: List of stock symbols to collect
        start_date: Start date for historical data (default: 1 year ago)
        end_date: End date for historical data (default: today)
        
    Returns:
        dict: Summary statistics with keys:
              - 'total_symbols': Total number of symbols processed
              - 'successful': Number of successfully stored symbols
              - 'failed': Number of failed symbols
              - 'details': List of per-symbol results
              
    Requirements: 1.2, 1.4, 18.5
    """
    # Set default date range
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=365)
    
    logger.info(f"Starting data collection for {len(symbols)} symbols")
    logger.info(f"Date range: {start_date} to {end_date}")
    
    # Initialize components
    collector = AsyncDataCollector(max_concurrent=10, max_retries=3)
    processor = DataProcessor()
    
    # Step 1: Fetch data concurrently
    logger.info("Step 1: Fetching stock data from external APIs...")
    raw_data = await collector.fetch_multiple_stocks(symbols, start_date, end_date)
    
    # Step 2: Process and store data for each symbol
    logger.info("Step 2: Processing and storing data...")
    
    summary = {
        'total_symbols': len(symbols),
        'successful': 0,
        'failed': 0,
        'details': []
    }
    
    for symbol, df in raw_data.items():
        symbol_result = {
            'symbol': symbol,
            'status': 'failed',
            'records_fetched': 0,
            'records_stored': 0,
            'error': None
        }
        
        try:
            if df.empty:
                logger.warning(f"✗ {symbol}: No data fetched, skipping")
                symbol_result['error'] = 'No data fetched from API'
                summary['failed'] += 1
                summary['details'].append(symbol_result)
                continue
            
            symbol_result['records_fetched'] = len(df)
            logger.info(f"Processing {symbol}: {len(df)} records fetched")
            
            # Step 2a: Clean data
            clean_df = processor.clean_data(df, symbol)
            
            if clean_df.empty:
                logger.warning(f"✗ {symbol}: All records invalid after cleaning, skipping")
                symbol_result['error'] = 'All records invalid after cleaning'
                summary['failed'] += 1
                summary['details'].append(symbol_result)
                continue
            
            # Step 2b: Calculate daily return
            clean_df = processor.calculate_daily_return(clean_df)
            
            # Step 2c: Calculate 7-day moving average
            clean_df = processor.calculate_moving_average(clean_df, window=7)
            
            # Step 2d: Calculate volatility score
            clean_df = processor.calculate_volatility_score(clean_df, window=30)
            
            # Step 3: Store in database
            storage_result = store_stock_data(symbol, clean_df)
            
            if storage_result['success']:
                symbol_result['status'] = 'success'
                symbol_result['records_stored'] = storage_result['inserted']
                summary['successful'] += 1
                logger.info(
                    f"✓ {symbol}: Successfully stored {storage_result['inserted']} records "
                    f"({storage_result['skipped']} duplicates skipped, "
                    f"{storage_result['failed']} failed)"
                )
            else:
                symbol_result['error'] = f"Storage failed: {storage_result['failed']} records failed"
                summary['failed'] += 1
                logger.error(f"✗ {symbol}: Storage failed")
            
        except Exception as e:
            symbol_result['error'] = str(e)
            summary['failed'] += 1
            logger.error(f"✗ {symbol}: Error during processing: {e}", exc_info=True)
        
        summary['details'].append(symbol_result)
    
    # Log final summary
    logger.info("=" * 80)
    logger.info("DATA COLLECTION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total symbols: {summary['total_symbols']}")
    logger.info(f"Successful: {summary['successful']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(f"Success rate: {summary['successful']/summary['total_symbols']*100:.1f}%")
    logger.info("=" * 80)
    
    # Log per-symbol details
    logger.info("\nPer-symbol details:")
    for detail in summary['details']:
        status_icon = "✓" if detail['status'] == 'success' else "✗"
        logger.info(
            f"{status_icon} {detail['symbol']}: "
            f"fetched={detail['records_fetched']}, "
            f"stored={detail['records_stored']}"
            + (f", error={detail['error']}" if detail['error'] else "")
        )
    
    return summary


def main():
    """
    Main entry point for the data collection script.
    
    This function:
    1. Initializes the database (creates tables if needed)
    2. Runs the async data collection pipeline
    3. Logs summary statistics
    """
    logger.info("=" * 80)
    logger.info("STOCK DATA COLLECTION SCRIPT")
    logger.info("=" * 80)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
        
        # Get symbols from environment variable or use defaults
        symbols_env = os.getenv('STOCK_SYMBOLS')
        if symbols_env:
            symbols = [s.strip() for s in symbols_env.split(',')]
            logger.info(f"Using symbols from environment: {symbols}")
        else:
            symbols = DEFAULT_SYMBOLS
            logger.info(f"Using default symbols: {symbols}")
        
        # Run data collection
        summary = asyncio.run(collect_and_store_data(symbols))
        
        # Exit with appropriate code
        if summary['failed'] == 0:
            logger.info("✓ Data collection completed successfully!")
            sys.exit(0)
        elif summary['successful'] > 0:
            logger.warning(
                f"⚠ Data collection completed with {summary['failed']} failures"
            )
            sys.exit(0)  # Partial success is still acceptable
        else:
            logger.error("✗ Data collection failed for all symbols")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nData collection interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Fatal error during data collection: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
