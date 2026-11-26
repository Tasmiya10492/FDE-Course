# Day 18 — Learning Reflection

## What I built

- Multi-stage Docker images for the HR API and LangGraph agent.
- A Caddy reverse proxy with internal HTTPS.
- A Compose stack with database health dependencies and service
  health checks.
- Non-root runtime users and container capability restrictions.
- Resource limits, log limits and persistent volumes.
- Liveness and readiness endpoints.

## What I verified

- Docker image build, history, run, logs, exec and inspect.
- Database connectivity and application readiness.
- API authentication and agent routing through Caddy.
- Caddy configuration validation.
- Container image vulnerability scans.
- The running containers remained healthy during candidate builds.

## Security lessons

A successful build does not mean an image is secure.
A scanner finding does not automatically prove exploitability.
A finding must be investigated and documented, not hidden.
Pinning a base image digest improves reproducibility, but
uncontrolled package upgrades can make later builds differ.

## What I would improve

- Establish a repeatable image rebuild and scan process.
- Assign owners and remediation dates to vulnerabilities.
- Record explicit risk acceptance for unresolved findings.
- Re-scan after dependency and base-image updates.
- Test rollback and graceful shutdown during a controlled window.

## Reflection

The most important lesson is that production readiness includes
security, operational verification, communication and documented
risk decisions—not just a running container.
