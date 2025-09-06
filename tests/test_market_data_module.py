#!/usr/bin/env python3
"""
Market Data Test Module
Tests market data functionality with real API calls
"""

import asyncio

import aiohttp

from finance_data_server.providers.market_client import MultiProviderClient


async def run_market_data_tests(runner):
    """Run market data tests with real API calls"""

    client = MultiProviderClient()

    async with aiohttp.ClientSession() as session:

        # Test 1: Stock Quote
        try:
            result = await client.get_stock_quote(session, "AAPL")
            if "data" in result and "c" in result["data"]:
                price = result["data"]["c"]
                provider = result.get("provider", "unknown")
                runner.add_result(
                    "Market Data", "Stock Quote", True, f"AAPL: ${price} via {provider}"
                )
            else:
                runner.add_result(
                    "Market Data",
                    "Stock Quote",
                    False,
                    f"Error: {result.get('error', 'No data')}",
                )
        except Exception as e:
            runner.add_result("Market Data", "Stock Quote", False, f"Exception: {e}")

        # Test 2: Stock Fundamentals
        try:
            result = await client.get_stock_fundamentals(session, "AAPL")
            if "data" in result:
                provider = result.get("provider", "unknown")
                runner.add_result(
                    "Market Data",
                    "Stock Fundamentals",
                    True,
                    f"Fundamentals via {provider}",
                )
            else:
                runner.add_result(
                    "Market Data",
                    "Stock Fundamentals",
                    False,
                    f"Error: {result.get('error', 'No data')}",
                )
        except Exception as e:
            runner.add_result(
                "Market Data", "Stock Fundamentals", False, f"Exception: {e}"
            )

        # Test 3: Technical Indicators
        try:
            result = await client.get_technical_indicators(session, "AAPL", "RSI")
            if "data" in result:
                provider = result.get("provider", "unknown")
                runner.add_result(
                    "Market Data", "Technical Indicators", True, f"RSI via {provider}"
                )
            else:
                runner.add_result(
                    "Market Data",
                    "Technical Indicators",
                    False,
                    f"Error: {result.get('error', 'No data')}",
                )
        except Exception as e:
            runner.add_result(
                "Market Data", "Technical Indicators", False, f"Exception: {e}"
            )

        # Test 4: Market Status
        try:
            result = await client.get_market_status(session)
            if "data" in result:
                is_open = result["data"].get("isOpen", "unknown")
                provider = result.get("provider", "unknown")
                runner.add_result(
                    "Market Data",
                    "Market Status",
                    True,
                    f"Market open: {is_open} via {provider}",
                )
            else:
                runner.add_result(
                    "Market Data",
                    "Market Status",
                    False,
                    f"Error: {result.get('error', 'No data')}",
                )
        except Exception as e:
            runner.add_result("Market Data", "Market Status", False, f"Exception: {e}")
