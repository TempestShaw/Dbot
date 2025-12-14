from typing import List, Optional
import asyncio
from utils.logger import get_logger

try:
    from playwright.async_api import async_playwright  # type: ignore
except Exception:
    async_playwright = None  # Playwright not installed yet


class WebCrawlerRepo:
    """Fetch top sector info from Moomoo via API triggered by page navigation."""

    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
    async def _scrape_top_sectors_details_async(self, url: str = "https://www.moomoo.com/quote/us/concepts", limit: int = 10) -> List[dict]:
        """Use Playwright to capture API responses from the live page."""
        if async_playwright is None:
            self.logger.error(
                "Playwright not installed. Run `pip install playwright` and `python -m playwright install chromium`."
            )
            return []

        collected_data: List[dict] = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    locale="en-US",
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/127.0.0.0 Safari/537.36"
                    ),
                    extra_http_headers={
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Origin": "https://moomoo.com",
                        "Referer": "https://moomoo.com/quote/us/concepts",
                    },
                )
                page = await context.new_page()

                async def handle_response(response):
                    if "get-plate-list" in response.url:
                        try:
                            data = await response.json()
                            real_list = data.get("data", {}).get("list", [])
                            collected_data.extend(real_list)
                        except Exception as e:
                            self.logger.warning(f"Failed to parse JSON from response: {e}")

                page.on("response", lambda resp: asyncio.create_task(handle_response(resp)))

                await page.goto(url, wait_until="networkidle")
                await page.wait_for_selector(".base-pagination .item")

                first_page_item = await page.query_selector(".base-pagination .item:nth-child(2)")
                if first_page_item:
                    await first_page_item.click()

                await page.wait_for_timeout(1000)  # Wait for API response

                await context.close()
                await browser.close()

            return collected_data[:limit]
        except Exception as exc:
            self.logger.exception(f"Failed to scrape sector details via Playwright: {exc}")
            return []


    async def fetch_top_sectors_details_async(
        self, url: Optional[str] = "https://www.moomoo.com/quote/us/concepts", limit: int = 10
    ) -> List[dict]:
        """Public async wrapper to get top sector info."""
        target_url = url or getattr(self.config, "sectors_url", "")
        if not target_url:
            self.logger.warning("No sectors URL provided.")
            return []

        return await self._scrape_top_sectors_details_async(url=target_url, limit=limit)

    def fetch_top_sectors_names(self, url: Optional[str] = None, limit: int = 5) -> List[str]:
        """Sync wrapper to get top sector names (returns empty list for now)."""
        # TODO: Implement sync version or remove this method
        self.logger.warning("fetch_top_sectors_names is not implemented for sync version")
        return []

    def fetch_top_sectors_details(self, url: Optional[str] = "https://www.moomoo.com/quote/us/concepts", limit: int = 5) -> List[dict]:
        """Sync wrapper to get top sector details (returns empty list for now)."""
        # TODO: Implement sync version or remove this method
        self.logger.warning("fetch_top_sectors_details is not implemented for sync version")
        return []


# Example usage
if __name__ == "__main__":
    import argparse
    import json
    from discord_finance_bot.config import load_config  # type: ignore

    cfg = load_config()
    repo = WebCrawlerRepo(cfg)

    parser = argparse.ArgumentParser(description="Test sector details scraping via API capture")
    parser.add_argument("--url", type=str, default="https://www.moomoo.com/quote/us/concepts")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    details = asyncio.run(repo.fetch_top_sectors_details_async(url=args.url, limit=args.limit))
    print(json.dumps({"sectors": details}, ensure_ascii=False, indent=2))
