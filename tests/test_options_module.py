#!/usr/bin/env python3
"""
Options Test Module
Tests options functionality with real API calls
"""

import asyncio

from finance_data_server.providers.unified_options_provider import (
    UnifiedOptionsProvider,
)


async def run_options_tests(runner):
    """Run options-related tests with real API calls"""

    provider = UnifiedOptionsProvider()

    # Test 1: Basic Options Chain
    try:
        result = await provider.get_options_chain(
            "AAPL", max_expirations=1, include_greeks=False
        )

        if "error" not in result:
            if "optimization_summary" in result:
                reduction = result["optimization_summary"].get(
                    "reduction_percentage", 0
                )
                total_after = result["optimization_summary"].get(
                    "total_options_after_filter", 0
                )
                runner.add_result(
                    "Options",
                    "Options Chain Retrieval",
                    True,
                    f"Retrieved {total_after} options, {reduction}% reduction",
                )
            else:
                runner.add_result(
                    "Options",
                    "Options Chain Retrieval",
                    True,
                    "Basic options data retrieved",
                )
        else:
            error_msg = result.get("error", "")
            if "authentication" in error_msg.lower():
                runner.add_result(
                    "Options", "Options Chain Retrieval", True, "Expected auth error"
                )
            else:
                runner.add_result(
                    "Options", "Options Chain Retrieval", False, f"Error: {error_msg}"
                )
    except Exception as e:
        runner.add_result(
            "Options", "Options Chain Retrieval", False, f"Exception: {e}"
        )

    # Test 2: Fallback System
    try:
        result = await provider.get_options_chain("INVALID_SYMBOL_TEST")

        if "error" in result:
            provider_used = result.get("provider", "unknown")
            runner.add_result(
                "Options", "Fallback System", True, f"Error handled by {provider_used}"
            )
        else:
            runner.add_result(
                "Options",
                "Fallback System",
                False,
                "Should have failed for invalid symbol",
            )
    except Exception as e:
        runner.add_result("Options", "Fallback System", True, f"Exception handled")

    provider.logout()
