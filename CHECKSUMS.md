# Checksum manifest — OrgSmith v2.1.1

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 253 | `f1091fb83a64734473daf7eb12a2e48a7e7d2ce2195d6e26dc76c6b5704c34a6` |
| brackenridge-civil | 125 | `8e448cff27ece18ec611b5a13cb6cd1d1c434bd3b4fa9288e015779d73694b66` |
| calderwood-partners | 503 | `f46e4cc848042b16b6a42dde6b946cee8e631e0d3b7c6a94e5218cca96dff5cd` |
| hollowell-ip | 179 | `faeb0353073c77b00a7b5fdb047e14820bbed5e7f0fdb9b165c033cb7f01d708` |
| meridian-actuarial | 196 | `e11fa071013f3eb48b0f2d447b6f59340637927bfeaab72805ead959fe3c6900` |
| northgate-staffing | 166 | `cfa3a7f78d733cd20334c7751ae528d53c8a9c5af3b853982be0077d0524530f` |
| saltmarsh-environmental | 124 | `0d40e2e9a851aaa676096bc45cc89a388aff14ecf4297b9af1588a94f5a46d4f` |
| verdant-health | 103 | `68e6fe86284d8a694efe2d4b48269eac4c405f81c93c0c646b5234454ca9eacd` |
| **fleet** | 1649 | `c10078554cf6a7f40567bd3d3f8319cd4f4b16efaff20ee0f18cbeb25a467861` |
