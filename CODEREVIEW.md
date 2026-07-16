# CODEREVIEW

## Review — 2026-07-16 (commit: 1204cd2)

**Summary:** Light review of the M8 spec turn, scope origin/main..HEAD (1
commit, `1204cd2`). The review diff is `BACKLOG.md` only, +6 lines, one new
entry (`board-negative-control`). SPEC.md is excluded from the review diff by
the skill's own exclusion list, so the M8 spec text itself is deliberately not
in scope here. Docs-only, so light tier: no test suite run, no security chain,
no external reviewers, no fix loop.

**External reviewers:** Skipped (light review).

### Findings

Every factual claim in the new entry was verified against artifacts rather than
memory, following the lesson from the prior docs review (which caught a quote
attributed to the wrong source). All checks pass: `docs/REVIEW-CALIBRATION.md`
resolves; the README's "What this does not prove" section does say the board has
no negative control (README.md:317-318, verbatim); the claimed count of 11
majors against fernhollow is exact (counted from
`companies/fernhollow-partners-metadata/review/findings/`); the Origin quote
matches the M7 proposal verbatim (`af1b4ab:SPEC.md:271`); the entry carries all
three required fields (Why deferred / Revisit criteria / Origin); no
secret-shaped strings in the added lines.

[NOTE] BACKLOG.md:15 — the citation supporting the entry's own
deferral rationale is correct but incomplete for the conclusion it draws.
  Evidence: the entry says `rf:finance-1`'s claim that "every expense line is a
  fixed share of revenue is confirmed in 30 seconds by reading the hardcoded
  `_EXPENSE_CATEGORIES` split in `fabric/finance.py:12-18`". Lines 12-18 fix
  each category's share of `expense_total`, not of revenue. What makes it a
  fixed share of *revenue* is `fabric/finance.py:48`
  (`expense_total = int(round(year_revenue * charter.finance.expense_ratio))`).
  A reader following only the cited range sees weights summing to 1.00 of an
  unnamed total. Both verified by reading at HEAD.
  Severity: NOTE, not WARN. The file:line is accurate, the conclusion is true,
  and this is a backlog rationale rather than a spec or a contract. Reported
  because the sentence's whole point is that the claim is cheap to re-verify,
  and the proof chain it hands the reader is one line short.
  Suggested fix: cite `fabric/finance.py:12-18,48`.

[NOTE] tests/test_short.py:238 — carried from the prior review, unchanged and
outside this diff's scope: `test_no_validator_rule_references_the_generator`
asserts the substring `"generator"` is absent from every file under
`orgsmith/validate/`; the intent is right but the mechanism is brittle against
innocuous future prose.

[NOTE] orgsmith/render/__init__.py:28-48 — carried from the prior review,
unchanged and outside this diff's scope: `people_index`'s docstring claims an
EML-01 contract narrower than stated. No drift today. Note that M8's spec makes
titles date-dependent, which is the condition under which this docstring's claim
would start to matter; recorded in the M8 spec's Context for that reason.

[NOTE] orgsmith/render/pdf.py:37,64 — carried from the prior review, unchanged
and outside this diff's scope: letterhead lines rendered unescaped,
recipe-author controlled, no concrete vector.

Not reported: the entry's length against the BACKLOG format's "entries stay
terse" guidance. The neighbouring `pdf-newline-flattening` entry has the same
shape, so this is a house-consistent choice rather than a defect.

### Fixes Applied

None. The single new finding is a NOTE, and NOTEs are not auto-fixed.

### Accepted Risks

None.

---
*Prior review (2026-07-16, commit 04a3423): refresh of the complete M7 turn;
0 BLOCK / 3 WARN / 3 NOTEs, all three WARNs fixed in one codefix cycle and each
independently re-verified by probe (report sanitization, findings-file swallow,
the last raw ingest printer).*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"1204cd2","reviewed_up_to":"1204cd2ceeeac6bda061d954a99caaa2ac317a9c","base":"origin/main","tier":"light","block":0,"warn":0,"note":4} -->
