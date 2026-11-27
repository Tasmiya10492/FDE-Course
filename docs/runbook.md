# Operations Runbook

## Application unavailable
1. Check container status.
2. Inspect application logs.
3. Verify database health and connectivity.
4. Verify required environment variables.
5. Identify the cause before restarting.

## Database unavailable
1. Check PostgreSQL container status.
2. Check database readiness.
3. Verify connection settings.
4. Inspect database logs.
5. Restore from a verified backup if required.

## Failed deployment
1. Stop further rollout.
2. Inspect failing health checks and logs.
3. Keep the last known-good image available.
4. Roll back using the deployment process.
5. Record the cause and corrective action.

## Security incident
Preserve relevant logs, restrict affected access, notify the responsible administrator, and follow the organization's incident-response process.
