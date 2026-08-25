"""Time and date management with Asia/Kolkata (IST) support and dynamic real-time calculation."""
from datetime import datetime
import pytz

DEFAULT_TIMEZONE = "Asia/Kolkata"

def get_current_ist_datetime(tz_name: str = DEFAULT_TIMEZONE) -> datetime:
    """Returns the current timezone-aware datetime."""
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone(DEFAULT_TIMEZONE)
    return datetime.now(tz)

def get_live_time_metrics(tz_name: str = DEFAULT_TIMEZONE) -> dict:
    """Calculates all real-time temporal parameters dynamically."""
    now = get_current_ist_datetime(tz_name)
    
    return {
        "datetime": now,
        "date_str": now.strftime("%d %B %Y"),
        "time_str": now.strftime("%H:%M:%S"),
        "day_name": now.strftime("%A"),
        "month_name": now.strftime("%B"),
        "month_num": now.month,
        "day_num": now.day,
        "year": now.year,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "timezone": tz_name,
        "tz_offset": now.strftime("%z"),
        "iso_format": now.isoformat(),
        "timestamp_str": now.strftime("%Y-%m-%d %H:%M:%S %Z")
    }

def format_timestamp(dt: datetime) -> str:
    """Formats datetime for UI display."""
    return dt.strftime("%d %b %Y, %I:%M:%S %p IST")

def format_hour(hour_24: int) -> str:
    """Formats hour for forecast charts."""
    return f"{hour_24:02d}:00"
