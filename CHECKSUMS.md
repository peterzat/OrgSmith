# Checksum manifest — OrgSmith v2.4.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `dff72b248c77bdd54afa2c2b654476ccbd472912c2e664296aa32145586e9deb` |
| brackenridge-civil | 127 | `40b0a3d9b79aa56494bfa8cb12ea1904f819731dd9dbcccc1411f94a728a0114` |
| calderwood-partners | 505 | `6dc961da67953a9ac46c036227da0480183fac7e7678f3025c563a4c1000418b` |
| hollowell-ip | 181 | `41a9958a64d8c1fcbd821480e61a20ac7b5e2569f6a807eb66ccf58f6fbfec6f` |
| meridian-actuarial | 198 | `6d2aa3b00e7b238d3a6b5212e1e98c508afad7c73c11e7489bfcd17769843ae4` |
| northgate-staffing | 200 | `bb71abba6f3abaef787298f5e5af4b323c7ed0c211233eb3e465879dcbb99088` |
| quillon-harbor | 214 | `3ea746422e567dc736511bd650a1fa20876a7e0fd4f55b8040de317817d0b448` |
| saltmarsh-environmental | 126 | `3333041862c0a726003dc0c1ab3e9587c03527c31be1c8dc409a74694bcf414f` |
| verdant-health | 105 | `68a99e2e3a86dc3e764d25e2729686ca5b01c9fcddeec44e646cc96aaab1740f` |
| **fleet** | 1911 | `232bfa65c6b9b5f6d07099176c223cd8c41580979ac762d27840332f2aa124fa` |
