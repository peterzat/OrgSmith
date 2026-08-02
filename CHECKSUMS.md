# Checksum manifest — OrgSmith v2.1.1

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 252 | `a238d43a778b37cc324a70ed031cadb79e61f0a83bfd93c25ef7315b3fd48ff2` |
| brackenridge-civil | 124 | `cc2ffea39af40a23b7fbeb8014ac5f485af518454899809de721d3df098ec216` |
| calderwood-partners | 502 | `622234f5dee9d3d4803a6c2970930e6dc87ad2d78e743b00d2135d915be5a978` |
| hollowell-ip | 178 | `17ac7397ce3028e8404d2e86efc924a70746ac752d792c4f28425b1355f8876f` |
| meridian-actuarial | 195 | `72e6e9037b5bfcf2d670986e422df4e137b7a7e49af08372a52981b2fe669868` |
| northgate-staffing | 165 | `85e5f7115f68eee5c05682c193a3174e9c1aad913c830808e0c300d23f3d16df` |
| saltmarsh-environmental | 123 | `2e4708c9c390c49beb0b7bd6e95c60e57ef067406a990e0f3dc7762c93335cf4` |
| verdant-health | 102 | `ecfc6177787b2754fc0f576a165085b573819fd838c34ef6ea4c9e7182acc83b` |
| **fleet** | 1641 | `9009dc911909382e9c1e6df91ec12157a08042e9fded34b0f76cf58c82136e82` |
