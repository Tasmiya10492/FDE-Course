# Day 18 — Container Security Review

Date: 26 November 2026

## Scan summary

| Image | Candidate/version | Critical | High | Medium | Low | Unknown | Total |
|---|---|---:|---:|---:|---:|---:|---:|
| HR API | day18-v1 | 0 | 35 | 33 | 5 | 6 | 79 |
| LangGraph agent | day18-v1 | 0 | 35 | 33 | 5 | 6 | 79 |
| Caddy original | day18-v1 | 17 | 60 | 48 | 9 | 92 | 226 |
| Caddy candidate | day18-v3 | 0 | 1 | 5 | 0 | 6 | 12 |

The HR and agent scans each report four vulnerabilities as fixable.
The Caddy v3 scan reports nine vulnerabilities as fixable.

## Caddy candidate improvements

Caddy v3 uses Caddy 2.11.9 with a digest-pinned Alpine base.
Alpine packages were upgraded during the image build.

Verified package versions:
- OpenSSL: libcrypto3/libssl3 3.5.9-r1
- zlib: 1.4-r0
- zstd-libs: 1.6.0-r1

The candidate runs as the non-root caddy user and its Caddyfile
validation passed.

The v3 candidate reports 12 findings compared with 226 in the
running v1 image. However, one High finding remains:
- GHSA-mgcc-cww5-fp2q
- Component: github.com/go-jose/go-jose/v3
- Detected version: 3.0.5

## Deployment and risk decision

The running HR, agent and proxy containers remain on their
day18-v1 images and were healthy during the checks.

The v3 Caddy candidate has not replaced the running proxy.

The current v1 proxy is being retained temporarily, not because
it is considered safer. Its scan reports substantially more
findings than the v3 candidate.

Before production release, the responsible owner must assess
vulnerable-code reachability, external exposure, compensating
controls, available remediation and residual risk. Record risk
owners, mitigations, acceptance and target remediation dates.

Do not represent unresolved findings as fixed or treat scan counts
alone as proof that an image is safe.

## Agent state limitation

The LangGraph graph currently uses InMemorySaver for checkpointing.
The API also tracks active thread IDs in an in-memory set.

Pending approval state and active-thread tracking are therefore
not durable across process restarts. Multi-worker deployments
also require shared, durable checkpointing and coordinated thread
tracking. This must be addressed before relying on approvals in
production.

## Reports

- reports/osv-hr-image-scan.md
- reports/osv-agent-image-scan.md
- reports/osv-caddy-image-scan-v3.md
- reports/caddy-v3-assessment.md

## Limitations

These are point-in-time image scans. Rebuilds, package updates,
base-image changes or new OSV advisories require another scan.
The apk upgrade step also means Alpine package resolution is
time-dependent even though the base image is pinned by digest.