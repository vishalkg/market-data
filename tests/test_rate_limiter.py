#!/usr/bin/env python3
"""Unit tests for rate limiter functionality"""

import pytest
import asyncio
from datetime import datetime, timedelta
from market_data.utils.rate_limiter import (
    RateLimitConfig,
    ProviderRateLimiter,
    SharedRateLimiter,
    get_rate_limiter
)


class TestRateLimitConfig:
    """Test rate limit configuration"""
    
    def test_config_creation(self):
        """Test creating rate limit config"""
        config = RateLimitConfig(requests_per_minute=60, requests_per_day=1000)
        assert config.requests_per_minute == 60
        assert config.requests_per_day == 1000
    
    def test_config_with_burst(self):
        """Test config with burst size"""
        config = RateLimitConfig(requests_per_minute=60, burst_size=10)
        assert config.burst_size == 10


class TestProviderRateLimiter:
    """Test provider-specific rate limiter"""
    
    @pytest.mark.asyncio
    async def test_acquire_within_limits(self):
        """Test acquiring permission within rate limits"""
        config = RateLimitConfig(requests_per_minute=60)
        limiter = ProviderRateLimiter("test_provider", config)
        
        # Should succeed
        result = await limiter.acquire(timeout=1.0)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self):
        """Test that rate limits are enforced"""
        config = RateLimitConfig(requests_per_minute=2)
        limiter = ProviderRateLimiter("test_provider", config)
        
        # First 2 should succeed
        assert await limiter.acquire(timeout=0.1) is True
        assert await limiter.acquire(timeout=0.1) is True
        
        # Third should fail (timeout)
        result = await limiter.acquire(timeout=0.1)
        assert result is False
    
    def test_get_status(self):
        """Test getting rate limit status"""
        config = RateLimitConfig(requests_per_minute=60, requests_per_day=1000)
        limiter = ProviderRateLimiter("test_provider", config)
        
        status = limiter.get_status()
        assert status["provider"] == "test_provider"
        assert status["minute_limit"] == 60
        assert status["daily_limit"] == 1000
        assert "can_make_request" in status


class TestSharedRateLimiter:
    """Test shared rate limiter singleton"""
    
    def test_singleton_pattern(self):
        """Test that SharedRateLimiter is a singleton"""
        limiter1 = SharedRateLimiter()
        limiter2 = SharedRateLimiter()
        assert limiter1 is limiter2
    
    def test_default_providers_registered(self):
        """Test that default providers are registered"""
        limiter = SharedRateLimiter()
        
        # Check default providers
        assert "alpha_vantage" in limiter.provider_limiters
        assert "finnhub" in limiter.provider_limiters
        assert "robinhood" in limiter.provider_limiters
    
    def test_register_custom_provider(self):
        """Test registering a custom provider"""
        limiter = SharedRateLimiter()
        config = RateLimitConfig(requests_per_minute=100)
        
        limiter.register_provider("custom_provider", config)
        assert "custom_provider" in limiter.provider_limiters
    
    @pytest.mark.asyncio
    async def test_acquire_for_provider(self):
        """Test acquiring rate limit for specific provider"""
        limiter = SharedRateLimiter()
        
        # Should succeed for robinhood (high limits)
        result = await limiter.acquire("robinhood", timeout=0.5)
        assert result is True
    
    def test_get_provider_status(self):
        """Test getting status for specific provider"""
        limiter = SharedRateLimiter()
        
        status = limiter.get_provider_status("finnhub")
        assert status is not None
        assert status["provider"] == "finnhub"
    
    def test_get_all_status(self):
        """Test getting status for all providers"""
        limiter = SharedRateLimiter()
        
        all_status = limiter.get_all_status()
        assert "alpha_vantage" in all_status
        assert "finnhub" in all_status
        assert "robinhood" in all_status


class TestGetRateLimiter:
    """Test rate limiter factory function"""
    
    def test_get_rate_limiter_returns_singleton(self):
        """Test that get_rate_limiter returns the singleton"""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is limiter2
    
    def test_get_rate_limiter_returns_shared_instance(self):
        """Test that get_rate_limiter returns SharedRateLimiter"""
        limiter = get_rate_limiter()
        assert isinstance(limiter, SharedRateLimiter)
