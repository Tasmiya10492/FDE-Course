# Day 15 — Agent Framework Decision Matrix

**Date:** 20 November 2026
**Project:** Employee HR Policy Assistant

## Objective

Choose an appropriate approach for building and operating an employee-facing
HR policy assistant. The system must protect tenant and role-based access,
retrieve policy information with citations, abstain when evidence is missing,
and remain testable and maintainable.

## Evaluation criteria and weights

Scores use a 1–5 scale, where 5 is strongest. Weights reflect this project's
priorities and total 100%.

| Criterion | Weight | What is evaluated |
|---|---:|---|
| Licence and usage fit | 15% | Licence clarity and suitability for the intended internal use |
| Security and control | 25% | Ability to enforce authentication, authorization, secrets handling, and safe execution |
| Maintainability | 25% | Testability, debugging, code ownership, version control, and long-term support |
| Integration and orchestration | 15% | APIs, databases, external systems, and workflow connectivity |
| Fit for this use case | 20% | Suitability for a grounded, permission-aware HR assistant |

## Weighted scores

| Approach | Licence (15%) | Security (25%) | Maintainability (25%) | Integration (15%) | Use-case fit (20%) | Weighted total |
|---|---:|---:|---:|---:|---:|---:|
| Plain Python / FastAPI | 5 | 5 | 4 | 3 | 5 | **4.45 / 5** |
| LangGraph | 5 | 4 | 4 | 4 | 4 | **4.15 / 5** |
| Langflow | 5 | 3 | 3 | 4 | 4 | **3.65 / 5** |
| n8n | 2 | 3 | 3 | 5 | 5 | **3.55 / 5** |

Weighted total = sum of (criterion score × criterion weight) divided by 100.

## Findings

### 1. Plain Python / FastAPI

- Provides direct control over authentication, role checks, tenant filtering,
  retrieval, citations, and abstention.
- Supports conventional automated tests, code review, logging, and version control.
- Requires developers to implement and maintain orchestration and integrations.
- Best choice for the security-critical RAG and policy-answering core.

### 2. LangGraph

- Suitable for stateful, multi-step agent workflows with explicit control flow.
- Keeps orchestration in code and supports testing individual workflow steps.
- Adds framework concepts and complexity that may not be necessary for a
  straightforward retrieval-and-answer flow.
- Consider if the assistant later needs branching, human approval, retries,
  or persistent multi-step agent state.

### 3. Langflow

- Visual flow building makes components and connections easier to inspect
  and demonstrate.
- Custom components can connect the visual workflow to the existing FastAPI
  service.
- Visual configuration and custom components still require security review,
  version control, and automated testing.
- Useful for prototyping and demonstrating an agent workflow, rather than
  replacing the permission-aware API.

### 4. n8n

- Strong visual workflow automation and integration capabilities.
- Useful for webhooks, request validation, routing, and connecting business
  systems.
- Credential management, workflow permissions, instance hardening, and
  deployment governance must be handled carefully.
- n8n uses a Sustainable Use License rather than a conventional OSI-approved
  open-source licence; confirm the applicable terms for the intended use.

## Recommendation

Use **plain Python / FastAPI as the authoritative HR RAG service**. Keep
authentication, tenant and role authorization, retrieval filtering, citations,
and abstention in this tested API.

Use **n8n for external workflow integration**, such as receiving employee
requests through a secured webhook and routing validated requests.

Use **Langflow for visual prototyping and demonstration**, with a custom
component calling the secured FastAPI endpoint.

Adopt **LangGraph only when** the product requires more complex stateful
agent orchestration that justifies its additional framework complexity.

## Security and governance conditions

- Keep API keys, passwords, and encryption keys out of source control and
  exported workflow files.
- Keep development services bound to localhost unless an approved deployment
  requires otherwise.
- Enforce authorization in the API; do not rely on a visual workflow to
  provide the security boundary.
- Review dependencies, framework advisories, licence terms, and deployment
  configuration before production use.
- Re-run automated tests and security checks after changes.

## Scoring note

These scores are reasoned estimates for this learning project, not independent
security audits or vendor rankings. Security scores assess the practical
control available in the proposed implementation; they do not certify any
framework or product as secure. Licence terms and dependency licences should
be checked against the exact versions and deployment model before adoption.
