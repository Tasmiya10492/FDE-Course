Scanning local image tarball "/reports/fde-caddy-day18-v3.tar"
Starting filesystem walk for root:
End status: 108 dirs visited, 926 inodes visited, 89 Extract calls, 6.924139ms elapsed, 6.924669ms wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 918.707µs elapsed, 918.961µs wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 1.30934ms elapsed, 1.309728ms wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 393.814µs elapsed, 394.121µs wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 1.08898ms elapsed, 1.089271ms wall time
Starting filesystem walk for root:
End status: 0 dirs visited, 1 inodes visited, 1 Extract calls, 562.375µs elapsed, 562.612µs wall time

Container Scanning Result (Alpine Linux v3.24) (Based on "caddy" image):
Total 9 packages affected by 12 known vulnerabilities (0 Critical, 1 High, 5 Medium, 0 Low, 6 Unknown) from 1 ecosystem.
9 vulnerabilities can be fixed.

| OSV URL | CVSS | Ecosystem | Package | Version | Fixed Version | Source |
| --- | --- | --- | --- | --- | --- | --- |
| https://osv.dev/GHSA-4w3g-jfj2-cw2q | 6.9 | Go | github.com/go-jose/go-jose/v3 | 3.0.5 | -- | usr/bin/caddy |
| https://osv.dev/GHSA-mgcc-cww5-fp2q | 7.5 | Go | github.com/go-jose/go-jose/v3 | 3.0.5 | -- | usr/bin/caddy |
| https://osv.dev/GHSA-vvm8-gf78-28g4 | 6.9 | Go | github.com/go-jose/go-jose/v3 | 3.0.5 | -- | usr/bin/caddy |
| https://osv.dev/GO-2026-6865 |  | Go | github.com/klauspost/compress | 1.20.1 | 1.20.2 | usr/bin/caddy |
| https://osv.dev/GO-2026-6975 |  | Go | go.opentelemetry.io/otel | 1.46.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6974<br/>https://osv.dev/GHSA-q7gw-24fr-5p69 | 5.3 | Go | go.opentelemetry.io/otel/sdk | 1.46.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6974<br/>https://osv.dev/GHSA-q7gw-24fr-5p69 | 5.3 | Go | go.opentelemetry.io/otel/sdk/log | 0.22.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6974<br/>https://osv.dev/GHSA-q7gw-24fr-5p69 | 5.3 | Go | go.opentelemetry.io/otel/trace | 1.46.0 | 1.47.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-5932 |  | Go | golang.org/x/crypto | 0.57.0 | 0.58.1-0.20261009181718-2f1f834330b2 | usr/bin/caddy |
| https://osv.dev/GO-2026-6860 |  | Go | golang.org/x/net | 0.60.0 | 0.62.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6866 |  | Go | golang.org/x/net | 0.60.0 | 0.62.0 | usr/bin/caddy |
| https://osv.dev/GO-2026-6859 |  | Go | stdlib | 1.27.3 | 1.27.4 | usr/bin/caddy |
