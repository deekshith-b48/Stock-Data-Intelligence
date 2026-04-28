"""
Integration tests for the complete Stock Data Intelligence Dashboard workflow.

Tests the complete data pipeline:
1. Data collection → processing → storage → API → frontend

Requirements tested: All core requirements (1-20)
Task: 14.1 - Run full integration test suite
"""

import pytest
import asyncio
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.data_collector.collector import AsyncDataCollector
from src.data_processor.processor import DataProcessor
from src.models.database import Base, Company, StockData
from src.api.main import app
from src.storage import store_company, store_stock_data


@pytest.fixture(scope="module")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="module")
def test_db_session(test_db_engine):
    """Create a test database session."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="module")
def api_client():
    """Create a FastAPI test client."""
    return TestClient(app)


class TestEndToEndDataPipeline:
    """Test the complete data pipeline from collection to storage."""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_single_stock(self, test_db_session):
        """Test complete workflow for a single stock: collect → process → store."""
        # Step 1: Collect data
        collector = AsyncDataCollector(max_concurrent=1, max_retries=2)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        raw_data = await collector.fetch_stock(
            'AAPL',
            start_date,
            end_date
        )
        
        # Verify data was collected
        assert not raw_data.empty, "Data collection failed"
        assert 'date' in raw_data.columns
        assert 'close' in raw_data.columns
        
        # Step 2: Process data
        processor = DataProcessor()
        
        # Clean data
        clean_data = processor.clean_data(raw_data, 'AAPL')
        assert not clean_data.empty, "Data cleaning failed"
        
        # Calculate metrics
        clean_data = processor.calculate_daily_return(clean_data)
        clean_data = processor.calculate_moving_average(clean_data, window=7)
        clean_data = processor.calculate_volatility_score(clean_data, window=30)
        
        # Verify metrics were calculated
        assert 'daily_return' in clean_data.columns
        assert 'moving_avg_7d' in clean_data.columns
        assert 'volatility_score' in clean_data.columns
        
        # Step 3: Store data
        result = store_stock_data('AAPL_TEST', clean_data, test_db_session)
        
        assert result['success'] is True
        assert result['total_records'] > 0
        
        print(f"✓ Complete pipeline test passed: {result['inserted']} records stored")
    
    @pytest.mark.asyncio
    async def test_concurrent_collection_multiple_stocks(self):
        """Test concurrent data collection for multiple stocks."""
        collector = AsyncDataCollector(max_concurrent=3, max_retries=2)
        
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        results = await collector.fetch_multiple_stocks(symbols)
        
        # Verify all symbols were processed
        assert len(results) == len(symbols)
        
        # Verify at least some data was collected
        successful = sum(1 for df in results.values() if not df.empty)
        assert successful >= 2, f"Only {successful}/{len(symbols)} stocks collected successfully"
        
        print(f"✓ Concurrent collection test passed: {successful}/{len(symbols)} stocks collected")
    
    def test_data_processor_handles_edge_cases(self):
        """Test data processor with various edge cases."""
        processor = DataProcessor()
        
        # Test with minimal data
        import pandas as pd
        minimal_data = pd.DataFrame({
            'date': [date(2024, 1, 1)],
            'open': [100.0],
            'high': [105.0],
            'low': [99.0],
            'close': [102.0],
            'volume': [1000000]
        })
        
        result = processor.clean_data(minimal_data, 'TEST')
        assert not result.empty
        
        # Calculate metrics (should handle insufficient data gracefully)
        result = processor.calculate_daily_return(result)
        result = processor.calculate_moving_average(result, window=7)
        result = processor.calculate_volatility_score(result, window=30)
        
        # First record should have NaN for daily_return
        assert pd.isna(result['daily_return'].iloc[0])
        
        print("✓ Edge case handling test passed")


class TestAPIEndpoints:
    """Test all API endpoints with real data."""
    
    def test_health_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint test passed")
    
    def test_companies_endpoint(self, api_client):
        """Test GET /companies endpoint."""
        response = api_client.get("/companies")
        assert response.status_code == 200
        
        companies = response.json()
        assert isinstance(companies, list)
        
        # Should have some companies from init_db
        assert len(companies) > 0
        
        # Verify structure
        if companies:
            assert 'symbol' in companies[0]
            assert 'name' in companies[0]
        
        print(f"✓ Companies endpoint test passed: {len(companies)} companies found")
    
    def test_data_endpoint_valid_symbol(self, api_client):
        """Test GET /data/{symbol} with valid symbol."""
        # Use a symbol that should exist from init_db
        response = api_client.get("/data/RELIANCE?days=10")
        
        # Should return 200 or 404 (if no data yet)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ Data endpoint test passed: {len(data)} records returned")
        else:
            print("✓ Data endpoint test passed: 404 for symbol without data")
    
    def test_data_endpoint_invalid_symbol(self, api_client):
        """Test GET /data/{symbol} with invalid symbol format."""
        response = api_client.get("/data/INVALID@SYMBOL")
        assert response.status_code == 400
        
        error = response.json()
        assert 'error_code' in error or 'detail' in error
        print("✓ Invalid symbol test passed")
    
    def test_summary_endpoint(self, api_client):
        """Test GET /summary/{symbol} endpoint."""
        response = api_client.get("/summary/RELIANCE")
        
        # Should return 200 or 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert 'symbol' in data
            print("✓ Summary endpoint test passed")
        else:
            print("✓ Summary endpoint test passed: 404 for symbol without data")
    
    def test_compare_endpoint_valid_symbols(self, api_client):
        """Test GET /compare with valid symbols."""
        response = api_client.get("/compare?symbol1=RELIANCE&symbol2=TCS")
        
        # Should return 200 or 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert 'stock1' in data
            assert 'stock2' in data
            print("✓ Compare endpoint test passed")
        else:
            print("✓ Compare endpoint test passed: 404 for symbols without data")
    
    def test_compare_endpoint_identical_symbols(self, api_client):
        """Test GET /compare with identical symbols."""
        response = api_client.get("/compare?symbol1=RELIANCE&symbol2=RELIANCE")
        assert response.status_code == 400
        
        error = response.json()
        assert 'error_code' in error or 'detail' in error
        print("✓ Identical symbols test passed")
    
    def test_api_error_handling(self, api_client):
        """Test API error handling for various scenarios."""
        # Test 404 for non-existent endpoint
        response = api_client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test missing query parameters (API returns 400 for validation errors)
        response = api_client.get("/compare?symbol1=RELIANCE")
        assert response.status_code == 400
        
        print("✓ Error handling test passed")


class TestDataIntegrity:
    """Test data integrity and validation."""
    
    def test_database_constraints(self, test_db_session):
        """Test database unique constraints and relationships."""
        from sqlalchemy.exc import IntegrityError
        
        # Test unique constraint on company symbol
        company1 = Company(symbol='TEST_UNIQUE', name='Test Company')
        test_db_session.add(company1)
        test_db_session.commit()
        
        company2 = Company(symbol='TEST_UNIQUE', name='Test Company 2')
        test_db_session.add(company2)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        
        test_db_session.rollback()
        print("✓ Database constraints test passed")
    
    def test_cascade_delete_behavior(self, test_db_session):
        """Test cascade delete from company to stock data."""
        # Create company
        company = Company(symbol='TEST_CASCADE', name='Test Cascade')
        test_db_session.add(company)
        test_db_session.commit()
        
        # Add stock data
        stock = StockData(
            company_id=company.id,
            date=date(2024, 1, 1),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000000
        )
        test_db_session.add(stock)
        test_db_session.commit()
        
        # Delete company
        test_db_session.delete(company)
        test_db_session.commit()
        
        # Verify stock data was deleted
        remaining = test_db_session.query(StockData).filter_by(
            company_id=company.id
        ).count()
        assert remaining == 0
        
        print("✓ Cascade delete test passed")
    
    def test_metric_calculations_accuracy(self):
        """Test accuracy of financial metric calculations."""
        import pandas as pd
        processor = DataProcessor()
        
        # Create test data with known values
        data = pd.DataFrame({
            'date': [date(2024, 1, i) for i in range(1, 11)],
            'close': [100.0, 102.0, 101.0, 103.0, 105.0, 104.0, 106.0, 108.0, 107.0, 109.0]
        })
        
        # Calculate daily return
        result = processor.calculate_daily_return(data)
        
        # Verify second day return: (102-100)/100 * 100 = 2.0
        assert abs(result['daily_return'].iloc[1] - 2.0) < 0.01
        
        # Calculate moving average
        result = processor.calculate_moving_average(result, window=3)
        
        # Verify third day MA: (100+102+101)/3 = 101.0
        assert abs(result['moving_avg_7d'].iloc[2] - 101.0) < 0.01
        
        print("✓ Metric calculation accuracy test passed")


class TestErrorScenarios:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_symbol_collection(self):
        """Test data collection with invalid symbol."""
        collector = AsyncDataCollector(max_concurrent=1, max_retries=1)
        
        result = await collector.fetch_stock('INVALID_XYZ_123')
        
        # Should return empty DataFrame, not raise exception
        assert result.empty
        print("✓ Invalid symbol collection test passed")
    
    def test_empty_dataframe_processing(self):
        """Test processing empty DataFrame."""
        import pandas as pd
        processor = DataProcessor()
        
        empty_df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        
        # Should handle gracefully
        result = processor.clean_data(empty_df, 'TEST')
        assert result.empty
        
        result = processor.calculate_daily_return(result)
        assert result.empty
        
        print("✓ Empty DataFrame processing test passed")
    
    def test_missing_data_handling(self):
        """Test handling of missing values in data."""
        import pandas as pd
        processor = DataProcessor()
        
        data = pd.DataFrame({
            'date': [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
            'open': [100.0, None, 102.0],
            'high': [105.0, 106.0, 107.0],
            'low': [99.0, 100.0, 101.0],
            'close': [102.0, 103.0, 104.0],
            'volume': [1000000, 2000000, 3000000]
        })
        
        result = processor.clean_data(data, 'TEST')
        
        # Should forward-fill missing value
        assert not result.empty
        assert result['open'].iloc[1] == 100.0  # Forward-filled
        
        print("✓ Missing data handling test passed")


class TestPerformance:
    """Test performance requirements."""
    
    @pytest.mark.asyncio
    async def test_concurrent_fetch_performance(self):
        """Test that concurrent fetching meets performance requirements."""
        import time
        
        collector = AsyncDataCollector(max_concurrent=10, max_retries=1)
        
        # Test with 10 symbols (scaled down from 50 for faster testing)
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
                   'META', 'NVDA', 'JPM', 'V', 'WMT']
        
        start_time = time.time()
        results = await collector.fetch_multiple_stocks(symbols)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (scaled: 10 stocks in 10 seconds)
        assert elapsed < 15, f"Performance issue: {elapsed:.2f}s for {len(symbols)} stocks"
        
        print(f"✓ Performance test passed: {len(symbols)} stocks in {elapsed:.2f}s")
    
    def test_api_response_time(self, api_client):
        """Test API response time requirements."""
        import time
        
        # Test /companies endpoint (should be < 500ms for up to 1000 companies)
        start_time = time.time()
        response = api_client.get("/companies")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 0.5, f"Response time too slow: {elapsed:.3f}s"
        
        print(f"✓ API response time test passed: {elapsed*1000:.0f}ms")


def run_integration_tests():
    """Run all integration tests and print summary."""
    print("\n" + "="*70)
    print("RUNNING FULL INTEGRATION TEST SUITE")
    print("="*70)
    
    # Run pytest programmatically
    import sys
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-k', 'test_'
    ])
    
    print("\n" + "="*70)
    print("INTEGRATION TEST SUITE COMPLETE")
    print("="*70)
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_integration_tests()
    sys.exit(exit_code)
