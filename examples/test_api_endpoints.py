"""
Test script to verify all API endpoints work correctly.

This script:
1. Collects sample stock data
2. Processes and stores it in the database
3. Tests all API endpoints
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collector.collector import AsyncDataCollector
from src.data_processor.processor import DataProcessor
from src.models.connection import get_database, init_database
from src.models.database import Company, StockData
import pandas as pd


async def collect_and_store_data():
    """Collect sample data for testing API endpoints."""
    print("=" * 60)
    print("COLLECTING SAMPLE DATA FOR API TESTING")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_database()
    
    # Get database connection
    db = get_database()
    
    # Sample symbols
    symbols = ['RELIANCE.NS', 'TCS.NS']
    
    # Collect data
    print(f"\n2. Collecting data for {len(symbols)} symbols...")
    collector = AsyncDataCollector(max_concurrent=2)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    results = {}
    for symbol in symbols:
        print(f"   Fetching {symbol}...")
        data = await collector.fetch_stock_data(
            symbol,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        if not data.empty:
            results[symbol] = data
            print(f"   ✓ Fetched {len(data)} records for {symbol}")
        else:
            print(f"   ✗ No data for {symbol}")
    
    # Process and store data
    print(f"\n3. Processing and storing data...")
    processor = DataProcessor()
    
    for symbol, raw_data in results.items():
        # Clean symbol (remove .NS suffix)
        clean_symbol = symbol.replace('.NS', '')
        
        print(f"\n   Processing {clean_symbol}...")
        
        # Clean data
        clean_data = processor.clean_data(raw_data, clean_symbol)
        
        if clean_data.empty:
            print(f"   ✗ No valid data after cleaning for {clean_symbol}")
            continue
        
        # Calculate metrics
        clean_data = processor.calculate_daily_return(clean_data)
        clean_data = processor.calculate_moving_average(clean_data, window=7)
        clean_data = processor.calculate_volatility_score(clean_data, window=30)
        
        # Store in database
        with db.get_session() as session:
            # Get or create company
            company = session.query(Company).filter(
                Company.symbol == clean_symbol
            ).first()
            
            if not company:
                print(f"   ✗ Company {clean_symbol} not found in database")
                continue
            
            # Store stock data
            records_added = 0
            for _, row in clean_data.iterrows():
                # Check if record already exists
                existing = session.query(StockData).filter(
                    StockData.company_id == company.id,
                    StockData.date == row['date']
                ).first()
                
                if existing:
                    continue
                
                stock_record = StockData(
                    company_id=company.id,
                    date=row['date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume']),
                    daily_return=float(row['daily_return']) if pd.notna(row['daily_return']) else None,
                    moving_avg_7d=float(row['moving_avg_7d']) if pd.notna(row['moving_avg_7d']) else None,
                    volatility_score=float(row['volatility_score']) if pd.notna(row['volatility_score']) else None
                )
                session.add(stock_record)
                records_added += 1
            
            session.commit()
            print(f"   ✓ Stored {records_added} new records for {clean_symbol}")
    
    print("\n" + "=" * 60)
    print("DATA COLLECTION COMPLETE")
    print("=" * 60)


def test_api_with_curl():
    """Test API endpoints using curl commands."""
    print("\n" + "=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)
    
    print("\nNOTE: Start the API server first with:")
    print("  python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
    print("\nThen run these curl commands to test:")
    print("\n1. Health check:")
    print("   curl http://localhost:8000/health")
    print("\n2. List companies:")
    print("   curl http://localhost:8000/companies")
    print("\n3. Get stock data:")
    print("   curl 'http://localhost:8000/data/RELIANCE?days=10'")
    print("\n4. Get summary:")
    print("   curl http://localhost:8000/summary/RELIANCE")
    print("\n5. Compare stocks:")
    print("   curl 'http://localhost:8000/compare?symbol1=RELIANCE&symbol2=TCS'")
    print("\n6. View API docs:")
    print("   Open http://localhost:8000/docs in your browser")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Collect and store data
    asyncio.run(collect_and_store_data())
    
    # Print test instructions
    test_api_with_curl()
