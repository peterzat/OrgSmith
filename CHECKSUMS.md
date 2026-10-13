# Checksum manifest — OrgSmith v2.4.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `cc3bbe293663a725796d542f0a745cd47c118acfde8eb9aabb4eabb5472804af` |
| brackenridge-civil | 127 | `3d5fd7962d1df70ed2eec186c51fa7cd173c0292f457a7b41b8fb1af18d79eab` |
| calderwood-partners | 505 | `b34c0a44e834a0a912bd2540bcd35ae5c624140d8b37c04fc6a09f4d01a46a2f` |
| hollowell-ip | 181 | `22d71fe80a93560f8d21cf16359234d83a189c03efbccc6845775d296ea4a1dc` |
| meridian-actuarial | 198 | `0df92d237631902a178dd5a28abc414af95394f20701361a8260d76190b818a7` |
| northgate-staffing | 200 | `3a04723c4c148338e43efca41f179609ebbae56775bc83b64d4df2bf55a5eb5b` |
| quillon-harbor | 214 | `1ac0d7a51a91bfb272505d3063269b52a49af12dcca82fbd7a62ba67c54b855f` |
| saltmarsh-environmental | 126 | `80ffe02d6c25fa43d3e91384d9732311825343842b31b26f1597f317d7834145` |
| verdant-health | 105 | `94e71807b97df87fc7cca578e820c1a2dbf3e91aee74cce02e74f3c15d478058` |
| **fleet** | 1911 | `4ac8969aa405e56694982abbb876bb7b8c9dace6051973ea3414df8e98438e2e` |
