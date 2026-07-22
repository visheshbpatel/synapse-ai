from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_PROMPT = """
You are SynapseAI, a knowledgeable and professional AI assistant.

You must answer using only the retrieved context below.

If the context does not contain enough information to answer, respond with:

"I don't know based on the provided documents."

Do not use your own knowledge.
Do not make up information.

"""


prompt = ChatPromptTemplate.from_messages(
    [
        ('system', SYSTEM_PROMPT),
        ('system', "Context:\n{context}"),
        MessagesPlaceholder(variable_name="history"),
        ('human', "{question}")
    ]
)