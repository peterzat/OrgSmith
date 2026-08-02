# SPEC

## Spec — 2026-08-02 — M17b: the batch-boundary turn

**Goal:** Close the structural gap that produced both of M17's board blockers:
a fresh-context worker never sees a sibling, so the corpus diverges where
continuity is required and converges where variation is required. Make the
ledger own the quantities documents currently invent, make the plan own a
per-document skeleton, and give the realism instrument an axis that can see
paraphrased outline repetition. Capability only, no regeneration: the M18
flagship is the proof, and this turn is the gate before it.

### Acceptance Criteria

- [x] **Engagement scope quantities become ledger facts.** A default-off
  recipe knob declares an engagement's unit of work, comparison group, and an
  ordered funnel; the fabric plants them as additional entries in the existing
  `Engagement.facts` list with a strictly non-increasing funnel, drawing only
  from a NEW seed stream. Each rendered surface carries its unit noun rather
  than a bare numeral, so a planted count cannot match inside a currency
  amount or a date and cannot swamp the value-collision diagnostic. Every
  committed org re-derives its ledger byte-identical with the knob absent, and
  a knob-off org draws zero values from the new stream.

- [x] **A document cannot contradict its own folder about a planted
  quantity.** Documents cite scope facts through the placeholder machinery, so
  the same ledger object appears in every document that states it; a document
  cites a funnel stage only when its own date implies that stage is complete.
  Demonstrated on a synthetic engagement where an early and a late document
  both state the same stage and resolve to the same rendered surface. With the
  knob off, every committed manifest re-derives byte-identical.

- [x] **SCOPE-01 recomputes the planted quantities.** A new validator rule
  re-derives them from the charter and compares ids, values, and rendered
  surfaces exactly, and asserts the funnel is monotone and complete per
  engagement. It grandfathers by charter: skips visibly when the knob is off,
  and a knob on with the ledger mutated is a finding, never a skip. A mutated
  value yields a finding in a test.

- [x] **Scope facts become scored questions automatically.** Every planted
  scope fact emits an extraction question with a readable prompt, so a knob-on
  org gains cross-document questions where one fact is hosted by several
  documents. `emit-evals` stays byte-idempotent on all nine committed orgs and
  EVAL-01 stays green fleet-wide, because no committed org adopts the knob.

- [x] **A client-facing report briefs its client reader.** A default-off knob
  makes the status-report genre brief the engagement's client contact rather
  than the internal team only, closing the audience limb of the narrative
  blocker. Off, every committed manifest is byte-identical; on, the planned
  mentions for that genre include the client contact.

- [x] **The plan assigns a per-document skeleton.** A default-off knob makes
  the docplan deal each authored document a section skeleton from a per-genre
  pool, drawing only from a NEW seed stream, recorded without adding any field
  to `ManifestEntry`. The deal is deterministic across runs, and **no two
  consecutive same-genre documents share a skeleton**, which also means no two
  documents of one genre inside a single engagement share one. Knob off, no
  document carries a skeleton and the stream is never drawn from.

- [x] **OUT-01 recomputes the skeleton assignment** and fails on a tampered
  record, asserting the no-adjacent-repeat property. Grandfathers by charter,
  as above.

- [x] **Authoring ingest enforces the skeleton it briefed.** A deliverable
  that omits a section form its outline requires, or carries a block kind its
  outline forbids, is rejected with an actionable message; a conforming
  deliverable passes. Inert when the brief carries no outline, so knob-off
  work orders and deliverables are byte-identical.

- [x] **Skeleton variety is measured, not asserted.** A knob-off scripted
  corpus yields exactly one distinct block-shape signature per genre; a
  knob-on corpus of the same recipe yields at least `min(pool size, documents
  in that genre)`. Asserted as counts, never as a similarity threshold.

- [x] **The realism instrument gains a structural axis.** A new metric scores
  same-genre authored pairs on document structure and on positional openers,
  reported in `GENERATION-REPORT.md` beside the existing lexical score rather
  than replacing it, and byte-stable across two runs. It is never a validator
  rule and no number it produces becomes an assert. A constructed
  paraphrase-twin (same structure, disjoint vocabulary) scores high
  structurally and near zero lexically; a constructed same-words-different-
  shape pair inverts.

- [x] **The new axis is calibrated against the board's own findings.**
  `docs/REVIEW-CALIBRATION.md` records, as a dated measurement, where the
  structural axis ranks the pairs the M17 board named on the frozen exemplar
  (including the `rf:voice-1` blocker pair `d:0021`/`d:0039`, which the lexical
  metric does not flag), the pairs it misses, and the stated limit that no
  keyless proxy sees `rf:voice-3`-style paraphrased recurrence across genres.

- [x] **The turn closes without moving a fixture.** No committed org's
  ledgers, manifest, or authored prose is regenerated; `PINNED = SLUGS` is
  green at every commit including mid-turn; derived artifacts re-emit in the
  order metrics/report, then checksums, then data cards. The BACKLOG sweep
  lands: `packaging-and-archival` is closed or rewritten (its text is
  factually stale, since `pyproject.toml` now carries `[build-system]` and
  `[project.scripts]`, and a `Dockerfile` and `requirements.lock` exist), and
  `cross-document-voice` gains the structural-instrument annotation. Full
  `bin/test` (short, unit, org, flagship) passes keyless and offline.

### Context

- **Adopted from plan**
  `~/.claude/plans/consider-what-we-ve-just-witty-bentley.md` (approved
  2026-08-02). It carries the increment order, the prototype measurements
  behind the structural axis, the concrete schema shapes, and a risk
  assessment. Read it before implementing; do not re-derive decisions
  recorded there.

- **Where this came from.** M17's board returned 37 findings on the freshly
  regenerated exemplar, including two blockers. `rf:narr-1` (with
  `rf:docplaus-4`, `rf:finance-2`) is divergence: a closing report describing
  a different engagement from its own folder, invisible to the validator
  because the quantities are prose rather than ledger facts. `rf:voice-1`
  (with `rf:voice-2/4/6`) is convergence: two kickoff memos by different
  authors two years apart, the same memo re-skinned. The board's own note
  `rf:voice-7` is the diagnosis worth trusting: per-person voice works now, so
  the defect is in what each document is asked to contain.

- **What this turn does not claim, and the spec must not imply.** With no
  regeneration, the skeleton work is proven as plumbing and as block-shape
  counts under the scripted author; whether real prose stops converging is
  settled by the next generation, not here. "Impossible by construction" is an
  overclaim: a finite pool cycles, and the real guarantee is no adjacent and
  no within-engagement repeat. The skeleton work does not address
  `rf:voice-3`, a paraphrased move recurring across five genres and eight
  authors, and no keyless proxy will.

- **Two constraints that will bite silently.** `dump_json` serializes every
  model field, so adding a field to `Fact`, `Engagement`, or `ManifestEntry`
  writes a new key into every committed ledger and manifest line and breaks
  the byte pin on all nine orgs; scope quantities go in the existing `facts`
  list and the skeleton id rides in `render_params`, as M12 did for
  `noise_of`. Separately, `datacard._knob_rows` walks the charter model, so
  every new knob rewrites all nine data cards and each knob-adding increment
  must re-emit them in the same commit.

- **The exemplar is frozen this turn**, which is why doc-id anchors
  (`d:0021`/`d:0039`) are legitimate calibration checkpoints here, where M17
  had to avoid them.

- **Hard rules in force.** Airlock: `orgsmith/` never calls a model or the
  network; all tiers keyless and offline; no LLM grades an LLM in an automated
  tier. Additive evolution: knobs default off with inert schema defaults on
  existing schema ids, randomness only from new `seeds.py` streams, proven
  inert before anything adopts them. Committed fixtures are frozen and no
  carve-out is open. Nothing that is not an oracle may gate: no metric
  threshold becomes a bar, and the new axis is reported, never enforced.

- **House practices (zat.env).** Small committable increments with tests in
  the same increment; run the relevant tier after each change; do not stack
  untested changes. Verification over prompting: M16 already proved that a
  banned-construction list in authoring guidance only stops literal strings,
  which is why this turn moves the fix into the plan rather than the prompt.
  Do not reword or reorder these criteria; check off only when verified.
  Committing is local; pushing is the user's call.

- **BACKLOG overlap.** `cross-document-voice` (ACTIVE) is the direct target
  and both of its revisit criteria have fired. `event-simulation` is adjacent:
  the board's finance findings (`exemplar-has-no-2020`) are its territory and
  stay out of scope. `packaging-and-archival` is factually stale and is swept
  at close. `board-negative-control` fired again and stays open.
  `mundane-broadcast-names-a-recipient-in-the-body` is untouched here.

- **Out of scope.** Any fleet regeneration; the M18 flagship; era shocks in
  the finance model; inbound mail modelling; the DL-broadcast naming device;
  and anything asserting that authored prose improved, which is the board's
  job and needs a generation.

- **Baselines for this turn.** Suite green at `0d39895`: 16 short, 615 unit,
  228 org (+27 skipped), 65 flagship (+5 skipped); 886 collected across the
  default tiers. Nine committed orgs, `PINNED = SLUGS` fleet-wide, v2.2.0
  tagged and pushed.

---
*Prior spec (2026-07-29): M17, the answer-key turn; 13/16 criteria met, with
the verbatim-critique criterion and the two mail-demonstrator regenerations
deliberately left out of scope.*

<!-- SPEC_META: {"date":"2026-08-02","title":"M17b: the batch-boundary turn","criteria_total":12,"criteria_met":12} -->
