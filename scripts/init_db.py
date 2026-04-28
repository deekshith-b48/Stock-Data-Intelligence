"""
Database initialization script for Stock Data Intelligence Dashboard.

This script:
1. Creates all database tables from ORM models
2. Populates the database with sample Indian stock companies
3. Verifies the initialization was successful

Usage:
    python scripts/init_db.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import get_database, init_database, Company


# Sample Indian stock companies
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
    """Create all database tables from ORM models."""
    print("Creating database tables...")
    init_database()
    print("✓ Database tables created successfully\n")


def populate_sample_data():
    """Populate database with sample Indian stock companies."""
    print("Populating sample company data...")
    
    db = get_database()
    
    with db.get_session() as session:
        # Check if companies already exist
        existing_count = session.query(Company).count()
        
        if existing_count > 0:
            print(f"⚠ Database already contains {existing_count} companies")
            response = input("Do you want to add more companies? (y/n): ").lower()
            if response != 'y':
                print("Skipping sample data population")
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
                print(f"  - Skipped {company_data['symbol']} (already exists)")
                skipped_count += 1
            else:
                company = Company(
                    symbol=company_data["symbol"],
                    name=company_data["name"]
                )
                session.add(company)
                print(f"  + Added {company_data['symbol']} - {company_data['name']}")
                added_count += 1
        
        # Commit is handled by context manager
    
    print(f"\n✓ Sample data population complete")
    print(f"  Added: {added_count} companies")
    print(f"  Skipped: {skipped_count} companies\n")


def verify_initialization():
    """Verify that the database was initialized correctly."""
    print("Verifying database initialization...")
    
    db = get_database()
    
    with db.get_session() as session:
        # Count companies
        company_count = session.query(Company).count()
        print(f"  Total companies in database: {company_count}")
        
        # List all companies
        if company_count > 0:
            print("\n  Companies:")
            companies = session.query(Company).order_by(Company.symbol).all()
            for company in companies:
                print(f"    - {company.symbol}: {company.name}")
        
    print("\n✓ Database verification complete\n")


def main():
    """Main initialization workflow."""
    print("=" * 60)
    print("Stock Data Intelligence Dashboard - Database Initialization")
    print("=" * 60)
    print()
    
    # Display database configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./stock_dashboard.db')
    print(f"Database URL: {database_url}")
    print()
    
    try:
        # Step 1: Create tables
        create_tables()
        
        # Step 2: Populate sample data
        populate_sample_data()
        
        # Step 3: Verify initialization
        verify_initialization()
        
        print("=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
