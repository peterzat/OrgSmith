# Checksum manifest — OrgSmith v2.3.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `041163e1b3910fc1a096e7fd0e0f157b1593deb61db31e0770c3b6db5fa8dbda` |
| brackenridge-civil | 127 | `3d5fd7962d1df70ed2eec186c51fa7cd173c0292f457a7b41b8fb1af18d79eab` |
| calderwood-partners | 505 | `b34c0a44e834a0a912bd2540bcd35ae5c624140d8b37c04fc6a09f4d01a46a2f` |
| hollowell-ip | 181 | `b8292c3e357494a9f75fb5f8378c468ff7e614504faea709d2455d5fe44c0d38` |
| meridian-actuarial | 198 | `1aa4b0c082e1cd770d3d5804fb87e27775a5e13876436573c99447335ddf8da1` |
| northgate-staffing | 200 | `8fda280a0c1763dfa2f5a7d64a6d5d7b829fce731fdaf20077ef7e4347f5374d` |
| quillon-harbor | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| saltmarsh-environmental | 126 | `80ffe02d6c25fa43d3e91384d9732311825343842b31b26f1597f317d7834145` |
| verdant-health | 105 | `94e71807b97df87fc7cca578e820c1a2dbf3e91aee74cce02e74f3c15d478058` |
| **fleet** | 1697 | `402b4564850593f1554ac8e24e0b77ffda5a9b0fa73d2b4ae0dfe2fd67efd506` |
