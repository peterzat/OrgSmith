# CODEREVIEW

## Review — 2026-07-16 (commit: c013c06)

**Summary:** Full review of the unpushed M8+M9 arc (scope origin/main..HEAD),
focused at full depth on the M9 document-supply changes committed this turn:
the genre registry (`docplan/registry.py`), the registry-driven planner
rewrite (`docplan/planner.py`), per-genre lengths sourced from the registry
(`authoring/contexts.py`), the `target_docs`/`format_mix` advisory change
(`schemas.py`), the two PDF letter fixes (`render/pdf.py`), and the email
cadence. The M8 code in scope (behavioral finance, engagements, scaffold
churn, era names) shipped as v1.7.0 and was checked for interactions with the
M9 planner, which the org tier exercises end to end. `bin/test` green: 386
passing (12 short / 334 unit / 40 org). The 72 changed `companies/` files are
machine-generated fixtures (the dev-mini regeneration) validated by the org
tier, not reviewed by hand.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN findings. The M9 delta is clean on every dimension checked:

- **Correctness / hard cases preserved.** The planner walks the registry;
  the signature-page fee still lands only on the letter (`hosts_signature`)
  and the filename-only minutes date only on the first minutes instance
  (`hosts_filename`, dated by the shared `minutes_date()`), so
  `_check_hard_cases` still finds each non-body fact in exactly one doc.
  Verified by the passing hard-case/loc unit tests and the clean org tier.
- **Paths and injection.** Every emit path is a code-constant registry
  template filled with recipe/ledger values, then run through `_add` →
  `check_relpath`; the model controls no path. `render/pdf.py`'s new
  `_para_html` HTML-escapes before inserting `<br>`, and the leading-heading
  suppression only reads the recipe-controlled firm name, so neither adds an
  injection vector (confirmed by the `/security` pass).
- **Determinism / regression.** New randomness (email cadence) draws from a
  dedicated `seeds.py` stream; `dev-mini` re-pins byte-identically and the
  six frozen fixtures derive without crashing and validate clean
  (`test_org_regen.py`, `test_org_fleet.py`). `contexts._TARGET_WORDS` now
  derives from the registry with no circular import (`review/corpus.py`
  imports it unchanged).

Three NOTEs carried from prior reviews, all pre-existing and outside the M9
intent:

[NOTE] orgsmith/render/pdf.py:38,65-66 — letterhead context (`letterhead0`,
`letterhead_rest`) interpolated unescaped under `autoescape=False`.
Recipe-author-controlled and `no_remote_fetcher` blocks egress/file-read, so
no concrete vector. M9 reworked this file but left the letterhead
interpolation untouched. One-line `html.escape()` fixes it; no urgency.

[NOTE] orgsmith/render/__init__.py:28-48 — `people_index`'s docstring claims
an EML-01 contract narrower than what holds now that titles are date-scoped.
Documentation drift, not a defect.

[NOTE] tests/test_short.py:238 — `test_no_validator_rule_references_the_generator`
asserts on free text under `orgsmith/validate/`; brittle against innocuous
future prose.

### Fixes Applied

None. No BLOCK or WARN findings to fix.

### Accepted Risks

None.

---
*Prior review (2026-07-16, commit 50be889): light review of the README
opening rewrite; 0 BLOCK / 0 WARN / 3 NOTE, two draft defects fixed before
push (one caught by the push gate).*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"c013c06","reviewed_up_to":"c013c064","base":"origin/main","tier":"full","block":0,"warn":0,"note":3} -->
