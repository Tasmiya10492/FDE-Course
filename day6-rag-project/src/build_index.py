from pathlib import Path

from src.chunking import (
    fixed_size_chunks,
    sentence_chunks,
    paragraph_chunks,
)
from src.embeddings import generate_embedding
from src.vector_store import store_chunks


PROJECT_ROOT = Path(__file__).resolve().parent.parent
POLICY_FOLDER = PROJECT_ROOT / "data" / "hr_policies"


# Three different chunking approaches.
CHUNKING_METHODS = {
    "fixed": fixed_size_chunks,
    "sentence": sentence_chunks,
    "paragraph": paragraph_chunks,
}


def build_index():
    """
    Read all policy files, split them using three methods,
    generate embeddings and store them in ChromaDB.
    """

    policy_files = sorted(POLICY_FOLDER.glob("*.txt"))

    if not policy_files:
        raise FileNotFoundError(f"No policy files found in {POLICY_FOLDER}")

    print(f"Found {len(policy_files)} policy documents.")

    for method_name, chunk_function in CHUNKING_METHODS.items():
        collection_name = f"hr_{method_name}_chunks"

        all_chunks = []

        print(f"\nProcessing method: {method_name}")

        for policy_file in policy_files:
            text = policy_file.read_text(encoding="utf-8")

            # Apply the selected chunking method.
            if method_name == "fixed":
                chunks = chunk_function(
                    text,
                    chunk_size=300,
                    overlap=50,
                )

            elif method_name == "sentence":
                chunks = chunk_function(
                    text,
                    chunk_size=300,
                )

            else:
                chunks = chunk_function(text)

            # Generate an embedding for every chunk.
            for index, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)

                all_chunks.append(
                    {
                        "id": f"{policy_file.stem}_{method_name}_{index}",
                        "document": chunk,
                        "embedding": embedding,
                        "metadata": {
                            "policy_id": policy_file.stem,
                            "source_file": policy_file.name,
                            "chunking_method": method_name,
                            "chunk_index": index,
                        },
                    }
                )

        # Store all chunks for this method.
        store_chunks(collection_name, all_chunks)

        print(f"Total chunks for {method_name}: {len(all_chunks)}")


if __name__ == "__main__":
    build_index()
