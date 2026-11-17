# Access Control Design – Day 8

## 1. Tenant Isolation

Each company is treated as a separate tenant.

Users can access documents belonging to their own tenant, provided they satisfy the document's role requirements.

Cross-tenant access is denied by default. Access to another tenant's document is allowed only when the document has been explicitly shared with the requesting tenant.

## 2. Role-Based Access Control

Each document contains an `allowed_roles` field.

A user must possess all roles specified in the document's allowed_roles field to access it.

Role matching uses an AND condition.

## 3. Missing Permissions

The system follows a default-deny policy.

- Missing allowed_roles: Deny.
- Empty allowed_roles: Deny.
- Missing user roles: Deny.
- Invalid permission metadata: Deny.

## 4. Cross-Tenant Sharing

Cross-tenant sharing must be explicitly authorized and recorded.

The requesting tenant must be included in the document's approved sharing permissions.

## 5. User Identity

Tenant ID and user roles must come from a trusted authentication context.

The application must not trust tenant IDs or roles supplied directly by the user in a search request.

## 6. Permission Enforcement

Tenant and role permissions must be applied inside the PostgreSQL similarity-search query before ranking and limiting the results.

Unauthorized document chunks must never be returned.

## 7. Security Testing

Tests must verify tenant isolation, explicit sharing, role matching, missing permissions and unauthorized retrieval.

The expected behaviour is that no unauthorized document chunk is returned.
