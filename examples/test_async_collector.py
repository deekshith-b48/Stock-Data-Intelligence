"""
Example script to test AsyncDataCollector functionality.

This script demonstrates concurrent fetching of multiple stock symbols
using the AsyncDataCollector class.
"""

import asyncio
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collector import AsyncDataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Test async data collection for multiple stocks."""
    # Initialize async collector
    collector = AsyncDataCollector(max_concurrent=10, max_retries=3)
    
    # Define test symbols (using US stocks for reliability)
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    
    # Define date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nFetching data for {len(symbols)} symbols concurrently...")
    print(f"Date range: {start_date} to {end_date}\n")
    
    # Fetch data concurrently
    results = await collector.fetch_multiple_stocks(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    for symbol, data in results.items():
        if not data.empty:
            print(f"\n{symbol}:")
            print(f"  Records: {len(data)}")
            print(f"  Date range: {data['date'].min()} to {data['date'].max()}")
            print(f"  Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        else:
            print(f"\n{symbol}: No data retrieved")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())
