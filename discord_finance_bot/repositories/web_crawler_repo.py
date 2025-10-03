from typing import List
import requests
from bs4 import BeautifulSoup


class WebCrawlerRepo:
    """Simple web crawler repository to fetch headlines from websites.

    This module is intentionally minimal and can be extended to scrape
    sites like Investing.com or Bloomberg with proper selectors.
    """

    def __init__(self, config):
        self.config = config

    def fetch_investing_news(self, url: str = "https://www.investing.com/news/") -> List[str]:
        """Fetch headlines from Investing (placeholder scraping)."""
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        headlines = [tag.get_text(strip=True) for tag in soup.select("h1, h2, h3")]
        return headlines[:10]