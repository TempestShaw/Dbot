import datetime as dt
from typing import Dict, List, Optional

from repositories.alphavantage_repo import AlphaVantageRepo


class AlphaVantageService:
    """Thin service wrapper that delegates to AlphaVantageRepo.

    Keeps service layer consistent: controllers/services call services,
    and heavy lifting stays in repositories.
    """

    def __init__(self, config):
        self.repo = AlphaVantageRepo(config)

    def get_week_earnings_for_dates(
        self,
        dates: List[dt.date]
    ) -> List[Dict[str, str]]:
        return self.repo.get_earnings_this_week(dates)

    def get_week_ipos_for_dates(self, dates: List[dt.date]) -> List[Dict[str, str]]:
        return self.repo.get_ipos_this_week(dates)