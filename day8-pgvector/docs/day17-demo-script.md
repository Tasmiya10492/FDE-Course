# Day 17 — HR Policy Assistant Demo Script

## 1. Demo objective

Demonstrate the HR policy RAG assistant, its answers and citations, access
control, security hardening, and the fallback process when the model is slow,
an answer is unsupported, or a service is unavailable.

## 2. Start and verify the services

From the project directory:

```bash
docker compose up -d postgres
docker compose ps
```



Expected database health: HTTP 200 and database connected.

## 3. Demonstrate the browser interface

Open http://localhost:8000/ui.

Ask:
"What is the annual paid leave entitlement for a full-time employee?"

Explain that the assistant retrieves relevant policy chunks, generates an answer,
and displays citations. Verify that the citations support the answer.

## 4. Demonstrate abstention

Ask a question that is not covered by the available HR policies.

Expected response:

"I don't know based on the available HR policy information."

Explain that refusing to guess is safer than inventing HR policy.

## 5. Explain API authentication and permissions

The JSON endpoint is POST /ask and requires an X-API-Key header.

- Employee key maps to tenant main and role employee.
- HR key maps to tenant main and role HR administrator.
- Missing or invalid credentials are rejected.
- Missing or identical configured keys cause authentication to fail closed.

The browser UI uses session and CSRF validation. Its current ask handler uses
tenant_a and Employee role. Do not claim that the browser UI demonstrates
the HR administrator role.

Never expose real API keys in screenshots, recordings, or Git.

## 6. Fallback: model is slow

1. Explain that response time depends on local resources.
2. Avoid repeatedly submitting the same question.
3. Check Ollama:
   curl --max-time 5 http://localhost:11434/api/tags
4. Check that qwen3.5:2b is listed.
5. Continue with a previously verified example and its citations.
6. Do not claim database health proves model health.

## 7. Fallback: answer appears incorrect

1. Do not present the answer as authoritative.
2. Inspect citations and source documents.
3. Check whether retrieved material supports the answer.
4. If evidence remains insufficient, use the abstention response.
5. Escalate policy interpretation to the appropriate HR owner.

## 8. Fallback: network, database, or model unavailable

1. Check database:
   curl -i http://localhost:8000/health
2. Check Ollama:
   curl --max-time 5 http://localhost:11434/api/tags
3. If database health fails, inspect docker compose ps.
4. Inspect logs:
   docker compose logs --tail=50 postgres
5. Check the Ollama service and required models independently.
6. Tell the audience the assistant is temporarily unavailable.
7. Resume only after the relevant dependency is restored.

Important: /health checks PostgreSQL, not Ollama.

## 9. Security and hardening points

- CORS uses explicitly configured origins; wildcard origins are rejected.
- Security headers include CSP, nosniff, frame protection, and referrer policy.
- Rate limiting returns HTTP 429 with Retry-After.
- Request bodies have a size limit.
- Uploads have extension, size, and UTF-8 validation and server-generated filenames.
- Uploads are not automatically ingested.
- API authentication fails closed.
- Dependency and source scans are documented in the security triage report.
- The secret-removal drill demonstrates secret response and history cleanup.

## 10. Limitations and closing

- Rate limiting is in-memory and is not shared across multiple workers.
- Upload validation is not a malware scanner or general file sanitizer.
- Uploaded files are not automatically added to the RAG knowledge base.
- A healthy database does not guarantee model availability.
- Generated answers must be checked against citations and authoritative HR policies.

Closing statement:

"The goal is not just to generate an answer. The assistant must retrieve
permitted information, show its evidence, reject unsupported questions,
and fail safely when a dependency is unavailable."
