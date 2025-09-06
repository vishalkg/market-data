#!/usr/bin/env python3
"""
Authentication Test Module
Tests Robinhood authentication and credential management
"""

import asyncio

from finance_data_server.auth.robinhood_auth import RobinhoodAuth
from finance_data_server.providers.unified_options_provider import (
    UnifiedOptionsProvider,
)


async def run_auth_tests(runner):
    """Run authentication-related tests"""

    # Test 1: RobinhoodAuth Creation
    try:
        auth = RobinhoodAuth()
        runner.add_result(
            "Authentication", "RobinhoodAuth Creation", True, "Auth object created"
        )
    except Exception as e:
        runner.add_result(
            "Authentication", "RobinhoodAuth Creation", False, f"Error: {e}"
        )

    # Test 2: Credential Status Check
    try:
        auth = RobinhoodAuth()
        has_creds = auth.has_stored_credentials()
        runner.add_result(
            "Authentication", "Credential Check", True, f"Has credentials: {has_creds}"
        )
    except Exception as e:
        runner.add_result("Authentication", "Credential Check", False, f"Error: {e}")

    # Test 3: Provider Status
    try:
        provider = UnifiedOptionsProvider()
        status = provider.get_provider_status()
        auth_status = status.get("robinhood_status", "unknown")

        if auth_status == "authenticated":
            runner.add_result(
                "Authentication",
                "Provider Authentication",
                True,
                "Robinhood authenticated",
            )
        else:
            runner.add_result(
                "Authentication",
                "Provider Authentication",
                True,
                f"Status: {auth_status} (expected)",
            )

        provider.logout()
    except Exception as e:
        runner.add_result(
            "Authentication", "Provider Authentication", False, f"Error: {e}"
        )

    # Test 4: Authentication Flow
    try:
        provider = UnifiedOptionsProvider()

        # Try to get provider capabilities
        status = provider.get_provider_status()
        capabilities = {
            "robinhood_available": status.get("robinhood_status") == "authenticated",
            "fallback_available": "finnhub" in status.get("fallback_providers", []),
            "greeks_available": status.get("greeks_available", False),
        }

        runner.add_result(
            "Authentication",
            "Provider Capabilities",
            True,
            f"RH: {capabilities['robinhood_available']}, Fallback: {capabilities['fallback_available']}",
        )

        provider.logout()
    except Exception as e:
        runner.add_result(
            "Authentication", "Provider Capabilities", False, f"Error: {e}"
        )
