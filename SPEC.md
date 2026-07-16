# SPEC

## Spec — 2026-07-16 — Prove parallel authoring with real workers (dev-mini)

**Goal:** M10 built the concurrent-batch airlock and proved it *offline* with
conftest stand-ins for the model. Before M11 commits a ~360-document fleet to
that machinery, exercise the real path once: run the `/forge` authoring loop on
`dev-mini` with live `forge-author` workers, prove the concurrent-dispatch /
serial-ingest loop holds end to end, and capture the first real per-batch
authoring wall-clock, which `docs/SCALE.md` states it does not have. Small,
bounded, and cheap (dev-mini is 17 batchable docs in 4 engagement-group
batches); it de-risks M11's large generation and turns SCALE.md's authoring-wall
arithmetic from estimate into measurement.

### Acceptance Criteria

- [x] **Live parallel authoring runs end to end on dev-mini with a real
  concurrent window.** A real authoring pass dispatches more than one
  `forge-author` worker in a single message (the K>1 window of
  `forge/SKILL.md` Step 3b), each authoring through the live CLI airlock
  (`author --next-batch` / `author --ingest`), not conftest stand-ins. With
  dev-mini partitioning into 4 batchable engagement groups (17 batchable docs;
  5 static workbooks), at least two author work orders are outstanding at the
  same time, verified by `status --json` reporting more than one `author_batches`
  entry at the peak of the window.

- [x] **The concurrent-dispatch / serial-ingest loop holds with live workers.**
  Each worker writes only its reply file (author-only, no ingest); the
  orchestrator runs every `author --ingest` itself, serially. Batches ingest
  cleanly regardless of completion order (at least one round ingested in an
  order different from emission, to exercise out-of-order ingest for real);
  draining covers every batchable doc exactly once (none lost, none duplicated).
  The author stage reaches `done`, and after render every batchable doc has
  exactly one DocIR and one rendered file.

- [x] **The live-authored org validates and matches the committed structure.**
  `validate` passes all rules with 0 errors on the live-authored result, and its
  pure-stage structure (foundation structural fields, `ledger/*.json`,
  `docplan/manifest.jsonl`) is byte-identical to the committed dev-mini, proving
  live parallel authoring perturbs only prose. Generated in a scratch workspace
  (`--root`) so the committed dev-mini fixture is left frozen; this is a
  determinism check against the committed bytes, not a regeneration of them.

- [x] **The first real per-batch authoring timing is written to `docs/SCALE.md`,**
  replacing its stated gap ("not measured here ... no clean per-batch timing
  exists"): a single real batch's wall-clock, the concurrent window's wall-clock
  for the remaining batches, the serial-equivalent that implies, and the
  measurement's limits (one run, one shared box, one model/effort). Recorded as
  a measurement, never a gate: no wall-clock assertion enters any test tier.

- [x] **The run's verdict on the M10 machinery is recorded, and any defect it
  surfaces is fixed minimally with test coverage.** If the live run exposes a
  bug in the skill's dispatch/ingest loop or the airlock verbs, it is fixed in
  the smallest change that addresses it and pinned by a unit test; if the run
  confirms M10 holds unchanged under live workers, that is stated in the turn's
  records (commit message / SCALE.md). No skill or CLI change is made that the
  run did not motivate. The committed dev-mini fixture is not churned; the
  deliverables are the measurement and any hardening the run earns.

- [x] **`bin/test` passes all tiers offline and keyless at close** (short /
  unit / org), with counts and timing recorded, and no tier gains a model,
  network, key, or wall-clock dependency. The dev-mini structure pin and the
  fleet re-derivation stay green (the committed fixture is unchanged this turn).

### Context

- **Why this and not M11.** M11 (the reference fleet: ~6-8 orgs, ~360 docs) is
  the big model-driven turn and carries open design decisions the proposal
  flags (six slugs or eight; regenerate recipes or write new ones) plus the
  restore-the-frozen-rules-and-re-freeze step. That is a multi-session,
  human-in-the-loop turn, not an autonomous-and-push one. This spec takes the
  proposal's explicitly-recommended first step ("Prove parallel authoring with
  real workers before the fleet ... Do this first"), which is bounded, verifiable
  offline after the fact, and produces the timing M11's planning needs.

- **What M10 already proved, and the gap this closes.** M10's five commits
  landed `author_batches` in `state.json` (additive; all seven committed
  state.json load unchanged), disjoint `--next-batch` emission that partitions
  the manifest exactly once, per-id independent `--ingest`, `status --json`
  surfacing of the outstanding set, seven unit tests, and `/forge` rewritten to
  a K=4 window. Every one of those was verified against conftest's scripted
  authoring stand-in (`run_authoring`), never a live model worker. The one thing
  no unit tier can reach is "a real `forge-author` worker, spawned concurrently
  with siblings, authors a batch that ingests and validates," because tiers must
  never call a model (CLAUDE.md: never LLM-grades-LLM; TESTING.md's three static
  guards). This turn is that missing end-to-end pass, run once by hand through
  the skill.

- **The measurement, concretely.** `docs/SCALE.md` (authoring-wall section)
  says per-batch timing is unmeasured because the committed fleet was authored
  across sessions. Methodology to fill it honestly: author batch 1 alone (one
  worker) to isolate a single-batch wall-clock P; then emit the remaining 3
  batches, confirm `status --json` shows 3 outstanding, dispatch 3 workers in
  one message, and measure the concurrent window Q. Q landing near P rather than
  near 3P is the parallelism payoff, stated with its caveats. This uses the same
  CLI verbs as the documented K=4 path; the 1-then-3 split only isolates a clean
  per-batch number.

- **The committed fixture stays frozen; the proof runs in a scratch workspace.**
  The de-risk goal (live workers exercise the concurrent loop; capture real
  timing) needs the *run*, not a committed prose churn. So the pipeline runs
  under `--root <scratch>` against the same recipe, producing a fresh org whose
  structure must come out byte-identical to committed dev-mini (a stronger
  determinism check than the in-place pin, since it diffs live-authored output
  against the frozen bytes). This keeps the push clean and low-risk: an in-place
  regen would rewrite ~50 derived files (docir, evals, mention_map, acl,
  GENERATION-REPORT) and strand the committed board `review/` findings, all for
  no proof the scratch run does not already give. Consistent with the M10 spec's
  "no needless regen" and the frozen-fixtures discipline; the real fleet regen is
  M11's job, done wholesale.

- **The airlock is not touched.** Python still never calls a model or the
  network. The concurrency lives entirely in the skill (multiple `Agent`
  dispatches in one message); the CLI only emits and ingests self-contained JSON
  work orders, and the orchestrator is the single serial writer of `state.json`.
  If the run reveals a defect, the fix stays on the skill/orchestration side or
  is an additive CLI correction with a unit test, never a relaxation of the
  airlock.

- **Determinism and seeds unchanged.** No new randomness, no new `seeds.py`
  stream: this turn reorders and times work, it does not generate anything new.
  The pure stages that feed authoring are the pinned ones, so structure holds.

- **House practices (zat.env).** Oracles beat proxies beat critics: `validate`
  (29 rules) and the structure pin are the oracles for every criterion here; the
  timing is a proxy written down, never a gate; there is no board pass this turn.
  Small committable increments with tests in the same increment; the build and
  tests were green at turn start (short 12 / unit 334 / org 40). A prompt or
  knob that cannot name the failure mode it prevents is the first to delete. No
  push or remote mutation without explicit user instruction (given this turn:
  implement autonomously, then push).

- Environment: Python 3.10-compatible; always `.venv/bin/python`. Tests stay
  keyless and offline; CI has no LibreOffice. dev-mini uses no legacy formats,
  so this run needs no `soffice`.

---
*Prior spec (2026-07-16): M10 parallel authoring (concurrent-batch airlock) —
`author_batches` in state.json, disjoint `--next-batch` emission, per-id
`--ingest`, `status` surfacing, `/forge` K=4 window; all 8 criteria met, proved
offline against conftest stand-ins.*

### Proposal (2026-07-16)

**What happened.** The de-risk landed. dev-mini authored end to end through
the live `/forge` loop (Opus 4.8 at max effort), not conftest stand-ins: one
enrichment worker plus four authoring batches, the three remaining batches run
as one concurrent window with three work orders outstanding at once, disjoint
over all 17 batchable docs, ingested serially out of emission order, the author
stage flipping to `done` only on the last. `validate`: 23 rules, 0 errors; the
live-authored structure came out byte-identical to the committed fixture
(foundation, all four ledgers, manifest, charter, even derived acl), so
determinism holds under live workers. First measured per-batch timing, written
to `docs/SCALE.md` which had none: ~12 min/batch (range 9.3-16.9), a 3-wide
window at **2.24x** within 4% of the slowest worker. Run in a scratch workspace
via `--root`, so committed dev-mini stays frozen and no code changed: **M10
works unchanged under real workers.**

**Questions and directions.**
1. *M11, the reference fleet, is now de-risked and next.* Six slugs or eight,
   for sector/era/ACL/format breadth? Regenerate the existing recipes under the
   full v2.0 stack (M8 fabric + M9 supply + M10 parallel) or write new ones? At
   the measured ~12 min/batch and K=4, a ~360-doc fleet is roughly a 4-6 hour
   generation (one or two sessions, resume carrying across), not a marathon.
2. *Restore the frozen rules at M11.* CLAUDE.md and README both say M11 ends the
   v2.0 breaking window: set `test_org_regen.py`'s `PINNED` back to `SLUGS`,
   restore the additive-evolution and frozen-fixtures wording, re-freeze the new
   fleet. Sequence it as the last step, after the fleet validates.
3. *The deferred backlog comes due at M11.* `recipe-growth-outruns-headcount`
   (each recipe's growth/headcount/span must describe one firm),
   `charter-redump-drift` (byte-frozen vs additive charter.json, decide when
   re-freezing), `acl-blind-to-departure` (departed-employee read access), and
   `org-tier-scaling-plan` (the tier crosses its split triggers as the fleet
   grows) all name M11 as their revisit signal.
4. *Fold live timing into fleet-scale re-measurement.* SCALE.md's M10 bullet
   asks for a K=4 re-measurement against many batches; M11's generation is
   exactly that data, at scale, for free.

<!-- SPEC_META: {"date":"2026-07-16","title":"Prove parallel authoring with real workers (dev-mini)","criteria_total":6,"criteria_met":6} -->
