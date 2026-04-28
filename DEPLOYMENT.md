# Deployment Guide

This guide provides detailed instructions for deploying the Stock Data Intelligence Dashboard to various platforms.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
  - [Render.com](#rendercom)
  - [Oracle Cloud](#oracle-cloud)
  - [AWS](#aws)
- [Production Checklist](#production-checklist)

## Local Development

### Quick Start

1. **Setup environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env - use SQLite for development
   ```

3. **Initialize database**
   ```bash
   python scripts/init_db.py
   python scripts/collect_data.py
   ```

4. **Run development server**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access application**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Dashboard: Open `dashboard/index.html` in browser

## Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Basic Deployment (API + PostgreSQL)

1. **Configure environment**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file**
   ```bash
   # Required changes:
   DATABASE_URL=postgresql://admin:changeme@db:5432/stock_dashboard
   DB_PASSWORD=your_secure_password_here
   SECRET_KEY=your_secret_key_here
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec api python scripts/init_db.py
   ```

5. **Collect initial data**
   ```bash
   docker-compose exec api python scripts/collect_data.py
   ```

6. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

### With Redis Caching

```bash
# Update .env
CACHE_ENABLED=true

# Start with cache profile
docker-compose --profile with-cache up -d
```

### With Nginx Reverse Proxy

```bash
# Start with nginx profile
docker-compose --profile with-nginx up -d

# Access via Nginx
# Dashboard: http://localhost/
# API: http://localhost/api/
```

### Docker Commands

```bash
# View logs
docker-compose logs -f api

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Scale API workers
docker-compose up -d --scale api=3
```

## Cloud Deployment

### Render.com

**Step 1: Create PostgreSQL Database**

1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `stock-dashboard-db`
   - Database: `stock_dashboard`
   - User: `admin`
   - Region: Choose closest to your users
   - Plan: Free or Starter
4. Click "Create Database"
5. Copy the "Internal Database URL"

**Step 2: Create Web Service**

1. Click "New +" → "Web Service"
2. Connect your Git repository
3. Configure:
   - Name: `stock-dashboard-api`
   - Environment: `Python 3`
   - Region: Same as database
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**Step 3: Configure Environment Variables**

Add these environment variables:

```
DATABASE_URL=<paste Internal Database URL>
SECRET_KEY=<generate random string>
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=production
YFINANCE_ENABLED=true
MAX_CONCURRENT_REQUESTS=10
ALLOWED_ORIGINS=https://your-app.onrender.com
```

**Step 4: Deploy**

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Access your API at `https://your-app.onrender.com`

**Step 5: Initialize Database**

```bash
# Using Render Shell
# Go to your web service → Shell tab
python scripts/init_db.py
python scripts/collect_data.py
```

**Step 6: Setup Scheduled Data Collection**

1. Go to your web service
2. Click "Cron Jobs" tab
3. Add new cron job:
   - Name: `collect-stock-data`
   - Command: `python scripts/collect_data.py`
   - Schedule: `0 18 * * *` (daily at 6 PM)

### Oracle Cloud

**Prerequisites:**
- Oracle Cloud account
- OCI CLI installed and configured

**Step 1: Create Compute Instance**

```bash
# Create VM instance
oci compute instance launch \
  --availability-domain <AD> \
  --compartment-id <COMPARTMENT_ID> \
  --shape VM.Standard.E2.1.Micro \
  --image-id <UBUNTU_IMAGE_ID> \
  --subnet-id <SUBNET_ID> \
  --display-name stock-dashboard-vm
```

**Step 2: Setup Instance**

```bash
# SSH into instance
ssh ubuntu@<INSTANCE_IP>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Step 3: Deploy Application**

```bash
# Clone repository
git clone <your-repo-url>
cd stock-data-intelligence-dashboard

# Configure environment
cp .env.example .env
nano .env  # Edit configuration

# Start services
docker-compose up -d

# Initialize database
docker-compose exec api python scripts/init_db.py
docker-compose exec api python scripts/collect_data.py
```

**Step 4: Configure Firewall**

```bash
# Open ports in OCI Security List
# Add ingress rules for:
# - Port 80 (HTTP)
# - Port 443 (HTTPS)
# - Port 8000 (API)

# Configure UFW on instance
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

**Step 5: Setup SSL (Optional)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### AWS

**Using EC2 + RDS**

1. **Create RDS PostgreSQL Instance**
   - Engine: PostgreSQL 14
   - Instance class: db.t3.micro (free tier)
   - Storage: 20 GB
   - Enable automatic backups

2. **Create EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t2.micro (free tier)
   - Security group: Allow ports 22, 80, 443, 8000

3. **Deploy Application**
   ```bash
   # SSH into EC2
   ssh -i your-key.pem ubuntu@<EC2_IP>
   
   # Install Docker (same as Oracle Cloud steps)
   # Clone and deploy (same as Oracle Cloud steps)
   ```

4. **Configure Environment**
   ```bash
   # In .env
   DATABASE_URL=postgresql://admin:password@<RDS_ENDPOINT>:5432/stock_dashboard
   ```

## Production Checklist

### Security

- [ ] Change default passwords in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Configure `ALLOWED_ORIGINS` to specific domains
- [ ] Enable HTTPS/SSL
- [ ] Use environment-specific credentials
- [ ] Enable database encryption at rest
- [ ] Configure firewall rules
- [ ] Set up VPC/private networking
- [ ] Enable database backups

### Performance

- [ ] Configure connection pooling (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`)
- [ ] Enable Redis caching (`CACHE_ENABLED=true`)
- [ ] Set appropriate `WORKERS` count (2-4 × CPU cores)
- [ ] Configure CDN for static assets
- [ ] Enable gzip compression (Nginx)
- [ ] Set up database indexes (done automatically)
- [ ] Monitor query performance
- [ ] Configure rate limiting

### Monitoring

- [ ] Set up application logging
- [ ] Configure log rotation
- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure uptime monitoring
- [ ] Set up performance monitoring (New Relic, DataDog)
- [ ] Configure database monitoring
- [ ] Set up alerts for errors and downtime
- [ ] Monitor API response times
- [ ] Track data collection success rates

### Reliability

- [ ] Configure health checks
- [ ] Set up automatic restarts
- [ ] Configure database backups
- [ ] Test disaster recovery procedures
- [ ] Set up load balancing (if needed)
- [ ] Configure auto-scaling (if needed)
- [ ] Test failover scenarios
- [ ] Document incident response procedures

### Data Management

- [ ] Schedule regular data collection
- [ ] Configure data retention policies
- [ ] Set up database backups
- [ ] Test backup restoration
- [ ] Monitor database size
- [ ] Configure data archival (if needed)
- [ ] Document data collection schedule

### Documentation

- [ ] Update API documentation
- [ ] Document deployment procedures
- [ ] Create runbooks for common issues
- [ ] Document environment variables
- [ ] Create architecture diagrams
- [ ] Document backup/restore procedures

## Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs api

# Check container status
docker-compose ps

# Restart services
docker-compose restart
```

**Database connection failed:**
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify connection string
docker-compose exec api env | grep DATABASE_URL
```

### Performance Issues

**Slow API responses:**
1. Enable Redis caching
2. Check database indexes
3. Increase worker count
4. Monitor database query performance

**High memory usage:**
1. Reduce `WORKERS` count
2. Decrease `DB_POOL_SIZE`
3. Enable connection pooling limits

### Data Collection Issues

**Data collection fails:**
```bash
# Check logs
docker-compose logs api | grep collector

# Test manually
docker-compose exec api python scripts/collect_data.py

# Verify API access
docker-compose exec api python -c "import yfinance as yf; print(yf.download('AAPL', period='1d'))"
```

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check data collection success
- Verify API health

**Weekly:**
- Review performance metrics
- Check database size
- Update dependencies (if needed)

**Monthly:**
- Review and rotate logs
- Test backup restoration
- Update security patches
- Review and optimize queries

### Backup Procedures

**Database Backup:**
```bash
# PostgreSQL backup
docker-compose exec db pg_dump -U admin stock_dashboard > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T db psql -U admin stock_dashboard < backup_20240115.sql
```

**Application Backup:**
```bash
# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check main README.md
4. Create an issue in the repository

---

**Last Updated:** January 2024
