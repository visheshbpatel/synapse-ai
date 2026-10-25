from pathlib import Path
import hashlib
import json
from typing import TypedDict

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from components.document import (
    get_document_by_filename,
    delete_document as delete_document_record,
)


# Configuration

USERS_DATA_PATH = Path("data/users")

CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "synapse-ai"


# Shared Objects

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

_embeddings = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )

    return _embeddings


def get_user_paths(user_id: int):
    user_path = USERS_DATA_PATH / str(user_id)

    return {
        "uploads": user_path / "uploads",
        "index_state": user_path / "index_state.json",
    }


# Vector Store

def _get_vector_store() -> Chroma:
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=_get_embeddings(),
        collection_name=COLLECTION_NAME,
    )


# Document Handling

def _discover_documents(user_id: int):
    paths = get_user_paths(user_id)

    uploads_path = paths["uploads"]

    uploads_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return list(uploads_path.glob("*"))


def _load_document(file_path: Path) -> list[Document]:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(file_path))

    elif suffix in {".txt", ".md"}:
        loader = TextLoader(
            str(file_path),
            encoding="utf-8",
            autodetect_encoding=True,
        )

    else:
        raise ValueError(
            f"Unsupported document type: {file_path.suffix}"
        )

    return loader.load()


def _add_indexing_metadata(
    document: Document,
    user_id: int,
    document_id: str,
    file_hash: str,
) -> Document:
    document.metadata["user_id"] = user_id
    document.metadata["document_id"] = document_id
    document.metadata["file_hash"] = file_hash

    return document


def _prepare_document(
    file_path: Path,
    user_id: int,
) -> list[Document]:
    document_id = _get_document_id(file_path)
    file_hash = _get_file_hash(file_path)

    documents = _load_document(file_path)

    documents = [
        _add_indexing_metadata(
            document,
            user_id,
            document_id,
            file_hash,
        )
        for document in documents
    ]

    return documents


def _split_documents(
    documents: list[Document],
) -> list[Document]:
    return text_splitter.split_documents(documents)


def list_documents(user_id: int) -> list[dict]:
    documents = []

    for file_path in _discover_documents(user_id):
        documents.append(
            {
                "name": file_path.name,
                "path": str(file_path),
            }
        )

    return documents


# Index State

def _get_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(
            lambda: file.read(8192),
            b"",
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def _get_document_id(file_path: Path) -> str:
    return str(file_path.resolve())


def _load_index_state(user_id: int) -> dict:
    state_path = get_user_paths(user_id)["index_state"]

    if not state_path.exists():
        return {}

    try:
        with open(
            state_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except json.JSONDecodeError:
        print(
            f"Warning: Invalid index state file: {state_path}"
        )
        return {}


def _save_index_state(
    user_id: int,
    state: dict,
) -> None:
    state_path = get_user_paths(user_id)["index_state"]

    state_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        state_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=4,
        )


def _get_current_document_state(
    user_id: int,
) -> dict:
    current_state = {}

    for file_path in _discover_documents(user_id):
        document_id = _get_document_id(file_path)
        file_hash = _get_file_hash(file_path)

        current_state[document_id] = {
            "file_hash": file_hash,
        }

    return current_state


def _get_document_changes(
    current_state: dict,
    previous_state: dict,
) -> dict:
    new_documents = []
    changed_documents = []
    unchanged_documents = []
    deleted_documents = []

    for document_id, current_metadata in current_state.items():
        document = {
            "document_id": document_id,
            "file_hash": current_metadata["file_hash"],
        }

        if document_id not in previous_state:
            new_documents.append(document)
            continue

        previous_metadata = previous_state[document_id]

        if (
            current_metadata["file_hash"]
            == previous_metadata["file_hash"]
        ):
            unchanged_documents.append(document)

        else:
            changed_documents.append(document)

    for document_id in previous_state:
        if document_id not in current_state:
            deleted_documents.append(
                {
                    "document_id": document_id,
                }
            )

    return {
        "new": new_documents,
        "changed": changed_documents,
        "unchanged": unchanged_documents,
        "deleted": deleted_documents,
    }


# Indexing

class IndexResult(TypedDict):
    indexed: list[str]
    changed: list[str]
    deleted: list[str]
    unchanged: list[str]
    failed: list[str]

def _delete_document(
    vector_store: Chroma,
    document_id: str,
) -> None:
    vector_store.delete(
        where={
            "document_id": document_id,
        }
    )


def _index_document(
    vector_store: Chroma,
    file_path: Path,
    user_id: int,
) -> int:
    documents = _prepare_document(
        file_path,
        user_id,
    )

    chunks = _split_documents(documents)

    if not chunks:
        print(
            f"No text extracted from: {file_path}"
        )
        return 0

    vector_store.add_documents(chunks)

    return len(chunks)


def index_documents(user_id: int) -> IndexResult:
    vector_store = _get_vector_store()

    result: IndexResult = {
        "indexed": [],
        "changed": [],
        "deleted": [],
        "unchanged": [],
        "failed": [],
    }

    failed_documents = []

    current_state = _get_current_document_state(user_id)
    previous_state = _load_index_state(user_id)

    changes = _get_document_changes(
        current_state,
        previous_state,
    )

    successful_state = previous_state.copy()

    # New documents

    for document in changes["new"]:
        file_path = Path(
            document["document_id"]
        )

        print(
            f"Indexing new document: {file_path}"
        )

        chunks_indexed = _index_document(
            vector_store,
            file_path,
            user_id,
        )

        if chunks_indexed == 0:
            result["failed"].append(
                str(file_path)
            )
            continue

        successful_state[
            document["document_id"]
        ] = {
            "file_hash": document["file_hash"],
        }

        result["indexed"].append(
            document["document_id"]
        )

    # Changed documents

    for document in changes["changed"]:
        document_id = document["document_id"]
        file_path = Path(document_id)

        print(
            f"Updating document: {file_path}"
        )

        try:
            chunks_indexed = _index_document(
                vector_store,
                file_path,
                user_id,
            )

            if chunks_indexed == 0:
                result["failed"].append(
                    document_id
                )
                continue

            _delete_document(
                vector_store,
                document_id,
            )

            successful_state[document_id] = {
                "file_hash": document["file_hash"],
            }

            result["changed"].append(
                document_id
            )

        except Exception as error:
            print(
                f"Failed to update document: {file_path} — {error}"
            )

            result["failed"].append(
                document_id
            )

    # Deleted documents

    for document in changes["deleted"]:
        document_id = document["document_id"]

        print(
            f"Deleting document: {document_id}"
        )

        _delete_document(
            vector_store,
            document_id,
        )

        successful_state.pop(
            document_id,
            None,
        )

        result["deleted"].append(
            document_id
        )

    # Unchanged documents

    for document in changes["unchanged"]:
        result["unchanged"].append(
            document["document_id"]
        )

    _save_index_state(
        user_id,
        successful_state,
    )

    if result["failed"]:
        print("\nIndexing completed with errors:")

        for document in result["failed"]:
            print(f"  {document}")

    else:
        print("\nIndexing completed successfully")

    return result



def delete_document(
    user_id: int,
    filename: str,
) -> None:
    document = get_document_by_filename(
        user_id,
        filename,
    )

    if document is None:
        raise FileNotFoundError(
            f"Document not found: {filename}"
        )

    uploads_path = get_user_paths(user_id)["uploads"]
    file_path = uploads_path / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Document file not found: {filename}"
        )

    document_path = _get_document_id(
        file_path
    )

    vector_store = _get_vector_store()

    _delete_document(
        vector_store,
        document_path,
    )

    state = _load_index_state(user_id)

    state.pop(
        document_path,
        None,
    )

    _save_index_state(
        user_id,
        state,
    )

    file_path.unlink()

    delete_document_record(
        user_id=user_id,
        document_id=document["id"],
    )


# Retrieval

def get_retriever(user_id: int):
    vector_store = _get_vector_store()

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4,
            "filter": {
                "user_id": user_id,
            },
        },
    )

    return retriever


def retrieve_documents(
    user_id: int,
    question: str,
) -> list[Document]:
    retriever = get_retriever(user_id)

    return retriever.invoke(question)
