#!/usr/bin/env python3
"""Unit tests for authentication refresh logic"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta


class TestAuthenticationRefresh:
    """Test authentication refresh functionality"""
    
    @pytest.mark.asyncio
    async def test_auth_expiration_detection(self):
        """Test that expired auth is detected"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        with patch('market_data.utils.rate_limiter.get_rate_limiter'):
            provider = RobinhoodProvider()
            
            # Set old timestamp
            provider._auth_timestamp = datetime.now() - timedelta(hours=24)
            
            # Should detect as expired
            is_expired = provider._is_auth_expired()
            assert is_expired is True
    
    @pytest.mark.asyncio
    async def test_auth_not_expired(self):
        """Test that fresh auth is not expired"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        with patch('market_data.utils.rate_limiter.get_rate_limiter'):
            provider = RobinhoodProvider()
            
            # Set recent timestamp
            provider._auth_timestamp = datetime.now()
            
            # Should not be expired
            is_expired = provider._is_auth_expired()
            assert is_expired is False
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated_when_expired(self):
        """Test that ensure_authenticated refreshes when expired"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        with patch('market_data.utils.rate_limiter.get_rate_limiter'):
            provider = RobinhoodProvider()
            provider._authenticated = True
            provider._auth_timestamp = datetime.now() - timedelta(hours=24)
            
            # Mock successful re-auth
            with patch.object(provider.auth, 'login', return_value=True):
                await provider.ensure_authenticated()
                
                # Should have new timestamp
                assert provider._auth_timestamp is not None
                assert (datetime.now() - provider._auth_timestamp).seconds < 10
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated_when_fresh(self):
        """Test that ensure_authenticated skips when fresh"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        with patch('market_data.utils.rate_limiter.get_rate_limiter'):
            provider = RobinhoodProvider()
            provider._authenticated = True
            provider._auth_timestamp = datetime.now()
            
            old_timestamp = provider._auth_timestamp
            
            # Should not re-authenticate
            await provider.ensure_authenticated()
            
            # Timestamp should be unchanged
            assert provider._auth_timestamp == old_timestamp
    
    @pytest.mark.asyncio
    async def test_auth_retry_logic(self):
        """Test authentication retry with exponential backoff"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        with patch('market_data.utils.rate_limiter.get_rate_limiter'):
            provider = RobinhoodProvider()
            provider._authenticated = False
            
            call_count = {"count": 0}
            
            def mock_login():
                call_count["count"] += 1
                if call_count["count"] < 3:
                    return False
                return True
            
            # Mock login to fail twice then succeed
            with patch.object(provider.auth, 'login', side_effect=mock_login):
                await provider.ensure_authenticated()
                
                # Should have retried
                assert call_count["count"] == 3
                assert provider._authenticated is True
    
    @pytest.mark.asyncio
    async def test_auth_retry_exhaustion(self):
        """Test that auth fails after max retries"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        with patch('market_data.utils.rate_limiter.get_rate_limiter'):
            provider = RobinhoodProvider()
            provider._authenticated = False
            
            # Mock login to always fail
            with patch.object(provider.auth, 'login', return_value=False):
                with pytest.raises(Exception) as exc_info:
                    await provider.ensure_authenticated()
                
                assert "authentication failed" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_session_cleanup_on_auth_failure(self):
        """Test that session is cleaned up on auth failure"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        with patch('market_data.utils.rate_limiter.get_rate_limiter'):
            provider = RobinhoodProvider()
            provider._authenticated = True
            provider._auth_timestamp = datetime.now()
            
            # Mock logout to avoid real call
            with patch('robin_stocks.robinhood.logout'):
                # Cleanup should reset state
                await provider.cleanup_session()
            
            assert provider._authenticated is False
            assert provider._auth_timestamp is None
    
    @pytest.mark.asyncio
    async def test_auth_timeout_constant(self):
        """Test that AUTH_TIMEOUT_HOURS is set correctly"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        # Should be 23 hours (before 24-hour expiry)
        assert RobinhoodProvider.AUTH_TIMEOUT_HOURS == 23
    
    @pytest.mark.asyncio
    async def test_max_auth_retries_constant(self):
        """Test that MAX_AUTH_RETRIES is set correctly"""
        from market_data.providers.robinhood_provider import RobinhoodProvider
        
        # Should be 3 retries
        assert RobinhoodProvider.MAX_AUTH_RETRIES == 3
