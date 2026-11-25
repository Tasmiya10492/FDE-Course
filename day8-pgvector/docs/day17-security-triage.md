# Day17 Security Triage Report

## 1. Scope

This review covers the Day17 security hardening work for the HR Policy RAG
API. It includes application security checks, dependency scanning, static
analysis, secret scanning, HTTP security headers, and focused tests.

A clean automated scan does not prove that the application is completely
secure. Results below are limited to the tools, rules, code, and environment
tested.

## 2. Automated scan results

| Tool / check | What it checks | Result | Triage |
|---|---|---|---|
| Bandit | Common Python security issues | 0 low, 0 medium, 0 high findings across 1,776 LOC | No findings reported |
| pip-audit | Known vulnerabilities in installed dependency versions | No known vulnerabilities found | No reported vulnerable dependencies |
| Semgrep CE | Python security and quality rules | 151 rules run; 0 findings | No findings under the selected community rules |
| Gitleaks | Secrets committed in Git history | 21 commits scanned; no leaks found | No secrets detected in scanned history |
| uv lock --check | Lockfile consistency and dependency resolution | Passed; 82 packages resolved | Lockfile is valid |
| Ruff | Python lint checks | All checks passed | No lint findings |
| Ruff format | Python formatting | 31 files already formatted | No formatting changes required |
| git diff --check | Whitespace errors in changes | Passed | No whitespace errors |

## 3. HTTP security headers

Evidence: `docs/day17-header-scan.txt`

A test request to `GET /ui` returned HTTP 200.

The following headers were present:

- Content-Security-Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy

HSTS was not applicable to this scan because the application was running
in the development environment. The application adds
`Strict-Transport-Security: max-age=31536000` only in production.

## 4. Application hardening implemented

- Security headers are added to application responses.
- CORS uses an explicit origin allowlist. Wildcard origins and malformed
  origins are rejected by configuration validation.
- API rate limiting returns HTTP 429 and a Retry-After header.
- Request bodies are limited to 2 MiB.
- Document uploads accept only `.txt` and `.md` files, enforce a 1 MiB
  size limit, validate content type and UTF-8 text, and reject NUL bytes.
- Uploaded files receive random server-generated names and restrictive
  filesystem permissions.
- Upload access is restricted to HR administrators.
- Uploaded documents are stored outside the static file directory and
  excluded from Git.

## 5. Focused test evidence

The following Day17-focused test runs passed:

| Test group | Result |
|---|---:|
| Upload routes | 1 passed |
| Record authorization regression check | 1 passed |
| CORS, rate limiting, and request-size tests | 7 passed |
| Total across these focused runs | 9 passed |

The upload tests cover authorization, accepted file types, content-type
mismatches, empty files, invalid UTF-8, NUL bytes, size limits, generated
filenames, and file/directory permissions.

## 6. Findings, limitations, and follow-up

### Informational

- Test runs display a Starlette deprecation warning about using `httpx`
  with `starlette.testclient`. It did not cause test failures.
- Semgrep Community Edition ran the available Python rules. Additional
  Pro rules were unavailable because the environment was not authenticated.
- Gitleaks scanned the repository history available to the command at the
  time of the scan. This is not a guarantee that no secret exists elsewhere.
- pip-audit checks known published vulnerabilities; it cannot detect every
  possible dependency or application risk.

### Operational limitations

- The current rate limiter stores counters in process memory. It is suitable
  for this learning build but is not shared across multiple workers or
  application instances. A distributed deployment should use a shared
  rate-limit store such as Redis.
- Upload validation checks extension, declared content type, size, and text
  validity. It is not a malware scanner or a general-purpose file sanitizer.
- Uploaded documents are not automatically ingested into the RAG index.

## 7. Overall assessment

The recorded automated checks passed, and the focused Day17 tests passed.
No findings were reported by the selected scanners.

The implementation has meaningful security controls, but further review is
needed before production deployment. In particular, distributed rate
limiting, deployment configuration, broader security testing, and ongoing
dependency monitoring remain important.
