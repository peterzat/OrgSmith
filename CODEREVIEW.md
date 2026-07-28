# CODEREVIEW

## Review — 2026-07-28 (commit: dcd8c91)

**Summary:** Full review of the M16 push (11 commits, `origin/main`..HEAD): the
eight-org fleet regenerated wholesale under the realism wave's knobs and
re-frozen, boarded across six dimensions, the CLAUDE.md carve-out closed, and
the docs (README, TESTING, DISTRIBUTIONS, BACKLOG) reconciled to the regenerated
reality. The diff is dominated by generated fixtures under `companies/` (1524
files); the only executable code change is `orgsmith/distributions.py`.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN issues.

- The one code change, `orgsmith/distributions.py`, adds a frozen
  `WAVE_BASELINE_M15` constant and a `_wave_before_after` renderer that emits a
  committed M15→M16 before/after table. Correctness verified: the 5-tuple order
  in the constant matches the unpacking, `by_slug` keys on the same `slug`
  values the rows carry (including `**fleet**`), and orgs absent from either
  side are safely skipped. No new I/O or input surface.
- Security (`/security orgsmith/distributions.py`, this run): 0 findings. The
  markdown-injection path into the derived dashboard is unreachable — the only
  variable cell is `charter.slug` (pattern-locked `^[a-z0-9][a-z0-9-]*$`), every
  other cell is numeric, and authored prose reaches the table only through an
  integer word count.
- The regenerated fixtures are validated by the org tier (per-org validators,
  0 errors) and the fleet byte pin (`PINNED = SLUGS`), both green; the recipe
  knob additions (business calendar, sample book, style/voice, mail, noise) pass
  the recipe-coherence test. These are generated, not hand-written, and are
  covered by the test suite rather than line review.
- NOTE (not a diff defect, recorded for the human): criterion 1's clause "no
  recipe brief recites its own genre specifications" is **not** met — the recipe
  briefs still carry genre-spec prose (stored in `charter.json` as `narrative`),
  so `recipe-brief-leaks-genre-spec` stays open in BACKLOG. The regenerated
  overviews happen not to parrot it. Closing it needs a brief rewrite plus
  regeneration.
- NOTE (documented, recorded not fixed): `hollowell-ip`'s document_plausibility
  board found a blocker — 9 of 18 engagement emails render a duplicated `To:/Cc:`
  block because the mention check drove workers to put the recipient full name in
  the body. The board is read-only and the fixture prose is frozen; a renderer or
  authoring-guidance fix plus re-render is a separate unit of work (noted in
  CLAUDE.md and the README).

### Fixes Applied

None.

### Accepted Risks

None.

### Test Baseline

Full default suite green: 606 passing (14 short, 518 unit, 74 org), keyless and
offline; byte pin green at every mid-wave commit. Flagship tier 20 passing.

---
*Prior review (2026-07-23, commit 014c138): full review of the M15 turn, 0 BLOCK / 3 WARN / 1 NOTE; that review's code is not present in this push's diff.*

<!-- REVIEW_META: {"date":"2026-07-28","commit":"dcd8c91","reviewed_up_to":"dcd8c910da0f046796f5f1f38d519d1ca02cb4c1","base":"origin/main","tier":"full","block":0,"warn":0,"note":2} -->
