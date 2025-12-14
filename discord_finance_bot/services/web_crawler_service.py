from typing import List, Optional, Dict
from repositories.web_crawler_repo import WebCrawlerRepo
from repositories.polymarket_repo import PolymarketRepo


class WebCrawlerService:
    """Service layer wrapping WebCrawlerRepo for sector scraping.

    Keeps MessageService and controllers decoupled from repo details.
    """

    def __init__(self, config):
        self.repo = WebCrawlerRepo(config)
        self.polymarket_repo = PolymarketRepo(config)
        self.config = config

    def get_top_sectors_names(self, url: Optional[str] = None, limit: int = 5) -> List[str]:
        return self.repo.fetch_top_sectors_names(url=url, limit=limit)

    def get_top_sectors_details(self, url: Optional[str] = "https://www.moomoo.com/hans/quote/us/concepts", limit: int = 5) -> List[Dict]:
        return self.repo.fetch_top_sectors_details(url=url, limit=limit)

    async def get_top_sectors_details_async(self, url: Optional[str] = "https://www.moomoo.com/hans/quote/us/concepts", limit: int = 10) -> List[Dict]:
        return await self.repo.fetch_top_sectors_details_async(url=url, limit=limit)

    async def get_polymarket_earnings_async(self) -> List[Dict]:
        """Fetch earnings data from Polymarket."""
        return await self.polymarket_repo.scrape_polymarket_earnings()



if __name__ == "__main__":
    # Minimal CLI to verify top sector details via sync service
    import json
    from discord_finance_bot.config import load_config

    cfg = load_config()
    svc = WebCrawlerService(cfg)
    details = svc.get_top_sectors_details()
