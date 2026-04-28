"""
Example usage of database connection and session management.

This script demonstrates:
- Initializing the database
- Creating and querying records
- Using context managers for session management
- Retry logic for connection failures
"""

import os
import sys
from datetime import date
from decimal import Decimal

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import get_database, init_database, Company, StockData


def main():
    """Demonstrate database connection and session management."""
    
    # Set database URL to use SQLite for this example
    os.environ['DATABASE_URL'] = 'sqlite:///./example_stock_dashboard.db'
    
    print("=== Database Connection Example ===\n")
    
    # Initialize database (creates tables)
    print("1. Initializing database...")
    init_database()
    print("   ✓ Database initialized\n")
    
    # Get database instance
    db = get_database()
    
    # Example 1: Using context manager for session management
    print("2. Creating a company record...")
    with db.get_session() as session:
        company = Company(symbol='RELIANCE', name='Reliance Industries Ltd.')
        session.add(company)
    print("   ✓ Company created: RELIANCE\n")
    
    # Example 2: Query the company
    print("3. Querying company...")
    with db.get_session() as session:
        result = session.query(Company).filter_by(symbol='RELIANCE').first()
        print(f"   Found: {result.symbol} - {result.name}")
        company_id = result.id
    print()
    
    # Example 3: Add stock data
    print("4. Adding stock data...")
    with db.get_session() as session:
        stock_data = StockData(
            company_id=company_id,
            date=date(2024, 1, 15),
            open=Decimal('2500.00'),
            high=Decimal('2550.00'),
            low=Decimal('2480.00'),
            close=Decimal('2530.00'),
            volume=5000000,
            daily_return=Decimal('1.2000'),
            moving_avg_7d=Decimal('2510.00'),
            volatility_score=Decimal('15.50')
        )
        session.add(stock_data)
    print("   ✓ Stock data added for 2024-01-15\n")
    
    # Example 4: Query stock data with relationship
    print("5. Querying stock data with company relationship...")
    with db.get_session() as session:
        stock = session.query(StockData).filter_by(company_id=company_id).first()
        print(f"   Date: {stock.date}")
        print(f"   Close: ₹{stock.close}")
        print(f"   Volume: {stock.volume:,}")
        print(f"   Company: {stock.company.name}")
    print()
    
    # Example 5: Using retry context manager
    print("6. Using retry context manager...")
    with db.get_session_with_retry_context(max_attempts=3) as session:
        companies = session.query(Company).all()
        print(f"   ✓ Found {len(companies)} companies in database\n")
    
    # Example 6: Demonstrate connection pooling info
    print("7. Connection pool information:")
    print(f"   Database URL: {db.database_url}")
    print(f"   Pool size: {db.pool_size}")
    print(f"   Max overflow: {db.max_overflow}")
    print()
    
    print("=== Example completed successfully ===")
    
    # Cleanup
    db.close()


if __name__ == '__main__':
    main()
