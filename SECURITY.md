# Security

## Security Review — 2026-07-16 (scope: paths)

**Summary:** M7-close scan of the quality instrument (range 5a59288..37e061b):
the new `review/` package (sample, corpus, metrics, report, findings ingest),
the `orgsmith/review-finding@1` and `orgsmith/review-findings@1` contracts, the
self-reported generator record and its two ingest recording points, the effort
floor module and `doctor`'s reading of it, and the three committed fernhollow
review artifacts. One WARN: the provenance table interpolates the model's own
self-reported strings into GENERATION-REPORT.md with no escaping, verified by
probe to forge a "Corpus reviewed clean" section in the artifact whose purpose
is recording what the instrument found. One new NOTE: `foundation --ingest` is a
third ingest printer that echoes deliverable-controlled strings raw, the vector
the prior entry declared closed on a scope that never included the file. The pdf
letterhead NOTE carries forward unchanged. No BLOCKs.

### Findings

**[WARN] orgsmith/review/report.py:47-49 — the self-reported generator record is
interpolated into GENERATION-REPORT.md unescaped, so a model pass can forge
report sections including a quality verdict**

  Attack vector: `Generator.model` and `Generator.effort` (schemas.py:574-575)
  are `str` with `min_length=1` and no other constraint. They arrive in a model
  pass's deliverable, which this project's own doctrine treats as untrusted
  (review/ingest.py:3-5, "the board is a model pass, so its deliverable is
  untrusted input"; the CLAUDE.md airlock rule). `author --ingest` copies the
  field into state verbatim (authoring/ingest.py:223-224), as does
  `foundation --ingest` (foundation/ingest.py:60-61); `save_state` persists it;
  `_provenance_lines` then renders it into a markdown table with no escaping.
  The adversary is an authoring pass that self-reports something other than what
  the operator assumes (a misbehaving, misconfigured, or injected model), not a
  remote attacker: the field is already documented as self-reported and
  unverifiable, but the documented risk is a *wrong value in its own cell*, not
  arbitrary control of the surrounding document.
  Evidence: probe at HEAD (built dev-mini through authoring, first batch
  reporting a hostile generator). `report.py:49` is
  `lines.append(f"| {wo_id} | {gen.model} | {gen.effort} |")`. A `model` value
  carrying `|`, newlines and a `<!--` opener produced, in the written
  GENERATION-REPORT.md: a forged provenance row for `wo:author:9999`, a work
  order that does not exist; a forged `## Review board` section reading "No board
  findings ingested. Corpus reviewed clean."; and an HTML comment swallowing the
  rest of the real line. `run_report` exited 0. The forged section renders above
  the genuine one, which still reports the truth further down the page.
  The same file already defends the adjacent table: `_findings_lines`
  (report.py:122) runs `f.summary.replace("|", "\\|").replace("\n", " ")` for
  exactly this reason, and every other field it prints is schema-constrained
  (`ReviewFinding.id` pattern at schemas.py:744, dimension and severity Literals
  at schemas.py:727-739, `docs` checked against the manifest at
  review/ingest.py:92-96). The provenance table is the one path with neither
  constraint nor escape.
  Impact is bounded and does not reach a gate: the report gates nothing by
  design, no validator rule may read the record (proved by
  test_unit_review.py:247), exit codes are unchanged, and no ledger, manifest or
  prose is touched. It is display deception in a persisted, committable
  artifact rather than in a terminal line that scrolls away, which is why it is
  rated above the printer class.
  Remediation: escape the cells in `_provenance_lines`. Prefer one shared helper
  used by both tables that escapes `|` and neutralizes CR and LF, and apply it in
  `_findings_lines` too: that path escapes `|` and `\n` but leaves a bare `\r`,
  which CommonMark also treats as a line ending (probed: CR survives, though with
  pipes escaped no forged row is reachable through `summary` today). A
  `max_length` on `Generator.model`/`effort` would additionally bound the field
  at the airlock, where the untrusted value first arrives.

**[NOTE] orgsmith/foundation/ingest.py:52 — the enrichment rejection printer
echoes deliverable-controlled strings raw; the third ingest printer, outside
every prior scan's scope**

  Attack vector: `PersonaEnrichment.person_id` (schemas.py:579) is an
  unconstrained `str`, so an id survives schema validation and lands in the
  "unknown person ids" problem string (foundation/ingest.py:44-45), which line 52
  prints with no `strip_control`. This is the same class the prior entry
  remediated at `authoring/ingest.py:218` and `evals/score.py:274,317,341`, and
  the same one `review/ingest.py:105` was built with from the start. It was
  missed because it was never in scope: `orgsmith/foundation/ingest.py` appears
  in no prior `scanned_files` list, so the class was declared closed on a path
  scope that excluded this file. M7 touched the file (three lines, the generator
  recording at 60-61), which is what brought it into this scan.
  Evidence: probe at HEAD. An enrichment deliverable carrying
  `person_id: "p:x\x1b[2J\x1b[31mPWNED"` printed
  `  - unknown person ids: p:x^[[2J^[[31mPWNED` with the ESC bytes raw on stdout
  (confirmed through `cat -v`), exit code 1. Unlike the remediated authoring twin,
  where only newline injection survived, this path passes full escape sequences,
  so earlier terminal output can be erased or rewritten. Impact is display-only
  and matches the prior entry's rating of the class: the exit code stays 1, no
  foundation is written, and skills key off exit codes.
  No test covers it. The suite's three escape probes reach `ingest_author`
  (test_unit_airlock.py:147-150), `review --ingest`
  (test_unit_review.py:356-365) and `score` (test_unit_evals.py); none reaches
  `ingest_enrichment`.
  Remediation: `print(f"  - {strip_control(p, keep='')}")`, matching
  authoring/ingest.py:220 and review/ingest.py:105. Line 31 needs no change: it
  prints `str(err)` from pydantic, which escapes control characters inside its
  value reprs (re-verified at HEAD).

**[NOTE] orgsmith/render/pdf.py:37,64 — letterhead lines rendered unescaped
(carried from prior reviews; no current attack vector; file unchanged in this
range, verified by empty diff; outside this run's path scope)**

  Attack vector: none concrete. The letterhead is `charter.name` and
  `www.{charter.domain}`, interpolated raw into the HTML template under
  `Environment(autoescape=False)` (pdf.py:73). Only the recipe author controls
  the charter, and `no_remote_fetcher` blocks all non-`data:` URLs, so injected
  markup cannot egress or read files.
  Remediation: `html.escape()` the letterhead lines (and CSS-escape the
  `@top-left` string) when building the template context. One-line change, no
  urgency.

### Reviewed Surface

- Review findings ingest (`orgsmith/review/ingest.py`): the strongest of the
  three ingest paths. `dimension` is a Literal (schemas.py:727-737), so
  `findings_path`'s `f"{dimension}.json"` (ingest.py:24) cannot traverse: an
  unknown dimension is rejected by the schema before it can name a file.
  Verified that this is load-bearing and not incidental. Finding ids are
  pattern-constrained, doc ids are checked against the manifest, cross-dimension
  id collisions are caught (ingest.py:87-91), and both printers are wrapped with
  the correct `keep`. All-or-nothing holds: the write at ingest.py:108-110 is
  unreachable while `problems` is non-empty.
- Sample and metrics: pure functions of committed files. `review/sample.py`
  draws only from the new `review.sample` stream (sample.py:38,71), so no
  existing stream moves. `corpus.py:44`'s `docir_path` joins a manifest doc_id
  (pattern `^d:\d{4}$`, schemas.py:437), not a deliverable-controlled string.
  `briefed_targets` (corpus.py:98-117) parses retained work orders defensively:
  OSError and JSONDecodeError become skips, and non-int targets are ignored by
  the isinstance guards, so a corrupt work order yields a smaller target map
  rather than a traceback.
- Provenance is a record, not an oracle, and the code holds that line.
  `state.generators` has exactly one reader in the package (report.py:36,47,48,
  confirmed by grep), and test_unit_review.py:247 asserts no validator module
  mentions the generator or reads GENERATION-REPORT.md. This is what bounds the
  WARN above to display impact.
- Effort floor (`orgsmith/effort.py`, `orgsmith/doctor.py`): `session_effort`
  reads `CLAUDE_EFFORT` from the environment and `doctor.py:75` prints it back
  through `effort_report`. An unknown value is echoed unsanitized, but the
  environment of a locally run CLI is the operator's own trust domain, so this
  is self-injection, not a finding. `doctor` correctly declines to record effort
  into `probes` (doctor.py:71-73), so re-probing a frozen fixture cannot rewrite
  its state.json.
- Airlock and offline posture intact: no network, subprocess, `eval`, `exec`,
  `pickle`, or `yaml.load` sink in any of the 22 scoped files (the one grep hit,
  `evals_dir` matching `eval(` at score.py:89, is a false positive).
  `test_short.py:178-190` pins the quality verbs to offline imports and
  `test_short.py:224-234` pins the suite keyless.
- The prior entry's remediation holds at HEAD, re-verified rather than assumed:
  score.py:276,320,348 all pass `keep=""`, and the graph class printer is
  wrapped.
- Secrets and PII: pattern grep over all 22 scoped files plus
  `git log -p --follow` over the new modules (effort.py, review/report.py,
  review/ingest.py, state.py): clean. The only hits are the word "tokens",
  `credential` as fixture prose, and `test_no_tier_reads_a_model_api_key`, which
  asserts the absence of provider keys. The three committed fernhollow review
  artifacts contain synthetic org content only (Faker-derived rosters, fictional
  client names); the findings' `generator` records name a model and effort, not a
  person. No scoped file handles credentials. Not PII.
- Dependencies: requirements.txt, requirements-dev.txt, pyproject.toml and
  .github/ are unchanged in this range (verified by empty diff); every
  requirement remains pinned. Offline review, no live vulnerability database
  query.
- Prompt injection into the board was considered and is not reported as a
  finding. Reviewers read authored prose, which is model-written, so a document
  could in principle address its reader. The authoring pass has no external input
  to be injected from (work orders are built from repo-controlled ledgers), and
  the board's output gates nothing: findings are a record a human reads, no rule
  may reference them, and `bin/test` never invokes the board. No concrete vector,
  so no finding.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-15, scope paths, commit 5a59288): M6-close scan of the
pre-fleet hardening turn (name screen and its enforcement points, affiliation
planting, era-resolved employer surfaces, validator read hardening); no BLOCKs or
WARNs, two NOTEs, one of which (newline line-injection surviving the control-character
fix) was remediated inside that same review cycle at the ingest and score
printers. Its path scope did not include `orgsmith/foundation/ingest.py`, which
is why the third printer of that class surfaces only now.*

<!-- SECURITY_META: {"date":"2026-07-16","commit":"37e061bf3c2005604acac6c70fdf2d13c4da3cb4","scope":"paths","scanned_files":["companies/fernhollow-partners-metadata/review/findings/cross_document_voice.json","companies/fernhollow-partners-metadata/review/metrics.json","companies/fernhollow-partners-metadata/review/sample.json","orgsmith/authoring/ingest.py","orgsmith/cli.py","orgsmith/doctor.py","orgsmith/effort.py","orgsmith/evals/score.py","orgsmith/foundation/ingest.py","orgsmith/paths.py","orgsmith/review/__init__.py","orgsmith/review/corpus.py","orgsmith/review/ingest.py","orgsmith/review/metrics.py","orgsmith/review/report.py","orgsmith/review/sample.py","orgsmith/schemas.py","orgsmith/state.py","tests/conftest.py","tests/test_short.py","tests/test_unit_doctor.py","tests/test_unit_review.py"],"block":0,"warn":1,"note":2} -->
