#!/usr/bin/env python3

import logging
from typing import Any, Dict, List, Optional
import robin_stocks.robinhood as rh
from datetime import datetime

from ..auth.robinhood_auth import RobinhoodAuth

logger = logging.getLogger(__name__)


class RobinhoodStockProvider:
    """Robinhood stock data provider with unlimited rate limits"""
    
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
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote from Robinhood (unlimited)"""
        await self.ensure_authenticated()
        
        try:
            # Get quote data from Robinhood
            quote_data = rh.get_quotes(symbol)
            
            if not quote_data or not quote_data[0]:
                raise Exception(f"No quote data returned for {symbol}")
            
            quote = quote_data[0]
            
            # Format to match existing interface
            formatted_quote = {
                "c": float(quote.get("last_trade_price", 0)),  # current price
                "h": float(quote.get("high", 0)),  # high
                "l": float(quote.get("low", 0)),   # low
                "o": float(quote.get("open", 0)),  # open
                "pc": float(quote.get("previous_close", 0)),  # previous close
                "t": int(datetime.now().timestamp()),  # timestamp
            }
            
            # Calculate percentage change
            if formatted_quote["pc"] > 0:
                change = formatted_quote["c"] - formatted_quote["pc"]
                formatted_quote["dp"] = round((change / formatted_quote["pc"]) * 100, 2)
                formatted_quote["d"] = round(change, 2)
            else:
                formatted_quote["dp"] = 0
                formatted_quote["d"] = 0
            
            return {
                "provider": "robinhood",
                "symbol": symbol,
                "data": formatted_quote,
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited"
            }
            
        except Exception as e:
            logger.error(f"Robinhood stock quote failed for {symbol}: {e}")
            raise
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get multiple stock quotes in single request (major advantage over Finnhub)"""
        await self.ensure_authenticated()
        
        try:
            # Robinhood can handle multiple symbols in one call
            quotes_data = rh.get_quotes(symbols)
            
            if not quotes_data:
                raise Exception(f"No quote data returned for symbols: {symbols}")
            
            results = {}
            for i, quote in enumerate(quotes_data):
                if quote and i < len(symbols):
                    symbol = symbols[i]
                    
                    formatted_quote = {
                        "c": float(quote.get("last_trade_price", 0)),
                        "h": float(quote.get("high", 0)),
                        "l": float(quote.get("low", 0)),
                        "o": float(quote.get("open", 0)),
                        "pc": float(quote.get("previous_close", 0)),
                        "t": int(datetime.now().timestamp()),
                    }
                    
                    # Calculate percentage change
                    if formatted_quote["pc"] > 0:
                        change = formatted_quote["c"] - formatted_quote["pc"]
                        formatted_quote["dp"] = round((change / formatted_quote["pc"]) * 100, 2)
                        formatted_quote["d"] = round(change, 2)
                    else:
                        formatted_quote["dp"] = 0
                        formatted_quote["d"] = 0
                    
                    results[symbol] = formatted_quote
            
            return {
                "provider": "robinhood",
                "data": results,
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited",
                "batch_size": len(symbols)
            }
            
        except Exception as e:
            logger.error(f"Robinhood batch quotes failed for {symbols}: {e}")
            raise
