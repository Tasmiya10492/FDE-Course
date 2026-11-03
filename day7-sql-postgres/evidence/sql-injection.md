# SQL Injection Demonstration

## Vulnerable approach
Used Python f-strings to construct an SQL query directly
from user input.

## Attack input
' OR '1'='1' --

## Result
The vulnerable query returned all three demo users because
the injected condition was always true.

## Secure approach
Used psycopg parameterised queries with %s placeholders.

## Result
The same malicious input was treated as a username value
and did not return other users.

## Upsert
Used INSERT ... ON CONFLICT DO UPDATE.

## Result
Repeated execution did not create duplicate usernames.

## Learning
Never concatenate untrusted user input into SQL.
Use parameterised queries and appropriate unique constraints.