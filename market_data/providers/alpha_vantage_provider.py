#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, List, Optional
import aiohttp

from .base_provider import BaseProvider, ProviderCapability
from ..utils.api_keys import APIKeyManager, ProviderType

logger = logging.getLogger(__name__)


class AlphaVantageProvider(BaseProvider):
    """Alpha Vantage provider specialized for technical indicators"""
    
    def __init__(self):
        self.key_manager = APIKeyManager()
        self.base_url = "https://www.alphavantage.co/query"
    
    @property
    def name(self) -> str:
        return "alpha_vantage"
    
    def get_capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.TECHNICAL_INDICATORS,
            ProviderCapability.HISTORICAL_DATA,
            ProviderCapability.RATE_LIMITED
        ]
    
    async def health_check(self) -> bool:
        """Check if Alpha Vantage API is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                result = await self._make_request(session, {
                    "function": "TIME_SERIES_INTRADAY",
                    "symbol": "AAPL",
                    "interval": "1min"
                })
                return "data" in result and not "error" in result
        except Exception:
            return False
    
    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        params: Dict[str, Any],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Make HTTP request to Alpha Vantage API"""
        key = self.key_manager.get_available_key(ProviderType.ALPHA_VANTAGE)
        if not key:
            return {"error": "No available API keys for Alpha Vantage"}

        # Add API key to params
        params["apikey"] = key.key

        for attempt in range(max_retries):
            try:
                self.key_manager.update_key_usage(key)
                logger.info(f"Making Alpha Vantage request: {params.get('function', 'unknown')}")

                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return {"data": data}
                        except Exception:
                            return {"error": "API returned non-JSON response"}
                    
                    elif response.status == 429:
                        logger.warning(f"Rate limited on Alpha Vantage, attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2**attempt)
                            continue
                    
                    else:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}", "details": error_text}

            except Exception as e:
                logger.error(f"Alpha Vantage request failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                return {"error": str(e)}

        return {"error": "Max retries exceeded"}
    
    # Stock data methods - Limited support
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote from Alpha Vantage (limited)"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        }
        
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"]
                }
            return result
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get multiple quotes (individual requests)"""
        async with aiohttp.ClientSession() as session:
            results = {}
            errors = {}
            
            for symbol in symbols:
                try:
                    result = await self.get_stock_quote(symbol)
                    if "data" in result:
                        results[symbol] = result["data"]
                    else:
                        errors[symbol] = result.get("error", "Unknown error")
                except Exception as e:
                    errors[symbol] = str(e)
            
            return {
                "data": results,
                "errors": errors,
                "batch_size": len(symbols)
            }
    
    # Options data methods - Not supported
    async def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """Options chain not supported by Alpha Vantage"""
        raise NotImplementedError("Options chain not available from Alpha Vantage")
    
    # Fundamentals data methods - Limited support
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get company overview from Alpha Vantage"""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol
        }
        
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"]
                }
            return result
    
    # Historical data methods
    async def get_historical_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get historical data from Alpha Vantage"""
        # Use daily time series for historical data
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "full" if period in ["1y", "5y"] else "compact"
        }
        
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"],
                    "period": period
                }
            return result
    
    # Technical indicators methods - Primary strength
    async def get_rsi(self, symbol: str, period: int = 14) -> Dict[str, Any]:
        """Get RSI from Alpha Vantage"""
        params = {
            "function": "RSI",
            "symbol": symbol,
            "interval": "daily",
            "time_period": period,
            "series_type": "close",
        }

        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "indicator": "RSI",
                    "period": period,
                    "data": result["data"]
                }
            return result
    
    async def get_macd(self, symbol: str) -> Dict[str, Any]:
        """Get MACD from Alpha Vantage"""
        params = {
            "function": "MACD",
            "symbol": symbol,
            "interval": "daily",
            "series_type": "close",
        }

        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "indicator": "MACD",
                    "data": result["data"]
                }
            return result
    
    async def get_bollinger_bands(self, symbol: str, period: int = 20) -> Dict[str, Any]:
        """Get Bollinger Bands from Alpha Vantage"""
        params = {
            "function": "BBANDS",
            "symbol": symbol,
            "interval": "daily",
            "time_period": period,
            "series_type": "close",
        }

        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "indicator": "BBANDS",
                    "period": period,
                    "data": result["data"]
                }
            return result
