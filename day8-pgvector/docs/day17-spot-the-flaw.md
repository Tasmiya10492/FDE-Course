# Day17 Spot-the-Flaw Code Review

## Review method

Each snippet was reviewed for security weaknesses, possible exploitation, impact, and recommended remediation. The review considers confidentiality, integrity, authorization, input validation, and safe error handling.

---

## Snippet 1 — Ticket search

### Review comment

**Reject.** The SQL query is constructed using an f-string that directly inserts the user-controlled search term into the SQL statement. This creates a SQL injection vulnerability.

Use a parameterized query and validate the search input. The database driver must handle the parameter separately from the SQL command.

### Risk

An attacker could submit a specially crafted search term that changes the meaning of the SQL query. Depending on the database permissions and query structure, this could expose unauthorized ticket information, bypass intended filters, or modify data.

This is an injection vulnerability because untrusted input is treated as executable SQL rather than data.

### Recommended fix

Use parameterized SQL:

```python
@router.get("/tickets/search")
def search(q: str, db=Depends(get_db)):
    if not q or len(q) > 200:
        raise HTTPException(status_code=400, detail="Invalid search query")

    sql = "SELECT id, title FROM tickets WHERE title LIKE %s"
    return db.execute(sql, (f"%{q}%",)).fetchall()

### Risk

An attacker could submit a specially crafted search term that changes the meaning of the SQL query. Depending on database permissions, this could expose unauthorized ticket information or modify data.

### Recommended fix

Use parameterized SQL:

```python
@router.get("/tickets/search")
def search(q: str, db=Depends(get_db)):
    if not q or len(q) > 200:
        raise HTTPException(status_code=400, detail="Invalid search query")

    sql = "SELECT id, title FROM tickets WHERE title LIKE %s"
    return db.execute(sql, (f"%{q}%",)).fetchall()
```

Also enforce the caller's ticket-access permissions.

**Decision: Reject the original code. Approve only after parameterization, input validation, and authorization checks.**

---

## Snippet 2 — Invoice access

### Review comment

**Reject.** The endpoint authenticates the user but does not check whether that user owns the requested invoice or has permission to access it. This is Broken Object Level Authorization (BOLA), also known as IDOR.

### Risk

An authenticated user could change the `invoice_id` in the URL and retrieve another customer's invoice. This could expose confidential financial and customer information.

### Recommended fix

Check ownership as part of the database query, or perform an explicit authorization check before returning the invoice.

```python
@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, user=Depends(current_user), db=Depends(get_db)):
    row = db.execute(
        "SELECT * FROM invoices WHERE id = %s AND user_id = %s",
        (invoice_id, user.id),
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return row
```

The `user_id` field is an illustrative assumption; use the actual ownership field in the application schema. Administrative access must be handled through explicit permissions.

**Decision: Reject the original code. Approve only after object-level authorization is enforced.**

---

## Snippet 3 — Passwords and tokens

### Review comment

**Reject.** There are three security concerns:

1. The JWT signing secret is hard-coded in the source code.
2. MD5 is used for password hashing, which is not suitable for securely storing passwords.
3. The JWT has no expiry claim.

### Risk

If the signing secret is exposed, an attacker could potentially forge JWTs and impersonate users.

MD5 is very fast, making stolen password hashes easier to crack through large-scale guessing.

Tokens without expiry may remain valid indefinitely unless another mechanism invalidates them.

### Recommended fix

- Store secrets in environment variables or a secrets manager.
- Use Argon2id for password hashing.
- Include token expiry and validate JWT claims.
- Rotate exposed signing keys and invalidate affected tokens.

Example password hashing:

```python
from argon2 import PasswordHasher

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return password_hasher.verify(stored_hash, password)
    except Exception:
        return False
```

Load the JWT signing key from secure configuration rather than hard-coding it.

**Decision: Reject the original code. Approve only after secure password hashing, secret management, and token-expiration controls are implemented.**

---

## Snippet 4 — Sessions and preferences

### Review comment

**Reject.** There are two concerns:

1. The package `fastapi_jwt_guardrail_kit` must be independently verified before installation. An AI-suggested package name is not proof that the package is legitimate.
2. `pickle.loads()` is unsafe for untrusted input because malicious pickle data can execute arbitrary code during deserialization.

### Risk

An unverified or malicious package could introduce malicious code into the application or its environment.

An attacker who controls the `blob` value could supply a crafted pickle payload that executes code with the application's permissions.

### Recommended fix

- Verify package existence, maintainers, source repository, release history, and purpose before installation.
- Pin reviewed dependency versions.
- Avoid pickle for untrusted data.
- Use JSON with schema validation for preferences.

Example:

```python
import json


def load_prefs(blob: bytes) -> dict:
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid preferences data") from exc

    if not isinstance(value, dict):
        raise ValueError("Preferences must be a JSON object")

    return value
```

Validate allowed preference keys and value types before using the data.

**Decision: Reject the original code. Approve only after package verification and replacement of unsafe pickle deserialization.**

---

## Snippet 5 — Error handler

### Review comment

**Reject.** The handler logs a user's password, exposes exception details and a traceback to the client, and returns HTTP 200 for an internal server error.

Passwords and tokens must never be logged.

### Risk

Sensitive credentials could be exposed to anyone with access to application logs.

Tracebacks and exception messages may disclose internal paths, database details, and implementation information.

Returning HTTP 200 incorrectly tells clients and monitoring systems that the request succeeded.

### Recommended fix

- Never log passwords or authentication tokens.
- Log safe error details with a request ID.
- Return a generic error response.
- Use HTTP 500 for unexpected server errors.
- Keep detailed diagnostic information in protected server-side logs.

Example:

```python
@app.exception_handler(Exception)
async def handle(request, exc):
    request_id = getattr(request.state, "request_id", "unknown")

    logger.exception(
        "Unhandled application error",
        extra={"request_id": request_id},
    )

    return JSONResponse(
        {
            "error": "Internal server error",
            "request_id": request_id,
        },
        status_code=500,
    )
```

**Decision: Reject the original code. Approve only after sensitive-data logging and information disclosure are removed and the correct HTTP status is returned.**

---

## Snippet 6 — Preview and download

### Review comment

**Reject.** There are two vulnerabilities:

1. The preview endpoint fetches an arbitrary user-provided URL, creating a Server-Side Request Forgery (SSRF) risk.
2. The download endpoint inserts an untrusted filename into a filesystem path, creating a path traversal risk.

### Risk

An attacker could use SSRF to make the application access internal services, localhost, or cloud metadata endpoints.

An attacker could use directory traversal sequences such as `../` to attempt to access files outside the intended upload directory.

This could expose internal services, credentials, configuration files, or sensitive files.

### Recommended fix

For URL preview:

- Prefer approved resource identifiers over arbitrary URLs.
- Use a strict destination allowlist where external URLs are required.
- Block localhost, private, link-local, and reserved IP addresses.
- Validate DNS results and redirects.
- Apply network egress restrictions and request timeouts.

For downloads:

- Use server-generated filenames or opaque file IDs.
- Resolve paths within the approved upload directory.
- Check authorization before returning files.

Example path validation:

```python
from pathlib import Path

UPLOAD_DIR = Path("/data/uploads").resolve()


@router.get("/download")
def download(name: str):
    if Path(name).name != name:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = (UPLOAD_DIR / name).resolve()

    if file_path.parent != UPLOAD_DIR or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)
```

This example also needs an appropriate file-access authorization check. SSRF requires separate destination validation; path validation alone does not fix it.

**Decision: Reject the original code. Approve only after SSRF protections, safe path handling, and file-access authorization are implemented.**

---

## Overall review conclusion

All six original snippets should be rejected in their current form.

The review identified:

1. SQL injection.
2. Broken Object Level Authorization (BOLA/IDOR).
3. Insecure password hashing, hard-coded JWT secret, and missing token expiry.
4. Unverified package dependency and unsafe pickle deserialization.
5. Sensitive credential logging, exception information disclosure, and incorrect HTTP status handling.
6. Server-Side Request Forgery (SSRF) and path traversal.

AI-generated code must not be accepted just because it looks correct or runs successfully. Security-sensitive code requires independent review, testing, dependency verification, and authorization checks.

**Final decision: Reject all six original snippets. Request remediation and security tests before approval.**
