from langchain_core.tools import tool

from components.rag import list_documents


@tool
def get_documents() -> str:
    """List the documents currently available in SynapseAI"""

    documents = list_documents()

    if not documents:
        return "No documents are currently available."

    return "\n".join(
        document["name"]
        for document in documents
    ) 