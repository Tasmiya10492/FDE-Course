# ChromaDB vs pgvector Comparison

## 1. Objective

Compare ChromaDB and PostgreSQL pgvector for retrieving relevant
HR policy documents in a Retrieval-Augmented Generation (RAG) system.

## 2. Evaluation setup

Both evaluations use:

- 20 HR policy documents.
- The same source document content.
- Ollama embedding model: nomic-embed-text.
- 768-dimensional embeddings.
- Paragraph-based chunking.
- 141 paragraph chunks.
- The same 10 evaluation questions.
- Top 3 retrieved chunks (Hit@3).

## 3. Results

| Metric | Day 6 ChromaDB | Day 8 pgvector |
|---|---:|---:|
| Documents | 20 | 20 |
| Paragraph chunks | 141 | 141 |
| Evaluation questions | 10 | 10 |
| Successful hits | 10 | 10 |
| Hit@3 accuracy | 100% | 100% |

## 4. Interpretation

Both vector databases achieved 100% Hit@3 accuracy on the
10-question evaluation.

This means the expected HR policy was present among the top
three retrieved results for every question.

The evaluation shows that pgvector can achieve the same retrieval
accuracy as the existing ChromaDB implementation for this dataset.

## 5. Important limitations

- This evaluation uses a relatively small dataset of 20 documents.
- Hit@3 measures whether the expected policy appears in the top
  three results. It does not measure the quality of the generated answer.
- The evaluation does not establish which database performs better
  at larger scale.
- The pgvector retrieval timings include embedding generation.
  Equivalent ChromaDB timings were not collected, so a database-only
  performance comparison has not yet been established.

## 6. Conclusion

For this HR policy dataset and evaluation set, both ChromaDB and
pgvector achieved 100% Hit@3 accuracy.

PostgreSQL pgvector provides an alternative that combines relational
data storage, vector similarity search, and SQL-based tenant and
role access filtering in one database.

Further testing with larger datasets and controlled latency
measurements would be needed to compare scalability and performance.
