# Checksum manifest — OrgSmith v2.1.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 252 | `6a39b5ff6507fbc363c4954800bcd24bb99e185fcee1f0705c88a6321e4ebffa` |
| brackenridge-civil | 124 | `9a25894226a5c81f8578bb2108f1aa8399cda4de633911ce5277e2cab02a883c` |
| calderwood-partners | 502 | `ee2a7ac209f46c07f72d3bcb6bbc493c9956227f4f46a240e8e0fd613fc2e583` |
| hollowell-ip | 178 | `ab8ea1f00aade36acf37db9b50057dd1b47bbd6be94a8d0a997313afa6b9f10c` |
| meridian-actuarial | 195 | `605bb9ecef3715131513c62dab8ee8b519b3758e64fc22c1906c043f78d620ab` |
| northgate-staffing | 165 | `ba0ee7d04c1cda958cd40596e4ad9306e3a38152149646d653ea6ab3c5ee5fbd` |
| saltmarsh-environmental | 123 | `88afad493a926ddb6e107521b5ee68219b23a9512764e8437e98b2c23223414d` |
| verdant-health | 102 | `ba2b401fa08bc93638c88c554e85323f6fad281008e63ced152e79a683138aee` |
| **fleet** | 1641 | `30a28f3f54a162e53d7937e5268807fb1a0affa412c4a25ff71487b3e3e12955` |
