"""
Data processor module for cleaning and transforming stock market data.

This module provides the DataProcessor class for cleaning raw stock data,
handling missing values, validating numeric fields, removing duplicates,
and converting dates to ISO 8601 format.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import logging
from datetime import date
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes and cleans stock market data.
    
    Features:
    - Handle missing values using forward-fill method
    - Validate numeric fields (prices, volume)
    - Remove duplicate records based on date
    - Convert dates to ISO 8601 format (YYYY-MM-DD)
    - Log invalid records and exclude from output
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    def __init__(self):
        """Initialize DataProcessor."""
        logger.info("DataProcessor initialized")
    
    def clean_data(self, df: pd.DataFrame, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Clean and validate stock data.
        
        This method performs the following operations:
        1. Convert dates to ISO 8601 format (YYYY-MM-DD)
        2. Validate numeric fields (prices and volume must be positive)
        3. Handle missing values using forward-fill method
        4. Remove duplicate records based on date
        5. Log invalid records and exclude them from output
        
        Args:
            df: DataFrame with columns [date, open, high, low, close, volume]
            symbol: Optional stock symbol for logging purposes
            
        Returns:
            pd.DataFrame: Cleaned DataFrame with same columns
                         Invalid records are excluded
                         
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        
        Example:
            >>> processor = DataProcessor()
            >>> raw_data = pd.DataFrame({
            ...     'date': ['2024-01-01', '2024-01-02', '2024-01-02'],
            ...     'open': [100.0, None, 102.0],
            ...     'close': [101.0, 103.0, 104.0],
            ...     'volume': [1000, 2000, 3000]
            ... })
            >>> clean_data = processor.clean_data(raw_data, 'AAPL')
        """
        if df.empty:
            logger.warning(f"Empty DataFrame provided for cleaning{f' ({symbol})' if symbol else ''}")
            return df
        
        symbol_label = f" for {symbol}" if symbol else ""
        logger.info(f"Starting data cleaning{symbol_label}: {len(df)} records")
        
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        original_count = len(df)
        invalid_records = []
        
        # Step 1: Convert dates to ISO 8601 format (YYYY-MM-DD)
        try:
            # Handle different date formats
            if df['date'].dtype == 'object':
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            elif not isinstance(df['date'].iloc[0], (date, pd.Timestamp)):
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Convert to date type (remove time component) and format as ISO 8601
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Check for invalid dates (NaT converted to None)
            invalid_dates = df[df['date'].isna()]
            if not invalid_dates.empty:
                for idx, row in invalid_dates.iterrows():
                    invalid_records.append({
                        'index': idx,
                        'reason': 'Invalid date format',
                        'data': row.to_dict()
                    })
                    logger.warning(
                        f"Invalid date record{symbol_label} at index {idx}: {row.to_dict()}"
                    )
                df = df[df['date'].notna()]
            
        except Exception as e:
            logger.error(f"Error converting dates{symbol_label}: {e}")
            # If date conversion fails completely, return empty DataFrame
            return pd.DataFrame(columns=df.columns)
        
        # Step 2: Convert numeric fields to numeric type
        numeric_fields = ['open', 'high', 'low', 'close', 'volume']
        
        for field in numeric_fields:
            if field not in df.columns:
                logger.error(f"Missing required field '{field}'{symbol_label}")
                continue
            
            # Convert to numeric, coercing errors to NaN
            df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Step 3: Sort by date before handling missing values
        df = df.sort_values('date').reset_index(drop=True)
        
        # Step 4: Handle missing values using forward-fill
        missing_before = df.isnull().sum().sum()
        if missing_before > 0:
            logger.info(
                f"Handling {missing_before} missing values using forward-fill{symbol_label}"
            )
            df = df.ffill()
            
            # If there are still NaN values at the beginning (no previous value to fill),
            # use backward fill
            df = df.bfill()
            
            # If still NaN (entire column is NaN), drop those rows
            remaining_nan = df.isnull().sum().sum()
            if remaining_nan > 0:
                logger.warning(
                    f"Dropping {df.isnull().any(axis=1).sum()} rows with "
                    f"unfillable missing values{symbol_label}"
                )
                df = df.dropna()
        
        # Step 5: Validate numeric fields (must be positive)
        for field in numeric_fields:
            # Check for non-positive values (prices and volume must be positive)
            invalid_mask = (df[field] <= 0) | (df[field].isna())
            invalid_rows = df[invalid_mask]
            
            if not invalid_rows.empty:
                for idx, row in invalid_rows.iterrows():
                    invalid_records.append({
                        'index': idx,
                        'reason': f'Invalid {field} value (must be positive)',
                        'data': row.to_dict()
                    })
                    logger.warning(
                        f"Invalid {field} value{symbol_label} at index {idx}: "
                        f"{row[field]} (must be positive)"
                    )
        
        # Remove all rows with any invalid numeric values
        valid_mask = (
            (df['open'] > 0) &
            (df['high'] > 0) &
            (df['low'] > 0) &
            (df['close'] > 0) &
            (df['volume'] > 0)
        )
        df = df[valid_mask]
        
        if df.empty:
            logger.warning(
                f"All records invalid after numeric validation{symbol_label}. "
                f"Original count: {original_count}"
            )
            return df
        
        # Step 6: Remove duplicate records based on date
        duplicates_before = df.duplicated(subset=['date'], keep='first').sum()
        if duplicates_before > 0:
            duplicate_rows = df[df.duplicated(subset=['date'], keep='first')]
            for idx, row in duplicate_rows.iterrows():
                logger.warning(
                    f"Duplicate record{symbol_label} for date {row['date']}: "
                    f"removing duplicate at index {idx}"
                )
            
            df = df.drop_duplicates(subset=['date'], keep='first')
            logger.info(
                f"Removed {duplicates_before} duplicate records{symbol_label}"
            )
        
        # Final validation: ensure data integrity
        # Check that high >= low, high >= open, high >= close, low <= open, low <= close
        integrity_issues = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )
        
        if integrity_issues.any():
            invalid_rows = df[integrity_issues]
            for idx, row in invalid_rows.iterrows():
                invalid_records.append({
                    'index': idx,
                    'reason': 'Data integrity violation (high/low/open/close relationship)',
                    'data': row.to_dict()
                })
                logger.warning(
                    f"Data integrity issue{symbol_label} at index {idx}: "
                    f"high={row['high']}, low={row['low']}, "
                    f"open={row['open']}, close={row['close']}"
                )
            
            df = df[~integrity_issues]
        
        # Reset index after all cleaning operations
        df = df.reset_index(drop=True)
        
        # Summary logging
        records_removed = original_count - len(df)
        if records_removed > 0:
            logger.info(
                f"Data cleaning complete{symbol_label}: "
                f"{len(df)} valid records, {records_removed} invalid records removed "
                f"({records_removed/original_count*100:.1f}% removed)"
            )
            logger.info(
                f"Invalid records breakdown{symbol_label}: "
                f"{len(invalid_records)} total issues logged"
            )
        else:
            logger.info(
                f"Data cleaning complete{symbol_label}: "
                f"all {len(df)} records valid"
            )
        
        return df
    
    def calculate_daily_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily return percentage for stock data.
        
        Daily return is calculated as:
        ((close_price - previous_close_price) / previous_close_price) * 100
        
        Args:
            df: DataFrame with 'close' column, sorted by date
            
        Returns:
            pd.DataFrame: DataFrame with added 'daily_return' column
                         First row will have NULL/NaN for daily_return
                         
        Requirements: 3.1
        
        Example:
            >>> processor = DataProcessor()
            >>> data = pd.DataFrame({
            ...     'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            ...     'close': [100.0, 105.0, 102.0]
            ... })
            >>> result = processor.calculate_daily_return(data)
            >>> result['daily_return'].iloc[1]  # (105-100)/100 * 100 = 5.0
            5.0
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for daily return calculation")
            df['daily_return'] = None
            return df
        
        if 'close' not in df.columns:
            logger.error("DataFrame missing 'close' column for daily return calculation")
            df['daily_return'] = None
            return df
        
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Calculate daily return: ((close - prev_close) / prev_close) * 100
        # shift(1) gets the previous row's value
        prev_close = df['close'].shift(1)
        df['daily_return'] = ((df['close'] - prev_close) / prev_close) * 100
        
        # First row will have NaN since there's no previous close
        logger.info(f"Calculated daily return for {len(df)} records ({(len(df)-1)} valid returns)")
        
        return df
    
    def calculate_moving_average(self, df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
        """
        Calculate moving average of closing prices.
        
        Args:
            df: DataFrame with 'close' column, sorted by date
            window: Number of days for moving average (default: 7)
            
        Returns:
            pd.DataFrame: DataFrame with added 'moving_avg_7d' column
                         Rows with insufficient data will have NULL/NaN
                         
        Requirements: 3.2
        
        Example:
            >>> processor = DataProcessor()
            >>> data = pd.DataFrame({
            ...     'date': [date(2024, 1, i) for i in range(1, 11)],
            ...     'close': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0]
            ... })
            >>> result = processor.calculate_moving_average(data, window=7)
            >>> result['moving_avg_7d'].iloc[6]  # Average of first 7 days
            103.0
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for moving average calculation")
            df['moving_avg_7d'] = None
            return df
        
        if 'close' not in df.columns:
            logger.error("DataFrame missing 'close' column for moving average calculation")
            df['moving_avg_7d'] = None
            return df
        
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Calculate rolling mean with specified window
        df['moving_avg_7d'] = df['close'].rolling(window=window, min_periods=window).mean()
        
        # Count how many valid moving averages we calculated
        valid_count = df['moving_avg_7d'].notna().sum()
        logger.info(
            f"Calculated {window}-day moving average for {len(df)} records "
            f"({valid_count} valid averages)"
        )
        
        return df
    
    def calculate_52_week_stats(self, df: pd.DataFrame) -> dict:
        """
        Calculate 52-week statistics (high, low, average close).
        
        Args:
            df: DataFrame with 'close' column for last 52 weeks (or less)
            
        Returns:
            dict: Dictionary with keys:
                  - '52_week_high': Maximum closing price (or None if insufficient data)
                  - '52_week_low': Minimum closing price (or None if insufficient data)
                  - 'avg_close': Average closing price (or None if insufficient data)
                  
        Requirements: 3.3, 3.4, 3.5, 3.6
        
        Example:
            >>> processor = DataProcessor()
            >>> data = pd.DataFrame({
            ...     'date': [date(2024, 1, i) for i in range(1, 366)],
            ...     'close': [100.0 + i for i in range(365)]
            ... })
            >>> stats = processor.calculate_52_week_stats(data)
            >>> stats['52_week_high']
            464.0
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for 52-week stats calculation")
            return {
                '52_week_high': None,
                '52_week_low': None,
                'avg_close': None
            }
        
        if 'close' not in df.columns:
            logger.error("DataFrame missing 'close' column for 52-week stats calculation")
            return {
                '52_week_high': None,
                '52_week_low': None,
                'avg_close': None
            }
        
        # Filter to last 52 weeks (364 days, approximately 52 * 7)
        # Assuming data is already sorted by date
        # Take last 364 days of data (52 weeks * 7 days)
        last_52_weeks = df.tail(364)
        
        if last_52_weeks.empty:
            logger.warning("No data available for 52-week stats calculation")
            return {
                '52_week_high': None,
                '52_week_low': None,
                'avg_close': None
            }
        
        # Calculate statistics
        week_52_high = float(last_52_weeks['close'].max())
        week_52_low = float(last_52_weeks['close'].min())
        avg_close = float(last_52_weeks['close'].mean())
        
        logger.info(
            f"Calculated 52-week stats from {len(last_52_weeks)} records: "
            f"high={week_52_high:.2f}, low={week_52_low:.2f}, avg={avg_close:.2f}"
        )
        
        return {
            '52_week_high': week_52_high,
            '52_week_low': week_52_low,
            'avg_close': avg_close
        }
    
    def calculate_volatility_score(self, df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
        """
        Calculate volatility score based on standard deviation of daily returns.
        
        Volatility score measures price fluctuation intensity over a rolling window.
        The score is normalized to a 0-100 scale for easy comparison across stocks.
        
        Args:
            df: DataFrame with 'daily_return' column, sorted by date
            window: Number of days for volatility calculation (default: 30)
            
        Returns:
            pd.DataFrame: DataFrame with added 'volatility_score' column
                         Rows with insufficient data (< 7 days) will have NULL/NaN
                         Normalized to 0-100 scale
                         
        Requirements: 4.1, 4.2, 4.3, 4.4
        
        Example:
            >>> processor = DataProcessor()
            >>> data = pd.DataFrame({
            ...     'date': [date(2024, 1, i) for i in range(1, 32)],
            ...     'daily_return': [1.5, -0.8, 2.1, -1.2, 0.5, ...] # 31 days
            ... })
            >>> result = processor.calculate_volatility_score(data, window=30)
            >>> result['volatility_score'].iloc[29]  # First valid score at day 30
            45.2
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for volatility score calculation")
            df['volatility_score'] = None
            return df
        
        if 'daily_return' not in df.columns:
            logger.error("DataFrame missing 'daily_return' column for volatility score calculation")
            df['volatility_score'] = None
            return df
        
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Minimum data requirement: 7 days
        min_periods = 7
        
        if len(df) < min_periods:
            logger.warning(
                f"Insufficient data for volatility score calculation: "
                f"{len(df)} records (minimum {min_periods} required)"
            )
            df['volatility_score'] = None
            return df
        
        # Calculate rolling standard deviation of daily returns
        # Use min_periods to ensure we have at least 7 days of data
        volatility_raw = df['daily_return'].rolling(
            window=window, 
            min_periods=min_periods
        ).std()
        
        # Normalize to 0-100 scale
        # Find the maximum volatility in the dataset for normalization
        max_volatility = volatility_raw.max()
        
        if pd.isna(max_volatility) or max_volatility == 0:
            logger.warning("No valid volatility values calculated (all NaN or zero)")
            df['volatility_score'] = None
            return df
        
        # Normalize: (raw_volatility / max_volatility) * 100
        df['volatility_score'] = (volatility_raw / max_volatility) * 100
        
        # Count how many valid volatility scores we calculated
        valid_count = df['volatility_score'].notna().sum()
        logger.info(
            f"Calculated volatility score for {len(df)} records "
            f"({valid_count} valid scores, window={window}, min_periods={min_periods})"
        )
        
        return df
