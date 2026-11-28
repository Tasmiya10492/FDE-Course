# Day 19 - Security Scan Workbook

## Purpose
Record the security tools used, commands executed, results and limitations.

## Application and dependency scans

| Tool | Command | Result |
|---|---|---|
| Ruff | `uv run ruff check src tests` | Passed |
| Ruff format | `uv run ruff format --check src tests` | Passed |
| Pyright | `uv run pyright src tests` | 0 errors |
| Pytest | `uv run pytest -q tests` | 99 passed |
| Bandit | `uv run bandit -r src` | 0 Low, Medium or High findings |
| pip-audit | `uv run pip-audit` | No known vulnerabilities |
| Semgrep CE | `uvx semgrep scan --config auto src` | 0 findings |

## Secret scanning

- Tool: Gitleaks.
- Scanned repository history through the CI workflow.
- Result: CI secret-scan job passed.
- Commit hooks also ran Gitleaks successfully.

## Container image scanning

- Tool: OSV-Scanner.
- Target: `fde-service:day19`.
- Image was rebuilt without cache, exported and scanned.
- Detailed reports are stored in `docs/security-evidence/`.

Latest scan summary:

- Affected packages: 17.
- Total known vulnerabilities: 75.
- Critical: 0.
- High: 35.
- Medium: 33.
- Low: 5.
- Unknown: 2.
- Fixes identified by the scanner: 0.

The image findings remain unresolved. Package-level findings require applicability and exposure review; they do not automatically prove that vulnerable functionality is reachable through the application.

## Alternative tooling and limitations

The requested `/app-scan` workflow was not available in this environment. Alternative checks were performed using Bandit, Semgrep CE, pip-audit, Gitleaks and OSV-Scanner.

The OSV source scan using an exported requirements file could not complete dependency resolution because of a conflicting package constraint. This is not a clean OSV source-scan result. pip-audit independently reported no known Python dependency vulnerabilities.

Semgrep CE completed with zero findings. Semgrep Code and Supply Chain features were not enabled.

## Follow-up actions

1. Review the unresolved OSV image findings for actual applicability.
2. Re-scan when updated Debian packages or base images become available.
3. Keep security checks in CI.
4. Review new findings before production deployment.

## Overall assessment

Application checks passed. The container image still has unresolved reported vulnerabilities, including 35 High findings. Do not treat the image as vulnerability-free or production-ready until these risks have been reviewed and addressed.
