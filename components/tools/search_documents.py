from components.context import UserContext
from pathlib import Path

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from components.rag import retrieve_documents


@tool(response_format="content_and_artifact")
def search_documents(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """Search the contents of uploaded documents for information relevant to the user's query.

    Use this when the user asks about information contained inside their documents.
    """
    user_id = runtime.context.user_id

    documents = retrieve_documents(
        user_id,
        query,
    )

    if not documents:
        return (
            "No relevant information was found in the uploaded documents.",
            [],
        )

    results = []
    sources = []

    for document in documents:
        source = document.metadata.get("source")

        if source:
            source = Path(source).name

        page = document.metadata.get("page_label")

        content = document.page_content

        if page:
            results.append(
                f"[Source: {source}, Page: {page}]\n{content}"
            )

            sources.append(
                {
                    "source": source,
                    "page": page,
                }
            )

        else:
            results.append(
                f"[Source: {source}]\n{content}"
            )

            sources.append(
                {
                    "source": source,
                }
            )

    return "\n\n".join(results)