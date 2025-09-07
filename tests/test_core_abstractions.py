#!/usr/bin/env python3

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import List

from market_data.providers.base_provider import BaseProvider, ProviderCapability
from market_data.providers.provider_factory import ProviderFactory
from market_data.providers.provider_chain import ProviderChain


class MockProvider(BaseProvider):
    """Mock provider for testing"""
    
    def __init__(self, provider_name: str = "mock", capabilities: List[ProviderCapability] = None, healthy: bool = True):
        self._name = provider_name
        self._capabilities = capabilities or [ProviderCapability.REAL_TIME_QUOTES]
        self._healthy = healthy
    
    @property
    def name(self) -> str:
        return self._name
    
    def get_capabilities(self) -> List[ProviderCapability]:
        return self._capabilities
    
    async def health_check(self) -> bool:
        return self._healthy
    
    async def get_stock_quote(self, symbol: str):
        if not self._healthy:
            raise Exception("Provider unhealthy")
        return {"symbol": symbol, "price": 100.0}
    
    async def get_multiple_quotes(self, symbols: List[str]):
        if not self._healthy:
            raise Exception("Provider unhealthy")
        return {"data": {s: {"price": 100.0} for s in symbols}}
    
    async def get_options_chain(self, symbol: str, expiration_date=None):
        return {"symbol": symbol, "options": []}
    
    async def get_fundamentals(self, symbol: str):
        return {"symbol": symbol, "pe_ratio": 15.0}
    
    async def get_historical_data(self, symbol: str, period: str = "1y"):
        return {"symbol": symbol, "data": []}
    
    async def get_rsi(self, symbol: str, period: int = 14):
        return {"symbol": symbol, "rsi": 50.0}
    
    async def get_macd(self, symbol: str):
        return {"symbol": symbol, "macd": 0.0}
    
    async def get_bollinger_bands(self, symbol: str, period: int = 20):
        return {"symbol": symbol, "bands": {}}


class TestProviderFactory:
    
    def setup_method(self):
        ProviderFactory.reset()
    
    def test_register_provider(self):
        ProviderFactory.register_provider("test", MockProvider)
        assert "test" in ProviderFactory.list_providers()
    
    def test_create_provider(self):
        ProviderFactory.register_provider("test", MockProvider)
        provider = ProviderFactory.create_provider(
            "test", 
            provider_name="test_instance", 
            capabilities=[ProviderCapability.REAL_TIME_QUOTES],
            healthy=True
        )
        assert provider.name == "test_instance"
        assert isinstance(provider, MockProvider)
    
    def test_unknown_provider_error(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            ProviderFactory.create_provider("nonexistent")
    
    def test_get_provider_caching(self):
        ProviderFactory.register_provider("test", MockProvider)
        provider1 = ProviderFactory.get_provider(
            "test", 
            provider_name="cached", 
            capabilities=[ProviderCapability.REAL_TIME_QUOTES]
        )
        provider2 = ProviderFactory.get_provider("test")
        assert provider1 is provider2


@pytest.mark.asyncio
class TestProviderChain:
    
    async def test_successful_execution(self):
        provider = MockProvider("test", [ProviderCapability.REAL_TIME_QUOTES])
        chain = ProviderChain([provider])
        
        result = await chain.execute("get_stock_quote", "AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["provider"] == "test"
        assert result["fallback_used"] is False
    
    async def test_fallback_execution(self):
        failing_provider = MockProvider("failing", [ProviderCapability.REAL_TIME_QUOTES], healthy=False)
        working_provider = MockProvider("working", [ProviderCapability.REAL_TIME_QUOTES])
        chain = ProviderChain([failing_provider, working_provider])
        
        result = await chain.execute("get_stock_quote", "AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["provider"] == "working"
        assert result["fallback_used"] is True
        assert "failing" in result["failed_providers"]
    
    async def test_all_providers_fail(self):
        failing1 = MockProvider("fail1", [ProviderCapability.REAL_TIME_QUOTES], healthy=False)
        failing2 = MockProvider("fail2", [ProviderCapability.REAL_TIME_QUOTES], healthy=False)
        chain = ProviderChain([failing1, failing2])
        
        result = await chain.execute("get_stock_quote", "AAPL")
        
        assert "error" in result
        assert result["error"] == "All providers in chain failed"
        assert len(result["provider_errors"]) == 2
    
    async def test_capability_filtering(self):
        quote_provider = MockProvider("quotes", [ProviderCapability.REAL_TIME_QUOTES])
        options_provider = MockProvider("options", [ProviderCapability.OPTIONS_CHAIN])
        chain = ProviderChain([quote_provider, options_provider])
        
        result = await chain.execute_with_capability_filter(
            "get_stock_quote", 
            ProviderCapability.REAL_TIME_QUOTES, 
            "AAPL"
        )
        
        assert result["provider"] == "quotes"
    
    async def test_no_capable_providers(self):
        provider = MockProvider("test", [ProviderCapability.FUNDAMENTALS])
        chain = ProviderChain([provider])
        
        result = await chain.execute_with_capability_filter(
            "get_stock_quote",
            ProviderCapability.REAL_TIME_QUOTES,
            "AAPL"
        )
        
        assert "error" in result
        assert "No providers support capability" in result["error"]
    
    async def test_chain_status(self):
        healthy_provider = MockProvider("healthy", [ProviderCapability.REAL_TIME_QUOTES])
        unhealthy_provider = MockProvider("unhealthy", [ProviderCapability.FUNDAMENTALS], healthy=False)
        chain = ProviderChain([healthy_provider, unhealthy_provider])
        
        status = await chain.get_chain_status()
        
        assert status["total_providers"] == 2
        assert status["healthy_providers"] == 1
        assert status["chain_status"]["healthy"]["healthy"] is True
        assert status["chain_status"]["unhealthy"]["healthy"] is False
    
    def test_reorder_by_priority(self):
        provider1 = MockProvider("first", [])
        provider2 = MockProvider("second", [])
        provider3 = MockProvider("third", [])
        chain = ProviderChain([provider1, provider2, provider3])
        
        chain.reorder_by_priority(["third", "first"])
        
        assert chain.providers[0].name == "third"
        assert chain.providers[1].name == "first"
        assert chain.providers[2].name == "second"


class TestBaseProvider:
    
    def test_supports_capability(self):
        provider = MockProvider("test", [ProviderCapability.REAL_TIME_QUOTES])
        
        assert provider.supports_capability(ProviderCapability.REAL_TIME_QUOTES)
        assert not provider.supports_capability(ProviderCapability.OPTIONS_CHAIN)
    
    def test_get_metadata(self):
        capabilities = [ProviderCapability.REAL_TIME_QUOTES, ProviderCapability.FUNDAMENTALS]
        provider = MockProvider("test", capabilities)
        
        metadata = provider.get_metadata()
        
        assert metadata["name"] == "test"
        assert metadata["type"] == "MockProvider"
        assert len(metadata["capabilities"]) == 2
        assert "real_time_quotes" in metadata["capabilities"]
        assert "fundamentals" in metadata["capabilities"]


if __name__ == "__main__":
    pytest.main([__file__])
