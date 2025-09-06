#!/usr/bin/env python3

import logging
from typing import Any, Dict
import aiohttp

from .robinhood_historical import RobinhoodHistoricalProvider
from .providers import ProviderClient
from ..utils.config import ProviderType

logger = logging.getLogger(__name__)


class UnifiedHistoricalProvider:
    """Unified historical provider: Robinhood primary, Polygon S3 fallback"""
    
    def __init__(self):
        self.robinhood_provider = RobinhoodHistoricalProvider()
        self.fallback_provider = ProviderClient()
    
    async def get_historical_data(self, symbol: str, interval: str = "day", span: str = "year") -> Dict[str, Any]:
        """Get historical data with intelligent fallback"""
        
        # Try Robinhood first (unlimited, real-time API)
        try:
            logger.info(f"Attempting Robinhood historical for {symbol} ({interval}, {span})")
            result = await self.robinhood_provider.get_historical_data(symbol, interval, span)
            logger.info(f"Robinhood historical successful for {symbol}")
            return result
            
        except Exception as e:
            logger.warning(f"Robinhood historical failed for {symbol}: {e}, falling back to Polygon S3")
            
            # Fallback to Polygon S3 (static files)
            try:
                # Note: This is a simplified fallback - in practice you'd implement S3 access
                result = {
                    "provider": "polygon_s3_fallback",
                    "symbol": symbol,
                    "interval": interval,
                    "span": span,
                    "error": "Polygon S3 fallback not implemented in this demo",
                    "fallback_reason": str(e),
                    "note": "Would access pre-downloaded S3 files here"
                }
                
                logger.info(f"Polygon S3 fallback noted for {symbol}")
                return result
                
            except Exception as fallback_error:
                logger.error(f"All historical providers failed for {symbol}")
                return {
                    "error": "All historical providers failed",
                    "robinhood_error": str(e),
                    "polygon_error": str(fallback_error),
                    "symbol": symbol,
                    "interval": interval,
                    "span": span
                }
    
    async def get_intraday_data(self, symbol: str, interval: str = "5minute") -> Dict[str, Any]:
        """Get intraday data (5min, 10min, 30min)"""
        return await self.get_historical_data(symbol, interval=interval, span="day")
    
    async def get_daily_data(self, symbol: str, span: str = "year") -> Dict[str, Any]:
        """Get daily historical data"""
        return await self.get_historical_data(symbol, interval="day", span=span)
    
    async def get_weekly_data(self, symbol: str, span: str = "5year") -> Dict[str, Any]:
        """Get weekly historical data"""
        return await self.get_historical_data(symbol, interval="week", span=span)
    
    async def get_supported_intervals(self) -> Dict[str, Any]:
        """Get supported intervals and spans"""
        try:
            await self.robinhood_provider.ensure_authenticated()
            return {
                "provider": "robinhood",
                "supported": self.robinhood_provider.get_supported_intervals()
            }
        except Exception as e:
            return {
                "provider": "fallback",
                "error": str(e),
                "supported": {
                    "intervals": ["day"],
                    "spans": ["year"],
                    "note": "Limited fallback support"
                }
            }
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all historical providers"""
        status = {
            "robinhood": {"available": False, "error": None},
            "polygon_s3": {"available": False, "error": None}
        }
        
        # Test Robinhood
        try:
            await self.robinhood_provider.ensure_authenticated()
            status["robinhood"]["available"] = True
        except Exception as e:
            status["robinhood"]["error"] = str(e)
        
        # Polygon S3 is always "available" (static files)
        status["polygon_s3"]["available"] = True
        status["polygon_s3"]["note"] = "Static file fallback"
        
        return status
