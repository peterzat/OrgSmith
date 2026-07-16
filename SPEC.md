# SPEC

## Spec — 2026-07-16 — M8: the firm gets a history (roster churn, behavioral finance, staffing rotation, date-scoped briefs, era naming)

**Goal:** M7 built an instrument to grade the model's prose, and it mostly
indicted the deterministic side instead: nobody is ever hired or promoted, every
expense line is a frozen percentage of revenue, the same three people staff every
engagement, and the author sees the firm's whole history no matter what the
document is dated. Give the fabric a time dimension and scope every brief to its
document's date, as recipe knobs that default off so the seven committed fixtures
stay byte-identical.

### Acceptance Criteria

- [ ] A roster-churn recipe knob (default off, randomness from a NEW `seeds.py`
  stream) gives the roster a time dimension: across the charter's date range
  people are hired, promoted, and depart, as backfills into the seats `headcount`
  declares, so `headcount` keeps its current meaning (concurrent seats, not
  people-ever) and that meaning is stated where the field is defined. With the
  knob on, the org chart stays a single acyclic tree with no dangling
  `reports_to` and no orphan, the CEO-equivalent never departs, and every
  existing validator rule (authors employed on the date they wrote, org-chart
  acyclicity, graph orphans and dangling edges) passes unchanged. A roster too
  small for the knob fails with an actionable message naming the knob, matching
  the existing pattern at `foundation/scaffold.py:219`.

- [ ] Promotions have somewhere to live: `Person` gains a title history that
  defaults empty and inert on the existing schema id, `Person.title` keeps its
  current meaning (the latest title), and a `title_at(person, date)` resolver
  returns the title held on a given date. An empty history resolves to `title`
  for every date, so all seven fixtures load and regenerate byte-identically.

- [ ] Every person brief is scoped to its document's date: `_brief_person`
  (`authoring/contexts.py:123`) resolves an internal person's title and
  employment as of the document date, the way it already resolves an external
  person's employer. A test with a synthetic charter where someone is promoted
  mid-range proves the earlier document briefs the earlier title. This is a
  precondition for the churn knob, not an independent nicety: `Person.title` is
  scalar today and briefed regardless of date, so churn without this would brief
  a 2024 title into a 2020 letter and manufacture the anachronism the knob was
  added to remove.

- [ ] A document can locate itself inside its engagement without being shown a
  fact value: the brief carries the engagement's elapsed position as of that
  document's date, computed in Python. `rf:narr-2`'s exact failure (a deck 51
  days into a 204-day program calling itself "past its midpoint") stops being
  expressible, because the author is told where it sits instead of guessing. The
  airlock holds: the brief states position, never the start date, and ingest
  still rejects a literal value written where a placeholder belongs.

- [ ] The firm overview has true material as of its date instead of inventing it.
  `rf:narr-1` has two root causes and both are addressed: `contexts.py:249` hands
  `charter.narrative` (timeless present-tense recipe prose describing the whole
  arc) verbatim to every document, and a `company_overview` briefed with one
  client fact plus a "representative client work" instruction has nothing true to
  write. The brief carries a date-scoped digest of what exists as of the document
  date, naming clients by fact id and never by value, and the instructions state
  that nothing post-dating the document may be presented as established.

- [ ] An expense-model knob on `FinanceProfile` (default preserves today's math
  byte-identically) adds a behavioral mode where categories stop moving in
  lockstep. Verified against a synthetic charter: no two categories grow at the
  same rate in a given year, at least one category is step-fixed across a
  multi-year span (`rf:finance-2`: rent is a lease cost and cannot compound 11% a
  year because fees went up), and compensation tracks headcount rather than
  revenue. Existing ledger tie-out checks still pass. What `expense_ratio` means
  in behavioral mode is documented, and a year of negative net income is recorded
  rather than crashed.

- [ ] A staffing-rotation knob (default off) varies engagement leads and teams:
  with the knob on and a large enough roster, no two engagements carry an
  identical internal participant set and no consultant appears on every
  engagement. Today `lead = available[0]` (`fabric/engagements.py:225`) is the
  same person for every engagement in the org's life. A roster too small to
  rotate degrades to today's behavior visibly rather than crashing.

- [ ] An era-naming knob (default off) draws roster and external first names from
  an era table bundled under `orgsmith/data/`, offline, with no network. With the
  knob off the `Faker` draw sequence is unchanged, which is what keeps the seven
  fixtures byte-identical: `fake` is seeded once and consumed in order by
  `_build_people` then `_build_externals`, so any added or reordered draw shifts
  every later name in the org. The name screen still runs on era-drawn names. The
  interaction with `_NICKNAMES` (an era-agnostic pool the collision and nickname
  passes draw replacement first names from) is either made era-consistent or
  documented as a limit.

- [ ] One new committed fixture: a period firm generated with churn, rotation,
  behavioral finance, and era naming all on, sized per `docs/SCALE.md` (fixtures
  prove kinds, not volume). It is the regression oracle for every knob above and
  the era-correct sibling `cindergrove-advisors` cannot become. Cindergrove is
  frozen, so era naming does not retroactively fix its known anachronism, and the
  README's note saying so stays accurate.

- [ ] The new org is boarded and the board does not gate. The six majors this
  turn targets (`rf:orgreal-1`, `rf:finance-1`, `rf:finance-2`, `rf:graph-1`,
  `rf:narr-1`, `rf:narr-2`) are verified resolved at the **ledger** level by
  deterministic tests, which is the oracle. The board's judgment of the prose is
  run and its outcome recorded; findings that persist are recorded rather than
  resolved by assertion. No metric and no board finding becomes a validator rule.

- [ ] All seven previously committed fixtures load, validate clean with an
  unchanged skip set, regenerate byte-identical structure, and re-emit their
  evals byte-identically. No ledger, manifest, or authored prose is edited or
  regenerated.

- [ ] `docs/SCALE.md` and README stop attributing the `_TARGET_WORDS` raise to
  M8. SCALE.md currently says "Until they are raised (M8)" and "Raising the
  targets is what makes the flagship affordable, which is why M8 precedes M11";
  the README's next-up list leads with era naming and realistic document lengths.
  The length work moves out, and either the milestone references are corrected or
  the renumbering is stated once and referenced.

- [ ] From a fresh checkout, `bin/test` passes all tiers offline and keyless,
  with `unit` under ~20s and `org` under ~5s. The eighth fixture's org-tier cost
  stays inside that budget (baseline: ~15ms per validated file, 107 files, 1.7s;
  `docs/SCALE.md` puts the ceiling near 330 files). CI configuration unchanged:
  still no LibreOffice.

### Context

- Adopted from the M7 proposal (2026-07-16), consumed by this entry. Scope was
  settled by explicit user decision this turn: fabric history **and** date-scoped
  briefs together (the proposal's recommended option), era naming folded in, and
  the board's negative control deferred to `BACKLOG.md`.

- **The reframe this turn acts on.** Of the board's 11 majors against
  fernhollow-partners, only 3 are about the model's writing. Four indict the
  brief and four indict the ledgers. The instrument was built to grade the model
  and mostly found that our deterministic side is too clean. "Facts are
  load-bearing" still holds; the facts are the unrealistic part. The findings are
  committed under `companies/fernhollow-partners-metadata/review/findings/` and
  each cites ledger-traceable evidence, so they can be re-checked without the
  board.

- **Why churn and date-scoping are one unit and not two.** `EmploymentSpan` and
  `_employed_at` already exist and are consumed in four modules
  (`docplan/planner.py`, `validate/rules.py`, `fabric/engagements.py`), so
  employment already has a time dimension. `Person.title` does not: it is a
  scalar, and `_brief_person` briefs it regardless of the document's date (only
  external people get `employer_at(xp, at)`). Ship churn alone and the knob
  becomes a generator of anachronisms rather than a cure for them.

- **Determinism landmines, both load-bearing.** (1) `foundation/scaffold.py:286`
  seeds one `Faker` instance and consumes it in order across `_build_people` then
  `_build_externals`; adding, removing, or reordering a single draw shifts every
  subsequent name in the org. (2) `rng(charter.seed, "foundation.scaffold")` is
  shared by the roster loop and the timeline events, so a new `rand` call in that
  stream moves committed timeline dates. Both are why every new pass must draw
  from its own stream, the way `foundation.collisions`, `foundation.nicknames`,
  and `foundation.affiliations` already do, and why knob-off must take the exact
  code path it takes today.

- **Two semantics that must be settled in writing, not assumed.** `headcount`
  currently means "people who exist"; under churn it has to mean concurrent
  seats, or the field silently changes meaning for every existing recipe.
  `expense_ratio` currently defines `expense_total` and the categories are split
  out of it (`fabric/finance.py:48-52`); a behavioral model derives the total
  from the categories instead, which inverts the relationship and leaves
  `expense_ratio` needing a stated job.

- **The airlock constrains the date-scoped digest.** Client names are facts
  (`f:E-2020-001.client`), so a digest naming them by value would leak what a
  placeholder resolves to. Note the airlock already held here: d:0007 wrote
  `{{fact:f:E-2020-001.client}}` correctly, and its invention was the unbriefed
  relationship claim ("valuation and readiness workstreams") around it. The
  digest must carry structure and fact ids, never values.

- **Low similarity is not health.** Measured twice independently in M7
  (calibration and the A/B): the corpus that scored *lower* same-genre overlap
  was the worse one. A metric can flag prose that repeats and is blind to prose
  that fails to repeat where house style requires it. Nothing this turn may turn
  a metric or a board finding into a bar.

- **Interaction to decide: the new fixture is born rendering PDFs.**
  `pdf-newline-flattening` (BACKLOG) says `render/pdf.py:90` silently flattens
  `\n` inside a paragraph while the DOCX renderer honors it, and its revisit
  criteria name "the first fixture regeneration that would re-render an affected
  PDF." An eighth fixture with PDFs is arguably that trigger, and a frozen
  fixture born with a known smear is worse than one that inherited it. Not scoped
  in as a criterion; call it before generating.

- **Charter re-dump drift, now larger.** A committed fixture's `charter.json`
  gains inert default fields when re-derived (harmless today only because frozen
  fixtures are never re-written). This turn adds at least three more such fields
  (churn, expense model, era). Carried forward from the M7 spec as still open and
  uncarried; worth a `/spec backlog` entry if it should survive this turn.

- **Scope discipline.** Deliberately out: raising `_TARGET_WORDS` together with
  clause-rich and credential-aware briefs (M9, and they are one change, not two,
  because a real engagement letter is 800-1500 words *because it has clauses*, so
  raising the target without enriching the brief buys padding); parallel
  authoring (M9, the only binding constraint per `docs/SCALE.md`); the reference
  fleet (M10); the flagship org (M11); `forge-fix` (unscheduled, and the proposal
  doubts it: a fix loop is where a critic quietly becomes a gate); the board's
  negative control (`BACKLOG.md`, `board-negative-control`).

- **Airlock unchanged.** Python still never calls a model and never touches the
  network, including the era name table, which ships as bundled data. Everything
  this turn adds is a pure stage or a brief field.

- **Frozen fixtures.** The seven committed orgs are frozen: ledgers, manifests,
  and authored prose are never edited or regenerated. Only `evals/`, `acl.json`,
  PERMISSIONS.md, and GENERATION-REPORT.md are derived and re-emittable. The
  eighth fixture is new, so it raises no frozen-fixture question; once committed,
  it joins them.

- **Open review items carried in.** CODEREVIEW.md at HEAD is 0 BLOCK / 0 WARN
  with two NOTEs: `render/__init__.py:28-48` (a `people_index` docstring claiming
  an EML-01 contract that no longer holds; no drift today, but any title- or
  org-derived eml header would make renderer and checker drift silently, and this
  turn makes titles date-dependent) and `render/pdf.py:37,64` (letterhead lines
  unescaped under `autoescape=False`; recipe-author controlled, no concrete
  vector).

- **House practices (zat.env).** Oracles beat proxies beat critics, and know
  which one carries any given claim: the ledger-level tests are the oracle here
  and the board is not. Small committable increments with tests in the same
  increment. Verify the build and existing tests pass before starting. Precision
  over recall. Hard gates only for irreversible actions; the board stays
  prompt-enforced and never gates CI. No push or remote mutation without explicit
  user instruction.

- Environment: Python 3.10-compatible (the box runs 3.10 though `.python-version`
  says 3.12); always `.venv/bin/python`.

---
*Prior spec (2026-07-16): M7 the quality instrument (review board, generation
provenance, model/effort policy); all 13 criteria met, shipped as v1.6.0.*

<!-- SPEC_META: {"date":"2026-07-16","title":"M8: the firm gets a history (roster churn, behavioral finance, staffing rotation, date-scoped briefs, era naming)","criteria_total":13,"criteria_met":0} -->
