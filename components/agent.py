from langchain.agents import create_agent

from components.llm import model
from components.tools.time import get_current_time
from components.tools.weather import get_weather


def get_agent():

    agent = create_agent(
        model=model,
        tools=[
            get_current_time,
            get_weather
            ]
    )

    return agent
