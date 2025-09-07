#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, List, Optional
import aiohttp

from .base_provider import BaseProvider, ProviderCapability
from ..utils.api_keys import APIKeyManager, ProviderType

logger = logging.getLogger(__name__)


class FMPProvider(BaseProvider):
    """Financial Modeling Prep provider specialized for fundamentals"""
    
    def __init__(self):
        self.key_manager = APIKeyManager()
        self.base_url = "https://financialmodelingprep.com/api/v3"
    
    @property
    def name(self) -> str:
        return "fmp"
    
    def get_capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.FUNDAMENTALS,
            ProviderCapability.REAL_TIME_QUOTES,
            ProviderCapability.HISTORICAL_DATA,
            ProviderCapability.RATE_LIMITED
        ]
    
    async def health_check(self) -> bool:
        """Check if FMP API is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                result = await self._make_request(session, "quote/AAPL")
                return "data" in result and not "error" in result
        except Exception:
            return False
    
    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Make HTTP request to FMP API"""
        if params is None:
            params = {}
            
        key = self.key_manager.get_available_key(ProviderType.FMP)
        if not key:
            return {"error": "No available API keys for FMP"}

        # Add API key to params
        params["apikey"] = key.key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(max_retries):
            try:
                self.key_manager.update_key_usage(key)
                logger.info(f"Making FMP request: {endpoint}")

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return {"data": data}
                        except Exception:
                            return {"error": "API returned non-JSON response"}
                    
                    elif response.status == 429:
                        logger.warning(f"Rate limited on FMP, attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2**attempt)
                            continue
                    
                    else:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}", "details": error_text}

            except Exception as e:
                logger.error(f"FMP request failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                return {"error": str(e)}

        return {"error": "Max retries exceeded"}
    
    # Stock data methods
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote from FMP"""
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, f"quote/{symbol}")
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"]
                }
            return result
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get multiple quotes from FMP"""
        symbol_list = ",".join(symbols)
        
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, f"quote/{symbol_list}")
            
            if "data" in result:
                # Convert list response to dict keyed by symbol
                data_dict = {}
                if isinstance(result["data"], list):
                    for item in result["data"]:
                        if "symbol" in item:
                            data_dict[item["symbol"]] = item
                
                return {
                    "data": data_dict,
                    "batch_size": len(symbols)
                }
            return result
    
    # Options data methods - Not supported
    async def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """Options chain not supported by FMP"""
        raise NotImplementedError("Options chain not available from FMP")
    
    # Fundamentals data methods - Primary strength
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive fundamentals from FMP"""
        async with aiohttp.ClientSession() as session:
            # Get company profile
            profile_result = await self._make_request(session, f"profile/{symbol}")
            
            if "error" in profile_result:
                return profile_result
            
            # Get key metrics
            metrics_result = await self._make_request(session, f"key-metrics/{symbol}")
            
            # Combine results
            fundamentals_data = {
                "profile": profile_result.get("data", []),
                "metrics": metrics_result.get("data", []) if "data" in metrics_result else []
            }
            
            return {
                "symbol": symbol,
                "data": fundamentals_data
            }
    
    # Historical data methods
    async def get_historical_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get historical data from FMP"""
        # Map period to FMP format
        period_map = {
            "1d": "1day",
            "1w": "1week", 
            "1m": "1month",
            "3m": "3month",
            "1y": "1year",
            "5y": "5year"
        }
        
        # Use daily historical prices
        async with aiohttp.ClientSession() as session:
            result = await self._make_request(session, f"historical-price-full/{symbol}")
            
            if "data" in result:
                return {
                    "symbol": symbol,
                    "data": result["data"],
                    "period": period
                }
            return result
    
    # Technical indicators - Not supported
    async def get_rsi(self, symbol: str, period: int = 14) -> Dict[str, Any]:
        """RSI not supported by FMP"""
        raise NotImplementedError("RSI not available from FMP")
    
    async def get_macd(self, symbol: str) -> Dict[str, Any]:
        """MACD not supported by FMP"""
        raise NotImplementedError("MACD not available from FMP")
    
    async def get_bollinger_bands(self, symbol: str, period: int = 20) -> Dict[str, Any]:
        """Bollinger Bands not supported by FMP"""
        raise NotImplementedError("Bollinger Bands not available from FMP")
