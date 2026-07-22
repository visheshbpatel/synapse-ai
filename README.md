# SynapseAI – RAG Foundation

## Overview

This PR integrates a complete Retrieval-Augmented Generation (RAG) pipeline into SynapseAI using LangChain.

The chatbot can now retrieve relevant information from a local knowledge base before generating responses, allowing it to answer questions grounded in indexed documents instead of relying only on the LLM.

---

## Features

- Modular RAG architecture
- Offline document indexing
- Markdown, Text, and PDF document support
- Recursive document chunking
- HuggingFace embeddings (`all-MiniLM-L6-v2`)
- Chroma vector database
- Similarity-based retrieval
- LCEL RAG pipeline
- Streaming responses
- Conversation history
- Context-aware prompting
- Graceful handling of unknown questions

---

## Project Structure

```text
components/
├── __init__.py
├── llm.py
├── prompt.py
└── rag.py

scripts/
├── __init__.py
└── index_documents.py

data/
├── documents/
└── chroma/

chatbot.py
```

---

## RAG Workflow

```text
Documents
    │
    ▼
Document Loaders
    │
    ▼
Text Splitter
    │
    ▼
Embeddings
    │
    ▼
Chroma Vector Store
    │
    ▼
Retriever
    │
    ▼
Prompt + Conversation History
    │
    ▼
LLM
    │
    ▼
Streaming Response
```

---

## Supported Document Types

- Markdown (`.md`)
- Text (`.txt`)
- PDF (`.pdf`)

---

## Components

### Document Loading

Documents are loaded using LangChain document loaders.

- DirectoryLoader
- TextLoader
- PyPDFLoader

---

### Text Splitting

Documents are split using:

- RecursiveCharacterTextSplitter

Configuration:

- Chunk Size: `1000`
- Chunk Overlap: `200`

---

### Embeddings

Embedding model:

```
sentence-transformers/all-MiniLM-L6-v2
```

Provider:

- HuggingFace Embeddings

---

### Vector Store

Vector database:

- Chroma

Persistence:

```
data/chroma/
```

---

### Retrieval

Retriever configuration:

- Similarity Search
- Top K = 4

---

### Prompt

The prompt combines:

- System instructions
- Retrieved context
- Conversation history
- User question

---

### LCEL Pipeline

The RAG chain is built using LangChain Expression Language (LCEL).

Pipeline:

```text
Question
      │
      ├──────────────┐
      ▼              ▼
 Retriever      Original Question
      │
      ▼
 Retrieved Context
      │
      └──────────────┐
                     ▼
                  Prompt
                     │
                     ▼
                    LLM
                     │
                     ▼
              Output Parser
```

---

## Indexing

Documents are indexed separately from the chatbot.

Run:

```bash
uv run python -m scripts.index_documents
```

This:

- Loads documents
- Splits documents
- Creates embeddings
- Builds the Chroma vector database

---

## Chat Flow

```text
User
   │
   ▼
Retriever
   │
   ▼
Relevant Context
   │
   ▼
Prompt
   │
   ▼
LLM
   │
   ▼
Response
```

---

## Verification

The RAG pipeline was validated by:

- Retrieving information from indexed documents
- Testing custom facts added to the knowledge base
- Confirming unknown questions return an appropriate fallback response
- Verifying retrieved context during development

---

## Future Improvements

- Source citations
- File upload from UI
- Metadata support
- Metadata filtering
- MMR retrieval
- Similarity threshold search
- MultiQueryRetriever
- Context compression
- Query rewriting
- Hybrid search
- Incremental indexing
- Knowledge base management