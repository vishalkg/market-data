#!/usr/bin/env python3

import logging

import aiohttp
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_stock_tools(mcp: FastMCP, multi_client):
    """Register stock-related MCP tools"""

    @mcp.tool()
    async def get_stock_quote(symbol: str) -> dict:
        """Get real-time stock market data for active trading, portfolio valuation, and market monitoring.

        WHEN TO USE: Current price requests, live trading decisions, portfolio P&L calculations,
        market alerts, intraday analysis, real-time market surveillance, algorithmic trading inputs.

        WHEN NOT TO USE: Historical analysis (use historical tools), company research (use fundamentals),
        technical patterns (use technical indicators), options analysis (use options chain).

        Professional-grade data from Finnhub with 180 req/min capacity across 3 API keys.
        <500ms response time, 50,000+ global securities, exchange-grade accuracy.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'MSFT')

        Returns:
            dict: Real-time quote with current price, open, high, low, volume, percentage change,
                  provider metadata, and data freshness timestamp

        Example:
            get_stock_quote('AAPL') -> {"provider": "finnhub", "data": {"c": 227.76, "h": 229.87, ...}}
        """
        logger.info(f"get_stock_quote called for symbol: {symbol}")

        async with aiohttp.ClientSession() as session:
            try:
                result = await multi_client.get_stock_quote(session, symbol)
                logger.info(f"Stock quote retrieved for {symbol}")
                return result
            except Exception as e:
                logger.error(f"Error getting stock quote for {symbol}: {e}")
                return {"error": str(e)}

    @mcp.tool()
    async def get_stock_fundamentals(symbol: str) -> dict:
        """Get comprehensive company fundamentals for investment research, valuation analysis, and due diligence.

        WHEN TO USE: Investment decisions, company analysis, financial metrics research, DCF modeling,
        sector comparisons, ESG analysis, credit assessment, business overview requests, competitive analysis.

        WHEN NOT TO USE: Intraday trading (use quotes), technical analysis (use indicators),
        options strategies (use options chain), market timing (use technical tools).

        Intelligent failover: FMP primary (250/day, 70K+ companies, 30yr history) → Finnhub backup.
        Professional-grade fundamental data used by institutional investors and analysts.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')

        Returns:
            dict: Comprehensive fundamentals including market cap, P/E ratio, revenue, ROE, debt ratios,
                  business description, industry classification, and key financial metrics

        Example:
            get_stock_fundamentals('AAPL') -> {"provider": "fmp", "data": {"marketCap": 3.5T, "peRatio": 28.5, ...}}
        """
        logger.info(f"get_stock_fundamentals called for symbol: {symbol}")

        async with aiohttp.ClientSession() as session:
            try:
                result = await multi_client.get_stock_fundamentals(session, symbol)
                logger.info(f"Stock fundamentals retrieved for {symbol}")
                return result
            except Exception as e:
                logger.error(f"Error getting stock fundamentals for {symbol}: {e}")
                return {"error": str(e)}
