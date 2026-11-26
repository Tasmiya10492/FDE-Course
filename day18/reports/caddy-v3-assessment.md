# Caddy v3 security assessment

## Candidate

- Image: fde-caddy:day18-v3
- Caddy version: 2.11.9
- Base: caddy:2.11.9-alpine pinned by digest
- Alpine package updates applied during build
- Runtime user: caddy (non-root)
- Caddy configuration validation: passed

## OSV scan

- Total findings: 12
- Critical: 0
- High: 1
- Medium: 5
- Low: 0
- Unknown: 6

## Comparison with the running v1 image

The running v1 image has 226 findings:
- Critical: 17
- High: 60
- Medium: 48
- Low: 9
- Unknown: 92

The v3 candidate has 12 findings and represents a substantial
reduction in reported findings. However, the candidate still has
one unresolved High finding.

Neither scan result proves that every vulnerable code path is
reachable or unreachable in this deployment.

## Unresolved High finding

- Advisory: GHSA-mgcc-cww5-fp2q
- CVE: CVE-2026-116587
- Component: github.com/go-jose/go-jose/v3
- Detected version: 3.0.5
- Risk: CPU exhaustion when parsing crafted RSA JWK input.
- Fixed version: no fixed v3 version listed in the advisory.

## Deployment and risk decision

The v3 candidate has not replaced the running v1 proxy.

Keep the current deployment temporarily while both versions undergo
a documented risk review. This is not a conclusion that v1 is safer:
its scan reports substantially more findings than v3.

Before selecting a production image, the release owner must assess:
- Whether the reported vulnerable components and code paths are
  reachable in this deployment.
- External exposure and applicable compensating controls.
- Available upstream fixes or defensible remediation options.
- Residual risk and explicit acceptance by the responsible owner.

Do not deploy v3 or mark either image as secure solely on the basis
of these scan counts. Rebuild and rescan after remediation.

A scanner finding is evidence of an affected component, not proof
that the vulnerable code path is reachable in this deployment.