#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp

from ..utils.api_keys import APIKeyManager, ProviderType

logger = logging.getLogger(__name__)


class ProviderClient:
    def __init__(self):
        self.key_manager = APIKeyManager()
        self.provider_configs = {
            ProviderType.FINNHUB: {
                "base_url": "https://finnhub.io/api/v1",
                "auth_param": "token",
                "auth_method": "query",  # Use query parameter instead of header
                "free_endpoints": [
                    "quote",
                    "company-profile2",
                    "stock/candle",
                ],  # Free tier endpoints
            },
            ProviderType.ALPHA_VANTAGE: {
                "base_url": "https://www.alphavantage.co/query",
                "auth_param": "apikey",
            },
            ProviderType.FMP: {
                "base_url": "https://financialmodelingprep.com/api/v3",
                "auth_param": "apikey",
            },
            ProviderType.POLYGON: {
                "base_url": "https://files.polygon.io",
                "auth_param": "apikey",
            },
        }

    def validate_endpoint_access(self, provider: ProviderType, endpoint: str) -> bool:
        """Check if endpoint is available for free tier"""
        if provider == ProviderType.FINNHUB:
            config = self.provider_configs[provider]
            free_endpoints = config.get("free_endpoints", [])
            return any(endpoint.startswith(free_ep) for free_ep in free_endpoints)
        return True  # Other providers don't have this restriction

    async def make_request(
        self,
        session: aiohttp.ClientSession,
        provider: ProviderType,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        if params is None:
            params = {}

        # Validate endpoint access for free tier
        if not self.validate_endpoint_access(provider, endpoint):
            return {
                "error": f"Endpoint '{endpoint}' requires premium subscription",
                "provider": provider.value,
                "details": "This endpoint is not available on the free tier",
            }

        config = self.provider_configs[provider]
        key = self.key_manager.get_available_key(provider)

        if not key:
            return {"error": f"No available API keys for {provider.value}"}

        # Add API key to params (always use query parameter for Finnhub)
        params[config["auth_param"]] = key.key
        url = f"{config['base_url']}/{endpoint}"

        for attempt in range(max_retries):
            try:
                self.key_manager.update_key_usage(key)
                logger.info(f"Making request to {provider.value}: {url}")

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        try:
                            # Try JSON parsing first regardless of content-type
                            data = await response.json()
                            return {"provider": provider.value, "data": data}
                        except Exception:
                            # If JSON parsing fails, try parsing text as JSON
                            text_data = await response.text()
                            try:
                                # Attempt to parse text as JSON
                                import json

                                data = json.loads(text_data)
                                return {"provider": provider.value, "data": data}
                            except json.JSONDecodeError:
                                logger.warning(
                                    f"Non-JSON response from {provider.value} (length: {len(text_data)} chars)"
                                )
                                return {
                                    "error": f"API returned non-JSON text response",
                                    "provider": provider.value,
                                }
                    elif response.status == 401:  # Unauthorized
                        error_text = await response.text()
                        logger.error(
                            f"401 Unauthorized from {provider.value}: {error_text}"
                        )

                        # Try next key if available
                        next_key = self.key_manager.get_next_available_key(
                            provider, key.key
                        )
                        if next_key and attempt < max_retries - 1:
                            key = next_key
                            params[config["auth_param"]] = key.key
                            logger.info(f"Trying next API key for {provider.value}")
                            continue

                        return {
                            "error": f"Invalid API key or insufficient permissions",
                            "provider": provider.value,
                            "details": error_text,
                            "suggestion": "Check if endpoint requires premium subscription or API key is valid",
                        }
                    elif response.status == 429:  # Rate limited
                        logger.warning(
                            f"Rate limited on {provider.value}, attempt {attempt + 1}"
                        )
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2**attempt)
                            continue
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"HTTP {response.status} from {provider.value}: {error_text}"
                        )
                        return {
                            "error": f"HTTP {response.status}",
                            "provider": provider.value,
                            "details": error_text,
                        }

            except Exception as e:
                logger.error(f"Request failed for {provider.value}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                return {"error": str(e), "provider": provider.value}

        return {"error": "Max retries exceeded", "provider": provider.value}
