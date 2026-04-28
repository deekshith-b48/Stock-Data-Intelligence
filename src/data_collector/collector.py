"""
Data collector module for fetching stock market data from external sources.

This module provides the DataCollector class for fetching stock data using yfinance API
with comprehensive error handling, logging, and retry logic with exponential backoff.

It also provides AsyncDataCollector for concurrent fetching of multiple stocks.

Requirements: 1.1, 1.2, 1.3, 1.4, 18.1, 18.2, 18.3, 18.4, 18.5
"""

import asyncio
import logging
import time
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Collects stock market data from external sources (yfinance API).
    
    Features:
    - Fetch historical stock data for specified date ranges
    - Error handling and logging for API failures
    - Retry logic with exponential backoff (3 attempts: 1s, 2s, 4s)
    - Support for multiple stock symbols
    
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize DataCollector.
        
        Args:
            max_retries: Maximum number of retry attempts for failed requests (default: 3)
        """
        self.max_retries = max_retries
        logger.info(f"DataCollector initialized with max_retries={max_retries}")
    
    def fetch_stock_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch stock data for a given symbol with retry logic and exponential backoff.
        
        This method fetches historical stock data from yfinance API including:
        - Date, Open, High, Low, Close prices
        - Trading Volume
        
        Implements retry logic with exponential backoff:
        - Attempt 1: immediate
        - Attempt 2: wait 1 second
        - Attempt 3: wait 2 seconds
        - Attempt 4: wait 4 seconds (if max_retries > 3)
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS.NS', 'AAPL')
            start_date: Start date for historical data (default: 1 year ago)
            end_date: End date for historical data (default: today)
            
        Returns:
            pd.DataFrame: DataFrame with columns [Date, Open, High, Low, Close, Volume]
                         Returns empty DataFrame if all attempts fail
                         
        Requirements: 1.1, 1.2, 1.3, 1.4
        
        Example:
            >>> collector = DataCollector()
            >>> data = collector.fetch_stock_data('RELIANCE.NS', 
            ...                                    start_date=date(2024, 1, 1),
            ...                                    end_date=date(2024, 12, 31))
            >>> print(data.head())
        """
        # Set default date range if not provided
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        logger.info(
            f"Fetching stock data for {symbol} from {start_date} to {end_date}"
        )
        
        attempt = 0
        last_exception = None
        
        while attempt < self.max_retries:
            try:
                # Fetch data using yfinance
                ticker = yf.Ticker(symbol)
                data = ticker.history(
                    start=start_date,
                    end=end_date,
                    auto_adjust=False  # Keep raw OHLC data
                )
                
                # Check if data was retrieved
                if data.empty:
                    logger.warning(
                        f"No data retrieved for {symbol} (attempt {attempt + 1}/{self.max_retries})"
                    )
                    raise ValueError(f"No data available for symbol {symbol}")
                
                # Reset index to make Date a column
                data = data.reset_index()
                
                # Rename columns to match our schema
                data = data.rename(columns={
                    'Date': 'date',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                
                # Select only required columns
                data = data[['date', 'open', 'high', 'low', 'close', 'volume']]
                
                # Convert date column to date type (remove time component)
                data['date'] = pd.to_datetime(data['date']).dt.date
                
                logger.info(
                    f"Successfully fetched {len(data)} records for {symbol} "
                    f"on attempt {attempt + 1}"
                )
                
                return data
                
            except Exception as e:
                last_exception = e
                attempt += 1
                
                # Log the error with timestamp and source
                error_timestamp = datetime.now().isoformat()
                logger.error(
                    f"Failed to fetch data for {symbol} (attempt {attempt}/{self.max_retries}): "
                    f"{type(e).__name__}: {str(e)} [timestamp: {error_timestamp}, source: yfinance]"
                )
                
                # If not the last attempt, wait with exponential backoff
                if attempt < self.max_retries:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** (attempt - 1)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # All attempts failed
        logger.error(
            f"All {self.max_retries} attempts failed for {symbol}. "
            f"Last error: {type(last_exception).__name__}: {str(last_exception)}"
        )
        
        # Return empty DataFrame to allow processing to continue for other symbols
        return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    
    def fetch_multiple_stocks(
        self,
        symbols: list[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch stock data for multiple symbols sequentially.
        
        This method fetches data for multiple symbols one at a time. If one symbol
        fails after all retries, the method continues processing remaining symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for historical data (default: 1 year ago)
            end_date: End date for historical data (default: today)
            
        Returns:
            dict: Dictionary mapping symbol to DataFrame
                  Failed symbols will have empty DataFrames
                  
        Requirements: 1.2, 1.4
        
        Example:
            >>> collector = DataCollector()
            >>> symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
            >>> results = collector.fetch_multiple_stocks(symbols)
            >>> for symbol, data in results.items():
            ...     print(f"{symbol}: {len(data)} records")
        """
        logger.info(f"Fetching data for {len(symbols)} symbols")
        
        results = {}
        successful = 0
        failed = 0
        
        for symbol in symbols:
            data = self.fetch_stock_data(symbol, start_date, end_date)
            results[symbol] = data
            
            if not data.empty:
                successful += 1
                logger.info(f"✓ {symbol}: {len(data)} records fetched")
            else:
                failed += 1
                logger.warning(f"✗ {symbol}: Failed to fetch data")
        
        logger.info(
            f"Batch fetch complete: {successful} successful, {failed} failed "
            f"out of {len(symbols)} total symbols"
        )
        
        return results


class AsyncDataCollector:
    """
    Asynchronous data collector for concurrent fetching of multiple stock symbols.
    
    Features:
    - Concurrent fetching with semaphore-based rate limiting (max 10 concurrent)
    - Async/await pattern for non-blocking I/O
    - Individual error handling per symbol (failures don't block other symbols)
    - Comprehensive logging of completion status
    
    Requirements: 18.1, 18.2, 18.3, 18.4, 18.5
    """
    
    def __init__(self, max_concurrent: int = 10, max_retries: int = 3):
        """
        Initialize AsyncDataCollector.
        
        Args:
            max_concurrent: Maximum number of concurrent requests (default: 10)
            max_retries: Maximum number of retry attempts for failed requests (default: 3)
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(
            f"AsyncDataCollector initialized with max_concurrent={max_concurrent}, "
            f"max_retries={max_retries}"
        )
    
    async def fetch_stock(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Asynchronously fetch stock data for a single symbol with semaphore control.
        
        This method uses a semaphore to limit concurrent requests and runs the
        synchronous yfinance API call in a thread pool executor to avoid blocking
        the event loop.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS.NS', 'AAPL')
            start_date: Start date for historical data (default: 1 year ago)
            end_date: End date for historical data (default: today)
            
        Returns:
            pd.DataFrame: DataFrame with columns [date, open, high, low, close, volume]
                         Returns empty DataFrame if all attempts fail
                         
        Requirements: 18.1, 18.2, 18.3
        """
        # Set default date range if not provided
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        async with self.semaphore:
            logger.info(
                f"Fetching stock data for {symbol} from {start_date} to {end_date}"
            )
            
            attempt = 0
            last_exception = None
            
            while attempt < self.max_retries:
                try:
                    # Run synchronous yfinance call in executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    ticker = yf.Ticker(symbol)
                    
                    # Execute the blocking yfinance call in a thread pool
                    data = await loop.run_in_executor(
                        None,
                        lambda: ticker.history(
                            start=start_date,
                            end=end_date,
                            auto_adjust=False
                        )
                    )
                    
                    # Check if data was retrieved
                    if data.empty:
                        logger.warning(
                            f"No data retrieved for {symbol} "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        raise ValueError(f"No data available for symbol {symbol}")
                    
                    # Reset index to make Date a column
                    data = data.reset_index()
                    
                    # Rename columns to match our schema
                    data = data.rename(columns={
                        'Date': 'date',
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    })
                    
                    # Select only required columns
                    data = data[['date', 'open', 'high', 'low', 'close', 'volume']]
                    
                    # Convert date column to date type (remove time component)
                    data['date'] = pd.to_datetime(data['date']).dt.date
                    
                    logger.info(
                        f"Successfully fetched {len(data)} records for {symbol} "
                        f"on attempt {attempt + 1}"
                    )
                    
                    return data
                    
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    
                    # Log the error with timestamp and source
                    error_timestamp = datetime.now().isoformat()
                    logger.error(
                        f"Failed to fetch data for {symbol} "
                        f"(attempt {attempt}/{self.max_retries}): "
                        f"{type(e).__name__}: {str(e)} "
                        f"[timestamp: {error_timestamp}, source: yfinance]"
                    )
                    
                    # If not the last attempt, wait with exponential backoff
                    if attempt < self.max_retries:
                        # Exponential backoff: 1s, 2s, 4s
                        wait_time = 2 ** (attempt - 1)
                        logger.info(f"Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
            
            # All attempts failed
            logger.error(
                f"All {self.max_retries} attempts failed for {symbol}. "
                f"Last error: {type(last_exception).__name__}: {str(last_exception)}"
            )
            
            # Return empty DataFrame to allow processing to continue for other symbols
            return pd.DataFrame(
                columns=['date', 'open', 'high', 'low', 'close', 'volume']
            )
    
    async def fetch_multiple_stocks(
        self,
        symbols: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Asynchronously fetch stock data for multiple symbols concurrently.
        
        This method uses asyncio.gather to fetch data for all symbols concurrently,
        with the semaphore limiting concurrent requests to max_concurrent. If one
        symbol fails after all retries, processing continues for remaining symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for historical data (default: 1 year ago)
            end_date: End date for historical data (default: today)
            
        Returns:
            dict: Dictionary mapping symbol to DataFrame
                  Failed symbols will have empty DataFrames
                  
        Requirements: 18.1, 18.2, 18.3, 18.4, 18.5
        
        Example:
            >>> collector = AsyncDataCollector()
            >>> symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
            >>> results = await collector.fetch_multiple_stocks(symbols)
            >>> for symbol, data in results.items():
            ...     print(f"{symbol}: {len(data)} records")
        """
        logger.info(f"Starting concurrent fetch for {len(symbols)} symbols")
        start_time = time.time()
        
        # Create tasks for all symbols
        tasks = [
            self.fetch_stock(symbol, start_date, end_date)
            for symbol in symbols
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Map results to symbols
        results_dict = dict(zip(symbols, results))
        
        # Log completion status for each symbol
        successful = 0
        failed = 0
        
        for symbol, data in results_dict.items():
            if not data.empty:
                successful += 1
                logger.info(f"✓ {symbol}: {len(data)} records fetched successfully")
            else:
                failed += 1
                logger.warning(f"✗ {symbol}: Failed to fetch data")
        
        elapsed_time = time.time() - start_time
        logger.info(
            f"Concurrent fetch complete in {elapsed_time:.2f} seconds: "
            f"{successful} successful, {failed} failed out of {len(symbols)} total symbols"
        )
        
        return results_dict
