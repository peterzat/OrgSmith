# CODEREVIEW

## Review — 2026-07-16 (commit: 045151b)

**Summary:** Light review of the docs turn that closes M8's spec work, scope
origin/main..HEAD plus working tree: `BACKLOG.md` (+8/-1) and `README.md`
(+84/-21). Docs-only, so light tier: no test suite run, no security chain, no
external reviewers, no fix loop. SPEC.md is excluded from the review diff by
the skill's own exclusion list, so the M8 spec text itself is again not in
scope. `bin/test` green at review time (12 short / 272 unit / 22 org = 306).

**External reviewers:** Skipped (light review).

### Findings

No open findings. Every factual claim added this turn was verified against
artifacts rather than memory, which is the check the prior two docs reviews
established. That check earned its keep twice more this turn, both recorded
under Fixes Applied below: it caught an overclaim about email capability
before it shipped, and it caught six wrong date ranges that predate this diff.

Verified clean: all 21 relative README links resolve; all 16 `companies/`
links point at paths actually present on `origin/main` (repo is PUBLIC, all
seven orgs pushed with both share tree and answer key, 107 share files
matching the README's own figure); the new fleet table matches ground truth
row-for-row and its document counts total 95, consistent with the fleet table
below it; no secret-shaped strings in either diff; both BACKLOG entries carry
all three required fields.

`charter-redump-drift`'s claims were each verified at HEAD before the entry
was written: `charter.py:59` writes unconditionally, `scaffold.py:327` guards,
`forge/SKILL.md:44` invokes charter unconditionally, the README quote at
README.md:235 is verbatim, and the drift measurement (5 of 7 fixtures) was
taken by re-deriving each charter from its recipe read-only. The entry's
causal claim ("the two regenerated most recently") was confirmed
topologically: dev-mini and fernhollow-partners are the 67th and 68th commits
touching a charter.json and the only two carrying `affiliations_in_docs`,
which is exactly why they are the only two that do not drift.

[NOTE] tests/test_short.py:238 — carried from the prior review, unchanged and
outside this diff's scope: `test_no_validator_rule_references_the_generator`
asserts the substring `"generator"` is absent from every file under
`orgsmith/validate/`; the intent is right but the mechanism is brittle against
innocuous future prose.

[NOTE] orgsmith/render/__init__.py:28-48 — carried from the prior review,
unchanged and outside this diff's scope: `people_index`'s docstring claims an
EML-01 contract narrower than stated. No drift today. M8 makes titles
date-dependent, which is the condition under which the claim starts to matter;
recorded in the M8 spec's Context for that reason.

[NOTE] orgsmith/render/pdf.py:37,64 — carried from the prior review, unchanged
and outside this diff's scope: letterhead lines rendered unescaped,
recipe-author controlled, no concrete vector.

### Fixes Applied

- [NOTE→fixed] BACKLOG.md:15 — the prior review's only new finding. The
  finance citation now reads `fabric/finance.py:12-18,48`; 12-18 fixes each
  category's share of `expense_total`, and 48 is what ties that total to
  revenue. Re-read at HEAD to confirm both lines say what the entry claims.

- [overclaim, caught pre-push] README.md — the reframed "not modeled today"
  section first claimed email volume was "a fixture that has not been written
  rather than a capability that is missing." Checking the planner refuted it:
  `docplan/planner.py:285` does drive email count straight from
  `format_mix.eml`, but line 296 dates the k-th message of a thread at
  `eng.start + 30 + 45*k` and clamps to the charter range, so successive
  messages sit 45 days apart and pile up at the boundary at volume. Real
  threads run hours apart. Corrected to say the knob exists but email-dominant
  realism needs more than turning it up. This mattered because the section's
  whole job is to be believed about limits.

- [pre-existing defect] README.md — six of seven per-org date ranges in "What
  is in the box today" were wrong, and would have contradicted the new
  browsable fleet table. The prose used each recipe's *allowed window* rather
  than the documents' actual dates (quillbrook advertised 2016-2020 against
  real files spanning 2019-2020, a three-year overstatement), and dev-mini's
  "2019-2022" matched neither window nor reality. All seven now match the
  manifests, verified programmatically. Only cindergrove was already correct.

### Accepted Risks

None.

---
*Prior review (2026-07-16, commit 1204cd2): light review of the M8 spec
commit, scope BACKLOG.md only; 0 BLOCK / 0 WARN / 4 NOTEs, one new (an
incomplete finance citation, fixed this turn) and three carried.*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"045151b","reviewed_up_to":"045151bfca970ed10a8cdf1e4d1921b3ba1b7b4a","base":"origin/main","tier":"light","block":0,"warn":0,"note":3} -->
