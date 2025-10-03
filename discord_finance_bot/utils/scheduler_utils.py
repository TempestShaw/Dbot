from typing import Any
from zoneinfo import ZoneInfo


def get_timezone(tz_name: str) -> Any:
    """Return tzinfo for APScheduler using IANA time zone names.

    Fallback to UTC if provided name is invalid or unavailable.
    """
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo("UTC")