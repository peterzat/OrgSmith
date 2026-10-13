# Checksum manifest — OrgSmith v2.4.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `280d5a1979cad16fff3b02f9e49d05d97ba6e16a2a9f17e051a0e874fd111e79` |
| brackenridge-civil | 127 | `40b0a3d9b79aa56494bfa8cb12ea1904f819731dd9dbcccc1411f94a728a0114` |
| calderwood-partners | 505 | `6dc961da67953a9ac46c036227da0480183fac7e7678f3025c563a4c1000418b` |
| hollowell-ip | 181 | `2ea7130ea6fcd9f072281e4941991f4462e0f588efa27b4dda59cc4ccff6cf97` |
| meridian-actuarial | 200 | `5a140496e0c1f7576298f74dbf4c8cc43faed0e78baa94322f2afb530b0d9031` |
| northgate-staffing | 200 | `bb71abba6f3abaef787298f5e5af4b323c7ed0c211233eb3e465879dcbb99088` |
| quillon-harbor | 214 | `3ea746422e567dc736511bd650a1fa20876a7e0fd4f55b8040de317817d0b448` |
| saltmarsh-environmental | 126 | `3333041862c0a726003dc0c1ab3e9587c03527c31be1c8dc409a74694bcf414f` |
| verdant-health | 105 | `68a99e2e3a86dc3e764d25e2729686ca5b01c9fcddeec44e646cc96aaab1740f` |
| **fleet** | 1913 | `d1d7633b890f683055cdc136feff3ddb9d71b1974116c148ddb13ee98215b519` |
