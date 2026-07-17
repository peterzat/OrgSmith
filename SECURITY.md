# Security

## Security Review — 2026-07-17 (scope: paths)

**Summary:** Re-scan of the eight files changed since the M11b scan
(de60065..HEAD, two commits): a documentation pass over README.md and three
`docs/` files, three test modules touched by a prior review's fix loop, and
the CODEREVIEW.md record. No product code changed and no dependency manifest
changed. No BLOCK, no WARN, no NOTE. The docs pass was the reason for the
re-scan: it quotes board findings, model ids, vendor pricing, and repo paths
into a README that publishes to a public GitHub repo, so it was read as
outbound disclosure rather than as prose.

### Findings

No security issues identified in the reviewed scope.

### Reviewed Surface

- **Nothing secret-shaped entered the range, and the sweep was run per-commit
  rather than against the net diff.** `git diff de60065..HEAD` would hide a
  credential added in `4c4f9b9` and removed in `f7f945c`, so `git log -p` over
  the range was swept instead, across all eight files including CODEREVIEW.md
  and SECURITY.md themselves: Anthropic/OpenAI/AWS/GitHub/Slack/Google key
  shapes, JWTs, private-key blocks, bearer tokens, quoted
  `api_key|password|secret|token=` assignments, and
  postgres/mysql/mongodb/amqp connection strings all return zero hits. The
  distinction is the point here, because a docs pass is exactly the kind of
  change where a value gets pasted in for illustration and edited out a commit
  later.
- **The docs pass discloses nothing but public facts.** Every added line was
  swept for URLs, emails, IPs, phone numbers, and local paths. The complete
  set of hits is one URL, `https://github.com/peterzat/zat.env`, which is the
  author's own public repo, is deliberate self-attribution in a public
  README's provenance section, and **predates this diff** (added in `e516334`,
  present at de60065:README.md:639); the line is reflowed prose, not new
  disclosure. No email address, IP, phone number, `/home/` or `/Users/` path,
  hostname, tailnet name, or `localhost` appears in any added line. The
  generation box stays unnamed, which is the exposure a docs pass would most
  plausibly create and did not.
- **The quoted board findings, model ids, and pricing are not sensitive.**
  `claude-opus-4-8[1m]`, the effort levels (`xhigh`, `max`), and the $3/$15 and
  $5/$25 per-MTok rate cards are published vendor facts, not entitlements: they
  name no account, no key, no org id, and no endpoint, and the README states
  affirmatively that OrgSmith needs no API keys. The quoted findings
  (README.md:209-247) describe synthetic orgs, and the personas the removed
  text named ("Jim/James Grant", the two-Joseph collision) are fixture
  personas, not people. No real-world person, client, or firm is named in any
  added line.
- **The README is published for downstream indexing and carries no injection
  payload.** It now quotes model-authored review-board prose at length, which
  makes it model output republished as documentation, and the repo's own
  fixtures are explicitly intended for downstream RAG. The added lines were
  swept for `ignore previous instructions`, `disregard`, `system prompt`, role
  tags (`<|im_start|>`, `[INST]`), and `as an AI language model`: zero hits.
  Worth stating why this was checked rather than waved through: the M11b scan
  applied the same screen to the fixture corpus, and a README quoting the same
  models' output is the same class of surface with a wider audience.
- **The three test changes are exactly three executable lines, and all move
  toward strictness.** Isolating non-comment changes from the diff confirms
  the executable delta is: `test_unit_compat.py:114` adds
  `assert culture.ocr_layer_rate == 0.0` (one more knob asserted inert on an
  old charter); `test_unit_evals.py:286` tightens `locations <= expected` to
  `locations == expected` with a message that now also reports the missing
  set; and `test_unit_evals.py:400` changes "four orgs" to "five" inside a
  docstring. Everything else in the diff is module-docstring and comment prose.
  The `<=` to `==` tightening is the security-relevant one and it closes rather
  than opens: a subset assertion let an org silently fail to produce a location
  its charter enables, which is grandfather-by-absence, the exact pattern
  CLAUDE.md forbids and the M11b diff was already closing elsewhere.
- **No test reads or writes outside `tmp_path` or the repo, verified at the
  changed call sites rather than inferred.** `test_unit_compat.py` performs no
  I/O at all and imports only pydantic and `orgsmith.schemas`. The tightened
  assertion in `test_extraction_covers_committed_fixtures`
  (test_unit_evals.py:257-290) is read-only: it iterates `REPO / "companies"`
  and loads charters, writing nothing. `test_org_regen.py`'s `regenerated`
  fixture (test_org_regen.py:142-153) roots every write at
  `tmp_path_factory.mktemp("regen")` and touches the repo only to
  `copytree` recipes out of it. No `subprocess`, `eval`, `exec`, `pickle`,
  `yaml.load`, `os.system`, socket, or HTTP client is imported by any of the
  three, and no archive is extracted, so there is no zip-slip surface and the
  airlock holds in test.
- **Not re-verified, and named rather than implied:** the M9 `render/pdf.py`
  letterhead NOTE (recipe-author-controlled interpolation under
  `autoescape=False`) is against unchanged code outside this path scope and
  **carries forward open**. It is distinct from the intra-paragraph newline
  bug that `docs/MODEL-AB.md` records as fixed at M9; that diff line closes a
  rendering defect, not this one. Dimensions with no surface in this scope:
  authentication/authorization, dependency and supply chain (no manifest
  changed), and infrastructure (no config changed) were not examined because
  no file in scope touches them, which is a scope statement rather than a
  clean bill. The M11b fixture-corpus conclusions and the M11a airlock
  conclusions stand unre-examined by design: no file under `companies/` or
  `orgsmith/` changed. Sanity check: the three changed modules pass (86
  tests), and `git status` is clean.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-17, scope paths, commit de60065): M11b scan of ~850
newly committed model-generated fixture files across five new synthetic orgs,
eight test modules, and two skill files; 0 BLOCK / 0 WARN / 0 NOTE. It treated
the fixture corpus as untrusted output because it publishes to a public repo,
verified the NAME-01 and PROV-01 screens by execution rather than by reading,
and established by decode-and-scan that the corpus carries no secrets, no real
PII, no macro/DDE/JavaScript payloads in its OOXML/OLE/PDF binaries, no
generation-box identity in document metadata, and no leftover `{{fact:}}`
placeholders or injection-shaped text in the rendered tree. It carried forward
the M9 `render/pdf.py` letterhead NOTE.*

<!-- SECURITY_META: {"date":"2026-07-17","commit":"f7f945cf64ea7d9e1266e63fa2a0a09c483a9593","scope":"paths","scanned_files":["CODEREVIEW.md","README.md","docs/MODEL-AB.md","docs/REVIEW-CALIBRATION.md","docs/SCALE.md","tests/test_org_regen.py","tests/test_unit_compat.py","tests/test_unit_evals.py"],"block":0,"warn":0,"note":0} -->
