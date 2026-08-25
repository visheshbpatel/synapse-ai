from langchain.agents import create_agent

from components.llm import model
from components.tools.time import get_current_time
from components.tools.weather import get_weather
from components.tools.documents import get_documents
from components.tools.web_search import get_web_search


def get_agent():

    agent = create_agent(
        model=model,
        tools=[
            get_current_time,
            get_weather,
            get_documents,
            get_web_search
            ]
    )

    return agent
