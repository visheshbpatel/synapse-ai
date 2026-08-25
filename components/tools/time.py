from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.tools import tool


TIMEZONES = {
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "india": "Asia/Kolkata",
    "tokyo": "Asia/Tokyo",
    "london": "Europe/London",
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
}

@tool
def get_current_time(location: str) -> str:
    """Get the current local time for a supported location"""

    timezone = TIMEZONES.get(location.lower().strip())

    if not timezone:
        return f"Time zone for {location} is not supported."

    current_time = datetime.now(ZoneInfo(timezone))

    return current_time.strftime("%I:%M:%S %p")