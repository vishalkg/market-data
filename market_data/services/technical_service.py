#!/usr/bin/env python3

import logging
from typing import Any, Dict, List

from ..providers.provider_factory import ProviderFactory
from ..providers.provider_chain import ProviderChain
from ..providers.base_provider import ProviderCapability

logger = logging.getLogger(__name__)


class TechnicalService:
    """Clean technical indicators aggregation service using provider chains"""
    
    def __init__(self):
        # Register providers
        self._register_providers()
        
        # Create provider chain: Alpha Vantage primary (only provider with technical indicators)
        self.technical_chain = ProviderChain([
            ProviderFactory.get_provider("alpha_vantage")
        ])
    
    def _register_providers(self):
        """Register all technical indicators capable providers"""
        from ..providers.alpha_vantage_provider import AlphaVantageProvider
        
        ProviderFactory.register_provider("alpha_vantage", AlphaVantageProvider)
    
    async def get_rsi(self, symbol: str, period: int = 14) -> Dict[str, Any]:
        """Get RSI technical indicator"""
        logger.info(f"Getting RSI for {symbol} (period: {period})")
        
        result = await self.technical_chain.execute_with_capability_filter(
            "get_rsi",
            ProviderCapability.TECHNICAL_INDICATORS,
            symbol,
            period=period
        )
        
        # Optimize RSI data if successful
        if "data" in result:
            result = self._optimize_rsi_data(result, symbol, period)
        
        logger.info(f"RSI completed for {symbol} via {result.get('provider', 'unknown')}")
        return result
    
    def _optimize_rsi_data(self, result: Dict[str, Any], symbol: str, period: int) -> Dict[str, Any]:
        """Optimize RSI data structure"""
        data = result.get("data", {})
        
        # Extract RSI values from Alpha Vantage format
        rsi_key = "Technical Analysis: RSI"
        if rsi_key in data:
            rsi_data = data[rsi_key]
            
            # Convert to more usable format
            optimized_data = []
            for date, values in rsi_data.items():
                optimized_data.append({
                    "date": date,
                    "rsi": float(values.get("RSI", 0))
                })
            
            # Sort by date (most recent first)
            optimized_data.sort(key=lambda x: x["date"], reverse=True)
            
            result["data"] = {
                "symbol": symbol,
                "indicator": "RSI",
                "period": period,
                "values": optimized_data[:50],  # Limit to 50 most recent
                "latest_rsi": optimized_data[0]["rsi"] if optimized_data else None
            }
            result["optimized"] = True
        
        return result
    
    async def get_macd(self, symbol: str) -> Dict[str, Any]:
        """Get MACD technical indicator"""
        logger.info(f"Getting MACD for {symbol}")
        
        result = await self.technical_chain.execute_with_capability_filter(
            "get_macd",
            ProviderCapability.TECHNICAL_INDICATORS,
            symbol
        )
        
        # Optimize MACD data if successful
        if "data" in result:
            result = self._optimize_macd_data(result, symbol)
        
        logger.info(f"MACD completed for {symbol} via {result.get('provider', 'unknown')}")
        return result
    
    def _optimize_macd_data(self, result: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Optimize MACD data structure"""
        data = result.get("data", {})
        
        # Extract MACD values from Alpha Vantage format
        macd_key = "Technical Analysis: MACD"
        if macd_key in data:
            macd_data = data[macd_key]
            
            # Convert to more usable format
            optimized_data = []
            for date, values in macd_data.items():
                optimized_data.append({
                    "date": date,
                    "macd": float(values.get("MACD", 0)),
                    "macd_signal": float(values.get("MACD_Signal", 0)),
                    "macd_hist": float(values.get("MACD_Hist", 0))
                })
            
            # Sort by date (most recent first)
            optimized_data.sort(key=lambda x: x["date"], reverse=True)
            
            result["data"] = {
                "symbol": symbol,
                "indicator": "MACD",
                "values": optimized_data[:50],  # Limit to 50 most recent
                "latest_macd": optimized_data[0] if optimized_data else None
            }
            result["optimized"] = True
        
        return result
    
    async def get_bollinger_bands(self, symbol: str, period: int = 20) -> Dict[str, Any]:
        """Get Bollinger Bands technical indicator"""
        logger.info(f"Getting Bollinger Bands for {symbol} (period: {period})")
        
        result = await self.technical_chain.execute_with_capability_filter(
            "get_bollinger_bands",
            ProviderCapability.TECHNICAL_INDICATORS,
            symbol,
            period=period
        )
        
        # Optimize Bollinger Bands data if successful
        if "data" in result:
            result = self._optimize_bollinger_data(result, symbol, period)
        
        logger.info(f"Bollinger Bands completed for {symbol} via {result.get('provider', 'unknown')}")
        return result
    
    def _optimize_bollinger_data(self, result: Dict[str, Any], symbol: str, period: int) -> Dict[str, Any]:
        """Optimize Bollinger Bands data structure"""
        data = result.get("data", {})
        
        # Extract Bollinger Bands values from Alpha Vantage format
        bb_key = "Technical Analysis: BBANDS"
        if bb_key in data:
            bb_data = data[bb_key]
            
            # Convert to more usable format
            optimized_data = []
            for date, values in bb_data.items():
                optimized_data.append({
                    "date": date,
                    "upper_band": float(values.get("Real Upper Band", 0)),
                    "middle_band": float(values.get("Real Middle Band", 0)),
                    "lower_band": float(values.get("Real Lower Band", 0))
                })
            
            # Sort by date (most recent first)
            optimized_data.sort(key=lambda x: x["date"], reverse=True)
            
            result["data"] = {
                "symbol": symbol,
                "indicator": "BBANDS",
                "period": period,
                "values": optimized_data[:50],  # Limit to 50 most recent
                "latest_bands": optimized_data[0] if optimized_data else None
            }
            result["optimized"] = True
        
        return result
    
    async def get_all_indicators(self, symbol: str) -> Dict[str, Any]:
        """Get all available technical indicators for a symbol"""
        logger.info(f"Getting all technical indicators for {symbol}")
        
        results = {}
        
        # Get RSI
        try:
            rsi_result = await self.get_rsi(symbol)
            results["rsi"] = rsi_result
        except Exception as e:
            results["rsi"] = {"error": str(e)}
        
        # Get MACD
        try:
            macd_result = await self.get_macd(symbol)
            results["macd"] = macd_result
        except Exception as e:
            results["macd"] = {"error": str(e)}
        
        # Get Bollinger Bands
        try:
            bb_result = await self.get_bollinger_bands(symbol)
            results["bollinger_bands"] = bb_result
        except Exception as e:
            results["bollinger_bands"] = {"error": str(e)}
        
        return {
            "symbol": symbol,
            "indicators": results,
            "timestamp": "now"
        }
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all technical indicators providers"""
        return await self.technical_chain.get_chain_status()
    
    def reorder_providers(self, priority_order: List[str]) -> None:
        """Reorder providers by priority"""
        self.technical_chain.reorder_by_priority(priority_order)
        logger.info(f"Reordered technical providers: {priority_order}")
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all providers in the chain"""
        capabilities = {}
        for provider in self.technical_chain.providers:
            capabilities[provider.name] = [cap.value for cap in provider.get_capabilities()]
        return capabilities
