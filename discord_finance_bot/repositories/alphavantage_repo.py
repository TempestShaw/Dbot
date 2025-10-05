import csv
import datetime as dt
from typing import Dict, List, Optional
import requests
from utils.logger import get_logger


BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageRepo:
    """Repository for Alpha Vantage CSV endpoints."""

    def __init__(self, config):
        self.logger = get_logger(__name__)
        self.api_key = getattr(config, "alphavantage_api_key", "") or ""

    def _fetch_csv(self, params: Dict[str, str]) -> List[Dict[str, str]]:
        if not self.api_key:
            self.logger.warning("ALPHAVANTAGE_API_KEY is not configured.")
        q = {**params, "apikey": self.api_key or "demo"}
        try:
            resp = requests.get(BASE_URL, params=q, timeout=10)
            resp.raise_for_status()
        except Exception as exc:
            self.logger.exception(f"AlphaVantage request failed: {exc}")
            return []

        try:
            text = resp.content.decode("utf-8")
            reader = csv.DictReader(text.splitlines())
            return [dict(row) for row in reader]
        except Exception as exc:
            self.logger.exception(f"Failed to parse CSV: {exc}")
            return []

    def fetch_earnings_calendar(self, horizon: str = "3month", symbol: Optional[str] = None) -> List[Dict[str, str]]:
        params = {"function": "EARNINGS_CALENDAR", "horizon": horizon}
        if symbol:
            params["symbol"] = symbol
        return self._fetch_csv(params)

    def fetch_ipo_calendar(self) -> List[Dict[str, str]]:
        params = {"function": "IPO_CALENDAR"}
        return self._fetch_csv(params)

    @staticmethod
    def _normalize_date(value: str) -> Optional[dt.date]:
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
            try:
                return dt.datetime.strptime(value.strip(), fmt).date()
            except Exception:
                continue
        return None

    @staticmethod
    def _filter_by_dates(rows: List[Dict[str, str]], date_field: str, dates: List[dt.date]) -> List[Dict[str, str]]:
        target = set(dates)
        out: List[Dict[str, str]] = []
        for r in rows:
            d = AlphaVantageRepo._normalize_date(r.get(date_field, ""))
            if d and d in target:
                out.append(r)
        return out

    @staticmethod
    def _filter_by_range(rows: List[Dict[str, str]], date_field: str, start: dt.date, end: dt.date) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        for r in rows:
            d = AlphaVantageRepo._normalize_date(r.get(date_field, ""))
            if d and start <= d <= end:
                out.append(r)
        return out

    def get_earnings_for_dates(self, dates: List[dt.date], horizon: str = "3month", symbol: Optional[str] = None) -> List[Dict[str, str]]:
        rows = self.fetch_earnings_calendar(horizon=horizon, symbol=symbol)
        filt = self._filter_by_dates(rows, "reportDate", dates)
        fields = ["symbol", "name", "reportDate", "fiscalDateEnding", "estimateEPS", "estimateCurrency"]
        return [{k: r.get(k, "") for k in fields} for r in filt]

    def get_ipos_for_dates(self, dates: List[dt.date]) -> List[Dict[str, str]]:
        rows = self.fetch_ipo_calendar()
        filt = self._filter_by_dates(rows, "ipoDate", dates)
        fields = ["symbol", "name", "ipoDate", "priceRange", "currency"]
        return [{k: r.get(k, "") for k in fields} for r in filt]

    def get_earnings_this_week(
        self,
        dates: Optional[List[dt.date]] = None,
        horizon: str = "3month",
        symbol: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Return earnings within the given date range or the next 7 days."""
        rows = self.fetch_earnings_calendar(horizon=horizon, symbol=symbol)

        if dates:
            start, end = min(dates), max(dates)
        else:
            start = dt.date.today()
            end = start + dt.timedelta(days=7)

        filt = self._filter_by_range(rows, "reportDate", start, end)
        fields = ["symbol", "name", "reportDate", "fiscalDateEnding", "estimateEPS", "estimateCurrency"]
        return [{k: r.get(k, "") for k in fields} for r in filt]

    def get_ipos_this_week(self, dates: Optional[List[dt.date]] = None) -> List[Dict[str, str]]:
        """Return IPOs within the given date range or the next 7 days."""
        rows = self.fetch_ipo_calendar()

        if dates:
            start, end = min(dates), max(dates)
        else:
            start = dt.date.today()
            end = start + dt.timedelta(days=7)

        filt = self._filter_by_range(rows, "ipoDate", start, end)
        fields = ["symbol", "name", "ipoDate", "priceRange", "currency"]
        return [{k: r.get(k, "") for k in fields} for r in filt]
