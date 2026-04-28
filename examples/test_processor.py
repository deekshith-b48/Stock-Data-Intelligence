"""
Example script to test the data processor with sample data.

This script demonstrates:
- Creating sample stock data
- Cleaning data with the DataProcessor
- Handling various data quality issues
"""

import pandas as pd
from datetime import date
from src.data_processor import DataProcessor


def main():
    """Test the data processor with sample data."""
    
    # Create sample data with various issues
    print("Creating sample stock data with quality issues...")
    sample_data = pd.DataFrame({
        'date': [
            '2024-01-01', '2024-01-02', '2024-01-02',  # Duplicate date
            '2024-01-03', '2024-01-04', '2024-01-05',
            '2024-01-06'
        ],
        'open': [100.0, 101.0, 101.5, None, 103.0, -50.0, 105.0],  # Missing and negative
        'high': [105.0, 106.0, 106.5, 108.0, 109.0, 110.0, 111.0],
        'low': [99.0, 100.0, 100.5, 101.0, 102.0, 103.0, 104.0],
        'close': [103.0, 104.0, 104.5, 105.0, 106.0, 107.0, 108.0],
        'volume': [1000, 2000, 2500, 3000, 4000, 5000, 6000]
    })
    
    print(f"\nOriginal data ({len(sample_data)} records):")
    print(sample_data)
    print("\nData issues:")
    print("- Row 2: Duplicate date (2024-01-02)")
    print("- Row 3: Missing 'open' value")
    print("- Row 5: Negative 'open' value (-50.0)")
    
    # Create processor and clean data
    processor = DataProcessor()
    print("\n" + "="*70)
    print("Cleaning data...")
    print("="*70)
    
    cleaned_data = processor.clean_data(sample_data, 'SAMPLE')
    
    print("\n" + "="*70)
    print(f"Cleaned data ({len(cleaned_data)} records):")
    print("="*70)
    print(cleaned_data)
    
    print("\n" + "="*70)
    print("Summary:")
    print("="*70)
    print(f"Original records: {len(sample_data)}")
    print(f"Cleaned records: {len(cleaned_data)}")
    print(f"Records removed: {len(sample_data) - len(cleaned_data)}")
    print(f"Data quality: {len(cleaned_data)/len(sample_data)*100:.1f}%")
    
    # Verify data integrity
    print("\n" + "="*70)
    print("Data Integrity Checks:")
    print("="*70)
    print(f"✓ All dates are unique: {cleaned_data['date'].is_unique}")
    print(f"✓ All prices are positive: {(cleaned_data[['open', 'high', 'low', 'close']] > 0).all().all()}")
    print(f"✓ All volumes are positive: {(cleaned_data['volume'] > 0).all()}")
    print(f"✓ No missing values: {cleaned_data.isnull().sum().sum() == 0}")
    print(f"✓ High >= Low: {(cleaned_data['high'] >= cleaned_data['low']).all()}")
    print(f"✓ Data is sorted by date: {cleaned_data['date'].is_monotonic_increasing}")


if __name__ == '__main__':
    main()
