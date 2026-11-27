# Project Overview

This project is a Retrieval-Augmented Generation (RAG) application for HR policy information.

## Main capabilities
- Retrieve relevant HR policy chunks from PostgreSQL with pgvector.
- Generate responses using an Ollama language model.
- Apply authentication and authorization controls.
- Record relevant security and audit events.
- Return an abstention response when the available evidence is insufficient.

## Main application
The application code is in `day8-pgvector/`.

## Technology
- Python and FastAPI
- PostgreSQL and pgvector
- Ollama for embeddings and language-model responses
- Pytest, Ruff and Pyright
- Docker and GitHub Actions
