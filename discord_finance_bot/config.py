import os
from dataclasses import dataclass
from typing import List, Optional


# Configuration container for bot runtime settings
@dataclass
class Config:
    discord_token: str
    channel_id: Optional[int]
    selected_stocks: List[str]
    timezone: str = "Asia/Shanghai"


def load_config() -> Config:
    """Load configuration from environment variables.

    Environment variables:
    - DISCORD_TOKEN: Discord bot token
    - DISCORD_CHANNEL_ID: Channel ID to which scheduler posts (optional)
    - SELECTED_STOCKS: Comma-separated stock tickers, e.g., "AAPL,MSFT,GOOGL"
    - TIMEZONE: IANA time zone for scheduler, e.g., "Asia/Shanghai"
    """
    token = os.getenv("DISCORD_TOKEN", "")
    channel_id_env = os.getenv("DISCORD_CHANNEL_ID")
    stocks_env = os.getenv("SELECTED_STOCKS", "AAPL,MSFT,GOOGL")
    tz_env = os.getenv("TIMEZONE", "Asia/Shanghai")

    channel_id = int(channel_id_env) if channel_id_env else None
    selected_stocks = [s.strip() for s in stocks_env.split(",") if s.strip()]

    return Config(
        discord_token=token,
        channel_id=channel_id,
        selected_stocks=selected_stocks,
        timezone=tz_env,
    )