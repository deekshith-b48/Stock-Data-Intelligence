"""
Database initialization script for Stock Data Intelligence Dashboard.

This script:
1. Creates all database tables from ORM models
2. Populates the database with sample Indian stock companies
3. Verifies the initialization was successful

Usage:
    python -m src.init_db
    
Or from project root:
    python src/init_db.py
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import get_database, init_database, Company

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sample Indian stock companies (5-10 major stocks)
SAMPLE_COMPANIES = [
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


def create_tables():
    """
    Create all database tables from ORM models.
    
    Uses the init_database() function which creates tables based on
    the SQLAlchemy Base metadata.
    """
    logger.info("Creating database tables...")
    init_database()
    logger.info("✓ Database tables created successfully")


def populate_sample_data():
    """
    Populate database with sample Indian stock companies.
    
    Inserts 10 major Indian stock companies into the companies table.
    Skips companies that already exist (based on unique symbol constraint).
    """
    logger.info("Populating sample company data...")
    
    db = get_database()
    
    with db.get_session() as session:
        # Check if companies already exist
        existing_count = session.query(Company).count()
        
        if existing_count > 0:
            logger.warning(f"Database already contains {existing_count} companies")
            response = input("Do you want to add more companies? (y/n): ").lower()
            if response != 'y':
                logger.info("Skipping sample data population")
                return
        
        # Add sample companies
        added_count = 0
        skipped_count = 0
        
        for company_data in SAMPLE_COMPANIES:
            # Check if company already exists
            existing = session.query(Company).filter_by(
                symbol=company_data["symbol"]
            ).first()
            
            if existing:
                logger.info(f"  - Skipped {company_data['symbol']} (already exists)")
                skipped_count += 1
            else:
                company = Company(
                    symbol=company_data["symbol"],
                    name=company_data["name"]
                )
                session.add(company)
                logger.info(f"  + Added {company_data['symbol']} - {company_data['name']}")
                added_count += 1
        
        # Commit is handled by context manager
    
    logger.info(f"✓ Sample data population complete")
    logger.info(f"  Added: {added_count} companies")
    logger.info(f"  Skipped: {skipped_count} companies")


def verify_initialization():
    """
    Verify that the database was initialized correctly.
    
    Checks:
    - Total number of companies in database
    - Lists all companies with their symbols and names
    """
    logger.info("Verifying database initialization...")
    
    db = get_database()
    
    with db.get_session() as session:
        # Count companies
        company_count = session.query(Company).count()
        logger.info(f"  Total companies in database: {company_count}")
        
        # List all companies
        if company_count > 0:
            logger.info("  Companies:")
            companies = session.query(Company).order_by(Company.symbol).all()
            for company in companies:
                logger.info(f"    - {company.symbol}: {company.name}")
        else:
            logger.warning("  No companies found in database")
    
    logger.info("✓ Database verification complete")


def main():
    """
    Main initialization workflow.
    
    Executes the following steps:
    1. Display database configuration
    2. Create tables from ORM models
    3. Populate sample company data
    4. Verify initialization
    """
    print("=" * 60)
    print("Stock Data Intelligence Dashboard - Database Initialization")
    print("=" * 60)
    print()
    
    # Display database configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./stock_dashboard.db')
    logger.info(f"Database URL: {database_url}")
    print()
    
    try:
        # Step 1: Create tables
        create_tables()
        print()
        
        # Step 2: Populate sample data
        populate_sample_data()
        print()
        
        # Step 3: Verify initialization
        verify_initialization()
        print()
        
        print("=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
