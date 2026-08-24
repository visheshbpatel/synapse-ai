from pathlib import Path
import hashlib
import json

from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser

from components.prompt import prompt
from components.llm import model


DOCUMENTS_PATH = "data/documents"
UPLOADS_PATH = "data/uploads"

CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "synapse-ai"

INDEX_STATE_PATH = "data/index_state.json"

RELEVANCE_THRESHOLD = 1.0


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)



def _load_documents(directory: str):
    
    documents = []

    markdown_loader = DirectoryLoader(
        directory,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={
            "encoding": "utf-8",
            "autodetect_encoding": True,
        }
    )

    text_loader = DirectoryLoader(
        directory,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={
            "encoding": "utf-8",
            "autodetect_encoding": True,
        }
    )

    pdf_loader= DirectoryLoader(
        directory,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    documents.extend(markdown_loader.load())

    documents.extend(text_loader.load())

    documents.extend(pdf_loader.load())


    return documents



def _split_documents(documents):
    return text_splitter.split_documents(documents)



def _create_vector_store(chunks):

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME
    )

    return vector_store


def _index_document(vector_store, file_path: Path):

    documents = _prepare_document(file_path)

    chunks = _split_documents(documents)

    if not chunks:
        print(f"No text extracted from: {file_path}")
        return 0

    vector_store.add_documents(chunks)

    return len(chunks)


def index_documents():

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    failed_documents = []

    current_state = _get_current_document_state()
    previous_state = _load_index_state()

    changes = _get_document_changes(
        current_state,
        previous_state,
    )

    successful_state = previous_state.copy()

    # NEW documents
    for document in changes["new"]:

        file_path = Path(document["document_id"])

        print(f"Indexing new document: {file_path}")

        chunks_indexed = _index_document(
            vector_store,
            file_path,
        )

        if chunks_indexed == 0:
            failed_documents.append(str(file_path))
            print(f"Skipping state update for: {file_path}")
            continue

        successful_state[document["document_id"]] = {
            "file_hash": document["file_hash"]
        }

    # CHANGED documents
    for document in changes["changed"]:

        document_id = document["document_id"]
        file_path = Path(document_id)

        print(f"Updating document: {file_path}")

        _delete_document(
            vector_store,
            document_id,
        )

        chunks_indexed = _index_document(
            vector_store,
            file_path,
        )

        if chunks_indexed == 0:
            failed_documents.append(str(file_path))
            print(f"Skipping state update for: {file_path}")
            continue

        successful_state[document_id] = {
            "file_hash": document["file_hash"]
        }

    # DELETED documents
    for document in changes["deleted"]:

        document_id = document["document_id"]

        print(f"Deleting document: {document_id}")

        _delete_document(
            vector_store,
            document_id,
        )

        successful_state.pop(document_id, None)

    _save_index_state(successful_state)

    if failed_documents:
        print("\nIndexing completed with errors:")

        for document in failed_documents:
            print(f"  {document}")
    else:
        print("\nIndexing completed successfully")



def _delete_document(vector_store, document_id: str):

    vector_store.delete(
        where={
            "document_id":document_id
        }
    )


def get_retriever():

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k":4
        }
    )

    return retriever


def retrieve_documents(question):
    retriever = get_retriever()

    return retriever.invoke(question)


def _format_docs(documents):
    return "\n\n".join(
        doc.page_content
        for doc in documents
    )



def get_sources(documents):

    sources=[]

    for document in documents:

        metadata = document.metadata

        source = metadata.get("source")

        if not source:
            continue

        source_name = Path(source).name

        page = metadata.get("page_label")

        if page is not None:
            sources.append(
                {
                    "source": source_name,
                    "page": page,
                }
            )

        else:
            sources.append(
                {
                    "source": source_name
                }
            )

    return sources


rag_answer_chain = prompt | model | StrOutputParser()

def get_rag_response(question, history):

    documents = retrieve_documents(question)

    context = _format_docs(documents)

    answer_stream = rag_answer_chain.stream(
        {
            "context": context,
            "question": question,
            "history": history,
        }
    )

    sources = get_sources(documents)

    return answer_stream, sources


def _get_file_hash(file_path: str) -> str:

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def _get_document_id(file_path: str) -> str:

    return str(Path(file_path).resolve())


def _load_index_state() -> dict:

    state_path = Path(INDEX_STATE_PATH)

    if not state_path.exists():
        return {}

    with open(state_path, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_index_state(state: dict):

    state_path = Path(INDEX_STATE_PATH)

    state_path.parent.mkdir(parents=True, exist_ok=True)

    with open(state_path, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)


def _discover_documents() -> list[Path]:

    directories = [
        Path(DOCUMENTS_PATH),
        Path(UPLOADS_PATH),
    ]

    files = []

    for directory in directories:

        if not directory.exists():
            continue

        for file_path in directory.rglob("*"):

            if file_path.is_file() and file_path.suffix.lower() in {
                ".pdf",
                ".txt",
                ".md",
            }:
                files.append(file_path)


    return files


def _get_current_document_state() -> dict:

    current_state = {}

    for file_path in _discover_documents():

        document_id = _get_document_id(file_path)
        file_hash = _get_file_hash(file_path)

        current_state[document_id] = {
            "file_hash": file_hash
        }

    return current_state


def _get_document_changes(current_state: dict, previous_state: dict) -> dict:

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

        if current_metadata["file_hash"] == previous_metadata["file_hash"]:
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


def _add_indexing_metadata(document, document_id:str, file_hash:str):

    document.metadata["document_id"] = document_id
    document.metadata["file_hash"] = file_hash

    return document


def _load_document(file_path: Path):

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


def _prepare_document(file_path: Path):

    document_id = _get_document_id(file_path)
    file_hash = _get_file_hash(file_path)

    documents = _load_document(file_path)

    documents = [
        _add_indexing_metadata(
            document,
            document_id,
            file_hash,
        )
        for document in documents
    ]

    return documents



def list_documents() -> list[dict]:

    documents = []

    for file_path in _discover_documents():

        documents.append(

            {
                "name": file_path.name,
                "path": str(file_path)
            }
        )

    return documents


def delete_document(document_path: str):

    file_path = Path(document_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Document not found : {file_path}"
        )

    document_id = _get_document_id(file_path)

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    _delete_document(
        vector_store,
        document_id
    )

    state = _load_index_state()
    state.pop(document_id, None)
    _save_index_state(state)

    file_path.unlink()


def is_relevant(question: str) -> bool:

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    results = vector_store.similarity_search_with_score(
        question,
        k=1,
    )

    if not results:
        return False

    _, score = results[0]

    return score <= RELEVANCE_THRESHOLD

