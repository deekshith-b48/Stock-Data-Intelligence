# Implementation Plan: Stock Data Intelligence Dashboard

## Overview

This implementation plan breaks down the Stock Data Intelligence Dashboard into discrete, sequential coding tasks. The system is a full-stack financial data platform built with Python (FastAPI backend), PostgreSQL database, and HTML/JS frontend. The implementation prioritizes core functionality first (data collection, processing, API, basic visualization) with optional features clearly marked for faster MVP delivery within the 2-3 day timeline.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `src/`, `src/models/`, `src/api/`, `src/data_collector/`, `src/data_processor/`, `dashboard/`, `tests/`
  - Create `requirements.txt` with core dependencies: FastAPI, SQLAlchemy, pandas, numpy, yfinance, psycopg2-binary, uvicorn, gunicorn, pydantic
  - Create `.env.example` file with environment variable templates
  - Create `src/__init__.py` and module `__init__.py` files
  - _Requirements: 16.1, 16.2, 16.3_

- [-] 2. Implement database models and schema
  - [x] 2.1 Create SQLAlchemy ORM models
    - Define `Company` model with fields: id, symbol, name, created_at
    - Define `StockData` model with fields: id, company_id, date, open, high, low, close, volume, daily_return, moving_avg_7d, volatility_score, created_at
    - Add relationships and cascade delete configuration
    - Add unique constraints and indexes as specified in design
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 2.2 Create database connection and session management
    - Implement database connection with SQLAlchemy engine
    - Configure connection pooling (5-20 connections)
    - Add retry logic with exponential backoff (3 attempts)
    - Support both PostgreSQL and SQLite via environment variable
    - _Requirements: 5.5_
  
  - [x] 2.3 Create database initialization script
    - Write script to create tables from ORM models
    - Add sample company data (5-10 Indian stocks: RELIANCE, TCS, INFY, HDFCBANK, etc.)
    - _Requirements: 5.1_
  
  - [ ] 2.4 Write unit tests for database models
    - Test company insertion and retrieval
    - Test unique constraint violations
    - Test cascade delete behavior
    - Test stock data insertion with foreign key relationships
    - _Requirements: 5.3_

- [-] 3. Implement data collector module
  - [x] 3.1 Create base data collector class
    - Implement `fetch_stock_data(symbol, start_date, end_date)` method using yfinance
    - Add error handling and logging for API failures
    - Implement retry logic with exponential backoff (3 attempts: 1s, 2s, 4s)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 3.2 Implement async concurrent fetching
    - Create `AsyncDataCollector` class with semaphore (max 10 concurrent)
    - Implement `fetch_multiple_stocks(symbols)` method
    - Use asyncio.gather for concurrent execution
    - Log completion status for each symbol
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_
  
  - [ ] 3.3 Add CSV bhavcopy parsing support (optional)
    - Implement `parse_csv_bhavcopy(file_path)` method
    - Parse NSE/BSE CSV format to DataFrame
    - _Requirements: 1.1_
  
  - [ ] 3.4 Write unit tests for data collector
    - Test successful data fetching with mock yfinance responses
    - Test error handling when API fails
    - Test retry logic behavior
    - Test concurrent fetching limits
    - _Requirements: 1.4_

- [-] 4. Implement data processor module
  - [x] 4.1 Create data cleaning functions
    - Implement `clean_data(df)` function: handle missing values (forward-fill), validate numeric fields, remove duplicates
    - Convert dates to ISO 8601 format
    - Log invalid records and exclude from output
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 4.2 Implement standard financial metrics calculation
    - Implement `calculate_daily_return(df)`: ((close - prev_close) / prev_close) * 100
    - Implement `calculate_moving_average(df, window=7)`: rolling mean of close prices
    - Implement `calculate_52_week_stats(df)`: max, min, and average close over 52 weeks
    - Handle insufficient data cases by storing NULL
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [x] 4.3 Implement volatility score calculation
    - Implement `calculate_volatility_score(df, window=30)`: std dev of daily returns over 30 days
    - Normalize to 0-100 scale
    - Require minimum 7 days of data, store NULL otherwise
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 4.4 Write unit tests for data processor
    - Test daily return calculation with specific examples
    - Test moving average calculation
    - Test 52-week statistics calculation
    - Test volatility score with sufficient and insufficient data
    - Test data cleaning (duplicates, missing values, invalid data)
    - _Requirements: 2.4, 3.6, 4.3_

- [x] 5. Checkpoint - Ensure data pipeline works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement core API endpoints
  - [x] 6.1 Set up FastAPI application
    - Create FastAPI app instance with CORS middleware
    - Configure logging with rotating file handler
    - Add health check endpoint at `/health`
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_
  
  - [x] 6.2 Create Pydantic response models
    - Define `Company`, `StockData`, `Summary`, `ErrorResponse` schemas
    - Add field validation and examples
    - _Requirements: 10.4_
  
  - [x] 6.3 Implement GET /companies endpoint
    - Query all companies from database
    - Return JSON array with symbol and name
    - Handle empty database case (return empty array)
    - Add error handling with appropriate status codes
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 6.4 Implement GET /data/{symbol} endpoint
    - Validate symbol parameter (alphanumeric and hyphens only)
    - Query last 30 days of stock data for given symbol
    - Return data sorted by date descending
    - Return 404 if symbol not found, 400 if invalid format
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 10.1, 10.3_
  
  - [x] 6.5 Implement GET /summary/{symbol} endpoint
    - Query 52-week statistics for given symbol
    - Return symbol, name, 52_week_high, 52_week_low, avg_close
    - Return 404 if symbol not found
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 6.6 Implement GET /compare endpoint
    - Accept symbol1 and symbol2 query parameters
    - Validate both symbols exist and are different
    - Return side-by-side metrics for both stocks
    - Return 400 if symbols are identical, 404 if either doesn't exist
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 6.7 Add global error handling
    - Implement exception handlers for 400, 404, 500 errors
    - Return JSON error responses with error_code and message fields
    - Log all errors with stack traces
    - _Requirements: 10.1, 10.2, 10.4, 10.5_
  
  - [ ]* 6.8 Write integration tests for API endpoints
    - Test GET /companies with populated and empty database
    - Test GET /data/{symbol} with valid, invalid, and non-existent symbols
    - Test GET /summary/{symbol} with valid and invalid symbols
    - Test GET /compare with valid, identical, and non-existent symbols
    - Test error response formats
    - _Requirements: 6.5, 7.5, 8.5, 9.5, 10.4_

- [-] 7. Implement data storage pipeline
  - [x] 7.1 Create data persistence functions
    - Implement `store_company(symbol, name)` function with upsert logic
    - Implement `store_stock_data(symbol, dataframe)` function with bulk insert
    - Handle unique constraint violations gracefully
    - _Requirements: 5.3_
  
  - [x] 7.2 Create end-to-end data collection script
    - Integrate data collector, processor, and storage functions
    - Fetch data for all configured symbols
    - Process and calculate metrics
    - Store in database
    - Log success/failure for each symbol
    - _Requirements: 1.2, 1.4, 18.5_
  
  - [ ] 7.3 Write integration tests for data pipeline
    - Test full pipeline from collection to storage
    - Verify data integrity after storage
    - Test error handling when collection fails
    - _Requirements: 1.4, 2.4_

- [x] 8. Checkpoint - Ensure API and storage work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement frontend dashboard
  - [x] 9.1 Create HTML structure
    - Create `dashboard/index.html` with sections for company list, chart viewer, and top gainers/losers
    - Add Chart.js CDN link
    - Create basic CSS styling in `dashboard/css/styles.css`
    - _Requirements: 11.1, 12.1, 14.1_
  
  - [x] 9.2 Implement API client module
    - Create `dashboard/js/api.js` with APIClient class
    - Implement `getCompanies()`, `getStockData(symbol, days)`, `getSummary(symbol)` methods
    - Add error handling for failed requests
    - _Requirements: 11.3, 12.5_
  
  - [x] 9.3 Implement company list component
    - Create `dashboard/js/app.js` with company list rendering
    - Fetch companies from API on page load
    - Display alphabetically sorted list
    - Make company names clickable to trigger chart view
    - Show loading state and error messages
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 9.4 Implement chart viewer component
    - Create `dashboard/js/charts.js` with Chart.js integration
    - Render line chart with dates on x-axis and closing prices on y-axis
    - Include company name and symbol in chart title
    - Fetch data when company is selected
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x] 9.5 Implement time period filters
    - Add 30-day and 90-day filter buttons
    - Update chart when filter is selected
    - Default to 30-day view
    - Show visual indication of active filter
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ]* 9.6 Implement top gainers/losers component (optional)
    - Fetch top 5 gainers and losers from API
    - Display with color coding (green for gainers, red for losers)
    - Show symbol, name, and daily return percentage
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 10. Implement caching layer (optional)
  - [ ]* 10.1 Set up Redis connection
    - Add Redis client configuration
    - Add connection health check
    - Make caching optional via environment variable
    - _Requirements: 17.1, 17.2_
  
  - [ ]* 10.2 Implement cache decorator
    - Create `cache_response(ttl)` decorator
    - Generate cache keys from function name and parameters
    - Check cache before executing function
    - Store results in cache with TTL
    - _Requirements: 17.1, 17.2, 17.3_
  
  - [ ]* 10.3 Apply caching to API endpoints
    - Cache GET /data/{symbol} responses for 5 minutes
    - Cache GET /summary/{symbol} responses for 15 minutes
    - Add cache headers to HTTP responses
    - _Requirements: 17.1, 17.2, 17.4_
  
  - [ ]* 10.4 Write tests for caching behavior
    - Test cache hit and miss scenarios
    - Test cache invalidation
    - Test cache TTL expiration
    - _Requirements: 17.5_

- [x] 11. Create deployment configuration
  - [x] 11.1 Create Dockerfile
    - Use Python 3.9-slim base image
    - Copy requirements and install dependencies
    - Copy application code
    - Expose port 8000
    - Set Gunicorn as entrypoint with Uvicorn workers
    - _Requirements: 16.1, 16.4_
  
  - [x] 11.2 Create docker-compose.yml
    - Define services: db (PostgreSQL), api (FastAPI), nginx (optional)
    - Add Redis service if caching is enabled
    - Configure environment variables
    - Add health checks for all services
    - Set up volumes for data persistence
    - _Requirements: 16.2, 16.4_
  
  - [x] 11.3 Create environment configuration
    - Document all environment variables in `.env.example`
    - Add variables for: DATABASE_URL, REDIS_URL, ALPHA_VANTAGE_API_KEY, LOG_LEVEL, CACHE_ENABLED
    - _Requirements: 16.2, 16.5_
  
  - [ ]* 11.4 Create Render deployment configuration (optional)
    - Create `render.yaml` with web service, PostgreSQL, and Redis configurations
    - Document deployment steps in README
    - _Requirements: 16.1_

- [x] 12. Create documentation
  - [x] 12.1 Create README.md
    - Add project overview and features
    - Document installation and setup instructions
    - Document how to run locally with Docker
    - Document environment variables
    - Add API endpoint documentation
    - _Requirements: 15.1, 15.2, 15.3, 16.3_
  
  - [x] 12.2 Verify FastAPI auto-generated docs
    - Ensure OpenAPI documentation is accessible at `/docs`
    - Verify all endpoints are documented with parameters and responses
    - Add endpoint descriptions and examples
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 13. Implement ML price prediction (optional)
  - [ ]* 13.1 Create ML prediction module
    - Implement simple linear regression model using scikit-learn
    - Train model on historical closing prices
    - Predict next day's closing price
    - Calculate prediction confidence/error margin
    - _Requirements: 19.1, 19.2, 19.4_
  
  - [ ]* 13.2 Implement GET /predict/{symbol} endpoint
    - Load trained model for given symbol
    - Return predicted price, confidence, and date
    - Return 503 if model unavailable
    - _Requirements: 19.3_
  
  - [ ]* 13.3 Create model training script
    - Fetch historical data for all symbols
    - Train models and save to disk
    - Schedule weekly retraining
    - _Requirements: 19.5_
  
  - [ ]* 13.4 Write tests for ML prediction
    - Test model training with sample data
    - Test prediction endpoint
    - Test error handling when model unavailable
    - _Requirements: 19.4_

- [ ] 14. Final checkpoint and integration testing
  - [x] 14.1 Run full integration test suite
    - Test complete workflow: data collection → processing → storage → API → frontend
    - Verify all core endpoints work correctly
    - Test error scenarios and edge cases
    - _Requirements: All core requirements_
  
  - [x] 14.2 Test Docker deployment locally
    - Build Docker images
    - Run docker-compose up
    - Verify all services start correctly
    - Test API endpoints through Docker
    - Test frontend dashboard through Docker
    - _Requirements: 16.4_
  
  - [x] 14.3 Perform manual testing
    - Test dashboard in browser
    - Verify charts render correctly
    - Test time period filters
    - Test company selection and navigation
    - _Requirements: 11.1, 12.1, 13.1_

- [x] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery within 2-3 day timeline
- Core functionality (tasks 1-9, 11-12, 14) should be prioritized for the internship assignment
- Optional features (caching, ML prediction, CSV parsing, top gainers/losers) can be added if time permits
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- The implementation assumes Python 3.9+ and uses FastAPI, SQLAlchemy, pandas, and Chart.js as specified in the design
- Database can be PostgreSQL (production) or SQLite (development) based on environment configuration
- All API endpoints include proper error handling and validation as per requirements
