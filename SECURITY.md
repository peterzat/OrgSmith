# Security

## Security Review — 2026-07-15 (scope: paths)

**Summary:** M5-open scan of the six paths touched by the format-knob
increment (committed range e8297aa..50eeefa, chiefly 849f346): doctor's
new dependency probes, the M5 charter knobs in schemas.py, six new
pinned dependencies, the post-fix ACL validator family, and the ACL and
compat test suites. No new findings. The prior WARN (ACL rules
skippable by deleting the ledger) is verified remediated at HEAD with
regression tests. The two open NOTEs carry forward unchanged; both live
in files outside this scope that are untouched since the prior scan, so
their citations remain valid.

### Findings

No new security issues identified in the reviewed scope. Two open NOTEs
carry forward from prior reviews:

**[NOTE] orgsmith/evals/score.py:266-271,304-311 — untrusted
answers-file strings printed raw to the terminal in score failure
output (carried forward from 2026-07-14; file unchanged since the prior
scan; outside this run's path scope)**

  Attack vector: the designed use of `score --answers <file>` is
  grading a third-party extractor's output, so the answers file is
  untrusted input. A malicious file embeds ANSI escape sequences in
  strings that land in `missing`/`extra` or `docs_missing`/`docs_extra`,
  which the human-readable failure printers join and print unsanitized,
  letting the file manipulate the grader's terminal display, for
  example repainting the score line to show a passing result. Applies
  to retrieval, extraction, and visibility suites, and to unconstrained
  `id` fields from a third-party `--evals-dir`.
  Evidence: `", ".join(failure["extra"])` and sibling raw joins; values
  by contrast pass through `!r`, and JSON mode escapes control
  characters via `json.dumps` defaults.
  Remediation: strip control characters (or apply `!r`) to answers-file
  and evals-dir strings in the human-readable failure printers.

**[NOTE] orgsmith/render/pdf.py:37,64 — letterhead lines rendered
unescaped (residual from prior reviews; no current attack vector; file
unchanged since the prior scan; outside this run's path scope)**

  Attack vector: none concrete. The letterhead is `charter.name` and
  `www.{charter.domain}`, interpolated raw into the HTML template under
  `Environment(autoescape=False)` (pdf.py:73). Only the recipe author
  controls the charter, and `no_remote_fetcher` blocks all non-`data:`
  URLs, so injected markup cannot egress or read files.
  Remediation: `html.escape()` the letterhead lines (and CSS-escape the
  `@top-left` string) when building the template context. One-line
  change, no urgency.

### Reviewed Surface

- Prior WARN remediation verified at HEAD: `_needs_acl` gates the
  grandfather skip on `acl_posture == "open"` (rules.py:111-117);
  ACL-01/02/03 each yield a missing-ledger finding when acl.json is
  absent on a non-open org (`_acl_missing`, rules.py:504-511, guards at
  515-517, 530-532, 548-550); MAN-01 whitelists PERMISSIONS.md only
  while the ACL ledger exists (rules.py:291,306-308); acl_03 renders
  the PERMISSIONS.md comparison from the recomputed ledger, never the
  untrusted on-disk one (rules.py:568). Regression tests cover the
  stripped-ledger departmental org, the stray PERMISSIONS.md on a
  pre-ACL org, and the ghost-principal full run
  (tests/test_unit_acl.py:178-217).
- doctor.py: no subprocess, no network, no file reads beyond
  state.json. Probes are `importlib.import_module` over a hardcoded
  module list plus `shutil.which("soffice")` for presence only; nothing
  executes soffice. Probe results written into state.json are inert on
  the committed fixtures ("ok" strings, the Python version, the
  absent-optional message; no paths or usernames). A MISSING entry
  embeds only the local ImportError text and coincides with a failing
  doctor run (exit 1).
- Dependencies: six new exactly-pinned runtime deps (python-pptx 1.0.2,
  pypdfium2 5.11.0, Pillow 12.3.0, numpy 2.2.6, olefile 0.47,
  xlrd 2.0.2); installed versions match the pins. None has a known CVE
  at the reviewer's knowledge cutoff: Pillow 12.3.0 postdates the
  11.3.0 fix for CVE-2025-48379, xlrd 2.x contains no XML/xlsx code
  path, olefile is pure Python. Offline review, no live vulnerability
  database query. Today these deps are import-probed only
  (doctor.py:28-33); no orgsmith code parses input with them yet, so
  the untrusted-parse surface for .pptx/.xls/OLE arrives with later M5
  increments under the SPEC's stated trust boundary (soffice is
  generation-only; all validation-time reading is pure Python). That
  future validator code should be scanned when it lands.
- Schema knobs: `scanned_ratio`, `legacy_ratio`, `ocr_layer_rate` are
  range-bounded 0..1 (schemas.py:89-91) and the cross-field guard
  (`ocr_layer_rate` requires `scanned_ratio > 0`, schemas.py:103-107)
  is tested (tests/test_unit_compat.py:84-95); pre-M5 fixtures assert
  all knobs default off (tests/test_unit_compat.py:65-82). Robustness
  observation for the code-review lane, not a security finding:
  FormatMix counts (schemas.py:68-74) are unconstrained ints, so a
  recipe with a negative count that still sums to `target_docs` passes
  the charter validator; the recipe author is the trusted operator and
  no privilege boundary is crossed.
- Path safety unchanged: artifacts.py, naming.py, and paths.py are
  untouched since the prior scan, so manifest paths joined by rules.py
  (`doc_text`, `doc_pages`, file_01, man_01) remain check_relpath
  validated at load; ACL grant doc strings are compared against the
  manifest set and never joined to the filesystem.
- Airlock intact: no scoped file imports network or model libraries;
  the charter-side knob additions do not alter the work-order or
  deliverable contracts, and FactBrief still withholds rendered fact
  values from the model (schemas.py:489-493).
- Secrets and PII: pattern grep over the full committed range
  e8297aa..50eeefa and over requirements.txt history: clean (the only
  hits are prose in the security and review logs themselves). Scoped
  test files use synthetic ids only (p:ghost.reader, fictional slugs).
  No scoped file handles credentials.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-15, scope paths, commit e8297aa): M4-close scan
of the ACL overlay surface, visibility eval machinery, and the
bramblewood-legal fixture; 1 WARN (ACL validator family skippable by
deleting ledger/acl.json on a non-open org, with PERMISSIONS.md
whitelisted unconditionally) plus 2 carried NOTEs; fixture verified
synthetic end to end, secrets and supply chain clean. That WARN was
remediated in df11e42 and the fix is re-verified by the current entry.*

<!-- SECURITY_META: {"date":"2026-07-15","commit":"50eeefa28e77e0eab7f32e0298e2488d4cbb15b7","scope":"paths","scanned_files":["orgsmith/doctor.py","orgsmith/schemas.py","orgsmith/validate/rules.py","requirements.txt","tests/test_unit_acl.py","tests/test_unit_compat.py"],"block":0,"warn":0,"note":2} -->
