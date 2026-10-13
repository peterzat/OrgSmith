# SPEC

## Spec — 2026-10-13 — M17d: M18 readiness

**Goal:** Clear what M17c found standing between the project and the M18
flagship, re-baselined for Claude Opus 5.5. Fix the generator defects the
last board traced to the generator rather than the model, measure whether
the new model changes authored prose before anyone regenerates for it,
measure whether the board's recall survives a larger reading list, and
commit a clean tenth org that exercises the fixes. No committed org is
regenerated and no carve-out opens.

### Acceptance Criteria

- [x] **The Opus 5.5 probe is pre-registered, exactly controlled, and
  reported in either direction.** A dated evidence standard, committed
  before the first probe work order is dispatched, states what result would
  count as Opus 5.5 changing authored prose against the M17c Opus 5 control
  arms, what would count as it not, and the sha256 of every grading script
  it names. A fourth `quillon-harbor` control arm (`delta`) is authored on
  `claude-opus-5-5` at the effort the M17c arms recorded, from code pinned
  at the pre-registration commit. Its deterministic artifacts, persona
  enrichment, and every work order are byte-identical to `alpha`'s, so the
  model is the only variable; any work order that differs is enumerated
  rather than assumed away. The write-up reports structural and lexical
  similarity against the `alpha`/`gamma` noise floor, unowned numbers,
  words against brief, and a blind voice verdict on `delta` and `alpha` by
  reviewers of the same model, re-verifies the grader hashes, and states
  the conclusion the standard's own reading gives, null included. The arm
  stays uncommitted in `scratch/`.

- [x] **Five generator fixes land as default-off knobs, proven inert
  against the frozen fleet.** With every new knob off, all nine committed
  orgs load, validate clean, and re-derive byte-identical structure
  (`PINNED = SLUGS` green at every commit). Each knob draws randomness from
  no existing `seeds.py` stream, has a unit test showing its effect when on,
  and is documented in `docs/RECIPE-FORMAT.md`. With each knob on:
  - engagement start dates (and the `start` fact) land on a business day
    under the recipe's declared calendar;
  - every engagement whose span a recipe-named senior title covers carries
    one such person as an internal participant, and so reaches that
    engagement's mentions and ACL grants;
  - an engagement's scope vocabulary follows its service line, and a
    service declared to have no funnel gets no pipeline facts, with SCOPE-01
    recomputing the per-service planting exactly;
  - a declared era shock scales a named fiscal year's revenue and travel,
    with every finance tie-out still holding and the following year
    returning to trend;
  - a scope-on brief tells the author that a count placeholder renders its
    own noun, and that scope and pipeline counts must not be written as
    shares, subsets, or remainders of one another (scope-off briefs are
    byte-identical to before).

- [x] **Authoring ingest rejects a doubled count noun.** A deliverable whose
  text follows a count-fact placeholder, within the same clause, with a word
  that repeats a word of that fact's own noun phrase (singular or plural) is
  rejected with the doc id and fact id named. Every one of the eleven M17c
  REND-01 occurrences in `scratch/arms/beta` is rejected by the check when
  replayed, and no deliverable of `alpha`, `gamma`, or any committed org's
  `workorders/` reply is.

- [x] **Unowned numbers are measured and never gate.** `report` writes, for
  every org, a count of integers in authored prose that no ledger value
  accounts for, per document and in total. It reproduces the direction of
  the M17c `alpha`/`gamma` split (fewer in `alpha`), and no test tier or
  validator rule thresholds it.

- [ ] **A tenth org is committed and frozen.** `quillon-harbor`, re-authored
  as a labelled follow-up to M17c's treatment arm with this turn's knobs on,
  is generated through the live `/forge` airlock on `claude-opus-5-5`,
  validates clean, scores 100% on every eval split by construction, joins
  `PINNED = SLUGS`, and ships its data card, `GENERATION-REPORT.md`,
  `evals/`, `acl.json` and PERMISSIONS.md. A full six-dimension board ships
  beside it, unflattering findings included. The commit rule is fixed now:
  a blocker that traces to a mechanical defect the generator should have
  prevented (a fact surface, a ledger contradiction, a rendering error)
  declines the commit with cause, as M17c did; a prose-judgment blocker
  ships as a published finding. Its test-tier placement is recorded in
  TESTING.md with the measured added wall-clock.

- [x] **The board's recall is measured at two reading-list sizes.** A
  deterministic tool plants a fixed set of known defects into a scratch copy
  of `calderwood-partners` (never the committed fixture). Reviewers on two
  dimensions read a small and a large reading list, both containing every
  planted document, without being told an experiment exists. Predictions
  are committed before dispatch. Recall per defect kind per list size is
  reported in `docs/REVIEW-CALIBRATION.md`, `board-yield-at-scale` records
  the result against its own revisit criterion, and the write-up states that
  this is a recall measurement and not a false-positive rate.

- [x] **BYO authoring sends what it records.** An Anthropic-shape request
  carries the configured effort and the generator record stamps the same
  value; a reply cut off at the output limit fails with a message naming the
  truncation and the limit instead of entering the repair loop; the default
  output limit fits a full six-document batch; the Anthropic default model
  is `claude-opus-5-5`. Covered by unit tests on a stubbed transport, keyless
  and offline.

- [x] **Concurrent ingest cannot lose an update.** Two processes ingesting
  disjoint deliverables into the same org at once both land in `state.json`,
  shown by a unit test that races them.

- [x] **The board's read-only rule is checked, not just asked for.**
  `/forge-review` records a digest of the org before dispatch and verifies
  it after; the digest changes when a DocIR, ledger, manifest, or rendered
  file changes and ignores the board's own outputs (`review/`,
  `GENERATION-REPORT.md`). Unit-tested.

- [x] **The skills name only commands that exist, and dispatch with an
  explicit model and effort.** A short-tier test parses every
  `orgsmith` command line in `.claude/skills/*/SKILL.md` against the real CLI
  parser and fails on an unknown verb or flag, and every repo script a skill
  names exists. `/forge` and `/forge-review` pass the worker model and
  effort at dispatch, and workers stamp the effort they were dispatched with.

- [x] **The M17c findings are on the durable register.** Every M17c run-log
  finding that names a generator defect or gates M18 (AIRLOCK-01, REND-01,
  SCOPE-A, SCOPE-D, MENT-A, off-calendar engagement starts, partners absent
  from engagements) has a `BACKLOG.md` entry or is recorded as closed by this
  turn, and `exemplar-has-no-2020` records that its second-org criterion
  fired.

- [x] **CLAUDE.md is a map, not a history.** The carve-out narratives move
  to a file under `docs/`, CLAUDE.md keeps every hard rule and operational
  fact (re-emission order, the serialization traps, the current freeze
  status), and it is under 100 lines.

- [ ] **The docs reconcile to what the turn found, and it ships.** README,
  `docs/MODEL-AB.md` (Round 3), `docs/RECIPE-FORMAT.md`,
  `docs/BYO-AUTHORING.md`, `docs/REVIEW-CALIBRATION.md`, `BACKLOG.md`,
  `CHECKSUMS.md`, and every data card state the final state. The mail-org
  carve-out is written as a proposal, not executed. The version is bumped,
  full `bin/test` passes keyless and offline across all four tiers, no
  committed org's ledgers, manifest, or authored prose differ from
  `aef75a9`, and the branch is pushed after `/codereview` passes.

### Context

- **Adopted from this session's analysis (2026-10-13)**, run autonomously at
  the user's instruction ("proceed autonomously with your recommendations,
  finish by updating docs, README, backlog, and then push"). It supersedes
  the M17c proposal's four questions, answering each: fix the scope knob and
  re-run (criteria two, three, five), propose the mail carve-out (twelve),
  probe the board at scale (six), and hold M18 until all three are done.

- **Why the probe runs first and on pinned code.** The probe's control is
  the M17c arms, authored by `claude-opus-5` at `xhigh` on the code at
  `aef75a9`. Any change to briefs, ingest, or render between those arms and
  `delta` would sit inside the measured gap. So `delta` runs from a git
  worktree pinned at the pre-registration commit, whose code is
  `aef75a9`'s, while this turn's code changes land in the main tree. "Keep a
  floor of checks that never moves mid-experiment" (the essay at
  agent-hypervisor.ai/posts/agent-first-repos), and hash the grader.

- **The Opus 5.5 facts this turn relies on** (platform docs, checked
  2026-10-13): 1M-token context, so M18's sizing premise in
  `docs/SCALE.md` is unchanged; 128K max output; `output_config.effort`
  with an omitted effort now running at `medium`; adaptive thinking always
  on, and its output counts against `max_tokens`. Worktree isolation for
  subagents branches from the default branch, so it does not carry
  in-flight work orders and does not close
  `concurrent-workers-share-one-scratchpad`.

- **What the five knobs touch, measured before writing them.**
  `fabric/engagements.py:436` draws the start date with no calendar shift
  (`to_business_day` is in the same file); in `alpha` 4 of 8 starts are a
  weekend or the declared 2016-07-04 holiday. `_staff`
  (`engagements.py:271`) draws teams uniformly from the delivery department
  with no seniority. `ScopeProfile` is recipe-wide (`plant_scope_facts`),
  consumed by the planner, the brief, and SCOPE-01. The brief's count line
  reads "count of <noun>; place where the number belongs" while the
  placeholder renders the number with its noun, which is REND-01's cause.
  `fabric/finance.py` has no notion of an era.

- **Serialization traps, unchanged.** `dump_json` writes every field, so a
  new field on `Charter`'s sub-models rewrites all nine `charter.json` files
  and, through `datacard._knob_rows`, all nine data cards. A new field on
  `Fact`, `Engagement`, or `ManifestEntry` would rewrite committed ledgers
  and break the pin; avoid it. Re-emission order when metrics move:
  metrics/report, then `tools/checksums.py`, then `data-card` for every org.

- **Nothing that is not an oracle may gate.** The structural axis, the
  unowned-number count, and the recall numbers are measurements. No
  threshold any of them produces enters a test tier or a validator rule.
  Ingest's doubled-noun check is an oracle (a fact surface plus the text the
  author wrote), so it may reject.

- **Hard rules in force.** Airlock: `orgsmith/` never calls a model or the
  network. Additive evolution with new seed streams only. Committed fixtures
  frozen; adding a tenth org is not a regeneration. Validator rules
  grandfather by charter, never by artifact absence. Committing is local;
  pushing goes through `/codereview`.

- **House practices (zat.env).** Small committable increments with tests in
  the same increment; run the relevant tier after each change; if a change
  breaks a passing test, revert and rethink rather than editing the test;
  two failed fixes in a row means stop and re-plan. Re-baseline on each
  model generation, and prefer measurement to folklore: MODEL-AB exists
  because "use the strongest model" was never measured. Precision over
  recall for every reviewer this turn dispatches.

- **BACKLOG.** `board-yield-at-scale` and `cross-document-voice` are engaged
  (criteria six and one); `board-negative-control` is touched but not
  closed (recall is not a false-positive rate);
  `concurrent-workers-share-one-scratchpad` stays open with its mitigation
  unchanged (~13 + ~13 batches, the M17c exposure);
  `exemplar-has-no-2020` and `mail-audience-internal-vs-external` are
  engaged by criteria two and twelve. `event-simulation`,
  `external-validity-program`, `generator-fingerprinting`,
  `packaging-and-archival`, `state-json-mixes-execution-and-provenance`,
  and `recipe-coherence-test-has-no-floor` are out of scope.

- **Out of scope.** Regenerating any committed org (the mail carve-out is
  proposed only); the M18 flagship; changing the global zat.env skills
  (using Claude Code's built-in `/code-review` as a second finder is a
  zat.env change); a false-positive-rate measurement for the board.

- **Baselines for this turn.** Suite green at `aef75a9`: 16 short, 739 unit,
  230 org (+27 skipped), 65 flagship (+5 skipped). Nine committed orgs,
  `PINNED = SLUGS`, v2.3.0 tagged and pushed; M17c closed at 9/11 with no
  version bump.

---
*Prior spec (2026-08-03): M17c, the controlled proof; 9/11 criteria met. The
outline knob moved authored shape 7.7x the noise floor but relocated
convergence and left word choice unmoved, and the treatment arm was declined
for commit over a doubled-noun rendering defect.*

<!-- SPEC_META: {"date":"2026-10-13","title":"M17d: M18 readiness","criteria_total":13,"criteria_met":11} -->
