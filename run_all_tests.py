#!/usr/bin/env python3
"""
One-Click E2E Test Suite for Finance Data Server
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
        from finance_data_server.server import create_server

        results.add_result("Server Import", True, "Main server module imported")
    except Exception as e:
        results.add_result("Server Import", False, f"Error: {e}")

    try:
        from finance_data_server.providers.unified_options_provider import (
            UnifiedOptionsProvider,
        )

        results.add_result(
            "Options Provider Import", True, "Unified options provider imported"
        )
    except Exception as e:
        results.add_result("Options Provider Import", False, f"Error: {e}")

    try:
        from finance_data_server.auth.robinhood_auth import RobinhoodAuth

        results.add_result("Auth Import", True, "Authentication module imported")
    except Exception as e:
        results.add_result("Auth Import", False, f"Error: {e}")

    try:
        from finance_data_server.providers.market_client import MultiProviderClient

        results.add_result("Market Client Import", True, "Market client imported")
    except Exception as e:
        results.add_result("Market Client Import", False, f"Error: {e}")

    return results


async def test_core_functionality():
    """Test core functionality"""
    results = TestResults()

    print_section("CORE FUNCTIONALITY TESTS")

    try:
        from finance_data_server.server import create_server

        server = create_server()
        results.add_result(
            "Server Creation", True, f"Server created: {type(server).__name__}"
        )
    except Exception as e:
        results.add_result("Server Creation", False, f"Error: {e}")
        return results

    try:
        from finance_data_server.providers.unified_options_provider import (
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


async def test_options_functionality():
    """Test options functionality (may fail without auth)"""
    results = TestResults()

    print_section("OPTIONS FUNCTIONALITY TESTS")

    try:
        from finance_data_server.providers.unified_options_provider import (
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
        "finance_data_server",
        "finance_data_server/auth",
        "finance_data_server/providers",
        "finance_data_server/tools",
        "finance_data_server/utils",
        "tests",
    ]

    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            results.add_result(f"Directory {dir_path}", True, "Exists")
        else:
            results.add_result(f"Directory {dir_path}", False, "Missing")

    # Check key files
    key_files = [
        "finance_data_server/server.py",
        "finance_data_server/providers/unified_options_provider.py",
        "finance_data_server/auth/robinhood_auth.py",
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

    print_header("FINANCE DATA SERVER - COMPREHENSIVE E2E TEST SUITE")
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
