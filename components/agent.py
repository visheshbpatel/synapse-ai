from langchain.agents import create_agent

from components.llm import model
from components.tools.time import get_current_time


def get_agent():

    agent = create_agent(
        model=model,
        tools=[get_current_time],
    )

    return agent
