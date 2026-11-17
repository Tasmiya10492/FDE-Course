from pathlib import Path

import chromadb


# Store the vector database inside the results folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "results" / "chroma_db"


def get_collection(collection_name: str):
    """
    Create or retrieve a ChromaDB collection.
    """

    client = chromadb.PersistentClient(path=str(DB_PATH))

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def store_chunks(collection_name: str, chunks: list[dict]) -> None:
    """
    Store document chunks, embeddings and metadata in ChromaDB.
    """

    if not chunks:
        return

    collection = get_collection(collection_name)

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["document"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )

    print(f"Stored {len(chunks)} chunks in collection: {collection_name}")


def search_chunks(
    collection_name: str,
    query_embedding: list[float],
    top_k: int = 3,
) -> list[dict]:
    """
    Search ChromaDB for the most relevant chunks.
    """

    collection = get_collection(collection_name)

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for index in range(len(results["ids"][0])):
        matches.append(
            {
                "id": results["ids"][0][index],
                "document": results["documents"][0][index],
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index],
            }
        )

    return matches
