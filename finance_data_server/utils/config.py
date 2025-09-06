"""Secure configuration loader for API keys"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class ProviderType(Enum):
    FINNHUB = "finnhub"
    ALPHA_VANTAGE = "alpha_vantage"
    FMP = "fmp"
    POLYGON = "polygon"


@dataclass
class APIKey:
    provider: ProviderType
    key: str
    requests_per_minute: int
    requests_per_day: int
    requests_minute: int = 0
    requests_day: int = 0


def load_api_keys() -> Dict[ProviderType, List[APIKey]]:
    """Load API keys from environment variables"""

    # Load .env file if it exists
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    return {
        ProviderType.FINNHUB: [
            APIKey(ProviderType.FINNHUB, os.getenv("FINNHUB_KEY_1", "demo"), 60, 1000),
            APIKey(ProviderType.FINNHUB, os.getenv("FINNHUB_KEY_2", "demo"), 60, 1000),
            APIKey(ProviderType.FINNHUB, os.getenv("FINNHUB_KEY_3", "demo"), 60, 1000),
        ],
        ProviderType.ALPHA_VANTAGE: [
            APIKey(
                ProviderType.ALPHA_VANTAGE,
                os.getenv("ALPHA_VANTAGE_KEY_1", "demo"),
                5,
                500,
            ),
            APIKey(
                ProviderType.ALPHA_VANTAGE,
                os.getenv("ALPHA_VANTAGE_KEY_2", "demo"),
                5,
                500,
            ),
            APIKey(
                ProviderType.ALPHA_VANTAGE,
                os.getenv("ALPHA_VANTAGE_KEY_3", "demo"),
                5,
                500,
            ),
        ],
        ProviderType.FMP: [
            APIKey(ProviderType.FMP, os.getenv("FMP_API_KEY", "demo"), 250, 250),
        ],
        ProviderType.POLYGON: [
            APIKey(ProviderType.POLYGON, os.getenv("POLYGON_API_KEY", "demo"), 5, 1000),
        ],
    }
