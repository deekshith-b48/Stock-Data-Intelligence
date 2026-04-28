# Database Models Module

This module provides database models and connection management for the Stock Data Intelligence Dashboard.

## Components

### 1. Database Models (`database.py`)

SQLAlchemy ORM models for the application:

- **Company**: Stores company information (symbol, name)
- **StockData**: Stores daily stock data with calculated metrics

### 2. Database Connection (`connection.py`)

Manages database connections with the following features:

- **Connection Pooling**: Configurable pool size (5-20 connections)
- **Retry Logic**: Exponential backoff with 3 attempts (1s, 2s, 4s)
- **Multi-Database Support**: PostgreSQL (production) and SQLite (development)
- **Session Management**: Context managers for safe session handling

## Usage

### Basic Setup

```python
from src.models import get_database, init_database

# Initialize database (creates tables)
init_database()

# Get database instance
db = get_database()
```

### Using Sessions

#### Simple Context Manager

```python
from src.models import Company

with db.get_session() as session:
    company = Company(symbol='RELIANCE', name='Reliance Industries Ltd.')
    session.add(company)
    # Automatically commits on success, rolls back on error
```

#### Retry Context Manager

```python
# Automatically retries on connection failures
with db.get_session_with_retry_context(max_attempts=3) as session:
    companies = session.query(Company).all()
```

### Configuration

Set environment variables to configure the database:

```bash
# PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost:5432/stock_dashboard
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# SQLite (development)
DATABASE_URL=sqlite:///./stock_dashboard.db
```

## Features

### Connection Pooling

- **PostgreSQL**: Uses QueuePool with configurable size
- **SQLite**: Uses StaticPool for single-threaded access
- **Pool Pre-Ping**: Verifies connections before use
- **Connection Recycling**: Recycles connections after 1 hour

### Retry Logic

The retry mechanism handles transient connection failures:

1. **Attempt 1**: Immediate connection
2. **Attempt 2**: Wait 1 second, retry
3. **Attempt 3**: Wait 2 seconds, retry
4. **Attempt 4**: Wait 4 seconds, retry (if max_attempts > 3)

### Error Handling

- Automatic session rollback on errors
- Comprehensive logging of connection issues
- Graceful handling of connection failures

## Testing

Run the test suite:

```bash
# Test connection module
pytest tests/test_connection.py -v

# Test database models
pytest tests/test_models.py -v

# Run all tests
pytest tests/ -v
```

## Examples

See `examples/database_usage.py` for a complete working example.

## Requirements

- SQLAlchemy 2.0+
- psycopg2-binary (for PostgreSQL)
- python-dotenv (for environment variables)
