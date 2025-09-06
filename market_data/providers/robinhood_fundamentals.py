#!/usr/bin/env python3

import logging
from typing import Any, Dict
import robin_stocks.robinhood as rh
from datetime import datetime

from ..auth.robinhood_auth import RobinhoodAuth

logger = logging.getLogger(__name__)


class RobinhoodFundamentalsProvider:
    """Robinhood fundamentals provider with unlimited rate limits"""
    
    def __init__(self):
        self.auth = RobinhoodAuth()
        self._authenticated = False
    
    async def ensure_authenticated(self):
        """Ensure Robinhood authentication is active"""
        if not self._authenticated:
            success = self.auth.login()
            if not success:
                raise Exception("Robinhood authentication failed")
            self._authenticated = True
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive fundamentals from Robinhood (unlimited)"""
        await self.ensure_authenticated()
        
        try:
            # Get basic fundamentals
            fundamentals_data = rh.get_fundamentals(symbol)
            
            if not fundamentals_data or not fundamentals_data[0]:
                raise Exception(f"No fundamentals data returned for {symbol}")
            
            fundamentals = fundamentals_data[0]
            
            # Get additional data
            earnings_data = rh.get_earnings(symbol)
            ratings_data = rh.get_ratings(symbol)
            
            # Format comprehensive response
            result = {
                "provider": "robinhood",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited",
                "data": {
                    "fundamentals": {
                        "market_cap": fundamentals.get("market_cap"),
                        "pe_ratio": fundamentals.get("pe_ratio"),
                        "pb_ratio": fundamentals.get("pb_ratio"),
                        "dividend_yield": fundamentals.get("dividend_yield"),
                        "high_52_weeks": fundamentals.get("high_52_weeks"),
                        "low_52_weeks": fundamentals.get("low_52_weeks"),
                        "average_volume": fundamentals.get("average_volume"),
                        "shares_outstanding": fundamentals.get("shares_outstanding"),
                        "float": fundamentals.get("float"),
                        "description": fundamentals.get("description"),
                        "sector": fundamentals.get("sector"),
                        "industry": fundamentals.get("industry"),
                        "ceo": fundamentals.get("ceo"),
                        "headquarters_city": fundamentals.get("headquarters_city"),
                        "headquarters_state": fundamentals.get("headquarters_state"),
                        "num_employees": fundamentals.get("num_employees"),
                        "year_founded": fundamentals.get("year_founded")
                    }
                }
            }
            
            # Add earnings data if available
            if earnings_data:
                result["data"]["earnings"] = {
                    "recent_earnings": earnings_data[:4] if len(earnings_data) >= 4 else earnings_data,
                    "total_quarters": len(earnings_data)
                }
            
            # Add ratings data if available
            if ratings_data:
                result["data"]["analyst_ratings"] = {
                    "ratings_summary": ratings_data.get("summary", {}),
                    "ratings_count": len(ratings_data.get("ratings", [])),
                    "recent_ratings": ratings_data.get("ratings", [])[:5]  # Last 5 ratings
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Robinhood fundamentals failed for {symbol}: {e}")
            raise
    
    async def get_earnings_data(self, symbol: str) -> Dict[str, Any]:
        """Get detailed earnings data from Robinhood"""
        await self.ensure_authenticated()
        
        try:
            earnings_data = rh.get_earnings(symbol)
            
            if not earnings_data:
                raise Exception(f"No earnings data returned for {symbol}")
            
            return {
                "provider": "robinhood",
                "symbol": symbol,
                "data": {
                    "earnings": earnings_data,
                    "quarters_available": len(earnings_data)
                },
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited"
            }
            
        except Exception as e:
            logger.error(f"Robinhood earnings failed for {symbol}: {e}")
            raise
    
    async def get_analyst_ratings(self, symbol: str) -> Dict[str, Any]:
        """Get analyst ratings from Robinhood"""
        await self.ensure_authenticated()
        
        try:
            ratings_data = rh.get_ratings(symbol)
            
            if not ratings_data:
                raise Exception(f"No ratings data returned for {symbol}")
            
            return {
                "provider": "robinhood",
                "symbol": symbol,
                "data": {
                    "ratings": ratings_data,
                    "summary": ratings_data.get("summary", {}),
                    "ratings_count": len(ratings_data.get("ratings", []))
                },
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited"
            }
            
        except Exception as e:
            logger.error(f"Robinhood ratings failed for {symbol}: {e}")
            raise
