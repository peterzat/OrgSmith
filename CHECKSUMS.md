# Checksum manifest — OrgSmith v2.3.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `d7e1095e77919e84599c1ac0360a7a810c409819f0f53f266ae8013763397d8b` |
| brackenridge-civil | 127 | `a15330eaf13192a338d23539fdb36c752aa936e89895dbd84d764721a41690ff` |
| calderwood-partners | 505 | `6fe7a83db8301c4157347f93d7dcbe43b8512784b0ce0c7821df5ca5ea14d36c` |
| hollowell-ip | 181 | `c69013d928839ee8bb7967babc3549e6a5562566510deed3c3af20da27b882d6` |
| meridian-actuarial | 198 | `78357ed8a3a920cd2c9fc18248905ec930ed8b76781231c5226d3e7c5453697e` |
| northgate-staffing | 200 | `79c7ed40e7cd9d9d83e6ad4be2c8239b2411d7a83223c088f761ae6d869d7334` |
| saltmarsh-environmental | 126 | `55ff7778bdfcd5f0cd3235219506faa4cea4cccd054ea75ad51d95198aa2a290` |
| verdant-health | 105 | `43f03845b3dfdfd2be37d0df16a2c04fa581e055670bacb7b0727567043fd648` |
| **fleet** | 1697 | `1880f7f5feefc776ef3cfacffc174303e02d00f4d1ee9296471765e875b5b86a` |
