#!/usr/bin/env python3
"""
Shared rate limiting mechanism for coordinating API requests across services.
Prevents multiple services from exhausting the same provider's rate limits.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import deque

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Configuration for a provider's rate limits"""
    
    def __init__(
        self,
        requests_per_minute: Optional[int] = None,
        requests_per_day: Optional[int] = None,
        burst_size: Optional[int] = None
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.burst_size = burst_size or (requests_per_minute if requests_per_minute else 10)


class ProviderRateLimiter:
    """Rate limiter for a single provider"""
    
    def __init__(self, provider_name: str, config: RateLimitConfig):
        self.provider_name = provider_name
        self.config = config
        
        # Track requests in sliding windows
        self.minute_requests = deque()
        self.daily_requests = deque()
        
        # Request queue for when limits are reached
        self.request_queue = asyncio.Queue()
        self.processing = False
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    def _cleanup_old_requests(self):
        """Remove requests outside the time windows"""
        now = datetime.now()
        
        # Cleanup minute window
        if self.config.requests_per_minute:
            minute_ago = now - timedelta(minutes=1)
            while self.minute_requests and self.minute_requests[0] < minute_ago:
                self.minute_requests.popleft()
        
        # Cleanup daily window
        if self.config.requests_per_day:
            day_ago = now - timedelta(days=1)
            while self.daily_requests and self.daily_requests[0] < day_ago:
                self.daily_requests.popleft()
    
    def _can_make_request(self) -> bool:
        """Check if a request can be made without exceeding limits"""
        self._cleanup_old_requests()
        
        # Check minute limit
        if self.config.requests_per_minute:
            if len(self.minute_requests) >= self.config.requests_per_minute:
                return False
        
        # Check daily limit
        if self.config.requests_per_day:
            if len(self.daily_requests) >= self.config.requests_per_day:
                return False
        
        return True
    
    def _get_wait_time(self) -> float:
        """Calculate how long to wait before next request is allowed"""
        self._cleanup_old_requests()
        now = datetime.now()
        
        wait_times = []
        
        # Check minute limit
        if self.config.requests_per_minute and len(self.minute_requests) >= self.config.requests_per_minute:
            oldest = self.minute_requests[0]
            wait_until = oldest + timedelta(minutes=1)
            wait_times.append((wait_until - now).total_seconds())
        
        # Check daily limit
        if self.config.requests_per_day and len(self.daily_requests) >= self.config.requests_per_day:
            oldest = self.daily_requests[0]
            wait_until = oldest + timedelta(days=1)
            wait_times.append((wait_until - now).total_seconds())
        
        return max(wait_times) if wait_times else 0
    
    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request.
        Returns True if acquired, False if timeout exceeded.
        """
        async with self._lock:
            # Check if we can make request immediately
            if self._can_make_request():
                now = datetime.now()
                if self.config.requests_per_minute:
                    self.minute_requests.append(now)
                if self.config.requests_per_day:
                    self.daily_requests.append(now)
                return True
            
            # Need to wait
            wait_time = self._get_wait_time()
            
            if timeout and wait_time > timeout:
                logger.warning(
                    f"Rate limit wait time ({wait_time:.1f}s) exceeds timeout ({timeout}s) "
                    f"for provider {self.provider_name}"
                )
                return False
            
            logger.info(f"Rate limit reached for {self.provider_name}, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            
            # Try again after waiting
            now = datetime.now()
            if self.config.requests_per_minute:
                self.minute_requests.append(now)
            if self.config.requests_per_day:
                self.daily_requests.append(now)
            return True
    
    def get_status(self) -> Dict:
        """Get current rate limit status"""
        self._cleanup_old_requests()
        
        status = {
            "provider": self.provider_name,
            "minute_requests": len(self.minute_requests) if self.config.requests_per_minute else None,
            "minute_limit": self.config.requests_per_minute,
            "daily_requests": len(self.daily_requests) if self.config.requests_per_day else None,
            "daily_limit": self.config.requests_per_day,
            "can_make_request": self._can_make_request()
        }
        
        if not status["can_make_request"]:
            status["wait_time_seconds"] = self._get_wait_time()
        
        return status


class SharedRateLimiter:
    """
    Shared rate limiter coordinating requests across all services.
    Singleton pattern ensures all services use the same rate limits.
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.provider_limiters: Dict[str, ProviderRateLimiter] = {}
        self._initialized = True
        
        # Register default provider limits
        self._register_default_limits()
    
    def _register_default_limits(self):
        """Register known provider rate limits"""
        # Alpha Vantage: 25 requests per day (free tier)
        self.register_provider(
            "alpha_vantage",
            RateLimitConfig(requests_per_minute=5, requests_per_day=25)
        )
        
        # Finnhub: 60 requests per minute (free tier)
        self.register_provider(
            "finnhub",
            RateLimitConfig(requests_per_minute=60, requests_per_day=None)
        )
        
        # Robinhood: Unlimited (but be respectful)
        self.register_provider(
            "robinhood",
            RateLimitConfig(requests_per_minute=120, requests_per_day=None)
        )
    
    def register_provider(self, provider_name: str, config: RateLimitConfig):
        """Register a provider with its rate limit configuration"""
        if provider_name not in self.provider_limiters:
            self.provider_limiters[provider_name] = ProviderRateLimiter(provider_name, config)
            logger.info(f"Registered rate limiter for provider: {provider_name}")
    
    async def acquire(self, provider_name: str, timeout: Optional[float] = 30.0) -> bool:
        """
        Acquire permission to make a request to the specified provider.
        
        Args:
            provider_name: Name of the provider
            timeout: Maximum time to wait for rate limit (seconds)
        
        Returns:
            True if permission granted, False if timeout exceeded
        """
        if provider_name not in self.provider_limiters:
            logger.warning(f"No rate limiter configured for provider: {provider_name}")
            return True  # Allow request if no limits configured
        
        limiter = self.provider_limiters[provider_name]
        return await limiter.acquire(timeout)
    
    def get_provider_status(self, provider_name: str) -> Optional[Dict]:
        """Get rate limit status for a specific provider"""
        if provider_name not in self.provider_limiters:
            return None
        
        return self.provider_limiters[provider_name].get_status()
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get rate limit status for all providers"""
        return {
            name: limiter.get_status()
            for name, limiter in self.provider_limiters.items()
        }


# Global singleton instance
_rate_limiter = SharedRateLimiter()


def get_rate_limiter() -> SharedRateLimiter:
    """Get the global rate limiter instance"""
    return _rate_limiter
