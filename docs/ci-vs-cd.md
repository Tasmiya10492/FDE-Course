# CI vs CD

## Continuous Integration (CI)
CI automatically checks proposed changes. This project uses CI for formatting, linting, type checking, automated tests, security checks, secret scanning and Docker image building.

## Continuous Delivery / Deployment (CD)
CD takes a successfully built artifact through deployment stages. A safer process builds the image once, promotes the same image between environments, requires approval where appropriate, and provides a rollback path.

## Current project boundary
The current workflow implements CI and builds an application image. It does not automatically deploy that image to production.
