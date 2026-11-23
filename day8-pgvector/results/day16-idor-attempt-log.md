# Day 16 – IDOR Attempt Log

The record authorization integration test attempted cross-user access using
authenticated sessions.

| Attempt | Result | Security outcome |
|---|---|---|
| Employee attempted to read a line manager's record | HTTP 404 | Denied |
| Line manager attempted to read an employee's record | HTTP 404 | Denied |
| HR administrator attempted to read an employee's record | HTTP 200 | Allowed by role permission |

The test also checked the audit table and verified that denied cross-user
attempts generated `record_access_denied` events.

The application returns the same not-found response for an inaccessible
record and a nonexistent record, avoiding disclosure of another user's
record existence.

Evidence: `tests/test_record_authorization.py`.
