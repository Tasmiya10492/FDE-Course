# Day 18 — AI Use Log

AI assistance was used as a tutor and reviewer for:

- Explaining Docker, Compose, Caddy and container security concepts.
- Reviewing Dockerfiles and Compose configuration.
- Explaining health checks, readiness, liveness and shutdown.
- Interpreting OSV image scan findings.
- Suggesting verification commands and test sequences.
- Structuring the security assessment and consulting rehearsal.

Human verification performed:
- Commands were run in the local WSL2 environment.
- Docker build and runtime results were inspected.
- Image users and image versions were verified.
- Caddy configuration validation was executed.
- OSV reports were inspected rather than treating a scan exit
  code as proof of build failure.
- Deployment decisions were kept separate from candidate builds.

AI-generated recommendations were not treated as proof that
a vulnerability was fixed or that production deployment was safe.
