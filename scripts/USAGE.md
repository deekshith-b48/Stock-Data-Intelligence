# Database Initialization - Quick Start Guide

## Overview

The `init_db.py` script initializes the Stock Data Intelligence Dashboard database with tables and sample data.

## Quick Start

```bash
# Initialize database with default settings (SQLite)
python3 scripts/init_db.py
```

## What It Does

1. **Creates Tables**: Sets up the database schema from ORM models
   - `companies` table: Stores stock company information
   - `stock_data` table: Stores daily stock market data and metrics

2. **Adds Sample Data**: Populates 10 Indian stock companies:
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

3. **Verifies Setup**: Confirms tables and data were created successfully

## Configuration

### Using SQLite (Default)

```bash
# Uses sqlite:///./stock_dashboard.db
python3 scripts/init_db.py
```

### Using PostgreSQL

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/stock_dashboard"
python3 scripts/init_db.py
```

### Using .env File

Create a `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/stock_dashboard
```

Then run:
```bash
python3 scripts/init_db.py
```

## Expected Output

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
  + Added INFY - Infosys Ltd.
  + Added HDFCBANK - HDFC Bank Ltd.
  + Added ICICIBANK - ICICI Bank Ltd.
  + Added HINDUNILVR - Hindustan Unilever Ltd.
  + Added BHARTIARTL - Bharti Airtel Ltd.
  + Added ITC - ITC Ltd.
  + Added SBIN - State Bank of India
  + Added WIPRO - Wipro Ltd.

✓ Sample data population complete
  Added: 10 companies
  Skipped: 0 companies

Verifying database initialization...
  Total companies in database: 10

  Companies:
    - BHARTIARTL: Bharti Airtel Ltd.
    - HDFCBANK: HDFC Bank Ltd.
    - HINDUNILVR: Hindustan Unilever Ltd.
    - ICICIBANK: ICICI Bank Ltd.
    - INFY: Infosys Ltd.
    - ITC: ITC Ltd.
    - RELIANCE: Reliance Industries Ltd.
    - SBIN: State Bank of India
    - TCS: Tata Consultancy Services Ltd.
    - WIPRO: Wipro Ltd.

✓ Database verification complete

============================================================
Database initialization completed successfully!
============================================================
```

## Running Multiple Times

The script is **idempotent** - safe to run multiple times:

- If tables already exist, they won't be recreated
- If companies already exist, you'll be prompted:
  ```
  ⚠ Database already contains 10 companies
  Do you want to add more companies? (y/n):
  ```

## Troubleshooting

### Error: "No module named 'src'"

Make sure you're running from the project root directory:
```bash
cd /path/to/Stock\ Data\ Intelligence\ Dashboard
python3 scripts/init_db.py
```

### Error: "Could not connect to database"

Check your DATABASE_URL:
```bash
echo $DATABASE_URL
```

For PostgreSQL, ensure:
- PostgreSQL server is running
- Database exists
- Credentials are correct
- Network access is allowed

### Error: "Permission denied"

Ensure you have write permissions:
```bash
# For SQLite
ls -la stock_dashboard.db

# For PostgreSQL
psql -U user -d stock_dashboard -c "SELECT 1"
```

## Next Steps

After initialization:

1. **Verify the database**:
   ```bash
   python3 examples/database_usage.py
   ```

2. **Run tests**:
   ```bash
   python3 -m pytest tests/test_init_db.py -v
   ```

3. **Start collecting stock data** (when data collector is implemented):
   ```bash
   python3 scripts/collect_data.py
   ```

## Related Files

- `src/models/database.py` - ORM model definitions
- `src/models/connection.py` - Database connection management
- `tests/test_init_db.py` - Unit tests for initialization
- `examples/database_usage.py` - Example database operations
