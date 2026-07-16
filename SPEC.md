# SPEC

## Spec — 2026-07-16 — M10: parallel authoring (concurrent-batch airlock)

**Goal:** M9 made document supply honest; SCALE.md then names the one binding
constraint on everything after it: the authoring wall. The airlock allows *at
most one outstanding work order per stage*, so `/forge` dispatches authoring
batches strictly serially, one model worker at a time. That is a hard cap on
generation wall-clock (a ~360-doc reference fleet is ~60 serial batches, a
~2,000-doc flagship ~334), and it is why M11 (the fleet) and M12 (the flagship)
wait on M10. Lift the wall: make the *author* stage carry multiple concurrent
outstanding work orders over disjoint document sets, tracked in `state.json` so
a killed session still loses and duplicates nothing, and teach `/forge` to
dispatch a bounded window of workers in parallel. The change is offline,
deterministic, additive to the state schema, and regenerates no committed
fixture. K=1 must reproduce today's serial behavior exactly.

### Acceptance Criteria

- [x] **The author stage tracks multiple concurrent outstanding work orders,
  additively.** `state.json` gains a new field (empty by default) mapping each
  outstanding authoring work order to the documents it covers; the existing
  `outstanding` (one-per-stage) is unchanged and still governs foundation
  enrichment. The `orgsmith/state@1` schema id and `extra="forbid"` are
  unchanged, and all seven committed `state.json` files still load and validate
  (they carry `outstanding: {}` and no new field), proven by the `org` tier
  staying green.

- [x] **`author --next-batch` emits the next batch disjoint from every
  outstanding one; repeated calls partition the batchable manifest with no
  overlap and no gap.** Two successive `--next-batch` calls with no intervening
  ingest produce two distinct work orders whose document sets are disjoint;
  draining to completion covers every batchable doc exactly once (no doc in two
  orders, none skipped). The partition is a pure function of the immutable
  manifest: the same recipe built twice yields identical batch/doc groupings.

- [x] **Each deliverable ingests independently and in any order.**
  `author --ingest` matches a deliverable to its own outstanding work order by
  id, writes that batch's DocIR, and clears only that batch; other outstanding
  batches are untouched. Ingesting batch B before batch A leaves A outstanding
  and the author stage not-done. The stage is marked `done` only when the last
  outstanding batch is ingested and every batchable doc is authored. Ingesting a
  `work_order_id` that is not an outstanding author batch fails loudly (no
  partial write).

- [x] **Resume across a kill loses nothing and duplicates nothing with multiple
  batches in flight.** With N batches dispatched and only some ingested,
  reloading state in a fresh process preserves the outstanding set;
  `--next-batch` then emits only genuinely uncovered batches (never re-covering
  an in-flight one), and the outstanding-but-uningested batches re-dispatch and
  ingest cleanly. End state: every batchable doc has exactly one DocIR and one
  rendered file, the stage is `done`, and `validate` passes. (Extends the
  existing single-batch resume tests to a multi-batch kill point.)

- [x] **`status --json` surfaces the outstanding author batches so a fresh
  session can re-dispatch them.** For each outstanding authoring work order,
  `status` reports its work-order path and the count of documents it covers;
  with none outstanding the set is empty. This is the file-derived signal
  `/forge` reads on resume (never conversation memory).

- [x] **`/forge` dispatches a bounded window of authoring workers concurrently,
  preserving the airlock and resumability.** The forge `SKILL.md` authoring step
  fills a window of up to K outstanding batches (K stated in the skill), spawns
  one `forge-author` worker per batch *in a single message* so they run
  concurrently, refills as each ingests, and on resume re-dispatches the batches
  `status` reports outstanding before emitting fresh ones. The airlock is
  unchanged in kind: Python still never calls a model, each work order is a
  self-contained JSON file, and every deliverable still ingests through
  `author --ingest`. K=1 reproduces the prior serial loop.

- [x] **Determinism and the seed discipline hold; no new randomness is
  introduced.** Parallel authoring reorders work, it does not generate anything,
  so it adds no `seeds.py` stream: the batch partition derives from the immutable
  manifest and work-order emission is deterministic per run. No committed fixture
  is regenerated or edited; `dev-mini`'s pure-stage pin (`test_org_regen.py`)
  stays green because authoring is downstream of the pinned stages.

- [x] **From a fresh checkout, `bin/test` passes all tiers offline and keyless,
  with `org` under ~5s and `unit` under ~30s.** New unit tests cover the
  concurrent-batch airlock: emission disjointness, out-of-order and reject-path
  ingest, multi-batch resume, `status` surfacing, and partition determinism.
  Baseline test counts and timing are recorded at turn close.

### Context

- **This closes M9 and consumes its turn.** M9 landed the genre registry
  (driver-derived supply, realistic per-genre lengths, a folder taxonomy beyond
  `Engagements/Finance/Firm`) and regenerated `dev-mini` as the sole byte pin.
  Its board recorded 0 BLOCK / 0 WARN / 3 NOTE. The propose→consume cycle is
  compressed this turn by user instruction to implement autonomously.

- **Why this is the milestone, in the docs' own words (`docs/SCALE.md`).**
  "Authoring is a model pass per batch, `BATCH_SIZE = 6` documents, and `/forge`
  dispatches batches strictly serially — one worker at a time... This is why
  parallel authoring is M10 and precedes the fleet: the wall is the schedule.
  Nothing else on this page is close to binding." M10 attacks exactly that wall
  and nothing else.

- **The serial invariant, concretely.** `orgsmith/airlock.py` enforces "at most
  ONE outstanding work order per stage" via `state.outstanding: dict[str,str]`
  (stage → one work-order filename). `author --next-batch`
  (`authoring/contexts.py`) returns the first pending engagement group (≤
  `BATCH_SIZE`) and re-emits the same order until ingested; `author --ingest`
  (`authoring/ingest.py`) matches that single order and clears it. The rewrite
  keeps `outstanding` for the single-outstanding foundation stage and moves the
  author stage to a new multi-valued field keyed by `work_order_id`, each entry
  recording the doc_ids it covers so `--next-batch` can exclude in-flight docs
  without loading every work order.

- **Disjoint, complete, deterministic partition.** `pick_batch` gains an
  `exclude` set (docs already authored *or* covered by an outstanding order) and
  otherwise keeps its deterministic engagement-group logic, so draining
  `--next-batch` to exhaustion partitions the batchable manifest exactly once in
  manifest order. This is the property that makes a several-hundred-batch
  flagship both parallelizable and resumable.

- **Resume is file-derived, as ever.** Everything a resumed `/forge` needs is a
  pure function of committed files plus `state.json`. On restart the outstanding
  set is read back from `state.json`; `status --json` exposes it (work-order
  path + doc count) so the skill re-dispatches uningested batches before emitting
  fresh ones. Re-authoring an uningested batch is safe: its deliverable ingests
  against the same still-outstanding order. Serial numbering of work orders
  (`author-NNNN.json`) stays deterministic because the skill emits sequentially
  (separate shell calls) and only the model authoring runs concurrently.

- **The airlock is unchanged and absolute.** Python still never calls a model
  and never touches the network. Concurrency lives entirely in the orchestrating
  skill (multiple `Agent` dispatches in one message); the CLI only emits and
  ingests self-contained JSON work orders. The CLI does not cap concurrency — K
  is the skill's knob — which keeps every verb deterministic and offline.

- **Additive to the state schema (standing rule, not the relaxed one).** The
  v2.0 window relaxes additive evolution for *realism knobs and fleet regen*;
  parallel authoring is neither. It is a pure infra change: a new `state.json`
  field defaulting empty, no fixture regenerated, no schema id bumped. All seven
  committed `state.json` files load unchanged. This is stricter than the window
  requires, deliberately.

- **No org is regenerated this turn.** Proving the wall is lifted is an offline,
  deterministic exercise at the airlock/state level; the wall-clock payoff is
  realized only when `/forge` actually runs with concurrent workers (a model
  pass, tokens spent), which is how M11 exercises it at fleet scale. Regenerating
  `dev-mini` would re-author its committed prose for no test gain and is out of
  scope.

- **`org-tier-scaling-plan` stays deferred (BACKLOG).** Its revisit triggers
  (org tier > ~10s, the M11 reference fleet, or a committed org > ~150 files)
  have not fired: the `org` tier runs in ~1.3s and no fixture grows this turn.
  Splitting the tier now would be ceremony that saves nothing measurable.

- **House practices (zat.env).** Oracles beat proxies beat critics: the airlock
  and resume unit tests are the oracle for every criterion here; there is no
  board pass this turn. Small committable increments with tests in the same
  increment; the build and existing tests were green at turn start (short 12 /
  unit 334 / org 40). A prompt or knob that cannot name the failure mode it
  prevents is the first to delete. No push or remote mutation without explicit
  user instruction.

- Environment: Python 3.10-compatible; always `.venv/bin/python`. Tests are
  keyless and offline; CI has no LibreOffice, so nothing here may depend on it.

---
*Prior spec (2026-07-16): M9 the document-supply model (genre registry drives
driver-derived supply, realistic per-genre lengths, folder taxonomy beyond
Engagements/Finance/Firm); all 9 criteria met, dev-mini regenerated and re-pinned.*

### Proposal (2026-07-16)

**What happened.** M10 lifted the authoring wall offline. Five commits: the
concurrent-batch airlock (`author_batches` in state.json, additive so all
seven committed state.json load unchanged; `emit/match/clear_author_batch`),
`author --next-batch` emitting disjoint batches that partition the manifest
exactly once, per-id independent `--ingest`, `status --json` surfacing the
outstanding set, seven new unit tests, and `/forge` rewritten to dispatch a
K=4 parallel window with the orchestrator serializing ingest (workers author
only) so the CLI stays a lock-free single writer. All tiers green (393; org
1.3s, unit 29.8s). An end-to-end CLI drive confirmed three disjoint batches
emit, ingest in reverse order, and validate clean. No org regenerated: the
wall-clock payoff is realized only when `/forge` runs with real workers.

**Questions and directions.**
1. *Prove parallel authoring with real workers before the fleet.* This turn
   proved the machinery offline; nothing has yet measured the actual
   speedup or exercised the skill's concurrent dispatch + serial-ingest loop
   with live forge-author workers. A single real `/forge dev-mini` run (small,
   cheap) would de-risk M11's large generation and produce the first per-batch
   timing SCALE.md admits it lacks. Do this first, or fold it into M11?
2. *M11: the reference fleet* (`docs/SCALE.md`: ~6-8 orgs, 30-60 docs each,
   ~360 total, breadth over volume). This is the big model-driven turn:
   regenerate/author the fleet under the full v2.0 stack (M8 fabric + M9
   supply + M10 parallel), then **restore the frozen-fixtures and additive
   rules** (CLAUDE.md says M11 does this) and re-freeze. Keep six slugs or
   widen to eight for sector/era/ACL/format breadth? Regenerate existing
   recipes or write new ones?
3. *The deferred backlog comes due at M11.* `recipe-growth-outruns-headcount`
   (make each recipe's growth/headcount/span describe one firm),
   `charter-redump-drift` (decide byte-frozen vs additive charter.json),
   `acl-blind-to-departure` (departed-employee read access), and
   `org-tier-scaling-plan` (the tier will cross its split triggers as the
   fleet grows) all have M11 as their revisit signal.

<!-- SPEC_META: {"date":"2026-07-16","title":"M10: parallel authoring (concurrent-batch airlock)","criteria_total":8,"criteria_met":8} -->
