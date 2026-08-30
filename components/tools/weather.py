import os
import requests
from dotenv import load_dotenv


from langchain_core.tools import tool

load_dotenv()

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""

    api_key = os.getenv("OPENWEATHER_API_KEY")

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": location,
            "appid": api_key,
            "units": "metric",
        }
    )

    if response.status_code != 200:
        return f"Could not get weather for {location}."

    data = response.json()

    return (
        f"{data['name']}: "
        f"{data['main']['temp']}°C, "
        f"feels like {data['main']['feels_like']}°C, "
        f"{data['weather'][0]['description']}, "
        f"humidity {data['main']['humidity']}%, "
        f"wind speed {data['wind']['speed']} m/s."
    )