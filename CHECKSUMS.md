# Checksum manifest — OrgSmith v2.2.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `f285cc5ee59f660ba136b660226cbb03366032202209c037c6e64e05a13ccd16` |
| brackenridge-civil | 127 | `0266fdd672da2ae28eba03af4da656a81e8499567da01e9058b2e32f16831758` |
| calderwood-partners | 505 | `c3b1e4307bfe22c0f6aef22a8f33b45d8fd366bc468922c46afcc603f502e394` |
| hollowell-ip | 181 | `0d7e53b35a3d2ea4375101ed18ba8c0a4c4a7d408e3d49d46fd6eda1f4678f8a` |
| meridian-actuarial | 198 | `1a85e072a42eaf147b5c68bd85d3eca6d28efb1b50769e13008ff8122c75c601` |
| northgate-staffing | 200 | `11a9358a35d9354dc9a8ef8a0ad00a5b9c83f8885752949a491a6b10a36e1b35` |
| saltmarsh-environmental | 126 | `c85403862f02274c091e9edca27e0bead348cd139e31892b4cc0cad6724167be` |
| verdant-health | 105 | `599fda716a1fe2bd2c3a425ef4fdb6cb4fd87c87986ca9b4c889c9a36a4ba537` |
| **fleet** | 1697 | `ae1125ff236893ad8507a28d226b12fc6e71635a937fcf2ab03bb3fd16e0489f` |
