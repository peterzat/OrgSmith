# Checksum manifest — OrgSmith v2.3.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `ec10c81c087fb316cf8246a117834bb192a85bf8f08f834fc4005baf3c383fb6` |
| brackenridge-civil | 127 | `8310a4212e0af0d39913fc02598e907cc28aa1099557420dc17329fde4fc708e` |
| calderwood-partners | 505 | `e634bcb18fb039dd5b07ce2b6a3fffc807ae9038b94e2cdcf52cc91814833cd2` |
| hollowell-ip | 181 | `149057b5be6a76a87103195ef06c7a19cfdf3d99c0188492a4bc91596220c8e9` |
| meridian-actuarial | 198 | `5404dcc2176c039ff234cae9a7467c25e280efc378c54bca3423bc0006d30e53` |
| northgate-staffing | 200 | `0ab9fb83c81b23d0e058ec65f322e8e8191d3edf7670f84b5ec1bb0ef6035b83` |
| saltmarsh-environmental | 126 | `1fb7674024812849d93b5326a82a2d7f703b3eb123175a0d7d52be531eb04a83` |
| verdant-health | 105 | `44992ed93df69c129dfd726574981a769ec9ef729fcb776db13b55dbd2f3892a` |
| **fleet** | 1697 | `39f8f8b4c5f4781589861166b964ec942b013308d24ddddaf912d1776f78bc3f` |
