from typing import List, Dict
from utils.logger import get_logger

try:
    from playwright.async_api import async_playwright
except Exception as e:
    async_playwright = None


class PolymarketRepo:
    """Scrape Polymarket earnings data using Playwright."""

    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)

    async def scrape_polymarket_earnings(self) -> List[Dict]:
        """Scrape data from Polymarket and return structured data."""
        if async_playwright is None:
            self.logger.error(
                "Playwright not installed. Run `pip install playwright` and `python -m playwright install chromium`."
            )
            return []

        earnings_data = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                self.logger.info("Navigating to Polymarket Earnings page...")
                await page.goto("https://polymarket.com/earnings")

                # Wait for page main elements to load
                try:
                    await page.wait_for_selector("text=Earnings Calendar", timeout=15000)
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    self.logger.error(f"Page load timeout: {e}")
                    await browser.close()
                    return []

                self.logger.info("Starting data parsing...")

                # Find all "active" date columns
                active_columns = await page.locator("div.lg\\:grid-cols-5 > div.opacity-100").all()

                self.logger.info(f"Found {len(active_columns)} active date columns.")

                for col_index, col in enumerate(active_columns):
                    # Get date
                    try:
                        date_element = col.locator("span.text-sm.font-semibold").first
                        if await date_element.count() > 0:
                            date_num = await date_element.inner_text()
                        else:
                            date_num = f"Day_{col_index+1}"
                    except Exception as e:
                        self.logger.warning(f"Failed to get date {col_index}: {e}")
                        date_num = f"Day_{col_index+1}"

                    # Iterate through all groups for this date
                    groups = await col.locator("div.mb-4").all()

                    for group in groups:
                        # Get time period (Pre Market / Post Market)
                        try:
                            time_elements = await group.locator("span.text-\\[11px\\]").all()
                            if time_elements:
                                time_label = await time_elements[0].inner_text()
                            else:
                                time_label = "Unknown"
                        except Exception as e:
                            self.logger.warning(f"Failed to get time period: {e}")
                            time_label = "Unknown"

                        # Iterate through cards in the group
                        cards = await group.locator("div.cursor-pointer").all()

                        for card in cards:
                            try:
                                # Extract ticker symbol
                                ticker_element = card.locator("h4")
                                ticker = await ticker_element.inner_text()

                                # Extract EPS forecast
                                eps_element = card.locator("p.text-xs").first
                                eps_text = await eps_element.inner_text()

                                # Extract probability
                                prob_element = card.locator("span.text-sm.font-medium", has_text="%")
                                prob_text = await prob_element.inner_text()

                                # Organize data
                                item = {
                                    "date": date_num,
                                    "time": time_label,
                                    "ticker": ticker,
                                    "eps_forecast": eps_text,
                                    "probability": prob_text
                                }
                                earnings_data.append(item)
                                self.logger.debug(f"Scraped: {ticker} ({time_label})")

                            except Exception as e:
                                # Skip cards with parsing errors
                                self.logger.debug(f"Card parsing error: {e}")
                                continue

                await browser.close()

        except Exception as e:
            self.logger.exception(f"Error scraping Polymarket data: {e}")
            return []

        self.logger.info(f"Total scraped {len(earnings_data)} earnings data entries.")
        return earnings_data
