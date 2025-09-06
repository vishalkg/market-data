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
    async def get_multiple_stock_quotes(symbols: str) -> dict:
        """Get multiple stock quotes in single request for portfolio analysis and batch processing.

        WHEN TO USE: Portfolio monitoring, watchlist updates, multi-symbol analysis, batch price checks,
        correlation analysis, sector screening, algorithmic trading inputs, dashboard updates.

        WHEN NOT TO USE: Single symbol requests (use get_stock_quote), historical analysis,
        fundamental research, technical analysis.

        Robinhood batch processing: 10+ symbols in single API call vs individual requests.
        Unlimited rate limits, real-time data, significant performance improvement for multi-symbol analysis.

        Args:
            symbols: Comma-separated stock symbols (e.g., 'AAPL,TSLA,MSFT,GOOGL')

        Returns:
            dict: Batch quote results with individual symbol data, performance metrics,
                  provider attribution, and batch processing statistics

        Example:
            get_multiple_stock_quotes('AAPL,TSLA,MSFT') -> {
                "provider": "robinhood", "data": {"AAPL": {...}, "TSLA": {...}}, "batch_size": 3
            }
        """
        logger.info(f"get_multiple_stock_quotes called for symbols: {symbols}")

        # Parse comma-separated symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        
        if not symbol_list:
            return {"error": "No valid symbols provided"}

        try:
            result = await multi_client.unified_stock_provider.get_multiple_quotes(symbol_list)
            logger.info(f"Batch quotes retrieved for {len(symbol_list)} symbols")
            return result
        except Exception as e:
            logger.error(f"Error getting batch quotes for {symbols}: {e}")
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
                result = await multi_client.get_fundamentals(session, symbol)
                logger.info(f"Stock fundamentals retrieved for {symbol}")
                return result
            except Exception as e:
                logger.error(f"Error getting stock fundamentals for {symbol}: {e}")
                return {"error": str(e)}

    @mcp.tool()
    async def get_enhanced_fundamentals(symbol: str, include_earnings: bool = True, include_ratings: bool = True) -> dict:
        """Get enhanced company fundamentals with earnings history and analyst ratings from Robinhood.

        WHEN TO USE: Deep fundamental analysis, earnings trend analysis, analyst sentiment research,
        investment thesis development, comprehensive company research, institutional-grade analysis.

        WHEN NOT TO USE: Quick price checks (use quotes), technical analysis (use indicators),
        basic company info (use get_stock_fundamentals), options analysis (use options chain).

        Robinhood exclusive: Unlimited access to earnings history, analyst ratings, and comprehensive
        fundamental metrics. Professional-grade data used by institutional investors and research analysts.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            include_earnings: Include detailed earnings history (default: True)
            include_ratings: Include analyst ratings and price targets (default: True)

        Returns:
            dict: Enhanced fundamentals with earnings history, analyst ratings, market metrics,
                  business description, financial ratios, and comprehensive company analysis

        Example:
            get_enhanced_fundamentals('AAPL', include_earnings=True, include_ratings=True) -> {
                "provider": "robinhood", "data": {"fundamentals": {...}, "earnings": [...], "analyst_ratings": {...}}
            }
        """
        logger.info(f"get_enhanced_fundamentals called for {symbol} (earnings={include_earnings}, ratings={include_ratings})")

        try:
            result = await multi_client.unified_fundamentals_provider.get_enhanced_fundamentals(
                symbol, include_earnings, include_ratings
            )
            logger.info(f"Enhanced fundamentals retrieved for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error getting enhanced fundamentals for {symbol}: {e}")
            return {"error": str(e)}
