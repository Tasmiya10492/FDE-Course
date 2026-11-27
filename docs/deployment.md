# Deployment Guide

## Prerequisites
- Docker and Docker Compose
- Python 3.14 and uv for local development
- PostgreSQL with pgvector
- Ollama if running the local model workflow

## Configuration
Configure the required database connection and model settings through environment variables or the local `.env` file.

Do not commit `.env` files, passwords, API keys or other secrets.

## Database
Initialize the database using `sql/schema.sql`, then apply migrations in order.

## Application
Use the repository Dockerfile and Compose configuration for the container-based workflow. Verify that the database is healthy and that the application can connect before testing API endpoints.

## Verification
Run the automated tests and health checks after deployment. Review application logs for startup or database errors.
