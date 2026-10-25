# SynapseAI Backend

FastAPI backend for SynapseAI, built with SQLAlchemy 2, PostgreSQL, pgvector, Alembic, and JWT authentication.

## Features

- User registration and login
- Argon2 password hashing
- JWT-based authentication
- PostgreSQL database with pgvector support
- Database migrations using Alembic
- Health and database-readiness endpoints
- Automated tests using pytest

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- A PostgreSQL database with the `vector` extension enabled
- Neon PostgreSQL account, or a local PostgreSQL instance with pgvector

## Environment Setup

From the `backend/` directory, install the dependencies:

```powershell
uv sync
```

Create `backend/.env` from `.env.example` and configure:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection URL for development |
| `TEST_DATABASE_URL` | Separate PostgreSQL connection URL for automated tests |
| `JWT_SECRET` | Secret used to sign JWT access tokens |

Use SQLAlchemy's psycopg driver URL format:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

For Neon, use the direct connection URL rather than the pooled URL. Keep credentials private and never commit `.env`.

Generate a JWT secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Database Setup

Enable pgvector on the development and test databases:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Apply migrations:

```powershell
uv run alembic upgrade head
```

To reverse all application migrations on the development database when intentionally testing rollback:

```powershell
uv run alembic downgrade base
```

**Warning:** Downgrading to `base` removes the application tables managed by these migrations. Never run destructive migration commands against Neon `main`.

## Run the API

Start the development server:

```powershell
uv run uvicorn app.main:app --reload
```

Open the interactive API documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Basic health check |
| `GET` | `/health/ready` | Checks database readiness |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Authenticate and receive a JWT |
| `GET` | `/auth/me` | Return the authenticated user's profile |

Login accepts JSON containing `email` and `password`. Authenticated requests must include:

```text
Authorization: Bearer <access_token>
```

## Database Schema

| Table | Purpose |
|---|---|
| `users` | User accounts and password hashes |
| `documents` | Uploaded document metadata and indexing status |
| `chunks` | Document chunks, embeddings, and full-text search data |
| `conversations` | User-owned conversations; UUID IDs are designed to serve as LangGraph thread IDs |
| `api_keys` | Hashed API key metadata and revocation state |

### Schema Design Notes

- **Duplicated `chunks.user_id`:** lets retrieval queries filter chunks by owner directly, without first joining the documents table. A composite foreign key ensures that the chunk's owner matches its document's owner.
- **Generated `tsv` column and GIN index:** PostgreSQL generates a searchable `tsvector` from chunk content. The GIN index accelerates full-text search.
- **LangGraph checkpoint tables:** these are managed by LangGraph's checkpointer and should not be managed by the application's Alembic migrations.
- **Direct Neon URL:** using a direct connection avoids compatibility issues with prepared statements and the planned PostgreSQL checkpointer.

## Testing

Run the tests from the `backend/` directory:

```powershell
uv run pytest
```

The test suite requires a separate `TEST_DATABASE_URL`. It must not point to the same database as `DATABASE_URL`. The tests reset application tables, so configure it to use the dedicated test database only.

## Code Quality

Run Ruff's checks and formatter:

```powershell
uv run ruff check .
uv run ruff format --check .
```

## Current Scope

This backend foundation includes authentication, database models, migrations, health checks, and automated tests. Document ingestion, pgvector retrieval workflows, LangGraph chat endpoints, evaluation, guardrails, and deployment are planned for later phases.
