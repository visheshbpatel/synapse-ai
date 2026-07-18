# SynapseAI

SynapseAI is a modern AI workspace built with **LangChain** and **Streamlit**.

The project is developed by implementing LangChain concepts incrementally while building real-world AI applications. Each feature is added as a separate milestone, keeping the codebase simple, maintainable, and easy to understand.

> **Current Status:** Early development (v0.1)

---

## Features

* Interactive chat interface built with Streamlit
* Real-time streaming responses
* Multi-turn conversation history
* OpenRouter integration
* Modern LangChain Expression Language (LCEL) pipeline
* Clean and minimal architecture

---

## Tech Stack

* Python
* Streamlit
* LangChain
* OpenRouter
* python-dotenv

---

## Project Structure

```text
synapse-ai/
├── chatbot.py          # Main chatbot application
├── .env                # Environment variables (not committed)
├── pyproject.toml      # Project dependencies
├── uv.lock             # Dependency lock file
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd synapse-ai
```

### 2. Create a virtual environment

```bash
uv venv
```

### 3. Activate the virtual environment

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
uv sync
```

### 5. Create a `.env` file

```env
OPENROUTER_API_KEY=your_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 6. Run the application

```bash
streamlit run chatbot.py
```

---

## LangChain Concepts Implemented

* Models
* Prompt Templates
* ChatPromptTemplate
* Output Parsers
* LCEL
* Runnables (`invoke()` and `stream()`)
* Streaming responses
* MessagesPlaceholder
* Conversation history

---

## Development Workflow

This project follows a Feature Branch Workflow.

```text
main
│
develop
│
feature/*
```

Each feature is developed in its own branch, reviewed through a Pull Request, and merged into `develop`.

---

## Roadmap

* [x] Basic chatbot
* [x] Streamlit chat interface
* [x] Streaming responses
* [x] Conversation history
* [ ] Prompt engineering
* [ ] RAG
* [ ] Tools
* [ ] Agents
* [ ] LangGraph

---

## License

This project is licensed under the MIT License.
