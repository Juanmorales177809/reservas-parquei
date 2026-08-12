from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings


def ahora_local() -> datetime:
    """Return local business time without tzinfo for comparison with DATE/TIME columns."""
    return datetime.now(ZoneInfo(settings.app_timezone)).replace(tzinfo=None)
