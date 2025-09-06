#!/usr/bin/env python3

import logging
from typing import Any, Dict, Optional

import aiohttp

from ..utils.api_keys import ProviderType
from ..utils.data_optimizers import DataOptimizer
from .providers import ProviderClient
from .unified_stock_provider import UnifiedStockProvider
from .unified_fundamentals_provider import UnifiedFundamentalsProvider
from .unified_historical_provider import UnifiedHistoricalProvider

logger = logging.getLogger(__name__)


class MultiProviderClient(ProviderClient):
    def __init__(self):
        super().__init__()
        self.optimizer = DataOptimizer()
        self.unified_stock_provider = UnifiedStockProvider()
        self.unified_fundamentals_provider = UnifiedFundamentalsProvider()
        self.unified_historical_provider = UnifiedHistoricalProvider()

    async def get_quote(
        self, session: aiohttp.ClientSession, symbol: str
    ) -> Dict[str, Any]:
        """Get real-time stock quote: Robinhood primary, Finnhub fallback"""
        return await self.unified_stock_provider.get_stock_quote(session, symbol)

    async def get_options_chain(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        expiration_date: Optional[str] = None,
        max_expirations: int = 10,
    ) -> Dict[str, Any]:
        """Get options chain from Finnhub with Robinhood failover"""
        params = {"symbol": symbol}
        if expiration_date:
            params["expiration"] = expiration_date

        # Try Finnhub first
        result = await self.make_request(
            session, ProviderType.FINNHUB, "stock/option-chain", params
        )

        # If Finnhub fails, fallback to Robinhood
        if "error" in result:
            logger.info(f"Finnhub failed for {symbol}, trying Robinhood fallback")
            try:
                import robin_stocks.robinhood as rh

                # Get options data from Robinhood
                options_data = rh.options.get_chains(symbol)

                if options_data:
                    return {
                        "provider": "robinhood",
                        "data": {
                            "symbol": symbol,
                            "options": options_data,
                            "note": "Data from Robinhood (comprehensive options data)",
                        },
                    }
                else:
                    return {
                        "error": "No options data available from Robinhood",
                        "provider": "robinhood",
                    }

            except Exception as e:
                logger.error(f"Robinhood fallback failed: {e}")
                return {
                    "error": f"Both Finnhub and Robinhood failed. Finnhub: {result.get('error', 'Unknown error')}, Robinhood: {str(e)}",
                    "provider": "failover_exhausted",
                }

        # Optimize Finnhub data if successful
        if "data" in result:
            return self.optimizer.optimize_options_data(result, max_expirations)
        return result

    async def get_fundamentals(
        self, session: aiohttp.ClientSession, symbol: str
    ) -> Dict[str, Any]:
        """Get company fundamentals: Robinhood primary, FMP → Finnhub fallback"""
        return await self.unified_fundamentals_provider.get_fundamentals(session, symbol)

    async def get_rsi(
        self, session: aiohttp.ClientSession, symbol: str, period: int = 14
    ) -> Dict[str, Any]:
        """Get RSI from Alpha Vantage with optimization"""
        params = {
            "function": "RSI",
            "symbol": symbol,
            "interval": "daily",
            "time_period": period,
            "series_type": "close",
        }

        result = await self.make_request(
            session, ProviderType.ALPHA_VANTAGE, "", params
        )

        if "data" in result:
            return self.optimizer.optimize_rsi_data(result, symbol, period)
        return result

    async def get_macd(
        self, session: aiohttp.ClientSession, symbol: str
    ) -> Dict[str, Any]:
        """Get MACD from Alpha Vantage with optimization"""
        params = {
            "function": "MACD",
            "symbol": symbol,
            "interval": "daily",
            "series_type": "close",
        }

        result = await self.make_request(
            session, ProviderType.ALPHA_VANTAGE, "", params
        )

        if "data" in result:
            return self.optimizer.optimize_macd_data(result, symbol)
        return result

    async def get_bollinger_bands(
        self, session: aiohttp.ClientSession, symbol: str, period: int = 20
    ) -> Dict[str, Any]:
        """Get Bollinger Bands from Alpha Vantage with optimization"""
        params = {
            "function": "BBANDS",
            "symbol": symbol,
            "interval": "daily",
            "time_period": period,
            "series_type": "close",
        }

        result = await self.make_request(
            session, ProviderType.ALPHA_VANTAGE, "", params
        )

        if "data" in result:
            return self.optimizer.optimize_bollinger_data(result, symbol, period)
        return result

    async def get_market_status(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Get market status from Finnhub"""
        return await self.make_request(
            session, ProviderType.FINNHUB, "stock/market-status", {"exchange": "US"}
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self.key_manager.get_usage_stats()
