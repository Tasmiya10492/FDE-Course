# High-Level Design: HR Policy RAG Assistant

## 1. Problem Statement (Draft - Validate with Client)

Employees and HR staff need a reliable way to find answers to HR policy
questions without manually searching multiple policy documents.

The answers should be grounded in the actual policy content. Users should
also be able to inspect the source passage supporting an answer.

The system must respect tenant and role-based access permissions. If the
available policy information does not support an answer, the assistant
should clearly say that it does not know.

## 2. Intended Users

- Employees: Ask questions about HR policies and understand applicable rules.
- HR staff: Help employees find policy information and verify answers.
- System administrators: Maintain policy documents and access permissions.

## 3. Data Used and Why

The prototype uses 20 HR policy text documents.

The document content provides the actual policy information needed to answer
questions.

Additional metadata supports controlled access:

- Tenant information identifies which organisation owns or can access data.
- Role information controls which users can access particular documents.
- Sharing permissions allow explicitly authorised cross-tenant access.

Each document is split into smaller chunks so that relevant passages can
be retrieved without sending entire documents to the language model.

## 4. High-Level Architecture

### A. Document Ingestion

1. Read HR policy text documents.
2. Split documents into smaller chunks.
3. Generate embeddings using the local nomic-embed-text model.
4. Store chunk content, source information, permission metadata and embeddings
   in PostgreSQL with pgvector.

### B. Storage

PostgreSQL stores the policy chunks and associated metadata.

The pgvector extension supports vector similarity search. This allows the
system to retrieve policy passages based on the meaning of a question rather
than relying only on exact keyword matches.

### C. Retrieval

When a user asks a question:

1. Generate an embedding for the question.
2. Search for semantically similar policy chunks.
3. Apply tenant and role-based permission filters.
4. Return the most relevant chunks with their IDs, source filenames and
   similarity distances.

### D. RAG Answer Generation

The ask() service:

1. Retrieves relevant policy chunks.
2. Applies a similarity-distance threshold.
3. Selects chunks within the configured context-token budget.
4. Sends the selected passages and question to the local Ollama model.
5. Requests an answer grounded only in the supplied policy passages.
6. Returns citations containing the chunk ID, source filename and exact
   original passage.

If no usable evidence is available, or the model explicitly abstains, the
service returns:

"I don't know based on the available HR policy information."

## 5. Main Components and Technologies

| Component | Technology | Responsibility |
|---|---|---|
| Application logic | Python | Ingestion, retrieval and RAG service |
| Vector storage | PostgreSQL + pgvector | Store and search policy embeddings |
| Embedding model | nomic-embed-text | Convert text into 768-dimensional vectors |
| Language model | qwen3.5:2b via Ollama | Generate evidence-based answers |
| Data validation | Existing Python validation and tests | Check expected inputs and behaviour |
| Evaluation | Python scripts and golden set | Measure retrieval performance |

## 6. Trust, Security and Answer Quality

- Tenant and role permissions are enforced during retrieval.
- The RAG service uses only retrieved, permission-filtered passages.
- Context is restricted by a configurable token budget.
- Citations identify the exact source chunk and preserve its original text.
- The assistant abstains when usable evidence is unavailable or the model
  explicitly says it does not know.
- Automated tests verify citations, context budgeting and abstention.

## 7. Evaluation Results

The Day 9 golden set contains 15 questions:

- 12 answerable questions.
- 3 questions that should not be answered from the available evidence.

Chunk-level retrieval results:

| Metric | Result |
|---|---:|
| Recall@1 | 8/12 (66.67%) |
| Recall@3 | 10/12 (83.33%) |
| Recall@5 | 11/12 (91.67%) |

These results measure whether the expected source chunk is retrieved. They
do not independently measure answer correctness or prove that the assistant
always abstains correctly.

## 8. Important Design Decisions

### PostgreSQL with pgvector

Chosen to keep policy data, metadata and vector search within the same
database technology.

### Local Ollama models

Chosen for local development and to avoid depending on a hosted language
model API for this prototype.

### Chunk-based retrieval

Chosen because smaller passages make it easier to retrieve relevant evidence
and provide precise citations.

### Permission-filtered retrieval

Chosen so that users cannot retrieve policy content outside their authorised
tenant and role access.

### Citations and abstention

Chosen to make answers easier to verify and reduce unsupported responses.

### Context budget

Chosen to limit how much retrieved content is sent to the language model.
The current token count is an approximate character-based estimate, not an
exact model tokenizer count.

## 9. Out of Scope

The current prototype does not include:

- A production web or chat user interface.
- Policy authoring or document approval workflows.
- Document download links or passage highlighting.
- Live integration with an HR management system.
- Production monitoring, deployment and enterprise authentication.
- A guarantee that every generated answer is factually correct.

## 10. Future Improvements

- Improve retrieval for questions where the expected chunk is missed.
- Use model-specific token counting instead of the current estimate.
- Add more difficult and realistic evaluation questions.
- Evaluate answer correctness and citation support separately from retrieval.
- Add production-grade authentication, monitoring and deployment controls.

## 11. Current Status

This is a learning prototype demonstrating document ingestion, vector
retrieval, tenant and role-based access control, RAG answer generation,
citations, abstention and retrieval evaluation.
