# Design Document: Stock Data Intelligence Dashboard

## Overview

The Stock Data Intelligence Dashboard is a full-stack financial data platform that collects, processes, stores, and visualizes stock market data. The system is designed as a modular architecture with clear separation between data collection, processing, API services, storage, and presentation layers.

### Core Objectives

- Collect stock market data from public APIs (yfinance, Alpha Vantage) or CSV files
- Process and calculate financial metrics (daily returns, moving averages, volatility)
- Expose RESTful APIs for data access and querying
- Provide web-based visualizations for stock analysis
- Support deployment to cloud platforms with Docker containerization

### Technology Stack

**Backend:**
- Python 3.9+
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- Pandas & NumPy (data processing)
- yfinance / Alpha Vantage SDK (data collection)
- Redis (optional caching)
- scikit-learn (optional ML predictions)

**Database:**
- PostgreSQL (production) or SQLite (development)

**Frontend:**
- HTML5 / CSS3 / JavaScript
- Chart.js or Plotly.js (visualizations)
- Fetch API (HTTP client)

**Deployment:**
- Docker & Docker Compose
- Gunicorn (WSGI server)
- Nginx (reverse proxy, optional)

## Architecture

### System Components

```mermaid
graph TB
    subgraph External
        API[External APIs<br/>yfinance/Alpha Vantage]
        CSV[CSV Files<br/>NSE/BSE Bhavcopy]
    end
    
    subgraph Backend
        DC[Data Collector<br/>Async fetching]
        DP[Data Processor<br/>Cleaning & Metrics]
        AS[API Server<br/>FastAPI]
        Cache[Redis Cache<br/>Optional]
    end
    
    subgraph Storage
        DB[(Database<br/>PostgreSQL/SQLite)]
    end
    
    subgraph Frontend
        UI[Web Dashboard<br/>HTML/JS/Chart.js]
    end
    
    API -->|Stock Data| DC
    CSV -->|CSV Data| DC
    DC -->|Raw Data| DP
    DP -->|Processed Data| DB
    DB -->|Query| AS
    AS -->|Cache Check| Cache
    Cache -->|Cached Response| AS
    AS -->|JSON API| UI
    UI -->|HTTP Requests| AS
```

### Data Flow

1. **Collection Phase**: Data Collector fetches stock data from external sources (APIs or CSV files)
2. **Processing Phase**: Data Processor cleans, validates, and calculates metrics
3. **Storage Phase**: Processed data is persisted to the database with proper indexing
4. **API Phase**: FastAPI server exposes RESTful endpoints with optional caching
5. **Visualization Phase**: Web dashboard consumes APIs and renders interactive charts

### Component Responsibilities

**Data Collector:**
- Fetch data from yfinance, Alpha Vantage, or CSV files
- Support concurrent fetching for multiple symbols
- Handle rate limiting and API errors
- Schedule periodic data updates

**Data Processor:**
- Clean and validate raw data
- Handle missing values (forward-fill, interpolation)
- Calculate financial metrics (daily return, moving averages, volatility)
- Normalize and transform data for storage

**API Server:**
- Expose RESTful endpoints for data access
- Validate request parameters
- Handle errors with appropriate HTTP status codes
- Implement caching for performance
- Generate OpenAPI documentation

**Database:**
- Store companies and stock data in relational schema
- Enforce constraints and indexes
- Support both PostgreSQL and SQLite

**Dashboard:**
- Display company listings
- Render interactive charts
- Provide time period filters
- Show top gainers/losers

## Components and Interfaces

### Data Collector Module

**Interface:**
```python
class DataCollector:
    async def fetch_stock_data(symbol: str, start_date: date, end_date: date) -> pd.DataFrame
    async def fetch_multiple_stocks(symbols: List[str]) -> Dict[str, pd.DataFrame]
    def parse_csv_bhavcopy(file_path: str) -> pd.DataFrame
```

**Implementation Details:**
- Use `yfinance` library as primary data source
- Fallback to Alpha Vantage API if yfinance fails
- Support CSV parsing for NSE/BSE bhavcopy files
- Implement async/await for concurrent fetching (max 10 concurrent requests)
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
- Rate limiting: respect API limits (yfinance: no limit, Alpha Vantage: 5 calls/min)

### Data Processor Module

**Interface:**
```python
class DataProcessor:
    def clean_data(df: pd.DataFrame) -> pd.DataFrame
    def calculate_daily_return(df: pd.DataFrame) -> pd.DataFrame
    def calculate_moving_average(df: pd.DataFrame, window: int = 7) -> pd.DataFrame
    def calculate_52_week_stats(df: pd.DataFrame) -> Dict[str, float]
    def calculate_volatility_score(df: pd.DataFrame, window: int = 30) -> pd.DataFrame
```

**Metric Calculation Algorithms:**

1. **Daily Return:**
   ```
   daily_return = ((close_price - previous_close_price) / previous_close_price) * 100
   ```

2. **Moving Average (7-day):**
   ```
   moving_avg_7d = rolling_mean(close_price, window=7)
   ```

3. **52-Week Statistics:**
   ```
   52_week_high = max(close_price) over last 52 weeks
   52_week_low = min(close_price) over last 52 weeks
   avg_close = mean(close_price) over last 52 weeks
   ```

4. **Volatility Score:**
   ```
   volatility_raw = std_dev(daily_return) over last 30 days
   volatility_score = (volatility_raw / max_volatility_observed) * 100
   ```
   - Normalized to 0-100 scale
   - Minimum 7 days of data required
   - Store NULL if insufficient data

**Data Cleaning Rules:**
- Missing values: forward-fill for prices, interpolate for volume
- Date format: convert to ISO 8601 (YYYY-MM-DD)
- Numeric validation: ensure prices and volume are positive
- Duplicate removal: based on (symbol, date) combination
- Invalid records: log and exclude from storage

### API Server Module

**Endpoints:**

1. **GET /companies**
   - Returns list of all companies
   - Response: `[{symbol: str, name: str}]`
   - Status: 200 (success), 500 (error)

2. **GET /data/{symbol}**
   - Returns last 30 days of stock data
   - Parameters: `symbol` (path)
   - Response: `[{date, open, high, low, close, volume, daily_return, moving_avg_7d}]`
   - Status: 200 (success), 404 (not found), 400 (invalid symbol)

3. **GET /summary/{symbol}**
   - Returns 52-week statistics
   - Parameters: `symbol` (path)
   - Response: `{symbol, name, 52_week_high, 52_week_low, avg_close}`
   - Status: 200 (success), 404 (not found)

4. **GET /compare**
   - Compares two stocks
   - Parameters: `symbol1`, `symbol2` (query)
   - Response: `{stock1: {...}, stock2: {...}}`
   - Status: 200 (success), 404 (not found), 400 (invalid/identical symbols)

5. **GET /predict/{symbol}** (optional)
   - Returns ML price prediction
   - Parameters: `symbol` (path)
   - Response: `{symbol, predicted_price, confidence, date}`
   - Status: 200 (success), 404 (not found), 503 (model unavailable)

**Request/Response Schemas:**

```python
# Pydantic models
class Company(BaseModel):
    symbol: str
    name: str

class StockData(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_return: Optional[float]
    moving_avg_7d: Optional[float]

class Summary(BaseModel):
    symbol: str
    name: str
    week_52_high: float
    week_52_low: float
    avg_close: float
    volatility_score: Optional[float]

class ErrorResponse(BaseModel):
    error_code: str
    message: str
```

**Error Handling Patterns:**
- 400 Bad Request: Invalid parameters, validation errors
- 404 Not Found: Symbol doesn't exist, endpoint not found
- 500 Internal Server Error: Database errors, unexpected exceptions
- All errors return JSON: `{error_code: str, message: str}`
- Log all errors with stack traces
- Validate symbol format: alphanumeric and hyphens only

**Caching Strategy:**
- Cache `/data/{symbol}` responses for 5 minutes
- Cache `/summary/{symbol}` responses for 15 minutes
- Invalidate cache on new data insertion
- Use Redis for distributed caching (optional)
- Include cache headers: `Cache-Control`, `ETag`

### Database Module

**Schema Design:**

```sql
-- Companies table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock data table
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    daily_return DECIMAL(10, 4),
    moving_avg_7d DECIMAL(10, 2),
    volatility_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, date)
);

-- Indexes for performance
CREATE INDEX idx_stock_data_company_id ON stock_data(company_id);
CREATE INDEX idx_stock_data_date ON stock_data(date);
CREATE INDEX idx_stock_data_company_date ON stock_data(company_id, date DESC);
CREATE INDEX idx_companies_symbol ON companies(symbol);
```

**Constraints:**
- Primary keys on all tables
- Foreign key: `stock_data.company_id` → `companies.id`
- Unique constraint: `(company_id, date)` prevents duplicates
- NOT NULL constraints on essential fields
- Cascade delete: removing company removes all stock data

**Connection Management:**
- Connection pooling: 5-20 connections
- Retry logic: 3 attempts with exponential backoff
- Timeout: 30 seconds for queries
- Support both PostgreSQL and SQLite via SQLAlchemy

### Frontend Dashboard Module

**Component Structure:**

```
dashboard/
├── index.html          # Main page
├── css/
│   └── styles.css      # Styling
├── js/
│   ├── api.js          # API client
│   ├── charts.js       # Chart rendering
│   ├── filters.js      # Time period filters
│   └── app.js          # Main application logic
```

**Key Components:**

1. **Company List Component:**
   - Fetches from `/companies` endpoint
   - Displays alphabetically sorted list
   - Clickable items trigger chart view
   - Loading state and error handling

2. **Chart Viewer Component:**
   - Fetches from `/data/{symbol}` endpoint
   - Renders line chart using Chart.js
   - X-axis: dates, Y-axis: closing prices
   - Title includes company name and symbol
   - Responsive design

3. **Filter Component:**
   - Buttons for 30-day and 90-day views
   - Default: 30-day view
   - Updates chart on selection
   - Visual indication of active filter

4. **Top Gainers/Losers Component:**
   - Displays top 5 gainers (green)
   - Displays top 5 losers (red)
   - Shows symbol, name, daily return %
   - Updates daily

**Chart.js Integration:**

```javascript
const config = {
    type: 'line',
    data: {
        labels: dates,
        datasets: [{
            label: 'Closing Price',
            data: closePrices,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: `${companyName} (${symbol})`
            }
        },
        scales: {
            x: { title: { display: true, text: 'Date' } },
            y: { title: { display: true, text: 'Price' } }
        }
    }
};
```

**API Integration Pattern:**

```javascript
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }
    
    async getCompanies() {
        const response = await fetch(`${this.baseURL}/companies`);
        if (!response.ok) throw new Error('Failed to fetch companies');
        return response.json();
    }
    
    async getStockData(symbol, days = 30) {
        const response = await fetch(`${this.baseURL}/data/${symbol}?days=${days}`);
        if (!response.ok) throw new Error(`Failed to fetch data for ${symbol}`);
        return response.json();
    }
}
```

## Data Models

### Domain Models

**Company:**
```python
@dataclass
class Company:
    id: int
    symbol: str
    name: str
    created_at: datetime
```

**StockRecord:**
```python
@dataclass
class StockRecord:
    id: int
    company_id: int
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    daily_return: Optional[Decimal]
    moving_avg_7d: Optional[Decimal]
    volatility_score: Optional[Decimal]
    created_at: datetime
```

### SQLAlchemy ORM Models

```python
from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    stock_data = relationship("StockData", back_populates="company", cascade="all, delete-orphan")

class StockData(Base):
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    daily_return = Column(Numeric(10, 4))
    moving_avg_7d = Column(Numeric(10, 2))
    volatility_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="stock_data")
    
    __table_args__ = (
        UniqueConstraint('company_id', 'date', name='uq_company_date'),
        Index('idx_company_date_desc', 'company_id', date.desc()),
    )
```


## Data Processing Pipeline

### Collection Pipeline

```mermaid
sequenceDiagram
    participant Scheduler
    participant Collector
    participant API as External API
    participant Processor
    participant DB as Database
    
    Scheduler->>Collector: Trigger collection
    loop For each symbol
        Collector->>API: Fetch stock data
        API-->>Collector: Raw data
        Collector->>Processor: Send raw data
        Processor->>Processor: Clean & validate
        Processor->>Processor: Calculate metrics
        Processor->>DB: Store processed data
    end
    Collector-->>Scheduler: Collection complete
```

### Processing Steps

**Step 1: Data Collection**
- Input: List of stock symbols
- Process: Async fetch from yfinance/Alpha Vantage
- Output: Raw DataFrames with OHLCV data
- Error handling: Log failures, continue with remaining symbols

**Step 2: Data Cleaning**
- Input: Raw DataFrame
- Process:
  - Convert dates to ISO 8601 format
  - Validate numeric fields (positive values)
  - Handle missing values (forward-fill for prices)
  - Remove duplicates by (symbol, date)
- Output: Clean DataFrame
- Error handling: Log invalid records, exclude from output

**Step 3: Metric Calculation**
- Input: Clean DataFrame
- Process:
  - Sort by date ascending
  - Calculate daily return: `(close - prev_close) / prev_close * 100`
  - Calculate 7-day moving average: `rolling(7).mean()`
  - Calculate volatility score: `std(daily_return, 30 days)` normalized to 0-100
- Output: DataFrame with calculated metrics
- Error handling: Store NULL for metrics with insufficient data

**Step 4: Database Storage**
- Input: Processed DataFrame
- Process:
  - Upsert company record
  - Bulk insert stock data records
  - Handle unique constraint violations
- Output: Persisted data
- Error handling: Retry on connection failure, log constraint violations

### Async Processing Implementation

```python
import asyncio
from typing import List
import yfinance as yf

class AsyncDataCollector:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_stock(self, symbol: str) -> pd.DataFrame:
        async with self.semaphore:
            try:
                # yfinance is synchronous, run in executor
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(
                    None, 
                    lambda: yf.download(symbol, period="1y", progress=False)
                )
                return data
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                return pd.DataFrame()
    
    async def fetch_multiple(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        tasks = [self.fetch_stock(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        return dict(zip(symbols, results))
```

### Scheduled Updates

- **Frequency**: Daily at market close (e.g., 6 PM IST for Indian markets)
- **Mechanism**: Cron job or APScheduler
- **Process**: Fetch latest data for all configured symbols
- **Monitoring**: Log completion status, alert on failures

## Error Handling

### Error Categories

1. **External API Errors**
   - Rate limiting (429)
   - Service unavailable (503)
   - Invalid symbol (404)
   - Authentication failure (401)

2. **Data Validation Errors**
   - Missing required fields
   - Invalid data types
   - Out-of-range values
   - Duplicate records

3. **Database Errors**
   - Connection failures
   - Constraint violations
   - Query timeouts
   - Disk space issues

4. **API Server Errors**
   - Invalid request parameters
   - Resource not found
   - Internal server errors
   - Timeout errors

### Error Handling Strategies

**Retry Logic:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_with_retry(symbol: str):
    return await fetch_stock_data(symbol)
```

**Graceful Degradation:**
- If primary API fails, fallback to secondary API
- If cache unavailable, serve from database
- If ML prediction fails, return historical average

**Error Responses:**
```python
class ErrorResponse(BaseModel):
    error_code: str  # e.g., "SYMBOL_NOT_FOUND"
    message: str     # Human-readable description
    details: Optional[Dict] = None  # Additional context

# Example responses
{
    "error_code": "SYMBOL_NOT_FOUND",
    "message": "Stock symbol 'XYZ' does not exist in the database"
}

{
    "error_code": "INVALID_PARAMETER",
    "message": "Symbol must contain only alphanumeric characters and hyphens",
    "details": {"parameter": "symbol", "value": "ABC@123"}
}
```

**Logging Strategy:**
```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Log levels
logger.debug("Fetching data for symbol: AAPL")  # Development
logger.info("Successfully processed 50 stocks")  # Normal operations
logger.warning("Cache miss for symbol: AAPL")    # Potential issues
logger.error("Database connection failed", exc_info=True)  # Errors
```

## Testing Strategy

### Testing Approach

The Stock Data Intelligence Dashboard requires a comprehensive testing strategy that combines unit tests for specific functionality and integration tests for end-to-end workflows. Given the nature of this system—which involves data collection, processing, API endpoints, and database interactions—property-based testing is NOT the primary testing approach. Instead, we will focus on:

1. **Unit Tests**: Test individual functions and methods with specific examples
2. **Integration Tests**: Test component interactions and API endpoints
3. **End-to-End Tests**: Test complete workflows from data collection to visualization

### Why Property-Based Testing Is Not Applicable

Property-based testing (PBT) is most effective for testing pure functions with universal properties that hold across all inputs. However, this system primarily involves:

- **External API Integration**: Behavior depends on external services (yfinance, Alpha Vantage)
- **Database Operations**: CRUD operations with specific schemas and constraints
- **Data Processing Pipelines**: Transformations with specific business logic
- **REST API Endpoints**: Request/response patterns with specific formats

These characteristics make example-based unit tests and integration tests more appropriate than property-based tests.

### Unit Testing Strategy

**Data Processor Tests:**
```python
import pytest
import pandas as pd
from datetime import date

def test_calculate_daily_return():
    # Test with specific example
    data = pd.DataFrame({
        'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
        'close': [100.0, 105.0, 102.0]
    })
    result = calculate_daily_return(data)
    assert result['daily_return'].iloc[1] == 5.0  # (105-100)/100 * 100
    assert result['daily_return'].iloc[2] == pytest.approx(-2.857, rel=0.01)

def test_calculate_daily_return_with_missing_data():
    # Test edge case: missing previous close
    data = pd.DataFrame({
        'date': [date(2024, 1, 1)],
        'close': [100.0]
    })
    result = calculate_daily_return(data)
    assert pd.isna(result['daily_return'].iloc[0])

def test_volatility_score_insufficient_data():
    # Test edge case: less than 7 days
    data = pd.DataFrame({
        'date': [date(2024, 1, i) for i in range(1, 6)],
        'close': [100.0, 101.0, 99.0, 102.0, 98.0]
    })
    result = calculate_volatility_score(data)
    assert pd.isna(result['volatility_score'].iloc[0])

def test_clean_data_removes_duplicates():
    # Test duplicate removal
    data = pd.DataFrame({
        'symbol': ['AAPL', 'AAPL', 'AAPL'],
        'date': [date(2024, 1, 1), date(2024, 1, 1), date(2024, 1, 2)],
        'close': [100.0, 100.0, 101.0]
    })
    result = clean_data(data)
    assert len(result) == 2
```

**API Endpoint Tests:**
```python
from fastapi.testclient import TestClient

def test_get_companies_success(client: TestClient):
    response = client.get("/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_companies_empty_database(client: TestClient):
    # Clear database
    response = client.get("/companies")
    assert response.status_code == 200
    assert response.json() == []

def test_get_stock_data_success(client: TestClient):
    response = client.get("/data/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 30  # Last 30 days
    assert all(key in data[0] for key in ['date', 'open', 'high', 'low', 'close', 'volume'])

def test_get_stock_data_invalid_symbol(client: TestClient):
    response = client.get("/data/INVALID@SYMBOL")
    assert response.status_code == 400
    assert "error_code" in response.json()

def test_get_stock_data_not_found(client: TestClient):
    response = client.get("/data/NONEXISTENT")
    assert response.status_code == 404

def test_compare_stocks_success(client: TestClient):
    response = client.get("/compare?symbol1=AAPL&symbol2=GOOGL")
    assert response.status_code == 200
    data = response.json()
    assert "stock1" in data and "stock2" in data

def test_compare_stocks_identical_symbols(client: TestClient):
    response = client.get("/compare?symbol1=AAPL&symbol2=AAPL")
    assert response.status_code == 400
```

**Database Tests:**
```python
def test_insert_company(db_session):
    company = Company(symbol="AAPL", name="Apple Inc.")
    db_session.add(company)
    db_session.commit()
    
    result = db_session.query(Company).filter_by(symbol="AAPL").first()
    assert result.name == "Apple Inc."

def test_unique_constraint_violation(db_session):
    company1 = Company(symbol="AAPL", name="Apple Inc.")
    company2 = Company(symbol="AAPL", name="Apple Inc.")
    db_session.add(company1)
    db_session.commit()
    
    db_session.add(company2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_cascade_delete(db_session):
    company = Company(symbol="AAPL", name="Apple Inc.")
    db_session.add(company)
    db_session.commit()
    
    stock_data = StockData(
        company_id=company.id,
        date=date(2024, 1, 1),
        open=100.0, high=105.0, low=99.0, close=102.0, volume=1000000
    )
    db_session.add(stock_data)
    db_session.commit()
    
    db_session.delete(company)
    db_session.commit()
    
    result = db_session.query(StockData).filter_by(company_id=company.id).first()
    assert result is None
```

### Integration Testing Strategy

**End-to-End Data Pipeline Test:**
```python
@pytest.mark.integration
async def test_full_data_pipeline():
    # 1. Collect data
    collector = DataCollector()
    raw_data = await collector.fetch_stock_data("AAPL", start_date, end_date)
    assert not raw_data.empty
    
    # 2. Process data
    processor = DataProcessor()
    clean_data = processor.clean_data(raw_data)
    processed_data = processor.calculate_metrics(clean_data)
    assert 'daily_return' in processed_data.columns
    
    # 3. Store in database
    db = Database()
    db.store_stock_data("AAPL", processed_data)
    
    # 4. Retrieve via API
    response = client.get("/data/AAPL")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

**Cache Integration Test:**
```python
@pytest.mark.integration
def test_cache_behavior(client: TestClient, redis_client):
    # First request - cache miss
    response1 = client.get("/data/AAPL")
    assert response1.status_code == 200
    
    # Second request - cache hit
    response2 = client.get("/data/AAPL")
    assert response2.status_code == 200
    assert response1.json() == response2.json()
    
    # Verify cache was used (check Redis)
    cached_value = redis_client.get("data:AAPL")
    assert cached_value is not None
```

### Test Coverage Goals

- **Unit Tests**: 80%+ code coverage
- **Integration Tests**: Cover all API endpoints and data pipelines
- **Edge Cases**: Test boundary conditions, missing data, invalid inputs
- **Error Scenarios**: Test all error handling paths

### Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/ -m integration

# Run specific test file
pytest tests/unit/test_data_processor.py
```

## Deployment Architecture

### Docker Containerization

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY dashboard/ ./dashboard/

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: stock_dashboard
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@db:5432/stock_dashboard
      REDIS_URL: redis://redis:6379/0
      ALPHA_VANTAGE_API_KEY: ${ALPHA_VANTAGE_API_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./dashboard:/app/dashboard

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./dashboard:/usr/share/nginx/html:ro
    depends_on:
      - api

volumes:
  postgres_data:
```

### Environment Configuration

**Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stock_dashboard
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true

# External APIs
ALPHA_VANTAGE_API_KEY=your_api_key_here
YFINANCE_ENABLED=true

# Application
LOG_LEVEL=INFO
DEBUG=false
SECRET_KEY=your_secret_key_here

# Data Collection
COLLECTION_SCHEDULE=0 18 * * *  # Daily at 6 PM
MAX_CONCURRENT_REQUESTS=10

# ML Prediction (optional)
ML_ENABLED=false
MODEL_RETRAIN_SCHEDULE=0 0 * * 0  # Weekly on Sunday
```

**.env.example:**
```bash
DATABASE_URL=postgresql://admin:changeme@localhost:5432/stock_dashboard
REDIS_URL=redis://localhost:6379/0
ALPHA_VANTAGE_API_KEY=demo
LOG_LEVEL=INFO
CACHE_ENABLED=true
ML_ENABLED=false
```

### Deployment Platforms

**1. Render Deployment:**
```yaml
# render.yaml
services:
  - type: web
    name: stock-dashboard-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: stock-dashboard-db
          property: connectionString
      - key: ALPHA_VANTAGE_API_KEY
        sync: false

  - type: pserv
    name: stock-dashboard-db
    env: postgres
    plan: starter
    ipAllowList: []

  - type: redis
    name: stock-dashboard-cache
    plan: starter
    ipAllowList: []
```

**2. Oracle Cloud Deployment:**
- Use Oracle Container Engine for Kubernetes (OKE)
- Deploy PostgreSQL on Oracle Autonomous Database
- Use Oracle Object Storage for logs and backups
- Configure load balancer for API service

**3. GitHub Pages (Frontend Only):**
- Deploy static dashboard to GitHub Pages
- Configure API base URL to point to backend service
- Use GitHub Actions for automated deployment

### Caching Strategy

**Cache Layers:**

1. **Application-Level Cache (Redis):**
   - Cache API responses
   - TTL: 5 minutes for `/data/{symbol}`, 15 minutes for `/summary/{symbol}`
   - Invalidation: On new data insertion

2. **Database Query Cache:**
   - PostgreSQL query result caching
   - Materialized views for complex aggregations

3. **HTTP Cache Headers:**
   - `Cache-Control: public, max-age=300` for data endpoints
   - `ETag` for conditional requests

**Cache Implementation:**
```python
from functools import wraps
import redis
import json

redis_client = redis.Redis.from_url(os.getenv('REDIS_URL'))

def cache_response(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@app.get("/data/{symbol}")
@cache_response(ttl=300)
async def get_stock_data(symbol: str):
    # Implementation
    pass
```

### Monitoring and Logging

**Logging Configuration:**
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure rotating file handler
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler, logging.StreamHandler()]
)
```

**Metrics to Monitor:**
- API response times
- Database query performance
- Cache hit/miss rates
- Data collection success/failure rates
- Error rates by endpoint
- Active connections

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_database_connection(),
        "cache": check_redis_connection(),
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Scaling Considerations

**Horizontal Scaling:**
- Run multiple API server instances behind load balancer
- Use Redis for shared cache across instances
- Database connection pooling

**Vertical Scaling:**
- Increase worker processes (Gunicorn workers)
- Optimize database queries with indexes
- Use database read replicas for read-heavy workloads

**Performance Optimization:**
- Implement pagination for large result sets
- Use database indexes on frequently queried fields
- Compress API responses (gzip)
- Implement rate limiting to prevent abuse

---

## Summary

This design document provides a comprehensive blueprint for the Stock Data Intelligence Dashboard. The architecture follows a modular approach with clear separation of concerns:

- **Data Collection**: Async fetching from external APIs with retry logic
- **Data Processing**: Pandas-based pipeline for cleaning and metric calculation
- **API Layer**: FastAPI with OpenAPI documentation and caching
- **Storage**: PostgreSQL with optimized schema and indexes
- **Frontend**: Lightweight HTML/JS dashboard with Chart.js visualizations
- **Deployment**: Docker containerization with support for multiple platforms

The system is designed to be scalable, maintainable, and extensible, with comprehensive error handling, logging, and testing strategies. The technology choices prioritize developer productivity (Python, FastAPI) while ensuring production-ready performance (PostgreSQL, Redis, Docker).
