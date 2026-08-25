import os

from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.tools import tool


load_dotenv()


@tool
def get_web_search(
    query: str,
    topic: str = "general",
    time_range: str | None = None,
) -> str:
    """Search the web for current or external information.

    Use topic='news' for recent news.
    Use time_range='day' for today's news.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "Web search is unavailable because the Tavily API key is not configured."

    try:
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=query,
            topic=topic,
            time_range=time_range,
            max_results=3,
            search_depth="basic",
        )

        results = response.get("results", [])

        if not results:
            return "No search results found."

        formatted_results = []

        for index, result in enumerate(results, start=1):
            published_date = result.get("published_date")

            formatted_results.append(
                f"**{index}**. **{result['title']}**\n"
                f"{result['content']}\n"
                f"Published: {published_date or 'Not provided'}\n"
                f"Source: **{result['url']}**"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"Web search failed: {e}"