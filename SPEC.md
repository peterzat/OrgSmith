# SPEC

## Spec — 2026-07-16 — M11a: the reference fleet's recipes, proven on one tracer

**Goal:** M11 is the v2.0 fleet reset, and it splits cleanly into work that is
deterministic and work that is a multi-hour authoring run. This turn takes the
deterministic half: write the new reference fleet's six-to-eight recipes from
scratch for breadth, close the four deferred decisions that all name M11 as
their revisit signal, fix the M10 security NOTE, and prove the new recipe shape
by generating exactly one of them end to end through the live `/forge` loop.
The fleet's remaining orgs, the retirement of the six old fixtures, and the
re-freeze are the next turn's job, which this one de-risks.

### Acceptance Criteria

- [x] **Six to eight new reference-fleet recipes land, and every recipe in the
  repo derives.** New `recipes/<slug>/ORG-CHARTER.md` files, designed for
  breadth rather than revised from the existing seven: across the set, spans
  covering a pre-2007 era and modern ones, both `acl_posture` values, and
  format mixes that exercise legacy binaries, scans (with and without an OCR
  layer), decks, and mail. Each recipe sits in SCALE.md's fleet band
  (`doc_culture.target_docs` in 30-60), and the recorded number equals what
  `docplan` actually yields, per RECIPE-FORMAT.md's honesty rule. Every recipe
  under `recipes/` runs all four pure stages to completion, enforced by a test
  that covers recipes with **no committed org yet**: today
  `test_every_committed_recipe_still_derives` walks only `COMMITTED ∩ recipes`,
  so a new recipe is untested until its org exists, which is exactly backwards
  ahead of a multi-hour fleet run.

- [x] **Every new recipe's growth, headcount, and span describe one firm**
  (closes `recipe-growth-outruns-headcount`). No new recipe reproduces the
  45-55% terminal net margins the backlog measured across the old fleet; each
  recipe's realized expense ratio across its full span is computed from its
  finance ledger and recorded, deterministically and with no model or
  wall-clock involved. `headcount` is concurrent *seats* and `RosterChurn`
  backfills a departure into the same seat rather than growing the firm, so
  this is a real decision (a headcount-over-time capability, or growth matched
  to fixed seats), not a number tweak. Whichever way it resolves is stated once
  in the recipe documentation.

- [x] **One new recipe is generated end to end through the live `/forge` loop
  and committed as the fleet's tracer.** It authors 30-60 documents through the
  real airlock (not conftest stand-ins), `validate` passes with 0 errors and
  SKIP lines only for knobs its recipe leaves off, its structure re-derives
  byte-identical from the recipe, and it joins `PINNED` beside `dev-mini`. Its
  per-org authoring wall-clock and batch count are written to `docs/SCALE.md`
  as the fleet-scale re-measurement its M10 bullet asks for, with the
  measurement's limits stated (one run, one box, one model/effort). Recorded as
  a measurement, never a gate: no wall-clock assertion enters any test tier. If
  the run exposes a defect, it is fixed in the smallest change that addresses
  it and pinned by a unit test.

- [x] **The M10 security NOTE is closed at the schema or the sink, not by check
  ordering.** A deliverable carrying a traversal-shaped `DocIR.doc_id` (e.g.
  `../../evil`) is rejected before any filesystem write by a guard local to
  `schemas.py` or `docir_path`, rather than only by `run_ingest`'s upstream
  `unknown` membership check running first. A unit test asserts the rejection
  directly. SECURITY.md records the fix and the NOTE closes.

- [x] **`acl-blind-to-departure` is decided and implemented.** Either `open`
  scopes grants to employment windows, with the question of whether a departed
  person keeps tenure-era access settled explicitly rather than left implicit,
  or `open` is documented to mean "current and former staff". Whichever:
  implemented in `acl.py`, pinned by a unit test that names the
  departed-employee case, reflected in the visibility suite, and the whole
  committed fleet's derived `acl.json` and PERMISSIONS.md re-emitted and
  validating clean.

- [x] **`charter-redump-drift` is decided and implemented.** Either
  `run_charter`'s write is guarded so re-deriving a committed fixture leaves
  `charter.json` byte-identical (matching `run_scaffold`'s
  immutable-once-written behavior), or the additive contract is made permanent
  and documented as such. `test_committed_charter_redump_stays_additive`
  tightens to whichever contract was chosen, and the CLAUDE.md / TESTING.md /
  README wording about frozen fixtures matches the decision.

- [x] **`org-tier-scaling-plan` is decided and documented.** The `org` tier is
  re-measured with the tracer committed (wall-clock and per-file cost, via
  `bin/test org`), and TESTING.md carries the split policy plus the trigger
  that fires it. "No split is warranted yet, and here is the measured trigger"
  is a valid resolution; an undocumented one is not.

- [x] **`bin/test` passes all tiers offline and keyless at close** (short /
  unit / org), with counts and timing recorded, and no tier gains a model,
  network, key, or wall-clock dependency. `dev-mini`'s byte pin and the
  fleet-wide re-derivation stay green.

### Context

- **Why this shape.** The proposal put M11 next and flagged it as multi-session
  and human-in-the-loop. Its open questions are now settled by decision: the
  fleet's recipes are **new, not revisions** of the existing seven; this turn
  is **prep plus one tracer org**, not the full ~360-document run; and all four
  deferred backlog entries close here. Splitting M11 this way puts every
  expensive, irreversible thing (the multi-hour fleet authoring, retiring six
  committed fixtures, the re-freeze) behind a cheap proof that the new recipes
  derive, cohere, and generate.

- **`recipes/dev-mini` is not retired and is not part of the new fleet.** It is
  the unit tier's scaffold: `build_pure_stages`, `build_knobbed_stages`,
  `build_acl_stages`, `build_hardcase_stages`, `build_mix_stages` and friends
  all copy `recipes/dev-mini` into `tmp_path`, so deleting it would take the
  ~334-test unit tier with it. SCALE.md is explicit that fixtures (9-19 docs,
  regression oracles) and the reference fleet (30-60 docs/org, breadth) are
  **different jobs, not points on one line**. dev-mini stays a fixture and the
  byte-pinned tracer; the six-to-eight new recipes are the fleet.

- **The six old fixtures stay committed this turn and retire at the fleet
  turn.** Deleting `torchlake-engineering`, `quillbrook-appraisal`,
  `bramblewood-legal`, `gladepoint-strategies`, `cindergrove-advisors`, and
  `fernhollow-partners` now would leave the repo advertising seven companies in
  its README while shipping two, and would strand the committed board findings
  the README quotes at length ("We publish what the critic said about us").
  They retire wholesale when the new fleet replaces them, so every commit on
  the way stays shippable. Their derived artifacts (`acl.json`, PERMISSIONS.md,
  `evals/`) are re-emitted this turn as the ACL decision requires; that is
  explicitly allowed by CLAUDE.md and is not a regeneration.

- **`headcount` is concurrent seats.** `Charter.headcount` counts seats held at
  any instant, and `RosterChurn.departures` backfills a leaver into the *same*
  seat, so no recipe today can describe a firm that grows. That is the
  mechanical root of `recipe-growth-outruns-headcount`: fees compound at
  `growth_rate`, compensation tracks a seat count that never moves, and the
  margin climbs to something no professional-services firm posts. It also bears
  on criterion 1, since the M9 supply model derives document volume from
  engagements, fiscal years, and **hires** — a firm that grows produces more
  documents, which is how a recipe reaches the 30-60 band honestly rather than
  by inflating `engagements.count`.

- **`seeds.py` per-stream discipline is NOT relaxed.** CLAUDE.md suspends
  additive evolution for the v2.0 window (knobs may default on, one code path,
  the fleet is regenerated), but the per-stream seed rule stands: any new
  randomness draws from a NEW named stream, never by re-using or reordering an
  existing one. That is what keeps a single generation reproducible, and
  `test_org_regen.py` exists specifically because a reordered draw passes every
  other tier.

- **The airlock is not touched.** Python still never calls a model or the
  network. The security fix hardens the inbound boundary (schema/sink guard);
  it does not relax it. Any recipe or capability work stays on the
  deterministic side of the airlock.

- **Nothing new gates.** The margin figures in criterion 2 are ground-truth
  ledger coherence, not prose proxies, so a deterministic check over them is
  legitimate; but no `report` metric, board finding, or wall-clock number
  becomes an assertion (TESTING.md: no metric threshold as a bar, no wall-clock
  asserts). The tracer's timing is written down and gates nothing. There is no
  board pass this turn.

- **What a new recipe can fail on, before it costs authoring time.** NAME-01
  screens generated names against `orgsmith/data/real_firms.txt` at charter and
  scaffold, so a collision fails early; `affiliations_in_docs` requires
  `multi_affiliations >= 1` and realistically `engagements.count >= 4`;
  `ocr_layer_rate` requires `scanned_ratio > 0`; `date_range` must not precede
  `founded`. Criterion 1's derive-every-recipe test is what turns each of these
  into a ~60ms failure instead of one discovered hours into the fleet run.

- **House practices (zat.env).** Oracles beat proxies beat critics: `validate`
  and the structure pin are the oracles for every criterion here. Small
  committable increments with tests in the same increment; verify the suite is
  green before starting (short 12 / unit 341 / org 40 at turn start, per the
  M10 review). When fixing a bug, change only what is necessary. If two
  consecutive fix attempts fail, revert to the last working state and
  re-evaluate. A knob that cannot name the failure mode it prevents is the
  first to delete.

- **Environment.** Python 3.10-compatible; run everything via `.venv/bin/python`.
  Tests stay keyless and offline. Any new recipe using `legacy_ratio` needs
  LibreOffice at generation time only (`python -m orgsmith doctor` reports
  `soffice ok`); CI has none, so validation of every committed fixture must
  stay pure Python.

- **This turn ends with a push** (explicitly authorized): implement
  autonomously, then push when the criteria are met and `bin/test` is green.

---
*Prior spec (2026-07-16): Prove parallel authoring with real workers on
dev-mini — live `/forge` loop, three concurrent work orders at 2.24x, first
measured per-batch timing (~12 min) written to `docs/SCALE.md`; all 6 criteria
met, M10 confirmed unchanged under live workers.*

<!-- SPEC_META: {"date":"2026-07-16","title":"M11a: the reference fleet's recipes, proven on one tracer","criteria_total":8,"criteria_met":8} -->
</content>
