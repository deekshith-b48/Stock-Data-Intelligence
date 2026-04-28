#!/bin/bash

# Stock Data Intelligence Dashboard - Quick Start Script
# This script helps you quickly set up and run the application

set -e

echo "=========================================="
echo "Stock Data Intelligence Dashboard"
echo "Quick Start Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file with your configuration before proceeding${NC}"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Ask user for deployment type
echo "Select deployment type:"
echo "1) Basic (API + PostgreSQL)"
echo "2) With Redis caching"
echo "3) With Nginx reverse proxy"
echo "4) Full stack (Redis + Nginx)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        COMPOSE_CMD="docker-compose up -d"
        ;;
    2)
        COMPOSE_CMD="docker-compose --profile with-cache up -d"
        ;;
    3)
        COMPOSE_CMD="docker-compose --profile with-nginx up -d"
        ;;
    4)
        COMPOSE_CMD="docker-compose --profile with-cache --profile with-nginx up -d"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}Starting services...${NC}"
eval $COMPOSE_CMD

echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check if database is ready
echo -e "${YELLOW}Checking database connection...${NC}"
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U admin -d stock_dashboard &> /dev/null; then
        echo -e "${GREEN}✓ Database is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Database failed to start${NC}"
        exit 1
    fi
    sleep 2
done

# Ask if user wants to initialize database
echo ""
read -p "Initialize database with sample data? [y/N]: " init_db

if [[ $init_db =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    docker-compose exec api python scripts/init_db.py
    echo -e "${GREEN}✓ Database initialized${NC}"
    
    echo ""
    read -p "Collect initial stock data? [y/N]: " collect_data
    
    if [[ $collect_data =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Collecting stock data (this may take a few minutes)...${NC}"
        docker-compose exec api python scripts/collect_data.py
        echo -e "${GREEN}✓ Data collection complete${NC}"
    fi
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✓ Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Access your application:"
echo "  • API:        http://localhost:8000"
echo "  • API Docs:   http://localhost:8000/docs"
echo "  • Health:     http://localhost:8000/health"

if [[ $choice == "3" || $choice == "4" ]]; then
    echo "  • Dashboard:  http://localhost/"
    echo "  • API (Nginx): http://localhost/api/"
else
    echo "  • Dashboard:  Open dashboard/index.html in your browser"
fi

echo ""
echo "Useful commands:"
echo "  • View logs:        docker-compose logs -f api"
echo "  • Stop services:    docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • Collect data:     docker-compose exec api python scripts/collect_data.py"
echo ""
echo -e "${GREEN}Happy analyzing! 📈${NC}"
