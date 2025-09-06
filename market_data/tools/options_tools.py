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
        """Get professional options chain data for volatility trading, strategy construction, and risk management.

        WHEN TO USE: Options strategies (straddles, strangles, spreads, covered calls), volatility analysis,
        hedging strategies, arbitrage opportunities, Greeks analysis, market making, institutional trading.

        WHEN NOT TO USE: Basic stock analysis (use stock tools), fundamental research (use fundamentals),
        simple buy/hold strategies (use stock quotes), dividend analysis (use fundamentals).

        Professional-grade data: Robinhood primary (unlimited, real-time) + Finnhub fallback.
        ATM-focused optimization for active traders. Used by hedge funds and professional options traders.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            expiration_date: Optional expiration filter (YYYY-MM-DD format)
            max_expirations: Maximum expirations to return (default: 3, optimized for speed)
            include_greeks: Include Delta, Gamma, Theta, Vega (slower but complete analysis)
            raw_data: Return all strikes without ATM filtering (comprehensive analysis)

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
            # Use unified options provider with Robinhood primary + Finnhub fallback
            from ..providers.unified_options_provider import UnifiedOptionsProvider

            unified_provider = UnifiedOptionsProvider()

            result = await unified_provider.get_options_chain(
                symbol=symbol,
                expiration=expiration_date,
                max_expirations=max_expirations,
                raw_data=raw_data,
                include_greeks=include_greeks,
            )

            # Keep session active for better performance
            # unified_provider.logout()  # Removed to maintain session

            # Wrap result in expected format for MCP
            if "error" in result:
                return {
                    "provider": result.get("provider", "unified"),
                    "error": result["error"],
                    "symbol": symbol,
                }
            else:
                return {
                    "provider": result.get("provider", "unified"),
                    "data": result,
                    "symbol": symbol,
                }

        except Exception as e:
            logger.error(f"Unified options provider failed for {symbol}: {e}")

            # Final fallback to original multi-provider system
            async with aiohttp.ClientSession() as session:
                try:
                    result = await multi_client.get_options_chain(
                        session, symbol, expiration_date, max_expirations
                    )

                    if isinstance(result, dict) and "error" in result:
                        error_msg = result.get("error", "")
                        if "401" in error_msg or "Invalid API key" in error_msg:
                            return {
                                "error": "All options providers failed",
                                "provider": "fallback_failed",
                                "details": "Both Robinhood and Finnhub unavailable",
                                "symbol": symbol,
                            }

                    return {
                        "provider": "finnhub_final_fallback",
                        "data": result,
                        "symbol": symbol,
                    }

                except Exception as fallback_error:
                    logger.error(
                        f"Final fallback failed for {symbol}: {fallback_error}"
                    )
                    return {
                        "error": "All options providers failed",
                        "provider": "all_failed",
                        "primary_error": str(e),
                        "fallback_error": str(fallback_error),
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
        Used by options market makers and quantitative trading firms.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            strike: Strike price of the option (e.g., 240.0)
            expiration_date: Expiration date in YYYY-MM-DD format
            option_type: 'call' or 'put'

        Returns:
            dict: Greeks data with Delta, Gamma, Theta, Vega, Rho, IV,
                  plus current market data (bid, ask, volume, OI)

        Example:
            get_option_greeks('AAPL', 240.0, '2025-09-20', 'call') -> {
                "greeks": {"delta": 0.65, "gamma": 0.02, ...}, "market_data": {...}
            }
        """
        logger.info(
            f"get_option_greeks called for {symbol} {strike} {expiration_date} {option_type}"
        )

        try:
            from ..providers.unified_options_provider import UnifiedOptionsProvider

            unified_provider = UnifiedOptionsProvider()

            result = await unified_provider.get_option_greeks(
                symbol=symbol,
                strike=strike,
                expiration=expiration_date,
                option_type=option_type,
            )

            # Keep session active for better performance
            # unified_provider.logout()  # Removed to maintain session

            if "error" in result:
                return {
                    "provider": result.get("provider", "unified"),
                    "error": result["error"],
                    "symbol": symbol,
                    "strike": strike,
                    "expiration": expiration_date,
                    "option_type": option_type,
                }
            else:
                return {
                    "provider": result.get("provider", "unified"),
                    "data": result,
                    "symbol": symbol,
                }

        except Exception as e:
            logger.error(f"Greeks analysis failed for {symbol} {strike}: {e}")
            return {
                "provider": "error",
                "error": f"Greeks analysis unavailable: {str(e)}",
                "symbol": symbol,
                "note": "Greeks require Robinhood authentication",
            }

    @mcp.tool()
    async def get_provider_status() -> dict:
        """Get status of all data providers and their capabilities.

        Shows authentication status, rate limits, and available features
        for Robinhood (primary) and Finnhub (fallback) providers.

        Returns:
            dict: Provider status, authentication state, and capabilities

        Example:
            get_provider_status() -> {
                "robinhood": "authenticated", "finnhub": "available",
                "options_source": "robinhood", "greeks_available": true
            }
        """
        logger.info("get_provider_status called")

        try:
            from ..providers.unified_options_provider import UnifiedOptionsProvider

            unified_provider = UnifiedOptionsProvider()
            status = unified_provider.get_provider_status()

            # Add capability information
            enhanced_status = {
                **status,
                "options_primary_source": (
                    "robinhood"
                    if status["robinhood_status"] == "authenticated"
                    else "finnhub"
                ),
                "greeks_available": status["robinhood_status"] == "authenticated",
                "rate_limits": {
                    "robinhood": "unlimited (authenticated account)",
                    "finnhub": "60 requests/min (fallback)",
                },
                "data_quality": {
                    "robinhood": "professional-grade, real-time, complete Greeks",
                    "finnhub": "basic options data, limited Greeks",
                },
            }

            # Keep session active for better performance
            # unified_provider.logout()  # Removed to maintain session

            return {"provider": "unified_status", "data": enhanced_status}

        except Exception as e:
            logger.error(f"Provider status check failed: {e}")
            return {"provider": "error", "error": f"Status check failed: {str(e)}"}
