from langchain_core.tools import tool

from components.rag import list_documents


@tool
def get_documents() -> str:
    """List the filenames of documents currently uploaded to SynapseAI. 
    Use this only when the user asks what documents are available.
    Do not use this tool to search the contents of documents."""

    documents = list_documents()

    if not documents:
        return "No documents are currently available."

    return "\n".join(
        document["name"]
        for document in documents
    ) 