from repositories.yahoo_repo import YahooRepo


class StockService:
    """Business logic for selected stocks: quotes, earnings, etc."""

    def __init__(self, config):
        self.yahoo_repo = YahooRepo(config)
        self.selected_stocks = list(config.selected_stocks)

    def get_selected_stocks(self):
        """Return latest quotes for configured selected stocks."""
        return self.yahoo_repo.fetch_stocks(self.selected_stocks)