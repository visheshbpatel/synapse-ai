from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from components.llm import model

from components.tools.documents import get_documents
from components.tools.search_documents import search_documents
from components.tools.time import get_current_time
from components.tools.weather import get_weather
from components.tools.web_search import get_web_search


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


tools = [
    get_current_time,
    get_weather,
    get_documents,
    get_web_search,
    search_documents,
]


model_with_tools = model.bind_tools(tools)


def call_agent(state: AgentState):
    """Run the model using the current conversation state."""

    response = model_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


workflow = StateGraph(AgentState)

workflow.add_node("agent", call_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    },
)

workflow.add_edge("tools", "agent")

graph = workflow.compile()