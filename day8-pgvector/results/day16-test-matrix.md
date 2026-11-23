# Day 16 – Role and Endpoint Test Matrix

| Role | Register/Login | Create record | List records | Read own record | Read another user's record |
|---|---|---|---|---|---|
| Employee | Allow | Allow | Own records only | Allow | Deny (404) |
| Line manager | Allow | Allow | Own records only | Allow | Deny (404) |
| HR administrator | Allow | Allow | All records | Allow | Allow |

## Additional checks

| Test | Expected result | Observed result |
|---|---|---|
| Unauthenticated record listing | 401 | Pass |
| Unauthenticated record creation | 401 | Pass |
| Employee reads manager's record | 404 | Pass |
| Manager reads employee's record | 404 | Pass |
| HR administrator reads employee's record | 200 | Pass |
| Denied cross-user access is audited | Audit event recorded | Pass |

Evidence: `tests/test_record_authorization.py`.
