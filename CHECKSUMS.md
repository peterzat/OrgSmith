# Checksum manifest — OrgSmith v2.3.0

SHA-256 rollup per committed org, over every committed file under
`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order
(each entry hashes `relpath\0` then the file's SHA-256). Regenerate with
`python tools/checksums.py`. The fleet digest is the SHA-256 of the
per-org `slug:digest` lines in the table order. `dev-mini` is the test
fixture and is excluded.

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `043a5d373c02036afe307f4b56f4b50f1ac74868619b8c723ee07fda0a098d51` |
| brackenridge-civil | 127 | `59d2a647da2c4a5a3e1f3af80d425aa0c2d3d481fc898eb8b5099afa14ba738e` |
| calderwood-partners | 505 | `900963955e9b5c5c934ad5db7edb85a4e520e60412ac29357e900c1c468a84b3` |
| hollowell-ip | 181 | `bdb9281bfefb69fe6c283409183c272583ad3e23ce803313e622170385dcbe04` |
| meridian-actuarial | 198 | `92903f3119834ef239646ff75d67817050485154c6bf775a5ca28ad44444c18a` |
| northgate-staffing | 200 | `b9179cc6f0e33d5ad123fe7ef6befa70696a8427cdb733157a921d281bd96fda` |
| saltmarsh-environmental | 126 | `9d181bb9db09d51df69e89e905e6db969e6a62f5053bdc9891a1f27aaf613005` |
| verdant-health | 105 | `895f483d699630bb0e09a19c870317d75bad63657b097ccffa477c09ee431028` |
| **fleet** | 1697 | `a112120bc7cbf642adec194db1fc67d03a30484fc858273da58dcb5812a74e1c` |
