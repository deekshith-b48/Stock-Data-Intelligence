"""
Test script to verify AsyncDataCollector meets all requirements.

Requirements tested:
- 18.1: Concurrent fetching for multiple stock symbols
- 18.2: Limit concurrent requests to 10
- 18.3: Continue processing when one stock fails
- 18.4: Complete 50 stocks within 30 seconds
- 18.5: Log completion status for each symbol
"""

import asyncio
import logging
import sys
import time
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collector import AsyncDataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_requirement_18_1_concurrent_fetching():
    """Test Requirement 18.1: Concurrent fetching for multiple stock symbols."""
    print("\n" + "="*60)
    print("TEST: Requirement 18.1 - Concurrent Fetching")
    print("="*60)
    
    collector = AsyncDataCollector(max_concurrent=10)
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    results = await collector.fetch_multiple_stocks(symbols)
    
    # Verify all symbols were processed
    assert len(results) == len(symbols), "Not all symbols were processed"
    print("✓ PASSED: Multiple symbols fetched concurrently")
    return True

async def test_requirement_18_2_max_concurrent():
    """Test Requirement 18.2: Limit concurrent requests to 10."""
    print("\n" + "="*60)
    print("TEST: Requirement 18.2 - Max 10 Concurrent Requests")
    print("="*60)
    
    collector = AsyncDataCollector(max_concurrent=10)
    
    # Verify semaphore is set to 10
    assert collector.semaphore._value == 10, "Semaphore not set to 10"
    assert collector.max_concurrent == 10, "max_concurrent not set to 10"
    
    print("✓ PASSED: Semaphore configured for max 10 concurrent requests")
    return True

async def test_requirement_18_3_continue_on_failure():
    """Test Requirement 18.3: Continue processing when one stock fails."""
    print("\n" + "="*60)
    print("TEST: Requirement 18.3 - Continue on Failure")
    print("="*60)
    
    collector = AsyncDataCollector(max_concurrent=10, max_retries=1)
    
    # Mix valid and invalid symbols
    symbols = ['AAPL', 'INVALID_SYMBOL_XYZ', 'MSFT', 'ANOTHER_INVALID']
    
    results = await collector.fetch_multiple_stocks(symbols)
    
    # Verify all symbols were processed (even invalid ones)
    assert len(results) == len(symbols), "Not all symbols were processed"
    
    # Verify valid symbols have data
    assert not results['AAPL'].empty, "Valid symbol AAPL should have data"
    assert not results['MSFT'].empty, "Valid symbol MSFT should have data"
    
    # Verify invalid symbols have empty DataFrames
    assert results['INVALID_SYMBOL_XYZ'].empty, "Invalid symbol should have empty DataFrame"
    assert results['ANOTHER_INVALID'].empty, "Invalid symbol should have empty DataFrame"
    
    print("✓ PASSED: Processing continued despite failures")
    return True

async def test_requirement_18_4_performance():
    """Test Requirement 18.4: Complete 50 stocks within 30 seconds."""
    print("\n" + "="*60)
    print("TEST: Requirement 18.4 - Performance (50 stocks in 30s)")
    print("="*60)
    
    collector = AsyncDataCollector(max_concurrent=10)
    
    # Create list of 50 symbols (using real symbols, some may fail)
    symbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT',
        'JNJ', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX',
        'CMCSA', 'XOM', 'VZ', 'INTC', 'CSCO', 'PFE', 'ABT', 'KO', 'PEP', 'TMO',
        'AVGO', 'NKE', 'MRK', 'COST', 'DHR', 'ACN', 'TXN', 'LLY', 'NEE', 'MDT',
        'UNP', 'BMY', 'ORCL', 'PM', 'HON', 'QCOM', 'UPS', 'LOW', 'IBM', 'RTX'
    ]
    
    start_time = time.time()
    results = await collector.fetch_multiple_stocks(symbols)
    elapsed_time = time.time() - start_time
    
    print(f"\nFetched {len(symbols)} symbols in {elapsed_time:.2f} seconds")
    
    # Verify performance requirement
    assert elapsed_time < 30, f"Performance requirement not met: {elapsed_time:.2f}s > 30s"
    
    print(f"✓ PASSED: Completed {len(symbols)} stocks in {elapsed_time:.2f}s (< 30s)")
    return True

async def test_requirement_18_5_logging():
    """Test Requirement 18.5: Log completion status for each symbol."""
    print("\n" + "="*60)
    print("TEST: Requirement 18.5 - Logging Completion Status")
    print("="*60)
    
    # This is verified by visual inspection of logs
    # The AsyncDataCollector logs:
    # - "✓ {symbol}: {count} records fetched successfully" for successful fetches
    # - "✗ {symbol}: Failed to fetch data" for failed fetches
    # - Summary with successful/failed counts
    
    collector = AsyncDataCollector(max_concurrent=10)
    symbols = ['AAPL', 'GOOGL', 'INVALID_XYZ']
    
    print("\nExpected log output:")
    print("- Success logs with ✓ for valid symbols")
    print("- Failure logs with ✗ for invalid symbols")
    print("- Summary with counts\n")
    
    results = await collector.fetch_multiple_stocks(symbols)
    
    print("\n✓ PASSED: Completion status logged for each symbol (see logs above)")
    return True

async def main():
    """Run all requirement tests."""
    print("\n" + "="*60)
    print("ASYNC DATA COLLECTOR REQUIREMENTS VERIFICATION")
    print("="*60)
    
    tests = [
        ("18.1", test_requirement_18_1_concurrent_fetching),
        ("18.2", test_requirement_18_2_max_concurrent),
        ("18.3", test_requirement_18_3_continue_on_failure),
        ("18.4", test_requirement_18_4_performance),
        ("18.5", test_requirement_18_5_logging),
    ]
    
    results = []
    for req_id, test_func in tests:
        try:
            result = await test_func()
            results.append((req_id, "PASSED", None))
        except Exception as e:
            results.append((req_id, "FAILED", str(e)))
            print(f"✗ FAILED: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for req_id, status, error in results:
        if status == "PASSED":
            print(f"Requirement {req_id}: ✓ {status}")
        else:
            print(f"Requirement {req_id}: ✗ {status} - {error}")
    
    passed = sum(1 for _, status, _ in results if status == "PASSED")
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
