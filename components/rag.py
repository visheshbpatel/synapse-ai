from operator import itemgetter

from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser

from components.prompt import prompt
from components.llm import model


CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "synapse-ai"


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)



def _load_documents():
    
    documents = []

    markdown_laoder = DirectoryLoader(
        "data/documents",
        glob="**/*.md",
        loader_cls=TextLoader
    )

    text_loader = DirectoryLoader(
        "data/documents",
        glob="**/*.txt",
        loader_cls=TextLoader
    )

    pdf_laoder = DirectoryLoader(
        "data/documents",
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    documents.extend(markdown_laoder.load())

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

    documents = _load_documents()
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


def _format_docs(documents):
    return "\n\n".join(
        doc.page_content
        for doc in documents
    )



def get_rag_chain():

    retriever = get_retriever()

    parser = StrOutputParser()

    chain = (
        {
            "context": itemgetter("question") | retriever | _format_docs,
            "question": itemgetter("question"),
            "history": itemgetter("history"),
        }
        | prompt | model | parser
    )

    return chain