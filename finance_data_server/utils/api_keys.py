"""API Key management with secure configuration loading"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add root directory to path for config files
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from .config import APIKey, ProviderType, load_api_keys

logger = logging.getLogger(__name__)


class APIKeyManager:
    def __init__(self):
        self.api_keys = load_api_keys()

    def get_available_key(self, provider: ProviderType) -> Optional[APIKey]:
        """Get an available API key for the provider"""
        keys = self.api_keys.get(provider, [])

        for key in keys:
            if key.requests_minute < key.requests_per_minute:
                return key

        return keys[0] if keys else None

    def get_next_available_key(
        self, provider: ProviderType, current_key: str
    ) -> Optional[APIKey]:
        """Get the next available API key for rotation when current key fails"""
        keys = self.api_keys.get(provider, [])

        # Find current key index
        current_index = -1
        for i, key in enumerate(keys):
            if key.key == current_key:
                current_index = i
                break

        # Try keys after current one
        for i in range(current_index + 1, len(keys)):
            if keys[i].requests_minute < keys[i].requests_per_minute:
                return keys[i]

        # Try keys before current one
        for i in range(0, current_index):
            if keys[i].requests_minute < keys[i].requests_per_minute:
                return keys[i]

        return None

    def update_key_usage(self, key: APIKey):
        """Update usage counter for a key (legacy method name)"""
        key.requests_minute += 1
        key.requests_day += 1

    def increment_usage(self, provider: ProviderType, key_value: str):
        """Increment usage counter for a specific key"""
        keys = self.api_keys.get(provider, [])
        for key in keys:
            if key.key == key_value:
                key.requests_minute += 1
                key.requests_day += 1
                break

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        stats = {"providers": {}, "summary": {}}

        for provider, keys in self.api_keys.items():
            provider_stats = []
            for key in keys:
                provider_stats.append(
                    {
                        "key": key.key[:8] + "..." if len(key.key) > 8 else key.key,
                        "requests_minute": key.requests_minute,
                        "limit_minute": key.requests_per_minute,
                        "requests_day": key.requests_day,
                        "limit_day": key.requests_per_day,
                    }
                )
            stats["providers"][provider.value] = provider_stats

        # Summary
        total_requests = sum(
            sum(key.requests_minute for key in keys) for keys in self.api_keys.values()
        )
        stats["summary"] = {
            "total_requests_minute": total_requests,
            "providers_count": len(self.api_keys),
            "total_keys": sum(len(keys) for keys in self.api_keys.values()),
        }

        return stats

    def reset_minute_counters(self):
        """Reset per-minute counters (called by scheduler)"""
        for keys in self.api_keys.values():
            for key in keys:
                key.requests_minute = 0

    def reset_daily_counters(self):
        """Reset daily counters (called by scheduler)"""
        for keys in self.api_keys.values():
            for key in keys:
                key.requests_day = 0
