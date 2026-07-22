# SPEC

## Spec — 2026-07-21 — M14: email realism (thread mechanics + mailbox ecology) and the email-first pilot

**Goal:** Ship the realism wave's most important improvement: email that reads
like a real mailbox. Thread mechanics (minute-granularity timing, In-Reply-To /
References chains, quoted history, To/Cc, promotion-aware signatures, varied
depth) plus mailbox ecology (a mundane internal genre, MIME transmittal
attachments, distribution lists) all land under a new optional
`doc_culture.mail` block that leaves every committed artifact byte-identical
when off. Then prove it in one committed, boarded pilot org whose fixtures
exercise `k>0` threads for the first time, closing the standing
`email-threads-unproven-in-fixtures` debt with a fixture rather than an
argument.

### Acceptance Criteria

- [x] **Additive and inert by default.** A new optional `MailCulture` block on
  `DocCulture` (no `doc-culture` / `docplan-manifest` / `foundation` schema id
  bump) and a `Foundation.distribution_lists` field defaulting empty. All eight
  committed fleet orgs plus `calderwood-partners` load, validate, re-serialize,
  and regenerate byte-identically; `PINNED = SLUGS` stays green fleet-wide; a
  knob-off charter draws zero values from every new `seeds.py` stream
  (`docplan.email.hours`, `docplan.email.threads`, `docplan.email.mundane`,
  `docplan.email.attach`, `foundation.dls`), proven by a test that regenerates a
  committed org and asserts byte-identity, not merely validity. Every new
  validator check skips *visibly* on a knob-off charter and fails on
  knob-on-with-artifact-missing (grandfather by charter, per CLAUDE.md).

- [x] **Thread timing.** Under `doc_culture.mail`, a thread's messages carry
  strictly increasing minute-granularity send datetimes inside the recipe's
  declared business hours, with same-day replies occurring; every `.eml` `Date`
  header recomputes exactly from ledgers plus manifest through the single shared
  `expected_headers` function. Same-day replies in one thread render to distinct,
  non-colliding filenames (collision test). Knob-off orgs keep the fixed 09:00
  UTC `Date` header and the committed fleet revalidates unchanged.

- [x] **Threading headers, one shared twin.** Replies carry `In-Reply-To` naming
  the predecessor's `Message-ID` and an ordered `References` chain; thread
  openers carry neither; reply subjects read `RE: {subject}` and openers carry
  the plain subject. The renderer and the validator compute these from one shared
  `expected_headers` function (no twin drift); a hand-tampered threading header
  is a validator *failure*, not a skip. Proven by a unit test that renders a
  reply manifest entry and validates the rendered bytes against the same shared
  expectation.

- [x] **Derived quoted history, zero tokens, byte-stable.** A reply renders a
  derived quoted tail (`On {date}, {name} wrote:` followed by the predecessor's
  quote-prefixed resolved body) at render time with no model pass, byte-identical
  on re-render. Any planted-fact surface a quoted tail carries is owned by that
  reply's own manifest entry (`facts_refs` propagation), so the extraction and
  retrieval eval suites still score 100% by construction on the pilot.

- [x] **Deterministic To/Cc partition.** Recipients split into To and Cc
  deterministically from ledger ground truth (departed-as-of-send-date people
  handled, not crashed); at least one committed pilot thread has a Cc set
  disjoint from its To set; the people-graph and visibility eval suites stay
  exact on the pilot.

- [x] **Promotion-aware signature blocks.** Knob-on mail ends in a deterministic
  signature block (name, title as of the send date, phone) sourced from
  `foundation.json` and never authored, so a promotion changes a person's
  signature mid-corpus. The model still cannot author a signature block (the
  ingest rejection of authored signature facts stands); signature content
  recomputes in validation.

- [x] **Varied thread depth from a new stream.** Thread depth varies across
  engagements, drawn from `docplan.email.threads` rather than a uniform
  round-robin, and the pilot ships at least one thread of depth 4 or more.

- [x] **A mundane internal-email genre.** A new non-engagement email genre
  (scheduling / logistics / admin) is planned across the recipe date range under
  the knob, authored short, carrying name mentions but no engagement facts, and
  acting as a retrieval/extraction distractor: it appears in the `distractors`
  and `full` eval splits and is never a retrieval or extraction *answer*. (It
  remains a visibility answer, exactly, because it is a readable document, so it
  does appear in `core` via the visibility suite; that is correct, not a leak.)
  A knob-off charter plans none of it.

- [x] **MIME transmittal attachments.** At least one committed pilot transmittal
  email carries a real MIME attachment whose bytes are identical to a rendered
  share document; the manifest owns the email→attachment relationship; `FILE-01`
  still opens the `.eml`, `MAN-01` (manifest 1:1 with share files) still holds
  because the attachment lives inside the `.eml` and is not an extra share file;
  and any attachment-carried planted fact is attributed in the derived eval
  suites.

- [x] **Distribution lists as a derived ledger.** Distribution-list objects
  (name, address, members) live in a derived `ledger/distribution_lists.json`,
  NOT on `Foundation` (a field on the frozen, non-re-emittable foundation would
  break the byte pin criterion 1 requires; the DL ledger is derived from charter
  + roster like `acl.json`, so committed foundations stay byte-identical and the
  ledger re-emits). Knob-on mundane mail can address a DL (the To header is the
  list), and the visibility ground truth expands DL membership deterministically
  so every current member of a DL-addressed message's list can read it (DL-01).
  Scope: address plus flat members plus visibility expansion; no nesting, no
  moderation semantics.

- [x] **The email-first pilot, committed and boarded.** A new pilot org
  (`ashcombe-advisory`, ~12 seats, ~5-6 engagements, ~60-75 docs) is generated
  live through the airlock, committed, and browsable: `.eml` is 50% or more of
  its authored documents, it ships 5 or more threads with a max depth up to ~8,
  and its `format_mix.eml` sits well above its engagement count. It validates
  green (new rules skipping visibly where the charter leaves a sub-knob off),
  scores 100% on all four eval splits, is run through `/forge-review` with the
  board findings published in its `GENERATION-REPORT.md`. This closes BACKLOG
  `email-threads-unproven-in-fixtures` with a fixture.

- [x] **Additive proof, docs, and the carve-out.** Full `bin/test` is green on
  all tiers, keyless and offline, with the byte pin green on every previously
  committed org. The project `CLAUDE.md` gains the M13-M16 frozen-fixture
  carve-out declaration naming the pilot as a wave workbench; `docs/RECIPE-FORMAT.md`
  documents the `doc_culture.mail` block; the README's "no committed fixture
  exercises threads" / "all 11 `.eml` files are Email 1" language is corrected
  (it becomes false this turn); and BACKLOG `event-simulation` is annotated that
  email work advances process realism without the `fabric` rewrite.

### Context

- **Adopted from the M14 section of `~/.claude/plans/we-ve-gotten-to-a-squishy-torvalds.md`**,
  the approved M13-M16 realism wave. The plan lists 12 candidate outcomes and the
  exact touchpoints; the criteria above reformulate and consolidate them. Read
  the plan's M14 section for the outcome-by-outcome detail and the wave context.

- **Meeting-invite mail (`text/calendar` VEVENT) is the declared cut-line.** The
  plan's outcome 10 (an invite email preceding a minuted working session, its
  VEVENT date recomputed by the validator) is the first thing cut if the turn
  runs long. Implement it if the capability layer lands with room; it is not a
  hard criterion above. A standalone `.ics` DocFormat is explicitly out
  (`text/calendar` inside `.eml` reuses the existing renderer/validator/`FILE-01`
  plumbing). Timezones stay UTC, documented.

- **The one shared `expected_headers` twin is the load-bearing anti-drift
  device.** `render/eml.py` already computes every header as a pure function of
  the ledgers (`EML-01`). The renderer and the validator must call the *same*
  function to derive threading headers, subjects, and dates, and a unit test must
  render one entry and validate those bytes so the two cannot diverge silently.

- **Additive-evolution discipline is in force (the carve-out only reopens frozen
  fixtures, not additive evolution).** Every capability lands as a default-off
  knob with inert schema defaults on existing schema ids and randomness drawn
  only from the new streams listed in criterion 1. `docplan.email.cadence` (the
  M9 stream) is left untouched so knob-off byte-stability holds. Prove inertness
  against the not-yet-regenerated committed fixtures before the pilot turns
  anything on.

- **In scope, and nothing wider.** Schema (`schemas.py`: `MailCulture` on
  `DocCulture`, `Foundation.distribution_lists`, genre `Literal` additions),
  `docplan/registry.py` (genre rows), `docplan/planner.py` (`_emit_email` knob-on
  branch, `facts_refs` propagation to replies, send-minute planting; fix the
  stale Cc comment at `:65`), `render/eml.py` (shared `expected_headers`
  extension, MIME multipart, quoting, signatures, optional calendar part),
  `render/__init__.py` (reply resolves after predecessor; attachment embed pass),
  `foundation/scaffold.py` (DL derivation), `validate/rules.py` (`EML-01`
  extension or `EML-02`), `authoring/contexts.py` (thread-position and mundane
  genre brief guidance), `evals/emit.py` (split keying, attachment attribution),
  `acl.py` (DL expansion if the posture interacts), the new
  `recipes/ashcombe-advisory/ORG-CHARTER.md`, `docs/RECIPE-FORMAT.md`, and unit
  tests. **Out:** any noise interaction (M15), attachment-version mismatch (M15,
  where version chains exist), personal / off-topic content, timezone modeling.

- **Known edge cases the pressure test surfaced.** (1) Same-day replies must not
  collide on filename; add a dedupe/collision test. (2) A reply must render only
  after its predecessor is resolved, so `render/__init__.py` orders replies after
  their openers. (3) The To/Cc partition must tolerate a recipient who has
  departed as of the send date rather than crash. (4) A quoted tail that carries
  a planted fact must attribute that fact to the reply's manifest entry, or the
  extraction eval drops below 100%.

- **CI has WeasyPrint but no LibreOffice, and no model, network, key, or wall
  clock in any test tier.** The `.eml` renderer is stdlib `email`, so the whole
  mail path validates pure-Python in CI. The render-and-validate twin test and
  the quoted-tail byte-stability test need no renderer beyond stdlib. Keep every
  new fixture-validating test pure-Python, per CLAUDE.md.

- **House practices (zat.env).** Small committable increments with tests in the
  same increment; run the relevant tier after each functional change. When
  fixing a bug, change only what is necessary; do not refactor surrounding code
  in the same change. If two consecutive fix attempts fail, revert to the last
  working state and re-evaluate. Do not modify a test to accommodate a
  regression. The airlock is not otherwise touched: Python still never calls a
  model or the network, and no LLM grades an LLM in any automated tier. The
  pilot's prose is authored only inside skills, through the file-exchange
  airlock.

- **Verification (this turn).** `bin/test` all tiers green, keyless and offline;
  the byte pin green on every previously committed org at every commit including
  mid-turn; knob-off proofs (byte-identical committed artifacts, zero draws from
  the new streams) per capability; the render-and-validate twin test and the
  same-day-collision test pass; the pilot generates live end to end, validates
  green, scores 100% on all four eval splits, and is boarded via `/forge-review`.

---
*Prior spec (2026-07-21): M13 — path containment and letterhead escaping
(realism-wave hygiene); state-derived work-order names contained at schema, sink,
and terminal, charter-tainted letterhead context-escaped, both SECURITY.md notes
closed; all 7 criteria met.*

<!-- SPEC_META: {"date":"2026-07-21","title":"M14: email realism (thread mechanics + mailbox ecology) and the email-first pilot","criteria_total":12,"criteria_met":12} -->
