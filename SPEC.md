# SPEC

## Spec — 2026-07-17 — M12a: the flagship's capability layer, proven on a pilot

**Goal:** Build the capability layer the M12 flagship needs (a business-day
calendar, engagement/revenue coherence, a deterministic noise model, nested
eval splits, and a voice mitigation), land every piece of it additively so the
seven pinned orgs do not move, and prove the whole stack live on one pilot org
that turns every new knob on. The window-defeating ~2,000-document flagship is
M12b; this turn buys the right to run it without discovering its defects 30
hours in.

### Acceptance Criteria

- [ ] **A business-day calendar knob lands default-off.** A recipe that
  declares a calendar gets no document of a genre that asserts attendance
  (`meeting_minutes`, `engagement_email`) on a Saturday, Sunday, or a declared
  holiday; today 19 of 53 northgate documents (36%) land on a weekend and two
  minutes record client sessions on a Saturday and on US Independence Day. The
  knob moves `minutes_date`, which fabric plants as a *fact value* and docplan
  independently recomputes (`fabric/engagements.py:39-48`,
  `docplan/planner.py:238`), so both sides land on the same day or the org
  fails to derive rather than shipping a filename that disagrees with its own
  minutes. The calendar is era- and locale-dependent (the fleet spans
  1999-2025), so the recipe declares it rather than the code assuming one. Any
  new randomness draws from a NEW `seeds.py` stream. A validator rule
  grandfathers by charter: it skips visibly when the knob is off, and a knob
  that is on with the property violated is a failure, never a skip.

- [ ] **An engagement/revenue coherence knob lands default-off and closes the
  gap two reviewers found independently.** `build_finance` never receives the
  engagements ledger today (`fabric/finance.py:72`), so fees are 1.6-5.1% of
  lifetime revenue in every committed org while the firm's own overview calls
  five engagements "the whole business". With the knob on, the paperwork and
  the financial summaries describe one book: either revenue derives from the
  engagement ledger or `firm_digest` tells the author its engagements are a
  sample. The pilot's measured fee/revenue ratio is written to its
  `GENERATION-REPORT.md` and read before the org is committed. Recorded as a
  measurement, never a gate: no ratio threshold enters any test tier.

- [ ] **Prose can no longer contradict a reporting line the ledger owns.**
  This is a hard-rule violation rather than a realism gap: CLAUDE.md says
  relationships come from the ledgers and generated text never carries a value
  the ledger owns, but the org chart is not wired into the placeholder
  mechanism, so northgate ships two onboarding records telling a hire she
  reports to the Managing Director when `foundation.json` reports her to the
  Principal. A deliverable that states a reporting relationship contradicting
  `foundation.json`'s edges is rejected at ingest or cannot be written at all,
  proven by a unit test that feeds a contradicting deliverable and asserts the
  rejection. Not a knob: it applies to every org generated after it. Committed
  fixtures are not edited, so the frozen fleet keeps its drift.

- [ ] **A deterministic noise model lands default-off and costs no tokens.**
  With the knob on, a recipe emits duplicates, near-duplicates, and
  draft/final version chains **derived from already-authored documents rather
  than from a model pass**, drawn from a NEW `seeds.py` stream and
  byte-identical on re-derivation. Exact byte-duplicates alone are not
  sufficient: an agent collapses those on a hash without reading them
  (`docs/SCALE.md`), which is the caveat that decides whether the flagship's
  token count is real. Ground truth labels every noise file and names the
  document it derives from, so authored and derived words are separable and a
  scorer can exclude them; a knob that is on with those labels missing is a
  failure. No noise file carries a planted fact the answer key does not own.

- [ ] **`emit-evals` derives nested splits and ground truth still scores 100%
  on each.** Core / +distractors / +noise / full, one suite graded across all
  four, so the pilot yields a degradation curve rather than a headline number.
  What counts as a distractor versus noise is written down in `docs/` rather
  than left to the reader. `score` grades any split from nothing but the
  `evals/` directory, and ground-truth answers score 100% on every split by
  construction, which is the sanity check that the harness measures what it
  claims. Splits are derived and never stored, so the frozen fleet gains them
  without regeneration.

- [ ] **The voice mitigation is implemented, measured against a pre-registered
  pattern set, and reported whatever it says.** Cross-document voice is the
  board's largest cluster (5 of 16 majors) and `review/metrics.py` is
  structurally blind to it: northgate's own report records no same-genre pair
  above 0.0751 4-gram Jaccard against a corpus where four of five engagement
  emails contain the literal string "Two asks. First... Second...". A cheap
  mitigation ships (a per-author style vector, a banned-construction list, or
  equivalent) and its effect is measured on the pilot with an instrument whose
  patterns are **printed in the output**, reporting a range across strict and
  loose readings rather than a single number, because no ledger owns whether
  two sentences are the same rhetorical figure and every published count here
  has been taste wearing a decimal point. The result is recorded and published
  even if the mitigation does not move it, and the confounds are stated (n=1,
  a different recipe from the fleet's baseline). Nothing here gates.

- [ ] **One pilot org is generated end to end through live `/forge`, with
  every new knob on, and committed.** Roughly 200-300 documents: large enough
  to measure the knobs and the noise model at fleet-like batch counts, far
  short of defeating a context window, which is M12b's job. `validate` passes
  with 0 errors and SKIP lines only for knobs its recipe leaves off; its
  structure re-derives byte-identical; it joins `PINNED` automatically
  (`PINNED = SLUGS`, `tests/test_org_regen.py:127`). Its `format_mix.eml`
  exceeds its engagement count, so at least one thread ships with `k>0` and
  M9's 1-3 day reply cadence appears in a rendered `.eml` for the first time
  in any committed fixture. `state.json`'s `generators` records the model and
  effort per batch, every pass at or above `AUTHORING_EFFORT_FLOOR` on the
  same model as the fleet (`claude-opus-4-8[1m]`). Mean words and mean ratio
  to brief are recorded and read before the org is committed. `doctor` reports
  `soffice ok` before dispatching anything that needs it.

- [ ] **The seven committed orgs do not move, and the README stops calling
  knob-fixable findings generator limits.** The byte pin stays green
  fleet-wide, every new knob defaults off, every charter re-dump stays
  additive (`test_committed_charter_redump_stays_additive`), and no existing
  `seeds.py` stream is reused or reordered. The README's "What is not modeled
  today" currently states that every finding in it is a generator limit rather
  than a knob a recipe declined, and that when that stops being true the
  section has to say which. This turn makes it stop being true for the weekend
  meetings and the fee/revenue gap, so the section says so; `BACKLOG.md:86`
  calls paying this price mandatory rather than optional. Every README count,
  table, and fleet claim matches what is committed at each commit, not only at
  the end.

- [ ] **`bin/test` passes all tiers offline and keyless at close, and the
  pilot does not blow the org tier's budget.** The org tier is ~4.8s against a
  ~5s budget at ~13.7 ms/file, and a 200-300 doc pilot adds ~3-4s, so it takes
  its own marker excluded from the default run if it pushes the tier past
  budget (`TESTING.md:94-97` pre-specifies exactly this for the flagship;
  registering it means `pyproject.toml`, the `bin/test` allowlist, and a
  module-level `pytestmark`). Counts and timing are recorded in TESTING.md. No
  tier gains a model, network, key, or wall-clock dependency, and `dev-mini`'s
  byte pin stays green.

### Context

- **Scope decision (user, this turn): capability plus a scaled-down pilot.**
  The ~2,000-document flagship is ~334 batches and ~1.3 days of authoring
  (`docs/SCALE.md`). Building the knobs and proving them on a ~200-300 doc org
  first mirrors the M11a/M11b split that worked: M11a wrote six recipes and
  generated one tracer; M11b spent the 3-6 hours that proof de-risked. A
  defect found after 30 hours of flagship authoring costs another 30.

- **Additive evolution is restored and this turn does not suspend it.** The
  triad that makes default-off knobs safe is real and load-bearing:
  `seeds.py:13` hashes stream names through SHA-256, so a new stream cannot
  perturb an existing one ("Adding a new consumer never disturbs existing
  streams"); `schemas.py:51` sets `extra="forbid"` with inert defaults, so a
  new field is rejected rather than silently ignored; and
  `test_org_regen.py:322` enforces that a charter re-dump may gain a key but
  never drop or move one. The worked example to copy is `affiliations_in_docs`
  (`schemas.py:155-168`): an inert default, a comment naming the milestone, a
  `@model_validator` rejecting incoherent combinations, and inertness enforced
  at the consumer (`fabric/engagements.py:330-335`: "Knob off = zero fields
  touched and zero RNG consumed"). Schema ids stay `@1`; default-off is
  backward-compatible by construction.

- **The fleet and `dev-mini` are NOT regenerated** (`BACKLOG.md`,
  `fleet-regenerates-under-the-new-knobs`, decided 2026-07-17). SCALE.md keeps
  fixtures, fleet, and flagship as three jobs rather than three points on one
  line; regenerating the fleet to turn on flagship knobs conflates them, and
  re-suspending the freeze one milestone after restoring it makes the rules
  decorative. The price is paid in the README instead (criterion 8).

- **Where the code actually stands**, verified this turn rather than assumed:
  there is **no business-day calendar anywhere** (grep for weekday/weekend
  across `orgsmith/` returns zero hits), and document dates are mostly
  deterministic arithmetic off engagement anchors rather than RNG draws, so
  the knob is a change to `_engagement_dates`/`_add` rather than a new draw.
  **No noise model exists**: the `v2 FINAL` / `v3` filenames are cosmetic with
  no v1 behind them (`registry.py:148,196`), and `ManifestEntry.rev` is a
  soft-fix counter, so this is genuinely new surface. `build_finance` takes no
  engagements ledger at all, so criterion 2 changes its signature and the
  `fabric/run.py` stage order. Adding a genre on an existing driver needs only
  a `REGISTRY` row (`registry.py:99-209`).

- **Two entries fire as side effects and should be watched, not fixed.**
  Deriving `base_revenue` from the engagement book makes low-revenue recipes
  reachable by accident, which fires `recipe-coherence-test-has-no-floor`: the
  fleet coherence test asserts a 0.40 margin ceiling with **no floor**
  (`tests/test_org_regen.py:112,252`), so an absurdly poor firm passes it. If
  criterion 2 takes the derive-revenue design, the floor stops being
  hypothetical and a number can be chosen against a real case. Separately, a
  pilot at fleet-like batch counts does *not* multiply
  `concurrent-workers-share-one-scratchpad`'s exposure ~9x the way the
  flagship will; the prompt-level mitigation (`/forge` Step 3b, namespace
  scratch per work order) held across 38 batches at M11b and is at proven
  exposure here. M12b's spec must take the position this one defers.

- **What can fail before it costs authoring time.** `test_every_recipe_derives`
  turns impossible knob combinations into ~60ms failures across every recipe.
  Run `bin/test` green before dispatching anything. `doctor` reports `soffice
  ok` and effort `xhigh` against a `high` floor on this box today; CI has no
  LibreOffice, so validation of every committed fixture must stay pure Python.

- **Use the same model as the fleet, at or above the effort floor. This is
  measured, not a preference.** `docs/MODEL-AB.md`: the weak arm produced a
  corpus at 60% of what its briefs asked, which a blind board rejected
  outright and which **passed all 29 validator rules with zero errors**.
  Nothing downstream can detect a weak authoring pass from the artifacts. The
  pilot gets byte-pinned like everything else. `AUTHORING_EFFORT_FLOOR` lives
  in exactly one place (`effort.py:30`) and a short-tier test enforces that.

- **Nothing new gates, and the hierarchy decides which instrument to trust.**
  Oracles beat proxies beat critics (zat.env): `validate` and the byte pin are
  the oracles, `report` and the voice instrument are proxies, the board is the
  critic and is treated as the weakest. No `report` metric, board finding,
  ratio, or wall-clock number becomes an assertion. A similarity rule would
  only teach the generator to paraphrase. The metric measures, the board
  judges, the human decides.

- **The airlock is not touched.** Python still never calls a model or the
  network. Model touchpoints stay exactly `--emit-context`/`--next-batch` and
  `--ingest`. No LLM grades an LLM in any automated tier.

- **House practices (zat.env).** Small committable increments with tests in
  the same increment; every commit ships. When fixing a bug, change only what
  is necessary. If two consecutive fix attempts fail, revert to the last
  working state and re-evaluate. Do not modify a test to accommodate a
  regression. Write state to a file before context grows stale: this turn
  spans a multi-hour authoring run, and resume is file-derived from
  `state.json` plus committed files, never conversation memory.

- **Environment.** Python 3.10-compatible; run everything via
  `.venv/bin/python`. Tests stay keyless and offline. Expect roughly 3-5 hours
  of pilot authoring wall-clock at the fleet's measured ~5.2 min/batch and
  1.86x window speedup, and treat that as a range rather than a constant:
  per-batch time varied ~9x within a single run at one setting.

- **This turn ends with a push** (explicitly authorized): implement
  autonomously, then push when the criteria are met and `bin/test` is green.

---
*Prior spec (2026-07-17): M11b — the five remaining fleet orgs generated live,
the six pre-v2.0 fixtures retired, one flagship boarded, and the byte pin and
additive evolution restored fleet-wide; all 8 criteria met, reviewed 3 BLOCK /
3 WARN / 6 NOTE, all fixed.*

<!-- SPEC_META: {"date":"2026-07-17","title":"M12a: the flagship's capability layer, proven on a pilot","criteria_total":9,"criteria_met":0} -->
