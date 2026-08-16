from pathlib import Path

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

    pdf_laoder = DirectoryLoader(
        directory,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    documents.extend(markdown_loader.load())

    documents.extend(text_loader.load())

    documents.extend(pdf_laoder.load())


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


def index_documents():

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    try:
        vector_store.delete_collection()
    except Exception:
        pass

    documents = (
        _load_documents(DOCUMENTS_PATH)
        + _load_documents(UPLOADS_PATH)
    )
    chunks = _split_documents(documents)

    _create_vector_store(chunks)

    print("Vector database indexed successfully")


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


