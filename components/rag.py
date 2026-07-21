from langchain_community.document_loaders import DirectoryLoader, TextLoader


def load_documents():
    laoder = DirectoryLoader(
        "data/documents",
        glob="**/*.md",
        loader_cls=TextLoader
    )

    return laoder.load()