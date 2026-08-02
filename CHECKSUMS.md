# Checksum manifest — OrgSmith v2.3.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `28bfb6dacf9ef06984ddcd31b3649ed851f18cc73b235bc2a99d715d041e5a3e` |
| brackenridge-civil | 127 | `0f6b2070fdc1d82552b7a03b22d7ad8d0c1c3b18401247807e5fe1221641283b` |
| calderwood-partners | 505 | `289879742f44f20dd01a9637631e94d99735e13bba7beff7be312c98d69c3415` |
| hollowell-ip | 181 | `ae75ace9f2b3f2cab578afe9ff59acc81051f5b82f956e264a3e79f274d419a6` |
| meridian-actuarial | 198 | `ff25da9de72c9bf80ea2bd66190441041094e93e86a00dc2ea473a04b4ba7ae4` |
| northgate-staffing | 200 | `0ff7ad47b8e8bd90fc0017f74e842e53026971b3100e75ed3c905f04e672855d` |
| saltmarsh-environmental | 126 | `9e5e7c090e6b30d6958844a2c6cc45fdbe2b429bce7a0d515aa69c3fd03e87c3` |
| verdant-health | 105 | `17233284f92e227f4330289c7829b07ebc33b2740924e4119dcd871d07cfcd15` |
| **fleet** | 1697 | `108198c2c240f95a91780907404ca7d825c61e0c001aebdca05bfdfbf4942df3` |
