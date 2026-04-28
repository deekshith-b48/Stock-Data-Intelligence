# Data Collector Module

The Data Collector module is responsible for fetching stock market data from external sources (yfinance API) with comprehensive error handling, logging, and retry logic.

## Features

- **Fetch Historical Stock Data**: Retrieve OHLCV (Open, High, Low, Close, Volume) data for any stock symbol
- **Retry Logic with Exponential Backoff**: Automatically retries failed requests with increasing delays (1s, 2s, 4s)
- **Error Handling**: Comprehensive error handling with detailed logging
- **Multiple Stock Support**: Fetch data for multiple stocks sequentially
- **Flexible Date Ranges**: Specify custom date ranges or use defaults (1 year)

## Requirements

This module implements the following requirements:
- **1.1**: Fetch stock data from yfinance API
- **1.2**: Retrieve historical stock data for configured companies
- **1.3**: Store raw stock data (date, open, high, low, close, volume)
- **1.4**: Log errors with source name and timestamp

## Usage

### Basic Usage

```python
from datetime import date, timedelta
from src.data_collector import DataCollector

# Initialize collector
collector = DataCollector()

# Fetch data for a single stock
end_date = date.today()
start_date = end_date - timedelta(days=365)  # Last year

data = collector.fetch_stock_data('AAPL', start_date, end_date)
print(f"Fetched {len(data)} records")
print(data.head())
```

### Fetching Multiple Stocks

```python
# Fetch data for multiple stocks
symbols = ['AAPL', 'GOOGL', 'MSFT']
results = collector.fetch_multiple_stocks(symbols, start_date, end_date)

for symbol, data in results.items():
    if not data.empty:
        print(f"{symbol}: {len(data)} records")
    else:
        print(f"{symbol}: Failed to fetch")
```

### Indian Stocks (NSE/BSE)

```python
# For NSE stocks, add .NS suffix
# For BSE stocks, add .BO suffix
indian_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
results = collector.fetch_multiple_stocks(indian_symbols)
```

### Custom Retry Configuration

```python
# Configure custom retry attempts
collector = DataCollector(max_retries=5)
data = collector.fetch_stock_data('AAPL')
```

## Data Format

The returned DataFrame contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| date | date | Trading date |
| open | float | Opening price |
| high | float | Highest price of the day |
| low | float | Lowest price of the day |
| close | float | Closing price |
| volume | int | Trading volume |

## Error Handling

The collector implements robust error handling:

1. **Retry Logic**: Failed requests are automatically retried up to `max_retries` times
2. **Exponential Backoff**: Wait times increase exponentially (1s, 2s, 4s, ...)
3. **Detailed Logging**: All errors are logged with timestamps and source information
4. **Graceful Degradation**: Returns empty DataFrame if all retries fail, allowing processing to continue

## Logging

The module uses Python's standard logging framework. Configure logging in your application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Log levels:
- **INFO**: Successful operations, retry attempts
- **WARNING**: Empty data responses, partial failures
- **ERROR**: API failures, exceptions

## Testing

### Unit Tests

Run the unit tests:

```bash
pytest tests/test_data_collector.py -v
```

### Live Integration Test

Test with real API calls (requires internet):

```bash
python examples/test_collector_live.py
```

## Implementation Details

### Retry Logic

The retry mechanism uses exponential backoff:
- Attempt 1: Immediate
- Attempt 2: Wait 1 second (2^0)
- Attempt 3: Wait 2 seconds (2^1)
- Attempt 4: Wait 4 seconds (2^2)
- And so on...

### API Integration

The module uses the `yfinance` library to fetch data from Yahoo Finance API:
- No API key required
- No rate limiting for basic usage
- Supports global stock markets
- Historical data available

### Data Processing

Raw data from yfinance is processed to match our schema:
1. Reset index to make Date a column
2. Rename columns to lowercase (Date → date, Open → open, etc.)
3. Select only required columns (filters out Dividends, Stock Splits, etc.)
4. Convert date column to date type (removes time component)

## Future Enhancements

Potential improvements for future iterations:
- Async/concurrent fetching for better performance (Task 3.2)
- Support for Alpha Vantage API as fallback
- CSV bhavcopy parsing for NSE/BSE data (Task 3.3)
- Caching to reduce API calls
- Rate limiting to respect API quotas

## Related Modules

- **Data Processor**: Cleans and calculates metrics on collected data
- **Database Models**: Stores processed data in database
- **API Server**: Exposes collected data via REST endpoints
