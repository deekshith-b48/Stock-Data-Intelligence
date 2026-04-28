"""
Unit tests for database initialization script.

Tests verify:
- Table creation from ORM models
- Sample company data insertion
- Handling of existing data
- Database verification
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import get_database, Company, StockData
from src.models.connection import DatabaseConnection


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_file.name
    temp_file.close()
    
    # Set database URL
    database_url = f'sqlite:///{temp_db_path}'
    
    # Create database connection
    db = DatabaseConnection(database_url=database_url)
    
    yield db
    
    # Cleanup
    db.close()
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


def test_create_tables(temp_db):
    """Test that tables are created from ORM models."""
    # Create tables
    temp_db.create_tables()
    
    # Verify tables exist by querying them
    with temp_db.get_session() as session:
        # Should not raise an error
        company_count = session.query(Company).count()
        stock_count = session.query(StockData).count()
        
        assert company_count == 0
        assert stock_count == 0


def test_insert_sample_companies(temp_db):
    """Test insertion of sample company data."""
    temp_db.create_tables()
    
    # Sample companies
    sample_companies = [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd."},
        {"symbol": "TCS", "name": "Tata Consultancy Services Ltd."},
        {"symbol": "INFY", "name": "Infosys Ltd."},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd."},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd."},
    ]
    
    # Insert companies
    with temp_db.get_session() as session:
        for company_data in sample_companies:
            company = Company(
                symbol=company_data["symbol"],
                name=company_data["name"]
            )
            session.add(company)
    
    # Verify insertion
    with temp_db.get_session() as session:
        companies = session.query(Company).all()
        assert len(companies) == 5
        
        # Verify specific companies
        reliance = session.query(Company).filter_by(symbol="RELIANCE").first()
        assert reliance is not None
        assert reliance.name == "Reliance Industries Ltd."
        
        tcs = session.query(Company).filter_by(symbol="TCS").first()
        assert tcs is not None
        assert tcs.name == "Tata Consultancy Services Ltd."


def test_unique_constraint_on_symbol(temp_db):
    """Test that duplicate symbols are prevented by unique constraint."""
    temp_db.create_tables()
    
    # Insert first company
    with temp_db.get_session() as session:
        company1 = Company(symbol="RELIANCE", name="Reliance Industries Ltd.")
        session.add(company1)
    
    # Try to insert duplicate symbol
    from sqlalchemy.exc import IntegrityError
    
    with pytest.raises(IntegrityError):
        with temp_db.get_session() as session:
            company2 = Company(symbol="RELIANCE", name="Duplicate Company")
            session.add(company2)


def test_all_sample_companies_inserted(temp_db):
    """Test that all 10 sample Indian stock companies can be inserted."""
    temp_db.create_tables()
    
    # All sample companies from init_db.py
    sample_companies = [
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd."},
        {"symbol": "TCS", "name": "Tata Consultancy Services Ltd."},
        {"symbol": "INFY", "name": "Infosys Ltd."},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd."},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd."},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd."},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd."},
        {"symbol": "ITC", "name": "ITC Ltd."},
        {"symbol": "SBIN", "name": "State Bank of India"},
        {"symbol": "WIPRO", "name": "Wipro Ltd."},
    ]
    
    # Insert all companies
    with temp_db.get_session() as session:
        for company_data in sample_companies:
            company = Company(
                symbol=company_data["symbol"],
                name=company_data["name"]
            )
            session.add(company)
    
    # Verify all companies were inserted
    with temp_db.get_session() as session:
        companies = session.query(Company).all()
        assert len(companies) == 10
        
        # Verify symbols
        symbols = {c.symbol for c in companies}
        expected_symbols = {c["symbol"] for c in sample_companies}
        assert symbols == expected_symbols


def test_company_query_by_symbol(temp_db):
    """Test querying companies by symbol."""
    temp_db.create_tables()
    
    # Insert companies
    with temp_db.get_session() as session:
        session.add(Company(symbol="RELIANCE", name="Reliance Industries Ltd."))
        session.add(Company(symbol="TCS", name="Tata Consultancy Services Ltd."))
    
    # Query by symbol
    with temp_db.get_session() as session:
        reliance = session.query(Company).filter_by(symbol="RELIANCE").first()
        assert reliance is not None
        assert reliance.symbol == "RELIANCE"
        assert reliance.name == "Reliance Industries Ltd."
        
        # Query non-existent symbol
        non_existent = session.query(Company).filter_by(symbol="NONEXISTENT").first()
        assert non_existent is None


def test_company_list_ordered(temp_db):
    """Test that companies can be retrieved in alphabetical order."""
    temp_db.create_tables()
    
    # Insert companies in random order
    with temp_db.get_session() as session:
        session.add(Company(symbol="WIPRO", name="Wipro Ltd."))
        session.add(Company(symbol="RELIANCE", name="Reliance Industries Ltd."))
        session.add(Company(symbol="TCS", name="Tata Consultancy Services Ltd."))
    
    # Query ordered by symbol
    with temp_db.get_session() as session:
        companies = session.query(Company).order_by(Company.symbol).all()
        symbols = [c.symbol for c in companies]
        assert symbols == ["RELIANCE", "TCS", "WIPRO"]


def test_database_verification(temp_db):
    """Test database verification after initialization."""
    temp_db.create_tables()
    
    # Insert sample data
    with temp_db.get_session() as session:
        session.add(Company(symbol="RELIANCE", name="Reliance Industries Ltd."))
        session.add(Company(symbol="TCS", name="Tata Consultancy Services Ltd."))
    
    # Verify database state
    with temp_db.get_session() as session:
        company_count = session.query(Company).count()
        assert company_count == 2
        
        stock_count = session.query(StockData).count()
        assert stock_count == 0  # No stock data yet


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
