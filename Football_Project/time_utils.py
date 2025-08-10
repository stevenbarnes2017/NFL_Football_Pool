# Football_Project/time_utils.py
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

MT = ZoneInfo("America/Denver")

def espn_iso_to_mt_dt(iso_str: str) -> datetime:
    """
    ESPN date -> tz-aware Mountain datetime.
    Accepts '...Z' or offset ISO.
    """
    if not iso_str:
        raise ValueError("Missing kickoff date")
    s = iso_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(MT)

def ensure_dt_mt(val) -> datetime | None:
    """
    Accepts datetime, ISO string with offset/Z, or 'YYYY-MM-DD HH:MM:SS MDT/MST'.
    Returns tz-aware Mountain datetime (or None).
    """
    if not val:
        return None
    if isinstance(val, datetime):
        return val.astimezone(MT) if val.tzinfo else val.replace(tzinfo=timezone.utc).astimezone(MT)
    v = str(val)
    if "T" in v:  # ISO
        return espn_iso_to_mt_dt(v)
    # handle "YYYY-MM-DD HH:MM:SS MDT/MST"
    base = v.rsplit(" ", 1)[0]  # drop zone text
    dt = datetime.strptime(base, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=MT)

def fmt_mt(dt: datetime | None) -> str:
    """Format exactly like '2025-08-10 11:00:00 MDT'."""
    if not dt:
        return ""
    return dt.astimezone(MT).strftime("%Y-%m-%d %H:%M:%S %Z")
