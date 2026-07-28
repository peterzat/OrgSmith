# Checksum manifest — OrgSmith v2.1.1

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
| calderwood-partners | 502 | `3a16b303f525e1190e98a203f84e92f7aeb6a25815b53586884079c44a41cc52` |
| hollowell-ip | 178 | `ab8ea1f00aade36acf37db9b50057dd1b47bbd6be94a8d0a997313afa6b9f10c` |
| meridian-actuarial | 195 | `605bb9ecef3715131513c62dab8ee8b519b3758e64fc22c1906c043f78d620ab` |
| northgate-staffing | 165 | `6507214e4f6056241a62f3c27730d80b5db6b4de13776d6802d7a44412dda06c` |
| saltmarsh-environmental | 123 | `88afad493a926ddb6e107521b5ee68219b23a9512764e8437e98b2c23223414d` |
| verdant-health | 102 | `ba2b401fa08bc93638c88c554e85323f6fad281008e63ced152e79a683138aee` |
| **fleet** | 1641 | `ac95b89f970e788fd10e1d39af1e25db0d05d3d8369f5ad979eab19777542722` |
