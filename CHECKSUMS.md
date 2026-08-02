# Checksum manifest — OrgSmith v2.1.1

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 254 | `bfa7f925380b58addeb24e74767ef13549c11c48d14ca9122649ec3def7207a4` |
| brackenridge-civil | 126 | `2aff6815e30ff9a65bdf0204e494bb5996b84cf92f06fcbf76802fd4fec2762c` |
| calderwood-partners | 504 | `16cc1197dfb1a115e094692777977a6280f1fc7c95409db649fc028285c050f0` |
| hollowell-ip | 180 | `5a76a8f8e75507a3305ca58d5d21a1e5897f16d0a08785b104da1d6867068abe` |
| meridian-actuarial | 197 | `7a3c3de2d0770734acaaa03c1fe3a1a17b466d6f6758ee96abc6266a3368ad09` |
| northgate-staffing | 167 | `432cabf67d30943fc5f3b5a330751b42463d8e80f77eaebf07c38f6df2f22315` |
| saltmarsh-environmental | 125 | `4c1a8a5af4ae6cffb14be74d24d95f4fadca9d8b2637422f78c5ce6fe0b74f09` |
| verdant-health | 104 | `619d2de29e9048436f70f8b5b5447b34f6a9ad36d646814e755c38b903f460d1` |
| **fleet** | 1657 | `0f503c13684b71e7c84f4dd44699ee6ee5da8719de248a7c52cb5587e7b02df8` |
