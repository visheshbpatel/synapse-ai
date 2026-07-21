from components.rag import load_documents, split_documents

documents = load_documents()
chunks = split_documents(documents)

print(len(documents))
print(len(chunks))

print(chunks[0].page_content)



