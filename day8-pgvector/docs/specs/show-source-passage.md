# Feature Specification: Show the Source Passage

## 1. Problem

Users of the HR RAG assistant need to understand where an answer
comes from. A filename alone is insufficient because a document may
contain multiple passages about different topics.

Users need to see the exact policy passage used to generate an answer.

## 2. Objective

Expose the original retrieved policy passage alongside every citation
returned by the RAG service.

## 3. Functional requirements

1. Every citation must contain a chunk ID.
2. Every citation must contain the original source filename.
3. Every citation must contain the exact original chunk passage.
4. The passage must not be rewritten or paraphrased by the application.
5. Multiple citations must preserve the retrieval order.
6. Only chunks selected for the LLM context may be returned as citations.
7. If retrieval produces no usable evidence, the service must abstain
   and return an empty citation list.
8. If the model returns an empty answer, the service must abstain
   and return an empty citation list.
9. If the model explicitly abstains because it cannot answer, the
   service must return the standard abstention message and no citations.

## 4. Response contract

A successful response must have this structure:

- answer: generated answer as a string
- citations: list of citation objects

Each citation object must contain:

- chunk_id: database chunk identifier
- source: original document filename
- passage: exact original chunk content

Example:

{
  "answer": "Eligible employees can apply for annual leave.",
  "citations": [
    {
      "chunk_id": 43,
      "source": "HR001.txt",
      "passage": "Employees who complete the eligibility period can apply for annual leave."
    }
  ]
}

An abstention must return:

{
  "answer": "I don't know based on the available HR policy information.",
  "citations": []
}

## 5. Security requirements

- Source passages must come from the existing permission-filtered retrieval.
- The feature must not bypass tenant isolation.
- The feature must not bypass role-based access control.
- The feature must not retrieve arbitrary database chunks by ID.

## 6. Out of scope

- A web user interface for displaying citations.
- PDF or document download links.
- Highlighting passages inside original documents.
- Changes to the embedding model.
- Changes to the PostgreSQL schema.

## 7. Acceptance criteria

- A successful answer includes the exact source passage.
- Citation metadata matches the retrieved chunk.
- Multiple citations preserve their order.
- Context-budget exclusions do not appear as citations.
- Abstentions contain no citations.
- Automated tests verify these behaviours.
- An explicit model abstention returns no citations.
