# Checksum manifest — OrgSmith v2.1.1

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `aad96de5e97fde1462f6e55b0dbcffb37af9953b913f4efd3c25ecf3ee5bd837` |
| brackenridge-civil | 127 | `6d097f001c1d6df9203378ea60779e21131825c82d06ed41a52255610ed13f4a` |
| calderwood-partners | 505 | `87701c7ca54aa2b347796fa6072a25e918b5a208bc14ca57a26cd5a6810dc053` |
| hollowell-ip | 181 | `668876205990d525cbc5cdff13f935226d6ad4ef15e4c4d157d3fe08749d3f65` |
| meridian-actuarial | 198 | `9924c9d573b2e6970f02f8710775a4fc290b2b756d9353ed37c9dc08664b0e90` |
| northgate-staffing | 168 | `384875dbdd6688be736f283847660e2acdd6a65b57b73d31a43b41eb4fb10aeb` |
| saltmarsh-environmental | 126 | `c827f02b73df438c4d43bd0c6c5305124d3a804042bcaa0206ea6670ac4c3b2e` |
| verdant-health | 105 | `ea37fd9611ffa9710b134734d74a9ac62ab5ea5a64e462aa41c487ab1998d26c` |
| **fleet** | 1665 | `06c1ba53171ca8de8a730432e939d133575562985f0229d6fbc6f24cf5240837` |
