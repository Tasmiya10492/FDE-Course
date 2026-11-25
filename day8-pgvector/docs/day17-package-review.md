# Day17 Package Verification and Slopsquatting Review

## Objective

Evaluate ten AI-suggested Python package names before considering them
as project dependencies. No candidate package was installed.

## Verification method

- Queried the official PyPI JSON API.
- Checked package existence and earliest release upload date.
- Checked PyPI maintainer information and project links.
- Did not install any candidate.

## Candidate decision table

| # | Package | Exists? | Owner | Maintainer | First upload date | Decision |
|---|---|---|---|---|---|---|
| 1 | fastapi | Yes | Not separately displayed | tiangolo | 2018-12-08 | Existing; verify source and need |
| 2 | pydantic-settings | Yes | Pydantic | dmontagu | 2019-08-19 | Existing; verify source and need |
| 3 | psycopg | Yes | Not separately displayed | piro | 2021-08-30 | Existing; verify source and need |
| 4 | pgvector | Yes | Not separately displayed | ankane | 2021-06-12 | Existing; verify source and need |
| 5 | chromadb | Yes | Not separately displayed | jeff_chroma | 2023-02-09 | Existing; verify source and need |
| 6 | ollama | Yes | Not separately displayed | jmorganca | 2024-01-12 | Existing; verify source and need |
| 7 | python-multipart | Yes | Not separately displayed | Kludex | 2013-03-26 | Existing; verify source and need |
| 8 | uvicorn | Yes | Not separately displayed | Kludex | 2017-06-05 | Existing; verify source and need |
| 9 | fastapi-limter | No (404) | N/A | N/A | N/A | Reject; suspicious misspelling |
| 10 | pydantic-setting | No (404) | N/A | N/A | N/A | Reject; suspicious singular variant |

## Review questions

1. Does the package exist on official PyPI?
2. Does its purpose match the intended functionality?
3. Who owns it, if PyPI displays an owner?
4. Who maintains it?
5. When was its first release uploaded?
6. Is there a linked source repository?
7. Is the name suspiciously similar to another established package?
8. Would I approve it? Why?

## Security decision

Existence on PyPI does not automatically establish trustworthiness.
Verify identity, maintainers, source, release history, purpose,
security posture, and compatibility before adding a dependency.

Reject unchecked packages. No candidate was installed.
