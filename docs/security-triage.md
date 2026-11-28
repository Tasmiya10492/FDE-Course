# Day 19 - Container Security Triage Memo

## Scan details

- Tool: OSV-Scanner
- Target: fde-service:day19
- Operating system: Debian GNU/Linux 13 (trixie)
- Base image: python:3.14.10-slim
- Base image pinned by digest
- Image rebuilt after updating the base image and applying apt upgrades.

## Scan summary

- Affected packages: 17
- Known vulnerabilities: 75
- Critical: 0
- High: 35
- Medium: 33
- Low: 5
- Unknown: 2
- Fixes available according to the scan: 0

The scanner also reported 28 unimportant/filtered findings separately.

## Findings and triage

The findings are primarily associated with Debian packages inherited
from the Python base image.

Examples of higher-scoring findings include:

- SQLite: DEBIAN-CVE-2026-119373 (8.5)
- util-linux: DEBIAN-CVE-2026-76642 (8.5)
- ACL: DEBIAN-CVE-2026-54369 (8.4)
- OpenSSL: DEBIAN-CVE-2026-95691 (8.1)
- ncurses: DEBIAN-CVE-2025-69720 (7.8)

These findings require applicability and exposure review. A package-level
finding does not by itself prove that the vulnerable functionality is
reachable through the application.

## Actions taken

1. Pinned the Python base image using its updated digest.
2. Added an apt package upgrade step to the runtime image build.
3. Rebuilt the image without using the build cache.
4. Exported the image and scanned it using OSV-Scanner.
5. Saved the detailed scan output for review.

## Remaining risks

The latest scan still reports 75 known vulnerabilities, including
35 High findings. The scanner reports no available fixes for the
affected installed package versions.

The findings have not been suppressed or ignored. They remain open
for vendor updates and further applicability review.

## Follow-up actions

- Re-scan after an updated official base image or Debian security fix
  becomes available.
- Review the affected package functionality and application exposure.
- Keep the runtime image minimal and run the application as a non-root user.
- Review new scan results before releasing updated images.

## Decision

The image build succeeds, but the image is not vulnerability-free.
The remaining findings are documented as unresolved security risks.
They should be reviewed before production deployment.
