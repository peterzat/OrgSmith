# Security

## Security Review — 2026-07-17b (scope: paths)

**Summary:** Scan of the 29 files changed in the pre-M12 turn
(`62a5665..HEAD`, 11 commits). Product code changed this time, unlike the
previous scan: `orgsmith/airlock.py` (work-order serial), a new CLI verb, and
a new `orgsmith/schemas_export.py`. Also 19 generated JSON Schema files, a
verbatim external critique published into a public repo, and doc/backlog
edits. No BLOCK, no WARN, no NOTE.

### Findings

No security issues identified in the reviewed scope.

### Reviewed Surface

- **Swept per-commit, not against the net diff**, for the same reason as last
  time: `git diff 62a5665..HEAD` would hide a credential added and edited out
  within the range. `git log -p` over all added lines returns zero hits for
  private-key blocks, JWTs, AWS/GitHub/Slack/Google/Anthropic key shapes,
  bearer tokens, quoted `api_key|password|secret|token=` assignments, and
  postgres/mysql/mongodb/amqp connection strings.

- **The airlock still cannot reach a model or the network**, and the new code
  does not change that. `orgsmith/schemas_export.py` contains one `https://`
  string — `JSON_SCHEMA_DIALECT`, the JSON Schema 2020-12 dialect identifier
  that the spec requires be emitted in `$schema`. It is an identifier written
  into a file, not a URL that is fetched: no client, no `requests`/`urllib`/
  `socket` import anywhere in the module. Called out because a bare `https://`
  in this package is exactly the shape that should attract a second look.

- **`emit-schemas` writes files, so its path handling was read directly.**
  Output filenames are not attacker-influenced: `schema_filename()` derives
  them from `schema_id`, which is a `Literal` default on our own pydantic
  models (`schemas.py:25-45`), not from input. The `--out` directory is
  operator-chosen on the operator's own box and crosses no privilege boundary;
  `python -m orgsmith emit-schemas --out /etc` overwriting something is the
  operator instructing their own shell, which is not a vulnerability in this
  tool. No traversal reachable from either half.

- **Outbound disclosure, which is the real surface here.**
  `docs/EXTERNAL-CRITIQUE-2026-07-17.md` publishes a third party's verbatim
  text into a public repo. Read for that rather than for prose: it contains no
  credentials, no private URLs, no personal data, and no non-public
  information about this project — its content is an outside model's reading of
  the already-public snapshot, and every repo fact it cites is already
  published. The 19 emitted schemas were read for the same question: they are
  mechanical renderings of pydantic models whose source is already public, and
  they disclose field names and shapes that `schemas.py` already discloses.

- **No dependency manifest changed.** `requirements.txt` and
  `requirements-dev.txt` are untouched in the range; `test_requirements_are_pinned`
  still passes.

### Accepted Risks

None.

---
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

<!-- SECURITY_META: {"date":"2026-07-17","commit":"f897c63c0546cf7f350adab7178fa7ebb2a59fcd","scope":"paths","scanned_files":["BACKLOG.md","README.md","TESTING.md","docs/EXTERNAL-CRITIQUE-2026-07-17.md","docs/SCALE.md","orgsmith/airlock.py","orgsmith/cli.py","orgsmith/schemas_export.py","schemas/acl@1.json","schemas/authoring-deliverable@1.json","schemas/charter@1.json","schemas/corpus-metrics@1.json","schemas/docir@1.json","schemas/engagements@1.json","schemas/enrichment-deliverable@1.json","schemas/finance@1.json","schemas/foundation@1.json","schemas/graph-expected@1.json","schemas/graph@1.json","schemas/manifest-entry@1.json","schemas/mention-map@1.json","schemas/review-finding@1.json","schemas/review-findings@1.json","schemas/review-sample@1.json","schemas/scan-pages@1.json","schemas/state@1.json","schemas/work-order@1.json","tests/test_short.py","tests/test_unit_airlock.py"],"block":0,"warn":0,"note":0} -->
