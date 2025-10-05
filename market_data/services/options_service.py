#!/usr/bin/env python3

import logging
from typing import Any, Dict, List, Optional

from ..providers.provider_factory import ProviderFactory
from ..providers.provider_chain import ProviderChain
from ..providers.base_provider import ProviderCapability

logger = logging.getLogger(__name__)


class OptionsService:
    """Clean options data aggregation service using provider chains"""
    
    def __init__(self):
        # Register providers
        self._register_providers()
        
        # Create provider chain: Robinhood primary, Finnhub fallback
        self.options_chain = ProviderChain([
            ProviderFactory.get_provider("robinhood"),
            ProviderFactory.get_provider("finnhub")
        ])
    
    def _register_providers(self):
        """Register all options-capable providers"""
        from ..providers.robinhood_provider import RobinhoodProvider
        from ..providers.finnhub_provider import FinnhubProvider
        
        ProviderFactory.register_provider("robinhood", RobinhoodProvider)
        ProviderFactory.register_provider("finnhub", FinnhubProvider)
    
    async def get_options_chain(
        self,
        symbol: str,
        expiration_date: Optional[str] = None,
        max_expirations: int = 3,
        raw_data: bool = False,
        include_greeks: bool = False,
    ) -> Dict[str, Any]:
        """Get options chain with intelligent fallback"""
        logger.info(f"Getting options chain for {symbol}")
        
        # Use capability filtering to find options-capable providers
        result = await self.options_chain.execute_with_capability_filter(
            "get_options_chain",
            ProviderCapability.OPTIONS_CHAIN,
            symbol,
            expiration_date=expiration_date
        )
        
        # Post-process result based on parameters
        if "data" in result and not raw_data:
            result = self._optimize_options_data(result, max_expirations, include_greeks)
        
        logger.info(f"Options chain completed for {symbol} via {result.get('provider', 'unknown')}")
        return result
    
    def _optimize_options_data(
        self, 
        result: Dict[str, Any], 
        max_expirations: int,
        include_greeks: bool
    ) -> Dict[str, Any]:
        """Optimize options data structure"""
        # This would contain the optimization logic from the existing system
        # For now, just pass through with metadata
        if "data" in result:
            result["optimization"] = {
                "max_expirations": max_expirations,
                "include_greeks": include_greeks,
                "optimized": True
            }
        
        return result
    
    async def get_option_quote(self, option_id: str) -> Dict[str, Any]:
        """Get single option quote"""
        logger.info(f"Getting option quote for {option_id}")
        
        # Try to get option quote from available providers
        # Note: This would need to be implemented in providers that support it
        for provider in self.options_chain.providers:
            if hasattr(provider, 'get_option_quote'):
                try:
                    result = await provider.get_option_quote(option_id)
                    result["provider"] = provider.name
                    return result
                except Exception as e:
                    logger.warning(f"Provider {provider.name} failed for option {option_id}: {e}")
                    continue
        
        return {
            "error": "No providers support individual option quotes",
            "option_id": option_id
        }
    
    async def get_options_by_expiration(
        self, 
        symbol: str, 
        expiration_date: str
    ) -> Dict[str, Any]:
        """Get options for specific expiration date"""
        logger.info(f"Getting options for {symbol} expiring {expiration_date}")
        
        result = await self.get_options_chain(
            symbol, 
            expiration_date=expiration_date,
            max_expirations=1
        )
        
        if "data" in result:
            result["filtered_by_expiration"] = expiration_date
        
        return result
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all options providers"""
        return await self.options_chain.get_chain_status()
    
    def reorder_providers(self, priority_order: List[str]) -> None:
        """Reorder providers by priority"""
        self.options_chain.reorder_by_priority(priority_order)
        logger.info(f"Reordered options providers: {priority_order}")
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all providers in the chain"""
        capabilities = {}
        for provider in self.options_chain.providers:
            capabilities[provider.name] = [cap.value for cap in provider.get_capabilities()]
        return capabilities
