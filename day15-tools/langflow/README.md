# Langflow (day 15, part 2)

## What it is
Langflow is a **visual builder for AI flows and agents**: you drag components (a chat input, a
model, tools, a prompt, an output) onto a canvas, connect them with lines, and run the result in
a built-in chat window (the *Playground*). A finished flow can be called from your own code
through an API. It is open source (MIT licence), and runs on your own machine.

## When to use it (and when not)
- **Use** when a non-developer must see or change the flow, or to try an idea in minutes.
- **Do not use** for rules that must be tested (access checks, money, personal data): keep those in
  your Python service and let the flow call it (Playbook ORCH-03).

## Security first (read before you start)
Langflow has had **critical security flaws that attackers actually used** (remote code execution
without logging in). They were fixed in later releases, and new ones have been found since. So:

1. Install the **latest patched release** and read the advisories first:
   <https://github.com/langflow-ai/langflow/security/advisories>
2. Run it on **localhost only** (`127.0.0.1`). Never open it to the internet.
3. Keep **login on**: set `LANGFLOW_AUTO_LOGIN=false` and a strong superuser password from the environment.
4. Do not give untrusted input to components that run code.
5. Export flows to Git **without secrets**; search the file before you commit it.

(Rules ORCH-08, ORCH-09, ORCH-13.)

## Start it (choose one)

**A. With uv (simplest on a laptop).** Check which Python releases Langflow supports on the official
installation page before you start: <https://docs.langflow.org/get-started-installation>

```bash
uv venv langflow-env
# Windows PowerShell:  langflow-env\Scripts\activate     Linux/macOS: source langflow-env/bin/activate
uv pip install langflow
# keep login on, and use a strong password that you keep out of files:
export LANGFLOW_AUTO_LOGIN=false
export LANGFLOW_SUPERUSER=admin
export LANGFLOW_SUPERUSER_PASSWORD=<choose-a-strong-password>
uv run langflow run      # then open http://127.0.0.1:7860
```

**B. With Docker Compose.** Use `docker-compose.yml` in this folder after replacing its
placeholders (see `.env.example`), copying `.env.example` to `.env`, then:

```bash
docker compose up -d
docker compose logs -f langflow
# open http://127.0.0.1:7860
```

**C. Langflow Desktop** exists too (an app for macOS and Windows). It is fine for a quick try; the
two methods above are the ones we use because you can pin the version.

## Build the flow (about 90 minutes)
Goal: the same assistant as in the earlier labs, as a flow that calls YOUR service.

1. Create a new flow from the **Simple Agent** template (official quickstart: <https://docs.langflow.org/get-started-quickstart>).
2. In **Settings > Model Providers** add your own provider key (never paste keys into a flow file) and pick a model.
3. Add a tool that calls your FastAPI `/ask` endpoint (an *API request* or *custom* component; check the component list of your version).
4. Add instructions: answer only from the tool's result, say "I don't know" otherwise.
5. Open the **Playground** and test five questions from your golden set, including one that must be refused.
6. Call the flow from outside: **Share > API access** shows a ready `curl` snippet (the flow runs at `http://127.0.0.1:7860/api/v1/run/<FLOW_ID>` and needs a Langflow API key made in Settings).
7. **Export** the flow (JSON) to your repository after you have searched it for secrets.
8. Write the **choice memo** (30 minutes): a one-page weighted decision matrix comparing plain code, LangGraph, n8n and Langflow by licence, security record, who can maintain it and when to use each. Agree the criteria and weights first (template in the Field Kit).

## Check yourself
- Is login on and the address `127.0.0.1`?
- Does a refused question really get "I don't know"?
- Did you search the exported file for keys before committing?

## Framework decision

See the [Day 15 decision matrix](../DECISION-MATRIX.md) for the comparison and recommendation.
