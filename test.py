from components.rag import load_documents

documents = load_documents()

print(len(documents))

# for docs in documents:
#     print(docs.metadata)