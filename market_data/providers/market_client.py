#!/usr/bin/env python3

import logging
from typing import Any, Dict, Optional

import aiohttp

from ..services.stock_service import StockService
from ..services.options_service import OptionsService
from ..services.fundamentals_service import FundamentalsService
from ..services.technical_service import TechnicalService

logger = logging.getLogger(__name__)


class MultiProviderClient:
    """Simplified market client using clean service layer"""
    
    def __init__(self):
        # Initialize services
        self.stock_service = StockService()
        self.options_service = OptionsService()
        self.fundamentals_service = FundamentalsService()
        self.technical_service = TechnicalService()
        
        logger.info("MultiProviderClient initialized with service layer")

    # Stock data methods
    async def get_quote(self, session: aiohttp.ClientSession, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote via service layer"""
        return await self.stock_service.get_stock_quote(symbol)
    
    async def get_stock_quote(self, session: aiohttp.ClientSession, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote via service layer (compatibility alias)"""
        return await self.stock_service.get_stock_quote(symbol)
    
    async def get_multiple_quotes(self, symbols: list) -> Dict[str, Any]:
        """Get multiple stock quotes via service layer"""
        return await self.stock_service.get_multiple_quotes(symbols)

    # Options data methods
    async def get_options_chain(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        expiration_date: Optional[str] = None,
        max_expirations: int = 10,
    ) -> Dict[str, Any]:
        """Get options chain via service layer"""
        return await self.options_service.get_options_chain(
            symbol, 
            expiration_date=expiration_date,
            max_expirations=max_expirations
        )

    # Fundamentals data methods
    async def get_fundamentals(self, session: aiohttp.ClientSession, symbol: str) -> Dict[str, Any]:
        """Get company fundamentals via service layer"""
        return await self.fundamentals_service.get_fundamentals(symbol)
    
    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Get company profile via service layer"""
        return await self.fundamentals_service.get_company_profile(symbol)

    # Technical indicators methods
    async def get_rsi(self, session: aiohttp.ClientSession, symbol: str, period: int = 14) -> Dict[str, Any]:
        """Get RSI via service layer"""
        return await self.technical_service.get_rsi(symbol, period)

    async def get_macd(self, session: aiohttp.ClientSession, symbol: str) -> Dict[str, Any]:
        """Get MACD via service layer"""
        return await self.technical_service.get_macd(symbol)

    async def get_bollinger_bands(self, session: aiohttp.ClientSession, symbol: str, period: int = 20) -> Dict[str, Any]:
        """Get Bollinger Bands via service layer"""
        return await self.technical_service.get_bollinger_bands(symbol, period)
    
    async def get_technical_indicators(self, session: aiohttp.ClientSession, symbol: str, indicator: str) -> Dict[str, Any]:
        """Get technical indicators via service layer (compatibility method)"""
        if indicator.lower() == "rsi":
            return await self.technical_service.get_rsi(symbol)
        elif indicator.lower() == "macd":
            return await self.technical_service.get_macd(symbol)
        elif indicator.lower() == "bollinger_bands":
            return await self.technical_service.get_bollinger_bands(symbol)
        elif indicator.lower() == "all":
            return await self.technical_service.get_all_indicators(symbol)
        else:
            return {"error": f"Unknown indicator: {indicator}", "available": ["rsi", "macd", "bollinger_bands", "all"]}

    # Historical data methods (placeholder - would need historical service)
    async def get_historical_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get historical data - placeholder for future historical service"""
        # For now, try to get from stock service providers
        try:
            # Use first available provider that supports historical data
            for provider in self.stock_service.quote_chain.providers:
                if hasattr(provider, 'get_historical_data'):
                    result = await provider.get_historical_data(symbol, period)
                    result["provider"] = provider.name
                    return result
            
            return {"error": "No providers support historical data", "symbol": symbol}
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    # Market status methods (placeholder)
    async def get_market_status(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Get market status - placeholder"""
        return {"status": "unknown", "note": "Market status not implemented in service layer yet"}

    # Service management methods
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics from all services"""
        return {
            "stock_service": self.stock_service.get_available_capabilities(),
            "options_service": self.options_service.get_available_capabilities(),
            "fundamentals_service": self.fundamentals_service.get_available_capabilities(),
            "technical_service": self.technical_service.get_available_capabilities()
        }
    
    async def get_all_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers across all services"""
        return {
            "stock_providers": await self.stock_service.get_provider_status(),
            "options_providers": await self.options_service.get_provider_status(),
            "fundamentals_providers": await self.fundamentals_service.get_provider_status(),
            "technical_providers": await self.technical_service.get_provider_status()
        }
    
    def reorder_all_providers(self, priority_order: list) -> None:
        """Reorder providers across all services"""
        self.stock_service.reorder_providers(priority_order)
        self.options_service.reorder_providers(priority_order)
        self.fundamentals_service.reorder_providers(priority_order)
        self.technical_service.reorder_providers(priority_order)
        logger.info(f"Reordered all service providers: {priority_order}")
