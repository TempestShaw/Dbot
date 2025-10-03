from typing import List, Dict, Any
import yfinance as yf
from utils.logger import get_logger


class YahooRepo:
    """Yahoo Finance repository abstraction.

    Encapsulates calls to yfinance and any related parsing, providing
    simple, typed methods for services.
    """

    def __init__(self, config):
        self.logger = get_logger(__name__)
        self.config = config

    def fetch_macro_data(self) -> Dict[str, Any]:
        """Fetch macro data (placeholder implementation)."""
        # TODO: Replace with actual macro data retrieval via API or scraping
        return {"CPI": "3.2%", "PPI": "2.5%"}

    def fetch_market_news(self) -> List[str]:
        """Fetch market news headlines (placeholder)."""
        # TODO: Implement via yfinance news endpoint or web crawler
        return ["Powell: interest rates likely to remain unchanged"]

    def fetch_stocks(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Fetch latest quote for a list of tickers."""
        result = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="1d")
                if not hist.empty:
                    last = float(hist["Close"].iloc[-1])
                    result.append({"symbol": ticker, "last": last})
                else:
                    result.append({"symbol": ticker, "last": None})
            except Exception as exc:
                self.logger.exception(f"Failed to fetch ticker {ticker}: {exc}")
                result.append({"symbol": ticker, "last": None})
        return result

    def fetch_top_sectors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch top sectors by performance (placeholder)."""
        sectors = [
            {"name": "Technology", "change_pct": 1.8},
            {"name": "Healthcare", "change_pct": 1.2},
            {"name": "Energy", "change_pct": -0.3},
            {"name": "Financials", "change_pct": 0.7},
            {"name": "Consumer Staples", "change_pct": 0.5},
        ]
        return sectors[:limit]