
# Day 13 — n8n Workflow Orchestration

## What it is

n8n is a workflow automation platform. It connects services and automates processes using visual workflows.

In this project, n8n receives support requests through a webhook, validates the incoming data, calls the existing FastAPI application, and returns the response.

The main architectural principle is:

**n8n orchestrates; Python handles application logic.**

## Architecture

```text
Client / Simulator
        |
        | POST /webhook/coe-support
        | X-Webhook-Secret
        v
   n8n Webhook
        |
        v
   Code Node
   Validate request
        |
        v
     IF Node
      /    \
 Invalid   Valid
   |        |
   v        v
 HTTP 400  HTTP Request
              |
              | POST /ask
              v
          FastAPI
              |
              v
        Answer + Citations
              |
              v
       Respond to Webhook
              |
              v
         Client
```

## Technology stack

- n8n: workflow orchestration
- Docker Compose: container management
- PostgreSQL: persistent n8n database
- FastAPI: Python backend
- Python: request simulators and automated tests

## Project files

```text
day13-n8n/
├── .env                  # Local secrets; never commit
├── .env.example          # Environment variable template
├── README.md             # Project documentation
├── docker-compose.yml    # n8n and PostgreSQL services
├── test_simulator.py     # Automated tests
└── webhook_simulator.py  # Production/test webhook simulator
```

## n8n licence

This project uses the self-hosted n8n Community Edition.

n8n uses a Sustainable Use License rather than a conventional open-source licence. Review the official terms before using n8n in a customer-facing or commercial deployment.

Official documentation:

https://docs.n8n.io/n8n-community-license/sustainable-use-license/

For licensing questions, contact license@n8n.io or seek legal guidance.

## Environment configuration

The `.env` file contains local configuration and secrets.

Required variables:

```dotenv
TIMEZONE=Asia/Kolkata
POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=<your-postgres-password>
N8N_ENCRYPTION_KEY=<your-encryption-key>
WEBHOOK_SECRET=<your-webhook-secret>
```

Use `.env.example` as a template.

Important security practices:

- Never commit `.env` to Git.
- Never paste passwords, encryption keys, or webhook secrets into chat or documentation.
- Keep `.env` permissions restricted.
- Back up the existing `N8N_ENCRYPTION_KEY` securely. Do not regenerate it casually because n8n uses it to encrypt stored credentials.
- Use strong, unique values for passwords and secrets.

## Starting the services

Run these commands from the Day 13 project directory:

```bash
cd ~/FDE-Course/day13-n8n
```

Start n8n and PostgreSQL:

```bash
docker compose up -d
```

Check container status:

```bash
docker compose ps
```

View n8n logs:

```bash
docker compose logs -f n8n
```

View PostgreSQL logs:

```bash
docker compose logs -f postgres
```

Validate the Compose configuration:

```bash
docker compose config --quiet
```

Open n8n in your browser:

http://127.0.0.1:5678

## Useful Docker Compose commands

| Command | Purpose |
|---|---|
| `docker compose up -d` | Start services in the background |
| `docker compose ps` | Check service status |
| `docker compose logs -f n8n` | Follow n8n logs |
| `docker compose logs -f postgres` | Follow PostgreSQL logs |
| `docker compose config --quiet` | Validate Compose configuration |
| `docker compose pull` | Download updated images |
| `docker compose down` | Stop and remove containers and network |

The named volumes preserve application data when containers are recreated. Avoid using `docker compose down -v` unless you intentionally want to delete the persistent volumes and their data.

### Updating the containers

Before updating, review the image versions and any relevant release notes.

A typical update sequence is:

```bash
docker compose pull
docker compose down
docker compose up -d
docker compose ps
```

Do not update production services without an appropriate backup and validation plan.

## FastAPI connection

The existing FastAPI application runs outside Docker on port `8000`.

Its entry point is:

```text
app.main:app
```

The n8n container reaches the host application using:

```text
http://host.docker.internal:8000
```

The health endpoint is:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

The support endpoint is:

```text
POST /ask
```

Expected request structure:

```json
{
  "question": "How many annual leave days are available?"
}
```

The current FastAPI `/ask` endpoint is still a placeholder. It currently returns:

```json
{
  "answer": "I don't know. No sources are available yet.",
  "citations": []
}
```

This means the n8n workflow integration is working, but it does not yet provide a real HR policy answer.

## Workflow: COE Support Webhook

The workflow is named:

**COE Support Webhook**

It receives support requests, validates them, calls FastAPI, and returns the result.

### 1. Webhook node

Configuration:

- HTTP Method: `POST`
- Path: `coe-support`
- Authentication: `Header Auth`
- Credential: `COE Webhook Authentication`
- Header name: `X-Webhook-Secret`
- Response mode: `Using Respond to Webhook Node`

The credential value must match the `WEBHOOK_SECRET` configured in `.env`.

### 2. Code node — request validation

The Code node validates the incoming payload.

Checks include:

- `user` must be a non-empty string.
- `message` must be a non-empty string.
- `message` must not exceed 2000 characters.

The node trims whitespace and produces:

- `isValid`: whether the request passed validation.
- `validationError`: validation failure details.

Invalid requests are sent to the rejection response.

### 3. IF node

The IF node checks:

```javascript
{{ $json.isValid }}
```

- True branch: continue to FastAPI.
- False branch: return HTTP 400.

### 4. HTTP Request node — FastAPI

Configuration:

- Method: `POST`
- URL: `http://host.docker.internal:8000/ask`
- Send Body: enabled
- Body Content Type: JSON

Request body:

```javascript
{{ {
  "question": $json.message
} }}
```

The node forwards the validated support message to FastAPI.

### 5. Respond to Webhook — invalid request

Invalid requests receive HTTP 400.

Response structure:

```json
{
  "status": "rejected",
  "error": "Validation error message"
}
```

### 6. Respond to Webhook — successful request

Successful requests receive HTTP 200.

Response structure:

```json
{
  "status": "ok",
  "answer": "Answer returned by FastAPI",
  "citations": []
}
```

The answer and citations are taken from the FastAPI response.

### 7. Workflow publication

The workflow is published in n8n.

The production webhook URL is:

```text
http://127.0.0.1:5678/webhook/coe-support
```

The test webhook URL is:

```text
http://127.0.0.1:5678/webhook-test/coe-support
```

The test URL works when the Webhook node is listening for a test event. Use the production URL for the published workflow.

## Running the webhook simulator

The simulator sends requests to the webhook and checks the HTTP responses.

First, make sure:

1. Docker Compose services are running.
2. The n8n workflow is published if using the production URL.
3. The FastAPI application is running on port `8000`.
4. The `.env` file contains the correct webhook secret.

From the project directory, load the environment variables:

```bash
set -a
source .env
set +a
```

### Production webhook

Set the production URL:

```bash
export WEBHOOK_URL="http://127.0.0.1:5678/webhook/coe-support"
```

Run the simulator:

```bash
python webhook_simulator.py
```

### Test webhook

First open the workflow in n8n and select **Listen for test event** on the Webhook node.

Then, in the terminal, set the test URL:

```bash
export WEBHOOK_URL="http://127.0.0.1:5678/webhook-test/coe-support"
```

Run:

```bash
python webhook_simulator.py
```

The test URL is intended for test executions, whereas the production URL is used by the published workflow.

## Test cases and results

The production simulator was tested against eight cases.

| Test case | Expected status | Result |
|---|---:|---|
| Good message | 200 | Passed |
| Missing secret header | 403 | Passed |
| Wrong secret | 403 | Passed |
| Missing field | 400 | Passed |
| Empty message | 400 | Passed |
| Very long message | 400 | Passed |
| Wrong data type | 400 | Passed |
| Injection attempt | 200 | Passed |

The injection attempt currently receives HTTP 200 because this workflow validates the request structure and authentication, not the semantic safety of the message.

Prompt-injection detection and AI-agent safety are separate concerns to address in the later agent work.

### Run automated tests

From the repository root:

```bash
cd ~/FDE-Course
uv run pytest -q
```

Expected result for the current Day 13 tests:

```text
2 passed
```

Run Ruff lint checks:

```bash
uv run ruff check .
```

Check formatting:

```bash
uv run ruff format --check .
```

Check Git whitespace errors:

```bash
git diff --check
```

## Error handling and reliability

The current workflow includes request validation and HTTP responses for invalid requests.

The following are additional reliability improvements to implement and verify before considering the workflow production-ready:

- Add an Error Trigger workflow for workflow execution failures.
- Add structured failure logging with useful context and request identifiers.
- Configure an alert mechanism for important failures.
- Configure retries for temporary downstream failures, such as transient FastAPI connection errors.
- Define appropriate timeout and failure-response behavior.
- Introduce idempotency if the workflow later performs write operations.

Idempotency is not currently applicable because this workflow does not perform write operations.

## Security considerations

- Webhook authentication uses a stored n8n Header Auth credential.
- Secrets are stored in `.env`, which is excluded from Git.
- Incoming request fields are validated before calling FastAPI.
- Message length is limited to 2000 characters.
- n8n and PostgreSQL data are stored in persistent Docker volumes.
- n8n is bound to `127.0.0.1:5678` for local access.
- Do not expose the webhook publicly without appropriate HTTPS, access control, rate limiting, and security review.
- Do not treat successful request validation as protection against prompt injection.

## Exporting and version-controlling the workflow

Before handing in the project:

1. Export the `COE Support Webhook` workflow as JSON from n8n.
2. Save the exported file in this project directory.
3. Inspect the export for passwords, tokens, webhook secrets, and other sensitive values.
4. Remove or replace any sensitive values before committing.
5. Verify that the workflow can be imported without exposing credentials.
6. Commit the sanitized workflow export to Git.

Do not commit `.env` or any actual secret values.

## Day 13 learning outcomes

By completing this project, I practised:

- Running n8n and PostgreSQL using Docker Compose.
- Understanding persistent volumes and container configuration.
- Creating an authenticated webhook.
- Validating incoming JSON payloads.
- Using IF nodes to control workflow paths.
- Calling a FastAPI endpoint from n8n.
- Returning structured webhook responses.
- Testing success and failure scenarios.
- Understanding the separation between workflow orchestration and application logic.
- Managing environment variables and secrets safely.

## Future integration: AI agent

The current workflow connects n8n to the existing FastAPI `/ask` endpoint.

In the later AI-agent work, the backend can be extended to provide:

- Retrieval-based HR policy answers.
- Source citations.
- Safe abstention when information is unavailable.
- Prompt-injection protection.
- More robust error handling and observability.

The intended responsibility split remains:

**n8n handles orchestration; Python handles retrieval, reasoning, and application logic.**

## Self-check questions

1. Why do we use n8n instead of implementing every integration directly in Python?
2. What is the purpose of Header Auth in the Webhook node?
3. Why do we validate incoming requests before calling FastAPI?
4. What is the difference between a test webhook URL and a production webhook URL?
5. Why does the n8n container use `host.docker.internal` to reach FastAPI?
6. Why should secrets be stored in `.env` rather than committed to Git?
7. What is the purpose of a Respond to Webhook node?
8. Why are retries useful for temporary downstream failures?
9. Why should n8n orchestrate the workflow while Python owns application logic?
10. Why does accepting an injection-attempt request not mean the AI system is protected against prompt injection?
