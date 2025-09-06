#!/usr/bin/env python3

import logging
import time
from typing import Any, Dict, List, Optional

import robin_stocks.robinhood as rh

from ..auth.robinhood_auth import RobinhoodAuth

logger = logging.getLogger(__name__)


class RobinhoodOptionsProvider:
    def __init__(self):
        self.auth = RobinhoodAuth()
        self._authenticated = False

    def _ensure_authenticated(self):
        """Ensure we're authenticated before making API calls - with session persistence"""
        # Check if we already have an active session
        if hasattr(self.auth, "session_active") and self.auth.session_active:
            self._authenticated = True
            return

        # Only login if not authenticated
        if not self._authenticated:
            logger.info("🔐 Authenticating with Robinhood...")
            success = self.auth.login()
            if not success:
                raise Exception("Failed to authenticate with Robinhood")
            self._authenticated = True
            logger.info("✅ Robinhood authentication successful")

    def _format_options_data(self, options_data: List[Dict]) -> List[Dict]:
        """Format Robinhood options data to standard format"""
        formatted_options = []

        for option in options_data:
            try:
                formatted_option = {
                    "symbol": option.get("chain_symbol", ""),
                    "strike": float(option.get("strike_price", 0)),
                    "expiration": option.get("expiration_date", ""),
                    "option_type": option.get("type", ""),
                    "bid": (
                        float(option.get("bid_price", 0))
                        if option.get("bid_price")
                        else None
                    ),
                    "ask": (
                        float(option.get("ask_price", 0))
                        if option.get("ask_price")
                        else None
                    ),
                    "last_price": (
                        float(option.get("previous_close_price", 0))
                        if option.get("previous_close_price")
                        else None
                    ),
                    "volume": (
                        int(option.get("volume", 0)) if option.get("volume") else 0
                    ),
                    "open_interest": (
                        int(option.get("open_interest", 0))
                        if option.get("open_interest")
                        else 0
                    ),
                    "implied_volatility": (
                        float(option.get("implied_volatility", 0))
                        if option.get("implied_volatility")
                        else None
                    ),
                    "delta": (
                        float(option.get("delta", 0)) if option.get("delta") else None
                    ),
                    "gamma": (
                        float(option.get("gamma", 0)) if option.get("gamma") else None
                    ),
                    "theta": (
                        float(option.get("theta", 0)) if option.get("theta") else None
                    ),
                    "vega": (
                        float(option.get("vega", 0)) if option.get("vega") else None
                    ),
                    "rho": float(option.get("rho", 0)) if option.get("rho") else None,
                    "mark_price": (
                        float(option.get("adjusted_mark_price", 0))
                        if option.get("adjusted_mark_price")
                        else None
                    ),
                    "provider": "robinhood",
                    "option_id": option.get("id", ""),
                    "tradeable": option.get("tradeable", False),
                }
                formatted_options.append(formatted_option)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error formatting option data: {e}")
                continue

        return formatted_options

    def get_options_chain(
        self,
        symbol: str,
        expiration: Optional[str] = None,
        max_expirations: int = 10,
        raw_data: bool = False,
        include_greeks: bool = True,
    ) -> Dict[str, Any]:
        """Get complete options chain for a symbol"""
        try:
            self._ensure_authenticated()

            symbol = symbol.upper().strip()
            logger.info(
                f"Fetching options chain for {symbol} (raw_data={raw_data}, greeks={include_greeks})"
            )

            # Get basic chain info
            logger.info(f"📋 Getting options chain info for {symbol}")
            chain_info = rh.options.get_chains(symbol)
            if not chain_info:
                return {
                    "error": f"No options chain found for {symbol}",
                    "provider": "robinhood",
                }

            # Get tradable options with timing
            logger.info(
                f"🔍 Fetching tradable options for {symbol} (this may take time for large chains)"
            )
            options_start = time.time()

            if expiration:
                options_data = rh.options.find_tradable_options(
                    symbol, expirationDate=expiration, info=None
                )
            else:
                options_data = rh.options.find_tradable_options(symbol, info=None)

            options_elapsed = time.time() - options_start

            if not options_data:
                return {
                    "error": f"No tradable options found for {symbol}",
                    "provider": "robinhood",
                }

            logger.info(
                f"✅ Retrieved {len(options_data)} raw options in {options_elapsed:.2f}s"
            )

            # Format options data with parallel processing for large datasets
            logger.info(f"🔄 Formatting {len(options_data)} options data")
            format_start = time.time()

            if len(options_data) > 100:
                # Use parallel processing for large datasets
                formatted_options = self._format_options_parallel(options_data)
            else:
                # Use sequential for small datasets
                formatted_options = self._format_options_data(options_data)

            format_elapsed = time.time() - format_start
            logger.info(f"✅ Formatted options in {format_elapsed:.2f}s")

            # Enhance with Greeks if requested
            if include_greeks:
                formatted_options = self._enhance_with_greeks(formatted_options)

            # If raw data requested, return everything
            if raw_data:
                calls = [
                    opt for opt in formatted_options if opt["option_type"] == "call"
                ]
                puts = [opt for opt in formatted_options if opt["option_type"] == "put"]
                calls.sort(key=lambda x: x["strike"])
                puts.sort(key=lambda x: x["strike"])

                return {
                    "symbol": symbol,
                    "provider": "robinhood",
                    "chain_info": (
                        chain_info[0] if isinstance(chain_info, list) else chain_info
                    ),
                    "calls": calls,
                    "puts": puts,
                    "total_options": len(formatted_options),
                    "expiration_filter": expiration,
                    "raw_data": True,
                    "greeks_included": include_greeks,
                }

            # Default: Summarized data
            return self._summarize_options_chain(
                formatted_options, symbol, expiration, max_expirations, include_greeks
            )

        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            return {"error": str(e), "provider": "robinhood"}

    def _enhance_with_greeks(self, options_data: List[Dict]) -> List[Dict]:
        """Enhance options data with Greeks from market data - OPTIMIZED PARALLEL"""
        import concurrent.futures
        import time

        total_options = len(options_data)
        logger.info(
            f"🔢 Fetching Greeks for {total_options} filtered options (parallel processing)"
        )
        start_time = time.time()

        def fetch_single_greek(option):
            """Fetch Greeks for a single option with rate limiting"""
            try:
                market_data = rh.options.get_option_market_data_by_id(option["id"])
                if market_data and len(market_data) > 0:
                    return {**option, **market_data[0]}
                else:
                    return option
            except Exception as e:
                logger.warning(
                    f"Failed to get market data for option {option.get('id')}: {e}"
                )
                return option

        # Use fewer workers to avoid rate limiting (4 instead of 8)
        max_workers = min(4, total_options)
        logger.info(f"⚡ Using {max_workers} parallel workers for Greeks API calls")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            enhanced_options = list(executor.map(fetch_single_greek, options_data))

        elapsed = time.time() - start_time

        # Count successful Greeks
        greeks_count = sum(1 for opt in enhanced_options if "delta" in opt)
        success_rate = (greeks_count / total_options * 100) if total_options > 0 else 0

        logger.info(
            f"✅ Greeks enhancement complete: {greeks_count}/{total_options} options ({success_rate:.1f}%) in {elapsed:.2f}s"
        )
        logger.info(
            f"📊 Performance: {total_options/elapsed:.1f} options/sec with {max_workers} workers"
        )

        return enhanced_options

    def _format_options_parallel(self, options_data: List[Dict]) -> List[Dict]:
        """Format options data using parallel processing for large datasets"""
        import concurrent.futures

        def format_single_option(option):
            """Format a single option"""
            try:
                return {
                    "id": option.get("id"),
                    "symbol": option.get("chain_symbol"),
                    "strike": float(option.get("strike_price", 0)),
                    "expiration": option.get("expiration_date"),
                    "option_type": option.get("type"),
                    "bid_price": float(option.get("bid_price") or 0),
                    "ask_price": float(option.get("ask_price") or 0),
                    "last_trade_price": float(option.get("last_trade_price") or 0),
                    "volume": int(option.get("volume") or 0),
                    "open_interest": int(option.get("open_interest") or 0),
                    "implied_volatility": float(option.get("implied_volatility") or 0),
                    "updated_at": option.get("updated_at"),
                }
            except (ValueError, TypeError) as e:
                logger.warning(f"Error formatting option {option.get('id')}: {e}")
                return None

        # Use parallel processing with optimal worker count
        max_workers = min(
            8, len(options_data) // 50 + 1
        )  # 1 worker per 50 options, max 8

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            formatted_options = list(executor.map(format_single_option, options_data))

        # Filter out None results
        return [opt for opt in formatted_options if opt is not None]

    def _summarize_options_chain(
        self,
        options_data: List[Dict],
        symbol: str,
        expiration_filter: Optional[str],
        max_expirations: int,
        greeks_included: bool = True,
    ) -> Dict[str, Any]:
        """Professional-grade options chain optimization focusing on tradeable options"""

        # Get current stock price for ATM calculation
        current_price = self._get_current_stock_price(symbol)

        # Group by expiration
        expirations_data = {}
        for option in options_data:
            exp_date = option["expiration"]
            if exp_date not in expirations_data:
                expirations_data[exp_date] = {"calls": [], "puts": []}

            if option["option_type"] == "call":
                expirations_data[exp_date]["calls"].append(option)
            else:
                expirations_data[exp_date]["puts"].append(option)

        # Sort expirations by date (nearest first)
        sorted_expirations = sorted(expirations_data.keys())

        # Limit expirations if not filtering by specific date
        if not expiration_filter:
            sorted_expirations = sorted_expirations[:max_expirations]

        # Professional filtering for each expiration
        summarized_expirations = {}
        total_options_before = len(options_data)
        total_options_after = 0

        for exp_date in sorted_expirations:
            exp_data = expirations_data[exp_date]

            # Professional filtering: Focus on ATM and near-money strikes
            filtered_calls = self._filter_professional_options(
                exp_data["calls"], current_price, "call"
            )
            filtered_puts = self._filter_professional_options(
                exp_data["puts"], current_price, "put"
            )

            if filtered_calls or filtered_puts:
                summarized_expirations[exp_date] = {
                    "calls": filtered_calls,
                    "puts": filtered_puts,
                    "total_calls": len(filtered_calls),
                    "total_puts": len(filtered_puts),
                    "atm_call_strike": self._find_atm_strike(
                        filtered_calls, current_price
                    ),
                    "atm_put_strike": self._find_atm_strike(
                        filtered_puts, current_price
                    ),
                }

                total_options_after += len(filtered_calls) + len(filtered_puts)

        # Create professional optimization summary
        optimization_summary = {
            "total_expirations_available": len(expirations_data),
            "expirations_returned": len(summarized_expirations),
            "total_options_before_filter": total_options_before,
            "total_options_after_filter": total_options_after,
            "reduction_percentage": (
                round((1 - total_options_after / total_options_before) * 100, 1)
                if total_options_before > 0
                else 0
            ),
            "filter_criteria": "Professional: ATM ±3 strikes, volume>0 OR OI>10 OR tight spreads",
            "current_stock_price": current_price,
            "focus": "Liquid, near-money options for active trading",
        }

        result = {
            "symbol": symbol,
            "provider": "robinhood",
            "expirations": summarized_expirations,
            "optimization_summary": optimization_summary,
            "expiration_filter": expiration_filter,
            "raw_data": False,
            "greeks_included": greeks_included,
        }

        logger.info(
            f"Professional filter: {total_options_before} -> {total_options_after} options "
            f"({optimization_summary['reduction_percentage']}% reduction)"
        )

        return result

    def _get_current_stock_price(self, symbol: str) -> float:
        """Get current stock price for ATM calculations"""
        try:
            import robin_stocks.robinhood as rh

            quote = rh.stocks.get_latest_price(symbol)
            if quote and len(quote) > 0:
                return float(quote[0])
        except Exception as e:
            logger.warning(f"Could not get current price for {symbol}: {e}")
        return 0.0

    def _filter_professional_options(
        self, options: List[Dict], current_price: float, option_type: str
    ) -> List[Dict]:
        """Filter options like a professional trader"""
        if not options or current_price <= 0:
            return options[:10]  # Fallback to first 10

        # Sort by strike price
        options.sort(key=lambda x: x["strike"])

        # Find ATM strike (closest to current price)
        atm_strike = min(options, key=lambda x: abs(x["strike"] - current_price))[
            "strike"
        ]

        # Professional criteria
        professional_options = []

        for option in options:
            strike = option["strike"]

            # Focus on ATM ±3 strikes (professional sweet spot)
            if option_type == "call":
                strike_range = abs(strike - atm_strike) <= (
                    current_price * 0.15
                )  # ±15% range
            else:
                strike_range = abs(strike - atm_strike) <= (current_price * 0.15)

            # Professional liquidity criteria
            volume = option.get("volume", 0)
            open_interest = option.get("open_interest", 0)
            bid = option.get("bid")
            ask = option.get("ask")

            # High-quality options criteria
            is_liquid = (
                volume > 0  # Has recent trading
                or open_interest > 10  # Decent open interest
                or (
                    bid is not None and ask is not None and bid > 0
                )  # Has market makers
            )

            if strike_range and is_liquid:
                professional_options.append(option)

        # If too few, add more near-money strikes
        if len(professional_options) < 5:
            # Add more strikes around ATM
            for option in options:
                if len(professional_options) >= 10:
                    break
                if option not in professional_options:
                    if abs(option["strike"] - atm_strike) <= (
                        current_price * 0.25
                    ):  # ±25% range
                        professional_options.append(option)

        # Sort by distance from ATM (closest first)
        professional_options.sort(key=lambda x: abs(x["strike"] - atm_strike))

        return professional_options[:8]  # Max 8 strikes per type per expiration

    def _find_atm_strike(
        self, options: List[Dict], current_price: float
    ) -> Optional[float]:
        """Find the ATM (at-the-money) strike price"""
        if not options or current_price <= 0:
            return None

        atm_option = min(options, key=lambda x: abs(x["strike"] - current_price))
        return atm_option["strike"]

    def get_option_greeks(
        self, symbol: str, strike: float, expiration: str, option_type: str
    ) -> Dict[str, Any]:
        """Get Greeks for a specific option"""
        try:
            self._ensure_authenticated()

            symbol = symbol.upper().strip()
            option_type = option_type.lower().strip()

            logger.info(
                f"Fetching Greeks for {symbol} {strike} {expiration} {option_type}"
            )

            # Find the specific option
            options_data = rh.options.find_tradable_options(
                symbol,
                expirationDate=expiration,
                strikePrice=str(strike),
                optionType=option_type,
                info=None,
            )

            if not options_data:
                return {
                    "error": f"Option not found: {symbol} {strike} {expiration} {option_type}",
                    "provider": "robinhood",
                }

            option = options_data[0]

            # Get market data with Greeks
            market_data = rh.options.get_option_market_data_by_id(option["id"])
            if not market_data or len(market_data) == 0:
                return {
                    "error": "No market data available for option",
                    "provider": "robinhood",
                }

            # Merge and format
            enhanced_option = {**option, **market_data[0]}
            formatted_options = self._format_options_data([enhanced_option])

            if formatted_options:
                option_data = formatted_options[0]

                # Extract Greeks specifically
                greeks = {
                    "delta": option_data.get("delta"),
                    "gamma": option_data.get("gamma"),
                    "theta": option_data.get("theta"),
                    "vega": option_data.get("vega"),
                    "rho": option_data.get("rho"),
                    "implied_volatility": option_data.get("implied_volatility"),
                }

                return {
                    "provider": "robinhood",
                    "symbol": symbol,
                    "strike": strike,
                    "expiration": expiration,
                    "option_type": option_type,
                    "greeks": greeks,
                    "market_data": {
                        "bid": option_data.get("bid"),
                        "ask": option_data.get("ask"),
                        "last_price": option_data.get("last_price"),
                        "mark_price": option_data.get("mark_price"),
                        "volume": option_data.get("volume"),
                        "open_interest": option_data.get("open_interest"),
                    },
                    "option": option_data,
                }
            else:
                return {
                    "error": "Failed to format option data",
                    "provider": "robinhood",
                }

        except Exception as e:
            logger.error(
                f"Error fetching Greeks for {symbol} {strike} {expiration} {option_type}: {e}"
            )
            return {"error": str(e), "provider": "robinhood"}

    def get_available_expirations(self, symbol: str) -> List[str]:
        """Get available expiration dates for a symbol"""
        try:
            self._ensure_authenticated()

            symbol = symbol.upper().strip()

            # Get all tradable options to extract expiration dates
            options_data = rh.options.find_tradable_options(symbol, info=None)

            if not options_data:
                return []

            # Extract unique expiration dates
            expirations = set()
            for option in options_data:
                exp_date = option.get("expiration_date")
                if exp_date:
                    expirations.add(exp_date)

            return sorted(list(expirations))

        except Exception as e:
            logger.error(f"Error fetching expirations for {symbol}: {e}")
            return []

    def logout(self):
        """Logout from Robinhood"""
        self.auth.logout()
        self._authenticated = False
