import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool


load_dotenv()


TIMEZONES = {
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "india": "Asia/Kolkata",
    "tokyo": "Asia/Tokyo",
    "london": "Europe/London",
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
}

TIMEZONE_API_URL = "https://api.timezone.io/v1/cities"


def lookup_timezone(location: str) -> str | None:
    """Look up an IANA timezone for a location using timezone.io."""

    token = os.getenv("TIMEZONE_API_TOKEN")

    if not token:
        return None

    try:
        response = requests.get(
            TIMEZONE_API_URL,
            params={"q": location, "per_page": 1},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()
        cities = data.get("data", [])

        if not cities:
            return None

        return cities[0]["timezone"]["iana"]

    except requests.RequestException:
        return None
    except (KeyError, TypeError, ValueError):
        return None


@tool
def get_current_time(location: str) -> str:
    """Get the current local time for a location."""

    location = location.strip()
    location_key = location.lower()

    timezone = TIMEZONES.get(location_key)

    if not timezone:
        timezone = lookup_timezone(location)

    if not timezone:
        return f"Could not determine the time zone for {location}."

    current_time = datetime.now(ZoneInfo(timezone))

    return current_time.strftime("%I:%M:%S %p")