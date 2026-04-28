# Stock Data Intelligence Dashboard

A full-stack financial data platform that collects, processes, stores, and visualizes stock market data with real-time analytics and insights.

![Dashboard Screenshot](assets/images/dashboard-screenshot.png)

## Features

### Core Functionality
- **Data Collection**: Fetch stock data from yfinance API with async concurrent processing
- **Data Processing**: Clean, validate, and calculate financial metrics automatically
- **REST API**: FastAPI-based endpoints for data access with comprehensive error handling
- **Database Storage**: PostgreSQL/SQLite with optimized schema and indexing
- **Web Dashboard**: Interactive visualizations with Chart.js for stock analysis

### Financial Metrics
- Daily returns and percentage changes
- 7-day and custom moving averages
- 52-week high/low statistics
- Custom volatility score (0-100 scale)
- Stock comparison capabilities

### Technical Features
- Asynchronous data collection (up to 10 concurrent requests)
- Automatic retry logic with exponential backoff
- Comprehensive logging with rotation
- Docker containerization for easy deployment
- OpenAPI documentation at `/docs`
- Health check endpoint for monitoring

## Technology Stack

**Backend:**
- Python 3.9+
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- Pandas & NumPy (data processing)
- yfinance (data collection)

**Database:**
- PostgreSQL (production)
- SQLite (development)

**Frontend:**
- HTML5 / CSS3 / JavaScript
- Chart.js (visualizations)
- Fetch API (HTTP client)

**Deployment:**
- Docker & Docker Compose
- Gunicorn with Uvicorn workers
- Optional: Nginx reverse proxy

## Quick Start

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 14+ (or use SQLite for development)
- Docker and Docker Compose (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-data-intelligence-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

6. **Collect initial data**
   ```bash
   python scripts/collect_data.py
   ```

7. **Start the API server**
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

8. **Open the dashboard**
   - Open `dashboard/index.html` in your browser
   - Or serve with a local HTTP server:
     ```bash
     python -m http.server 8080 --directory dashboard
     ```
   - Navigate to `http://localhost:8080`

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start all services**
   ```bash
   # Basic setup (API + PostgreSQL)
   docker-compose up -d

   # With Redis caching
   docker-compose --profile with-cache up -d

   # With Nginx reverse proxy
   docker-compose --profile with-nginx up -d
   ```

3. **Initialize database**
   ```bash
   docker-compose exec api python scripts/init_db.py
   ```

4. **Collect data**
   ```bash
   docker-compose exec api python scripts/collect_data.py
   ```

5. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8000/dashboard (with Nginx) or open `dashboard/index.html`

6. **View logs**
   ```bash
   docker-compose logs -f api
   ```

7. **Stop services**
   ```bash
   docker-compose down
   ```

### Using Docker Only

```bash
# Build image
docker build -t stock-dashboard .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./stock_dashboard.db \
  -e LOG_LEVEL=INFO \
  --name stock-dashboard-api \
  stock-dashboard
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@localhost:5432/stock_dashboard` |
| `SECRET_KEY` | Secret key for security | `your-secret-key-here` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DEBUG` | `false` | Enable debug mode |
| `HOST` | `0.0.0.0` | API server host |
| `PORT` | `8000` | API server port |
| `WORKERS` | `4` | Number of Gunicorn workers |
| `DB_POOL_SIZE` | `10` | Database connection pool size |
| `DB_MAX_OVERFLOW` | `20` | Max overflow connections |
| `MAX_CONCURRENT_REQUESTS` | `10` | Max concurrent API requests |
| `CACHE_ENABLED` | `false` | Enable Redis caching |
| `REDIS_URL` | - | Redis connection URL |
| `ALPHA_VANTAGE_API_KEY` | `demo` | Alpha Vantage API key |
| `YFINANCE_ENABLED` | `true` | Enable yfinance data source |
| `ML_ENABLED` | `false` | Enable ML predictions |

See `.env.example` for complete list with descriptions.

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. List Companies
```http
GET /companies
```

**Response:**
```json
[
  {
    "symbol": "RELIANCE.NS",
    "name": "Reliance Industries Ltd"
  },
  {
    "symbol": "TCS.NS",
    "name": "Tata Consultancy Services Ltd"
  }
]
```

#### 3. Get Stock Data
```http
GET /data/{symbol}?days=30
```

**Parameters:**
- `symbol` (path): Stock symbol (e.g., "RELIANCE.NS")
- `days` (query, optional): Number of days (default: 30)

**Response:**
```json
[
  {
    "date": "2024-01-15",
    "open": 2450.50,
    "high": 2475.00,
    "low": 2440.00,
    "close": 2465.75,
    "volume": 5234567,
    "daily_return": 1.25,
    "moving_avg_7d": 2455.30
  }
]
```

#### 4. Get Stock Summary
```http
GET /summary/{symbol}
```

**Response:**
```json
{
  "symbol": "RELIANCE.NS",
  "name": "Reliance Industries Ltd",
  "week_52_high": 2856.00,
  "week_52_low": 2150.00,
  "avg_close": 2503.45,
  "volatility_score": 45.67
}
```

#### 5. Compare Stocks
```http
GET /compare?symbol1=RELIANCE.NS&symbol2=TCS.NS
```

**Response:**
```json
{
  "stock1": {
    "symbol": "RELIANCE.NS",
    "name": "Reliance Industries Ltd",
    "week_52_high": 2856.00,
    "week_52_low": 2150.00,
    "avg_close": 2503.45,
    "volatility_score": 45.67
  },
  "stock2": {
    "symbol": "TCS.NS",
    "name": "Tata Consultancy Services Ltd",
    "week_52_high": 3950.00,
    "week_52_low": 3100.00,
    "avg_close": 3525.80,
    "volatility_score": 32.45
  }
}
```

### Error Responses

All errors return JSON with the following format:

```json
{
  "error_code": "SYMBOL_NOT_FOUND",
  "message": "Stock symbol 'XYZ' does not exist in the database"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (symbol doesn't exist)
- `500` - Internal Server Error

### Interactive Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
stock-data-intelligence-dashboard/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── endpoints.py      # API route handlers
│   │   └── schemas.py        # Pydantic models
│   ├── data_collector/
│   │   ├── __init__.py
│   │   └── collector.py      # Data fetching logic
│   ├── data_processor/
│   │   ├── __init__.py
│   │   └── processor.py      # Data processing & metrics
│   └── models/
│       ├── __init__.py
│       ├── database.py       # SQLAlchemy models
│       └── connection.py     # Database connection
├── dashboard/
│   ├── index.html            # Main dashboard page
│   ├── css/
│   │   └── styles.css        # Dashboard styling
│   └── js/
│       ├── api.js            # API client
│       ├── app.js            # Main application logic
│       └── charts.js         # Chart rendering
├── scripts/
│   ├── init_db.py            # Database initialization
│   └── collect_data.py       # Data collection script
├── tests/
│   ├── test_data_collector.py
│   ├── test_data_processor.py
│   └── test_models.py
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Multi-container setup
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## Database Schema

### Companies Table
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Stock Data Table
```sql
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
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
```

## Data Collection

### Manual Collection

```bash
# Collect data for all configured symbols
python scripts/collect_data.py

# Collect data for specific symbols
python scripts/collect_data.py --symbols RELIANCE.NS TCS.NS INFY.NS

# Collect data for a date range
python scripts/collect_data.py --start-date 2024-01-01 --end-date 2024-01-31
```

### Scheduled Collection

The system supports scheduled data collection using cron jobs or task schedulers.

**Example cron job (daily at 6 PM):**
```bash
0 18 * * * cd /path/to/project && /path/to/venv/bin/python scripts/collect_data.py
```

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test Files
```bash
pytest tests/test_data_collector.py
pytest tests/test_data_processor.py
pytest tests/test_models.py
```

## Troubleshooting

### Database Connection Issues

**Problem:** `OperationalError: could not connect to server`

**Solution:**
1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL in `.env`
3. Ensure database exists: `createdb stock_dashboard`
4. Check firewall/network settings

### Data Collection Failures

**Problem:** `Failed to fetch data for symbol`

**Solution:**
1. Check internet connectivity
2. Verify symbol format (e.g., "RELIANCE.NS" for NSE stocks)
3. Check API rate limits
4. Review logs: `tail -f app.log`

### Docker Issues

**Problem:** Container exits immediately

**Solution:**
1. Check logs: `docker-compose logs api`
2. Verify environment variables in `.env`
3. Ensure database is healthy: `docker-compose ps`
4. Check port conflicts: `lsof -i :8000`

## Performance Optimization

### Database Indexing
The schema includes optimized indexes for common queries:
- `idx_companies_symbol` on `companies.symbol`
- `idx_stock_data_company_date` on `stock_data(company_id, date DESC)`

### Caching (Optional)
Enable Redis caching for improved API performance:

```bash
# In .env
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379/0

# Start with caching
docker-compose --profile with-cache up -d
```

**Cache TTL:**
- `/data/{symbol}`: 5 minutes
- `/summary/{symbol}`: 15 minutes

### Connection Pooling
Configure database connection pool in `.env`:
```bash
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

## Deployment

### Render.com

1. Create new Web Service
2. Connect your repository
3. Configure environment variables
4. Deploy

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Oracle Cloud

1. Create Compute Instance
2. Install Docker and Docker Compose
3. Clone repository
4. Configure `.env`
5. Run `docker-compose up -d`

### GitHub Pages (Frontend Only)

Deploy static dashboard to GitHub Pages:

1. Push `dashboard/` directory to `gh-pages` branch
2. Configure API base URL in `dashboard/js/api.js`
3. Enable GitHub Pages in repository settings

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is created as an internship assignment and is available for educational purposes.

## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Review existing documentation
- Check logs for error details

## Acknowledgments

- **yfinance**: Yahoo Finance API wrapper
- **FastAPI**: Modern Python web framework
- **Chart.js**: JavaScript charting library
- **SQLAlchemy**: Python SQL toolkit and ORM

---

**Built with ❤️ for financial data analysis**
