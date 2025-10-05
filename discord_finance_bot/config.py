import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Optional

# Load environment variables from a .env file if present
load_dotenv()


# Configuration container for bot runtime settings
@dataclass
class Config:
    discord_token: str
    channel_id: Optional[int]
    selected_stocks: List[str]
    timezone: str = "Asia/Shanghai"
    alphavantage_api_key: str = ""


def load_config() -> Config:
    """Load configuration from environment variables.

    Environment variables:
    - DISCORD_TOKEN: Discord bot token
    - DISCORD_CHANNEL_ID: Channel ID to which scheduler posts (optional)
    - SELECTED_STOCKS: Comma-separated stock tickers, e.g., "AAPL,MSFT,GOOGL"
    - TIMEZONE: IANA time zone for scheduler, e.g., "Asia/Shanghai"
    - ALPHAVANTAGE_API_KEY: API key for Alpha Vantage endpoints (optional)
    """
    token = os.getenv("DISCORD_TOKEN", "")
    channel_id_env = os.getenv("DISCORD_CHANNEL_ID")
    stocks_env = os.getenv("SELECTED_STOCKS", "AAPL,MSFT,GOOGL")
    tz_env = os.getenv("TIMEZONE", "Asia/Shanghai")
    av_key = os.getenv("ALPHAVANTAGE_API_KEY", "")

    channel_id = int(channel_id_env) if channel_id_env else None
    selected_stocks = [s.strip() for s in stocks_env.split(",") if s.strip()]

    return Config(
        discord_token=token,
        channel_id=channel_id,
        selected_stocks=selected_stocks,
        timezone=tz_env,
        alphavantage_api_key=av_key,
    )