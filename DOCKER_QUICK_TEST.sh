#!/bin/bash

# Quick Docker Deployment Test Script
# Task 14.2: Test Docker deployment locally

set -e

echo "=========================================="
echo "Docker Deployment Quick Test"
echo "Task 14.2 Verification"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Helper function for tests
test_step() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

test_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Check prerequisites
echo "Step 1: Checking Prerequisites"
echo "----------------------------------------"

test_step "Checking Docker installation"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    test_pass "Docker installed: $DOCKER_VERSION"
else
    test_fail "Docker not installed"
    echo ""
    echo "Please install Docker:"
    echo "  macOS: brew install --cask docker"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo "  Windows: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
fi

test_step "Checking Docker Compose installation"
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
    else
        COMPOSE_VERSION=$(docker compose version)
    fi
    test_pass "Docker Compose installed: $COMPOSE_VERSION"
else
    test_fail "Docker Compose not installed"
    exit 1
fi

test_step "Checking Docker daemon"
if docker info &> /dev/null; then
    test_pass "Docker daemon is running"
else
    test_fail "Docker daemon is not running"
    echo "Please start Docker Desktop or Docker daemon"
    exit 1
fi

echo ""
echo "Step 2: Building Docker Images"
echo "----------------------------------------"

test_step "Building API service image"
if docker-compose build api; then
    test_pass "API image built successfully"
else
    test_fail "Failed to build API image"
    exit 1
fi

echo ""
echo "Step 3: Starting Services"
echo "----------------------------------------"

test_step "Starting database and API services"
if docker-compose up -d; then
    test_pass "Services started"
else
    test_fail "Failed to start services"
    exit 1
fi

test_info "Waiting 15 seconds for services to initialize..."
sleep 15

echo ""
echo "Step 4: Verifying Service Health"
echo "----------------------------------------"

test_step "Checking database container status"
DB_STATUS=$(docker-compose ps db --format json | grep -o '"State":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
if [ "$DB_STATUS" = "running" ]; then
    test_pass "Database container is running"
else
    test_fail "Database container status: $DB_STATUS"
fi

test_step "Checking API container status"
API_STATUS=$(docker-compose ps api --format json | grep -o '"State":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
if [ "$API_STATUS" = "running" ]; then
    test_pass "API container is running"
else
    test_fail "API container status: $API_STATUS"
fi

test_step "Checking database health"
if docker-compose exec -T db pg_isready -U admin -d stock_dashboard &> /dev/null; then
    test_pass "Database is healthy and accepting connections"
else
    test_fail "Database health check failed"
fi

echo ""
echo "Step 5: Testing API Endpoints"
echo "----------------------------------------"

test_step "Testing /health endpoint"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    test_pass "Health endpoint returned 200"
    HEALTH_DATA=$(curl -s http://localhost:8000/health)
    test_info "Response: $HEALTH_DATA"
else
    test_fail "Health endpoint returned $HEALTH_RESPONSE"
fi

test_step "Testing /docs endpoint"
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$DOCS_RESPONSE" = "200" ]; then
    test_pass "API documentation accessible"
else
    test_fail "API documentation returned $DOCS_RESPONSE"
fi

test_step "Testing /companies endpoint"
COMPANIES_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/companies)
if [ "$COMPANIES_RESPONSE" = "200" ]; then
    test_pass "Companies endpoint returned 200"
    COMPANIES_DATA=$(curl -s http://localhost:8000/companies)
    COMPANY_COUNT=$(echo "$COMPANIES_DATA" | grep -o '"symbol"' | wc -l | tr -d ' ')
    test_info "Found $COMPANY_COUNT companies"
else
    test_fail "Companies endpoint returned $COMPANIES_RESPONSE"
fi

echo ""
echo "Step 6: Initializing Database (Optional)"
echo "----------------------------------------"

read -p "Initialize database with sample data? [y/N]: " INIT_DB
if [[ $INIT_DB =~ ^[Yy]$ ]]; then
    test_step "Running database initialization"
    if docker-compose exec -T api python scripts/init_db.py; then
        test_pass "Database initialized successfully"
    else
        test_fail "Database initialization failed"
    fi
    
    read -p "Collect initial stock data? [y/N]: " COLLECT_DATA
    if [[ $COLLECT_DATA =~ ^[Yy]$ ]]; then
        test_step "Collecting stock data (this may take a few minutes)"
        if docker-compose exec -T api python scripts/collect_data.py; then
            test_pass "Data collection completed"
        else
            test_fail "Data collection failed"
        fi
        
        # Re-test companies endpoint
        test_step "Re-testing /companies endpoint after data collection"
        COMPANIES_DATA=$(curl -s http://localhost:8000/companies)
        COMPANY_COUNT=$(echo "$COMPANIES_DATA" | grep -o '"symbol"' | wc -l | tr -d ' ')
        if [ "$COMPANY_COUNT" -gt 0 ]; then
            test_pass "Found $COMPANY_COUNT companies after initialization"
            
            # Test a specific stock
            FIRST_SYMBOL=$(echo "$COMPANIES_DATA" | grep -o '"symbol":"[^"]*"' | head -1 | cut -d'"' -f4)
            if [ -n "$FIRST_SYMBOL" ]; then
                test_step "Testing /data/$FIRST_SYMBOL endpoint"
                DATA_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/data/$FIRST_SYMBOL")
                if [ "$DATA_RESPONSE" = "200" ]; then
                    test_pass "Stock data endpoint working for $FIRST_SYMBOL"
                else
                    test_fail "Stock data endpoint returned $DATA_RESPONSE"
                fi
                
                test_step "Testing /summary/$FIRST_SYMBOL endpoint"
                SUMMARY_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/summary/$FIRST_SYMBOL")
                if [ "$SUMMARY_RESPONSE" = "200" ]; then
                    test_pass "Summary endpoint working for $FIRST_SYMBOL"
                else
                    test_fail "Summary endpoint returned $SUMMARY_RESPONSE"
                fi
            fi
        fi
    fi
fi

echo ""
echo "Step 7: Checking Logs"
echo "----------------------------------------"

test_step "Checking for errors in API logs"
ERROR_COUNT=$(docker-compose logs api | grep -i "error" | grep -v "error_logfile" | wc -l | tr -d ' ')
if [ "$ERROR_COUNT" -eq 0 ]; then
    test_pass "No errors found in API logs"
else
    test_fail "Found $ERROR_COUNT error messages in logs"
    test_info "Run 'docker-compose logs api' to view details"
fi

echo ""
echo "Step 8: Testing Frontend Dashboard"
echo "----------------------------------------"

test_info "Dashboard files location: dashboard/index.html"
test_info "To test dashboard:"
test_info "  1. Open http://localhost:8000/docs in browser"
test_info "  2. Open dashboard/index.html in browser"
test_info "  3. Verify company list loads"
test_info "  4. Click a company to view charts"
test_info "  5. Test time period filters (30-day, 90-day)"

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Your Docker deployment is working correctly."
    echo ""
    echo "Access your application:"
    echo "  • API:        http://localhost:8000"
    echo "  • API Docs:   http://localhost:8000/docs"
    echo "  • Health:     http://localhost:8000/health"
    echo "  • Dashboard:  Open dashboard/index.html in browser"
    echo ""
    echo "Useful commands:"
    echo "  • View logs:        docker-compose logs -f api"
    echo "  • Stop services:    docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • View stats:       docker stats"
    echo ""
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker-compose logs api"
    echo "  2. Check logs: docker-compose logs db"
    echo "  3. Verify .env file configuration"
    echo "  4. Ensure ports 8000 and 5432 are not in use"
    echo "  5. Try rebuilding: docker-compose build --no-cache"
    echo ""
    echo "For detailed troubleshooting, see DOCKER_DEPLOYMENT_TEST_REPORT.md"
    echo ""
fi

echo "To stop services: docker-compose down"
echo ""
