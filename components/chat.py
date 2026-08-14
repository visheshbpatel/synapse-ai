from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from components.llm import model

CHAT_SYSTEM_PROMPT = """
You are SynapseAI, a knowledgeable and professional AI assistant.

Answer the user's question clearly and accurately.

Use the conversation history when it is releveant.
"""

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CHAT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)

chat_parser = StrOutputParser()

def get_chat_chain():

    chain = (
        chat_prompt | model | chat_parser
    )

    return chain

