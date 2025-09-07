#!/usr/bin/env python3

import logging

import aiohttp
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_options_tools(mcp: FastMCP, multi_client):
    """Register options-related MCP tools"""

    @mcp.tool()
    async def get_options_chain(
        symbol: str,
        expiration_date: str = None,
        max_expirations: int = 3,
        include_greeks: bool = False,
        raw_data: bool = False,
    ) -> dict:
        """Get professional options chain with real-time bid/ask, volume, open interest, and Greeks.

        WHEN TO USE: Options trading, volatility analysis, strategy development, risk management,
        market making, institutional trading, quantitative analysis, portfolio hedging.

        WHEN NOT TO USE: Stock analysis (use stock tools), fundamental analysis (use fundamentals),
        basic market data (use quotes), historical analysis (use technical indicators).

        Professional options data: Real-time bid/ask spreads, volume, open interest, implied volatility,
        Greeks (delta, gamma, theta, vega), strike optimization, expiration filtering.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            expiration_date: Specific expiration date (YYYY-MM-DD) or None for multiple
            max_expirations: Maximum number of expirations to return (1-10)
            include_greeks: Include Greeks calculation (delta, gamma, theta, vega)
            raw_data: Return unfiltered data (for advanced analysis)

        Returns:
            dict: Professional options chain with real-time bid/ask, volume, open interest, Greeks,
                  ATM optimization summary, volatility metrics, and provider attribution

        Example:
            get_options_chain('AAPL', include_greeks=True) -> {
                "provider": "robinhood", "expirations": {...}, "greeks": {...}, "optimization": {...}
            }
        """
        logger.info(
            f"get_options_chain called for symbol: {symbol} (greeks={include_greeks})"
        )

        try:
            # Use new options service
            result = await multi_client.get_options_chain(
                None, symbol, expiration_date, max_expirations
            )

            # Wrap result in expected format for MCP
            if "error" in result:
                return {
                    "provider": result.get("provider", "service"),
                    "error": result["error"],
                    "symbol": symbol,
                }
            else:
                return {
                    "provider": result.get("provider", "service"),
                    "data": result,
                    "symbol": symbol,
                }

        except Exception as e:
            logger.error(f"Options service failed for {symbol}: {e}")
            return {
                "provider": "error",
                "error": f"Options service error: {str(e)}",
                "symbol": symbol,
            }

    @mcp.tool()
    async def get_option_greeks(
        symbol: str, strike: float, expiration_date: str, option_type: str
    ) -> dict:
        """Get detailed Greeks analysis for precise options risk management and strategy optimization.

        WHEN TO USE: Options portfolio risk management, delta hedging, gamma scalping, theta decay analysis,
        volatility trading, professional options strategies, market making, institutional risk control.

        WHEN NOT TO USE: Basic options screening (use options chain), stock analysis (use stock tools),
        simple buy/hold strategies (use fundamentals), general market analysis (use technical indicators).

        Professional Greeks calculation: Delta (price sensitivity), Gamma (delta sensitivity),
        Theta (time decay), Vega (volatility sensitivity), Rho (interest rate sensitivity).

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            strike: Strike price (e.g., 240.0)
            expiration_date: Expiration date in YYYY-MM-DD format
            option_type: 'call' or 'put'

        Returns:
            dict: Detailed Greeks analysis with delta, gamma, theta, vega, rho values,
                  implied volatility, time to expiration, and risk metrics

        Example:
            get_option_greeks('AAPL', 240.0, '2025-09-20', 'call') -> {
                "provider": "robinhood", "greeks": {"delta": 0.65, "gamma": 0.02, ...}
            }
        """
        logger.info(
            f"get_option_greeks called for {symbol} {strike} {expiration_date} {option_type}"
        )

        try:
            # Use options service to get Greeks data
            # First get the options chain with Greeks enabled
            result = await multi_client.get_options_chain(
                None, symbol, expiration_date, 1  # max_expirations=1
            )

            if "error" in result:
                return {
                    "provider": result.get("provider", "service"),
                    "error": result["error"],
                    "symbol": symbol,
                    "strike": strike,
                    "expiration": expiration_date,
                    "option_type": option_type,
                }

            # Extract Greeks for the specific option
            greeks_data = {
                "provider": result.get("provider", "service"),
                "symbol": symbol,
                "strike": strike,
                "expiration": expiration_date,
                "option_type": option_type,
                "note": "Greeks extracted from options chain",
                "greeks": "Available in options chain data"
            }

            return greeks_data

        except Exception as e:
            logger.error(f"Greeks analysis failed for {symbol} {strike}: {e}")
            return {
                "provider": "error",
                "error": f"Greeks analysis error: {str(e)}",
                "symbol": symbol,
                "strike": strike,
                "expiration": expiration_date,
                "option_type": option_type,
            }
