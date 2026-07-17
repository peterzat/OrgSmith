# SPEC

## Spec — 2026-07-17 — M11b: the fleet turn, the retirement, and the re-freeze

**Goal:** Close the v2.0 arc. Generate the five remaining reference-fleet orgs
through the live `/forge` loop, retire the six pre-v2.0 fixtures wholesale,
board one flagship so the README can quote a critic on the org it actually
ships, and restore the two standing rules M8-M11 suspended: additive evolution
and the fixture freeze. M11a proved the recipes derive, cohere, and generate on
one tracer; this turn spends the 3-6 hours that proof was meant to de-risk.

### Acceptance Criteria

- [ ] **Resume survives the interrupt shape this run actually has: several
  concurrent outstanding batches.** `test_resume_mid_authoring_no_dup_no_loss`
  proves the single-orphan case, but M10 authors K=4 wide, so a killed session
  strands up to K outstanding orders at once, and that case has no test. A unit
  test kills a fresh process with **more than one** batch outstanding and
  asserts the M10 airlock invariant holds across the restart: every orphan stays
  outstanding, no document is claimed by two work orders, none is lost, and the
  org completes and validates clean. Resume stays file-derived: no new state
  file, no fleet-level ledger, no conversation memory. `/forge`'s Step 3 drain
  is what recovers it, and the test names that path.

- [ ] **The five remaining fleet orgs are generated end to end through live
  `/forge` and committed.** `brackenridge-civil`, `saltmarsh-environmental`,
  `hollowell-ip`, `northgate-staffing`, `verdant-health`. For each: authoring
  runs through the real airlock, `validate` passes with 0 errors and SKIP lines
  only for knobs its recipe leaves off, its structure re-derives byte-identical
  from the recipe, and it joins `PINNED`. Each batch records the model and
  effort that authored it in `state.json`'s `generators`, and every authoring
  pass runs at or above `AUTHORING_EFFORT_FLOOR` on the same model as the
  tracer. If a run exposes a defect, it is fixed in the smallest change that
  addresses it and pinned by a unit test.

- [ ] **Every org's authored length is checked against its briefs before the
  fleet is believed, and the number is recorded.** `report`'s mean-ratio-to-brief
  is the cheapest instrument in the system and the one that separated the
  MODEL-AB arms decisively for free (1.16 vs 0.60). Each new org's mean words
  and mean ratio to brief are written to its `GENERATION-REPORT.md` and read
  before the org is committed. Recorded as a measurement, never a gate: no
  ratio, length, or similarity threshold enters any test tier.

- [ ] **The six pre-v2.0 fixtures retire, and every commit on the way stays
  shippable.** `torchlake-engineering`, `quillbrook-appraisal`,
  `bramblewood-legal`, `gladepoint-strategies`, `cindergrove-advisors`, and
  `fernhollow-partners` are removed along with their recipes and metadata, and
  no commit in this turn leaves the repo advertising a company it does not ship
  or quoting findings against an org that is gone. The README's fleet table,
  counts, format/genre breakdowns, and "what is in the box" prose match what is
  committed at every step, not only at the end.

- [ ] **One flagship is boarded, and its findings replace fernhollow's in the
  README** (engages `board-negative-control`). `/forge-review` runs read-only
  against one new org; its findings commit next to the org they judged. The
  README's "What is not modeled today" section quotes the new board against the
  org it actually ships. Because the board's false-positive rate is still
  unmeasured, every major carried into the README is checkable by hand against a
  ledger, and any that is not is reported as the board's opinion rather than as
  a fact about the generator.

- [ ] **The fleet re-freezes and the two suspended rules are restored.** `PINNED`
  covers every committed org; CLAUDE.md's "Additive evolution — SUSPENDED" and
  "Committed fixtures are frozen — EXCEPT" carve-outs are removed and the
  standing rules restated, and the README's design principles match. The v2.0
  window is closed in the same commit that closes it in code.

- [ ] **`_COHERENCE_EXEMPT` cannot go stale** (closes the M11a review NOTE).
  `tests/test_org_regen.py` asserts `_COHERENCE_EXEMPT <= set(RECIPES)`, so a
  deleted recipe forces the set to be pruned in the same commit rather than
  silently exempting a future slug that reuses the name. The set shrinks to
  `{"dev-mini"}` as this turn's retirement makes the other six entries dead.

- [ ] **`bin/test` passes all tiers offline and keyless at close** (short / unit
  / org), with counts and timing recorded in TESTING.md, and no tier gains a
  model, network, key, or wall-clock dependency. `dev-mini`'s byte pin stays
  green and the fleet-wide re-derivation covers the new orgs.

### Context

- **Use the same model as the tracer, at or above the effort floor. This is
  measured, not a preference.** `docs/MODEL-AB.md` ran the same recipe at the
  same seed through both arms: the weaker model produced a corpus at **60% of
  what its briefs asked, 8 of 9 documents off brief**, which a blind board
  **rejected outright** — and which **passed all 29 validator rules with zero
  errors**. Nothing downstream can detect a weak authoring pass from the
  artifacts. Three things make this the wrong turn to save tokens on: the fleet
  is the published product and gets **byte-pinned at the end**, so a thin pass is
  discovered after 3-6 hours and costs another 3-6 to redo; `meridian-actuarial`
  was authored at `claude-opus-4-8[1m]` / `xhigh` (recorded in its `generators`)
  and is the tracer the other five are supposed to match, so a mid-fleet model
  switch makes the fleet heterogeneous in exactly the dimension it exists to
  demonstrate; and MODEL-AB tested Opus against Haiku, **not Sonnet**, so it
  does not license a Sonnet run — it only establishes that the axis is real and
  large. If the cheaper arm is ever worth testing, the honest experiment is one
  org, `report`, and a board pass (~40 min), not a five-org fleet.

- **The resume mechanism mostly exists; one shape is untested.** State is
  file-derived per CLAUDE.md: `state.json` carries per-stage status, per-doc
  `authored_hash`/`rendered_hash`, and outstanding batch refs; `airlock.py`
  enforces that no two outstanding author orders overlap; `/forge` Step 3 drains
  outstanding before emitting anything new, and re-authoring an outstanding
  batch is safe because its deliverable ingests against the same still-open
  order. `test_resume_mid_authoring_no_dup_no_loss` and
  `test_partial_render_survives_resume` cover this for **one** orphan. Criterion
  1 covers K>1 because that is the real shape of a killed K=4 window, and it is
  the only resume work this turn should do. Do not build a fleet-level progress
  file: per-org `state.json` plus `status --json` already answers "where did
  this stop", and a new ledger would be state that can disagree with the files.

- **Order the work so every commit ships.** Generate first, retire last: the
  retirement lands with (or after) the final generation, so the repo never
  advertises an org it does not have. The README is the constraint that makes
  this concrete — it quotes fernhollow's findings at length under "We publish
  what the critic said about us", so fernhollow cannot be deleted before the new
  flagship's board findings exist to replace them. That ordering makes criterion
  5 a prerequisite of criterion 4, not a follow-on.

- **What can fail before it costs authoring time.** M11a's derive-every-recipe
  test already turns NAME-01 collisions, `affiliations_in_docs` shortfalls,
  `ocr_layer_rate` without `scanned_ratio`, and a `date_range` preceding
  `founded` into ~60ms failures. Run `bin/test` green before starting.
  `brackenridge-civil` (`legacy_ratio: 1.0`, `scanned_ratio: 0.5`) and
  `saltmarsh-environmental` (`scanned_ratio: 0.6`) need **LibreOffice at
  generation time**: confirm `python -m orgsmith doctor` reports `soffice ok`
  before dispatching either, because the failure otherwise lands at render, after
  the tokens are spent. CI has none, so validation of every committed fixture
  must stay pure Python.

- **`seeds.py` per-stream discipline is NOT relaxed,** even though the fleet is
  being regenerated. Any new randomness draws from a NEW named stream, never by
  re-using or reordering an existing one. `test_org_regen.py` exists because a
  reordered draw passes every other tier.

- **The airlock is not touched.** Python still never calls a model or the
  network. The board is read-only, never authored what it reviews, and `bin/test`
  cannot reach it.

- **Nothing new gates.** No `report` metric, board finding, or wall-clock number
  becomes an assertion. The metric measures, the board judges, the human decides.

- **`dev-mini` is not regenerated** and is not part of the fleet. It is the unit
  tier's scaffold (~349 tests build on it) and its byte pin is the regression
  oracle. `dev-mini-margin-incoherent` stays deferred: this turn does not
  re-author the tracer, which is that entry's stated revisit signal.

- **House practices (zat.env).** Oracles beat proxies beat critics: `validate`
  and the structure pin are the oracles; `report` is the proxy; the board is the
  critic and is treated as the weakest. Small committable increments with tests
  in the same increment. When fixing a bug, change only what is necessary. If two
  consecutive fix attempts fail, revert to the last working state and
  re-evaluate.

- **Environment.** Python 3.10-compatible; run everything via `.venv/bin/python`.
  Tests stay keyless and offline. Expect ~3-6 hours of authoring wall-clock
  (`docs/SCALE.md`, M11a's fleet-scale measurement: ~209 docs, ~40 batches,
  ~5.2 min/batch at 1.86x). Sessions may be interrupted; criterion 1 is what
  makes that cheap.

- **This turn ends with a push** (explicitly authorized): implement
  autonomously, then push when the criteria are met and `bin/test` is green.

---
*Prior spec (2026-07-16): M11a — the reference fleet's six new recipes, roster
growth, employment-scoped ACL, the guarded charter write, the M10 security fix,
and `meridian-actuarial` generated live as the fleet's byte-pinned tracer; all 8
criteria met, reviewed 0 BLOCK / 0 WARN / 1 NOTE.*

<!-- SPEC_META: {"date":"2026-07-17","title":"M11b: the fleet turn, the retirement, and the re-freeze","criteria_total":8,"criteria_met":0} -->
</content>
