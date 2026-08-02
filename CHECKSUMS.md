# Checksum manifest — OrgSmith v2.2.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `b2ac4402b540ac422d7adeb0ad912b527c42ee3e41ac2d20a9fe6a35853a5315` |
| brackenridge-civil | 127 | `298fb75d6a2fa186de4f3c37a347183927af1897344d7fe726f664d0f9a9941a` |
| calderwood-partners | 505 | `3b913917b1e604fbd9fecbe6fb3ad5c525f512036dd45d3d3b83d25023ca297c` |
| hollowell-ip | 181 | `40eb78d473274e2d57b1501de3afff3ceff6ba491f6b4bd010a631633673e6c0` |
| meridian-actuarial | 198 | `6f9a9033bd459b7d696819037ac3862b73ccafca408918af1b33a043aec994a4` |
| northgate-staffing | 200 | `08c159a223ad7c2757dd86f74767fa08f15716eca1350763b1ab419f2e595352` |
| saltmarsh-environmental | 126 | `81ecc039f9355b83ab3232791b10bfcb0bce6bfde5e718d55522fa8e056322d8` |
| verdant-health | 105 | `c5f7254416577453acbabe521662ac21a8fed4cc30ca1172323ea3b22a4dcb26` |
| **fleet** | 1697 | `fabe6128cb20c15e186ec280d5b4f3bd2aa62db7a098dfdeb56ddb6d1f432d73` |
