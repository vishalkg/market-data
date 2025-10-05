#!/usr/bin/env python3

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from market_data.services.stock_service import StockService
from market_data.services.options_service import OptionsService
from market_data.services.fundamentals_service import FundamentalsService
from market_data.services.technical_service import TechnicalService


@pytest.mark.asyncio
class TestStockService:
    
    def setup_method(self):
        with patch('market_data.services.stock_service.ProviderFactory'):
            self.service = StockService()
    
    async def test_get_stock_quote_success(self):
        # Mock the provider chain
        mock_result = {
            "symbol": "AAPL",
            "data": {"c": 150.0, "h": 155.0},
            "provider": "robinhood"
        }
        
        self.service.quote_chain.execute_with_capability_filter = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_stock_quote("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["provider"] == "robinhood"
        assert result["data"]["c"] == 150.0
    
    async def test_get_multiple_quotes_batch(self):
        # Mock successful batch response
        mock_result = {
            "data": {"AAPL": {"c": 150.0}, "TSLA": {"c": 250.0}},
            "provider": "robinhood",
            "batch_size": 2
        }
        
        self.service.quote_chain.execute_with_capability_filter = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_multiple_quotes(["AAPL", "TSLA"])
        
        assert result["batch_size"] == 2
        assert "AAPL" in result["data"]
        assert "TSLA" in result["data"]
    
    async def test_get_multiple_quotes_individual_fallback(self):
        # Mock no batch capability, fallback to individual
        self.service.quote_chain.execute_with_capability_filter = AsyncMock(
            return_value={"error": "No providers support capability: batch_quotes"}
        )
        
        # Mock individual quote calls
        self.service.get_stock_quote = AsyncMock(side_effect=[
            {"data": {"c": 150.0}},
            {"data": {"c": 250.0}}
        ])
        
        result = await self.service.get_multiple_quotes(["AAPL", "TSLA"])
        
        assert result["method"] == "individual_fallback"
        assert result["batch_size"] == 2


@pytest.mark.asyncio
class TestOptionsService:
    
    def setup_method(self):
        with patch('market_data.services.options_service.ProviderFactory'):
            self.service = OptionsService()
    
    async def test_get_options_chain_success(self):
        # Mock the provider chain
        mock_result = {
            "symbol": "AAPL",
            "data": {"options": [{"strike": 150, "type": "call"}]},
            "provider": "robinhood"
        }
        
        self.service.options_chain.execute_with_capability_filter = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_options_chain("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["provider"] == "robinhood"
        assert "optimization" in result
    
    async def test_get_options_by_expiration(self):
        # Mock the provider chain
        mock_result = {
            "symbol": "AAPL",
            "data": {"options": []},
            "provider": "robinhood"
        }
        
        self.service.options_chain.execute_with_capability_filter = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_options_by_expiration("AAPL", "2024-01-19")
        
        assert result["filtered_by_expiration"] == "2024-01-19"


@pytest.mark.asyncio
class TestFundamentalsService:
    
    def setup_method(self):
        with patch('market_data.services.fundamentals_service.ProviderFactory'):
            self.service = FundamentalsService()
    
    async def test_get_fundamentals_success(self):
        # Mock the provider chain
        mock_result = {
            "symbol": "AAPL",
            "data": {"pe_ratio": 25.5, "market_cap": "2.5T"},
            "provider": "robinhood"
        }
        
        self.service.fundamentals_chain.execute_with_capability_filter = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_fundamentals("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["normalized"] is True
        assert result["data_type"] == "robinhood_fundamentals"
    
    async def test_get_company_profile(self):
        # Mock fundamentals call
        self.service.get_fundamentals = AsyncMock(return_value={
            "symbol": "AAPL",
            "data": {"companyName": "Apple Inc"},
            "provider": "fmp"
        })
        
        result = await self.service.get_company_profile("AAPL")
        
        assert result["profile_focused"] is True
    
    async def test_normalize_fmp_data(self):
        # Test FMP data normalization
        result = {
            "symbol": "AAPL",
            "provider": "fmp",
            "data": {"profile": {"companyName": "Apple"}, "metrics": {"peRatio": 25}}
        }
        
        normalized = self.service._normalize_fundamentals_data(result)
        
        assert normalized["normalized"] is True
        assert normalized["data_type"] == "fmp_comprehensive"


@pytest.mark.asyncio
class TestTechnicalService:
    
    def setup_method(self):
        with patch('market_data.services.technical_service.ProviderFactory'):
            self.service = TechnicalService()
    
    async def test_get_rsi_success(self):
        # Mock the provider chain
        mock_result = {
            "symbol": "AAPL",
            "data": {
                "Technical Analysis: RSI": {
                    "2023-01-01": {"RSI": "45.67"},
                    "2023-01-02": {"RSI": "46.23"}
                }
            },
            "provider": "alpha_vantage"
        }
        
        self.service.technical_chain.execute_with_capability_filter = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_rsi("AAPL", 14)
        
        assert result["optimized"] is True
        assert result["data"]["indicator"] == "RSI"
        assert result["data"]["period"] == 14
        assert result["data"]["latest_rsi"] == 46.23  # Most recent
    
    async def test_get_macd_success(self):
        # Mock the provider chain
        mock_result = {
            "symbol": "AAPL",
            "data": {
                "Technical Analysis: MACD": {
                    "2023-01-01": {"MACD": "1.23", "MACD_Signal": "1.45", "MACD_Hist": "-0.22"}
                }
            },
            "provider": "alpha_vantage"
        }
        
        self.service.technical_chain.execute_with_capability_filter = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_macd("AAPL")
        
        assert result["optimized"] is True
        assert result["data"]["indicator"] == "MACD"
        assert result["data"]["latest_macd"]["macd"] == 1.23
    
    async def test_get_all_indicators(self):
        # Mock individual indicator calls
        self.service.get_rsi = AsyncMock(return_value={"data": {"rsi": 45}})
        self.service.get_macd = AsyncMock(return_value={"data": {"macd": 1.23}})
        self.service.get_bollinger_bands = AsyncMock(return_value={"data": {"bands": {}}})
        
        result = await self.service.get_all_indicators("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert "rsi" in result["indicators"]
        assert "macd" in result["indicators"]
        assert "bollinger_bands" in result["indicators"]


# Integration tests for service layer
@pytest.mark.asyncio
class TestServiceIntegration:
    
    def test_all_services_instantiate(self):
        """Test that all services can be instantiated"""
        with patch('market_data.services.stock_service.ProviderFactory'), \
             patch('market_data.services.options_service.ProviderFactory'), \
             patch('market_data.services.fundamentals_service.ProviderFactory'), \
             patch('market_data.services.technical_service.ProviderFactory'):
            
            services = [
                StockService(),
                OptionsService(),
                FundamentalsService(),
                TechnicalService()
            ]
            
            for service in services:
                # Test required methods exist
                assert hasattr(service, 'get_provider_status')
                assert hasattr(service, 'reorder_providers')
                assert hasattr(service, 'get_available_capabilities')
    
    def test_service_provider_registration(self):
        """Test that services register appropriate providers"""
        with patch('market_data.services.stock_service.ProviderFactory') as mock_factory:
            StockService()
            
            # Should register robinhood and finnhub for stocks
            assert mock_factory.register_provider.call_count >= 2


if __name__ == "__main__":
    pytest.main([__file__])
