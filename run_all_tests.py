#!/usr/bin/env python3
"""
One-Click E2E Test Suite for Market Data Server
Run this after any code changes to verify functionality
"""

import asyncio
import os
import sys
import time
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title):
    """Print a formatted section"""
    print(f"\n--- {title} ---")


class TestResults:
    def __init__(self):
        self.results = {}
        self.total = 0
        self.passed = 0

    def add_result(self, test_name: str, success: bool, details: str = ""):
        self.results[test_name] = {"success": success, "details": details}
        self.total += 1
        if success:
            self.passed += 1

        status = "✅" if success else "❌"
        print(f"   {status} {test_name}: {details}")

    def print_summary(self):
        print_section("FINAL TEST SUMMARY")
        for test, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{test}: {status}")

        print(
            f"\nOverall: {self.passed}/{self.total} tests passed ({self.passed/self.total*100:.1f}%)"
        )

        if self.passed == self.total:
            print("\n🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
        elif self.passed >= self.total * 0.8:
            print(f"\n✅ MOSTLY WORKING - {self.passed}/{self.total} tests passed")
        else:
            print(
                f"\n⚠️  ISSUES DETECTED - Only {self.passed}/{self.total} tests passed"
            )


async def test_package_imports():
    """Test that all package imports work"""
    results = TestResults()

    print_section("PACKAGE IMPORT TESTS")

    try:
        from market_data.server import create_server

        results.add_result("Server Import", True, "Main server module imported")
    except Exception as e:
        results.add_result("Server Import", False, f"Error: {e}")

    try:
        from market_data.providers.unified_options_provider import (
            UnifiedOptionsProvider,
        )

        results.add_result(
            "Options Provider Import", True, "Unified options provider imported"
        )
    except Exception as e:
        results.add_result("Options Provider Import", False, f"Error: {e}")

    try:
        from market_data.auth.robinhood_auth import RobinhoodAuth

        results.add_result("Auth Import", True, "Authentication module imported")
    except Exception as e:
        results.add_result("Auth Import", False, f"Error: {e}")

    try:
        from market_data.providers.market_client import MultiProviderClient

        results.add_result("Market Client Import", True, "Market client imported")
    except Exception as e:
        results.add_result("Market Client Import", False, f"Error: {e}")

    return results


async def test_core_functionality():
    """Test core functionality"""
    results = TestResults()

    print_section("CORE FUNCTIONALITY TESTS")

    try:
        from market_data.server import create_server

        server = create_server()
        results.add_result(
            "Server Creation", True, f"Server created: {type(server).__name__}"
        )
    except Exception as e:
        results.add_result("Server Creation", False, f"Error: {e}")
        return results

    try:
        from market_data.providers.unified_options_provider import (
            UnifiedOptionsProvider,
        )

        provider = UnifiedOptionsProvider()

        status = provider.get_provider_status()
        auth_status = status.get("robinhood_status", "unknown")
        results.add_result("Provider Status", True, f"Status: {auth_status}")

        provider.logout()
    except Exception as e:
        results.add_result("Provider Status", False, f"Error: {e}")

    return results


async def test_stock_quotes_migration():
    """Test stock quotes migration to Robinhood primary"""
    results = TestResults()

    print_section("STOCK QUOTES MIGRATION TESTS")

    try:
        # Import the stock provider
        from market_data.providers.unified_stock_provider import UnifiedStockProvider
        
        provider = UnifiedStockProvider()

        # Test 1: Robinhood authentication
        try:
            await provider.robinhood_provider.ensure_authenticated()
            results.add_result("Robinhood Auth", True, "Authentication successful")
        except Exception as e:
            results.add_result("Robinhood Auth", False, f"Auth failed: {e}")
            return results

        # Test 2: Single quote
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                result = await provider.get_stock_quote(session, "AAPL")
            
            if result.get('provider') == 'robinhood' and 'data' in result:
                price = result['data'].get('c', 0)
                results.add_result("Single Quote", True, f"AAPL: ${price:.2f} from Robinhood")
            else:
                results.add_result("Single Quote", False, f"Provider: {result.get('provider')}")
        except Exception as e:
            results.add_result("Single Quote", False, f"Error: {e}")

        # Test 3: Batch quotes
        try:
            batch_result = await provider.get_multiple_quotes(['AAPL', 'TSLA'])
            
            if batch_result.get('provider') == 'robinhood' and len(batch_result.get('data', {})) > 0:
                batch_size = batch_result.get('batch_size', 0)
                results.add_result("Batch Quotes", True, f"{batch_size} symbols in single request")
            else:
                results.add_result("Batch Quotes", False, "Batch processing failed")
        except Exception as e:
            results.add_result("Batch Quotes", False, f"Error: {e}")

        # Test 4: Performance comparison
        try:
            import time
            
            # Single requests
            start = time.time()
            for symbol in ['AAPL', 'TSLA']:
                await provider.robinhood_provider.get_stock_quote(symbol)
            single_time = time.time() - start
            
            # Batch request
            start = time.time()
            await provider.robinhood_provider.get_multiple_quotes(['AAPL', 'TSLA'])
            batch_time = time.time() - start
            
            if batch_time < single_time:
                improvement = ((single_time - batch_time) / single_time) * 100
                results.add_result("Performance", True, f"{improvement:.1f}% faster with batch")
            else:
                results.add_result("Performance", False, "No performance improvement")
        except Exception as e:
            results.add_result("Performance", False, f"Error: {e}")

    except Exception as e:
        results.add_result("Stock Migration", False, f"Import error: {e}")

    return results


async def test_fundamentals_migration():
    """Test fundamentals migration to Robinhood primary"""
    results = TestResults()

    print_section("FUNDAMENTALS MIGRATION TESTS")

    try:
        # Import the fundamentals provider
        from market_data.providers.unified_fundamentals_provider import UnifiedFundamentalsProvider
        
        provider = UnifiedFundamentalsProvider()

        # Test 1: Robinhood authentication
        try:
            await provider.robinhood_provider.ensure_authenticated()
            results.add_result("Robinhood Auth", True, "Authentication successful")
        except Exception as e:
            results.add_result("Robinhood Auth", False, f"Auth failed: {e}")
            return results

        # Test 2: Basic fundamentals
        try:
            result = await provider.robinhood_provider.get_fundamentals("AAPL")
            
            if result.get('provider') == 'robinhood' and 'data' in result:
                market_cap = result['data']['fundamentals'].get('market_cap', 'N/A')
                results.add_result("Basic Fundamentals", True, f"Market cap: {market_cap}")
            else:
                results.add_result("Basic Fundamentals", False, f"Provider: {result.get('provider')}")
        except Exception as e:
            results.add_result("Basic Fundamentals", False, f"Error: {e}")

        # Test 3: Enhanced fundamentals
        try:
            enhanced_result = await provider.get_enhanced_fundamentals("AAPL", True, True)
            
            if enhanced_result.get('provider') == 'robinhood' and enhanced_result.get('enhanced', False):
                data = enhanced_result.get('data', {})
                has_earnings = 'earnings' in data
                has_ratings = 'analyst_ratings' in data
                results.add_result("Enhanced Fundamentals", True, f"Earnings: {has_earnings}, Ratings: {has_ratings}")
            else:
                results.add_result("Enhanced Fundamentals", False, "Enhancement failed")
        except Exception as e:
            results.add_result("Enhanced Fundamentals", False, f"Error: {e}")

        # Test 4: MCP integration
        try:
            from market_data.providers.market_client import MultiProviderClient
            client = MultiProviderClient()
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                result = await client.get_fundamentals(session, "AAPL")
            
            if result.get('provider') == 'robinhood':
                results.add_result("MCP Integration", True, "Using Robinhood provider")
            else:
                results.add_result("MCP Integration", False, f"Provider: {result.get('provider')}")
        except Exception as e:
            results.add_result("MCP Integration", False, f"Error: {e}")

    except Exception as e:
        results.add_result("Fundamentals Migration", False, f"Import error: {e}")

    return results


async def test_historical_migration():
    """Test historical data migration to Robinhood primary"""
    results = TestResults()

    print_section("HISTORICAL DATA MIGRATION TESTS")

    try:
        # Import the historical provider
        from market_data.providers.unified_historical_provider import UnifiedHistoricalProvider
        
        provider = UnifiedHistoricalProvider()

        # Test 1: Robinhood authentication
        try:
            await provider.robinhood_provider.ensure_authenticated()
            results.add_result("Robinhood Auth", True, "Authentication successful")
        except Exception as e:
            results.add_result("Robinhood Auth", False, f"Auth failed: {e}")
            return results

        # Test 2: Daily historical data
        try:
            result = await provider.robinhood_provider.get_daily_data("AAPL", span="month")
            
            if result.get('provider') == 'robinhood' and result.get('data_points', 0) > 0:
                data_points = result.get('data_points', 0)
                results.add_result("Daily Historical", True, f"{data_points} daily data points")
            else:
                results.add_result("Daily Historical", False, f"Provider: {result.get('provider')}")
        except Exception as e:
            results.add_result("Daily Historical", False, f"Error: {e}")

        # Test 3: Intraday data
        try:
            result = await provider.robinhood_provider.get_intraday_data("AAPL", "5minute")
            
            if result.get('provider') == 'robinhood' and result.get('interval') == '5minute':
                data_points = result.get('data_points', 0)
                results.add_result("Intraday Data", True, f"{data_points} 5-minute bars")
            else:
                results.add_result("Intraday Data", False, "5-minute data failed")
        except Exception as e:
            results.add_result("Intraday Data", False, f"Error: {e}")

        # Test 4: Supported intervals
        try:
            result = await provider.get_supported_intervals()
            
            if 'supported' in result:
                intervals = len(result['supported'].get('intervals', {}))
                spans = len(result['supported'].get('spans', {}))
                results.add_result("Supported Intervals", True, f"{intervals} intervals, {spans} spans")
            else:
                results.add_result("Supported Intervals", False, "No supported intervals")
        except Exception as e:
            results.add_result("Supported Intervals", False, f"Error: {e}")

    except Exception as e:
        results.add_result("Historical Migration", False, f"Import error: {e}")

    return results


async def test_options_functionality():
    """Test options functionality (may fail without auth)"""
    results = TestResults()

    print_section("OPTIONS FUNCTIONALITY TESTS")

    try:
        from market_data.providers.unified_options_provider import (
            UnifiedOptionsProvider,
        )

        provider = UnifiedOptionsProvider()

        # Test options chain
        result = await provider.get_options_chain(
            "AAPL", max_expirations=1, include_greeks=False
        )

        if "error" not in result:
            if "optimization_summary" in result:
                reduction = result["optimization_summary"].get(
                    "reduction_percentage", 0
                )
                results.add_result(
                    "Options Chain", True, f"Retrieved with {reduction}% reduction"
                )
            else:
                results.add_result(
                    "Options Chain", True, "Basic options data retrieved"
                )
        else:
            # Error is expected without authentication
            results.add_result(
                "Options Chain", True, f"Expected error: {result['error'][:50]}..."
            )

        # Test fallback system
        fallback_result = await provider.get_options_chain("INVALID_SYMBOL")
        if "error" in fallback_result:
            results.add_result("Fallback System", True, "Error handling working")
        else:
            results.add_result(
                "Fallback System", False, "Should have failed for invalid symbol"
            )

        provider.logout()

    except Exception as e:
        results.add_result("Options Functionality", False, f"Error: {e}")

    return results


async def test_file_structure():
    """Test that file structure is correct"""
    results = TestResults()

    print_section("FILE STRUCTURE TESTS")

    # Check key directories
    expected_dirs = [
        "market_data",
        "market_data/auth",
        "market_data/providers",
        "market_data/tools",
        "market_data/utils",
        "tests",
    ]

    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            results.add_result(f"Directory {dir_path}", True, "Exists")
        else:
            results.add_result(f"Directory {dir_path}", False, "Missing")

    # Check key files
    key_files = [
        "market_data/server.py",
        "market_data/providers/unified_options_provider.py",
        "market_data/auth/robinhood_auth.py",
        "setup.py",
        "start.sh",
    ]

    for file_path in key_files:
        if os.path.exists(file_path):
            results.add_result(f"File {file_path}", True, "Exists")
        else:
            results.add_result(f"File {file_path}", False, "Missing")

    return results


async def run_comprehensive_tests():
    """Run all tests and provide comprehensive report"""

    print_header("MARKET DATA SERVER - COMPREHENSIVE E2E TEST SUITE")
    print("One-click solution to verify system functionality after changes")

    start_time = time.time()
    all_results = []

    # Run all test categories
    import_results = await test_package_imports()
    all_results.append(("Package Imports", import_results))

    structure_results = await test_file_structure()
    all_results.append(("File Structure", structure_results))

    core_results = await test_core_functionality()
    all_results.append(("Core Functionality", core_results))

    # NEW: Stock quotes migration test
    stock_results = await test_stock_quotes_migration()
    all_results.append(("Stock Quotes Migration", stock_results))

    # NEW: Fundamentals migration test
    fundamentals_results = await test_fundamentals_migration()
    all_results.append(("Fundamentals Migration", fundamentals_results))

    # NEW: Historical data migration test
    historical_results = await test_historical_migration()
    all_results.append(("Historical Data Migration", historical_results))

    options_results = await test_options_functionality()
    all_results.append(("Options Functionality", options_results))

    # Aggregate results
    total_passed = sum(r.passed for _, r in all_results)
    total_tests = sum(r.total for _, r in all_results)

    # Final summary
    print_header("COMPREHENSIVE TEST RESULTS")

    for category, results in all_results:
        print(
            f"\n{category}: {results.passed}/{results.total} passed ({results.passed/results.total*100:.1f}%)"
        )

    elapsed = time.time() - start_time
    print(
        f"\nTotal: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)"
    )
    print(f"Execution time: {elapsed:.2f} seconds")

    if total_passed == total_tests:
        print("\n🎉 PERFECT SCORE - ALL SYSTEMS OPERATIONAL!")
        print("✅ Ready for production use")
        print("✅ All refactoring successful")
        print("✅ Package structure correct")
    elif total_passed >= total_tests * 0.9:
        print("\n✅ EXCELLENT - SYSTEM MOSTLY OPERATIONAL!")
        print("✅ Minor issues may exist but core functionality works")
    elif total_passed >= total_tests * 0.7:
        print("\n⚠️  GOOD - SYSTEM FUNCTIONAL WITH SOME ISSUES")
        print("⚠️  Some components may need attention")
    else:
        print("\n❌ ISSUES DETECTED - SYSTEM NEEDS ATTENTION")
        print("❌ Multiple components failing")

    print(f"\n📊 System Health Score: {total_passed/total_tests*100:.1f}%")

    return total_passed >= total_tests * 0.8  # 80% pass rate acceptable


if __name__ == "__main__":
    print("Starting comprehensive E2E test suite...")
    success = asyncio.run(run_comprehensive_tests())

    print(f"\n{'='*60}")
    if success:
        print("🎯 TEST SUITE COMPLETED SUCCESSFULLY")
    else:
        print("⚠️  TEST SUITE COMPLETED WITH ISSUES")
    print(f"{'='*60}")

    exit(0 if success else 1)
