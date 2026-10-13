# SPEC

## Spec — 2026-10-13 — M17e: the mail-org carve-out

**Goal:** Close both halves of the fleet's mail-mention device and the
live-mandate leak the M17d boards found, then regenerate the three mail orgs
once under those fixes and M17d's knobs, under a recorded, user-approved
carve-out. Every doc and README states the final state before the turn ships.

### Acceptance Criteria

- [ ] **The carve-out is opened, scoped, and closed on the record.** CLAUDE.md
  and `docs/FREEZE-LOG.md` record an M17e carve-out, approved by the user on
  2026-10-13, scoped to `ashcombe-advisory`, `hollowell-ip` and
  `meridian-actuarial` only. When the turn closes it is recorded closed,
  `PINNED = SLUGS` is enforced fleet-wide, and the other seven committed orgs'
  ledgers, manifests and authored prose are byte-identical to `61abcbd`.

- [ ] **A distribution-list broadcast names no one it was not about.** A new
  default-off mail knob gives list-addressed mail no individual recipients, so
  no colleague is a required body mention of a broadcast and the brief names
  no single recipient. With the knob off, every committed manifest, mention map
  and brief re-derives byte-identical; it draws from no existing seed stream;
  a unit test shows the effect when on; `docs/RECIPE-FORMAT.md` documents it.
  BACKLOG `mundane-broadcast-names-a-recipient-in-the-body` records it closed
  for every org that adopts it.

- [ ] **A firm overview names only finished engagements.** A new default-off
  knob limits an overview's client placeholders, in both the plan's required
  facts and the brief's digest, to engagements that ended before its date, and
  an overview dated before any engagement ends claims no client work. Inert
  when off, unit-tested when on, documented in `docs/RECIPE-FORMAT.md`.

- [ ] **The three mail orgs are regenerated once, through the live airlock.**
  Each is generated wholesale on `claude-opus-5-5` at `xhigh` with
  `mail.exempt_recipient_mentions`, the new list-mail knob, the overview
  knob, `business_calendar.engagement_starts`, `engagements.oversight_titles`
  and a declared 2020 `finance.era_shocks` on. Each validates clean, scores
  100% on every eval split by construction, has every planted fact hosted,
  and re-freezes under `PINNED = SLUGS` with its data card,
  `GENERATION-REPORT.md`, `evals/`, `acl.json`, PERMISSIONS.md, baselines and
  checksums re-emitted.

- [ ] **The mail devices are measured gone, not assumed gone.** For each
  regenerated org, a count reported in the write-up: planned person-to-person
  mail mentions of a recipient (expected zero), planned colleague mentions on
  list-addressed mail (expected zero), and how many authored mail bodies still
  name a recipient in full by the author's choice. The same counts for the
  committed versions are reported beside them.

- [ ] **Each regenerated org gets a full six-dimension board, read-only
  proven.** Every board runs with `review --digest` recorded before dispatch
  and verified after. Findings ship beside each org, unflattering ones
  included, and the write-up compares each org's blocker and major counts with
  its pre-carve-out board, labelled as a different corpus rather than a
  controlled comparison.

- [ ] **Every doc and README states the final state.** README (fleet table,
  vintages, picker and fixture tables, every quoted finding about the three
  orgs, the mail-artifact section, totals, roadmap), CLAUDE.md, FREEZE-LOG,
  TESTING (counts and measured tier times), `docs/RECIPE-FORMAT.md`, BACKLOG
  (closed entries recorded, new findings filed), CHECKSUMS, every data card,
  and the baselines and distributions dashboards. No doc still describes the
  three orgs as carrying the mail device, unless a measured count says so.

- [ ] **It ships.** Version bumped, full `bin/test` passes keyless and offline
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

<!-- SPEC_META: {"date":"2026-10-13","title":"M17e: the mail-org carve-out","criteria_total":8,"criteria_met":0} -->
