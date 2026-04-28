"""
Example demonstrating financial metrics calculation.

This script shows how to use the DataProcessor class to:
1. Clean stock data
2. Calculate daily returns
3. Calculate moving averages
4. Calculate 52-week statistics

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
"""

import pandas as pd
from datetime import date, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import DataProcessor


def main():
    """Demonstrate financial metrics calculation."""
    
    # Initialize processor
    processor = DataProcessor()
    
    # Create sample stock data (1 year of data)
    print("Creating sample stock data...")
    start_date = date(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # Simulate stock prices with some volatility
    import random
    random.seed(42)
    base_price = 100.0
    prices = []
    for i in range(365):
        # Add some random walk
        change = random.uniform(-2, 2)
        base_price = max(50, base_price + change)  # Keep price above 50
        prices.append(base_price)
    
    # Create DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': [p * 0.99 for p in prices],
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': [random.randint(1000000, 5000000) for _ in range(365)]
    })
    
    print(f"Created {len(data)} days of stock data")
    print(f"Date range: {data['date'].min()} to {data['date'].max()}")
    print()
    
    # Step 1: Clean the data
    print("Step 1: Cleaning data...")
    clean_data = processor.clean_data(data, 'EXAMPLE')
    print(f"Clean data: {len(clean_data)} records")
    print()
    
    # Step 2: Calculate daily returns
    print("Step 2: Calculating daily returns...")
    data_with_returns = processor.calculate_daily_return(clean_data)
    print(f"Daily returns calculated for {data_with_returns['daily_return'].notna().sum()} records")
    print("\nSample daily returns:")
    print(data_with_returns[['date', 'close', 'daily_return']].head(10))
    print()
    
    # Step 3: Calculate moving averages
    print("Step 3: Calculating 7-day moving averages...")
    data_with_ma = processor.calculate_moving_average(data_with_returns, window=7)
    print(f"Moving averages calculated for {data_with_ma['moving_avg_7d'].notna().sum()} records")
    print("\nSample moving averages:")
    print(data_with_ma[['date', 'close', 'moving_avg_7d']].tail(10))
    print()
    
    # Step 4: Calculate 52-week statistics
    print("Step 4: Calculating 52-week statistics...")
    stats = processor.calculate_52_week_stats(data_with_ma)
    print("\n52-Week Statistics:")
    print(f"  High: ${stats['52_week_high']:.2f}")
    print(f"  Low:  ${stats['52_week_low']:.2f}")
    print(f"  Avg:  ${stats['avg_close']:.2f}")
    print()
    
    # Summary statistics
    print("Summary Statistics:")
    print(f"  Total records: {len(data_with_ma)}")
    print(f"  Valid daily returns: {data_with_ma['daily_return'].notna().sum()}")
    print(f"  Valid moving averages: {data_with_ma['moving_avg_7d'].notna().sum()}")
    print(f"  Average daily return: {data_with_ma['daily_return'].mean():.2f}%")
    print(f"  Max daily return: {data_with_ma['daily_return'].max():.2f}%")
    print(f"  Min daily return: {data_with_ma['daily_return'].min():.2f}%")
    print()
    
    # Show final data structure
    print("Final data structure (last 5 records):")
    print(data_with_ma[['date', 'close', 'daily_return', 'moving_avg_7d']].tail())


if __name__ == '__main__':
    main()
