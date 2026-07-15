# Security

## Security Review — 2026-07-15 (scope: paths)

**Summary:** M5-close scan of the document-formats surface (range
50eeefa..449dcdf): the pptx/eml/scan/legacy render pipeline, the single
subprocess touchpoint (LibreOffice conversion), scan planning and the
OCR corruption engine, the new EML/SCAN/LEG validator families, eval
tag derivation, authoring contexts and ingest, and the two new recipe
charters. This fulfills the prior entry's deferred item: the validator
code that parses untrusted fixture bytes with the M5 dependencies has
landed and is scanned here. One new NOTE (ingest rejection printer
echoes deliverable-controlled strings raw to the terminal, the same
class as the carried score.py NOTE). No BLOCKs, no WARNs. The two
prior NOTEs carry forward; both files are unchanged in this range.

### Findings

**[NOTE] orgsmith/authoring/ingest.py:71,159,210-212 — deliverable
strings echoed raw to the terminal in ingest rejection output**

  Attack vector: the authoring deliverable is the airlock's untrusted
  input (model-authored, or any file passed to `--ingest <file>`).
  `DocIR.doc_id` is an unconstrained str (schemas.py:490-493) and
  placeholder ids are extracted from model prose with charset `[^}]*`
  (ingest.py:30, 48-49), so a deliverable can embed ANSI escape
  sequences via JSON `\u001b` escapes in a doc_id or a
  `{{fact:...}}` id. Both flow into `', '.join(...)` problem strings
  ("doc ids not in work order", "unbriefed fact ids used") that the
  rejection printer emits unsanitized, letting a misbehaving or
  adversarial deliverable repaint the operator's terminal, for example
  erasing the rejection listing and printing a fake success line.
  Verified reachable end to end with a probe deliverable at HEAD.
  Impact is display-only: the exit code stays 1, nothing is written
  (the unknown-doc-id problem forces return before the write loop at
  ingest.py:209-218), and skill automation keys off exit codes, so
  only a human reading the terminal can be misled. The schema-error
  path at ingest.py:147 is not affected (pydantic reprs escape control
  characters).
  Evidence: probe deliverable with `\u001b[2K...` doc_id and
  `{{fact:\u001b[31m...}}` placeholder passes
  `AuthoringDeliverable.model_validate_json` and
  `placeholders_in` returns the raw ESC bytes.
  Remediation: apply `!r` (or strip control characters) to
  deliverable-derived ids when building problem strings, or print each
  problem line through a control-character filter. Constraining
  `DocIR.doc_id` to `^d:\d{4}$` would also close the doc_id half but
  narrows a versioned deliverable contract; the printer fix is the
  minimal change. Fix alongside the score.py NOTE below, same class.

**[NOTE] orgsmith/evals/score.py:266-271,304-311 — untrusted
answers-file strings printed raw to the terminal in score failure
output (carried forward from 2026-07-14; file unchanged in this
range, verified by empty diff; outside this run's path scope)**

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
unchanged in this range, verified by empty diff; outside this run's
path scope)**

  Attack vector: none concrete. The letterhead is `charter.name` and
  `www.{charter.domain}`, interpolated raw into the HTML template under
  `Environment(autoescape=False)` (pdf.py:73). Only the recipe author
  controls the charter, and `no_remote_fetcher` blocks all non-`data:`
  URLs, so injected markup cannot egress or read files.
  Remediation: `html.escape()` the letterhead lines (and CSS-escape the
  `@top-left` string) when building the template context. One-line
  change, no urgency.

### Reviewed Surface

- Subprocess boundary (the pipeline's only shell-out): render_legacy
  invokes soffice via argv list, no shell (legacy.py:142-155).
  Arguments are the PATH-resolved binary (`require_soffice`), a
  Literal-constrained format from the pydantic-validated manifest, and
  tmpdir paths render created itself; an isolated
  `-env:UserInstallation` profile in the tmpdir, `capture_output`, and
  a 300s timeout bound the run. Input is the marker-verified modern
  intermediate render just produced, never external bytes. Render
  fails closed: missing soffice aborts before any doc renders
  (render/__init__.py:75-80), and an unmarked or unconverted result is
  a SystemExit, not a shipped file (legacy.py:157-169).
- Path safety: check_relpath (rejects `..`, absolute, control and
  forbidden characters) re-validates on every manifest load
  (artifacts.py:70-81) before render or validate joins entry.path to
  the share; the planner gates every planned path the same way
  (planner.py:137-140). DocIR files are written only for doc_ids
  present in the work order (unknown ids force rejection before the
  write loop, ingest.py:154-162, 209-218), and scan-archive filenames
  derive from pattern-validated manifest doc_ids (`^d:\d{4}$`).
  sanitize_component strips separators from client names used in
  folders (naming.py:52-58).
- eml integrity: every transport header is a pure function of ledger
  data (`expected_headers`, eml.py:22-43), shared verbatim with EML-01
  so renderer and checker cannot drift; stdlib EmailMessage under
  policy.SMTP rejects CR/LF in header values, closing header
  injection; bodies carry model prose only via set_content. Message-ID
  domains are the recipes' fictional domains; files are corpus
  artifacts, never transmitted mail.
- PDF content injection: the OCR text layer is written into content
  streams through `_pdf_escape`, which escapes backslash before
  parentheses (scan.py:95-97), and the layer text is pypdf's
  extraction of the self-rendered pdf, not raw model text. The
  corruption engine cannot alter planted surfaces: protected-span
  masking plus a post-check that recounts every surface and raises on
  drift (scan.py:204-220).
- Validator parsing of untrusted fixture bytes (the prior entry's
  deferred scan, now landed): FILE-01 wraps every native reader in a
  catch-all that converts parser failures into findings
  (rules.py:449-450); FIN-02's xlrd open is wrapped
  (rules.py:366-369); SCAN-01 catches pikepdf.PdfError
  (rules.py:836-838). Residual unwrapped paths (pypdf inside
  doc_text/scan_01, python-pptx inside _pptx_text) crash the run with
  a traceback and nonzero exit on malformed input: loud failure, never
  a silent pass. Robustness of those paths is code-review material,
  not a vulnerability.
- Tamper evidence follows the M4 lesson: rules skip only on the
  charter knob (EML-01/SCAN-01/SCAN-02/LEG-01 availability guards,
  rules.py:216-231), and knob-on-with-artifact-missing fails
  (manifest stripped of eml docs, missing/stray/gutted scan archives,
  legacy format stripped back to modern), each direction
  corruption-tested (test_unit_eml.py:140-146,
  test_unit_scan_validate.py:75-149, test_unit_legacy.py:227-239).
  FILE-01/PROV-01 treat unknown formats as findings, never a pass
  (rules.py:446-448, 966-968; test_unit_legacy.py:249-270).
- Residual risks accepted by design, documented in code, requiring
  repository write access (no privilege boundary crossed): image-only
  scan text obligations run against the metadata archive because
  pixels cannot be text-verified without OCR (SCAN-02 ties archive
  page counts to the rendered pdf, and a gutted archive fails FACT-01
  loudly); legacy .doc/.ppt prose obligations run against the
  fact-resolved DocIR because no pure-Python binary-format text
  extractor exists (rules.py:126-133); LEG-01 and PROV-01 still verify
  container type, stream, and marker on the binary itself.
- Airlock intact: work orders brief fact ids with hints and withhold
  rendered values (schemas.py:509-514); engagement summaries redact
  fee and dates (contexts.py:109-117); ingest rejects literal
  money/date surfaces arriving outside placeholders (ingest.py:176-187)
  and resolve_docir fails loudly on unknown or unresolved placeholders
  (resolve.py:20-30). Grep over orgsmith/ finds no network or model
  imports; the soffice call above is the package's only subprocess.
  match_outstanding resolves the work-order path from state, never
  from the deliverable's id string (airlock.py:60-75).
- Secrets and PII: pattern grep over all 24 scoped files and `git log
  -p` over the range and both charter histories: clean (the only
  "token" hits are the provenance marker token). The new charters
  contain fictional firms, no personal names, no contact details;
  test data is synthetic. No scoped file handles credentials.
- Dependencies: requirements.txt unchanged in this range; the six M5
  deps were verified pinned and CVE-clean in the prior entry. Offline
  review, no live vulnerability database query.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-15, scope paths, commit 50eeefa): M5-opening
scan of the format-knob increment (doctor probes, charter knobs, six
new pinned dependencies, ACL validator family and its test suites); no
new findings, the M4 ACL skip-evasion WARN verified remediated, 2
carried NOTEs; flagged that the untrusted-parse surface for the new
dependencies would arrive with later M5 increments and must be scanned
when that code lands (done in the current entry).*

<!-- SECURITY_META: {"date":"2026-07-15","commit":"449dcdf112e75b73fc63fecc5cccfe1dce9910fd","scope":"paths","scanned_files":["orgsmith/authoring/contexts.py","orgsmith/authoring/ingest.py","orgsmith/docplan/planner.py","orgsmith/evals/emit.py","orgsmith/paths.py","orgsmith/render/__init__.py","orgsmith/render/docx.py","orgsmith/render/eml.py","orgsmith/render/legacy.py","orgsmith/render/pptx.py","orgsmith/render/provenance.py","orgsmith/render/scan.py","orgsmith/schemas.py","orgsmith/validate/rules.py","recipes/cindergrove-advisors/ORG-CHARTER.md","recipes/gladepoint-strategies/ORG-CHARTER.md","tests/conftest.py","tests/test_unit_eml.py","tests/test_unit_evals_formats.py","tests/test_unit_legacy.py","tests/test_unit_pptx.py","tests/test_unit_scan_render.py","tests/test_unit_scan_validate.py","tests/test_unit_scanplan.py"],"block":0,"warn":0,"note":3} -->
