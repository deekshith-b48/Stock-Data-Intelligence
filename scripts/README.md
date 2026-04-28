# Database Scripts

This directory contains utility scripts for database management and data collection.

## collect_data.py

End-to-end data collection script that fetches, processes, and stores stock market data.

### Features

- Fetches stock data from yfinance API for multiple symbols concurrently
- Cleans and validates raw data (handles missing values, removes duplicates)
- Calculates financial metrics:
  - Daily return percentage
  - 7-day moving average
  - 30-day volatility score
- Stores processed data in database with duplicate handling
- Comprehensive logging of success/failure for each symbol
- Supports custom date ranges and symbol lists

### Usage

```bash
# Using default symbols and date range (last 1 year)
python scripts/collect_data.py

# Using custom symbols via environment variable
export STOCK_SYMBOLS="AAPL,GOOGL,MSFT"
python scripts/collect_data.py

# Using PostgreSQL (set DATABASE_URL environment variable)
export DATABASE_URL="postgresql://user:password@localhost:5432/stock_dashboard"
python scripts/collect_data.py

# Set log level
export LOG_LEVEL="DEBUG"
python scripts/collect_data.py
```

### Default Symbols

The script collects data for 10 Indian stocks by default:
- RELIANCE.NS (Reliance Industries)
- TCS.NS (Tata Consultancy Services)
- INFY.NS (Infosys)
- HDFCBANK.NS (HDFC Bank)
- ICICIBANK.NS (ICICI Bank)
- HINDUNILVR.NS (Hindustan Unilever)
- ITC.NS (ITC Limited)
- SBIN.NS (State Bank of India)
- BHARTIARTL.NS (Bharti Airtel)
- KOTAKBANK.NS (Kotak Mahindra Bank)

### Output

The script will:
1. Initialize database (create tables if needed)
2. Fetch data concurrently for all symbols
3. Process and calculate metrics for each symbol
4. Store data in database (skip duplicates)
5. Display summary statistics

### Example Output

```
================================================================================
STOCK DATA COLLECTION SCRIPT
================================================================================

Initializing database...
Database initialized successfully
Using default symbols: ['RELIANCE.NS', 'TCS.NS', ...]

Starting data collection for 10 symbols
Date range: 2025-04-27 to 2026-04-27

Step 1: Fetching stock data from external APIs...
Concurrent fetch complete in 1.28 seconds: 10 successful, 0 failed

Step 2: Processing and storing data...
✓ RELIANCE.NS: Successfully stored 246 records (0 duplicates skipped, 0 failed)
✓ TCS.NS: Successfully stored 246 records (0 duplicates skipped, 0 failed)
...

================================================================================
DATA COLLECTION SUMMARY
================================================================================
Total symbols: 10
Successful: 10
Failed: 0
Success rate: 100.0%
================================================================================

Per-symbol details:
✓ RELIANCE.NS: fetched=247, stored=246
✓ TCS.NS: fetched=247, stored=246
...

✓ Data collection completed successfully!
```

### Requirements

- Python 3.9+
- yfinance
- pandas
- SQLAlchemy
- All dependencies from `requirements.txt`

### Notes

- The script handles duplicates gracefully (skips existing records)
- Failed symbols don't block processing of other symbols
- All operations are logged to `app.log` and console
- The script is designed to be run periodically (e.g., daily via cron)
- Concurrent fetching is limited to 10 requests to respect API rate limits

## init_db.py

Database initialization script that creates tables and populates sample data.

### Features

- Creates all database tables from SQLAlchemy ORM models
- Populates database with 10 sample Indian stock companies:
  - RELIANCE (Reliance Industries Ltd.)
  - TCS (Tata Consultancy Services Ltd.)
  - INFY (Infosys Ltd.)
  - HDFCBANK (HDFC Bank Ltd.)
  - ICICIBANK (ICICI Bank Ltd.)
  - HINDUNILVR (Hindustan Unilever Ltd.)
  - BHARTIARTL (Bharti Airtel Ltd.)
  - ITC (ITC Ltd.)
  - SBIN (State Bank of India)
  - WIPRO (Wipro Ltd.)
- Verifies initialization was successful
- Handles existing data gracefully (prompts before adding duplicates)

### Usage

```bash
# Using default SQLite database
python scripts/init_db.py

# Using PostgreSQL (set DATABASE_URL environment variable)
export DATABASE_URL="postgresql://user:password@localhost:5432/stock_dashboard"
python scripts/init_db.py
```

### Output

The script will:
1. Display the database URL being used
2. Create all necessary tables
3. Add sample company data (or skip if already exists)
4. Verify and list all companies in the database

### Example Output

```
============================================================
Stock Data Intelligence Dashboard - Database Initialization
============================================================

Database URL: sqlite:///./stock_dashboard.db

Creating database tables...
✓ Database tables created successfully

Populating sample company data...
  + Added RELIANCE - Reliance Industries Ltd.
  + Added TCS - Tata Consultancy Services Ltd.
  ...

✓ Sample data population complete
  Added: 10 companies
  Skipped: 0 companies

Verifying database initialization...
  Total companies in database: 10

  Companies:
    - BHARTIARTL: Bharti Airtel Ltd.
    - HDFCBANK: HDFC Bank Ltd.
    ...

✓ Database verification complete

============================================================
Database initialization completed successfully!
============================================================
```

### Requirements

- Python 3.9+
- SQLAlchemy
- All dependencies from `requirements.txt`

### Notes

- The script is idempotent - it can be run multiple times safely
- If companies already exist, the script will prompt before adding more
- The script uses the `DATABASE_URL` environment variable or defaults to SQLite
- Tables are created using SQLAlchemy's `create_all()` method
