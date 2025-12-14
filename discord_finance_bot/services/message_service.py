from services.alphavantage_service import AlphaVantageService
from services.web_crawler_service import WebCrawlerService
from zoneinfo import ZoneInfo
import datetime as dt

class MessageService:
    """Generate Discord messages and JSON payloads for n8n integration with new API fields."""

    def __init__(self, config):
        self.alpha_service = AlphaVantageService(config)
        self.web_crawler_service = WebCrawlerService(config)
        self.config = config

    def generate_daily_summary_json(self):
        """Return standardized JSON payload consumable by n8n workflows (sync)."""
        top_sectors_details = self.web_crawler_service.get_top_sectors_details()

        today = dt.datetime.now(ZoneInfo(self.config.timezone)).date()
        dates = [today, today + dt.timedelta(days=1), today + dt.timedelta(days=2)]

        earnings = self.alpha_service.get_week_earnings_for_dates(dates)
        ipos = self.alpha_service.get_week_ipos_for_dates(dates)

        # map to new API fields
        sectors_mapped = [
            {
                "plateName": s.get("plateName") or s.get("name"),
                "plateEnName": s.get("plateEnName") or s.get("name"),
                "plateCode": s.get("plateCode"),
                "stockName": s.get("stockName") or s.get("leader_stock"),
                "stockCode": s.get("stockCode"),
                "changeRatio": s.get("changeRatio") or s.get("change_pct"),
                "stockChangeRatio": s.get("stockChangeRatio") or s.get("leader_change_pct"),
                "priceRiseCount": s.get("priceRiseCount") or s.get("up_count"),
                "priceFallCount": s.get("priceFallCount") or s.get("down_count"),
                "priceSameCount": s.get("priceSameCount") or s.get("unchanged_count"),
                "tradeTurnover": s.get("tradeTurnover"),
                "tradeVolumn": s.get("tradeVolumn"),
                "backgroundImageUrl": s.get("backgroundImageUrl"),
            }
            for s in top_sectors_details
        ]

        return {
            "top_sectors_details": sectors_mapped,
            "earnings": earnings,
            "ipos": ipos,
            "dates": [d.isoformat() for d in dates],
        }

    async def generate_daily_summary_json_async(self):
        """Async version returning standardized JSON payload for n8n/Discord flows."""
        top_sectors_details = await self.web_crawler_service.get_top_sectors_details_async()
        polymarket_earnings = await self.web_crawler_service.get_polymarket_earnings_async()

        today = dt.datetime.now(ZoneInfo(self.config.timezone)).date()
        dates = [today, today + dt.timedelta(days=1), today + dt.timedelta(days=2)]

        earnings = self.alpha_service.get_week_earnings_for_dates(dates)
        ipos = self.alpha_service.get_week_ipos_for_dates(dates)

        sectors_mapped = [
            {
                "plateName": s.get("plateName") or s.get("name"),
                "plateEnName": s.get("plateEnName") or s.get("name"),
                "plateCode": s.get("plateCode"),
                "stockName": s.get("stockName") or s.get("leader_stock"),
                "stockCode": s.get("stockCode"),
                "changeRatio": s.get("changeRatio") or s.get("change_pct"),
                "stockChangeRatio": s.get("stockChangeRatio") or s.get("leader_change_pct"),
                "priceRiseCount": s.get("priceRiseCount") or s.get("up_count"),
                "priceFallCount": s.get("priceFallCount") or s.get("down_count"),
                "priceSameCount": s.get("priceSameCount") or s.get("unchanged_count"),
                "tradeTurnover": s.get("tradeTurnover"),
                "tradeVolumn": s.get("tradeVolumn"),
                "backgroundImageUrl": s.get("backgroundImageUrl"),
            }
            for s in top_sectors_details
        ]

        return {
            "top_sectors_details": sectors_mapped,
            "earnings": earnings,
            "polymarket_earnings": polymarket_earnings,
            "ipos": ipos,
            "dates": [d.isoformat() for d in dates],
        }

    def generate_daily_summary_text(self) -> str:
        """Markdown text for Discord messages with new API fields."""
        payload = self.generate_daily_summary_json()

        from utils.data_parser import to_markdown_table
        earnings_tbl = to_markdown_table(
            payload.get("earnings", []),
            ["symbol", "name", "reportDate", "estimateEPS", "estimateCurrency"],
        )
        ipos_tbl = to_markdown_table(
            payload.get("ipos", []),
            ["symbol", "name", "ipoDate", "priceRange", "currency"],
        )
        dates_str = ", ".join(payload.get("dates", []))

        sectors = payload.get("top_sectors_details", [])
        sectors_tbl = to_markdown_table(
            sectors,
            [
                "plateName",
                "changeRatio",
                "stockName",
                "stockChangeRatio",
                "priceRiseCount",
                "priceSameCount",
                "priceFallCount",
            ],
        )

        return (
            f"🔥 Top Sector Details\n{sectors_tbl}\n\n"
            f"📅 Earnings & IPOs for {dates_str}\n\n"
            f"🧾 Earnings\n{earnings_tbl}\n\n"
            f"🆕 IPOs\n{ipos_tbl}"
        )

    async def generate_daily_summary_text_async(self) -> str:
        """Async Markdown text for Discord messages with new API fields."""
        payload = await self.generate_daily_summary_json_async()

        from utils.data_parser import to_markdown_table
        earnings_tbl = to_markdown_table(
            payload.get("earnings", []),
            ["symbol", "name", "reportDate", "estimateEPS", "estimateCurrency"],
        )
        ipos_tbl = to_markdown_table(
            payload.get("ipos", []),
            ["symbol", "name", "ipoDate", "priceRange", "currency"],
        )
        dates_str = ", ".join(payload.get("dates", []))

        sectors = payload.get("top_sectors_details", [])
        sectors_tbl = to_markdown_table(
            sectors,
            [
                "plateName",
                "changeRatio",
                "stockName",
                "stockChangeRatio",
                "priceRiseCount",
                "priceSameCount",
                "priceFallCount",
            ],
        )

        return (
            f"🔥 Top Sector Details\n{sectors_tbl}\n\n"
            f"📅 Earnings & IPOs for {dates_str}\n\n"
            f"🧾 Earnings\n{earnings_tbl}\n\n"
            f"🆕 IPOs\n{ipos_tbl}"
        )
