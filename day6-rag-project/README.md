# Day 6 - Local RAG Project

## Overview

This project implements a local Retrieval-Augmented Generation (RAG)
system for answering questions about HR policies.

It uses Ollama for local embeddings and language model inference,
and ChromaDB as the persistent vector database.

## Architecture

1. Read HR policy documents from `data/hr_policies/`.
2. Split documents into chunks using three strategies:
   - Fixed-size chunking
   - Sentence-based chunking
   - Paragraph-based chunking
3. Generate embeddings using `nomic-embed-text`.
4. Store document chunks and embeddings in ChromaDB.
5. Convert user questions into embeddings.
6. Retrieve the top three relevant chunks.
7. Generate answers using `qwen3.5:2b` and retrieved policy context.

## Technology

- Python 3.14+
- Ollama
- ChromaDB
- nomic-embed-text
- qwen3.5:2b
- tiktoken
- pytest

## Project structure

```text
day6-rag-project/
├── data/
│   └── hr_policies/       # 20 HR policy documents
├── docs/                  # Learning and evaluation notes
├── results/
│   ├── rag_answers.json
│   ├── retrieval_evaluation.json
│   └── token_counts.json
├── src/
│   ├── answer_questions.py
│   ├── build_index.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── evaluate.py
│   ├── rag.py
│   ├── token_lab.py
│   └── vector_store.py
├── tests/
├── requirements.txt
└── README.md
