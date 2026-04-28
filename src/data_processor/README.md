# Data Processor Module

The Data Processor module provides functionality for cleaning, validating, and transforming raw stock market data.

## Features

- **Data Cleaning**: Handle missing values using forward-fill method
- **Validation**: Validate numeric fields (prices and volume must be positive)
- **Duplicate Removal**: Remove duplicate records based on date
- **Date Formatting**: Convert dates to ISO 8601 format (YYYY-MM-DD)
- **Integrity Checks**: Validate data integrity (high >= low, etc.)
- **Comprehensive Logging**: Log invalid records and data quality issues

## Requirements

This module implements the following requirements:
- **2.1**: Handle missing values using forward-fill or interpolation methods
- **2.2**: Convert all date fields to ISO 8601 format (YYYY-MM-DD)
- **2.3**: Validate that numeric fields (prices, volume) contain valid positive numbers
- **2.4**: Log invalid records and exclude them from storage
- **2.5**: Remove duplicate records based on stock symbol and date combination

## Usage

### Basic Usage

```python
from src.data_processor import DataProcessor
import pandas as pd

# Create processor instance
processor = DataProcessor()

# Clean your data
raw_data = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
    'open': [100.0, 101.0, 102.0],
    'high': [105.0, 106.0, 107.0],
    'low': [99.0, 100.0, 101.0],
    'close': [103.0, 104.0, 105.0],
    'volume': [1000, 2000, 3000]
})

cleaned_data = processor.clean_data(raw_data, symbol='AAPL')
```

### Integration with Data Collector

```python
from src.data_collector import DataCollector
from src.data_processor import DataProcessor
from datetime import date, timedelta

# Initialize components
collector = DataCollector()
processor = DataProcessor()

# Fetch data
end_date = date.today()
start_date = end_date - timedelta(days=30)
raw_data = collector.fetch_stock_data('RELIANCE.NS', start_date, end_date)

# Clean data
cleaned_data = processor.clean_data(raw_data, symbol='RELIANCE.NS')

print(f"Fetched {len(raw_data)} records, cleaned to {len(cleaned_data)} records")
```

## Data Cleaning Process

The `clean_data` method performs the following operations in order:

1. **Date Conversion**: Convert dates to ISO 8601 format (YYYY-MM-DD)
   - Handles various date formats
   - Removes records with invalid dates

2. **Numeric Conversion**: Convert all numeric fields to proper numeric types
   - Coerces invalid values to NaN

3. **Sorting**: Sort data by date in ascending order
   - Required for forward-fill to work correctly

4. **Missing Value Handling**: Fill missing values using forward-fill
   - Forward-fill: Use previous valid value
   - Backward-fill: For values at the beginning with no previous value
   - Drop rows with unfillable missing values

5. **Numeric Validation**: Validate that all prices and volume are positive
   - Removes records with zero or negative values
   - Logs invalid records for debugging

6. **Duplicate Removal**: Remove duplicate records based on date
   - Keeps the first occurrence
   - Logs removed duplicates

7. **Integrity Validation**: Check data integrity constraints
   - High >= Low
   - High >= Open
   - High >= Close
   - Low <= Open
   - Low <= Close

## Data Quality Metrics

The processor logs comprehensive data quality metrics:

- Number of records processed
- Number of invalid records removed
- Percentage of data quality
- Breakdown of issues (duplicates, missing values, invalid values, integrity violations)

## Example Output

```
INFO: Starting data cleaning for RELIANCE.NS: 30 records
WARNING: Invalid open value for RELIANCE.NS at index 5: -50.0 (must be positive)
WARNING: Duplicate record for RELIANCE.NS for date 2024-01-15: removing duplicate at index 12
INFO: Removed 1 duplicate records for RELIANCE.NS
INFO: Data cleaning complete for RELIANCE.NS: 28 valid records, 2 invalid records removed (6.7% removed)
```

## Testing

Run the unit tests:

```bash
pytest tests/test_data_processor.py -v
```

Run the example scripts:

```bash
# Test processor with sample data
PYTHONPATH=. python examples/test_processor.py

# Test integration with collector
PYTHONPATH=. python examples/test_collector_and_processor.py
```

## API Reference

### DataProcessor

#### `__init__()`

Initialize the DataProcessor.

#### `clean_data(df: pd.DataFrame, symbol: Optional[str] = None) -> pd.DataFrame`

Clean and validate stock data.

**Parameters:**
- `df` (pd.DataFrame): DataFrame with columns [date, open, high, low, close, volume]
- `symbol` (str, optional): Stock symbol for logging purposes

**Returns:**
- `pd.DataFrame`: Cleaned DataFrame with same columns. Invalid records are excluded.

**Example:**
```python
processor = DataProcessor()
cleaned = processor.clean_data(raw_data, symbol='AAPL')
```

## Error Handling

The processor handles various data quality issues:

- **Invalid dates**: Logged and removed
- **Missing values**: Forward-filled when possible, otherwise removed
- **Negative/zero values**: Logged and removed
- **Duplicates**: Logged and removed (keeps first occurrence)
- **Integrity violations**: Logged and removed

All issues are logged with detailed information for debugging and monitoring.

## Performance Considerations

- The processor creates a copy of the input DataFrame to avoid modifying the original
- Operations are performed in-place on the copy for efficiency
- Sorting is performed once before missing value handling
- Validation checks are vectorized using pandas operations

## Future Enhancements

Planned enhancements for future versions:

- Support for interpolation methods (linear, polynomial)
- Configurable missing value handling strategies
- Outlier detection and handling
- Data normalization options
- Support for additional data integrity checks
