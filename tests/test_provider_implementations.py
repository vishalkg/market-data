#!/usr/bin/env python3

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from market_data.providers.base_provider import ProviderCapability
from market_data.providers.robinhood_provider import RobinhoodProvider
from market_data.providers.finnhub_provider import FinnhubProvider
from market_data.providers.alpha_vantage_provider import AlphaVantageProvider
from market_data.providers.fmp_provider import FMPProvider


@pytest.mark.asyncio
class TestRobinhoodProvider:
    
    def setup_method(self):
        self.provider = RobinhoodProvider()
    
    def test_name_and_capabilities(self):
        assert self.provider.name == "robinhood"
        capabilities = self.provider.get_capabilities()
        assert ProviderCapability.UNLIMITED_RATE in capabilities
        assert ProviderCapability.BATCH_QUOTES in capabilities
        assert ProviderCapability.OPTIONS_CHAIN in capabilities
    
    @patch('market_data.providers.robinhood_provider.rh')
    async def test_get_stock_quote_success(self, mock_rh):
        # Mock successful response
        mock_rh.get_quotes.return_value = [{
            "last_trade_price": "150.00",
            "high": "155.00",
            "low": "148.00",
            "open": "149.00",
            "previous_close": "147.00"
        }]
        
        # Mock auth
        self.provider._authenticated = True
        
        result = await self.provider.get_stock_quote("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["data"]["c"] == 150.0
        assert result["rate_limit"] == "unlimited"
        mock_rh.get_quotes.assert_called_once_with("AAPL")
    
    @patch('market_data.providers.robinhood_provider.rh')
    async def test_get_multiple_quotes_success(self, mock_rh):
        # Mock successful batch response
        mock_rh.get_quotes.return_value = [
            {"last_trade_price": "150.00", "high": "155.00", "low": "148.00", "open": "149.00", "previous_close": "147.00"},
            {"last_trade_price": "250.00", "high": "255.00", "low": "248.00", "open": "249.00", "previous_close": "247.00"}
        ]
        
        self.provider._authenticated = True
        
        result = await self.provider.get_multiple_quotes(["AAPL", "TSLA"])
        
        assert result["batch_size"] == 2
        assert "AAPL" in result["data"]
        assert "TSLA" in result["data"]
        assert result["data"]["AAPL"]["c"] == 150.0
    
    async def test_technical_indicators_not_implemented(self):
        with pytest.raises(NotImplementedError):
            await self.provider.get_rsi("AAPL")
        
        with pytest.raises(NotImplementedError):
            await self.provider.get_macd("AAPL")
        
        with pytest.raises(NotImplementedError):
            await self.provider.get_bollinger_bands("AAPL")


@pytest.mark.asyncio
class TestFinnhubProvider:
    
    def setup_method(self):
        self.provider = FinnhubProvider()
    
    def test_name_and_capabilities(self):
        assert self.provider.name == "finnhub"
        capabilities = self.provider.get_capabilities()
        assert ProviderCapability.RATE_LIMITED in capabilities
        assert ProviderCapability.REAL_TIME_QUOTES in capabilities
        assert ProviderCapability.FUNDAMENTALS in capabilities
    
    def test_validate_endpoint_access(self):
        assert self.provider._validate_endpoint_access("quote")
        assert self.provider._validate_endpoint_access("company-profile2")
        assert not self.provider._validate_endpoint_access("premium-endpoint")
    
    async def test_technical_indicators_not_implemented(self):
        with pytest.raises(NotImplementedError):
            await self.provider.get_rsi("AAPL")


@pytest.mark.asyncio
class TestAlphaVantageProvider:
    
    def setup_method(self):
        self.provider = AlphaVantageProvider()
    
    def test_name_and_capabilities(self):
        assert self.provider.name == "alpha_vantage"
        capabilities = self.provider.get_capabilities()
        assert ProviderCapability.TECHNICAL_INDICATORS in capabilities
        assert ProviderCapability.RATE_LIMITED in capabilities
    
    @patch('market_data.providers.alpha_vantage_provider.aiohttp.ClientSession.get')
    async def test_get_rsi_success(self, mock_get):
        # Mock successful RSI response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "Technical Analysis: RSI": {
                "2023-01-01": {"RSI": "45.67"}
            }
        }
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock API key manager
        with patch.object(self.provider.key_manager, 'get_available_key') as mock_key:
            mock_key.return_value = MagicMock(key="test_key")
            
            result = await self.provider.get_rsi("AAPL", 14)
            
            assert result["symbol"] == "AAPL"
            assert result["indicator"] == "RSI"
            assert result["period"] == 14
    
    @patch('market_data.providers.alpha_vantage_provider.aiohttp.ClientSession.get')
    async def test_get_macd_success(self, mock_get):
        # Mock successful MACD response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "Technical Analysis: MACD": {
                "2023-01-01": {"MACD": "1.23", "MACD_Signal": "1.45"}
            }
        }
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(self.provider.key_manager, 'get_available_key') as mock_key:
            mock_key.return_value = MagicMock(key="test_key")
            
            result = await self.provider.get_macd("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert result["indicator"] == "MACD"
    
    async def test_options_not_implemented(self):
        with pytest.raises(NotImplementedError):
            await self.provider.get_options_chain("AAPL")


@pytest.mark.asyncio
class TestFMPProvider:
    
    def setup_method(self):
        self.provider = FMPProvider()
    
    def test_name_and_capabilities(self):
        assert self.provider.name == "fmp"
        capabilities = self.provider.get_capabilities()
        assert ProviderCapability.FUNDAMENTALS in capabilities
        assert ProviderCapability.REAL_TIME_QUOTES in capabilities
        assert ProviderCapability.RATE_LIMITED in capabilities
    
    @patch('market_data.providers.fmp_provider.aiohttp.ClientSession.get')
    async def test_get_fundamentals_success(self, mock_get):
        # Mock successful fundamentals response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.side_effect = [
            [{"symbol": "AAPL", "companyName": "Apple Inc"}],  # profile
            [{"symbol": "AAPL", "peRatio": 25.5}]  # metrics
        ]
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(self.provider.key_manager, 'get_available_key') as mock_key:
            mock_key.return_value = MagicMock(key="test_key")
            
            result = await self.provider.get_fundamentals("AAPL")
            
            assert result["symbol"] == "AAPL"
            assert "profile" in result["data"]
            assert "metrics" in result["data"]
    
    @patch('market_data.providers.fmp_provider.aiohttp.ClientSession.get')
    async def test_get_multiple_quotes_success(self, mock_get):
        # Mock successful batch quotes response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = [
            {"symbol": "AAPL", "price": 150.0},
            {"symbol": "TSLA", "price": 250.0}
        ]
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(self.provider.key_manager, 'get_available_key') as mock_key:
            mock_key.return_value = MagicMock(key="test_key")
            
            result = await self.provider.get_multiple_quotes(["AAPL", "TSLA"])
            
            assert result["batch_size"] == 2
            assert "AAPL" in result["data"]
            assert "TSLA" in result["data"]
    
    async def test_technical_indicators_not_implemented(self):
        with pytest.raises(NotImplementedError):
            await self.provider.get_rsi("AAPL")
        
        with pytest.raises(NotImplementedError):
            await self.provider.get_bollinger_bands("AAPL")


# Integration tests for all providers
@pytest.mark.asyncio
class TestProviderIntegration:
    
    def test_all_providers_implement_interface(self):
        """Ensure all providers properly implement BaseProvider interface"""
        providers = [
            RobinhoodProvider(),
            FinnhubProvider(),
            AlphaVantageProvider(),
            FMPProvider()
        ]
        
        for provider in providers:
            # Test required properties
            assert hasattr(provider, 'name')
            assert isinstance(provider.name, str)
            
            # Test required methods
            assert hasattr(provider, 'get_capabilities')
            assert hasattr(provider, 'health_check')
            assert hasattr(provider, 'get_stock_quote')
            assert hasattr(provider, 'get_multiple_quotes')
            
            # Test capabilities are properly declared
            capabilities = provider.get_capabilities()
            assert isinstance(capabilities, list)
            assert all(isinstance(cap, ProviderCapability) for cap in capabilities)
    
    def test_provider_specializations(self):
        """Test that providers declare their specializations correctly"""
        rh = RobinhoodProvider()
        finnhub = FinnhubProvider()
        av = AlphaVantageProvider()
        fmp = FMPProvider()
        
        # Robinhood: Unlimited rate, batch quotes, options
        rh_caps = rh.get_capabilities()
        assert ProviderCapability.UNLIMITED_RATE in rh_caps
        assert ProviderCapability.BATCH_QUOTES in rh_caps
        assert ProviderCapability.OPTIONS_CHAIN in rh_caps
        
        # Alpha Vantage: Technical indicators
        av_caps = av.get_capabilities()
        assert ProviderCapability.TECHNICAL_INDICATORS in av_caps
        
        # FMP: Fundamentals
        fmp_caps = fmp.get_capabilities()
        assert ProviderCapability.FUNDAMENTALS in fmp_caps


if __name__ == "__main__":
    pytest.main([__file__])
