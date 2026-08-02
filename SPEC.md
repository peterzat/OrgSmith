# SPEC

## Spec — 2026-07-29 — M17: the answer-key turn

**Goal:** Make the evaluation layer truthful about the rendered corpus and make
the exemplar demonstrate the headline surface, in response to the 2026-07-28
external critique. The answer key gains equivalence clusters and scan-derived
acceptance so no document that visibly contains the answer is ever scored as an
error; scoring gains ranked metrics, baselines, and per-org data cards; and a
three-org carve-out regenerates northgate-staffing (enriched recipe) plus the
two mail demonstrators (recipient-mention exemption), closing at v2.2.0.

### Acceptance Criteria

- [x] **Byte-copy equivalence clusters.** Every derived byte-copy
  (`exact_duplicate`, `misfile`, byte-identity verified by hash at emit time,
  never assumed from the kind label) and every transmittal carrying a
  byte-identical attachment is an equivalence-class member of its source,
  emitted into `evals/` beside the questions. Returning a member in place of
  or beside its source scores correct on retrieval and extraction (the
  critique's Coleman-duplicate probe scores 41/41 pre-regen). Transmittals
  move from gold-union to cluster equivalents; the gold change is recorded as
  deliberate. A v2.1.1-shape evals dir with no cluster data scores
  byte-identically through the new scorer. Durable regression tests anchor on
  orgs that stay frozen (ashcombe duplicates, misfiles, transmittals) plus a
  fleet-wide property test (every byte-identical derived copy of a required
  doc is accepted), so they survive the regenerations.

- [x] **Rendered-truth acceptance for mention and alias questions.** Mention
  and alias questions carry scan-derived acceptable documents: word-boundary
  hits for the canonical full name or exact alias token in extracted document
  text, beyond the planned set. Acceptable docs are never penalized and never
  required (recall stays measured against planned gold). Pre-regen
  checkpoints: q:0030 gains exactly the six onboarding docs, q:0032's
  acceptance includes d:0006, and an answer returning all 23 Fuentes docs
  scores correct; the durable form is a fleet-wide property test (every
  scan hit for a questioned surface is required, acceptable, or a recorded
  diagnostic). A versioned label policy document defines the scan semantics,
  cluster canonicalization, never-acceptable doctrine (near-duplicates), and
  stated limitations; every emitted `evals/README.md` cites the policy
  version.

- [x] **Fact-value consistency diagnostics.** Every extraction
  `expected_value` surface is scanned corpus-wide at emit. Hits outside
  required-plus-clusters are recorded in an emitted diagnostics artifact
  (value collisions, unplanned-alias sightings, incidental-mention counts),
  never silently added to gold and never accepted as correct answers.
  Derived near-duplicate hits are lineage-explained rather than flagged.
  Pre-regen, northgate's diagnostics record the d:0006 "Jim" sighting with
  its registered owner; a synthetic-collision unit test proves the recording
  path.

- [ ] **Splits become a real degradation axis.** `build_splits` stops
  unioning visibility gold into the answer set; `distractors` strictly
  exceeds `core` on every org with mundane traffic (ashcombe, hollowell,
  meridian pre-regen; northgate post-regen). The visibility suite's
  non-gradability on core/distractors is documented, ground-truth-per-split
  self-checks are updated accordingly, and EVAL-SPLITS.md describes splits
  as a retrieval/extraction device.

- [ ] **Ranked and separated scoring.** For retrieval, `score` reports the
  cluster-canonical strict headline (map through clusters, drop acceptable,
  exact-compare to required), macro precision/recall/F1, Recall@5, Recall@10,
  MRR, and nDCG@10 computed from answer-list order per the plan's metric
  definitions; visibility stays raw exact-set. Extraction reports value
  accuracy and attribution accuracy separately beside the conjunctive
  headline, attribution cluster-canonical. All of it is in the `--json`
  payload. Ground-truth answers score 100% on every suite, org, and split,
  fleet-wide, before and after the regenerations.

- [x] **Graph contract covers participation and dates** (cut-line eligible
  per plan). Engagement entities enter the scored contract and participant
  edges stop being stripped: northgate's 22 participant edges are scorable
  end-to-end by naming engagements (pre-regen checkpoint; property test
  fleet-wide). Answer edges may carry optional start/end dates; a dated-edge
  credit ratio is reported; a dateless answer file validates and scores
  identical edge precision/recall to v2.1.1.

- [x] **Unanswerable questions exist and score** (cut-line eligible per
  plan). Empty-gold questions are emitted with an answerable-false marker
  instead of being dropped (the hollowell p:sharon.woods question exists
  pre-regen); abstention or returning only acceptable docs scores correct,
  an invented answer fails with an abstention-expected failure, and ranked
  aggregates skip unanswerables.

- [x] **Derived evals are stable and tamper-evident.** `emit-evals` is
  byte-idempotent on all nine orgs; a new EVAL-01 validator re-derives
  committed `evals/` and fails on any drifted, missing, or extra file
  (mutating one byte of a committed evals file yields a finding; an org
  whose evals were never emitted skips visibly); `tools/checksums.py
  --check` passes whenever the turn is at rest.

- [x] **Alias-agreement discipline.** A default-off charter knob gates two
  ingest rejections (a registered alias token in resolved authored text
  without a planned mention for that doc; an alias registered to one person
  appearing in another person's persona) and a validate-time MENT-03 twin.
  With the knob off the frozen fleet re-derives byte-identical and validates
  clean; forced on against the pre-regen northgate, MENT-03 flags d:0006
  (recorded checkpoint), and a synthetic-org unit test keeps proving the
  rejection and the rule after the regen.

- [x] **Keyless baselines.** Filename-only and BM25 retrieval baselines
  (pure Python, offline, deterministic, documented tokenizer and
  tie-breaking) produce ordinary answer files scored by the ordinary scorer,
  with committed per-org summaries for all nine orgs plus a fleet baselines
  document; recompute-and-compare tests prove byte-stability; baseline
  scores appear in each data card. No vector, embedding, or model baseline
  ships.

- [x] **Per-org data cards.** A derived data-card emitter writes a card for
  each of the nine orgs stating: feature matrix from the charter, document
  counts (authored/static/derived, format mix), question counts per family
  with difficulty tags and answerable counts, split cardinalities with an
  explicit distractor-gap line, ACL posture and grant fan-out, label-policy
  version, known residuals derived from board findings plus diagnostics
  (northgate's Jim entry pre-regen; the full-name device on
  ashcombe/calderwood), baseline scores, the org's checksum line, and
  recommended uses / non-claims. The README fleet table links every card;
  re-emission is byte-idempotent.

- [ ] **The critique is committed.** `docs/EXTERNAL-CRITIQUE-2026-07-28.md`
  holds the verbatim critique, hand-checked verdicts including the two
  places it undershot (the split collapse is fleet-wide and structural; the
  mention-gold disagreements are a policy gap closed by acceptable sets, not
  a wrong ledger), and the disposition table.

- [x] **Onboarding and docs are reconciled.** The README start-here count
  matches the fleet table (53 authored and static plus 13 derived, 66 in
  all); "read northgate and stop" gains coverage pointers naming the org
  that exercises each capability the exemplar lacks pre-regen; metric
  language matches the implemented scorer; TESTING.md and README test
  counts are re-measured by running the tiers; the flagship renumbers M17
  to M18 in README and docs/SCALE.md; `doctor` treats a missing
  WeasyPrint/Pango stack as generation-unavailable (warning, exit 0) while
  validation-only use passes.

- [ ] **The exemplar is regenerated under the carve-out.**
  northgate-staffing is regenerated once, wholesale, under its enriched
  recipe (departmental ACL, mail threads with mundane traffic and both
  mention exemptions, scanned_ratio with an OCR layer, signature-page and
  filename-date hard cases, alias-agreement on, noise suite kept). The
  regenerated org validates green (EVAL-01 and MENT-03 included), scores
  100% on all four splits, has four pairwise-distinct split cardinalities,
  non-vacuous visibility grants (departmental), extraction questions
  carrying scan and signature-page and filename-date difficulty tags, mail
  threads, an empty unplanned-alias diagnostics list, a published board,
  and a re-frozen byte pin; the org tier is green before the next
  regeneration starts.

- [ ] **The mail demonstrators are regenerated under the carve-out.** The
  recipient-mention exemption knob lands default-off and proven inert, then
  hollowell-ip and meridian-actuarial are regenerated wholesale under it:
  their mention_maps plan no forced recipient body-mentions for mail
  documents, MENT-01 still resolves recipients via transport headers, both
  orgs validate green, score 100% on all four splits, are boarded and
  re-frozen with the byte pin green after each.

- [ ] **The turn closes cleanly.** The CLAUDE.md carve-out (opened with the
  plan's declaration text before any regeneration) is replaced by closure
  language; the known-residual paragraph reflects the demonstrators' fix
  with the ashcombe/calderwood occurrences recorded in their data cards;
  the four BACKLOG annotations land (external-validity-program,
  mail-audience-internal-vs-external, board-negative-control,
  concurrent-workers-share-one-scratchpad); data cards and README are
  refreshed to final state; version 2.2.0 is set in the package and
  pyproject with an annotated v2.2.0 tag created (tag push only on explicit
  user confirmation); full `bin/test` (short, unit, org, flagship) passes
  keyless and offline.

### Context

- **Adopted from plan** `~/.claude/plans/output-of-this-planning-tranquil-melody.md`
  (approved 2026-07-28). The plan carries the increment order (17 committable
  units, cleave line after 12), the metric formulas, the label-policy
  outline, component designs (EVAL-01, MENT-03, baselines, data cards), the
  carve-out declaration text, and the disposition table. Read it before
  implementing; do not re-derive decisions recorded there. The critique text
  itself is in the planning conversation and must be committed verbatim in
  increment 1.

- **Frozen-fixture rule and the carve-out.** Exactly three orgs may be
  regenerated, once each, wholesale: northgate-staffing, hollowell-ip,
  meridian-actuarial. The plan's carve-out declaration goes into CLAUDE.md
  at increment 13 (before any regeneration) and is replaced by closure
  language at close. The other five fleet orgs and dev-mini stay frozen;
  `evals/`, `acl.json`, PERMISSIONS.md, GENERATION-REPORT.md, `review/`,
  baselines, and data cards are derived and re-emit freely. `PINNED =
  SLUGS` must be green at every commit, including mid-turn. Regenerate org
  by org with the org tier green between orgs; a blocker-level generator bug
  stops the turn and gets its own increment.

- **Probe anchoring.** The named northgate probes (q:0030, q:0032, d:0006,
  d:0054, d:0065) and the sharon.woods question are pre-regen checkpoints:
  the regenerations invalidate them. Durable regression tests must anchor on
  frozen orgs (ashcombe's duplicates, misfiles, transmittals) and on
  fleet-wide property tests, so the suite stays green after the three orgs
  are reborn. The MENT-03 d:0006 proof likewise converts to a synthetic-org
  test once northgate regenerates.

- **Hard rules in force all turn.** Airlock (orgsmith/ never calls a model
  or network; all test tiers keyless and offline; never LLM-grades-LLM in
  automated tiers). Additive evolution (both new knobs default off with
  inert schema defaults, proven byte-identical on the frozen six before any
  org turns them on; no randomness added, so no new seed streams are
  needed). Emitted evals gain a render-stage prerequisite; unit fixtures
  that emit without rendering must gain the render call (callers audited in
  the plan). New-field StrictModel forward-incompatibility (old orgsmith
  cannot read new evals) is accepted and documented; the reverse direction
  is tested. TESTING.md has no wall-clock asserts; org-tier cost of
  emit-time text extraction is measured and recorded, not gated. Board
  findings against fresh orgs are published, never prose-fixed.

- **House practices (zat.env).** Verification over prompting: the value of
  this turn is oracle quality, so every criterion is enforced by tests or
  recompute-and-compare, not prose. Small committable increments with tests
  in the same increment; run the relevant tier after each change; do not
  stack untested changes. Do not reword or reorder these criteria; check
  off only when verified. Committing is local; pushing (including the
  v2.2.0 tag) is a shared-state action for the user. Precision over recall
  in anything reported (diagnostics record, they do not speculate).

- **BACKLOG overlap.** `external-validity-program` (baselines and data
  cards are the adopted cheap slice; the transfer program stays out),
  `mail-audience-internal-vs-external` (recipient exemption lands;
  mixed internal/external thread design stays open),
  `board-negative-control` (three more boards this turn, tally maintained),
  `concurrent-workers-share-one-scratchpad` (~45-batch exposure; restate
  the /forge namespacing mitigation), `noise-kinds-deliberately-excluded`
  (cited for declining superseded-value families this turn),
  `recipe-coherence-test-has-no-floor` (three recipes are touched; the
  floor is still not adopted, margins must stay green). Annotations land at
  close per the plan's mutation table.

- **Out of scope.** Blind splits, leaderboards, confidence intervals;
  vector/embedding or model-agent baselines; superseded-value and temporal
  fact-history question families (their own schema turn); regeneration of
  any org beyond the three named (ashcombe/calderwood keep the full-name
  device, documented); the M18 flagship.

- **Baselines for this turn.** Current suite: 16 short, 563 unit, 74 org,
  20 flagship, green at 06cfc53 (CODEREVIEW.md 2026-07-28). TESTING.md's
  cold-open counts already drift from this; the docs criterion re-measures
  them at close.

---
*Prior spec (2026-07-28): fit-and-finish turn closing and hardening BYO,
reconciling docs, pruning the backlog; 7/7 criteria met.*

<!-- SPEC_META: {"date":"2026-07-29","title":"M17: the answer-key turn","criteria_total":16,"criteria_met":10} -->
