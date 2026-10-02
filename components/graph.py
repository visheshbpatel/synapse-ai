from typing import Annotated, TypedDict
from contextlib import ExitStack
from langgraph.runtime import Runtime

from components.context import UserContext
from langchain_core.messages import AnyMessage, ToolMessage, AIMessage, HumanMessage
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


def stream_response(user_input, thread_id, user_id):
    """ Stream the assistant response and collect source artifacts."""

    sources = []

    config = {
        "configurable": {
            "thread_id": thread_id
        },
        "metadata": {
            "thread_id": thread_id
        }
    }

    def stream():

        for chunk, _ in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            context=UserContext(user_id=user_id),
            stream_mode="messages"
        ):

            if isinstance(chunk, ToolMessage):
                artifact = getattr(chunk, "artifact", None)

                if artifact:
                    sources.extend(artifact)

            
            elif (
                isinstance(chunk, AIMessage)
                and isinstance(chunk.content, str)
                and chunk.content
            ):
                yield chunk.content

    return stream(), sources

            

workflow = StateGraph(
    AgentState,
    context_schema=UserContext,
)


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