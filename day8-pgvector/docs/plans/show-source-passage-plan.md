# Implementation Plan: Show the Source Passage

## Goal

Verify and strengthen the existing RAG citation response so that users
receive the exact source passage supporting an answer.

## Existing implementation

The current `ask()` function in `src/rag_service.py` already returns:

- chunk_id
- source
- passage

The citation passage is copied from the retrieved chunk content.

## Implementation approach

1. Review the current citation response implementation.
2. Compare current behaviour against the feature specification.
3. Identify acceptance criteria not adequately covered by tests.
4. Write tests for any missing behaviour before changing implementation.
5. Run the new tests and confirm that a test fails for the intended reason.
6. Implement only the missing behaviour.
7. Run the focused test suite.
8. Run the complete test suite.
9. Run Ruff and inspect the Git diff.

## Design decisions

- Reuse the existing `ask()` service.
- Reuse permission-filtered retrieval.
- Do not introduce a second database query for citations.
- Preserve original passage text.
- Keep the existing response structure.
- Avoid unnecessary changes to working code.

## Validation

The feature is accepted when all specification acceptance criteria
are covered by automated tests and the existing RAG service tests pass.
