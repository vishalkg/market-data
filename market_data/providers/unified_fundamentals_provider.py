#!/usr/bin/env python3

import logging
from typing import Any, Dict
import aiohttp

from .robinhood_fundamentals import RobinhoodFundamentalsProvider
from .providers import ProviderClient
from ..utils.config import ProviderType

logger = logging.getLogger(__name__)


class UnifiedFundamentalsProvider:
    """Unified fundamentals provider: Robinhood primary, FMP → Finnhub fallback"""
    
    def __init__(self):
        self.robinhood_provider = RobinhoodFundamentalsProvider()
        self.fallback_provider = ProviderClient()
    
    async def get_fundamentals(self, session: aiohttp.ClientSession, symbol: str) -> Dict[str, Any]:
        """Get fundamentals with intelligent fallback"""
        
        # Try Robinhood first (unlimited)
        try:
            logger.info(f"Attempting Robinhood fundamentals for {symbol}")
            result = await self.robinhood_provider.get_fundamentals(symbol)
            logger.info(f"Robinhood fundamentals successful for {symbol}")
            return result
            
        except Exception as e:
            logger.warning(f"Robinhood fundamentals failed for {symbol}: {e}, falling back to FMP")
            
            # Fallback to FMP (rate limited)
            try:
                result = await self.fallback_provider.make_request(
                    session, ProviderType.FMP, f"profile/{symbol}", {}
                )
                
                # Add fallback metadata
                if isinstance(result, dict) and "data" in result:
                    result["provider"] = "fmp_fallback"
                    result["fallback_reason"] = str(e)
                
                logger.info(f"FMP fallback successful for {symbol}")
                return result
                
            except Exception as fmp_error:
                logger.warning(f"FMP fallback failed for {symbol}: {fmp_error}, trying Finnhub")
                
                # Final fallback to Finnhub
                try:
                    result = await self.fallback_provider.make_request(
                        session, ProviderType.FINNHUB, "stock/profile2", {"symbol": symbol}
                    )
                    
                    if isinstance(result, dict) and "data" in result:
                        result["provider"] = "finnhub_fallback"
                        result["fallback_reason"] = f"Robinhood: {e}, FMP: {fmp_error}"
                    
                    logger.info(f"Finnhub fallback successful for {symbol}")
                    return result
                    
                except Exception as finnhub_error:
                    logger.error(f"All fundamentals providers failed for {symbol}")
                    return {
                        "error": "All fundamentals providers failed",
                        "robinhood_error": str(e),
                        "fmp_error": str(fmp_error),
                        "finnhub_error": str(finnhub_error),
                        "symbol": symbol
                    }
    
    async def get_enhanced_fundamentals(self, symbol: str, include_earnings: bool = True, include_ratings: bool = True) -> Dict[str, Any]:
        """Get enhanced fundamentals with earnings and ratings (Robinhood only)"""
        
        try:
            logger.info(f"Getting enhanced fundamentals for {symbol} (earnings={include_earnings}, ratings={include_ratings})")
            
            # Get base fundamentals
            base_result = await self.robinhood_provider.get_fundamentals(symbol)
            
            # Optionally add detailed earnings
            if include_earnings:
                try:
                    earnings_result = await self.robinhood_provider.get_earnings_data(symbol)
                    base_result["data"]["detailed_earnings"] = earnings_result["data"]["earnings"]
                except Exception as e:
                    logger.warning(f"Could not get detailed earnings for {symbol}: {e}")
            
            # Optionally add detailed ratings
            if include_ratings:
                try:
                    ratings_result = await self.robinhood_provider.get_analyst_ratings(symbol)
                    base_result["data"]["detailed_ratings"] = ratings_result["data"]["ratings"]
                except Exception as e:
                    logger.warning(f"Could not get detailed ratings for {symbol}: {e}")
            
            base_result["enhanced"] = True
            return base_result
            
        except Exception as e:
            logger.error(f"Enhanced fundamentals failed for {symbol}: {e}")
            return {
                "error": f"Enhanced fundamentals failed: {e}",
                "symbol": symbol,
                "note": "Enhanced fundamentals require Robinhood authentication"
            }
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all fundamentals providers"""
        status = {
            "robinhood": {"available": False, "error": None},
            "fmp": {"available": False, "error": None},
            "finnhub": {"available": False, "error": None}
        }
        
        # Test Robinhood
        try:
            await self.robinhood_provider.ensure_authenticated()
            status["robinhood"]["available"] = True
        except Exception as e:
            status["robinhood"]["error"] = str(e)
        
        # Test FMP and Finnhub (simple checks)
        try:
            async with aiohttp.ClientSession() as session:
                await self.fallback_provider.make_request(
                    session, ProviderType.FMP, "profile/AAPL", {}
                )
            status["fmp"]["available"] = True
        except Exception as e:
            status["fmp"]["error"] = str(e)
        
        try:
            async with aiohttp.ClientSession() as session:
                await self.fallback_provider.make_request(
                    session, ProviderType.FINNHUB, "stock/profile2", {"symbol": "AAPL"}
                )
            status["finnhub"]["available"] = True
        except Exception as e:
            status["finnhub"]["error"] = str(e)
        
        return status
