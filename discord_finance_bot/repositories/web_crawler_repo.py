from typing import List, Optional
import asyncio
import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

try:
    from playwright.async_api import async_playwright  # type: ignore
except Exception:
    async_playwright = None  # Playwright not installed yet

try:
    from playwright.sync_api import sync_playwright  # type: ignore
except Exception:
    sync_playwright = None  # Playwright sync API not installed


class WebCrawlerRepo:
    """Simple web crawler repository to fetch headlines and sector info."""

    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)

    async def _scrape_top_sectors_async(self, url: str = "https://www.moomoo.com/hans/quote/us/concepts", limit: int = 5) -> List[str]:
        """Use Playwright to scrape top sector names from the given page.

        Expected DOM structure (example):
          - Container: div.content-main
          - Items: a.list-item
          - Sector name: span.plate-name

        Returns a list of sector names (top `limit`).
        """
        if async_playwright is None:
            self.logger.error("Playwright is not installed. Please `pip install playwright` and `python -m playwright install chromium`.")
            return []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_selector("div.content-main", timeout=10000)
                items = await page.query_selector_all("div.content-main a.list-item")
                names: List[str] = []
                for item in items[:limit]:
                    name_el = await item.query_selector("span.plate-name")
                    text = await name_el.text_content() if name_el else None
                    if text:
                        names.append(text.strip())
                await context.close()
                await browser.close()
                return names
        except Exception as exc:
            self.logger.exception(f"Failed to scrape sectors via Playwright: {exc}")
            return []

    def fetch_top_sectors_names(self, url: Optional[str] = None, limit: int = 5) -> List[str]:
        """Public wrapper to get top sector names using Playwright sync API."""
        target_url = url or getattr(self.config, "sectors_url", "")
        if not target_url:
            self.logger.warning("No sectors URL provided. Pass `url` or set `config.sectors_url`.")
            return []

        if sync_playwright is None:
            self.logger.error("Playwright sync API not available. Install playwright and browsers.")
            return []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(target_url, wait_until="networkidle")
                page.wait_for_selector("div.content-main", timeout=10000)
                items = page.query_selector_all("div.content-main a.list-item")
                names: List[str] = []
                for item in items[:limit]:
                    name_el = item.query_selector("span.plate-name")
                    text = name_el.text_content() if name_el else None
                    if text:
                        names.append(text.strip())
                context.close()
                browser.close()
                return names
        except Exception as exc:
            self.logger.exception(f"Failed to fetch top sectors names (sync): {exc}")
            return []

    async def _scrape_top_sectors_details_async(self, url: str = "https://www.moomoo.com/hans/quote/us/concepts", limit: int = 5) -> List[dict]:
        """Use Playwright to scrape detailed top sectors.

        Extracts per sector:
          - name: `span.plate-name`
          - change_pct: first `span.change.value`
          - leader_stock: `object.stock-name a`
          - leader_change_pct: last `span.change.value` (if present)
          - up_count, unchanged_count, down_count: parsed from value elements.
        """
        if async_playwright is None:
            self.logger.error("Playwright is not installed. Please `pip install playwright` and `python -m playwright install chromium`.")
            return []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_selector("div.content-main", timeout=10000)

                items = await page.query_selector_all("div.content-main a.list-item")
                out: List[dict] = []
                for item in items[:limit]:
                    name_el = await item.query_selector("span.plate-name")
                    name = (await name_el.text_content()).strip() if name_el else ""

                    change_nodes = await item.query_selector_all("span.change.value")
                    change_texts: List[str] = []
                    for cn in change_nodes:
                        t = await cn.text_content()
                        if t:
                            change_texts.append(t.strip())
                    sector_change = change_texts[0] if change_texts else ""
                    leader_change = change_texts[-1] if len(change_texts) > 1 else ""

                    val_nodes = await item.query_selector_all("span.value.ellipsis")
                    val_texts: List[str] = []
                    for vn in val_nodes:
                        t = await vn.text_content()
                        if t:
                            val_texts.append(t.strip())
                    same_el = await item.query_selector("span.same-count.value.ellipsis")
                    same_text = (await same_el.text_content()).strip() if same_el else ""

                    def _to_int(s: str) -> Optional[int]:
                        try:
                            return int(s)
                        except Exception:
                            return None

                    up_count = _to_int(val_texts[0]) if val_texts else None
                    down_count = _to_int(val_texts[-1]) if val_texts else None
                    unchanged_count = _to_int(same_text) if same_text else None

                    leader_el = await item.query_selector("object.stock-name a")
                    leader_name = (await leader_el.text_content()).strip() if leader_el else ""

                    out.append(
                        {
                            "name": name,
                            "change_pct": sector_change,
                            "up_count": up_count,
                            "unchanged_count": unchanged_count,
                            "down_count": down_count,
                            "leader_stock": leader_name,
                            "leader_change_pct": leader_change,
                        }
                    )

                await context.close()
                await browser.close()
                return out
        except Exception as exc:
            self.logger.exception(f"Failed to scrape sector details via Playwright: {exc}")
            return []

    def fetch_top_sectors_details(self, url: Optional[str] = "https://www.moomoo.com/hans/quote/us/concepts", limit: int = 5) -> List[dict]:
        """Sync wrapper to get detailed top sector info using Playwright sync API."""
        target_url = url or getattr(self.config, "sectors_url", "")
        if not target_url:
            self.logger.warning("No sectors URL provided. Pass `url` or set `config.sectors_url`.")
            return []

        if sync_playwright is None:
            self.logger.error("Playwright sync API not available. Install playwright and browsers.")
            return []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(target_url, wait_until="networkidle")
                page.wait_for_selector("div.content-main", timeout=10000)
                items = page.query_selector_all("div.content-main a.list-item")
                out: List[dict] = []
                for item in items[:limit]:
                    name_el = item.query_selector("span.plate-name")
                    name = (name_el.text_content().strip() if name_el else "")

                    change_nodes = item.query_selector_all("span.change.value")
                    change_texts: List[str] = []
                    for cn in change_nodes:
                        t = cn.text_content()
                        if t:
                            change_texts.append(t.strip())
                    sector_change = change_texts[0] if change_texts else ""
                    leader_change = change_texts[-1] if len(change_texts) > 1 else ""

                    val_nodes = item.query_selector_all("span.value.ellipsis")
                    val_texts: List[str] = []
                    for vn in val_nodes:
                        t = vn.text_content()
                        if t:
                            val_texts.append(t.strip())
                    same_el = item.query_selector("span.same-count.value.ellipsis")
                    same_text = (same_el.text_content().strip() if same_el else "")

                    def _to_int(s: str) -> Optional[int]:
                        try:
                            return int(s)
                        except Exception:
                            return None

                    up_count = _to_int(val_texts[0]) if val_texts else None
                    down_count = _to_int(val_texts[-1]) if val_texts else None
                    unchanged_count = _to_int(same_text) if same_text else None

                    leader_el = item.query_selector("object.stock-name a")
                    leader_name = (leader_el.text_content().strip() if leader_el else "")

                    out.append(
                        {
                            "name": name,
                            "change_pct": sector_change,
                            "up_count": up_count,
                            "unchanged_count": unchanged_count,
                            "down_count": down_count,
                            "leader_stock": leader_name,
                            "leader_change_pct": leader_change,
                        }
                    )

                context.close()
                browser.close()
                return out
        except Exception as exc:
            self.logger.exception(f"Failed to fetch detailed top sectors (sync): {exc}")
            return []



if __name__ == "__main__":
    import argparse
    import json
    from discord_finance_bot.config import load_config  # type: ignore

    cfg = load_config()
    repo = WebCrawlerRepo(cfg)

    parser = argparse.ArgumentParser(description="Test sector details scraping via Playwright")
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.moomoo.com/hans/quote/us/concepts",
        help="Target sectors page URL (default: moomoo US concepts Chinese page)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of top sectors to return",
    )
    args = parser.parse_args()

    details = repo.fetch_top_sectors_details(url=args.url, limit=args.limit)
    print(json.dumps({"sectors": details}, ensure_ascii=False, indent=2))