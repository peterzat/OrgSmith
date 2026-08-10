# SPEC

## Spec — 2026-08-03 — M17c: the controlled proof

**Goal:** Settle whether M17b's outline and scope work actually changes
authored prose, on a mid-size org rather than on the flagship. Generate one
new recipe twice through the live airlock, control arm knobs off and
treatment arm knobs on, so the structural axis reads a real before/after
instead of a cross-recipe comparison. De-risk M18 against an unproven
capability for a fraction of its cost, and give the board the first
discrimination test it has ever had.

### Acceptance Criteria

- [x] **One new recipe, generated twice, with the M17b knobs as the only
  variable.** A new recipe under `recipes/` produces a control arm with
  `engagements.scope` absent and `doc_culture.outline_variety` and
  `doc_culture.client_facing_reports` off, and a treatment arm with all
  three on. Same slug family, same seed, both arms authored through the live
  `/forge` airlock with model and effort recorded per batch. Each arm scores
  at least 120 same-genre pairs (`structural_pairs_considered`), so the
  comparison is over a distribution rather than a handful.

- [x] **The evidence standard is fixed before the numbers exist.** A dated
  document, committed before either arm is authored, states what result
  would count as the outline work having changed the prose, what result
  would count as it not having, and what the measurement cannot distinguish
  either way. Verifiable from git order: the standard's commit precedes the
  first authoring commit.

- [x] **The control is exact where it must be, and its residue is
  enumerated.** Across arms the share tree (file paths) and the manifest's
  doc ids, genres, dates, and authors are identical, and `foundation.json`
  and the finance and people ledgers are byte-identical. Every remaining
  difference is enumerated and attributed to a named knob rather than
  hand-waved. Shown by diff, recorded in the write-up.

- [x] **The structural axis is compared over every scored pair, not the
  printed top 50.** The comparison reports each arm's full same-genre
  distribution, with shape and openers reported separately, so a shift in
  the body of the distribution cannot hide behind the truncated reading
  list. `STRUCTURAL_TOP_N` bounds what the report prints and must not bound
  what the comparison reads.

- [x] **The board is asked the voice question on both arms without being
  told which is which.** Neither arm's slug, path, nor dispatch prompt
  announces which is the control or that an experiment exists. The two
  verdicts are recorded side by side. The write-up states plainly that this
  measures whether the board can discriminate two arms, not a false-positive
  rate against known-good prose, so `board-negative-control` gains a
  measurement without being closed by it.

- [x] **The treatment arm gets a full six-dimension board and its findings
  ship beside it.** Unflattering findings included, in the house pattern. Any
  comparison of its voice cluster against the exemplar's is labelled as
  uncontrolled, because the recipes differ.

- [x] **The knobs' first live exercise is reported including what went
  wrong.** Per-arm authoring-ingest rejection counts, every case where the
  outline machinery briefed a skeleton a worker could not satisfy or
  rejected a deliverable a reader would call conforming, and every scope fact
  whose rendered surface reads badly. Recorded rather than fixed silently. If
  the enforcement has to change, the generator changes; the enforcement is not
  softened to let a deliverable through.

- [ ] **The treatment arm is committed and frozen; the control arm is not.**
  The treatment arm validates clean, scores 100% on every eval split by
  construction, joins `PINNED = SLUGS`, and ships its data card,
  `GENERATION-REPORT.md`, `evals/`, `acl.json` and PERMISSIONS.md as derived
  artifacts. Its test-tier placement (`org` or `flagship`) is a deliberate
  decision recorded in TESTING.md with the measured added wall-clock. The
  control arm stays in gitignored `scratch/` on the `ab-probe` precedent.

- [x] **No committed fixture moves and no carve-out is opened.** The nine
  existing orgs' ledgers, manifests, and authored prose are untouched;
  `PINNED = SLUGS` is green at every commit including mid-turn. Adding a
  tenth org is not a regeneration.

- [x] **The docs reconcile to what the generation found, in either
  direction.** README's M17b paragraph stating that the proof is the next
  generation is replaced by what this generation settled, including a null or
  negative result stated as such. `docs/REVIEW-CALIBRATION.md` gains the
  second-org calibration of the structural axis. `BACKLOG.md`'s
  `cross-document-voice` records the outcome against its own revisit
  criterion.

- [ ] **Full `bin/test` passes keyless and offline** across short, unit, org,
  and flagship tiers, with the new org's tier costs measured rather than
  assumed.

### Deferred, with cause (2026-08-10)

Two criteria are deliberately unmet. Recorded here rather than checked off or
quietly dropped.

- **Criterion eight (commit and freeze the treatment arm): declined.** The
  arm's six-dimension board returned 5 blockers, three of them one defect: a
  count fact renders carrying its own noun ("12 acquisition targets") and
  authors wrote the noun again, so 12 of 59 documents ship "15 acquisition
  targets targets" into the rendered `.docx`, including an executed engagement
  letter. Four engagements also read "of the 12 candidates... 64 have been
  screened", because `unit_range` and `pipeline_top_range` do not nest.
  Committed fixtures freeze, so committing would make those permanent in the
  newest fleet member. This turn exists to de-risk M18 against an unproven
  capability; committing the first output of a capability it just proved
  defective would defeat that. Criterion seven's own rule applies: the
  generator changes, the enforcement is not softened.
- **Criterion eleven (tier costs for the new org): not applicable while
  eight is declined.** No new org joined a tier, so there is no added
  wall-clock to measure. Full `bin/test` passes keyless and offline across all
  four tiers (16 short, 739 unit, 230 org +27 skipped, 65 flagship +5
  skipped), unchanged from the turn's baseline.

**The measurement stands and must not be re-run to rescue these.** The
comparison was pre-registered and run once. Fixing the generator and
re-authoring the treatment arm would produce a second number chosen after
seeing the first; any such re-run belongs in a later turn, labelled as a
follow-up with a changed treatment, with the M17c result left as it is.

### Context

- **Adopted from the 2026-08-03 proposal in the prior SPEC entry**, with two
  scoping decisions taken by the user at spec time: prove on a mid-size org
  before the flagship, and author a real knobs-off control arm rather than
  comparing against the committed fleet. Both were the proposal's own
  recommended readings of its open questions.

- **Why an intermediate turn.** M17b landed four default-off knobs and a
  structural axis and adopted none of them anywhere. What is proven today is
  plumbing and block-shape counts under a scripted author. The flagship is
  ~334 batches (`docs/SCALE.md`), roughly nine times any run to date, and
  running it against an unexercised capability risks discovering at document
  900 that the outline enforcement misbehaves. This turn is ~10-18 batches per
  arm.

- **What makes the control cheap and exact.** Both new seed streams are keyed
  per item (`rng(seed, "fabric.engagements.scope", eid)` in
  `fabric/engagements.py:172`, `rng(seed, "docplan.outline", genre)` in
  `docplan/registry.py:652`), so turning the knobs on advances no other
  stream. Roster, engagements, finance, dates, authors, and the document set
  are expected to be identical across arms for that reason. That expectation
  is what criterion three verifies rather than assumes.

- **What the treatment arm changes and where.** `engagements.scope` plants
  additional entries in the existing `Engagement.facts` list;
  `outline_variety` rides the skeleton id in `render_params`, not in a new
  `ManifestEntry` field; `client_facing_reports` adds the engagement's client
  contact to the status-report mention plan, which may move ACL grants and
  PERMISSIONS.md. `GenreRule.scope_refs` is already populated on five genre
  rows in `docplan/registry.py`, so the registry needs no recipe action.

- **Two serialization traps, unchanged from M17b.** `dump_json` serializes
  every model field, so adding a field to `Fact`, `Engagement`, or
  `ManifestEntry` writes a key into all nine committed ledgers and breaks the
  byte pin. `datacard._knob_rows` walks the charter model, so a new knob
  rewrites all nine data cards. Re-emission order when metrics move:
  metrics/report, then `tools/checksums.py`, then `data-card` for every org.

- **The measurement may come back null or negative, and that is a result.**
  Nothing in these criteria requires the outline work to have helped. The
  pre-registered standard exists precisely so the conclusion cannot be chosen
  after the numbers are seen, and criterion ten requires the README to say
  what happened either way. A turn that proves the knob does not change prose
  is a successful turn and saves the flagship from carrying it.

- **Nothing that is not an oracle may gate.** The structural axis stays a
  measurement: no threshold it produces enters a test tier or a validator
  rule, this turn included. The board judges, the metric measures, the human
  decides.

- **Scratchpad exposure.** Two arms at ~10-18 batches each is roughly the
  M11b exposure (38 batches), not the flagship's ninefold, so the prompt-level
  mitigation in `/forge` Step 3b is unchanged
  (`concurrent-workers-share-one-scratchpad`). Recorded here so it is on the
  record before the batches run.

- **Hard rules in force.** Airlock: `orgsmith/` never calls a model or the
  network; all tiers keyless and offline; no LLM grades an LLM in an automated
  tier. Additive evolution: any new capability lands default-off with inert
  schema defaults on the existing `orgsmith/<kind>@<ver>` schema ids, drawing
  only from new `seeds.py` streams. Committed fixtures are frozen. Validator
  rules grandfather by charter, never by artifact absence. The new org's
  generated names must not collide with a screened real firm; a validator rule
  already checks this.

- **House practices (zat.env).** Small committable increments with tests in
  the same increment; run the relevant tier after each change; do not stack
  untested changes. Verification over prompting. Do not reword or reorder
  these criteria; check off only when verified. Committing is local; pushing
  is the user's call.

- **BACKLOG.** `cross-document-voice` and `board-negative-control` are ACTIVE
  in this spec. `concurrent-workers-share-one-scratchpad` is noted above and
  stays open; its flagship trigger has not fired. `packaging-and-archival`,
  `event-simulation`, `generator-fingerprinting`, and
  `mundane-broadcast-names-a-recipient-in-the-body` are out of scope.

- **Out of scope.** The M18 flagship; any regeneration of a committed org;
  era shocks in the finance model; inbound mail modelling; the DL-broadcast
  naming device; `rf:voice-3`, which no keyless proxy reaches; and closing
  `board-negative-control`, which needs known-good prose rather than two arms.

- **Baselines for this turn.** Suite green at `71ce014`: 16 short, 716 unit,
  228 org (+27 skipped), 65 flagship (+5 skipped). Nine committed orgs,
  `PINNED = SLUGS` fleet-wide, v2.3.0 tagged and pushed. `CODEREVIEW.md` and
  `SECURITY.md` both record zero open findings.

---
*Prior spec (2026-08-02): M17b, the batch-boundary turn; 12/12 criteria met,
four default-off knobs and a structural similarity axis landed with no fixture
regenerated.*

### Proposal (2026-08-10)

**What happened.** M17c generated `quillon-harbor` three times through the live
airlock (control, treatment, control-replicate): 177 documents, 39 batches,
**zero ingest rejections**. 9 of 11 criteria met; 8 and 11 declined with cause
rather than dropped.

The measurement, pre-registered and run once: the outline work **does** move
authored shape, same-genre structural similarity 0.372 to 0.309 over 245 pairs
per arm against a 0.008 run-to-run floor, so 7.7x the like-for-like noise. But
it **relocates** convergence as much as it reduces it (the 50 same-skeleton
pairs score 0.402, worse than a typical control pair), it does **not** move word
choice (lexical 0.0073/0.0066/0.0077, treatment gap under the control-replicate
spread), and per-pair noise of 0.110 means no single pair's score may be read as
an effect. A blind board scored variety 4 (control) against 5 (treatment) with a
blocker on the control and none on the treatment, but answered the dimension's
own question identically on both. Both reviewers independently judged the
lexical metric misleading and shape the real signal.

**Neither arm was committed.** The treatment arm's six-dimension board returned
**5 blockers**, three of them one fact-surface defect: a count fact renders
carrying its own noun and authors wrote the noun again, so 12 of 59 documents
ship "15 acquisition targets targets" into the rendered `.docx`, including an
executed engagement letter. `scope` and the funnel counts also do not nest, so
four engagements read "of the 12 candidates... 64 have been screened". No
committed fixture moved and no carve-out opened.

Also this turn: `docs/M17C-RUN-LOG.md` records nine findings from the knobs'
first live exercise, including that the airlock does not stop a worker inventing
quantities no ledger owns (0 vs 18 such numbers across two identical control
runs). `docs/REVIEW-CALIBRATION.md` gained a second-org calibration. A newcomer
pass on README added the fleet rationale and fixed four stale claims, including
a validator described as 29-, 34- and 37-rule in four places when `RULES` has 39.
A fleet audit found **`ashcombe-advisory` is a third org carrying the
recipient-mention defect**, and the only one where a board rates it a blocker.

**Questions and directions.**

1. **Fix the scope knob and re-run the treatment arm?** The board corrected the
   remedy this log first proposed: four of eight engagements reconcile `scope`
   against the funnel correctly, so the fix is a **briefing constraint, not a
   ledger change**. Add a doubled-noun ingest check (mechanical, catches all 12),
   then re-run and commit a clean `quillon-harbor`. Any re-measurement must be
   labelled a follow-up with a changed treatment, not a second draw on the
   pre-registration.
2. **A mail-regeneration carve-out for the three orgs?** `ashcombe-advisory`,
   `hollowell-ip`, `meridian-actuarial` all run `exempt_recipient_mentions: off`
   and the fix is landed and proven inert. Ashcombe is the strongest case.
3. **Can the board work at flagship scale at all?** `board-yield-at-scale`
   records findings-per-sampled-document falling from 0.725 (northgate, 51
   sampled) to 0.048 (calderwood, 168 sampled) at the same coverage band. M18 is
   ~12x calderwood. Cheapest probe is re-boarding calderwood and measuring the
   yield a second time.
4. **Does M18 go before or after 1-3?** Three of this turn's findings gate it:
   the scope knob is not ready, the board may not scale, and the airlock permits
   unverifiable invented quantities.

<!-- SPEC_META: {"date":"2026-08-03","title":"M17c: the controlled proof","criteria_total":11,"criteria_met":9} -->
