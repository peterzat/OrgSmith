# Security

## Security Review — 2026-07-15 (scope: paths)

**Summary:** M4-close scan of the ACL overlay surface, the visibility
eval machinery, and the bramblewood-legal fixture (the committed range
`1830a11..e8297aa` plus the pending acl_03 fix, which the prior
changes-only entry flagged as unscanned). One new WARN: the ACL
validator family is skippable by deleting `ledger/acl.json`, even for
an org whose charter posture claims restrictions, so a tampered bundle
can carry an unverified PERMISSIONS.md and still validate clean. No
secrets, no PII, no injection paths; the fixture is verifiably
synthetic end to end. The two open NOTEs carry forward, one of them
with coverage extended to the new visibility suite.

### Findings

**[WARN] orgsmith/validate/rules.py:111-114,288 — ACL rules are
skippable by deleting the ledger, leaving PERMISSIONS.md and the
charter's posture claim unverified**

  Attack vector: whoever supplies an org bundle to a consumer who runs
  `orgsmith validate` as the integrity check (the same tamper threat
  model the ACL recomputation rules were built for). Delete
  `ledger/acl.json` and keep or forge `PERMISSIONS.md`: `_needs_acl`
  (rules.py:111-114) keys the grandfather skip solely on the ledger
  file's existence, so ACL-01/02/03 skip with the misleading reason
  "org predates the ACL overlay"; MAN-01 whitelists PERMISSIONS.md
  unconditionally via `_SHARE_EXTRAS` (rules.py:288); the run exits 0
  with JSON `ok: true` (validate/__init__.py:36-65). The org tier
  asserts only exit 0 (tests/test_org_fleet.py:35-37), so even the
  committed fixture's ACL could be stripped with tests green. The
  grandfather rationale does not cover this state: every pre-M4
  fixture has posture `open` (asserted at
  tests/test_unit_compat.py:56-62), so `departmental` with no ledger
  is never a legitimately generated org.
  Evidence: `_needs_acl` returns a skip reason on `ctx.acl is None`
  regardless of `ctx.charter.acl_posture`; `_SHARE_EXTRAS = {"TOC.md",
  "PERMISSIONS.md"}` applies to every org. Mitigations that keep this
  WARN rather than BLOCK: the skips are printed and enumerated in the
  JSON payload, nothing falsely reports the ACL as verified, and
  `score --suite visibility` fails loudly when the suite is absent.
  Remediation: when `charter.acl_posture != "open"` and acl.json is
  missing, fail instead of skipping (tighten `_needs_acl` or add an
  ACL rule that runs off the charter alone); optionally accept
  PERMISSIONS.md as a planned share extra only when the org has an ACL
  ledger. Add a ledger-deletion corruption test alongside the existing
  ACL corruption tests.

**[NOTE] orgsmith/evals/score.py:266-271,304-311 — untrusted
answers-file strings printed raw to the terminal in score failure
output (carried forward from 2026-07-14; coverage now includes the M4
visibility suite)**

  Attack vector: the designed use of `score --answers <file>` is
  grading a third-party extractor's output, so the answers file is
  untrusted input. A malicious file embeds ANSI escape sequences in
  strings that land in `missing`/`extra` (score.py:266-271) or
  `docs_missing`/`docs_extra` (score.py:304-311), which the
  human-readable failure printers join and print unsanitized, letting
  the file manipulate the grader's terminal display, for example
  repainting the score line to show a passing result. The new
  visibility suite grades through the same `_score_docset` result and
  the same printer branch (score.py:242-243,263-272), so
  permission-audit grading is now in the affected class too, as are
  unconstrained `id` fields from a third-party `--evals-dir`.
  Evidence: `", ".join(failure["extra"])` and sibling raw joins;
  values by contrast pass through `!r`, and JSON mode escapes control
  characters via `json.dumps` defaults.
  Remediation: strip control characters (or apply `!r`) to
  answers-file and evals-dir strings in the human-readable failure
  printers.

**[NOTE] orgsmith/render/pdf.py:37,64 — letterhead lines rendered
unescaped (residual from prior reviews; no current attack vector;
outside this run's path scope but citations re-verified at HEAD)**

  Attack vector: none concrete. The letterhead is `charter.name` and
  `www.{charter.domain}`, interpolated raw into the HTML template
  under `Environment(autoescape=False)` (pdf.py:73). Only the recipe
  author controls the charter, and `no_remote_fetcher` blocks all
  non-`data:` URLs, so injected markup cannot egress or read files.
  Remediation: `html.escape()` the letterhead lines (and CSS-escape
  the `@top-left` string) when building the template context. One-line
  change, no urgency.

### Reviewed Surface

- ACL core (`orgsmith/acl.py`): pure function of committed artifacts,
  no network, no subprocess, no RNG. `render_permissions` output is
  inert markdown built from owner-authored recipe and roster fields.
  Robustness observation for the code-review lane, not a security
  finding: acl_03 calls `derive_acl` on untrusted artifacts, and its
  raw lookups (`eng_by_id[entry.engagement]` acl.py:41, CEO `next()`
  acl.py:33) crash the validate run on a tampered engagements or
  foundation ledger, the same loud-failure class as date_02's
  `foundation.person` and fin_02's `render_params["year"]`. A crash
  exits nonzero with a traceback, so tampering is never certified
  clean; impact is diagnostics, not integrity.
- Path safety: manifest paths are re-validated by `check_relpath` at
  every load (artifacts.py:70-81), rejecting absolute paths, empty
  components, `..`, backslashes, and control characters
  (naming.py:13-49) before any filesystem join in validate or evals.
  The CLI's validate-target handling reduces to a basename; all verbs
  are local and offline, no privilege boundary crossed.
- Scoring inputs: answers files and evals-dir contents are parsed by
  strict pydantic models (`extra="forbid"`), malformed input exits 2
  with a schema message and no partial state; scoring never joins
  answer strings to the filesystem.
- Airlock intact: none of the scoped files import network or model
  libraries; model touchpoints remain the work-order/deliverable file
  exchange, and the committed bramblewood deliverables were
  schema-validated at ingest.
- Fixture content (`companies/bramblewood-legal*`,
  `recipes/bramblewood-legal`): all people, orgs, emails, and prose
  are synthetic; phones sit in the reserved 555-01xx fictional block;
  emails only at the three fixture-owned fictional domains; binary
  docx/xlsx/pdf members contain only standard OOXML namespace URIs and
  synthetic text (verified by extraction); TOC.md and PERMISSIONS.md
  match the ledgers. Client-name realism (e.g. "Foley Group") is
  faker-style and generic; the name-screen validator remains a tracked
  BACKLOG item, consistent with prior fixture reviews. The `authors`
  field in pyproject.toml carries the repo owner's name as deliberate
  authorship metadata, treated like git commit metadata per prior
  reviews.
- Secrets: pattern grep over all scoped text files, fixture binary
  members, extracted PDF text, and the full committed M4 range diff
  (`git diff 1830a11..e8297aa`): clean. The single grep hit is prose
  in a superseded SECURITY.md section discussing a `file:///etc/passwd`
  test string. No scoped file handles credentials, so no per-file
  history walk beyond the range scan was warranted.
- Dependencies: runtime and dev requirements are exactly pinned with
  per-line rationale (requirements.txt, requirements-dev.txt); the
  installed versions match the pins, and none has a known outstanding
  CVE (pydantic 2.13.4, Jinja2 3.1.6, pypdf 6.14.2, python-docx 1.2.0,
  openpyxl 3.1.5, weasyprint 69.0, pikepdf 10.10.0, pytest 9.1.1).
  pyproject.toml declares metadata and pytest config only.
- Scope note: this run covers the listed paths at the current working
  tree (HEAD e8297aa plus the pending acl_03 fix already scanned by
  the prior changes-only entry). The M4 range flagged as unscanned by
  the prior entry is hereby covered; render/, charter/, fabric/,
  docplan/, authoring/, foundation/ internals were out of scope this
  run and last had full coverage in the M3 full review.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-15, scope changes-only, commit e8297aa): pending
diff was the acl_03 fix (render PERMISSIONS.md comparison text from the
recomputed ledger instead of the on-disk one), its regression test, and
CODEREVIEW.md bookkeeping; no new findings, fix judged
security-positive (closes a KeyError crash on tampered acl.json and
strengthens drift detection), secret grep clean, and the M4 committed
range was flagged as still unscanned, which the current entry now
covers.*

<!-- SECURITY_META: {"date":"2026-07-15","commit":"e8297aa227cde3e4d9cce82ce3a92014ea76b966","scope":"paths","scanned_files":["companies/bramblewood-legal","companies/bramblewood-legal-metadata","orgsmith/__init__.py","orgsmith/acl.py","orgsmith/artifacts.py","orgsmith/cli.py","orgsmith/evals/emit.py","orgsmith/evals/score.py","orgsmith/paths.py","orgsmith/schemas.py","orgsmith/validate/rules.py","pyproject.toml","recipes/bramblewood-legal","tests/conftest.py","tests/test_unit_acl.py","tests/test_unit_compat.py","tests/test_unit_evals.py","tests/test_unit_validate_graph.py"],"block":0,"warn":1,"note":2} -->
