from pathlib import Path
from langchain_core.tools import tool 

from components.rag import retrieve_documents

@tool
def search_documents(query: str) -> str:
    """Search the contents of uploaded documents for information relevant to the user's query.
    Use this when the user asks about information contained inside their documents."""

    documents = retrieve_documents(query)

    if not documents:
        return "No relevant information was found in the uploaded documents."


    results = []

    for document in documents:
        source = document.metadata.get("source")

        if source:
            source = Path(source).name

        page = document.metadata.get("page_label")

        content = document.page_content

        if page:
            results.append(
                f"[Source: {source}, Page: {page}] \n {content}"
            )
        else:
            results.append(
                f"[Source: {source}] \n {content}"
            )

    return "\n\n".join(results)