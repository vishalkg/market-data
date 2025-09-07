#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, List, Optional
import aiohttp

from .base_provider import BaseProvider, ProviderCapability
from ..utils.api_keys import APIKeyManager, ProviderType

logger = logging.getLogger(__name__)


class FinnhubProvider(BaseProvider):
    """Finnhub provider with rate limiting and free tier restrictions"""
    
    def __init__(self):
        self.key_manager = APIKeyManager()
        self.base_url = "https://finnhub.io/api/v1"
        self.free_endpoints = ["quote", "company-profile2", "stock/candle"]
    
    @property
    def name(self) -> str:
        return "finnhub"
    
    def get_capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.REAL_TIME_QUOTES,
            ProviderCapability.FUNDAMENTALS,
            ProviderCapability.HISTORICAL_DATA,
            ProviderCapability.RATE_LIMITED
        ]
    
    async def health_check(self) -> bool:
        """Check if Finnhub API is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                result = await self._make_request(session, "quote", {"symbol": "AAPL"})
                return "data" in result and not "error" in result
        except Exception:
            return False
    
    def _validate_endpoint_access(self, endpoint: str) -> bool:
        """Check if endpoint is available for free tier"""
        return any(endpoint.startswith(free_ep) for free_ep in self.free_endpoints)
    
    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Make HTTP request to Finnhub API"""
        if params is None:
            params = {}

        # Validate endpoint access for free tier
        if not self._validate_endpoint_access(endpoint):
            return {
                "error": f"Endpoint '{endpoint}' requires premium subscription",
                "details": "This endpoint is not available on the free tier",
            }

        key = self.key_manager.get_available_key(ProviderType.FINNHUB)
        if not key:
            return {"error": "No available API keys for Finnhub"}

        # Add API key to params
        params["token"] = key.key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(max_retries):
            try:
                self.key_manager.update_key_usage(key)
                logger.info(f"Making Finnhub request: {url}")

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return {"data": data}
                        except Exception:
                            text_data = await response.text()
                            try:
                                import json
                                data = json.loads(text_data)
                                return {"data": data}
                            except json.JSONDecodeError:
                                return {"error": "API returned non-JSON response"}
                    
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.error(f"401 Unauthorized from Finnhub: {error_text}")
                        
                        # Try next key if available
                        next_key = self.key_manager.get_next_available_key(
                            ProviderType.FINNHUB, key.key
                        )
                        if next_key and attempt < max_retries - 1:
                            key = next_key
                            params["token"] = key.key
                            continue

                        return {
                            "error": "Invalid API key or insufficient permissions",
                            "details": error_text,
                        }
                    
                    elif response.status == 429:
                        logger.warning(f"Rate limited on Finnhub, attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2**attempt)
                            continue
                    
                    else:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}", "details": error_text}

            except Exception as e:
                logger.error(f"Finnhub request failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                return {"error": str(e)}

        return {"error": "Max retries exceeded"}
    
    # Stock data methods
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote from Finnhub"""
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, "quote", {"symbol": symbol})
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"],
                    "rate_limit": "180_per_minute"
                }
            return result
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get multiple quotes (individual requests - no batch support)"""
        async with aiohttp.ClientSession() as session:
            results = {}
            errors = {}
            
            for symbol in symbols:
                try:
                    result = await self._make_request(session, "quote", {"symbol": symbol})
                    if "data" in result:
                        results[symbol] = result["data"]
                    else:
                        errors[symbol] = result.get("error", "Unknown error")
                except Exception as e:
                    errors[symbol] = str(e)
            
            return {
                "data": results,
                "errors": errors,
                "batch_size": len(symbols),
                "rate_limit": "180_per_minute"
            }
    
    # Options data methods
    async def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """Get options chain from Finnhub"""
        params = {"symbol": symbol}
        if expiration_date:
            params["expiration"] = expiration_date
        
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, "stock/option-chain", params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"]
                }
            return result
    
    # Fundamentals data methods
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get company profile from Finnhub"""
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, "stock/profile2", {"symbol": symbol})
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"]
                }
            return result
    
    # Historical data methods
    async def get_historical_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get historical candle data from Finnhub"""
        # Map period to timestamps
        import time
        from datetime import datetime, timedelta
        
        end_time = int(time.time())
        
        period_map = {
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1),
            "1m": timedelta(days=30),
            "3m": timedelta(days=90),
            "1y": timedelta(days=365),
            "5y": timedelta(days=1825)
        }
        
        delta = period_map.get(period, timedelta(days=365))
        start_time = int((datetime.now() - delta).timestamp())
        
        params = {
            "symbol": symbol,
            "resolution": "D",  # Daily resolution
            "from": start_time,
            "to": end_time
        }
        
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, "stock/candle", params)
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"],
                    "period": period
                }
            return result
    
    # Technical indicators - Not supported by Finnhub directly
    async def get_rsi(self, symbol: str, period: int = 14) -> Dict[str, Any]:
        """RSI not supported by Finnhub"""
        raise NotImplementedError("RSI not available from Finnhub")
    
    async def get_macd(self, symbol: str) -> Dict[str, Any]:
        """MACD not supported by Finnhub"""
        raise NotImplementedError("MACD not available from Finnhub")
    
    async def get_bollinger_bands(self, symbol: str, period: int = 20) -> Dict[str, Any]:
        """Bollinger Bands not supported by Finnhub"""
        raise NotImplementedError("Bollinger Bands not available from Finnhub")
