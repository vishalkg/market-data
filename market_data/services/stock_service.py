#!/usr/bin/env python3

import logging
from typing import Any, Dict, List

from ..providers.provider_factory import ProviderFactory
from ..providers.provider_chain import ProviderChain
from ..providers.base_provider import ProviderCapability
from ..utils.errors import (
    ErrorType,
    create_error_response,
    create_success_response
)

logger = logging.getLogger(__name__)


class StockService:
    """Clean stock data aggregation service using provider chains"""
    
    def __init__(self):
        # Register providers
        self._register_providers()
        
        # Create provider chain: Robinhood primary, Finnhub fallback
        self.quote_chain = ProviderChain([
            ProviderFactory.get_provider("robinhood"),
            ProviderFactory.get_provider("finnhub")
        ])
    
    def _register_providers(self):
        """Register all stock-capable providers"""
        from ..providers.robinhood_provider import RobinhoodProvider
        from ..providers.finnhub_provider import FinnhubProvider
        
        ProviderFactory.register_provider("robinhood", RobinhoodProvider)
        ProviderFactory.register_provider("finnhub", FinnhubProvider)
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote with intelligent fallback"""
        logger.info(f"Getting stock quote for {symbol}")
        
        try:
            result = await self.quote_chain.execute_with_capability_filter(
                "get_stock_quote",
                ProviderCapability.REAL_TIME_QUOTES,
                symbol
            )
            
            # Check if result is an error
            if isinstance(result, dict) and result.get("error"):
                return result  # Already formatted error
            
            logger.info(f"Stock quote completed for {symbol} via {result.get('provider', 'unknown')}")
            return create_success_response(
                data=result.get("data", result),
                metadata={
                    "symbol": symbol,
                    "provider": result.get("provider"),
                    "timestamp": result.get("timestamp")
                }
            )
        except Exception as e:
            logger.error(f"Stock quote failed for {symbol}: {e}")
            return create_error_response(
                ErrorType.INTERNAL_ERROR,
                f"Failed to get stock quote for {symbol}",
                details={"symbol": symbol, "error": str(e)}
            )
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get multiple stock quotes with batch optimization"""
        logger.info(f"Getting batch quotes for {len(symbols)} symbols")
        
        # Try batch-capable providers first
        result = await self.quote_chain.execute_with_capability_filter(
            "get_multiple_quotes",
            ProviderCapability.BATCH_QUOTES,
            symbols
        )
        
        # If no batch-capable providers, fall back to individual quotes
        if "error" in result and "No providers support capability" in result["error"]:
            logger.info("No batch providers available, falling back to individual quotes")
            
            individual_results = {}
            errors = {}
            
            for symbol in symbols:
                try:
                    quote_result = await self.get_stock_quote(symbol)
                    if "data" in quote_result:
                        individual_results[symbol] = quote_result["data"]
                    else:
                        errors[symbol] = quote_result.get("error", "Unknown error")
                except Exception as e:
                    errors[symbol] = str(e)
            
            return {
                "data": individual_results,
                "errors": errors,
                "batch_size": len(symbols),
                "method": "individual_fallback"
            }
        
        logger.info(f"Batch quotes completed for {len(symbols)} symbols via {result.get('provider', 'unknown')}")
        return result
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all stock quote providers"""
        return await self.quote_chain.get_chain_status()
    
    def reorder_providers(self, priority_order: List[str]) -> None:
        """Reorder providers by priority"""
        self.quote_chain.reorder_by_priority(priority_order)
        logger.info(f"Reordered stock providers: {priority_order}")
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all providers in the chain"""
        capabilities = {}
        for provider in self.quote_chain.providers:
            capabilities[provider.name] = [cap.value for cap in provider.get_capabilities()]
        return capabilities
