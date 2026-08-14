from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from components.llm import model


class RouterDecision(BaseModel):
    route: Literal["chat", "rag"] = Field(
        description="The pipeline that should handle the user's query"
    )

ROUTER_SYSTEM_PROMPT = """
You are a query router for SynapseAI.

Your job is to decide whether the user's query should be handled by:

- "chat": General conversation or questions that do not require information
  from the user's uploaded documents.

- "rag": Questions that require information from, reference, or depend on
  the user's uploaded documents.

Consider the conversation history when making the decision.

Choose "rag" when the user refers to information that was previously discussed
from uploaded documents, even if the current question does not explicitly
mention the document.

Choose "chat" for general knowledge, casual conversation, writing help,
coding questions, or questions that do not depend on uploaded documents.

Return only the structured routing decision.
"""


router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ROUTER_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)

router = router_prompt | model.with_structured_output(RouterDecision)





