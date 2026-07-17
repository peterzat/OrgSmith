# CODEREVIEW

## Review — 2026-07-17c (commit: 1bf2c1d)

**Summary:** M12a, the capability layer plus the live pilot: `main..HEAD`, 11
commits, 36 code/test files (+2427/-330) plus the generated `calderwood-partners`
org (218 files). Reviewed against `main` (the branch has no upstream; the
marker base is the empty tree, so the push gate hashes the whole tree, but the
meaningful review surface is the branch diff). Five default-off knobs
(business-day calendar, engagement-book-is-sample, deterministic noise, nested
eval splits, voice mitigation) plus a generator-wide reporting-line fix. Tests
green: 493 across four tiers (14 short / 397 unit / 72 org / 10 flagship),
byte pin held fleet-wide, pilot validates 0 errors.

**External reviewers:** Skipped (not configured in this environment).

**Security:** Assessed inline rather than dispatched. The new surface is
deterministic generation with no network, auth, or secret handling. The one
new filesystem write (`render/__init__.py`, `shutil.copyfile` for an exact-
duplicate noise doc) copies from a manifest source path to that path plus
`" (copy)"`, both `check_relpath`-validated at docplan, both under
`share_dir` -- no traversal. The new regexes (`_REPORTS_TO`, the voice
patterns) are bounded quantifiers, no ReDoS. No finding.

### Findings

**[WARN] orgsmith/authoring/ingest.py:38 — the reporting-line lint's capture
window bleeds across commas, so valid onboarding prose can be falsely rejected
at ingest.**

  Evidence: `_REPORTS_TO` captures `([^.;:\n]{2,60})` after "reports to",
  which does not stop at a comma. Verified against the real check:
  "She reports to the analytics lead, and keeps the Managing Partner informed
  each month." is REJECTED, because the capture runs past "the analytics lead"
  (the true target) into the next clause and matches "Managing Partner" (a
  wrong internal management title). The reporting target is correct; the
  rejection is a false positive. It costs a re-author cycle at ingest, and gets
  likelier at flagship scale (~2,000 docs, more onboarding records). It did not
  fire on the pilot's 168 authored docs because the briefs told authors the
  reporting line, but a probabilistic lint should not rely on that.
  Suggested fix: add `,` to the capture's excluded-character class
  (`[^.;:,\n]{2,60}`), so the capture stops at the clause boundary. This loses
  no real detection: the genuine contradiction "reports to the <wrong title>"
  places the wrong title immediately after "to", before any comma.

### Fixes Applied

- **[WARN] orgsmith/authoring/ingest.py:38** — added `,` to the reporting-line
  capture's excluded-character class (`[^.;:\n]{2,60}` -> `[^.;:,\n]{2,60}`), so
  the capture stops at the clause boundary. Verified: the comma-bleed false
  positive no longer rejects valid onboarding prose, the genuine "reports to the
  <wrong title>" contradiction is still rejected, and correct prose still
  passes. All tiers green after the fix (483 default + 10 flagship).

### Accepted Risks

None new this review.

---
*Prior review (2026-07-17b, `59870b5`): the pre-M12 turn — 1 BLOCK / 2 WARN /
2 NOTE, all fixed; every finding died on a command rather than a reading.*

<!-- REVIEW_META: {"date":"2026-07-17","commit":"1bf2c1d","reviewed_up_to":"1bf2c1d","base":"empty-tree","tier":"full","block":0,"warn":1,"note":0} -->
