# Checksum manifest — OrgSmith v2.1.1

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `2b3b5f18d9343612ddcd31af4ef7746ac0d8a54c0b1ba39ef302cee48797f0e7` |
| brackenridge-civil | 127 | `3f94781d90c3bd28d0ce6da6924ea13967a60c61499fbe9f3efdd48eb448ee27` |
| calderwood-partners | 505 | `87f146ed4b0564b526d8d0ff8f4410e9f728bfe308c7c0a5f35e2fc497ad0328` |
| hollowell-ip | 181 | `aad86b1a28ba8adf11147fee859e6cce9514993500aea5bacceeaf321fe3b717` |
| meridian-actuarial | 198 | `d2be9c478af29c49dbfdc887e7908f633aa1927ee9ae60c11653f94defd270df` |
| northgate-staffing | 168 | `22400c18e9ce898bbf3a3c203c87f0e3b42f721806472ea2c6f152f1c02d18d4` |
| saltmarsh-environmental | 126 | `7d43a021e5c15c3ac4421572f550854b17b342af5aa38c804f3f854a472e5ad8` |
| verdant-health | 105 | `dc8eec23b3594fc6a93d94e77409ceffe5d041ee8f415625822faf37a5447c89` |
| **fleet** | 1665 | `c8f4306abc3db9e25d8748ca38baf07bd598bdf3536a9308f6cbab0bbfd0ce51` |
