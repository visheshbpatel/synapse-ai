# SynapseAI

An extensible AI chatbot built with LangChain, combining conversational AI, Retrieval-Augmented Generation (RAG), document management, and agent-based tools.

## Overview

SynapseAI is a Streamlit-based AI chatbot that can answer general questions, work with information from user-provided documents, and use external tools when additional information is required.

The current application combines:

* Conversational AI
* Retrieval-Augmented Generation (RAG)
* Document upload and management
* Incremental document indexing
* Chroma vector storage
* Agent-based tool calling
* Web search
* Weather information
* Current time lookup

The project is currently built around Streamlit and LangChain. A future goal is to separate the application, AI, and UI responsibilities and migrate the application to a FastAPI-based architecture.

## Features

### Conversational AI

SynapseAI can maintain conversation history during a Streamlit session and use previous messages when generating responses.

### Retrieval-Augmented Generation

SynapseAI can retrieve relevant information from indexed documents before generating an answer.

The RAG pipeline uses:

* Markdown (`.md`)
* Text (`.txt`)
* PDF (`.pdf`)
* Recursive text splitting
* Hugging Face embeddings
* Chroma vector store
* Similarity-based retrieval
* Context-aware prompting
* Source information from retrieved documents

### Document Management

Documents can be:

* Uploaded through the Streamlit interface
* Indexed into the vector store
* Listed from the application
* Deleted from the application

The indexing system also keeps track of document state using file hashes so that new, changed, unchanged, and deleted documents can be identified during indexing.

### Agent Tools

SynapseAI uses a LangChain agent with the following tools:

* **Time** — retrieves the current time for supported locations
* **Weather** — retrieves current weather information using OpenWeather
* **Documents** — lists documents currently available to SynapseAI
* **Web Search** — searches the web using Tavily

### Web Search

The web search tool can search for general or news-related information and supports:

* Search topics
* Optional time ranges
* Search result titles and content
* Publication dates when available
* Source URLs

## Current Architecture

The current application flow is:

```text
User
  │
  ▼
Streamlit UI
  │
  ▼
Application Logic
  │
  ▼
Document Relevance Check
  │
  ├──────── Relevant ────────► RAG Pipeline
  │                              │
  │                              ▼
  │                         Chroma Retriever
  │                              │
  │                              ▼
  │                       Retrieved Context
  │                              │
  │                              ▼
  │                             Prompt
  │                              │
  │                              ▼
  │                             LLM
  │
  └────── Not Relevant ─────► Agent
                                │
                ┌───────────────┼────────────────┐
                ▼               ▼                ▼
              Time           Weather         Documents
                                                   │
                                                   ▼
                                              Web Search
```

The current application determines whether a question is relevant to the indexed document collection using Chroma similarity search.

Relevant questions are handled by the RAG pipeline. Questions that are not considered relevant are handled by the agent.

> **Note:** `components/router.py` currently contains a structured chat/RAG router, but it is not currently connected to the main Streamlit application flow. The architecture will be revisited during the planned codebase refactoring phase.

## RAG Pipeline

The current RAG pipeline follows this general flow:

```text
Documents
    │
    ▼
Document Loading
    │
    ▼
Text Splitting
    │
    ▼
Hugging Face Embeddings
    │
    ▼
Chroma Vector Store
    │
    ▼
Similarity Retrieval
    │
    ▼
Retrieved Context
    │
    ▼
Prompt
    │
    ▼
LLM
    │
    ▼
Response + Sources
```

### Document Loading

Supported document types:

* Markdown (`.md`)
* Text (`.txt`)
* PDF (`.pdf`)

Documents are loaded from:

```text
data/documents/
data/uploads/
```

### Text Splitting

Documents are split using `RecursiveCharacterTextSplitter`.

Current configuration:

```text
Chunk size:    1000
Chunk overlap: 200
```

### Embeddings

The project currently uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

through LangChain's Hugging Face integration.

### Vector Store

SynapseAI uses Chroma as its vector store.

Current configuration:

```text
Persistence: data/chroma/
Collection:  synapse-ai
```

### Retrieval

The current retriever uses similarity search with:

```text
k = 4
```

Before selecting the RAG pipeline, the application also performs a similarity search to determine whether the question is relevant to the indexed documents.

## Incremental Indexing

SynapseAI keeps indexing state in:

```text
data/index_state.json
```

Document contents are hashed using SHA-256.

During indexing, documents are classified as:

```text
New
Changed
Unchanged
Deleted
```

This allows the indexer to:

* Add new documents
* Re-index changed documents
* Leave unchanged documents alone
* Remove deleted documents from the vector store

Documents are indexed using:

```bash
uv run python -m scripts.index_documents
```

## Project Structure

```text
synapse-ai/
│
├── components/
│   ├── tools/
│   │   ├── documents.py
│   │   ├── time.py
│   │   ├── weather.py
│   │   └── web_search.py
│   │
│   ├── __init__.py
│   ├── agent.py
│   ├── chat.py
│   ├── llm.py
│   ├── prompt.py
│   ├── rag.py
│   └── router.py
│
├── data/
│   ├── documents/
│   ├── uploads/
│   └── chroma/
│
├── scripts/
│   ├── __init__.py
│   └── index_documents.py
│
├── .env.example
├── .gitignore
├── LICENSE
├── chatbot.py
├── pyproject.toml
└── uv.lock
```

### Important Components

| Component                    | Responsibility                                                       |
| ---------------------------- | -------------------------------------------------------------------- |
| `chatbot.py`                 | Streamlit application and user interaction                           |
| `components/llm.py`          | LLM configuration                                                    |
| `components/rag.py`          | Document indexing, retrieval, RAG responses, and document management |
| `components/agent.py`        | LangChain agent configuration                                        |
| `components/chat.py`         | General conversational chain                                         |
| `components/router.py`       | Structured chat/RAG routing logic                                    |
| `components/prompt.py`       | RAG prompt                                                           |
| `components/tools/`          | Agent tools                                                          |
| `scripts/index_documents.py` | Document indexing entry point                                        |

Some components currently exist but are not fully integrated into the main application flow. These responsibilities will be reviewed during the planned refactoring phase.

## Tech Stack

### Language

* Python 3.12+

### AI / LLM

* LangChain
* LangChain OpenAI integration
* OpenRouter

### RAG

* LangChain
* Chroma
* Hugging Face
* Sentence Transformers
* PyPDF

### Tools

* Tavily
* OpenWeather

### Application

* Streamlit

### Configuration

* python-dotenv

## Environment Variables

Create a local `.env` file in the project root.

The required environment variables are:

```env
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=

OPENWEATHER_API_KEY=

TAVILY_API_KEY=
```

Never commit the actual `.env` file or API keys to Git.

A template is provided in:

```text
.env.example
```

## Installation

### Requirements

* Python 3.12+
* Git
* `uv`

Clone the repository:

```bash
git clone https://github.com/visheshbpatel/synapse-ai.git
cd synapse-ai
```

Install dependencies:

```bash
uv sync
```

Create your environment file:

```text
.env
```

and configure the required API keys and OpenRouter settings.

## Index Documents

Place documents in:

```text
data/documents/
```

or upload them through the Streamlit interface.

To index documents manually:

```bash
uv run python -m scripts.index_documents
```

The indexer supports:

```text
.pdf
.txt
.md
```

## Run SynapseAI

Start the Streamlit application with:

```bash
uv run streamlit run chatbot.py
```

The application provides:

* Chat interface
* Document upload
* Document indexing
* Document listing
* Document deletion
* RAG responses
* Agent-based tool use

## Usage

### General Questions

Ask a general question through the chat interface.

Questions that are not considered relevant to the indexed documents are handled by the agent.

### Document Questions

Add supported documents and index them.

Questions related to the indexed documents can then be answered using retrieved document context.

### Tools

The agent can use available tools when appropriate:

```text
Time
Weather
Documents
Web Search
```

## Roadmap

### Current Focus

* Improve project documentation
* Establish open-source contribution standards
* Improve repository structure where necessary
* Deeply understand the existing architecture
* Refactor responsibilities and module boundaries

### Future

* Separate UI, application, AI, RAG, and tool responsibilities
* Migrate the application from Streamlit to FastAPI
* Introduce API endpoints
* Build a dedicated frontend
* Improve testing and maintainability
* Continue improving the RAG and agent architecture

The FastAPI migration will be performed after the existing architecture has been thoroughly understood and refactored rather than simply converting Streamlit code directly into API endpoints.

## Contributing

Contributions are welcome.

Before contributing, please read:

```text
CONTRIBUTING.md
```

The project uses GitHub Issues and Pull Requests for feature proposals, bug reports, and contributions.

## License

SynapseAI is distributed under the license included in the repository:

```text
LICENSE
```
