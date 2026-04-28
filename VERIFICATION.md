# Deployment Verification Checklist

Use this checklist to verify your deployment is working correctly.

## Pre-Deployment Checks

### Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `DATABASE_URL` configured correctly
- [ ] `SECRET_KEY` changed from default
- [ ] `DB_PASSWORD` set to secure value
- [ ] `ALLOWED_ORIGINS` configured for production
- [ ] `DEBUG` set to `false` for production

### Files Present
- [ ] `Dockerfile` exists
- [ ] `docker-compose.yml` exists
- [ ] `requirements.txt` exists
- [ ] `src/` directory with all modules
- [ ] `dashboard/` directory with frontend files
- [ ] `scripts/` directory with init and collection scripts

## Deployment Verification

### Docker Services

```bash
# Check all services are running
docker-compose ps

# Expected output:
# NAME                    STATUS              PORTS
# stock-dashboard-api     Up (healthy)        0.0.0.0:8000->8000/tcp
# stock-dashboard-db      Up (healthy)        0.0.0.0:5432->5432/tcp
```

- [ ] All services show "Up" status
- [ ] Health checks show "healthy"
- [ ] No restart loops in logs

### Database Verification

```bash
# Check database connection
docker-compose exec api python -c "from src.models.connection import get_database; db = get_database(); print('✓ Database connected')"

# Check tables exist
docker-compose exec db psql -U admin -d stock_dashboard -c "\dt"

# Expected tables:
# - companies
# - stock_data
```

- [ ] Database connection successful
- [ ] `companies` table exists
- [ ] `stock_data` table exists
- [ ] Indexes created correctly

### API Verification

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected","timestamp":"..."}
```

- [ ] Health endpoint returns 200 OK
- [ ] Database status is "connected"
- [ ] Response is valid JSON

```bash
# Test companies endpoint
curl http://localhost:8000/companies

# Expected: JSON array (may be empty initially)
```

- [ ] Companies endpoint returns 200 OK
- [ ] Response is valid JSON array

```bash
# Test API documentation
curl -I http://localhost:8000/docs

# Expected: 200 OK
```

- [ ] API docs accessible at `/docs`
- [ ] ReDoc accessible at `/redoc`
- [ ] All endpoints documented

### Data Collection Verification

```bash
# Initialize database with sample companies
docker-compose exec api python scripts/init_db.py

# Expected output:
# ✓ Database initialized
# ✓ Sample companies added
```

- [ ] Database initialization successful
- [ ] Sample companies added

```bash
# Collect stock data
docker-compose exec api python scripts/collect_data.py

# Expected output:
# ✓ Collected data for RELIANCE.NS
# ✓ Collected data for TCS.NS
# ...
```

- [ ] Data collection completes without errors
- [ ] Data stored in database
- [ ] Metrics calculated correctly

```bash
# Verify data was stored
curl http://localhost:8000/companies

# Should return list of companies
```

- [ ] Companies endpoint returns data
- [ ] Company symbols and names correct

```bash
# Test stock data endpoint
curl http://localhost:8000/data/RELIANCE.NS

# Should return array of stock data
```

- [ ] Stock data endpoint returns data
- [ ] Data includes all required fields (date, open, high, low, close, volume)
- [ ] Calculated metrics present (daily_return, moving_avg_7d)

### Frontend Verification

**Option 1: Direct file access**
- [ ] Open `dashboard/index.html` in browser
- [ ] Update API base URL in `dashboard/js/api.js` if needed
- [ ] Dashboard loads without errors
- [ ] Company list displays
- [ ] Charts render when company selected

**Option 2: With Nginx**
```bash
# Start with Nginx profile
docker-compose --profile with-nginx up -d

# Access dashboard
open http://localhost/
```

- [ ] Dashboard accessible at root URL
- [ ] API accessible at `/api/` path
- [ ] Static assets load correctly
- [ ] No CORS errors in browser console

### Performance Verification

```bash
# Test API response time
time curl http://localhost:8000/health

# Should be < 100ms
```

- [ ] Health check responds quickly (< 100ms)
- [ ] Data endpoints respond in reasonable time (< 1s)
- [ ] No timeout errors

```bash
# Check resource usage
docker stats --no-stream

# Monitor CPU and memory usage
```

- [ ] API container uses reasonable resources (< 500MB RAM)
- [ ] Database container stable
- [ ] No memory leaks over time

### Logging Verification

```bash
# Check API logs
docker-compose logs api | tail -20

# Should show:
# - Startup messages
# - Request logs
# - No error messages
```

- [ ] Logs are being written
- [ ] Log level appropriate (INFO for production)
- [ ] No unexpected errors
- [ ] Request/response logging working

```bash
# Check for errors
docker-compose logs api | grep ERROR

# Should be empty or only expected errors
```

- [ ] No critical errors
- [ ] No database connection errors
- [ ] No unhandled exceptions

## Production-Specific Checks

### Security
- [ ] `DEBUG=false` in production
- [ ] `SECRET_KEY` is unique and secure
- [ ] Database password is strong
- [ ] `ALLOWED_ORIGINS` restricted to specific domains
- [ ] HTTPS/SSL configured (if applicable)
- [ ] Firewall rules configured
- [ ] Database not exposed to public internet

### Monitoring
- [ ] Health check endpoint accessible
- [ ] Logs being collected/monitored
- [ ] Error tracking configured (optional)
- [ ] Uptime monitoring configured (optional)
- [ ] Performance monitoring configured (optional)

### Backup
- [ ] Database backup strategy in place
- [ ] Backup restoration tested
- [ ] Configuration files backed up
- [ ] Backup schedule documented

### Scalability
- [ ] Worker count appropriate for load
- [ ] Database connection pool sized correctly
- [ ] Redis caching enabled (if needed)
- [ ] Resource limits configured

## Common Issues and Solutions

### Issue: Database connection failed

**Symptoms:**
- API returns 500 errors
- Logs show "OperationalError"
- Health check shows database error

**Solutions:**
1. Check database is running: `docker-compose ps db`
2. Verify DATABASE_URL in .env
3. Check database logs: `docker-compose logs db`
4. Restart database: `docker-compose restart db`

### Issue: Data collection fails

**Symptoms:**
- `collect_data.py` script fails
- Logs show "Failed to fetch data"
- No data in database

**Solutions:**
1. Check internet connectivity
2. Verify stock symbols are correct (e.g., "RELIANCE.NS" for NSE)
3. Check yfinance API status
4. Review logs for specific errors
5. Try collecting data for one symbol manually

### Issue: Frontend can't connect to API

**Symptoms:**
- Dashboard shows "Failed to fetch"
- Browser console shows CORS errors
- Network tab shows failed requests

**Solutions:**
1. Verify API is running: `curl http://localhost:8000/health`
2. Check ALLOWED_ORIGINS in .env
3. Update API base URL in `dashboard/js/api.js`
4. Check browser console for specific errors
5. Verify CORS middleware is configured

### Issue: Container keeps restarting

**Symptoms:**
- `docker-compose ps` shows "Restarting"
- Container exits immediately
- Logs show startup errors

**Solutions:**
1. Check logs: `docker-compose logs api`
2. Verify all environment variables are set
3. Check for syntax errors in code
4. Verify dependencies are installed
5. Check for port conflicts

## Performance Benchmarks

### Expected Performance

**API Response Times:**
- Health check: < 50ms
- GET /companies: < 100ms
- GET /data/{symbol}: < 500ms
- GET /summary/{symbol}: < 300ms
- GET /compare: < 600ms

**Data Collection:**
- Single symbol: < 5 seconds
- 10 symbols: < 30 seconds
- 50 symbols: < 2 minutes

**Resource Usage:**
- API container: 200-500 MB RAM
- Database container: 100-300 MB RAM
- Redis container: 50-100 MB RAM

### Load Testing (Optional)

```bash
# Install Apache Bench
# Ubuntu: apt-get install apache2-utils
# macOS: brew install httpd

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test data endpoint
ab -n 100 -c 5 http://localhost:8000/data/RELIANCE.NS
```

- [ ] API handles concurrent requests
- [ ] Response times remain consistent
- [ ] No errors under load
- [ ] Resource usage stays within limits

## Sign-off

### Development Environment
- [ ] All checks passed
- [ ] Sample data loaded
- [ ] Frontend working
- [ ] Ready for testing

**Verified by:** ________________  
**Date:** ________________

### Production Environment
- [ ] All checks passed
- [ ] Security configured
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Documentation updated
- [ ] Ready for launch

**Verified by:** ________________  
**Date:** ________________

---

**Note:** Keep this checklist updated as your deployment evolves. Add environment-specific checks as needed.
