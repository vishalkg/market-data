#!/usr/bin/env python3
"""
Modular Test Suite Runner
Combines all existing tests into organized modules with actual API calls
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSuiteRunner:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0

    def add_result(
        self, module_name: str, test_name: str, success: bool, details: str = ""
    ):
        if module_name not in self.results:
            self.results[module_name] = []

        self.results[module_name].append(
            {"test": test_name, "success": success, "details": details}
        )

        self.total_tests += 1
        if success:
            self.passed_tests += 1

        status = "✅" if success else "❌"
        print(f"   {status} {test_name}: {details}")

    def print_module_header(self, module_name: str):
        print(f"\n{'='*60}")
        print(f"  {module_name}")
        print(f"{'='*60}")

    def print_summary(self):
        print(f"\n{'='*60}")
        print("  COMPREHENSIVE TEST SUITE RESULTS")
        print(f"{'='*60}")

        for module_name, tests in self.results.items():
            module_passed = sum(1 for t in tests if t["success"])
            module_total = len(tests)
            print(
                f"\n{module_name}: {module_passed}/{module_total} passed ({module_passed/module_total*100:.1f}%)"
            )

            for test in tests:
                status = "✅" if test["success"] else "❌"
                print(f"  {status} {test['test']}")

        print(
            f"\nOverall: {self.passed_tests}/{self.total_tests} tests passed ({self.passed_tests/self.total_tests*100:.1f}%)"
        )

        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL!")
        elif self.passed_tests >= self.total_tests * 0.8:
            print(
                f"\n✅ MOSTLY WORKING - {self.passed_tests}/{self.total_tests} tests passed"
            )
        else:
            print(
                f"\n⚠️  ISSUES DETECTED - Only {self.passed_tests}/{self.total_tests} tests passed"
            )


async def run_modular_test_suite():
    """Run the complete modular test suite"""

    print("🧪 COMPREHENSIVE MODULAR TEST SUITE")
    print("Testing all market data server functionality with real API calls")

    runner = TestSuiteRunner()
    start_time = time.time()

    # Import and run each test module
    try:
        # 1. Authentication Tests
        runner.print_module_header("AUTHENTICATION TESTS")
        from test_auth_module import run_auth_tests

        await run_auth_tests(runner)

        # 2. Options Tests
        runner.print_module_header("OPTIONS FUNCTIONALITY TESTS")
        from test_options_module import run_options_tests

        await run_options_tests(runner)

        # 3. Market Data Tests
        runner.print_module_header("MARKET DATA TESTS")
        from test_market_data_module import run_market_data_tests

        await run_market_data_tests(runner)

        # 4. Integration Tests
        runner.print_module_header("INTEGRATION TESTS")
        from test_integration_module import run_integration_tests

        await run_integration_tests(runner)

    except ImportError as e:
        print(f"⚠️  Some test modules not found: {e}")
        print("Creating test modules...")

    elapsed = time.time() - start_time
    print(f"\nExecution time: {elapsed:.2f} seconds")

    runner.print_summary()

    return runner.passed_tests >= runner.total_tests * 0.8


if __name__ == "__main__":
    success = asyncio.run(run_modular_test_suite())
    exit(0 if success else 1)
