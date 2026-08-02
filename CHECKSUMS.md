# Checksum manifest — OrgSmith v2.1.1

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 254 | `fc95b3f24b35ded6a9a51a8eed86ae6601bbf86297217e8031f0cc3126c1bc87` |
| brackenridge-civil | 126 | `97800f37541dd4cd9d8ba88e4f543835d361039193e6cc19bf461150cb3521c2` |
| calderwood-partners | 504 | `b4e2d2606884482d0650a3d3316ea2f7b538c76256586830c2d9c78ed49ebcd4` |
| hollowell-ip | 180 | `59895dd42928de5ed2ed4662c34f8d08b636bea80473750ce86cc9b810453fdd` |
| meridian-actuarial | 197 | `db6195a2c72542c696c634ad2a412ce27baaa9e5542dfcde84a701a38195bbf1` |
| northgate-staffing | 167 | `dbad97f90b27c602da0fdb96367d4085b197601b6e867f0f08ee621ca4fe201c` |
| saltmarsh-environmental | 125 | `c0229d236a868e5a03d879bb8b854b6e4f22a0bc1aef29a57104fb024bda7ab9` |
| verdant-health | 104 | `02da48da393f94fc16f918a6c2878eac81005c6a72b95e795a3947e9323d48a7` |
| **fleet** | 1657 | `536ef20479beae4d46a05ac4bdc565d3fa2851cda6e293974db150371b01ad81` |
