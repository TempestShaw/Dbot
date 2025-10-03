from repositories.yahoo_repo import YahooRepo


class SectorService:
    """Business logic for sector performance calculation and ranking."""

    def __init__(self, config):
        self.yahoo_repo = YahooRepo(config)

    def get_top_sectors(self, limit: int = 5):
        """Return top performing sectors limited by `limit`."""
        return self.yahoo_repo.fetch_top_sectors(limit=limit)