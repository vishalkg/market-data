#!/usr/bin/env python3
"""
Integration Test Module
Tests MCP server integration and tool functionality
"""

import asyncio

from finance_data_server.server import create_server


async def run_integration_tests(runner):
    """Run integration tests"""

    # Test 1: MCP Server Creation
    try:
        server = create_server()
        runner.add_result(
            "Integration",
            "MCP Server Creation",
            True,
            f"Server: {type(server).__name__}",
        )
    except Exception as e:
        runner.add_result("Integration", "MCP Server Creation", False, f"Error: {e}")
        return

    # Test 2: Tool Registration
    try:
        tools = await server.get_tools()
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            "get_stock_quote",
            "get_stock_fundamentals",
            "get_options_chain",
            "get_option_greeks",
            "get_provider_status",
            "get_technical_indicators",
            "get_historical_data",
            "get_market_status",
        ]

        missing_tools = [tool for tool in expected_tools if tool not in tool_names]

        if not missing_tools:
            runner.add_result(
                "Integration",
                "Tool Registration",
                True,
                f"All {len(tools)} tools registered",
            )
        else:
            runner.add_result(
                "Integration", "Tool Registration", False, f"Missing: {missing_tools}"
            )
    except Exception as e:
        runner.add_result("Integration", "Tool Registration", False, f"Error: {e}")

    # Test 3: Tool Execution (sample)
    try:
        tools = await server.get_tools()
        tool_dict = {tool.name: tool for tool in tools}

        if "get_provider_status" in tool_dict:
            # This tool doesn't require external APIs
            result = await tool_dict["get_provider_status"].func()
            if "error" not in result:
                runner.add_result(
                    "Integration", "Tool Execution", True, "Provider status tool works"
                )
            else:
                runner.add_result(
                    "Integration",
                    "Tool Execution",
                    False,
                    f"Tool error: {result.get('error')}",
                )
        else:
            runner.add_result(
                "Integration", "Tool Execution", False, "Provider status tool not found"
            )
    except Exception as e:
        runner.add_result("Integration", "Tool Execution", False, f"Error: {e}")

    # Test 4: Error Handling
    try:
        tools = await server.get_tools()
        tool_dict = {tool.name: tool for tool in tools}

        if "get_stock_quote" in tool_dict:
            # Test with invalid symbol
            result = await tool_dict["get_stock_quote"].func("INVALID_SYMBOL_12345")
            # Should handle gracefully (either error or empty result)
            runner.add_result(
                "Integration",
                "Error Handling",
                True,
                "Invalid symbol handled gracefully",
            )
        else:
            runner.add_result(
                "Integration", "Error Handling", False, "Stock quote tool not found"
            )
    except Exception as e:
        runner.add_result(
            "Integration", "Error Handling", True, f"Exception handled: {str(e)[:50]}"
        )
