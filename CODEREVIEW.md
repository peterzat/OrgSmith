# CODEREVIEW

## Review — 2026-07-16 (commit: 37e061b)

**Summary:** Refresh review of the complete M7 turn, scope origin/main..HEAD
(8 commits). Focus set equals the full set: all 41 changed files are new since
origin/main. Code surface: the new `orgsmith/review/` package (sample, corpus
metrics, report, findings ingest), `orgsmith/effort.py` and the authoring
floor, generator provenance across two deliverable schemas and `state.json`,
two new CLI verbs, four skills, three docs, and the fernhollow board findings
as committed evidence. Tests green at HEAD (short 12 / unit 268 / org 22).

**External reviewers:** Configured and on PATH, but the invocation was BLOCKED
by the sandbox's data-exfiltration classifier (piping the repo diff to an
external service). Not run; not silently skipped. To enable, add a Bash
permission rule for `review-external.sh`.

**Docs addendum (light review, same day):** a README rewrite for a
researcher audience landed after the entry below. Docs-only, so light tier:
no test run, no security chain, no fix loop. Checks performed — all three
internal links resolve; no secrets (the `token` hits are context-window
prose); factual accuracy verified against the artifacts rather than memory.
That last check caught one real defect before it shipped: a quote attributed
to the board's reading of `fernhollow-partners` ("two engagements, thirteen
months, zero slipped dates") actually came from the model A/B's haiku arm —
fernhollow has four engagements. Replaced with quotes grep-verified verbatim
against `companies/fernhollow-partners-metadata/review/findings/`. The
"306 tests" and fleet-scale figures were re-measured, and the `score`
invocation was executed as written.

### Findings

[WARN] orgsmith/review/report.py:49,122 — untrusted strings reach
GENERATION-REPORT.md unsanitized. The sanitizer built this turn protects the
REJECTION printer but not the PERSISTED path, which is backwards: the stored
artifact is the one a human later reads.
  Evidence: two paths, both probe-verified at HEAD.
  (a) `_provenance_lines` (report.py:49) renders `f"| {wo_id} | {gen.model} |
  {gen.effort} |"`. `Generator.model`/`effort` are unconstrained `str`
  (schemas.py:574-575) copied verbatim from a model pass's deliverable
  (authoring/ingest.py:223-224, foundation/ingest.py:60-61) — no escape, no
  control-strip. The security pass's probe wrote a forged provenance row AND a
  forged `## Review board` section reading "No board findings ingested. Corpus
  reviewed clean." into the artifact whose entire purpose is recording what the
  instrument found. `run_report` exited 0.
  (b) `_findings_lines` (report.py:122) escapes `|` and `\n` in `f.summary`
  but not control characters. Probe: a finding with summary
  `"benign\x1b[2J\x1b[31mINJECTED"` ingested rc=0 and the raw ESC landed in
  GENERATION-REPORT.md verbatim.
  Severity note: nothing gates on the report and no rule reads the generator
  (test_unit_review.py:247 pins that), so the security pass rates the
  provenance path WARN on the grounds that it persists in a committable
  artifact rather than scrolling past in a terminal. Carried at WARN here for
  the same reason the prior turn carried its analogue: criterion 6 of this
  turn's spec made sanitizing untrusted board output a deliverable, the gap is
  an oversight rather than a judgment call, `_findings_lines` 70 lines away
  already escapes for exactly this reason, and the fix is mechanical.
  Suggested fix: `strip_control(..., keep="")` plus the existing pipe-escape on
  every untrusted field rendered into the report — both generator fields and
  the finding summary.

[WARN] orgsmith/review/ingest.py:35,53 — `load_findings` and
`_other_dimension_ids` silently swallow `(OSError, ValidationError)` and
`continue`, so an unreadable findings file vanishes from the report with no
signal.
  Evidence: probe at HEAD — corrupting `review/findings/org_realism.json` to
  invalid JSON made `load_findings` return only the surviving dimension and
  `render_report` print "1 findings from the review board." The user is told a
  number that is silently wrong about the board they just paid for. The same
  swallow in `_other_dimension_ids` (line 53) means a corrupt file also
  silently disables cross-dimension duplicate-id detection, which is one of
  criterion 6's required rejections.
  This also cuts against the house grain: the project's stated principle is
  "grandfather by charter, not by absence" — a missing or unreadable artifact
  is supposed to be evidence, not a skip.
  Suggested fix: let the error surface, or at minimum print a visible warning
  naming the unreadable file so the report never quietly under-reports.

[WARN] orgsmith/foundation/ingest.py:52 — the third ingest printer echoes
deliverable-controlled `person_id` raw; it is the last unsanitized one of the
three.
  Evidence: `print(f"  - {p}")` where `p` embeds `person_id` from the
  deliverable. The security pass's probe drove `p:x\x1b[2J\x1b[31mPWNED` to
  stdout with full raw ESC — strictly worse than the authoring twin the prior
  turn remediated, where only newline injection survived.
  `authoring/ingest.py:220` and `review/ingest.py:105` both pass
  `strip_control(p, keep="")`; this one does not.
  Why it survived: `orgsmith/foundation/ingest.py` appears in NO prior
  `scanned_files` list, so the prior entry declared this vector class closed on
  a path scope that excluded the file. M7 touching it is what surfaced it.
  Severity note: the security pass rates it NOTE (display-only, exit codes
  unchanged). Carried at WARN on code-review grounds, following the precedent
  this repo's prior review set explicitly: the codebase now claims this class
  is closed while 3 of 4 printers are wrapped and 1 is raw, and shipping that
  is a knowingly half-done sanitizer. Mechanical fix.
  Suggested fix: `print(f"  - {strip_control(p, keep='')}")`, matching the two
  siblings, plus a probe test alongside the existing three.

[NOTE] tests/test_short.py:238 — `test_no_validator_rule_references_the_generator`
asserts the substring `"generator"` is absent from every file under
`orgsmith/validate/`. The intent is right (criterion 4 forbids any rule reading
provenance) but the mechanism is brittle: "the generator" is this project's own
word for the model throughout its prose (README, CLAUDE.md), so an innocuous
future comment in `rules.py` would fail the test with a message about faking
guarantees. Consider asserting on the import/attribute surface
(`state.generators`, `from ..schemas import Generator`) rather than free text.

[NOTE] orgsmith/render/__init__.py:28-48 — carried from the prior review,
unchanged in this range: `people_index`'s docstring claims an EML-01 contract
that is now narrower than stated (`run_render` passes `at=entry.date`, EML-01
does not). No drift today; any title- or org-derived eml header would make
renderer and checker drift silently.

[NOTE] orgsmith/render/pdf.py:37,64 — carried from the prior review, unchanged
in this range: letterhead lines rendered unescaped, recipe-author controlled,
no concrete vector.

Security (paths scan of the 22 changed M7 code/test/fixture files, recorded in
SECURITY.md at 37e061b): 0 BLOCK / 1 WARN / 2 NOTEs. The WARN is folded into
the first finding above and the first NOTE into the third. Review-findings
ingest verified the strongest of the three ingest paths (the `dimension`
Literal is what makes `findings_path` traversal-proof — load-bearing, not
incidental). No network, subprocess, eval/exec/pickle, or `yaml.load` sink in
any scoped file; secrets and git history clean; fixture data synthetic, not
PII; dependencies unchanged and pinned. Prompt injection into the board was
considered and deliberately not reported: the authoring pass has no external
input to be injected from and board output gates nothing.

### Fixes Applied

All three WARNs fixed in one codefix cycle; tests 12/268/22 -> 12/**272**/22
(four new probes), no regressions, and every committed GENERATION-REPORT.md
re-emits byte-identically so the derived-artifact contract holds.

Each fix was independently re-verified by probe against the source, not
accepted on the fixer's report:

- [WARN] orgsmith/review/report.py:35-44,62,135 — added a `_cell()` helper and
  applied it to `gen.model`, `gen.effort` and `f.summary`. Re-probe: the ESC
  no longer reaches GENERATION-REPORT.md (content preserved), and a `model`
  of `"m |\n| wo:FAKE | forged | xhigh"` no longer forges a provenance row.
  Deviation from the suggested fix, accepted: the fixer used
  `strip_control(text, keep="\n").replace("\n", " ").replace("|", "\\|")`
  rather than literal `keep=""`. Same security property (no control character
  survives; neither newline nor pipe can break a row) while preserving the
  newline→space rendering benign summaries already had — `keep=""` would have
  turned a benign newline into U+FFFD and changed the derived bytes.
- [WARN] orgsmith/review/ingest.py:27-38,49-51,68-70 — added `_warn_unreadable()`
  at both swallow sites. Re-probe: a corrupted `org_realism.json` now prints
  `review: WARNING: org_realism.json did not load (ValidationError); its
  findings are absent from the report and cannot be checked for duplicate ids.`
  instead of vanishing.
- [WARN] orgsmith/foundation/ingest.py:56 — wrapped in `strip_control(p, keep='')`,
  matching its two siblings. Re-probe: `p:x\x1b[2J\x1b[31mPWNED` no longer
  drives the terminal; exit code unchanged (1), content preserved.
  `tests/test_unit_airlock.py:91` now probes this printer alongside the other
  three, closing the gap the prior `scanned_files` scope left open.

Two scoping calls the fixer made and this pass confirmed by reading:
`wo_id` stays unsanitized because `match_outstanding` `SystemExit`s unless it
equals an OrgSmith-emitted id, so it is not untrusted; and finding
`id`/`dimension`/`severity`/`docs` stay unsanitized because they are
pattern-constrained, Literals, and manifest-validated respectively. `summary`
is the only unconstrained `str` on `ReviewFinding`.

### Accepted Risks

None.

---
*Prior review (2026-07-15, commit 5a59288): refresh of the complete M6 turn;
0 BLOCK / 2 WARN / 2 NOTEs, both WARNs fixed (incomplete printer sanitization,
duplicate YAML key in the knobbed test recipe) and re-verified by probe.*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"04a3423","reviewed_up_to":"04a3423ffb6bb6f67153bd8a9a9a607a98f7efbb","base":"origin/main","tier":"refresh","block":0,"warn":3,"note":3} -->
