# Security

## Security Review — 2026-08-02 (scope: paths)

**Summary:** Reviewed the fourteen in-airlock files carrying the M17b
batch-boundary turn (~1,600 added lines since the last baseline `6bd7d77`):
engagement scope quantities as ledger facts, per-document section skeletons,
the client-facing-report participant override, the structural-similarity
axis, the SCOPE-01/OUT-01 rules, and the ingest outline gate. No secret, no
injection path, no PII, no new dependency. The two new rules do not extend
the standing `validate`-printer NOTE, because both repr-escape every
untrusted value they quote.

**The carried NOTE is CLOSED as of this entry** (2026-08-02, at the user's
instruction to clear the notes before pushing). `run_validate`'s human
printer now routes every field of every finding and skip through
`strip_control(..., keep="")`, so this file records zero open findings.

### Findings

```
[NOTE, FIXED] orgsmith/validate/rules.py:332,579,616,707,812-813,956,1168,1489 —
validate findings interpolate unconstrained ledger strings and third-party
parser exception text, and the plain-text printer emits them raw. Carried
forward from 2026-08-02 (`6bd7d77`), unchanged; line numbers re-derived at
this commit.
  Attack vector: an operator validates an org directory obtained from
    someone else (`python -m orgsmith validate <slug>`, or `validate
    companies/<slug>`). A hostile `ledger/finance.json` (`LedgerCheck.name`
    / `.detail`), `ledger/graph.json` (`GraphEdge.src` / `.dst`),
    `ledger/acl.json` (`AclGrant.person`), or `foundation.json`
    (`Person.reports_to`) embeds an ANSI escape sequence; the rule quotes it
    into a finding message and `validate/__init__.py:68` prints
    `f"{severity} {rule} [{target}] {message}"` with no neutralization. The
    escape can rewrite or hide earlier findings on the terminal, which is
    exactly the outcome `strip_control` was introduced to prevent.
  Evidence: the four models above declare bare `str` fields
    (schemas.py:520,525,608-610,674-676,682-684), so pydantic constrains
    nothing. The rule messages interpolate them without `!r` (contrast
    acl_02's `{doc!r}` at rules.py:973, which repr-escapes correctly).
    `orgsmith/validate/__init__.py` imports no sanitizer, while
    `foundation/ingest.py`, `authoring/ingest.py:424`, `evals/score.py`,
    `review/ingest.py`, `airlock.py` and `datacard.py` all route untrusted
    text through `strip_control` with the same stated rationale.
  Remediation: wrap the two plain-text prints in
    `orgsmith/validate/__init__.py` in `strip_control(..., keep="")`, one
    finding per line, matching the score-failure printer.
  FIXED 2026-08-02, exactly as remediated. Sanitized at the PRINTER rather
    than at each interpolation site, so the rules that do not yet quote with
    `!r` are covered and a rule added later cannot reintroduce it. `keep=""`
    drops newlines too, so a smuggled one cannot forge a second finding
    line. `--json` output is deliberately left raw: it is consumed by
    tooling, and `json.dumps` already escapes control characters.
    Regression-tested both ways in `tests/test_unit_validate.py`
    (`test_findings_printer_neutralizes_a_smuggled_escape`,
    `test_json_output_is_not_mangled_by_the_printer_sanitizer`); the first
    was proven to fail against the pre-fix printer.
```

The severity assessment that held it at NOTE is unchanged and is why it was
never urgent: the reachable input is an org tree the operator chose to trust
enough to validate, and the supported third-party ingress points (`score
--evals-dir`, `--answers`) were already guarded. It is fixed now because it
was cheap and it had been carried across two reviews.

### Verified this turn

- **The new validator rules do not widen the raw-string surface.** SCOPE-01
  quotes ledger values only through `!r` (rules.py:1126-1130), and its other
  interpolations are recomputed fact ids, which pass `Fact.id`'s
  `^f:[A-Za-z0-9.\-]+$` pattern at construction (schemas.py:721), and the
  charter's own stage phrases, also repr-escaped (rules.py:1143-1146). Its
  finding target is `Engagement.id`, pattern `^E-\d{4}-\d{3}$`
  (schemas.py:733). OUT-01 repr-escapes the manifest value it quotes
  (rules.py:1046,1057,1064) and otherwise interpolates `Literal`-constrained
  genre and authoring fields; its target is `entry.path`, which
  `check_relpath` re-checks at every manifest load.
- **The client-facing-report override does not widen read access.** The
  planner adds `eng.external_participants` to a status report's manifest
  participants when `doc_culture.client_facing_reports` is on
  (planner.py:253-268). `derive_acl` never reads `ManifestEntry.participants`:
  grants come from `eng.internal_participants` plus the CEO-equivalent, then
  are intersected with the currently-employed roster, which drops external
  ids outright (acl.py:110-136). Traced every other consumer of
  `entry.participants` (render/eml.py:113 is eml-only and `status_report` is
  docx; authoring/ingest.py:67-69 is onboarding-only; contexts.py:399,609-638;
  rules.py:185). No path from the knob to a grant.
- **Recipe-supplied scope strings reach no dangerous sink.** `unit`,
  `comparator` and the pipeline phrases flow to three places: a `Fact.id`
  fragment via `stage_slug`, which collapses everything outside
  `[A-Za-z0-9]` to hyphens and is then re-validated by the id pattern
  (engagements.py:110-114); a `Fact.rendered` surface, which reaches
  documents only as block text and is `html.escape`d by the PDF renderer
  (render/pdf.py:119-183) and set as run text by python-docx/pptx; and a
  brief hint plus eval question text, which are JSON-serialized. No filename,
  no path join, no shell, no SQL.
- **Model output that persists is still gated before the write.**
  `_check_outline` (authoring/ingest.py:276-325) is collected into the same
  `problems` list as every other check, and `run_ingest` returns 1 at
  ingest.py:417-425 before the DocIR write loop at 430-436. Problem strings
  are `strip_control(p, keep="")`-wrapped one per line. The outline itself is
  resolved from the MANIFEST, not from the model-visible brief
  (contexts.py:182-196), so a deliverable cannot argue its way out of the
  rule it is checked against.
- **The new report section cannot forge a table row.** `_structural_lines`
  (review/report.py:158-204) is the one place in this turn that writes into
  `GENERATION-REPORT.md` without `_cell`. Every value it interpolates is
  type-constrained: `genre` is the `Genre` `Literal` (schemas.py:849-860),
  the doc ids are `ManifestEntry.doc_id` (`^d:\d{4}$`), and the rest are
  floats. `run_report` recomputes `CorpusMetrics` from committed DocIR on
  every run and never reads `corpus_metrics.json` back (report.py:437-439,
  metrics.py:211-213), so a tampered metrics artifact has no path into the
  report. Model output elsewhere in the file still goes through `_cell`
  (report.py:39-48).
- **No new randomness, subprocess, network, or dependency.**
  `docplan.outline` and `fabric.engagements.scope` are new `seeds.rng`
  streams, seeded by sha256 rather than by `hash()`, so they are deterministic
  across processes and disturb no existing stream. `mask_surfaces` moved from
  `evals/emit.py` to `doctext.py` byte-identical, keeps its `re.escape`, and
  has no stale callers. `pyproject.toml` changed only its version string;
  `requirements.txt`, `requirements.lock`, the Dockerfile and CI are untouched
  in this range. Nothing in scope reads an environment variable.
- **No secret, in tree or history.** Pattern scan across the diff and across
  every commit in `6bd7d77..HEAD` touching these paths is clean. No email
  address, phone number, or real-person name appears in any of them;
  `tests/conftest.py` writes only under pytest fixture roots.
- **`count_noun` on a mutated ledger: filed as robustness, and FIXED.**
  `evals/emit.py` did `fact.rendered.split(" ", 1)[1]`, which raises
  `IndexError` for a hand-edited `count` fact whose rendered surface has no
  space. Unreachable from any recipe (`render_count` cannot produce one, and
  `ScopeProfile` now rejects a blank noun at parse), and the outcome was a
  traceback in a local offline CLI with no disclosure or privilege
  consequence — robustness, not security. Now uses `partition`, so
  `emit-evals` completes and SCOPE-01 reports the tamper. Covered by two
  tests in `tests/test_unit_scope_facts.py`.

### Accepted Risks

None.

---
*Prior review (2026-08-02, scope paths, commit 6bd7d77): the fifteen files of
the M17 answer-key turn, covering the new baselines, data cards, doc-text
reader, cluster/diagnostics emitters, ranked scorer, alias-agreement ingest
gates and the EVAL-01/MENT-03 rules. No secret, no injection path, no PII;
0 BLOCK / 0 WARN / 1 NOTE, that NOTE being the raw `validate` plain-text
printer carried forward above.*

<!-- SECURITY_META: {"date":"2026-08-02","commit":"e35e6eb180aff01202061e51b9cda08160ddc206","scope":"paths","scanned_files":["orgsmith/__init__.py","orgsmith/authoring/contexts.py","orgsmith/authoring/ingest.py","orgsmith/docplan/planner.py","orgsmith/docplan/registry.py","orgsmith/evals/emit.py","orgsmith/fabric/engagements.py","orgsmith/review/metrics.py","orgsmith/review/report.py","orgsmith/review/structure.py","orgsmith/schemas.py","orgsmith/validate/rules.py","pyproject.toml","tests/conftest.py"],"block":0,"warn":0,"note":0} -->
