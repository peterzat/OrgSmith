# Checksum manifest — OrgSmith v2.1.1

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `9af864dad9f92b89a2dd903ecf9759fdb92dd9c4d8b8d0246119cba2f4a85bea` |
| brackenridge-civil | 127 | `6d097f001c1d6df9203378ea60779e21131825c82d06ed41a52255610ed13f4a` |
| calderwood-partners | 505 | `87701c7ca54aa2b347796fa6072a25e918b5a208bc14ca57a26cd5a6810dc053` |
| hollowell-ip | 181 | `d20207594a49790f39bfdf349d1a20d3d1afcde9f7470cd06c936e891ac7568d` |
| meridian-actuarial | 198 | `8b51f15336ac3d257313770426218c4fac254810d45be33dbe363f45e1e0d121` |
| northgate-staffing | 168 | `384875dbdd6688be736f283847660e2acdd6a65b57b73d31a43b41eb4fb10aeb` |
| saltmarsh-environmental | 126 | `c827f02b73df438c4d43bd0c6c5305124d3a804042bcaa0206ea6670ac4c3b2e` |
| verdant-health | 105 | `ea37fd9611ffa9710b134734d74a9ac62ab5ea5a64e462aa41c487ab1998d26c` |
| **fleet** | 1665 | `e1354be8bc3735969e73ce18c417b444140a06f19791256b4658de1c97fc28ac` |
