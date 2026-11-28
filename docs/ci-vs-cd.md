# CI vs CD

## Continuous Integration (CI)

CI automatically checks proposed code changes. This project uses GitHub Actions to run formatting, linting, type checking, automated tests, security checks, secret scanning and Docker image building.

The pull request checks must pass before changes are considered ready to merge.

## Continuous Delivery and Continuous Deployment (CD)

CD takes a successfully built artifact through deployment stages.

- Continuous Delivery keeps the tested artifact ready for release, usually with a manual approval before production.
- Continuous Deployment automatically releases qualifying changes to production after required checks pass.

## Build once, deploy the same image

A safer release process builds the Docker image once, identifies it by an immutable digest, and promotes that exact image through test, staging and production environments.

Do not rebuild separately for each environment. This helps ensure that the artifact tested is the artifact released.

## Approval and rollback

- Require an authorized approval before production deployment where appropriate.
- Store deployment configuration and secrets securely.
- Monitor application health after deployment.
- Keep the previous known-good image digest available.
- If the new release fails health checks, roll back to the previous known-good image and investigate.

## Current project boundary

The current workflow implements CI and builds an application image. It does not automatically deploy that image to staging or production. Image promotion, deployment approvals, health verification and rollback are future CD work.
