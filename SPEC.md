# SPEC

## Spec — 2026-10-13 — M17e: the mail-org carve-out

**Goal:** Close both halves of the fleet's mail-mention device and the
live-mandate leak the M17d boards found, then regenerate the three mail orgs
once under those fixes and M17d's knobs, under a recorded, user-approved
carve-out. Every doc and README states the final state before the turn ships.

### Acceptance Criteria

- [x] **The carve-out is opened, scoped, and closed on the record.** CLAUDE.md
  and `docs/FREEZE-LOG.md` record an M17e carve-out, approved by the user on
  2026-10-13, scoped to `ashcombe-advisory`, `hollowell-ip` and
  `meridian-actuarial` only. When the turn closes it is recorded closed,
  `PINNED = SLUGS` is enforced fleet-wide, and the other seven committed orgs'
  ledgers, manifests and authored prose are byte-identical to `61abcbd`.

- [x] **A distribution-list broadcast names no one it was not about.** A new
  default-off mail knob gives list-addressed mail no individual recipients, so
  no colleague is a required body mention of a broadcast and the brief names
  no single recipient. With the knob off, every committed manifest, mention map
  and brief re-derives byte-identical; it draws from no existing seed stream;
  a unit test shows the effect when on; `docs/RECIPE-FORMAT.md` documents it.
  BACKLOG `mundane-broadcast-names-a-recipient-in-the-body` records it closed
  for every org that adopts it.

- [x] **A firm overview names only finished engagements.** A new default-off
  knob limits an overview's client placeholders, in both the plan's required
  facts and the brief's digest, to engagements that ended before its date, and
  an overview dated before any engagement ends claims no client work. Inert
  when off, unit-tested when on, documented in `docs/RECIPE-FORMAT.md`.

- [x] **The three mail orgs are regenerated once, through the live airlock.**
  Each is generated wholesale on `claude-opus-5-5` at `xhigh` with
  `mail.exempt_recipient_mentions`, the new list-mail knob, the overview
  knob, `business_calendar.engagement_starts`, `engagements.oversight_titles`
  and a declared 2020 `finance.era_shocks` on. Each validates clean, scores
  100% on every eval split by construction, has every planted fact hosted,
  and re-freezes under `PINNED = SLUGS` with its data card,
  `GENERATION-REPORT.md`, `evals/`, `acl.json`, PERMISSIONS.md, baselines and
  checksums re-emitted.

- [x] **The mail devices are measured gone, not assumed gone.** For each
  regenerated org, a count reported in the write-up: planned person-to-person
  mail mentions of a recipient (expected zero), planned colleague mentions on
  list-addressed mail (expected zero), and how many authored mail bodies still
  name a recipient in full by the author's choice. The same counts for the
  committed versions are reported beside them.

- [x] **Each regenerated org gets a full six-dimension board, read-only
  proven.** Every board runs with `review --digest` recorded before dispatch
  and verified after. Findings ship beside each org, unflattering ones
  included, and the write-up compares each org's blocker and major counts with
  its pre-carve-out board, labelled as a different corpus rather than a
  controlled comparison.

- [x] **Every doc and README states the final state.** README (fleet table,
  vintages, picker and fixture tables, every quoted finding about the three
  orgs, the mail-artifact section, totals, roadmap), CLAUDE.md, FREEZE-LOG,
  TESTING (counts and measured tier times), `docs/RECIPE-FORMAT.md`, BACKLOG
  (closed entries recorded, new findings filed), CHECKSUMS, every data card,
  and the baselines and distributions dashboards. No doc still describes the
  three orgs as carrying the mail device, unless a measured count says so.

- [x] **It ships.** Version bumped, full `bin/test` passes keyless and offline
  across all four tiers, and the branch is pushed after `/codereview` passes.

### Context

- **Direction, decided at the user's instruction.** The user approved the
  carve-out ("1. approved") and left the next turn to me ("2. your call",
  "continue autonomously"), asking that docs and READMEs be fully updated
  before the turn exits. M18 is out of scope: at ~334 authoring batches it
  exceeds this session's budget. A carve-out regeneration is also the
  cheapest place to exercise knobs, so the turn lands two more first and
  adopts them in the same regeneration rather than regenerating twice.

- **Why the list-mail fix is a planner change, not an exemption.**
  `plan_mentions` already exempts a person-to-person recipient
  (`mail.exempt_recipient_mentions`) because the To header names them. It
  deliberately does not exempt list mail, whose To header is the list address.
  The device's cause is upstream: `_emit_mundane` gives a list broadcast one
  or two randomly drawn colleagues as participants, and the planner then
  requires their names in the body. The draw must stay (it is on the existing
  `docplan.email.mundane` stream); only what the knob does with it may change.

- **Why the overview fix touches two places.** `_emit_firm_periodic` writes the
  overview's required `facts_refs` from engagements started by its date, and
  `contexts._firm_digest` briefs the same set. They must agree or ingest
  rejects the brief's own deliverable.

- **The M17d knobs each regenerated org adopts**, with values fixed in its
  recipe: oversight titles are the senior titles the recipe already declares;
  the 2020 shock is sized for the sector and named in the recipe comment.
  `scope_by_service` and `outline_variety` are not adopted: they need
  per-recipe vocabulary and pool design this turn does not do.

- **Serialization and re-emission, unchanged.** New charter fields rewrite
  every `charter.json` and data card (derived). Re-emission order: `charter`,
  `report`, `tools/checksums.py` (only after the orgs are committed: it reads
  `git ls-files`, and refuses an org with none), then `data-card` for every org.

- **Hard rules in force.** Airlock; additive evolution with new seed streams;
  grandfather by charter; nothing that is not an oracle may gate; the board is
  read-only and proves it. Committing is local; pushing goes through
  `/codereview`.

- **House practices (zat.env).** Small committable increments with tests;
  verify commits in a clean worktree while an uncommitted org is in
  `companies/`; gate every commit on the test exit status, never on a piped
  summary; revert rather than edit a test to accommodate a regression.

- **BACKLOG.** Engaged: `mail-orgs-recipient-mention-carve-out` (executed),
  `mundane-broadcast-names-a-recipient-in-the-body`,
  `overview-names-live-mandates`, `mail-audience-internal-vs-external`.
  Annotated if touched: `exemplar-has-no-2020`, `mention-filler-acl-seam`,
  `board-yield-at-scale`. Out of scope: everything else, including M18.

- **Baselines.** Suite green at `61abcbd`: 19 short, 824 unit, 261 org (+30
  skipped), 71 flagship (+5 skipped). Ten committed orgs, v2.4.0, pushed.

---
*Prior spec (2026-10-13): M17d, M18 readiness; 13/13. Five default-off knobs,
a pre-registered Opus 5.5 probe that found no reason to regenerate for the
model, a board recall probe that hit a ceiling, and a tenth org; pushed at
`61abcbd`.*

### Proposal (2026-10-13)

**What happened.** M17e met 8 of 8. Two default-off knobs landed and were
proven inert (`mail.broadcasts_address_the_list`, `4fd9465`;
`doc_culture.overview_cites_finished_work`, `061da37`). The user-approved
carve-out (`0ae6e3f`) regenerated `ashcombe-advisory`, `hollowell-ip` and
`meridian-actuarial` once on `claude-opus-5-5`: 198 documents, 39 batches,
zero ingest rejections, all validating clean (`ba969f8`). The device is
measured gone: planned recipient mentions 85/46/62 to 0, planned list mentions
4/3/3 to 0, direct bodies naming a recipient 39/39, 20/20, 24/24 to 1, 2, 1.
Six-dimension boards on opus-5-5 found 0 blockers and 13, 14, 14 majors. They
cannot be compared with the pre-carve-out boards, which ran on other reviewer
models (7 and 9 findings became 40 and 38), so the write-up compares
recurrence. The carve-out closed the same day with the seven other orgs
byte-identical apart from derived files. v2.5.0, pushed at `9dffb43`, CI green.

Three things this turn learned matter more than its counts:

- **The boards found generator defects with verified code causes, and two of
  them came from knobs.** `thread-split-across-concurrent-batches`: 11 of 12
  multi-message threads split across two work orders, and every thread
  contradiction sits at a split. `oversight-senior-takes-the-junior-slot`:
  M17d's appended senior lands where the planner reads the most junior member
  (minutes by a senior 0/8 to 6/8 on ashcombe). And the mail knobs, by removing
  forced mentions, fed `mention-filler-acl-seam`: hollowell's major ACL finding
  is a person the top-up moved out of mail and into a memo she cannot read.
- **An answer-key defect, fleet-wide.** 11 of 11 departed staff keep an
  open-ended `works_at` edge in `graph_expected.json`
  (`graph-departures-have-no-end-edge`).
- **Two silent passes caught by the turn's own checks.** The unanswerable-question
  test lost its only committed host, and the data-card tests are collected
  per existing card. The first was re-hosted. The second gained a guard test.
  Diffing the org tier's skip reasons against the pre-turn commit is what found
  them. Code review then found a third, a unit test that asserted nothing,
  which `/codefix` repaired.

**Questions and directions.**

1. **Fix the answer key and the batching before generating anything else.**
   `graph-departures-have-no-end-edge` is an eval-correctness defect and the
   highest-priority class. Decide which artifact owns the end date, then land
   the fix as a fabric knob, or fix it in the emitter with a recorded
   divergence. `thread-split-across-concurrent-batches` moves no frozen
   artifact: hold a continuation batch until its parent ingests, and brief it
   the thread's earlier messages. Both are small, testable without a model,
   and M18 depends on both.
2. **Land the oversight placement fix as a default-off knob now or with M18?**
   No committed org would adopt it without a carve-out, but M18 would adopt it
   at birth, and so would any new org.
3. **Is M18 next after that, or one more generator turn?** The M17e boards
   added a cluster of generator-level realism gaps that every org shares
   (`corpus-has-no-specifics`, one officer per client, firm-only threads,
   `mail-surface-ignores-send-time-and-audience`). M18 at ~334 batches would
   carry all of them at 10x scale. The alternative is to fix the cheapest two
   first, so M18 is not boarded into the same findings.
4. **Should board counts ever be reported across reviewer models?** This turn
   says no (`docs/REVIEW-CALIBRATION.md`). A small re-board of one frozen org on
   opus-5-5 would turn the confound into a measurement, at six reviewers' cost.

**Revisit candidates.**

- `graph-departures-have-no-end-edge`: its revisit criterion is "next turn".
- `thread-split-across-concurrent-batches`: "before any further generation run".
- `mention-filler-acl-seam`: fired again on two more orgs, and this turn's
  knobs fed it. Two more entries' criteria fired this turn
  (`noise-version-chain-copies-time-anchored-text` and
  `kickoff-and-onboarding-dated-after-the-start-they-anticipate`, each on a
  second org); see BACKLOG.md.

### Backlog Sweep
- **Delete:** `mail-orgs-recipient-mention-carve-out`: executed and closed this
  turn, and the record lives in `docs/FREEZE-LOG.md`.

<!-- SPEC_META: {"date":"2026-10-13","title":"M17e: the mail-org carve-out","criteria_total":8,"criteria_met":8} -->
