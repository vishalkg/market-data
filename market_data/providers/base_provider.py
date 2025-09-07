#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum


class DataType(Enum):
    STOCK_QUOTE = "stock_quote"
    OPTIONS_CHAIN = "options_chain"
    FUNDAMENTALS = "fundamentals"
    HISTORICAL = "historical"
    TECHNICAL = "technical"


class ProviderCapability(Enum):
    REAL_TIME_QUOTES = "real_time_quotes"
    BATCH_QUOTES = "batch_quotes"
    OPTIONS_CHAIN = "options_chain"
    FUNDAMENTALS = "fundamentals"
    HISTORICAL_DATA = "historical_data"
    TECHNICAL_INDICATORS = "technical_indicators"
    UNLIMITED_RATE = "unlimited_rate"
    RATE_LIMITED = "rate_limited"


class BaseProvider(ABC):
    """Abstract base class for all market data providers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ProviderCapability]:
        """Return list of capabilities this provider supports"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available and authenticated"""
        pass
    
    # Stock data methods
    @abstractmethod
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote for a single symbol"""
        pass
    
    @abstractmethod
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get real-time stock quotes for multiple symbols"""
        pass
    
    # Options data methods
    @abstractmethod
    async def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """Get options chain for a symbol"""
        pass
    
    # Fundamentals data methods
    @abstractmethod
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get company fundamentals data"""
        pass
    
    # Historical data methods
    @abstractmethod
    async def get_historical_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get historical price data"""
        pass
    
    # Technical indicators methods
    @abstractmethod
    async def get_rsi(self, symbol: str, period: int = 14) -> Dict[str, Any]:
        """Get RSI technical indicator"""
        pass
    
    @abstractmethod
    async def get_macd(self, symbol: str) -> Dict[str, Any]:
        """Get MACD technical indicator"""
        pass
    
    @abstractmethod
    async def get_bollinger_bands(self, symbol: str, period: int = 20) -> Dict[str, Any]:
        """Get Bollinger Bands technical indicator"""
        pass
    
    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if provider supports a specific capability"""
        return capability in self.get_capabilities()
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get provider metadata"""
        return {
            "name": self.name,
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "type": self.__class__.__name__
        }
