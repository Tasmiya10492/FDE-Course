# Day 18 — Technical Demo Script

1. Show the Dockerfiles and explain the build and runtime stages.
2. Show pinned base-image digests.
3. Show Compose services and health dependencies.
4. Show that PostgreSQL has no published host port.
5. Show non-root users and container security restrictions.
6. Show Docker image history.
7. Show container logs.
8. Use docker exec to inspect the runtime user.
9. Use docker inspect to show capabilities, memory limits
   and no-new-privileges.
10. Show HR liveness and readiness endpoints.
11. Show an authenticated HR API request.
12. Show the agent health endpoint through Caddy.
13. Show HTTPS routing through the reverse proxy.
14. Show the OSV reports and explain unresolved findings.
15. Explain why the Caddy v3 candidate was not silently deployed.
16. Explain the rollback image tags and deployment procedure.

Do not print secrets or expose environment-file contents.
Do not stop the database or remove persistent volumes during
the demonstration.
