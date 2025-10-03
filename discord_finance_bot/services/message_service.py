from services.finance_service import FinanceService
from services.stock_service import StockService
from services.sector_service import SectorService


class MessageService:
    """Generate Discord messages and JSON payloads for n8n integration.

    This service composes data from other services and formats output
    either as human-readable markdown text or machine-readable JSON.
    """

    def __init__(self, config):
        self.finance_service = FinanceService(config)
        self.stock_service = StockService(config)
        self.sector_service = SectorService(config)

    def generate_daily_summary_json(self):
        """Return standardized JSON payload consumable by n8n workflows."""
        macro = self.finance_service.get_macro_data()
        stocks = self.stock_service.get_selected_stocks()
        sectors = self.sector_service.get_top_sectors()
        return {
            "macro": macro,
            "stocks": stocks,
            "sectors": sectors,
        }

    def generate_daily_summary_text(self) -> str:
        """Return human-readable markdown text for Discord messages."""
        payload = self.generate_daily_summary_json()
        return (
            f"📊 Macro Data:\n{payload['macro']}\n\n"
            f"📈 Stocks:\n{payload['stocks']}\n\n"
            f"🚀 Sectors:\n{payload['sectors']}"
        )