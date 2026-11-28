Scanning local image tarball "/reports/fde-caddy-day18-v2.tar"
Starting filesystem walk for root:
End status: 108 dirs visited, 926 inodes visited, 89 Extract calls, 15.949159ms elapsed, 15.949336ms wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 1.164278ms elapsed, 1.164577ms wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 166.531µs elapsed, 166.636µs wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 215.57µs elapsed, 215.691µs wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 127.642µs elapsed, 127.754µs wall time

Container Scanning Result (Alpine Linux v3.24) (Based on "caddy" image):
Total 12 packages affected by 19 known vulnerabilities (1 Critical, 6 High, 6 Medium, 0 Low, 6 Unknown) from 2 ecosystems.
16 vulnerabilities can be fixed.

| OSV URL | CVSS | Ecosystem | Package | Version | Fixed Version | Source |
| --- | --- | --- | --- | --- | --- | --- |
| https://osv.dev/GHSA-4w3g-jfj2-cw2q | 6.9 | Go | github.com/go-jose/go-jose/v3 | 3.0.5 | -- | usr/bin/caddy |
| https://osv.dev/GHSA-mgcc-cww5-fp2q | 7.5 | Go | github.com/go-jose/go-jose/v3 | 3.0.5 | -- | usr/bin/caddy |
| https://osv.dev/GHSA-vvm8-gf78-28g4 | 6.9 | Go | github.com/go-jose/go-jose/v3 | 3.0.5 | -- | usr/bin/caddy |
| https://osv.dev/GHSA-mgcc-cww5-fp2q | 7.5 | Go | github.com/go-jose/go-jose/v4 | 4.1.5 | 4.1.6 | usr/bin/caddy |
| https://osv.dev/GO-2026-6865 |  | Go | github.com/klauspost/compress | 1.20.1 | 1.20.2 | usr/bin/caddy |
| https://osv.dev/GO-2026-6975 |  | Go | go.opentelemetry.io/otel | 1.46.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6974<br/>https://osv.dev/GHSA-q7gw-24fr-5p69 | 5.3 | Go | go.opentelemetry.io/otel/sdk | 1.46.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6974<br/>https://osv.dev/GHSA-q7gw-24fr-5p69 | 5.3 | Go | go.opentelemetry.io/otel/sdk/log | 0.22.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6974<br/>https://osv.dev/GHSA-q7gw-24fr-5p69 | 5.3 | Go | go.opentelemetry.io/otel/trace | 1.46.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-5932 |  | Go | golang.org/x/crypto | 0.57.0 | 0.58.1-0.20261009181718-2f1f834330b2 | usr/bin/caddy |
| https://osv.dev/GO-2026-6860 |  | Go | golang.org/x/net | 0.60.0 | 0.62.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6866 |  | Go | golang.org/x/net | 0.60.0 | 0.62.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6859 |  | Go | stdlib | 1.27.3 | 1.27.4 | usr/bin/caddy |
| https://osv.dev/ALPINE-CVE-2026-107496 | 7.5 | Alpine:v3.24 | openssl | 3.5.9-r0 | 3.5.9-r1 | lib/apk/db/installed |
| https://osv.dev/ALPINE-CVE-2026-88822 | 6.5 | Alpine:v3.24 | openssl | 3.5.9-r0 | 3.5.9-r1 | lib/apk/db/installed |
| https://osv.dev/ALPINE-CVE-2026-88823 | 7.5 | Alpine:v3.24 | openssl | 3.5.9-r0 | 3.5.9-r1 | lib/apk/db/installed |
| https://osv.dev/ALPINE-CVE-2026-95691 | 8.1 | Alpine:v3.24 | openssl | 3.5.9-r0 | 3.5.9-r1 | lib/apk/db/installed |
| https://osv.dev/ALPINE-CVE-2026-95692 | 7.5 | Alpine:v3.24 | openssl | 3.5.9-r0 | 3.5.9-r1 | lib/apk/db/installed |
| https://osv.dev/ALPINE-CVE-2026-4738 | 9.4 | Alpine:v3.24 | zlib | 1.3.2-r1 | 1.4-r0 | lib/apk/db/installed |
