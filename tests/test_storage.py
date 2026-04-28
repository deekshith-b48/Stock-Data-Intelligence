"""
Unit tests for storage module.

Tests the store_company and store_stock_data functions.
"""

import pytest
import pandas as pd
from datetime import date
from sqlalchemy.exc import IntegrityError

from src.storage import store_company, store_stock_data
from src.models.database import Company, StockData
from src.models.connection import get_database


@pytest.fixture
def db_session():
    """Create a test database session."""
    db = get_database()
    session = db.get_session_with_retry()
    yield session
    session.close()


def test_store_company_new(db_session):
    """Test storing a new company."""
    company = store_company('TEST', 'Test Company', db_session)
    
    assert company is not None
    assert company.symbol == 'TEST'
    assert company.name == 'Test Company'
    assert company.id is not None


def test_store_company_existing(db_session):
    """Test storing a company that already exists."""
    # Store first time
    company1 = store_company('TEST2', 'Test Company 2', db_session)
    assert company1 is not None
    
    # Store again - should return existing
    company2 = store_company('TEST2', 'Test Company 2', db_session)
    assert company2 is not None
    assert company2.id == company1.id


def test_store_stock_data_success(db_session):
    """Test storing stock data successfully."""
    # Create test data
    data = pd.DataFrame({
        'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
        'open': [100.0, 101.0, 102.0],
        'high': [105.0, 106.0, 107.0],
        'low': [99.0, 100.0, 101.0],
        'close': [102.0, 103.0, 104.0],
        'volume': [1000000, 1100000, 1200000],
        'daily_return': [None, 0.98, 0.97],
        'moving_avg_7d': [None, None, None],
        'volatility_score': [None, None, None]
    })
    
    result = store_stock_data('TEST3', data, db_session)
    
    assert result['success'] is True
    assert result['total_records'] == 3
    assert result['inserted'] == 3
    assert result['skipped'] == 0
    assert result['failed'] == 0


def test_store_stock_data_duplicates(db_session):
    """Test storing stock data with duplicates."""
    # Create test data
    data = pd.DataFrame({
        'date': [date(2024, 1, 1), date(2024, 1, 2)],
        'open': [100.0, 101.0],
        'high': [105.0, 106.0],
        'low': [99.0, 100.0],
        'close': [102.0, 103.0],
        'volume': [1000000, 1100000],
        'daily_return': [None, 0.98],
        'moving_avg_7d': [None, None],
        'volatility_score': [None, None]
    })
    
    # Store first time
    result1 = store_stock_data('TEST4', data, db_session)
    assert result1['success'] is True
    assert result1['inserted'] == 2
    
    # Store again - should skip duplicates
    result2 = store_stock_data('TEST4', data, db_session)
    assert result2['success'] is True
    assert result2['inserted'] == 0
    assert result2['skipped'] == 2


def test_store_stock_data_empty_dataframe(db_session):
    """Test storing empty dataframe."""
    data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    
    result = store_stock_data('TEST5', data, db_session)
    
    assert result['success'] is True
    assert result['total_records'] == 0
    assert result['inserted'] == 0


def test_store_stock_data_partial_metrics(db_session):
    """Test storing stock data with partial metrics (some NULL values)."""
    data = pd.DataFrame({
        'date': [date(2024, 1, 1), date(2024, 1, 2)],
        'open': [100.0, 101.0],
        'high': [105.0, 106.0],
        'low': [99.0, 100.0],
        'close': [102.0, 103.0],
        'volume': [1000000, 1100000],
        'daily_return': [None, 0.98],  # First is NULL
        'moving_avg_7d': [None, None],  # Both NULL
        'volatility_score': [None, 45.2]  # Second has value
    })
    
    result = store_stock_data('TEST6', data, db_session)
    
    assert result['success'] is True
    assert result['inserted'] == 2
    
    # Verify data was stored correctly
    company = db_session.query(Company).filter_by(symbol='TEST6').first()
    stock_records = db_session.query(StockData).filter_by(company_id=company.id).all()
    
    assert len(stock_records) == 2
    assert stock_records[0].daily_return is None
    assert stock_records[1].daily_return is not None
    assert stock_records[0].volatility_score is None
    assert stock_records[1].volatility_score is not None
