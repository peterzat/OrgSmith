# Checksum manifest — OrgSmith v2.2.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `85b1e369f586bef603ed808b0f3792b83c305da07765fe57d97638ac1ad39c45` |
| brackenridge-civil | 127 | `6d097f001c1d6df9203378ea60779e21131825c82d06ed41a52255610ed13f4a` |
| calderwood-partners | 505 | `87701c7ca54aa2b347796fa6072a25e918b5a208bc14ca57a26cd5a6810dc053` |
| hollowell-ip | 181 | `d20207594a49790f39bfdf349d1a20d3d1afcde9f7470cd06c936e891ac7568d` |
| meridian-actuarial | 198 | `8b51f15336ac3d257313770426218c4fac254810d45be33dbe363f45e1e0d121` |
| northgate-staffing | 200 | `bd2a7c515c9bf8c27bd139f54bd7f88434f10dffc827a89c667666ed9bf38f38` |
| saltmarsh-environmental | 126 | `c827f02b73df438c4d43bd0c6c5305124d3a804042bcaa0206ea6670ac4c3b2e` |
| verdant-health | 105 | `ea37fd9611ffa9710b134734d74a9ac62ab5ea5a64e462aa41c487ab1998d26c` |
| **fleet** | 1697 | `77be2b58dc2441222e5834ce205de7a6cc4029f9a2ff5f950a0ed1a3b038ee63` |
