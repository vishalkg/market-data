#!/usr/bin/env python3

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DataOptimizer:
    @staticmethod
    def optimize_options_data(raw_data: Dict, max_expirations: int = 10) -> Dict:
        """Optimize options chain data using professional trading criteria"""
        if not isinstance(raw_data, dict) or "data" not in raw_data:
            return raw_data

        contracts = raw_data.get("data", [])
        if not contracts:
            return raw_data

        current_price = raw_data.get("lastTradePrice", 0)
        if not current_price:
            return raw_data

        # Process each expiration date
        optimized_expirations = {}
        total_original = 0

        for contract in contracts:
            exp_date = contract.get("expirationDate")
            if not exp_date:
                continue

            calls = contract.get("options", {}).get("CALL", [])
            puts = contract.get("options", {}).get("PUT", [])
            total_original += len(calls) + len(puts)

            # Filter calls and puts by professional criteria
            filtered_calls = []
            filtered_puts = []

            for call in calls:
                strike = call.get("strike", 0)
                volume = call.get("volume", 0)
                oi = call.get("openInterest", 0)

                # Professional filters
                moneyness = abs(strike - current_price) / current_price * 100
                has_liquidity = volume > 10 or oi > 100
                is_relevant = moneyness <= 15  # Within 15% of current price

                if has_liquidity and is_relevant:
                    filtered_calls.append(
                        {
                            "strike": strike,
                            "volume": volume,
                            "openInterest": oi,
                            "bid": call.get("bid"),
                            "ask": call.get("ask"),
                            "lastPrice": call.get("lastPrice"),
                            "impliedVolatility": call.get("impliedVolatility"),
                            "delta": call.get("delta"),
                            "moneyness": round(moneyness, 2),
                        }
                    )

            for put in puts:
                strike = put.get("strike", 0)
                volume = put.get("volume", 0)
                oi = put.get("openInterest", 0)

                moneyness = abs(strike - current_price) / current_price * 100
                has_liquidity = volume > 10 or oi > 100
                is_relevant = moneyness <= 15

                if has_liquidity and is_relevant:
                    filtered_puts.append(
                        {
                            "strike": strike,
                            "volume": volume,
                            "openInterest": oi,
                            "bid": put.get("bid"),
                            "ask": put.get("ask"),
                            "lastPrice": put.get("lastPrice"),
                            "impliedVolatility": put.get("impliedVolatility"),
                            "delta": put.get("delta"),
                            "moneyness": round(moneyness, 2),
                        }
                    )

            # Only include expirations with significant activity
            total_volume = sum(
                c.get("volume", 0) for c in filtered_calls + filtered_puts
            )
            if total_volume > 50:  # Minimum volume threshold
                optimized_expirations[exp_date] = {
                    "calls": sorted(
                        filtered_calls, key=lambda x: x["volume"], reverse=True
                    )[:20],
                    "puts": sorted(
                        filtered_puts, key=lambda x: x["volume"], reverse=True
                    )[:20],
                    "total_volume": total_volume,
                }

        # Sort by volume and limit expirations
        sorted_expirations = dict(
            sorted(
                optimized_expirations.items(),
                key=lambda x: x[1]["total_volume"],
                reverse=True,
            )[:max_expirations]
        )

        total_optimized = sum(
            len(exp["calls"]) + len(exp["puts"]) for exp in sorted_expirations.values()
        )

        return {
            "provider": raw_data.get("provider"),
            "data": {
                "expirations": sorted_expirations,
                "optimization_summary": {
                    "original_contracts": total_original,
                    "optimized_contracts": total_optimized,
                    "reduction_percentage": round(
                        (
                            (1 - total_optimized / total_original) * 100
                            if total_original > 0
                            else 0
                        ),
                        1,
                    ),
                    "filter_criteria": {
                        "min_volume_or_oi": "volume > 10 OR openInterest > 100",
                        "moneyness_range": "±15% of current price",
                        "max_contracts_per_type": 20,
                        "max_expirations": max_expirations,
                        "min_expiration_volume": 50,
                    },
                },
            },
        }

    @staticmethod
    def optimize_rsi_data(raw_data: Dict, symbol: str, period: int) -> Dict:
        """Optimize RSI data for professional analysis"""
        if "data" not in raw_data:
            return raw_data

        time_series = raw_data["data"].get("Technical Analysis: RSI", {})
        if not time_series:
            return raw_data

        # Get recent values (last 5 periods for trend analysis)
        recent_values = []
        for date, data in sorted(time_series.items(), reverse=True)[:5]:
            try:
                rsi_value = float(data["RSI"])
                recent_values.append({"date": date, "rsi": rsi_value})
            except (KeyError, ValueError):
                continue

        if not recent_values:
            return raw_data

        latest = recent_values[0]
        latest_rsi = latest["rsi"]

        # Determine signal
        if latest_rsi >= 70:
            signal = "OVERBOUGHT"
        elif latest_rsi <= 30:
            signal = "OVERSOLD"
        elif latest_rsi > 50:
            signal = "BULLISH"
        else:
            signal = "BEARISH"

        # Trend analysis
        if len(recent_values) >= 3:
            trend_values = [v["rsi"] for v in recent_values[:3]]
            if all(
                trend_values[i] > trend_values[i + 1]
                for i in range(len(trend_values) - 1)
            ):
                trend = "RISING"
            elif all(
                trend_values[i] < trend_values[i + 1]
                for i in range(len(trend_values) - 1)
            ):
                trend = "FALLING"
            else:
                trend = "SIDEWAYS"
        else:
            trend = "INSUFFICIENT_DATA"

        return {
            "provider": raw_data.get("provider"),
            "data": raw_data["data"],
            "current_analysis": {
                "symbol": symbol,
                "period": period,
                "latest_rsi": latest_rsi,
                "signal": signal,
                "trend_direction": trend,
                "recent_values": recent_values,
            },
        }

    @staticmethod
    def optimize_macd_data(raw_data: Dict, symbol: str) -> Dict:
        """Optimize MACD data for professional analysis"""
        if "data" not in raw_data:
            return raw_data

        time_series = raw_data["data"].get("Technical Analysis: MACD", {})
        if not time_series:
            return raw_data

        # Get recent values for analysis
        recent_values = []
        for date, data in sorted(time_series.items(), reverse=True)[:5]:
            try:
                macd_value = float(data["MACD"])
                signal_value = float(data["MACD_Signal"])
                histogram = float(data["MACD_Hist"])
                recent_values.append(
                    {
                        "date": date,
                        "macd": macd_value,
                        "signal": signal_value,
                        "histogram": histogram,
                    }
                )
            except (KeyError, ValueError):
                continue

        if not recent_values:
            return raw_data

        latest = recent_values[0]

        # Determine crossover signals
        crossover_signal = "NEUTRAL"
        if len(recent_values) >= 2:
            current_diff = latest["macd"] - latest["signal"]
            previous_diff = recent_values[1]["macd"] - recent_values[1]["signal"]

            if current_diff > 0 and previous_diff <= 0:
                crossover_signal = "BULLISH_CROSSOVER"
            elif current_diff < 0 and previous_diff >= 0:
                crossover_signal = "BEARISH_CROSSOVER"
            elif current_diff > 0:
                crossover_signal = "BULLISH"
            else:
                crossover_signal = "BEARISH"

        # Histogram trend
        histogram_trend = "NEUTRAL"
        if len(recent_values) >= 3:
            hist_values = [v["histogram"] for v in recent_values[:3]]
            if all(
                hist_values[i] > hist_values[i + 1] for i in range(len(hist_values) - 1)
            ):
                histogram_trend = "STRENGTHENING"
            elif all(
                hist_values[i] < hist_values[i + 1] for i in range(len(hist_values) - 1)
            ):
                histogram_trend = "WEAKENING"

        return {
            "provider": raw_data.get("provider"),
            "data": raw_data["data"],
            "current_analysis": {
                "symbol": symbol,
                "latest_macd": latest["macd"],
                "latest_signal": latest["signal"],
                "latest_histogram": latest["histogram"],
                "crossover_signal": crossover_signal,
                "histogram_trend": histogram_trend,
                "recent_values": recent_values,
            },
        }

    @staticmethod
    def optimize_bollinger_data(raw_data: Dict, symbol: str, period: int) -> Dict:
        """Optimize Bollinger Bands data for professional analysis"""
        if "data" not in raw_data:
            return raw_data

        time_series = raw_data["data"].get("Technical Analysis: BBANDS", {})
        if not time_series:
            return raw_data

        # Get recent values
        recent_values = []
        for date, data in sorted(time_series.items(), reverse=True)[:5]:
            try:
                recent_values.append(
                    {
                        "date": date,
                        "upper_band": float(data["Real Upper Band"]),
                        "middle_band": float(data["Real Middle Band"]),
                        "lower_band": float(data["Real Lower Band"]),
                    }
                )
            except (KeyError, ValueError):
                continue

        if not recent_values:
            return raw_data

        latest = recent_values[0]

        # Determine squeeze condition
        squeeze_condition = "NORMAL"
        if len(recent_values) >= 5:
            band_widths = [
                (v["upper_band"] - v["lower_band"]) / v["middle_band"] * 100
                for v in recent_values
            ]
            avg_width = sum(band_widths) / len(band_widths)
            current_width = band_widths[0]

            if current_width < avg_width * 0.7:
                squeeze_condition = "SQUEEZE"
            elif current_width > avg_width * 1.3:
                squeeze_condition = "EXPANSION"

        # Band width trend
        width_trend = "STABLE"
        if len(recent_values) >= 3:
            widths = [
                (v["upper_band"] - v["lower_band"]) / v["middle_band"]
                for v in recent_values[:3]
            ]
            if widths[0] > widths[1] > widths[2]:
                width_trend = "EXPANDING"
            elif widths[0] < widths[1] < widths[2]:
                width_trend = "CONTRACTING"

        return {
            "provider": raw_data.get("provider"),
            "data": raw_data["data"],
            "current_analysis": {
                "symbol": symbol,
                "period": period,
                "latest_upper": latest["upper_band"],
                "latest_middle": latest["middle_band"],
                "latest_lower": latest["lower_band"],
                "squeeze_condition": squeeze_condition,
                "width_trend": width_trend,
                "recent_values": recent_values,
            },
        }
