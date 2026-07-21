from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader


def load_documents():
    
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