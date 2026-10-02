# SynapseAI

SynapseAI is a Streamlit-based AI assistant built with LangChain and LangGraph.

It combines conversational AI with document search, web search, weather and time tools, persistent conversations, user authentication, and per-user document storage.

## Features

* Conversational AI with streaming responses
* LangGraph-based agent orchestration
* Persistent multi-chat conversations
* User authentication with password hashing
* User-scoped document storage
* RAG over uploaded PDF, TXT, and Markdown files
* Chroma vector store
* Hugging Face embeddings
* Incremental document indexing
* Source references for document-based answers
* Web search with Tavily
* Current weather with OpenWeather
* Current time lookup
* LangSmith tracing support

## How It Works

SynapseAI uses LangGraph to orchestrate the conversation.

```text
User
  │
  ▼
Streamlit
  │
  ▼
LangGraph Agent
  │
  ├── Direct response
  │
  └── Tool call
        │
        ├── Time
        ├── Weather
        ├── Documents
        ├── Document Search
        └── Web Search
```

The model decides when a tool is required. Document search is implemented as a tool rather than as a separate RAG route.

### Document Search

```text
File
 │
 ▼
Loader
 │
 ▼
Text Splitter
 │
 ▼
Hugging Face Embeddings
 │
 ▼
Chroma
 │
 ▼
Similarity Retrieval
 │
 ▼
Relevant Chunks
 │
 ▼
LLM
 │
 ▼
Answer + Sources
```

Documents are split using `RecursiveCharacterTextSplitter` with a chunk size of `1000` and an overlap of `200`.

Embeddings use:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Document retrieval uses similarity search with `k=4` and filters results by the current user's ID.

### Incremental Indexing

Each user has an indexing state stored under:

```text
data/users/<user_id>/index_state.json
```

Files are tracked using SHA-256 hashes and classified as:

```text
New
Changed
Unchanged
Deleted
```

Only the required vector-store changes are applied when documents are indexed.

## Persistence

SynapseAI uses two SQLite databases for different purposes.

### Application Database

```text
data/synapse.db
```

Stores:

* Users
* Documents
* Conversations

### LangGraph Checkpoint Database

```text
data/checkpoints.db
```

Stores graph state associated with conversation `thread_id`s.

User IDs are passed through LangGraph runtime context so document-related tools operate on the current user's data.

## Project Structure

```text
synapse-ai/
│
├── components/
│   ├── tools/
│   │   ├── documents.py
│   │   ├── search_documents.py
│   │   ├── time.py
│   │   ├── weather.py
│   │   └── web_search.py
│   │
│   ├── auth.py
│   ├── context.py
│   ├── conversation.py
│   ├── database.py
│   ├── document.py
│   ├── graph.py
│   ├── llm.py
│   ├── rag.py
│   ├── ui.py
│   └── user.py
│
├── data/
│   ├── chroma/
│   ├── users/
│   ├── checkpoints.db
│   └── synapse.db
│
├── .env.example
├── .gitignore
├── LICENSE
├── chatbot.py
├── pyproject.toml
└── uv.lock
```

### Core Components

| File                         | Responsibility                                                                                      |
| ---------------------------- | --------------------------------------------------------------------------------------------------- |
| `chatbot.py`                 | Streamlit application, authentication flow, chat UI, document management, and conversation handling |
| `components/graph.py`        | LangGraph workflow, tool routing, streaming, and checkpointing                                      |
| `components/rag.py`          | Document loading, indexing, vector storage, retrieval, and document deletion                        |
| `components/database.py`     | SQLite connection and application database initialization                                           |
| `components/user.py`         | User creation and authentication                                                                    |
| `components/conversation.py` | Conversation metadata and history                                                                   |
| `components/document.py`     | Document metadata stored in SQLite                                                                  |
| `components/auth.py`         | Password hashing and verification                                                                   |
| `components/context.py`      | User context passed into LangGraph                                                                  |
| `components/tools/`          | Tools available to the agent                                                                        |
| `components/llm.py`          | LLM configuration                                                                                   |
| `components/ui.py`           | Streamlit theme and reusable UI components                                                          |

## Tech Stack

### Application

* Python 3.12+
* Streamlit

### AI

* LangChain
* LangGraph
* LangChain OpenAI integration
* LangSmith

### RAG

* Chroma
* Hugging Face
* Sentence Transformers
* PyPDF

### Tools

* Tavily
* OpenWeather
* timezone.io

### Storage

* SQLite

### Package Management

* uv

## Setup

### Requirements

* Python 3.12+
* Git
* [uv](https://docs.astral.sh/uv/)

Clone the repository:

```bash
git clone https://github.com/visheshbpatel/synapse-ai.git
cd synapse-ai
```

Install dependencies:

```bash
uv sync
```

Create a `.env` file from `.env.example` and configure the required API keys.

Example:

```env
GROQ_API_KEY=
GROQ_BASE_URL=

OPENWEATHER_API_KEY=

TAVILY_API_KEY=

TIMEZONE_API_TOKEN=

LANGSMITH_API_KEY=
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=synapse-ai
```
---
## API Keys

SynapseAI uses several external services. Add the required API keys to your `.env` file.

| Variable | Service | Where to get it |
|----------|---------|-----------------|
| `GROQ_API_KEY` | Groq | https://console.groq.com/keys |
| `GROQ_BASE_URL` | Groq | `https://api.groq.com/openai/v1` |
| `OPENWEATHER_API_KEY` | OpenWeather | https://home.openweathermap.org/api_keys |
| `TAVILY_API_KEY` | Tavily | https://app.tavily.com/ |
| `TIMEZONE_API_TOKEN` | Timezone API | https://timezoneapi.io/ |
| `LANGSMITH_API_KEY` | LangSmith | https://smith.langchain.com/settings |
| `LANGSMITH_TRACING` | LangSmith | Set to `true` |
| `LANGSMITH_PROJECT` | LangSmith | Set to `synapse-ai` |


One small point: **not every variable is necessarily required for the basic chat to work**. The keys correspond to optional capabilities such as web search, weather, timezone lookup, and LangSmith tracing. 

---

## Run

Start the application with:

```bash
uv run streamlit run chatbot.py
```

After starting SynapseAI:

1. Create an account or log in.
2. Upload PDF, TXT, or Markdown documents from the sidebar.
3. Index the documents.
4. Ask questions about the uploaded content.
5. Use the same chat to access the available tools.

## Notes

* Uploaded files and indexing state are stored locally under `data/users/`.
* Chroma data and SQLite databases are local application data and are ignored by Git.
* API keys must be kept in `.env` and should never be committed.

## License

SynapseAI is licensed under the MIT License.
