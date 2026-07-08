# 🦉 Owl Brain — Personal AI Knowledge Platform

A personal knowledge management platform powered by AI. Import ChatGPT conversations, auto-extract knowledge, store with vector embeddings (pgvector), and retrieve via RAG.

## Architecture

```
owl-brain/
│
├── app/
│   ├── config/              # Configuration via pydantic-settings
│   ├── database/            # SQLAlchemy async engine & session
│   ├── models/              # SQLAlchemy ORM models
│   ├── services/            # Business logic layer
│   ├── providers/           # Abstraction layer
│   │   ├── llm/             # LLM providers (DeepSeek, etc.)
│   │   └── embedding/       # Embedding providers (BGE, etc.)
│   ├── importer/            # Data importers (ChatGPT, etc.)
│   ├── extractor/           # Knowledge extraction pipeline
│   ├── retrieval/           # RAG retrieval engine
│   └── api/                 # FastAPI routes
│
├── tests/                   # pytest test suite
├── docs/                    # Documentation
├── prompts/                 # Prompt templates
├── scripts/                 # Utility scripts
├── docker/                  # Docker ancillary files
└── .devcontainer/           # VS Code Dev Container config
```

### Key Design Decisions

- **LLM Provider Abstraction** — Not tied to OpenAI. Default provider is DeepSeek.
- **pgvector** — Vector similarity search on PostgreSQL.
- **Async All The Way** — SQLAlchemy async engine + async session for non-blocking I/O.
- **uv** — Fast Python package manager for dependency management.

## Development Environment

- **Python** 3.12+
- **Database** PostgreSQL 16 + pgvector
- **Container** Docker + Dev Containers (VS Code)

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows)
- [VS Code](https://code.visualstudio.com/) with Dev Containers extension

### Get Started

```bash
# 1. Clone the repository
git clone https://github.com/your-username/owl-brain.git
cd owl-brain

# 2. Copy environment file
cp .env.example .env
# Edit .env with your API keys

# 3. Start services via Docker Compose
docker compose up -d

# 4. Verify PostgreSQL is healthy
docker compose ps
```

### Enter the Dev Container

1. Open the project folder in VS Code
2. Press `F1` → **Dev Containers: Reopen in Container**
3. Or click the green button in the bottom-left corner → **Reopen in Container**

### Inside the Container

```bash
# Check Python version
python --version

# Check dependencies are installed
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Apply database migrations (when models are ready)
uv run alembic upgrade head
```

### Manual Docker Access

```bash
# Enter the app container shell
docker compose exec app bash

# Or if already running
docker exec -it owl-app bash
```

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://owl:owl_password@postgres:5432/owl_brain` |
| `LLM_PROVIDER` | LLM provider name | `deepseek` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | — |
| `DEEPSEEK_MODEL` | DeepSeek model name | `deepseek-chat` |
| `EMBEDDING_PROVIDER` | Embedding model provider | `bge` |

## License

MIT
