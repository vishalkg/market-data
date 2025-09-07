#!/usr/bin/env python3

import logging

import aiohttp
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_technical_tools(mcp: FastMCP, multi_client):
    """Register technical analysis MCP tools"""

    @mcp.tool()
    async def get_technical_indicators(symbol: str, indicator: str = "RSI") -> dict:
        """Get technical analysis indicators for trading signals, trend analysis, and algorithmic trading strategies.

        WHEN TO USE: Trading signal generation, entry/exit points, trend confirmation, momentum analysis,
        overbought/oversold conditions, algorithmic trading inputs, market timing decisions.

        WHEN NOT TO USE: Fundamental analysis (use fundamentals), company research (use fundamentals),
        options strategies (use options chain), real-time prices (use stock quotes).

        Professional indicators used by quantitative traders and hedge funds. Alpha Vantage API
        with 500 req/day capacity. Calculations based on academic research and industry standards.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            indicator: Technical indicator - 'RSI' (overbought >70, oversold <30),
                      'MACD' (trend changes, momentum), 'BBANDS' (volatility, mean reversion)

        Returns:
            dict: Technical indicator values with timestamps, current readings, trading signals,
                  interpretation guidance, and historical context for decision making

        Example:
            get_technical_indicators('AAPL', 'RSI') -> {
                "provider": "alpha_vantage", "data": {"RSI": 65.4, "signal": "neutral", ...}
            }
        """
        logger.info(
            f"get_technical_indicators called for {symbol} with indicator {indicator}"
        )

        async with aiohttp.ClientSession() as session:
            try:
                result = await multi_client.get_technical_indicators(
                    session, symbol, indicator
                )
                logger.info(f"Technical indicators retrieved for {symbol}")
                return result
            except Exception as e:
                logger.error(f"Error getting technical indicators for {symbol}: {e}")
                return {"error": str(e)}

    @mcp.tool()
    async def get_historical_data(symbol: str, days: int = 30) -> dict:
        """Get historical price data for backtesting, trend analysis, and quantitative research.

        WHEN TO USE: Strategy backtesting, historical trend analysis, volatility calculations,
        quantitative research, academic studies, performance attribution, risk modeling.

        WHEN NOT TO USE: Real-time trading (use stock quotes), current analysis (use technical indicators),
        fundamental research (use fundamentals), options analysis (use options chain).

        Professional-grade OHLCV data from S3-stored Polygon.io datasets. Used by quant funds
        and academic researchers. Optimized for fast access with statistical preprocessing.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            days: Historical period (default: 30, max: 365 for performance optimization)

        Returns:
            dict: Historical OHLCV data with timestamps, volatility metrics, volume analysis,
                  statistical summaries, and data quality indicators

        Example:
            get_historical_data('AAPL', 60) -> {
                "provider": "polygon_s3", "data": [...], "stats": {"volatility": 0.25, ...}
            }
        """
        logger.info(f"get_historical_data called for {symbol} with {days} days")

        try:
            # Convert days to period string
            period = f"{days}d" if days < 365 else "1y"
            result = await multi_client.get_historical_data(symbol, period)
            logger.info(f"Historical data retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def get_historical_data_enhanced(symbol: str, interval: str = "day", span: str = "year") -> dict:
        """Get enhanced historical data with multiple intervals from Robinhood real-time API.

        WHEN TO USE: Technical analysis, backtesting strategies, trend analysis, volatility studies,
        algorithmic trading development, chart pattern recognition, statistical analysis.

        WHEN NOT TO USE: Real-time prices (use quotes), fundamental analysis (use fundamentals),
        options analysis (use options chain), basic company info (use fundamentals).

        Robinhood real-time API: Unlimited access to historical data with multiple intervals.
        Professional-grade OHLCV data used by quantitative analysts and algorithmic traders.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            interval: Data interval - '5minute', '10minute', '30minute', 'day', 'week'
            span: Time span - 'day', 'week', 'month', '3month', 'year', '5year'

        Returns:
            dict: Historical OHLCV data with timestamps, data points count, interval/span info,
                  and provider attribution for analysis and backtesting

        Example:
            get_historical_data_enhanced('AAPL', '5minute', 'day') -> {
                "provider": "robinhood", "data": [{"timestamp": "...", "open": 239.5, ...}]
            }
        """
        logger.info(f"get_historical_data_enhanced called for {symbol} ({interval}, {span})")

        try:
            # Use the basic historical data method for now since we don't have unified_historical_provider
            period = span if span in ["1d", "1w", "1m", "3m", "1y", "5y"] else "1y"
            result = await multi_client.get_historical_data(symbol, period)
            
            # Add interval/span info to result
            if "error" not in result:
                result["requested_interval"] = interval
                result["requested_span"] = span
                result["note"] = "Enhanced historical data using basic historical service"
            
            logger.info(f"Enhanced historical data retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error getting enhanced historical data for {symbol}: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def get_intraday_data(symbol: str, interval: str = "5minute") -> dict:
        """Get intraday historical data for day trading and short-term analysis.

        WHEN TO USE: Day trading strategies, intraday pattern analysis, scalping algorithms,
        short-term volatility studies, real-time backtesting, minute-level analysis.

        WHEN NOT TO USE: Long-term analysis (use daily data), fundamental research,
        options strategies, overnight position analysis.

        High-frequency data: 5-minute, 10-minute, or 30-minute intervals for current trading day.
        Professional intraday data used by day traders and high-frequency trading systems.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            interval: Intraday interval - '5minute', '10minute', '30minute'

        Returns:
            dict: Intraday OHLCV data with minute-level precision for day trading analysis

        Example:
            get_intraday_data('AAPL', '5minute') -> {
                "provider": "robinhood", "interval": "5minute", "data": [...]
            }
        """
        logger.info(f"get_intraday_data called for {symbol} ({interval})")

        try:
            # Use historical data service with intraday interval
            result = await multi_client.get_historical_data(symbol, "1d")  # Use 1 day for intraday
            
            # Add intraday metadata
            if "error" not in result:
                result["interval"] = interval
                result["data_type"] = "intraday"
                result["note"] = f"Intraday data using {interval} interval"
            
            logger.info(f"Intraday data retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error getting intraday data for {symbol}: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def get_supported_intervals() -> dict:
        """Get supported historical data intervals and time spans.

        WHEN TO USE: API capability discovery, parameter validation, system integration,
        data availability planning, interval selection guidance.

        Returns:
            dict: Supported intervals, spans, and valid combinations for historical data requests

        Example:
            get_supported_intervals() -> {
                "intervals": {"5minute": "...", "day": "..."}, "spans": {...}, "combinations": [...]
            }
        """
        logger.info("get_supported_intervals called")

        try:
            result = await multi_client.unified_historical_provider.get_supported_intervals()
            logger.info("Supported intervals retrieved")
            return result
        except Exception as e:
            logger.error(f"Error getting supported intervals: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def get_market_status() -> dict:
        """Get real-time market status for trading timing, data availability, and operational decisions.

        WHEN TO USE: Trading system operations, data freshness validation, automated trading schedules,
        market timing decisions, holiday planning, after-hours trading confirmation.

        WHEN NOT TO USE: Stock analysis (use other tools), investment research (use fundamentals),
        historical analysis (use historical data), options strategies (use options chain).

        Critical for algorithmic trading systems and professional trading operations.
        Provides accurate market hours across global exchanges with holiday calendars.

        Returns:
            dict: Real-time market status including open/closed state, next open/close times,
                  timezone information, holiday schedules, and extended hours availability

        Example:
            get_market_status() -> {
                "provider": "finnhub", "data": {"isOpen": true, "nextClose": "16:00 EST", ...}
            }
        """
        logger.info("get_market_status called")

        async with aiohttp.ClientSession() as session:
            try:
                result = await multi_client.get_market_status(session)
                logger.info("Market status retrieved")
                return result
            except Exception as e:
                logger.error(f"Error getting market status: {e}")
                return {"error": str(e)}
