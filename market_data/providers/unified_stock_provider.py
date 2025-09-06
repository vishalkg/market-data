#!/usr/bin/env python3

import logging
from typing import Any, Dict, List
import aiohttp

from .robinhood_stocks import RobinhoodStockProvider
from .providers import ProviderClient
from ..utils.config import ProviderType

logger = logging.getLogger(__name__)


class UnifiedStockProvider:
    """Unified stock provider: Robinhood primary, Finnhub fallback"""
    
    def __init__(self):
        self.robinhood_provider = RobinhoodStockProvider()
        self.finnhub_provider = ProviderClient()
    
    async def get_stock_quote(self, session: aiohttp.ClientSession, symbol: str) -> Dict[str, Any]:
        """Get stock quote with intelligent fallback"""
        
        # Try Robinhood first (unlimited)
        try:
            logger.info(f"Attempting Robinhood quote for {symbol}")
            result = await self.robinhood_provider.get_stock_quote(symbol)
            logger.info(f"Robinhood quote successful for {symbol}")
            return result
            
        except Exception as e:
            logger.warning(f"Robinhood quote failed for {symbol}: {e}, falling back to Finnhub")
            
            # Fallback to Finnhub (rate limited)
            try:
                result = await self.finnhub_provider.make_request(
                    session, ProviderType.FINNHUB, "quote", {"symbol": symbol}
                )
                
                # Add fallback metadata
                if isinstance(result, dict) and "data" in result:
                    result["provider"] = "finnhub_fallback"
                    result["fallback_reason"] = str(e)
                
                logger.info(f"Finnhub fallback successful for {symbol}")
                return result
                
            except Exception as fallback_error:
                logger.error(f"All providers failed for {symbol}. Robinhood: {e}, Finnhub: {fallback_error}")
                return {
                    "error": f"All providers failed",
                    "robinhood_error": str(e),
                    "finnhub_error": str(fallback_error),
                    "symbol": symbol
                }
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get multiple quotes with batch optimization"""
        
        # Try Robinhood batch request first
        try:
            logger.info(f"Attempting Robinhood batch quotes for {len(symbols)} symbols")
            result = await self.robinhood_provider.get_multiple_quotes(symbols)
            logger.info(f"Robinhood batch quotes successful for {len(symbols)} symbols")
            return result
            
        except Exception as e:
            logger.warning(f"Robinhood batch failed: {e}, falling back to individual Finnhub calls")
            
            # Fallback to individual Finnhub calls
            async with aiohttp.ClientSession() as session:
                results = {}
                errors = {}
                
                for symbol in symbols:
                    try:
                        result = await self.finnhub_provider.make_request(
                            session, ProviderType.FINNHUB, "quote", {"symbol": symbol}
                        )
                        if isinstance(result, dict) and "data" in result:
                            results[symbol] = result["data"]
                    except Exception as symbol_error:
                        errors[symbol] = str(symbol_error)
                
                return {
                    "provider": "finnhub_fallback",
                    "data": results,
                    "errors": errors,
                    "fallback_reason": str(e),
                    "batch_size": len(symbols)
                }
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all stock quote providers"""
        status = {
            "robinhood": {"available": False, "error": None},
            "finnhub": {"available": False, "error": None}
        }
        
        # Test Robinhood
        try:
            await self.robinhood_provider.ensure_authenticated()
            status["robinhood"]["available"] = True
        except Exception as e:
            status["robinhood"]["error"] = str(e)
        
        # Test Finnhub (simple check)
        try:
            async with aiohttp.ClientSession() as session:
                await self.finnhub_provider.make_request(
                    session, ProviderType.FINNHUB, "quote", {"symbol": "AAPL"}
                )
            status["finnhub"]["available"] = True
        except Exception as e:
            status["finnhub"]["error"] = str(e)
        
        return status
