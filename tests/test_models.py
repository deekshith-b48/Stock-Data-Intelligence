"""
Unit tests for SQLAlchemy ORM models.

Tests cover:
- Model instantiation
- Relationships
- Constraints
- Cascade delete behavior
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models import Base, Company, StockData


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_company_creation(db_session):
    """Test creating a Company record."""
    company = Company(symbol='RELIANCE', name='Reliance Industries Ltd.')
    db_session.add(company)
    db_session.commit()
    
    result = db_session.query(Company).filter_by(symbol='RELIANCE').first()
    assert result is not None
    assert result.symbol == 'RELIANCE'
    assert result.name == 'Reliance Industries Ltd.'
    assert result.created_at is not None


def test_company_unique_constraint(db_session):
    """Test that duplicate symbols are not allowed."""
    company1 = Company(symbol='TCS', name='Tata Consultancy Services')
    company2 = Company(symbol='TCS', name='TCS Limited')
    
    db_session.add(company1)
    db_session.commit()
    
    db_session.add(company2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_stock_data_creation(db_session):
    """Test creating a StockData record with foreign key relationship."""
    company = Company(symbol='INFY', name='Infosys Ltd.')
    db_session.add(company)
    db_session.commit()
    
    stock_data = StockData(
        company_id=company.id,
        date=date(2024, 1, 15),
        open=Decimal('1500.00'),
        high=Decimal('1520.50'),
        low=Decimal('1495.00'),
        close=Decimal('1510.25'),
        volume=1000000,
        daily_return=Decimal('0.5000'),
        moving_avg_7d=Decimal('1505.00'),
        volatility_score=Decimal('25.50')
    )
    db_session.add(stock_data)
    db_session.commit()
    
    result = db_session.query(StockData).filter_by(company_id=company.id).first()
    assert result is not None
    assert result.date == date(2024, 1, 15)
    assert result.close == Decimal('1510.25')
    assert result.volume == 1000000


def test_stock_data_unique_constraint(db_session):
    """Test that duplicate (company_id, date) combinations are not allowed."""
    company = Company(symbol='HDFCBANK', name='HDFC Bank Ltd.')
    db_session.add(company)
    db_session.commit()
    
    stock_data1 = StockData(
        company_id=company.id,
        date=date(2024, 1, 15),
        open=Decimal('1600.00'),
        high=Decimal('1620.00'),
        low=Decimal('1595.00'),
        close=Decimal('1610.00'),
        volume=500000
    )
    stock_data2 = StockData(
        company_id=company.id,
        date=date(2024, 1, 15),
        open=Decimal('1605.00'),
        high=Decimal('1625.00'),
        low=Decimal('1600.00'),
        close=Decimal('1615.00'),
        volume=600000
    )
    
    db_session.add(stock_data1)
    db_session.commit()
    
    db_session.add(stock_data2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_cascade_delete(db_session):
    """Test that deleting a company cascades to delete its stock data."""
    company = Company(symbol='WIPRO', name='Wipro Ltd.')
    db_session.add(company)
    db_session.commit()
    
    stock_data1 = StockData(
        company_id=company.id,
        date=date(2024, 1, 15),
        open=Decimal('400.00'),
        high=Decimal('410.00'),
        low=Decimal('395.00'),
        close=Decimal('405.00'),
        volume=800000
    )
    stock_data2 = StockData(
        company_id=company.id,
        date=date(2024, 1, 16),
        open=Decimal('405.00'),
        high=Decimal('415.00'),
        low=Decimal('400.00'),
        close=Decimal('410.00'),
        volume=850000
    )
    db_session.add_all([stock_data1, stock_data2])
    db_session.commit()
    
    # Verify stock data exists
    stock_count = db_session.query(StockData).filter_by(company_id=company.id).count()
    assert stock_count == 2
    
    # Delete company
    db_session.delete(company)
    db_session.commit()
    
    # Verify stock data was deleted
    stock_count = db_session.query(StockData).filter_by(company_id=company.id).count()
    assert stock_count == 0


def test_relationship_access(db_session):
    """Test accessing related records through relationships."""
    company = Company(symbol='BHARTIARTL', name='Bharti Airtel Ltd.')
    db_session.add(company)
    db_session.commit()
    
    stock_data = StockData(
        company_id=company.id,
        date=date(2024, 1, 15),
        open=Decimal('800.00'),
        high=Decimal('820.00'),
        low=Decimal('795.00'),
        close=Decimal('815.00'),
        volume=1200000
    )
    db_session.add(stock_data)
    db_session.commit()
    
    # Access company from stock_data
    assert stock_data.company.symbol == 'BHARTIARTL'
    
    # Access stock_data from company
    assert len(company.stock_data) == 1
    assert company.stock_data[0].close == Decimal('815.00')


def test_nullable_metric_fields(db_session):
    """Test that metric fields (daily_return, moving_avg_7d, volatility_score) can be NULL."""
    company = Company(symbol='ITC', name='ITC Ltd.')
    db_session.add(company)
    db_session.commit()
    
    stock_data = StockData(
        company_id=company.id,
        date=date(2024, 1, 15),
        open=Decimal('450.00'),
        high=Decimal('460.00'),
        low=Decimal('445.00'),
        close=Decimal('455.00'),
        volume=900000
        # Intentionally not setting daily_return, moving_avg_7d, volatility_score
    )
    db_session.add(stock_data)
    db_session.commit()
    
    result = db_session.query(StockData).filter_by(company_id=company.id).first()
    assert result.daily_return is None
    assert result.moving_avg_7d is None
    assert result.volatility_score is None
