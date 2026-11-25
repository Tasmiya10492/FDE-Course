# Day 17 — Leaked Secret Response

## Five steps for the team

### 1. Contain the exposure and investigate
Identify the affected credential, repository, branches, commits and exposure period.
Restrict access where necessary. Do not copy the secret into tickets, chat messages
or incident reports.

### 2. Revoke or rotate the credential immediately
Revoke the exposed credential with its provider and generate a replacement.
Update applications and deployment environments that depend on it. Verify that
the old credential no longer works. History cleanup does not replace rotation.

### 3. Assess the exposure
Check repository history, clones, forks, CI logs, build artifacts, deployment
logs and other locations where the credential may have been copied. Determine
whether other credentials or systems could also be affected.

### 4. Clean repository history when necessary
If the secret remains in Git history, coordinate a history rewrite using
git-filter-repo. Use --replace-text to redact a value while preserving the file,
or --invert-paths when the entire file must be removed from history.
Coordinate any required force push with repository administrators and the team.
Never rewrite a shared repository without an agreed recovery plan.

### 5. Verify and communicate
Run Gitleaks and inspect the relevant Git history again. Confirm that the old
credential is revoked and that the replacement works. Tell every collaborator
to re-clone the cleaned repository and avoid pushing old branches or clones.
Monitor for further exposure or suspicious use.

## Day 17 practice evidence

- Used the supplied course generator to create a disposable repository.
- Confirmed the fake key was committed on the oops branch.
- Ran Gitleaks; it reported no leaks for this deliberately fake value.
- Simulated rotation by committing a replacement fake value.
- Used git-filter-repo with --replace-text to redact the original value.
- Verified the original value was absent from reachable Git history.
- Ran Gitleaks again; it reported no leaks.
- Confirmed the working tree was clean.

## Learning

A clean scanner result does not prove that no secret exists. Detection depends
on scanner rules and the format of the value. Manual investigation and credential
rotation remain essential.
