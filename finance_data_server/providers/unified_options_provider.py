#!/usr/bin/env python3

import logging
from typing import Any, Dict, List, Optional

from .robinhood_options import RobinhoodOptionsProvider

logger = logging.getLogger(__name__)


class UnifiedOptionsProvider:
    """Unified options provider with Robinhood primary and Finnhub fallback"""

    def __init__(self):
        self.robinhood = RobinhoodOptionsProvider()
        self.fallback_available = True

    async def get_options_chain(
        self,
        symbol: str,
        expiration: Optional[str] = None,
        max_expirations: int = 3,
        raw_data: bool = False,
        include_greeks: bool = False,
    ) -> Dict[str, Any]:
        """Get options chain with intelligent fallback"""

        # Try Robinhood first (primary)
        try:
            logger.info(f"Attempting Robinhood options for {symbol}")
            result = self.robinhood.get_options_chain(
                symbol, expiration, max_expirations, raw_data, include_greeks
            )

            if "error" not in result:
                logger.info(f"✅ Robinhood success for {symbol}")
                return result
            else:
                logger.warning(f"Robinhood failed for {symbol}: {result['error']}")

        except Exception as e:
            logger.error(f"Robinhood exception for {symbol}: {e}")

        # Fallback to existing Finnhub system
        logger.info(f"Falling back to Finnhub for {symbol}")
        return await self._get_finnhub_fallback(symbol, expiration, max_expirations)

    async def _get_finnhub_fallback(
        self, symbol: str, expiration: Optional[str], max_expirations: int
    ) -> Dict[str, Any]:
        """Fallback to existing Finnhub options system"""
        try:
            # Import existing multi-provider client
            import aiohttp

            from .market_client import MultiProviderClient

            multi_client = MultiProviderClient()

            async with aiohttp.ClientSession() as session:
                result = await multi_client.get_options_chain(
                    session, symbol, expiration, max_expirations
                )

                if result and "error" not in result:
                    # Add fallback metadata
                    if isinstance(result, dict):
                        result["provider"] = "finnhub_fallback"
                        result["fallback_used"] = True
                        result["primary_provider_failed"] = "robinhood"

                    logger.info(f"✅ Finnhub fallback success for {symbol}")
                    return result
                else:
                    logger.error(f"Finnhub fallback failed for {symbol}")
                    return {
                        "error": "Both Robinhood and Finnhub failed",
                        "provider": "unified_fallback",
                        "primary_error": "Robinhood unavailable",
                        "fallback_error": (
                            result.get("error", "Unknown") if result else "No response"
                        ),
                    }

        except Exception as e:
            logger.error(f"Finnhub fallback exception for {symbol}: {e}")
            return {
                "error": f"All providers failed: {str(e)}",
                "provider": "unified_fallback",
                "primary_provider": "robinhood",
                "fallback_provider": "finnhub",
            }

    async def get_option_greeks(
        self, symbol: str, strike: float, expiration: str, option_type: str
    ) -> Dict[str, Any]:
        """Get Greeks with fallback (Robinhood only for now)"""
        try:
            result = self.robinhood.get_option_greeks(
                symbol, strike, expiration, option_type
            )

            if "error" not in result:
                return result
            else:
                return {
                    "error": "Greeks only available via Robinhood",
                    "provider": "unified_fallback",
                    "note": "Fallback providers don't support Greeks",
                }

        except Exception as e:
            return {
                "error": f"Greeks unavailable: {str(e)}",
                "provider": "unified_fallback",
            }

    def get_available_expirations(self, symbol: str) -> List[str]:
        """Get available expirations with fallback"""
        try:
            # Try Robinhood first
            expirations = self.robinhood.get_available_expirations(symbol)
            if expirations:
                return expirations
        except Exception as e:
            logger.warning(f"Robinhood expirations failed for {symbol}: {e}")

        # Fallback: return common expiration pattern
        from datetime import datetime, timedelta

        today = datetime.now()
        fallback_expirations = []

        # Generate next 4 Fridays (common options expirations)
        for i in range(4):
            days_ahead = (4 - today.weekday()) % 7  # Friday is 4
            if days_ahead == 0:
                days_ahead = 7
            friday = today + timedelta(days=days_ahead + (i * 7))
            fallback_expirations.append(friday.strftime("%Y-%m-%d"))

        logger.info(f"Using fallback expirations for {symbol}")
        return fallback_expirations

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {
            "primary_provider": "robinhood",
            "fallback_provider": "finnhub",
            "robinhood_status": "unknown",
            "finnhub_status": "available",
        }

        # Test Robinhood connection
        try:
            if self.robinhood.auth.is_authenticated():
                status["robinhood_status"] = "authenticated"
            else:
                # Try to authenticate
                if self.robinhood.auth.login():
                    status["robinhood_status"] = "authenticated"
                else:
                    status["robinhood_status"] = "authentication_failed"
        except Exception as e:
            status["robinhood_status"] = f"error: {str(e)}"

        return status

    def logout(self):
        """Logout from all providers"""
        try:
            self.robinhood.logout()
        except Exception as e:
            logger.warning(f"Error logging out from Robinhood: {e}")
