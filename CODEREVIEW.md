# CODEREVIEW

## Review — 2026-07-17 (commit: f7f945c)

**Summary:** Full-tier review of the documentation pass (`f7f945c`) plus the
three test files carried in `4c4f9b9`. Scope resolved as full rather than
light because test files changed, but the executable delta is three lines,
all of them the prior review's own recorded fix-loop output: an added
`ocr_layer_rate` default assertion, `locations <= expected` tightened to
`==`, and a docstring count. Everything else in those files is prose. The
substance of this review is therefore the docs. `bin/test` green and unmoved:
440 passing (12 short / 356 unit / 72 org). No product code has changed since
`de60065`.

**Reviewer separation:** the author wrote the docs, so the review was
delegated to a fresh-context adversary instructed to check every number
against the repo rather than read for plausibility. Its findings were then
re-verified independently before being acted on — which mattered: one was
wrong.

### Findings

**[BLOCK] docs/MODEL-AB.md:9 — "Both validated clean under all 29 rules" was
false; 20 rules ran.** *(fixed)*

  Evidence: the doc's own table 35 lines below reads "20 rules, **0 errors**"
  for both arms. `ab-probe` leaves 9 knobs off, so 9 rules skipped. The
  reviewer checked out the Round 1 commit and confirmed `a9ec852` already
  carried the same 29 rule ids, so this was an overstatement rather than an
  anachronism.
  Why it matters more than the arithmetic: the same pass had already deleted
  the identical sentence from the README (a prior review caught it there) and
  left it standing in the document the README cites as the authoritative
  write-up. Fixing a claim in the summary and not in the source is worse than
  not fixing it, because the source is what a sceptical reader opens.
  Fix: "Both validated clean, with zero errors, on every rule that ran." The
  README's `validate` example comment was corrected the same way (it implied
  all 29 run for an org where 24 do).

**[WARN] README.md — the Round 2 cost conclusion was stated harder than
MODEL-AB's own limits support.** *(fixed)*

  Evidence: the README asserted "at standard rates the cheaper-per-token
  model is the more expensive choice" with the caveat that the ratio "assumes
  both arms share a token mix". MODEL-AB is more forthright: the mix is not
  merely unproven, it is *known* to differ, and in the direction that
  undermines the conclusion — Sonnet re-read more (cheap input/cache tokens)
  while producing fewer words (expensive output tokens), so 1.135x is
  plausibly an over-estimate and a ~12% blended-price shift would drop it
  under 1.0.
  Why it matters: this repo's whole claim is that it publishes numbers you
  can check, and the section in question argues for spending more money. A
  summary that is less honest than the document it summarizes inverts the
  point.
  Fix: the README now makes the narrower claim it can defend — a 0.6x rate
  card does not buy a 0.6x bill, the gap is most of the way to erasing the
  discount, and the direction should not be assumed without measuring.

### Notes

- **[NOTE] README.md — "~16 MB of share plus its ground truth"** was
  ambiguous and 40% off on the natural reading (share 16.36 MB, metadata
  5.29 MB, total 21.64 MB). Now states both, measured by bytes. *(fixed)*
- **[NOTE] README.md — the fleet table mixed aggregations.** Mean words was
  doc-weighted (694.3) beside a ratio that only reproduced org-weighted
  (0.995). Both cells were individually true, but a reader recomputing the
  second the way they recomputed the first would not reproduce it. Now both
  doc-weighted (0.998). *(fixed)*
- **[NOTE] README.md — the board false-positive anecdote was told twice** in
  near-identical terms, ~40 lines apart, after the restructure moved a
  section. The first telling is now a pointer; the full account lives once,
  under a promoted `### What this does not prove` heading (which also fixed
  what would have been a dead anchor). *(fixed)*
- **[NOTE] Reviewer false positive, recorded deliberately.** The adversary
  reported that CLAUDE.md still declares additive evolution "SUSPENDED" and
  contradicts the README. It does not: it grepped the word and matched the
  clause that records the suspension *ending* ("This rule was SUSPENDED for
  the v2.0 window (M8-M11) ... and is **restored as of M11b**"). Verified
  before acting rather than after. This is the third reviewer/board false
  positive logged this turn, alongside the MODEL-AB byte-identical-prose
  claim and the "four of six reviewers" miscount — a useful running tally
  given `board-negative-control` is open and the README now tells readers to
  treat critics as the weakest instrument. Reviewers deserve the same
  scepticism the board gets.

### Fixes Applied

All BLOCK and WARN findings fixed, plus three of the four NOTEs; the fourth
was the reviewer's own error and needed no change. Tests unmoved at 440.

### Security

0 BLOCK / 0 WARN / 0 NOTE (`SECURITY.md`, commit `f7f945c`, scope `paths`,
8 files). Swept per-commit with `git log -p` rather than on the net diff,
because a net diff would hide a credential added and edited out within the
range — the plausible failure mode for a docs pass. No secrets, keys, or PII
in the added lines; the only URL is the author's own public repo and it
predates the range. The three test changes tighten rather than weaken, and
the `<=` -> `==` one closes a grandfather-by-absence hole. Carried forward
open: the M9 `render/pdf.py` letterhead NOTE (unchanged code, out of scope).

### Accepted Risks

None.

---
*Prior review (2026-07-17, `de60065`): the M11b arc — 2 BLOCK / 4 WARN / 7
NOTE, all fixed. Both BLOCKs were false published claims in the README
(a $500,500 fee total that was really $425,500, and "four of the six
reviewers" that was really two), caught only because the author delegated the
review to fresh-context adversaries rather than self-grading.*

<!-- REVIEW_META: {"date":"2026-07-17","commit":"f7f945c","reviewed_up_to":"f7f945cf64ea7d9e1266e63fa2a0a09c483a9593","base":"origin/main","tier":"full","block":0,"warn":0,"note":1} -->
