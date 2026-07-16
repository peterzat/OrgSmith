# CODEREVIEW

## Review — 2026-07-16 (commit: 50be889)

**Summary:** Light review of the README opening rewrite, scope
origin/main..HEAD: `README.md` (+12/-7), the airlock sentence and the Claude
Code skills paragraph. Docs-only, so light tier by the skill's rule. That
classification proved too generous this turn: a docs-only diff broke a test,
so the suite was run anyway. `bin/test` green after the fix (12 / 272 / 22 =
306).

**External reviewers:** Skipped (light review).

### Findings

No open findings. Two defects were caught in this turn's own draft and fixed
before push; both are recorded under Fixes Applied, and one of them was caught
by the push gate rather than by this review.

Verified against artifacts: the authoring floor is assigned exactly once
(`orgsmith/effort.py:30`) and referenced from four call sites; `doctor` reads
it via `effort_report()` and warns rather than fails (`doctor.py:74,83-84`),
so "warns" is the right verb and "prints your session's effort against the
authoring floor" matches what the code does; `docs/MODEL-AB.md` opens by
calling the strongest-model advice "folklore... never measured. This is the
measurement", so "measured rather than folklore" is that document's own
framing. All README links resolve. No secret-shaped strings.

Not claimed, deliberately: which model authored the committed fleet. All seven
fixtures predate M7's generator field and record no provenance, so the honest
answer is "unrecorded" and the README says nothing about it.

[NOTE] tests/test_short.py:238 — carried, unchanged, outside this diff's
scope: `test_no_validator_rule_references_the_generator` asserts on free text
under `orgsmith/validate/`; brittle against innocuous future prose.

[NOTE] orgsmith/render/__init__.py:28-48 — carried, unchanged, outside this
diff's scope: `people_index`'s docstring claims an EML-01 contract narrower
than stated. M8 makes titles date-dependent, which is when it starts to
matter.

[NOTE] orgsmith/render/pdf.py:37,64 — carried, unchanged, outside this diff's
scope: letterhead lines unescaped, recipe-author controlled, no concrete
vector.

### Fixes Applied

- [BLOCK-class, caught by the push gate] README.md — the draft wrote the
  authoring floor's value into prose. `test_short.py:198-221` failed the push:
  the floor must be assigned once in `orgsmith/effort.py` and never restated,
  and the test checks every SKILL.md and the README for a hardcoded value. Its
  comment is the rationale: a doc saying "use <value> effort" is "a second
  source of truth that no test could keep honest, and it is exactly the
  folklore this replaces." Rewritten to point at `doctor` and name no value,
  matching the phrasing the README already used further down. This is M7
  criterion 5 defending itself, and it is the one finding this turn that a
  light review would never have caught, because light tier skips the suite.

- [factual overstatement, caught pre-commit] README.md — the first draft of
  the airlock sentence read "a frontier LLM that never sees the facts it is
  writing about." The schema refutes it: `DocBrief` (schemas.py:534) carries
  the document's own `date`, `authors`/`participants` are `PersonBrief`
  (schemas.py:519) carrying real `name` and `title`, and `mentions` carries
  verbatim surface strings. Only `FactBrief` (schemas.py:527) withholds, and
  its own comment says "The rendered value is deliberately withheld." The
  model sees plenty of facts; what it never sees is the values behind the
  placeholders. Rewritten to claim exactly that. The phrasing this replaced
  ("never sees a number") was awkward but nearer the truth, so the rewrite had
  to fix the prose without losing the precision.

### Accepted Risks

None.

---
*Prior review (2026-07-16, commit 7820fcf): light review of the backlog update
closing the M8 spec turn; 0 BLOCK / 0 WARN / 3 NOTEs, all carried, with the
45-day thread cadence and the k>0 test coverage verified at HEAD.*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"50be889","reviewed_up_to":"50be88922e4ec93d916f24fc3a7a97577550a4f3","base":"origin/main","tier":"light","block":0,"warn":0,"note":3} -->
