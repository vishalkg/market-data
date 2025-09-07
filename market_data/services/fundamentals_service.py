#!/usr/bin/env python3

import logging
from typing import Any, Dict, List

from ..providers.provider_factory import ProviderFactory
from ..providers.provider_chain import ProviderChain
from ..providers.base_provider import ProviderCapability

logger = logging.getLogger(__name__)


class FundamentalsService:
    """Clean fundamentals data aggregation service using provider chains"""
    
    def __init__(self):
        # Register providers
        self._register_providers()
        
        # Create provider chain: Robinhood primary, FMP secondary, Finnhub fallback
        self.fundamentals_chain = ProviderChain([
            ProviderFactory.get_provider("robinhood"),
            ProviderFactory.get_provider("fmp"),
            ProviderFactory.get_provider("finnhub")
        ])
    
    def _register_providers(self):
        """Register all fundamentals-capable providers"""
        from ..providers.robinhood_provider import RobinhoodProvider
        from ..providers.fmp_provider import FMPProvider
        from ..providers.finnhub_provider import FinnhubProvider
        
        ProviderFactory.register_provider("robinhood", RobinhoodProvider)
        ProviderFactory.register_provider("fmp", FMPProvider)
        ProviderFactory.register_provider("finnhub", FinnhubProvider)
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get company fundamentals with intelligent fallback"""
        logger.info(f"Getting fundamentals for {symbol}")
        
        result = await self.fundamentals_chain.execute_with_capability_filter(
            "get_fundamentals",
            ProviderCapability.FUNDAMENTALS,
            symbol
        )
        
        # Normalize data format if successful
        if "data" in result:
            result = self._normalize_fundamentals_data(result)
        
        logger.info(f"Fundamentals completed for {symbol} via {result.get('provider', 'unknown')}")
        return result
    
    def _normalize_fundamentals_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize fundamentals data across different providers"""
        provider = result.get("provider", "unknown")
        data = result.get("data", {})
        
        # Create normalized structure
        normalized = {
            "symbol": result.get("symbol", ""),
            "provider": provider,
            "data": data,
            "normalized": True
        }
        
        # Provider-specific normalization
        if provider == "robinhood":
            normalized["data_type"] = "robinhood_fundamentals"
        elif provider == "fmp":
            normalized["data_type"] = "fmp_comprehensive"
            # FMP returns profile + metrics, keep structure
        elif provider == "finnhub":
            normalized["data_type"] = "finnhub_profile"
        
        return normalized
    
    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Get basic company profile information"""
        logger.info(f"Getting company profile for {symbol}")
        
        # Use fundamentals but focus on profile data
        result = await self.get_fundamentals(symbol)
        
        if "data" in result:
            # Extract profile-specific information
            profile_data = self._extract_profile_data(result)
            result["profile_focused"] = True
            result["data"] = profile_data
        
        return result
    
    def _extract_profile_data(self, fundamentals_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract profile-specific data from fundamentals"""
        provider = fundamentals_result.get("provider", "unknown")
        data = fundamentals_result.get("data", {})
        
        if provider == "fmp" and isinstance(data, dict) and "profile" in data:
            # FMP has separate profile section
            return data.get("profile", {})
        elif provider == "robinhood":
            # Robinhood data is already profile-focused
            return data
        elif provider == "finnhub":
            # Finnhub company-profile2 endpoint
            return data
        
        return data
    
    async def get_key_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get key financial metrics"""
        logger.info(f"Getting key metrics for {symbol}")
        
        # Try FMP first as it has dedicated metrics endpoint
        fmp_chain = ProviderChain([
            ProviderFactory.get_provider("fmp"),
            ProviderFactory.get_provider("robinhood")
        ])
        
        result = await fmp_chain.execute_with_capability_filter(
            "get_fundamentals",
            ProviderCapability.FUNDAMENTALS,
            symbol
        )
        
        if "data" in result:
            # Extract metrics-specific information
            metrics_data = self._extract_metrics_data(result)
            result["metrics_focused"] = True
            result["data"] = metrics_data
        
        return result
    
    def _extract_metrics_data(self, fundamentals_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics-specific data from fundamentals"""
        provider = fundamentals_result.get("provider", "unknown")
        data = fundamentals_result.get("data", {})
        
        if provider == "fmp" and isinstance(data, dict) and "metrics" in data:
            # FMP has separate metrics section
            return data.get("metrics", {})
        elif provider == "robinhood":
            # Extract key metrics from Robinhood data
            return {
                "pe_ratio": data.get("pe_ratio"),
                "market_cap": data.get("market_cap"),
                "dividend_yield": data.get("dividend_yield"),
                "volume": data.get("volume"),
                "average_volume": data.get("average_volume")
            }
        
        return data
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all fundamentals providers"""
        return await self.fundamentals_chain.get_chain_status()
    
    def reorder_providers(self, priority_order: List[str]) -> None:
        """Reorder providers by priority"""
        self.fundamentals_chain.reorder_by_priority(priority_order)
        logger.info(f"Reordered fundamentals providers: {priority_order}")
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all providers in the chain"""
        capabilities = {}
        for provider in self.fundamentals_chain.providers:
            capabilities[provider.name] = [cap.value for cap in provider.get_capabilities()]
        return capabilities
