"""
Example script demonstrating the integration of DataCollector and DataProcessor.

This script shows the complete data pipeline:
1. Fetch stock data using DataCollector
2. Clean and validate data using DataProcessor
3. Display results and statistics
"""

import asyncio
from datetime import date, timedelta
from src.data_collector import DataCollector
from src.data_processor import DataProcessor


async def main():
    """Demonstrate the complete data collection and processing pipeline."""
    
    print("="*70)
    print("Stock Data Collection and Processing Pipeline Demo")
    print("="*70)
    
    # Initialize components
    collector = DataCollector(max_retries=3)
    processor = DataProcessor()
    
    # Define test symbols (using .NS suffix for NSE stocks)
    symbols = ['RELIANCE.NS', 'TCS.NS']
    
    # Define date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nFetching data for: {', '.join(symbols)}")
    print(f"Date range: {start_date} to {end_date}")
    print("\n" + "="*70)
    
    # Step 1: Collect data
    print("STEP 1: Collecting data from yfinance...")
    print("="*70)
    
    results = {}
    for symbol in symbols:
        print(f"\nFetching {symbol}...")
        raw_data = collector.fetch_stock_data(symbol, start_date, end_date)
        results[symbol] = raw_data
        
        if not raw_data.empty:
            print(f"✓ Fetched {len(raw_data)} records for {symbol}")
        else:
            print(f"✗ Failed to fetch data for {symbol}")
    
    # Step 2: Process data
    print("\n" + "="*70)
    print("STEP 2: Cleaning and validating data...")
    print("="*70)
    
    cleaned_results = {}
    for symbol, raw_data in results.items():
        if raw_data.empty:
            print(f"\n✗ Skipping {symbol} (no data)")
            continue
        
        print(f"\nProcessing {symbol}...")
        print(f"  Raw records: {len(raw_data)}")
        
        cleaned_data = processor.clean_data(raw_data, symbol)
        cleaned_results[symbol] = cleaned_data
        
        print(f"  Clean records: {len(cleaned_data)}")
        print(f"  Data quality: {len(cleaned_data)/len(raw_data)*100:.1f}%")
        
        if not cleaned_data.empty:
            print(f"  Date range: {cleaned_data['date'].min()} to {cleaned_data['date'].max()}")
            print(f"  Price range: ${cleaned_data['close'].min():.2f} - ${cleaned_data['close'].max():.2f}")
    
    # Step 3: Display summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    total_raw = sum(len(df) for df in results.values())
    total_clean = sum(len(df) for df in cleaned_results.values())
    
    print(f"\nTotal symbols processed: {len(symbols)}")
    print(f"Successful fetches: {sum(1 for df in results.values() if not df.empty)}")
    print(f"Total raw records: {total_raw}")
    print(f"Total clean records: {total_clean}")
    print(f"Overall data quality: {total_clean/total_raw*100:.1f}%" if total_raw > 0 else "N/A")
    
    # Display sample data
    if cleaned_results:
        print("\n" + "="*70)
        print("SAMPLE DATA (First 5 records)")
        print("="*70)
        
        for symbol, data in cleaned_results.items():
            if not data.empty:
                print(f"\n{symbol}:")
                print(data.head())
    
    print("\n" + "="*70)
    print("Pipeline demo complete!")
    print("="*70)


if __name__ == '__main__':
    asyncio.run(main())
