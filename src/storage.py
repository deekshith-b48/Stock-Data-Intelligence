"""
Data storage module for persisting stock data to the database.

This module provides functions for storing company information and stock data
with proper error handling for unique constraint violations.

Requirements: 5.3
"""

import logging
from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.database import Company, StockData
from src.models.connection import get_database

logger = logging.getLogger(__name__)


def store_company(symbol: str, name: str, session: Optional[Session] = None) -> Optional[Company]:
    """
    Store or update company information in the database.
    
    Uses upsert logic: if company with symbol exists, returns existing record.
    Otherwise, creates a new company record.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS.NS')
        name: Company name (e.g., 'Reliance Industries Limited')
        session: Optional SQLAlchemy session. If None, creates a new session.
        
    Returns:
        Company: The stored or existing Company object, or None if storage fails
        
    Requirements: 5.3
    
    Example:
        >>> company = store_company('AAPL', 'Apple Inc.')
        >>> print(company.id, company.symbol, company.name)
        1 AAPL Apple Inc.
    """
    close_session = False
    
    try:
        # Create session if not provided
        if session is None:
            db = get_database()
            session = db.get_session_with_retry()
            close_session = True
        
        # Check if company already exists
        existing_company = session.query(Company).filter_by(symbol=symbol).first()
        
        if existing_company:
            logger.info(f"Company {symbol} already exists with id={existing_company.id}")
            return existing_company
        
        # Create new company
        company = Company(symbol=symbol, name=name)
        session.add(company)
        session.commit()
        session.refresh(company)
        
        logger.info(f"Successfully stored company {symbol} (id={company.id})")
        return company
        
    except IntegrityError as e:
        # Handle race condition: another process inserted the same symbol
        session.rollback()
        logger.warning(
            f"Integrity error storing company {symbol}: {e}. "
            f"Attempting to retrieve existing record."
        )
        
        # Try to retrieve the existing company
        try:
            existing_company = session.query(Company).filter_by(symbol=symbol).first()
            if existing_company:
                logger.info(f"Retrieved existing company {symbol} (id={existing_company.id})")
                return existing_company
            else:
                logger.error(f"Failed to retrieve company {symbol} after integrity error")
                return None
        except Exception as retrieve_error:
            logger.error(f"Error retrieving company {symbol}: {retrieve_error}")
            return None
            
    except Exception as e:
        session.rollback()
        logger.error(f"Error storing company {symbol}: {e}", exc_info=True)
        return None
        
    finally:
        if close_session and session:
            session.close()


def store_stock_data(
    symbol: str,
    dataframe: pd.DataFrame,
    session: Optional[Session] = None
) -> dict:
    """
    Store stock data for a company in the database.
    
    This function performs bulk insert of stock data records. It handles:
    - Company lookup/creation
    - Bulk insert of stock data records
    - Unique constraint violations (duplicate date records)
    - Comprehensive logging of success/failure
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS.NS')
        dataframe: DataFrame with columns [date, open, high, low, close, volume]
                   and optional [daily_return, moving_avg_7d, volatility_score]
        session: Optional SQLAlchemy session. If None, creates a new session.
        
    Returns:
        dict: Summary with keys:
              - 'symbol': Stock symbol
              - 'total_records': Total records in dataframe
              - 'inserted': Number of successfully inserted records
              - 'skipped': Number of skipped records (duplicates)
              - 'failed': Number of failed records
              - 'success': Boolean indicating overall success
              
    Requirements: 5.3
    
    Example:
        >>> data = pd.DataFrame({
        ...     'date': [date(2024, 1, 1), date(2024, 1, 2)],
        ...     'open': [100.0, 101.0],
        ...     'high': [105.0, 106.0],
        ...     'low': [99.0, 100.0],
        ...     'close': [102.0, 103.0],
        ...     'volume': [1000000, 1100000],
        ...     'daily_return': [None, 0.98],
        ...     'moving_avg_7d': [None, None],
        ...     'volatility_score': [None, None]
        ... })
        >>> result = store_stock_data('AAPL', data)
        >>> print(result)
        {'symbol': 'AAPL', 'total_records': 2, 'inserted': 2, 'skipped': 0, 'failed': 0, 'success': True}
    """
    close_session = False
    
    result = {
        'symbol': symbol,
        'total_records': len(dataframe),
        'inserted': 0,
        'skipped': 0,
        'failed': 0,
        'success': False
    }
    
    if dataframe.empty:
        logger.warning(f"Empty dataframe provided for {symbol}, nothing to store")
        result['success'] = True
        return result
    
    try:
        # Create session if not provided
        if session is None:
            db = get_database()
            session = db.get_session_with_retry()
            close_session = True
        
        # Get or create company
        company = store_company(symbol, symbol, session)
        
        if company is None:
            logger.error(f"Failed to get/create company for {symbol}")
            result['failed'] = len(dataframe)
            return result
        
        logger.info(f"Storing {len(dataframe)} stock data records for {symbol} (company_id={company.id})")
        
        # Prepare stock data records
        for idx, row in dataframe.iterrows():
            try:
                # Create StockData object
                stock_record = StockData(
                    company_id=company.id,
                    date=row['date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume']),
                    daily_return=float(row['daily_return']) if pd.notna(row.get('daily_return')) else None,
                    moving_avg_7d=float(row['moving_avg_7d']) if pd.notna(row.get('moving_avg_7d')) else None,
                    volatility_score=float(row['volatility_score']) if pd.notna(row.get('volatility_score')) else None
                )
                
                session.add(stock_record)
                
                # Commit in batches of 100 for better performance
                if (idx + 1) % 100 == 0:
                    try:
                        session.commit()
                        result['inserted'] += 100
                        logger.debug(f"Committed batch of 100 records for {symbol}")
                    except IntegrityError as e:
                        # Handle unique constraint violations in batch
                        session.rollback()
                        logger.warning(f"Integrity error in batch for {symbol}: {e}")
                        
                        # Re-insert records one by one to identify duplicates
                        for i in range(max(0, idx - 99), idx + 1):
                            try:
                                row_data = dataframe.iloc[i]
                                stock_record = StockData(
                                    company_id=company.id,
                                    date=row_data['date'],
                                    open=float(row_data['open']),
                                    high=float(row_data['high']),
                                    low=float(row_data['low']),
                                    close=float(row_data['close']),
                                    volume=int(row_data['volume']),
                                    daily_return=float(row_data['daily_return']) if pd.notna(row_data.get('daily_return')) else None,
                                    moving_avg_7d=float(row_data['moving_avg_7d']) if pd.notna(row_data.get('moving_avg_7d')) else None,
                                    volatility_score=float(row_data['volatility_score']) if pd.notna(row_data.get('volatility_score')) else None
                                )
                                session.add(stock_record)
                                session.commit()
                                result['inserted'] += 1
                            except IntegrityError:
                                session.rollback()
                                result['skipped'] += 1
                                logger.debug(f"Skipped duplicate record for {symbol} on {row_data['date']}")
                            except Exception as e:
                                session.rollback()
                                result['failed'] += 1
                                logger.error(f"Failed to insert record for {symbol} on {row_data['date']}: {e}")
                        
            except Exception as e:
                result['failed'] += 1
                logger.error(f"Error preparing record for {symbol} at index {idx}: {e}")
        
        # Commit remaining records
        try:
            remaining = len(dataframe) % 100
            if remaining > 0:
                session.commit()
                result['inserted'] += remaining
                logger.debug(f"Committed final batch of {remaining} records for {symbol}")
        except IntegrityError as e:
            # Handle unique constraint violations in final batch
            session.rollback()
            logger.warning(f"Integrity error in final batch for {symbol}: {e}")
            
            # Re-insert remaining records one by one
            start_idx = len(dataframe) - remaining
            for i in range(start_idx, len(dataframe)):
                try:
                    row_data = dataframe.iloc[i]
                    stock_record = StockData(
                        company_id=company.id,
                        date=row_data['date'],
                        open=float(row_data['open']),
                        high=float(row_data['high']),
                        low=float(row_data['low']),
                        close=float(row_data['close']),
                        volume=int(row_data['volume']),
                        daily_return=float(row_data['daily_return']) if pd.notna(row_data.get('daily_return')) else None,
                        moving_avg_7d=float(row_data['moving_avg_7d']) if pd.notna(row_data.get('moving_avg_7d')) else None,
                        volatility_score=float(row_data['volatility_score']) if pd.notna(row_data.get('volatility_score')) else None
                    )
                    session.add(stock_record)
                    session.commit()
                    result['inserted'] += 1
                except IntegrityError:
                    session.rollback()
                    result['skipped'] += 1
                    logger.debug(f"Skipped duplicate record for {symbol} on {row_data['date']}")
                except Exception as e:
                    session.rollback()
                    result['failed'] += 1
                    logger.error(f"Failed to insert record for {symbol} on {row_data['date']}: {e}")
        
        # Mark as successful if at least some records were inserted
        result['success'] = result['inserted'] > 0 or result['skipped'] > 0
        
        logger.info(
            f"Storage complete for {symbol}: "
            f"{result['inserted']} inserted, {result['skipped']} skipped (duplicates), "
            f"{result['failed']} failed out of {result['total_records']} total"
        )
        
        return result
        
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"Error storing stock data for {symbol}: {e}", exc_info=True)
        result['failed'] = result['total_records'] - result['inserted'] - result['skipped']
        return result
        
    finally:
        if close_session and session:
            session.close()
