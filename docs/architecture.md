# Architecture

## Request flow

1. A user sends a request to the FastAPI application.
2. Authentication identifies the user.
3. Authorization checks whether the user can access the requested information.
4. The retrieval service searches permitted document chunks using pgvector.
5. The application uses retrieved context to prepare an answer.
6. The response includes supporting sources when available.
7. If evidence is insufficient, the application abstains instead of inventing an answer.

## Main components
- `src/`: application code and API routes.
- `sql/`: database schema and migrations.
- `tests/`: automated tests.
- PostgreSQL: application data and vector storage.
- Ollama: embedding and language-model services.
