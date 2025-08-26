"""
Timezone utility functions for consistent timezone handling
"""
import datetime
from typing import Optional

# Vietnam timezone offset (UTC+7)
VIETNAM_TIMEZONE_OFFSET = 7

def get_utc_now() -> datetime.datetime:
    """Get current UTC time"""
    return datetime.datetime.utcnow()

def utc_to_vietnam_time(utc_time: datetime.datetime) -> datetime.datetime:
    """Convert UTC time to Vietnam time (UTC+7)"""
    return utc_time + datetime.timedelta(hours=VIETNAM_TIMEZONE_OFFSET)

def format_vietnam_time(utc_time: datetime.datetime, format_str: str = "%H:%M - %d/%m/%Y") -> str:
    """Format UTC time as Vietnam time string"""
    vietnam_time = utc_to_vietnam_time(utc_time)
    return vietnam_time.strftime(format_str)

def format_vietnam_datetime(utc_time: datetime.datetime) -> str:
    """Format UTC time as Vietnam datetime string"""
    return format_vietnam_time(utc_time, "%d/%m/%Y %H:%M:%S")

def format_vietnam_time_only(utc_time: datetime.datetime) -> str:
    """Format UTC time as Vietnam time only (HH:MM)"""
    return format_vietnam_time(utc_time, "%H:%M")

def format_vietnam_date_only(utc_time: datetime.datetime) -> str:
    """Format UTC time as Vietnam date only (DD/MM/YYYY)"""
    return format_vietnam_time(utc_time, "%d/%m/%Y")

# For API responses
def get_vietnam_timestamp_response(utc_time: Optional[datetime.datetime] = None) -> dict:
    """Get standardized timestamp response for API"""
    if utc_time is None:
        utc_time = get_utc_now()
    
    return {
        "timestamp": utc_time.isoformat(),  # UTC for API consistency
        "formatted_time": format_vietnam_time(utc_time),  # Vietnam time for display
        "vietnam_datetime": format_vietnam_datetime(utc_time),
        "timezone": "UTC+7 (Vietnam)"
    }

# Example usage:
if __name__ == "__main__":
    # Test timezone conversion
    utc_now = get_utc_now()
    print(f"UTC Time: {utc_now}")
    print(f"Vietnam Time: {utc_to_vietnam_time(utc_now)}")
    print(f"Formatted: {format_vietnam_time(utc_now)}")
    print(f"API Response: {get_vietnam_timestamp_response()}")
