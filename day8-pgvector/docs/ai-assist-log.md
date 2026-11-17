# Day 9 AI-Assistance Log

## Project

HR Policy RAG Assistant

## Purpose

This log records how AI assistance was used during the Day 9 development
work. AI suggestions were reviewed and tested rather than accepted blindly.

## 1. RAG Service Design

**Area:** Retrieval, context assembly and answer generation

**AI assistance:**
- Helped explain the responsibilities of the RAG service.
- Suggested an ordered flow for retrieval, filtering, context assembly,
  answer generation and citation creation.
- Explained why tenant and role permissions must remain enforced during
  retrieval.

**My work and review:**
- Reviewed the existing retrieval implementation.
- Checked that the RAG service reused the permission-filtered retrieval
  function.
- Reviewed the generated implementation and its behaviour.

**Verification:**
- Ran the RAG service tests.
- Ran the complete test suite.

## 2. Test-First Development: Source Passage Feature

**Area:** Showing exact source passages in citations

**AI assistance:**
- Helped identify missing test cases for explicit model abstention and
  context-budget exclusions.
- Explained why chunks excluded from the model context must not be returned
  as citations.
- Helped structure the feature specification and implementation plan.

**My work and review:**
- Reviewed the acceptance criteria.
- Added and reviewed the missing tests.
- Checked that citations contain the original passage, source filename
  and chunk ID.

**Verification:**
- Confirmed the new tests exposed the missing behaviour before the fix.
- Ran the complete test suite: 40 tests passed.

## 3. Golden Set and Retrieval Evaluation

**Area:** Retrieval quality measurement

**AI assistance:**
- Helped explain Recall@k and how to interpret retrieval misses.
- Helped review the evaluation results and distinguish retrieval recall
  from answer correctness.
- Helped identify why similarity distance alone cannot establish that
  a question is answerable.

**My work and review:**
- Reviewed the golden-set questions and expected chunk IDs.
- Examined the retrieval results.
- Documented the evaluation metrics and limitations.

**Verification:**
- Generated the Day 9 retrieval evaluation report.
- Checked that the high-level design uses the same evaluation figures.

## 4. High-Level Design Documentation

**Area:** Architecture and design decisions

**AI assistance:**
- Helped organise the high-level design into problem, users, data,
  architecture, technologies, security, evaluation and future improvements.
- Helped explain the reasons for the main design choices.

**My work and review:**
- Reviewed the document against the actual project implementation.
- Checked the model names, database technology, context budget and
  evaluation figures.
- Documented limitations rather than describing the prototype as
  production-ready.

## 5. Verification and Human Review

AI assistance was used as a development and learning aid. I reviewed the
suggestions, ran the tests and checked the implementation.

Verification performed:

- Complete test suite: 40 passed.
- Ruff lint checks: passed.
- Ruff formatting checks: passed.
- Git whitespace check: passed.

## 6. Lessons Learned

- Writing tests first helps expose missing behaviour before implementation.
- A citation should identify the exact evidence supplied to the model.
- Retrieval quality and answer quality are different measurements.
- Similarity distance alone cannot prove that evidence supports an answer.
- AI-generated suggestions must be reviewed and verified before use.
