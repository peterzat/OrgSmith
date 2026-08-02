# Checksum manifest — OrgSmith v2.2.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `6b53a99461bae941b5aaf7cdff655e17df2301213a28fab7e4a8f07420f7c4be` |
| brackenridge-civil | 127 | `fe8a29a0972fa38fd852ced3b291f835bf003a01de5200b10a3f2d1384c3c233` |
| calderwood-partners | 505 | `bac652e0358c857a7ef3d3bb288053cacfc6ed17ba3f62ee1db1aa599324a2da` |
| hollowell-ip | 181 | `44278261c2bb57617cac3fa9b1714e0b61327cc49f80646b3d954df1e0fc4ff7` |
| meridian-actuarial | 198 | `d9f5918ca897aff20d7e4645e64287144d723edb566dfb7277dadbeaa30420b7` |
| northgate-staffing | 200 | `14e7705861586fbbc33716625c3f3968335da2aa484a02a2d79c33150e13f18a` |
| saltmarsh-environmental | 126 | `a2fc79a8f5fa0ce4f9d0b668035ef0cd63eb6b317337d0fa11c05002fe05ab32` |
| verdant-health | 105 | `48ff3deb97551ad234d1e86ff44b0faae4cacf4b0568188ce12208a15ce262e8` |
| **fleet** | 1697 | `44e1031dd0efb8c334b1f3b1af9b735bb91ccf2bf7030ed7e880b31487158129` |
