# Day 16 – Security Demo Storyline

## Who is in the room?
The audience is a customer team reviewing the security of an employee
knowledge assistant. This may include HR stakeholders, application owners
and security reviewers.

## What do they care about?
They want to know that employees can access their own information without
being able to read another employee's private records. They also want
confidence that authentication, permissions and security events are handled
consistently.

## Demo flow
1. Register an employee account and explain that the password is stored as
   an Argon2id hash.
2. Log in and show the authenticated session.
3. Create a record and retrieve it as its owner.
4. Attempt to retrieve another employee's record and show the 404 response.
5. Explain that the denied attempt is recorded in the audit table.
6. Demonstrate that an HR administrator can access another employee's
   record because the role has that permission.
7. Log out and explain that the server-side session is invalidated.

## One thing they must remember
Authentication establishes who the user is. Authorisation determines what
that user is allowed to access. Record ownership must be checked on the
server for every relevant request.
