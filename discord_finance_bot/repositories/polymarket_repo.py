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
        """ data from Polymarket and return structured data."""
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

                self.logger.info("正在前往 Polymarket Earnings 頁面...")
                await page.goto("https://polymarket.com/earnings")

                # 等待頁面主要元素加載
                try:
                    await page.wait_for_selector("text=Earnings Calendar", timeout=15000)
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    self.logger.error(f"頁面加載超時: {e}")
                    await browser.close()
                    return []

                self.logger.info("開始解析數據...")

                # 找到所有 "活躍" 的日期列
                active_columns = await page.locator("div.lg\\:grid-cols-5 > div.opacity-100").all()

                self.logger.info(f"找到 {len(active_columns)} 個活躍日期列。")

                for col_index, col in enumerate(active_columns):
                    # 獲取日期
                    try:
                        date_element = col.locator("span.text-sm.font-semibold").first
                        if await date_element.count() > 0:
                            date_num = await date_element.inner_text()
                        else:
                            date_num = f"Day_{col_index+1}"
                    except Exception as e:
                        self.logger.warning(f"無法獲取日期 {col_index}: {e}")
                        date_num = f"Day_{col_index+1}"

                    # 遍歷該日期的所有分組
                    groups = await col.locator("div.mb-4").all()

                    for group in groups:
                        # 獲取時間段 (Pre Market / Post Market)
                        try:
                            time_elements = await group.locator("span.text-\\[11px\\]").all()
                            if time_elements:
                                time_label = await time_elements[0].inner_text()
                            else:
                                time_label = "Unknown"
                        except Exception as e:
                            self.logger.warning(f"無法獲取時間段: {e}")
                            time_label = "Unknown"

                        # 遍歷分組內的卡片
                        cards = await group.locator("div.cursor-pointer").all()

                        for card in cards:
                            try:
                                # 提取公司代號 (Ticker)
                                ticker_element = card.locator("h4")
                                ticker = await ticker_element.inner_text()

                                # 提取 EPS 預測
                                eps_element = card.locator("p.text-xs").first
                                eps_text = await eps_element.inner_text()

                                # 提取勝率 (Probability)
                                prob_element = card.locator("span.text-sm.font-medium", has_text="%")
                                prob_text = await prob_element.inner_text()

                                # 整理數據
                                item = {
                                    "date": date_num,
                                    "time": time_label,
                                    "ticker": ticker,
                                    "eps_forecast": eps_text,
                                    "probability": prob_text
                                }
                                earnings_data.append(item)
                                self.logger.debug(f"抓取到: {ticker} ({time_label})")

                            except Exception as e:
                                # 忽略解析錯誤的卡片
                                self.logger.debug(f"卡片解析錯誤: {e}")
                                continue

                await browser.close()

        except Exception as e:
            self.logger.exception(f"抓取 Polymarket 數據時發生錯誤: {e}")
            return []

        self.logger.info(f"總共抓取 {len(earnings_data)} 筆財報數據。")
        return earnings_data
