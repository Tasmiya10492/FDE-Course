# Day 16 – Security Design Note

## Authentication
The application supports user registration and login. Passwords are validated
against a minimum length of 15 characters and a local blocklist. Passwords are
stored as Argon2id hashes, not as plain text.

The password policy does not require special character combinations or
scheduled password changes. Longer passwords are accepted.

## Sessions
After successful login, the application creates a server-side session.
The browser receives a signed session cookie with HttpOnly, SameSite and
Secure-in-production protections.

Logout deletes the server-side session and clears the cookie. A deleted
session cannot be reused.

## Login protection and auditing
Failed login attempts are tracked by email and IP address. Repeated failures
trigger temporary throttling.

Important authentication and record-access events are written to the audit
table so that security-relevant actions can be reviewed.

## Authorisation
Role permissions are defined centrally. Employees and line managers can
create and read their own records. HR administrators can also read records
belonging to other users.

Record ownership is checked on the server. A user who tries to access another
user's record without permission receives a not-found response.

## Testing
Automated tests cover password validation, password hashing, authentication,
role permissions and record ownership. The integration test verifies that
employee and line-manager cross-user access is denied, while HR administrator
cross-user access is permitted.

## Limitations
The password blocklist is a small local learning example, not a comprehensive
breached-password service. Production deployment would require a larger
blocklist and operational security review.
