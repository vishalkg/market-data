#!/usr/bin/env python3

import logging
from typing import Any, Dict
import robin_stocks.robinhood as rh
from datetime import datetime

from ..auth.robinhood_auth import RobinhoodAuth

logger = logging.getLogger(__name__)


class RobinhoodHistoricalProvider:
    """Robinhood historical data provider with unlimited rate limits"""
    
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
    
    async def get_historical_data(self, symbol: str, interval: str = "day", span: str = "year") -> Dict[str, Any]:
        """Get historical data from Robinhood (unlimited)
        
        Args:
            symbol: Stock ticker symbol
            interval: Data interval - '5minute', '10minute', '30minute', 'day', 'week'
            span: Time span - 'day', 'week', 'month', '3month', 'year', '5year'
        """
        await self.ensure_authenticated()
        
        try:
            # Get historical data from Robinhood
            historical_data = rh.get_stock_historicals(symbol, interval=interval, span=span)
            
            if not historical_data:
                raise Exception(f"No historical data returned for {symbol}")
            
            # Format data for consistency
            formatted_data = []
            for item in historical_data:
                formatted_item = {
                    "timestamp": item.get("begins_at"),
                    "open": float(item.get("open_price", 0)),
                    "high": float(item.get("high_price", 0)),
                    "low": float(item.get("low_price", 0)),
                    "close": float(item.get("close_price", 0)),
                    "volume": int(item.get("volume", 0))
                }
                formatted_data.append(formatted_item)
            
            return {
                "provider": "robinhood",
                "symbol": symbol,
                "interval": interval,
                "span": span,
                "data_points": len(formatted_data),
                "data": formatted_data,
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited"
            }
            
        except Exception as e:
            logger.error(f"Robinhood historical data failed for {symbol}: {e}")
            raise
    
    async def get_intraday_data(self, symbol: str, interval: str = "5minute") -> Dict[str, Any]:
        """Get intraday historical data (5min, 10min, 30min intervals)"""
        return await self.get_historical_data(symbol, interval=interval, span="day")
    
    async def get_daily_data(self, symbol: str, span: str = "year") -> Dict[str, Any]:
        """Get daily historical data"""
        return await self.get_historical_data(symbol, interval="day", span=span)
    
    async def get_weekly_data(self, symbol: str, span: str = "5year") -> Dict[str, Any]:
        """Get weekly historical data"""
        return await self.get_historical_data(symbol, interval="week", span=span)
    
    def get_supported_intervals(self) -> Dict[str, Any]:
        """Get supported intervals and spans"""
        return {
            "intervals": {
                "5minute": "5-minute bars",
                "10minute": "10-minute bars", 
                "hour": "Hourly bars",
                "day": "Daily bars",
                "week": "Weekly bars"
            },
            "spans": {
                "day": "1 day (intraday only)",
                "week": "1 week",
                "month": "1 month",
                "3month": "3 months",
                "year": "1 year",
                "5year": "5 years"
            },
            "combinations": [
                {"interval": "5minute", "spans": ["day"]},
                {"interval": "10minute", "spans": ["day", "week"]},
                {"interval": "hour", "spans": ["day", "week", "month"]},
                {"interval": "day", "spans": ["week", "month", "3month", "year", "5year"]},
                {"interval": "week", "spans": ["year", "5year"]}
            ]
        }
