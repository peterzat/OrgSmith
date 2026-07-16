# SPEC

## Spec — 2026-07-16 — M8: the firm gets a history (roster churn, behavioral finance, staffing rotation, date-scoped briefs, era naming)

**Goal:** M7 built an instrument to grade the model's prose, and it mostly
indicted the deterministic side instead: nobody is ever hired or promoted, every
expense line is a frozen percentage of revenue, the same three people staff every
engagement, and the author sees the firm's whole history no matter what the
document is dated. Give the fabric a time dimension and scope every brief to its
document's date. The freeze on `companies/` is lifted this turn, so these arrive
as the generator's only behavior rather than as knobs defaulting off.

### Acceptance Criteria

- [x] The roster has a time dimension. Across the charter's date range people are
  hired, promoted, and depart, as backfills into the seats `headcount` declares,
  so `headcount` means concurrent seats rather than people-ever and that meaning
  is stated where the field is defined. `Person` gains a title history and a
  `title_at(person, date)` resolver returns the title held on a given date;
  `Person.title` keeps its current meaning (the latest title). The org chart
  stays a single acyclic tree with no dangling `reports_to` and no orphan, the
  CEO-equivalent never departs, and every existing validator rule (authors
  employed on the date they wrote, org-chart acyclicity, graph orphans and
  dangling edges) passes unchanged. Randomness comes from a NEW `seeds.py`
  stream.

- [x] **Churn degrades, it does not crash, at the smallest roster a recipe can
  declare.** This is what the freeze lift changes: with the knob defaulting off,
  a roster too small could fail with an actionable message and no committed
  recipe would ever see it. On by default, that message becomes a crash on a
  legitimate 5-person recipe — every recipe in the repo is 5-6 people. Verified
  against a synthetic charter at the schema minimum (`headcount` total 2): the
  pipeline completes and the degradation is visible in the ledger, not inferred.

- [x] Every brief is scoped to its document's date, and three separate
  fabrications stop being expressible:
  - `_brief_person` (`authoring/contexts.py:123`) resolves an internal person's
    title and employment as of the document date, the way it already resolves an
    external person's employer via `employer_at`. A synthetic charter where
    someone is promoted mid-range proves the earlier document briefs the earlier
    title.
  - The brief carries the engagement's elapsed position as of the document's
    date, computed in Python, so `rf:narr-2` (a deck 51 days into a 204-day
    program calling itself "past its midpoint") cannot recur. The brief states
    position, never the start date.
  - The firm overview gets a date-scoped digest of what exists as of its date,
    naming clients by fact id and never by value, with instructions stating that
    nothing post-dating the document may be presented as established. This
    replaces `contexts.py:249` handing `charter.narrative` (timeless
    present-tense recipe prose describing the whole arc) verbatim to every
    document, which is one of `rf:narr-1`'s two root causes; the other is a
    `company_overview` briefed with one client fact and told to write
    "representative client work" with nothing true to say.

  The airlock holds throughout: ingest still rejects a literal value written
  where a placeholder belongs.

- [x] Expenses stop moving in lockstep, and behavioral is the **only** mode —
  no legacy path is carried alongside it. Verified against a synthetic charter:
  no two categories grow at the same rate in a given year, at least one category
  is step-fixed across a multi-year span (`rf:finance-2`: rent is a lease cost
  and cannot compound 11% a year because fees went up), and compensation tracks
  headcount rather than revenue. Existing ledger tie-out checks (FIN-01, FIN-02)
  still pass. `expense_ratio` no longer defines `expense_total` (the categories
  do), so its remaining job is stated in the schema where it is defined. A year
  of negative net income is recorded rather than crashed.

- [x] Engagement leads and teams vary. With a roster large enough to rotate, no
  two engagements carry an identical internal participant set and no consultant
  appears on every engagement. Today `lead = available[0]`
  (`fabric/engagements.py:225`) is the same person for every engagement in the
  org's life. A roster too small to rotate degrades visibly rather than crashing.

- [x] Roster and external first names are drawn era-appropriately from a table
  bundled under `orgsmith/data/`, offline, with no network. The name screen
  (NAME-01) still runs on era-drawn names. The interaction with `_NICKNAMES` (an
  era-agnostic pool the collision and nickname passes draw replacement first
  names from) is either made era-consistent or documented as a limit.

- [x] **A single generation is still reproducible, and the seeds discipline that
  makes it so is not weakened by the freeze lift.** Cross-version byte-identity
  is gone; same-seed determinism is not. Every pass added this turn draws from
  its own NEW named `seeds.py` stream rather than sharing
  `rng(charter.seed, "foundation.scaffold")` with the roster loop and the
  timeline events. Verified by deriving the same recipe twice into two
  destinations and diffing: byte-identical charter, foundation, ledgers, and
  manifest.

- [x] **The `org` tier survives the freeze lift with its fault-injection property
  intact.** Behavioral finance moves `finance.json` and churn moves
  `foundation.json`, so three of `test_org_regen.py`'s four assertions cannot
  pass against the seven committed fixtures and must not be papered over.
  `dev-mini` is regenerated with this turn's behavior and becomes the sole
  byte-pinned fixture until the fleet resets in M11; the other six stay committed
  and keep validating clean, scoring their eval ground truth at 100%, and
  reporting complete, with the reason the pin is scoped recorded in TESTING.md.
  `test_every_committed_fixture_has_a_recipe` still holds. The fault injection
  TESTING.md documents (`+ 1` on every expense line in `fabric/finance.py`) still
  fails `test_org_regen.py`; re-run it rather than assuming it.

- [x] The six board majors this turn targets (`rf:orgreal-1`, `rf:finance-1`,
  `rf:finance-2`, `rf:graph-1`, `rf:narr-1`, `rf:narr-2`) are verified resolved
  at the **ledger** level by deterministic tests, which is the oracle. The board
  is run against the regenerated `dev-mini` and its outcome recorded; findings
  that persist are recorded rather than resolved by assertion. No metric and no
  board finding becomes a validator rule or a gate.

- [x] The roadmap renumbering is stated once in this file and referenced
  everywhere else, and no document still attributes work to a milestone that no
  longer owns it. `docs/SCALE.md` currently says "Until they are raised (M8)" and
  "Raising the targets is what makes the flagship affordable, which is why M8
  precedes M11"; the README's next-up list leads with era naming and realistic
  document lengths and says the fleet is six. Document length moves to M9,
  parallel authoring to M10, the fleet to M11, the flagship to M12. README and
  SCALE.md stop describing knobs that default off and fixtures that stay
  byte-identical, because neither is true after this turn.

- [x] From a fresh checkout, `bin/test` passes all tiers offline and keyless,
  with `unit` under ~20s and `org` under ~5s. CI configuration unchanged: still
  no LibreOffice. Baseline at adoption: 335 passing (12 short / 272 unit / 51
  org) in 21.9s.

### Context

- **This is the M8 spec re-scoped in place, not a new milestone.** Same unit of
  work; a user decision this turn lifted the freeze on `companies/` and made v2.0
  a breaking window. Thirteen criteria became ten, and the three that vanished
  were all ceremony the freeze demanded: knobs defaulting off, seven fixtures
  regenerating byte-identically, and an eighth committed fixture that M11 would
  have thrown away. Full arc:
  `~/.claude/plans/we-ve-come-a-long-synchronous-llama.md`.

- **The roadmap renumbering, stated once.** M8 (this turn) the firm gets a
  history → **M9** the corpus gets a business (the document supply model: a genre
  registry with drivers and cadences, folder taxonomy beyond
  `Engagements/Finance/Firm`, real email cadence, and realistic per-genre
  document lengths, which land here because length is a property of the genre
  table) → **M10** scale infrastructure (parallel authoring, the O(n²) fixes, the
  review sampler, the org-tier split, run-log measurement) → **M11** the new
  fleet (four recipes, the seven retire, the byte-pin is restored fleet-wide) →
  **M12** the exemplar (~800 documents) and v2.0. Old M9 split: lengths into M9,
  parallel authoring into M10. Old M10 → M11, old M11 → M12.

- **What lifting the freeze does and does not buy.** It removes: `default off` on
  every knob, both code paths for expenses, the pinned `Faker` draw order, and
  byte-identity against committed artifacts. It does **not** remove: the airlock,
  same-seed determinism, the per-pass `seeds.py` stream discipline, or the
  requirement that the seven fixtures keep validating clean. Determinism inside a
  run is what makes a generation reproducible and is untouched; only agreement
  with *previously committed bytes* is surrendered, and only until M11 re-pins it.

- **What the scoped pin costs, stated rather than hidden.** `cf9f02c` proved by
  fault injection that `test_org_regen.py` is the only thing catching a change
  that moves every fixture *consistently* — "exactly what a reordered `Faker`
  draw or a re-used `rng` stream does" — and that deriving twice and comparing
  cannot catch it, because it is green either way. Scoping the pin to `dev-mini`
  keeps that property on one recipe and gives it up on six. That is the real
  price of the freeze lift, it is temporary, and it is an argument for M11
  landing promptly rather than for skipping this turn.

- **The reframe this turn acts on.** Of the board's 11 majors against
  fernhollow-partners, only 3 are about the model's writing. Four indict the
  brief and four indict the ledgers. The instrument was built to grade the model
  and mostly found that our deterministic side is too clean. "Facts are
  load-bearing" still holds; the facts are the unrealistic part. The findings are
  committed under `companies/fernhollow-partners-metadata/review/findings/` and
  each cites ledger-traceable evidence, so they can be re-checked without the
  board.

- **Why churn and date-scoping are one unit and not two.** `EmploymentSpan` and
  `_employed_at` already exist and are consumed in `docplan/planner.py`,
  `validate/rules.py`, and `fabric/engagements.py`, so employment already has a
  time dimension. `Person.title` does not: it is a scalar, and `_brief_person`
  briefs it regardless of the document's date (only external people get
  `employer_at(xp, at)`). Ship churn alone and it becomes a generator of
  anachronisms rather than a cure for them.

- **The determinism landmines are still live, for a different reason.**
  `foundation/scaffold.py:286` seeds one `Faker` and consumes it in order across
  `_build_people` then `_build_externals`; `rng(charter.seed,
  "foundation.scaffold")` is shared by the roster loop and the timeline events.
  The freeze lift means reordering those no longer breaks a committed fixture —
  but a new pass drawing from a shared stream still couples two unrelated things,
  so that the next change to one silently moves the other. Draw from a new named
  stream because it is right, not because a test says so.

- **Two semantics settled in writing, not assumed.** `headcount` becomes
  concurrent seats. `expense_ratio` stops defining `expense_total` (the
  categories now derive it, inverting today's `fabric/finance.py:48-52`
  relationship) and needs a stated job or an explicit removal.

- **The airlock constrains the date-scoped digest.** Client names are facts
  (`f:E-2020-001.client`), so a digest naming them by value would leak what a
  placeholder resolves to. The airlock already held here: d:0007 wrote
  `{{fact:f:E-2020-001.client}}` correctly, and its invention was the unbriefed
  relationship claim ("valuation and readiness workstreams") around it. The
  digest carries structure and fact ids, never values.

- **Low similarity is not health.** Measured twice independently in M7
  (calibration and the A/B): the corpus that scored *lower* same-genre overlap
  was the worse one. A metric can flag prose that repeats and is blind to prose
  that fails to repeat where house style requires it. Nothing this turn may turn
  a metric or a board finding into a bar.

- **BACKLOG interactions.** `charter-redump-drift`: the freeze lift resolves the
  urgency (a re-dump dirtying a frozen fixture stops mattering when the fixture
  is not frozen), but the decision it names still wants making at M11 when the
  pin is restored fleet-wide; `test_committed_charter_redump_stays_additive`
  keeps passing this turn because new knobs are *gained* keys, not moved values.
  `pdf-newline-flattening`: its "live as of the M8 spec" note is now stale —
  M8 no longer commits an eighth fixture, so the trigger it named evaporates and
  the fix moves to M9, which re-renders everything anyway. `board-negative-control`
  stays deferred; its revisit criteria name a corpus whose ground truth the
  reader has not read, which is M12. `email-thread-spacing` and
  `org-tier-scaling-plan` are M9 and M10 respectively. None are in scope here.

- **Scope discipline.** Deliberately out: the genre registry and document lengths
  (M9 — and lengths are not a separate change from clause-rich briefs, because a
  real engagement letter is 800-1500 words *because it has clauses*, so raising
  the target without enriching the brief buys padding); parallel authoring (M10);
  the new fleet (M11); the exemplar (M12); `forge-fix` (unscheduled, and doubted:
  a fix loop is where a critic quietly becomes a gate).

- **Airlock unchanged and absolute.** Python still never calls a model and never
  touches the network, including the era name table, which ships as bundled data.
  Everything this turn adds is a pure stage or a brief field.

- **Open review items carried in.** CODEREVIEW.md at HEAD is 0 BLOCK / 0 WARN
  with two NOTEs, one of which this turn makes live: `render/__init__.py:28-48`
  is a `people_index` docstring claiming an EML-01 contract that no longer holds,
  and this turn makes titles date-dependent, which is when renderer and checker
  could drift silently. The other is `render/pdf.py:37,64` (letterhead lines
  unescaped under `autoescape=False`; recipe-author controlled, no concrete
  vector).

- **House practices (zat.env).** Oracles beat proxies beat critics, and know
  which one carries any given claim: the ledger-level tests are the oracle here
  and the board is not. Verification quality is the ceiling on what gets built,
  so invest there before prompts. Precision over recall — an empty board report
  is a good outcome. Small committable increments with tests in the same
  increment; verify the build and existing tests pass before starting. Hard gates
  only for irreversible actions; the board stays prompt-enforced and never gates
  CI. Prompts must earn their keep: an instruction that cannot name the failure
  mode it prevents is the first to delete. No push or remote mutation without
  explicit user instruction.

- Environment: Python 3.10-compatible (the box runs 3.10 though `.python-version`
  says 3.12); always `.venv/bin/python`.

---
*Prior spec (2026-07-16): M7 the quality instrument (review board, generation
provenance, model/effort policy); all 13 criteria met, shipped as v1.6.0.*

### Proposal (2026-07-16)

**What happened.** M8 gave the fabric a time dimension and shipped as v1.7.0,
the second step of the v2.0 arc. The freeze on `companies/` was lifted by user
decision, which collapsed the spec from 13 criteria to 11 (the byte-identical
and default-off ceremony went away) and made the realism knobs default on with
one code path. Landed, each with tests in the same increment: roster churn
(`RosterChurn`, hires/promotions/departures, `headcount` now means concurrent
seats), `Person.title_history` + `title_at`, date-scoped person briefs,
engagement elapsed position and a date-scoped firm digest in the brief,
behavioral finance (categories drive the total, `expense_ratio` calibrates the
first full year only, losses are recordable), staffing rotation, and
era-appropriate names from a bundled offline table. `dev-mini` was regenerated
end to end (Opus 4.8 at max effort) as the sole byte-pinned fixture; the other
six stay committed and validate clean until the M11 fleet reset. The board read
the regenerated `dev-mini` and confirmed all six targeted majors are gone,
surfacing new findings instead. Suite: 367 passing, ~19s.

**What we learned, that changes the next turns.** The document count is not a
knob and never was: the planner emits a fixed `2E + 7 + pptx + eml` skeleton
with three genres hard-capped at 2, so scaling documents is a planner rewrite,
not a recipe number. Behavioral finance also exposed that every committed
recipe's `growth_rate` is incoherent with its fixed `headcount` (a firm doubles
fees without hiring), which the old lockstep model hid. Both are M9/M11
substance and are in BACKLOG.

**Questions and directions for M9 (the document-supply model).** This is the
keystone the whole v2.0 arc waits on. A genre registry with per-genre drivers
(per-engagement-recurring, per-hire, per-year, per-vendor, firm-periodic),
cadences, folders beyond `Engagements/Finance/Firm`, and realistic per-genre
lengths, so `target_docs` becomes honest and a firm's share looks like a
business rather than a fixed skeleton. Open questions: does `target_docs` drive
the registry or does the registry derive it; how does `format_mix`'s
exact-sum constraint survive when format follows genre; and where do the two
render/authoring findings this turn produced get settled, since M9 re-renders
every letter. Both are in BACKLOG and both are on the engagement letter:
`letterhead-duplicated-in-letters` (major, the firm name printed twice) and
`pdf-newline-flattening` (the addressee smear).

**Revisit candidates for M9.** `letterhead-duplicated-in-letters` and
`pdf-newline-flattening` — both are letter-rendering findings on the genre M9
rebuilds, and settling the letterhead convention is naturally part of the
registry work. `email-thread-spacing` — real thread cadence is a per-genre
cadence question, which is exactly what the registry models.

<!-- SPEC_META: {"date":"2026-07-16","title":"M8: the firm gets a history (roster churn, behavioral finance, staffing rotation, date-scoped briefs, era naming)","criteria_total":11,"criteria_met":11} -->
