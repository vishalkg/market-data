#!/usr/bin/env python3

import logging
from typing import Any, Dict, List, Optional
import robin_stocks.robinhood as rh
from datetime import datetime, timedelta

from .base_provider import BaseProvider, ProviderCapability
from ..auth.robinhood_auth import RobinhoodAuth
from ..utils.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)


class RobinhoodProvider(BaseProvider):
    """Consolidated Robinhood provider with unlimited rate limits"""
    
    # Authentication refresh settings
    AUTH_TIMEOUT_HOURS = 23  # Re-authenticate before 24-hour token expiry
    MAX_AUTH_RETRIES = 3
    
    def __init__(self):
        self.auth = RobinhoodAuth()
        self._authenticated = False
        self._auth_timestamp = None
        self._auth_retry_count = 0
        self.rate_limiter = get_rate_limiter()
    
    @property
    def name(self) -> str:
        return "robinhood"
    
    def get_capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.REAL_TIME_QUOTES,
            ProviderCapability.BATCH_QUOTES,
            ProviderCapability.OPTIONS_CHAIN,
            ProviderCapability.FUNDAMENTALS,
            ProviderCapability.HISTORICAL_DATA,
            ProviderCapability.UNLIMITED_RATE
        ]
    
    async def health_check(self) -> bool:
        """Check if Robinhood authentication is working"""
        try:
            await self.ensure_authenticated()
            return True
        except Exception:
            return False
    
    def _is_auth_expired(self) -> bool:
        """Check if authentication token has expired"""
        if not self._auth_timestamp:
            return True
        
        elapsed = datetime.now() - self._auth_timestamp
        return elapsed > timedelta(hours=self.AUTH_TIMEOUT_HOURS)
    
    async def ensure_authenticated(self):
        """Ensure Robinhood authentication is active with automatic refresh"""
        # Check if we need to authenticate or refresh
        if not self._authenticated or self._is_auth_expired():
            await self._authenticate_with_retry()
    
    async def _authenticate_with_retry(self):
        """Authenticate with retry logic"""
        for attempt in range(self.MAX_AUTH_RETRIES):
            try:
                success = self.auth.login()
                if success:
                    self._authenticated = True
                    self._auth_timestamp = datetime.now()
                    self._auth_retry_count = 0
                    logger.info("Robinhood authentication successful")
                    return
                else:
                    logger.warning(f"Robinhood authentication attempt {attempt + 1} failed")
            except Exception as e:
                logger.error(f"Robinhood authentication error on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_AUTH_RETRIES - 1:
                    # Wait before retry (exponential backoff)
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
        
        # All retries failed
        self._authenticated = False
        self._auth_timestamp = None
        raise Exception(f"Robinhood authentication failed after {self.MAX_AUTH_RETRIES} attempts")
    
    async def cleanup_session(self):
        """Cleanup authentication session on failures"""
        try:
            rh.logout()
            logger.info("Robinhood session cleaned up")
        except Exception as e:
            logger.warning(f"Error during session cleanup: {e}")
        finally:
            self._authenticated = False
            self._auth_timestamp = None
            self._auth_retry_count = 0
    
    # Stock data methods
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote from Robinhood"""
        # Acquire rate limit permission
        if not await self.rate_limiter.acquire(self.name):
            raise Exception(f"Rate limit timeout for {self.name}")
        
        await self.ensure_authenticated()
        
        try:
            quote_data = rh.get_quotes(symbol)
            
            if not quote_data or not quote_data[0]:
                raise Exception(f"No quote data returned for {symbol}")
            
            quote = quote_data[0]
            
            formatted_quote = {
                "c": float(quote.get("last_trade_price", 0)),
                "h": float(quote.get("high", 0)),
                "l": float(quote.get("low", 0)),
                "o": float(quote.get("open", 0)),
                "pc": float(quote.get("previous_close", 0)),
                "t": int(datetime.now().timestamp()),
            }
            
            if formatted_quote["pc"] > 0:
                change = formatted_quote["c"] - formatted_quote["pc"]
                formatted_quote["dp"] = round((change / formatted_quote["pc"]) * 100, 2)
                formatted_quote["d"] = round(change, 2)
            else:
                formatted_quote["dp"] = 0
                formatted_quote["d"] = 0
            
            return {
                "symbol": symbol,
                "data": formatted_quote,
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited"
            }
            
        except Exception as e:
            logger.error(f"Robinhood stock quote failed for {symbol}: {e}")
            # Check if it's an auth error and cleanup
            if "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
                await self.cleanup_session()
            raise
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get multiple stock quotes in single request"""
        # Acquire rate limit permission
        if not await self.rate_limiter.acquire(self.name):
            raise Exception(f"Rate limit timeout for {self.name}")
        
        await self.ensure_authenticated()
        
        try:
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
                    
                    if formatted_quote["pc"] > 0:
                        change = formatted_quote["c"] - formatted_quote["pc"]
                        formatted_quote["dp"] = round((change / formatted_quote["pc"]) * 100, 2)
                        formatted_quote["d"] = round(change, 2)
                    else:
                        formatted_quote["dp"] = 0
                        formatted_quote["d"] = 0
                    
                    results[symbol] = formatted_quote
            
            return {
                "data": results,
                "timestamp": datetime.now().isoformat(),
                "rate_limit": "unlimited",
                "batch_size": len(symbols)
            }
            
        except Exception as e:
            logger.error(f"Robinhood batch quotes failed for {symbols}: {e}")
            raise
    
    # Options data methods
    async def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """Get options chain from Robinhood"""
        await self.ensure_authenticated()
        
        try:
            options_data = rh.options.get_chains(symbol)
            
            if not options_data:
                raise Exception(f"No options data available for {symbol}")
            
            return {
                "symbol": symbol,
                "data": {
                    "options": options_data,
                    "note": "Comprehensive options data from Robinhood"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Robinhood options chain failed for {symbol}: {e}")
            raise
    
    # Fundamentals data methods
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get company fundamentals from Robinhood"""
        await self.ensure_authenticated()
        
        try:
            fundamentals = rh.stocks.get_fundamentals(symbol)
            
            if not fundamentals or not fundamentals[0]:
                raise Exception(f"No fundamentals data for {symbol}")
            
            fund_data = fundamentals[0]
            
            formatted_data = {
                "market_cap": fund_data.get("market_cap"),
                "pe_ratio": fund_data.get("pe_ratio"),
                "dividend_yield": fund_data.get("dividend_yield"),
                "average_volume": fund_data.get("average_volume"),
                "average_volume_2_weeks": fund_data.get("average_volume_2_weeks"),
                "fifty_two_week_high": fund_data.get("high_52_weeks"),
                "fifty_two_week_low": fund_data.get("low_52_weeks"),
                "open": fund_data.get("open"),
                "high": fund_data.get("high"),
                "low": fund_data.get("low"),
                "volume": fund_data.get("volume"),
                "description": fund_data.get("description", "")
            }
            
            return {
                "symbol": symbol,
                "data": formatted_data,
                "timestamp": datetime.now().isoformat(),
                "source": "robinhood_fundamentals"
            }
            
        except Exception as e:
            logger.error(f"Robinhood fundamentals failed for {symbol}: {e}")
            raise
    
    # Historical data methods
    async def get_historical_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get historical price data from Robinhood"""
        await self.ensure_authenticated()
        
        try:
            # Map period to Robinhood format
            span_map = {
                "1d": "day",
                "1w": "week", 
                "1m": "month",
                "3m": "3month",
                "1y": "year",
                "5y": "5year"
            }
            
            span = span_map.get(period, "year")
            interval = "day" if span in ["month", "3month", "year", "5year"] else "5minute"
            
            historical_data = rh.stocks.get_stock_historicals(symbol, interval=interval, span=span)
            
            if not historical_data:
                raise Exception(f"No historical data for {symbol}")
            
            return {
                "symbol": symbol,
                "data": historical_data,
                "period": period,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Robinhood historical data failed for {symbol}: {e}")
            raise
    
    # Technical indicators - Not supported by Robinhood directly
    async def get_rsi(self, symbol: str, period: int = 14) -> Dict[str, Any]:
        """RSI not supported by Robinhood"""
        raise NotImplementedError("RSI not available from Robinhood")
    
    async def get_macd(self, symbol: str) -> Dict[str, Any]:
        """MACD not supported by Robinhood"""
        raise NotImplementedError("MACD not available from Robinhood")
    
    async def get_bollinger_bands(self, symbol: str, period: int = 20) -> Dict[str, Any]:
        """Bollinger Bands not supported by Robinhood"""
        raise NotImplementedError("Bollinger Bands not available from Robinhood")
