# SPEC

## Spec — 2026-07-22 — M15: organizational noise v2, persona voice v2, and the two-dashboard split

**Goal:** Land the wave's noise and voice capability layers plus the
measurement split that lets M16 show deltas: derived zero-token noise kinds
(version chains, misfiles, stale templates, filename variety,
attachment-version mismatch, empty directories), a structured per-person
style spec driving per-author briefs, deterministic per-author proxy
metrics, an integrity-vs-realism reporting split with distributional
numbers published against the still-frozen fleet, and dev-mini's one-time
regeneration as the voice proof bed, closing its incoherent margin.

### Acceptance Criteria

- [x] **Additive and inert by default.** `NoiseModel` gains count fields for
  the new kinds (version chains, misfiled copies, stale templates, empty
  directories, attachment-version mismatch) plus a filename-variety switch,
  all defaulting zero/off on the existing schema ids; the per-person style
  spec lands under a new default-off knob with inert schema defaults. Every
  committed org (the seven fleet orgs, `calderwood-partners`,
  `ashcombe-advisory`) loads, validates, re-serializes, and regenerates
  byte-identically with the new knobs off; `PINNED = SLUGS` stays green;
  all committed `foundation.json` files re-serialize byte-identically. In
  particular `calderwood-partners`, whose committed `{duplicates: 15,
  drafts: 20}` noise is already on, re-plans a byte-identical manifest, so
  the new fields cannot perturb the existing draw order. New randomness
  comes only from new `seeds.py` streams, and a knob-off charter draws zero
  values from every one of them. Every new validator check skips visibly on
  a knob-off charter and fails on knob-on-with-artifact-missing.

- [x] **Version chains with divergence.** A knob-on org contains a version
  chain of length 3 or more in which no two members are byte-identical, so
  hash dedupe cannot collapse it; every non-final member is labeled derived
  with its source and kind in the manifest and carries a deterministic date
  earlier than its source's, inside the recipe's date range.

- [x] **Misfiled copies.** A misfiled derived copy sits in a folder other
  than its source's, including across engagement folders; the manifest owns
  the location; ACL grants and the visibility suite follow the real
  location automatically (acl derives from the manifest), so a misfile
  readable by the wrong team is ground truth, never a validator failure.

- [x] **Stale templates.** Stale templates render as genre-shaped documents
  with bracketed dummy fields, zero planted facts, and zero planned
  mentions, labeled derived; they are never a retrieval or extraction
  answer (they remain visibility answers because they are readable
  documents, mirroring the mundane-genre precedent).

- [x] **Filename variety.** Noise filenames draw from a variant decoration
  grammar ("Copy of X", "X (1)", "X_old", "X FINAL FINAL" and the like)
  under the switch; existing kinds' naming stays byte-unchanged; the
  knob-on org shows at least three distinct decoration patterns.

- [x] **Attachment-version mismatch.** At least one knob-on transmittal
  email attaches a non-final version-chain member while the share holds the
  final; the attached bytes are byte-identical to the manifested draft
  member; the manifest owns the mismatch relationship; eval attribution
  stays exact.

- [x] **Split hygiene and tamper coverage.** Every new noise kind is
  excluded from the `core` and `distractors` eval splits and included in
  `noise` and `full` automatically; NOISE-01 (or a successor rule) covers
  the new kinds so knob-on with labels missing is a failure; ground truth
  scores 100% on all four splits; MAN-01, FILE-01, and PROV-01 hold
  unweakened (every derived file manifested, openable, stamped); empty
  directories recompute from the charter knob; a count with too few
  eligible sources fails actionably at plan time (the existing `NoiseModel`
  idiom), never silently under-plans.

- [x] **The zero-token pilot noise append.** `ashcombe-advisory` gains the
  noise kinds under its updated recipe via a wholesale pipeline re-run that
  reuses its committed DocIR: no authoring batch is dispatched (`state.json`
  shows none), derived entries are appended, the org re-renders,
  re-validates green, scores 100% on all four splits, and is re-pinned. The
  zero-token claim is stated in its `GENERATION-REPORT.md` and is true.

- [x] **Per-person style spec in the ledgers.** Under the new knob, each
  roster person carries a structured style spec (register, sentence-length
  bias, greeting and closing forms, formatting habits, banned tics) drawn
  deterministically from a new stream and stored in the deterministic
  ledgers; enrichment `persona` prose remains the model's only free-text
  field, and the spec is never model-authored.

- [x] **Per-author brief guidance.** Knob-on briefs carry per-author
  guidance derived from the style spec, auditable in retained work orders;
  `voice_diversify` v1 keeps meaning exactly what it means for existing
  recipes; style guidance composes with M14 signatures: style owns
  salutation and prose habits, the ledger owns signature facts.

- [x] **The two adopted mail-brief fixes.** (a) An engagement-thread reply
  brief names the recipient and audience (who the message is To, whether
  the thread is client-facing), so a client-delivered reply is no longer
  authored as an internal note; unit-tested against the brief text
  (capability half of `mail-audience-internal-vs-external`; fixture proof
  lands at M16's pilot regeneration). (b) Mention planning exempts a
  mail-block email's author from required body mentions, gated so every
  committed manifest still re-derives byte-identically; the render-time
  signature still names the author and validation still passes
  (capability half of `mundane-email-author-self-names`); unit-tested.

- [x] **Per-author proxy metrics.** `report` computes deterministic
  per-author metrics with no model (within-author vs cross-author
  similarity, author consistency over time), reported as ranges beside the
  existing pre-registered tic table and labeled measure-never-gate; no new
  metric gates any test tier.

- [x] **The two-dashboard split with frozen-fleet numbers.**
  `GENERATION-REPORT.md` and the README present Integrity (validator
  results, byte pin, evals scoring 100% by construction) and Realism
  (distributions, similarity, voice ranges, board findings) as separate
  dashboards with a hard line, no number appearing in the wrong context;
  the distributional dashboard runs against the still-frozen fleet and its
  numbers are committed before any regeneration so M16 can show deltas;
  reference lines are documented as non-calibrated context (annotating
  `external-validity-program`, not closing it).

- [x] **dev-mini regenerated once, coherent.** Under the carve-out,
  dev-mini's recipe is retuned so growth, headcount, and span describe one
  firm; the org regenerates wholesale, live through the airlock, with the
  voice knob on and noise off (the tracer stays bare); it validates green,
  scores 100% on all four splits, and is re-pinned; `_COHERENCE_EXEMPT` in
  `tests/test_org_regen.py` is emptied and the coherence test passes on
  dev-mini unexempted. Closes `dev-mini-margin-incoherent`.

- [x] **Tests, docs, and the ledger of record.** Full `bin/test` (all tiers
  plus `flagship`) green, keyless and offline, with the byte pin green at
  every commit including mid-turn; `docs/RECIPE-FORMAT.md` documents the
  new noise and voice knobs; a `noise-kinds-deliberately-excluded`
  BACKLOG.md entry records the four user-accepted exclusions
  (corrupted/unopenable files, personal material, contradictory
  corrections, broken cross-document links) with reasons and revisit
  criteria; `generator-fingerprinting` is annotated (filename grammar and
  voice-template fingerprints eroded; real defenses stay deferred).

### Context

- **Consumed from the 2026-07-22 proposal; adopted from the M15 section of
  `~/.claude/plans/we-ve-gotten-to-a-squishy-torvalds.md`** (the approved
  M13-M16 realism wave). Read that section for the outcome-by-outcome
  detail; the criteria above reformulate and consolidate its 11 candidate
  outcomes plus the dev-mini regen.

- **Two decisions taken at adoption.** (1) The two M14 pilot-board
  mail-brief fixes ride M15 rather than M16: M16 is scoped as
  regeneration, re-freeze, and release, and the additive rule requires a
  capability to exist and be proven inert before a regeneration can turn
  it on, so the capability half lands here and the fixture proof lands
  with M16's pilot regeneration. Both entries' revisit criteria name M15
  because the same files are touched (`authoring/contexts.py:389` for the
  reply guidance, `docplan/planner.py:741` `plan_mentions` for the
  exemption). (2) The dev-mini regeneration also fixes its incoherent
  margin, closing `dev-mini-margin-incoherent`, since the carve-out's
  one-time regen is exactly that entry's cheapest revisit path.

- **Out of scope (user-accepted exclusions, logged to BACKLOG per the last
  criterion):** corrupted or unopenable files (FILE-01 stays a tamper
  oracle), personal material, contradictory corrections, broken
  cross-document links. Also out: any post-hoc voice-editing pass, any
  gate on any voice or realism number, showing workers sibling prose (the
  M10 wall stays down), and fleet-brief rewrites
  (`recipe-brief-leaks-genre-spec` stays deferred to M16's recipe
  updates).

- **Carve-out mechanics.** `ashcombe-advisory` is the wave workbench: its
  extension is a wholesale pipeline re-run under an updated recipe with
  committed DocIR reused, never an in-place edit of ledgers, manifest, or
  prose. `dev-mini` regenerates exactly once, here. `PINNED = SLUGS` must
  be green at every commit, including between capability landing and
  regeneration.

- **Inertness edges the pressure test surfaced.** (1) `calderwood-partners`
  is the sharpest: its noise knob is already on, so new `NoiseModel` fields
  must not perturb the existing duplicates/drafts draw order (criterion 1
  pins its manifest byte-identity explicitly). (2) The mention-planning
  exemption changes pinned manifest content, so it must be gated such that
  committed manifests re-derive byte-identically until a recipe opts in.
  (3) Committed `foundation.json` files are frozen and non-re-emittable;
  wherever the style spec lives, their bytes cannot change (the M14
  distribution-lists precedent: a derived ledger is the escape hatch if an
  inert field cannot hold byte-identity).

- **CI has no LibreOffice, no model, no network, no key, no wall clock in
  any test tier.** All new noise kinds derive and validate pure-Python;
  fixture-validating tests stay keyless and offline, per CLAUDE.md.

- **House practices (zat.env).** Small committable increments with tests in
  the same increment; run the relevant tier after each functional change.
  If two consecutive fix attempts fail, revert and re-evaluate. Never
  modify a test to accommodate a regression. The airlock is untouched:
  Python never calls a model or the network, no LLM grades an LLM in any
  automated tier, and the noise stages spend zero tokens by construction.

- **Verification (this turn).** `bin/test` all tiers plus `flagship` green,
  keyless and offline; knob-off byte-identity proofs per capability before
  any org turns a knob on; the pilot noise append dispatches zero authoring
  batches; dev-mini regenerates live end to end, validates green, scores
  100% on all four splits; the frozen-fleet distributional numbers are
  committed before any regeneration.

---
*Prior spec (2026-07-21): M14 — email realism (thread mechanics + mailbox
ecology) under the optional `doc_culture.mail` block, proven by the committed
and boarded email-first pilot `ashcombe-advisory`; all 12 criteria met.*

### Proposal (2026-07-23)

**What happened.** M15 closed 15/15 in 18 commits (`bb2f4ae..e16b0ed`). Six
noise kinds, filename variety, attachment-version mismatch, and a structured
per-person style spec all landed as default-off knobs proven inert against
the frozen fleet before any org turned one on. Two orgs then turned them on:
`ashcombe-advisory` gained 17 derived documents (87 -> 104) as a pipeline
re-run over its committed DocIR, spending zero tokens — checked, not claimed:
`docir/` byte-identical, workorders unchanged, 16 generator batches with none
outstanding. `dev-mini` regenerated live at `xhigh` under a retuned recipe;
its terminal net margin fell 43.1% -> 22.7%, `_COHERENCE_EXEMPT` is empty,
and `dev-mini-margin-incoherent` is closed. Reporting split into Integrity
and Realism dashboards with frozen-fleet distributions committed first, so
M16's deltas are visible in git. Suite 551 -> 603; byte pin green at every
commit.

Three things the turn found that the spec did not anticipate, all fixed at
the cause: git cannot commit an empty directory (each planned junk directory
now carries a `.gitkeep`, sanctioned by both halves of the twin and nowhere
else); `style_specs.json` is an `acl`-stage output, so it joins
`DERIVED_LEDGERS` and is covered by STY-01's recompute instead; and unit
fixtures were inheriting optional knobs from the tracer recipe, which turned
one recipe edit into 51 unrelated test failures (`conftest.base_recipe_text`
now strips them, so fixtures pin their own knobs).

Two M15 capabilities are deliberately unproven on any fixture: the
mail-audience brief and the mundane-mail author-mention exemption exist,
gated and unit-tested, with `exempt_author_mentions: false` everywhere. Their
fixture proof was scoped to M16 at adoption.

**Questions and directions.** M16 is the wave's last turn: regenerate the six
remaining fleet orgs, `calderwood-partners`, and `ashcombe-advisory` once
each under updated recipes, re-freeze, and close the carve-out.

1. **Which knobs does each recipe turn on?** Eight orgs, eight recipes, and
   every wave knob is currently off in all of them. A fleet where each org
   demonstrates one thing is a different artifact from one where every org
   carries everything. This is the turn's main design decision and it should
   be made explicitly rather than knob by knob.
2. **What proves the two capability-only fixes?** Both need a regenerated org
   with the knob on plus something that reads the resulting prose. A client
   reply authored in an internal register is exactly the failure the board
   found and no automated tier can see.
3. **What does re-freeze mean concretely?** CLAUDE.md's carve-out paragraph
   is to be replaced with closure language mirroring M11b, and the README's
   fleet numbers, the knob table, `docs/DISTRIBUTIONS.md`, and TESTING.md's
   cold-open counts all move together.
4. **Board, and at what scope?** Eight regenerated orgs is the largest board
   surface yet, and `board-negative-control` is still open: the FP rate is
   unmeasured and every quoted finding still needs hand-verification.
5. **Cost.** ~600 documents of live authoring. Worth a batch estimate before
   the spec is written, not after.

**Revisit candidates.**

- `recipe-brief-leaks-genre-spec` — the entry's criterion ("the next time any
  fleet recipe's brief is edited") fired in M15 on dev-mini, and M16 rewrites
  all eight briefs. This is the cheapest moment this fix will ever have.
- `docplan-has-no-business-day-calendar` — criterion is "the fleet is
  regenerated for any other reason". The knob and CAL-01 shipped in M12; no
  fleet recipe declares one, and northgate still dates 36% of its documents
  on weekends, including two meetings that assert attendance.
- `reporting-line-drift` — needs correcting rather than only reviving: the
  entry says "nothing checks the prose agrees with it", which M12 made false
  (`authoring/ingest.py::_check_reporting_line`). What survives is the
  committed prose in the frozen fleet, which M16's regeneration clears, at
  which point the entry closes.

1 more in BACKLOG.md: `recipe-coherence-test-has-no-floor`, whose "the test
is touched for any other reason" criterion fired when M15 emptied
`_COHERENCE_EXEMPT`.

<!-- SPEC_META: {"date":"2026-07-22","title":"M15: organizational noise v2, persona voice v2, and the two-dashboard split","criteria_total":15,"criteria_met":15} -->
