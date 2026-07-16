# CODEREVIEW

## Review — 2026-07-16 (commit: 7820fcf)

**Summary:** Light review of the backlog update that closes the M8 spec turn,
scope origin/main..HEAD: `BACKLOG.md` (+7/-1), two entries touched
(`email-thread-spacing` added, `pdf-newline-flattening`'s revisit criteria
extended). Docs-only, so light tier: no test suite run, no security chain, no
external reviewers, no fix loop. SPEC.md remains excluded from the review diff
by the skill's own exclusion list. `bin/test` green (12 short / 272 unit / 22
org = 306).

**External reviewers:** Skipped (light review).

### Findings

No open findings. Every claim in the diff was verified against artifacts
before the entry was written, not after:

- `docplan/planner.py:296` reads
  `ed = self._clamp_range(eng.start + timedelta(days=30 + 45 * k))`, which is
  the 45-day thread cadence the entry describes.
- `tests/test_unit_eml.py:26,55` do plan 4 mails over 3 engagements and assert
  the round-robin lands a second mail on one engagement, so the k>0 path is
  covered for correctness. The entry's distinction holds: the wrap is tested,
  the plausibility of the spacing is not.
- All 4 `.eml` files in the committed fleet are "Email 1" (k=0), confirmed
  from the manifests, so no fixture exercises k>0.
- `docs/SCALE.md:57` does say "room for one deliberate oddity per org".
- README:162 does call email the "single largest" fidelity gap, so the entry
  does not overstate its own premise.
- The `pdf-newline-flattening` edit was tightened after checking: the eighth
  fixture's recipe is unwritten, so asserting it renders PDFs would have been
  an assumption. Verified instead that all seven committed fixtures carry 2-4
  PDFs and every one has engagement letters rendered exclusively as PDF, and
  the entry now states that evidence rather than the inference.

All nine file references in BACKLOG.md resolve. No secret-shaped strings in
the added lines. All four entries carry the three required fields.

Incidental confirmation of `charter-redump-drift` while checking format
mixes: reading `format_mix['eml']` off the committed charters raises
`KeyError` for bramblewood-legal, quillbrook-appraisal, and
torchlake-engineering, because those three predate the key. That is the same
drift the entry documents, observed from a different direction.

[NOTE] tests/test_short.py:238 — carried from the prior review, unchanged and
outside this diff's scope: `test_no_validator_rule_references_the_generator`
asserts the substring `"generator"` is absent from every file under
`orgsmith/validate/`; the intent is right but the mechanism is brittle against
innocuous future prose.

[NOTE] orgsmith/render/__init__.py:28-48 — carried from the prior review,
unchanged and outside this diff's scope: `people_index`'s docstring claims an
EML-01 contract narrower than stated. No drift today. M8 makes titles
date-dependent, which is the condition under which the claim starts to matter.

[NOTE] orgsmith/render/pdf.py:37,64 — carried from the prior review, unchanged
and outside this diff's scope: letterhead lines rendered unescaped,
recipe-author controlled, no concrete vector.

### Fixes Applied

None. No BLOCK or WARN findings; the three NOTEs are carried and are not
auto-fixed.

### Accepted Risks

None.

---
*Prior review (2026-07-16, commit 045151b): light review of the README and
BACKLOG docs turn; 0 BLOCK / 0 WARN / 3 NOTEs, with two defects caught before
push (an email-capability overclaim refuted by reading the planner, and six
pre-existing wrong per-org date ranges in the README).*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"7820fcf","reviewed_up_to":"7820fcfa0ccca69af9597eb168df286e9c3ce5e4","base":"origin/main","tier":"light","block":0,"warn":0,"note":3} -->
