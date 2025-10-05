from services.alphavantage_service import AlphaVantageService
from services.web_crawler_service import WebCrawlerService
from zoneinfo import ZoneInfo
import datetime as dt


class MessageService:
    """Generate Discord messages and JSON payloads for n8n integration.

    This service composes data from other services and formats output
    either as human-readable markdown text or machine-readable JSON.
    """

    def __init__(self, config):
        self.alpha_service = AlphaVantageService(config)
        self.web_crawler_service = WebCrawlerService(config)
        self.config = config

    def generate_daily_summary_json(self):
        """Return standardized JSON payload consumable by n8n workflows."""
        # add top sector details via crawler service
        top_sectors_details = self.web_crawler_service.get_top_sectors_details()

        # Compute today/tomorrow/day-after in configured timezone
        today = dt.datetime.now(ZoneInfo(self.config.timezone)).date()
        dates = [today, today + dt.timedelta(days=1), today + dt.timedelta(days=2)]

        earnings = self.alpha_service.get_week_earnings_for_dates(dates)
        ipos = self.alpha_service.get_week_ipos_for_dates(dates)

        return {
            "top_sectors_details": top_sectors_details,
            "earnings": earnings,
            "ipos": ipos,
            "dates": [d.isoformat() for d in dates],
        }

    async def generate_daily_summary_json_async(self):
        """Async version returning standardized JSON payload for n8n/Discord flows."""
        # fetch top sector details via async crawler service
        top_sectors_details = await self.web_crawler_service.get_top_sectors_details_async()

        # Compute today/tomorrow/day-after in configured timezone
        today = dt.datetime.now(ZoneInfo(self.config.timezone)).date()
        dates = [today, today + dt.timedelta(days=1), today + dt.timedelta(days=2)]

        # AlphaVantage calls remain synchronous
        earnings = self.alpha_service.get_week_earnings_for_dates(dates)
        ipos = self.alpha_service.get_week_ipos_for_dates(dates)
        print(top_sectors_details)
        return {
            "top_sectors_details": top_sectors_details,
            "earnings": earnings,
            "ipos": ipos,
            "dates": [d.isoformat() for d in dates],
        }

    def generate_daily_summary_text(self) -> str:
        """Return human-readable markdown text for Discord messages."""
        payload = self.generate_daily_summary_json()

        # Compose additional tables for earnings and IPOs
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
        # Build a clean markdown table for top sector details
        sectors_details = payload.get("top_sectors_details") or []
        sectors_details_tbl = to_markdown_table(
            sectors_details,
            [
                "name",
                "change_pct",
                "leader_stock",
                "leader_change_pct",
                "up_count",
                "unchanged_count",
                "down_count",
            ],
        )

        return (
            f"🔥 Top Sector Details\n{sectors_details_tbl}\n\n"
            f"📅 Earnings & IPOs for {dates_str}\n\n"
            f"🧾 Earnings\n{earnings_tbl}\n\n"
            f"🆕 IPOs\n{ipos_tbl}"
        )

    async def generate_daily_summary_text_async(self) -> str:
        """Async version returning human-readable markdown text for Discord messages."""
        payload = await self.generate_daily_summary_json_async()

        # Compose additional tables for earnings and IPOs
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
        sectors_details = payload.get("top_sectors_details") or []
        sectors_details_tbl = to_markdown_table(
            sectors_details,
            [
                "name",
                "change_pct",
                "leader_stock",
                "leader_change_pct",
                "up_count",
                "unchanged_count",
                "down_count",
            ],
        )

        return (
            f"🔥 Top Sector Details\n{sectors_details_tbl}\n\n"
            f"📅 Earnings & IPOs for {dates_str}\n\n"
            f"🧾 Earnings\n{earnings_tbl}\n\n"
            f"🆕 IPOs\n{ipos_tbl}"
        )


