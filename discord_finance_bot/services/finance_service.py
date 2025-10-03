from repositories.yahoo_repo import YahooRepo


class FinanceService:
    """Business logic for macro data and important news."""

    def __init__(self, config):
        self.yahoo_repo = YahooRepo(config)

    def get_macro_data(self):
        """Return macro data such as CPI, PPI, unemployment, etc."""
        return self.yahoo_repo.fetch_macro_data()

    def get_important_news(self):
        """Return a list of important market news entries."""
        return self.yahoo_repo.fetch_market_news()