# Checksum manifest — OrgSmith v2.3.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `ee5a1c7e4a7360eae8b6484a370656c1d9b406a868def31e4943bda3e896898a` |
| brackenridge-civil | 127 | `02c013694f56269a7fdf711492d2e2ce717fa7a25b3b7ea4e1c53b172e93c618` |
| calderwood-partners | 505 | `ac1a79ac8016950b7334f8206e755616321a4424373624baeb3d735f1c1877c6` |
| hollowell-ip | 181 | `5812cce8dfd7c15aef41c655d0056ecee212e97ee0cd8ac4df0823609af6303f` |
| meridian-actuarial | 198 | `ec072bdf3d0da33210f03e0e71624f6a8997aef763ef97f1427682f4bb6531d4` |
| northgate-staffing | 200 | `71ca466e67cb41cb4e52d9f2e1b02aa00bf7b04e5f128c2f87dbb3fbbe073c03` |
| saltmarsh-environmental | 126 | `34b434763608c737599ffb529d826138193f59bf1d721ca3a9515d68398dca06` |
| verdant-health | 105 | `5a71b75c4f7c706fa3601d7f09aece56f1bb32ea68597c287a28b4a0e7fe8bc6` |
| **fleet** | 1697 | `774f97a6f8ea1407a4315576226778b40e00ee9f875cbe9c4ee44638f52187e2` |
