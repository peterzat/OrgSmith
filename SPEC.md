# SPEC

## Spec — 2026-07-21 — M13: path containment and letterhead escaping (realism-wave hygiene)

**Goal:** Close the two open SECURITY.md notes and the divergent path helpers
they descend from, so the model boundary is contained at the schema, the sink,
and the terminal, and charter-tainted letterhead can no longer break out of its
render context. Zero tokens, pure Python, one turn, no regeneration: the first
milestone of the M13-M16 realism wave buys the right to open the frozen-fixture
carve-out in M14 with the path-safety debt already paid.

### Acceptance Criteria

- [ ] **A `state.json` whose `outstanding` value or `author_batches[].workorder`
  carries a path separator, `..`, an absolute path, or a control character is
  rejected at schema validation, and a value that reaches the sink anyway
  cannot resolve outside `workorders_dir`.** Today neither field carries a
  pattern (`state.py:69`, `:48`), so a tampered value survives validation as a
  free string and `outstanding_work_order` (`airlock.py:79`) /
  `match_author_batch` (`airlock.py:186`) join it under `workorders_dir` where
  pathlib discards the base for an absolute operand and `../` traverses out.
  Both layers guard, mirroring the two-layer fix `DocIR.doc_id` received: a
  pattern on the schema fields and a contained-join guard at the sink, so a
  refactor of one cannot reopen the hole. Proven by tamper tests in the shape
  of `tests/test_unit_airlock.py` /
  `tests/test_unit_pure_stages.py:136-153` (hostile absolute path, `../`
  traversal, control character) that assert rejection at parse and a raised
  guard at the join.

- [ ] **All eight committed `state.json` files still load, validate, and
  re-serialize under the new patterns, and the byte pin stays green fleet-wide.**
  The pattern admits every work-order name the generator has ever written
  (`{stage}-NNNN.json`, including the `foundation_enrich` stage and the
  `author-NNNN.json` batch refs), so no historically-committed value is
  rejected. This is the guard on the criterion above: `PINNED = SLUGS`
  (`tests/test_org_regen.py`) and the `org` tier revalidate all eight orgs with
  zero fixture movement. `orgsmith/state@1` is not bumped; this is a validator
  tightening on the existing id, safe only because it admits every committed
  value.

- [ ] **Letterhead and style interpolations are context-escaped, separately for
  the CSS-string and HTML contexts they land in, and the escape is an identity
  transform on all eight committed charters.** `render/pdf.py:74` runs Jinja2
  with `autoescape=False`, and `letterhead0` / `letterhead_rest` (charter name
  and domain, tainted via `render/styles.py:43`) reach a CSS `content:` string
  at `pdf.py:38` and HTML `<div>` contexts at `pdf.py:65-66` unescaped, while
  body blocks already go through `html.escape`. A charter name containing `"`,
  `<`, or `&` renders a well-formed PDF showing the literal name (the CSS string
  is not broken by a quote, the HTML is not broken by an angle bracket), proven
  by a render test feeding a hostile charter name. Because all eight committed
  charter names and domains are plain ASCII (verified this turn), the escape
  changes no committed output: a pure-Python test asserts the escape is identity
  on each committed `charter.name` and `charter.domain`, so the claim holds in
  CI without rendering.

- [ ] **Exactly one guarded helper turns a `doc_id` into a safe filesystem name,
  and `review/corpus.py` and `render/scan.py` route through it.** The
  `doc_id.replace(':', '')` join is copied unguarded at `review/corpus.py:44`
  and `render/scan.py:31`, while `authoring/ingest.py:99-103` guards its own
  copy with `check_filename`. After this turn the guarded basename derivation
  exists once; both other sites call it (each appending its own directory and
  suffix), and a `doc_id` containing a separator raises rather than escaping its
  directory, proven the way `tests/test_unit_airlock.py`'s traversal test proves
  the ingest sink. (`render/eml.py:42` also joins a `doc_id` but into a
  Message-ID, not a path, and is out of scope.)

- [ ] **State-derived strings interpolated into terminal output are neutralized
  via `strip_control` or `!r`.** The un-repr'd `{path}` interpolations in
  `airlock.py`'s `SystemExit` / `print` sites carry a tampered name's control
  characters straight to the terminal, where an ESC sequence can rewrite earlier
  output; deliverable-controlled interpolations in the module are already
  `!r`-quoted. Proven by a test that drives an ESC/control-bearing state-derived
  value to a print site and asserts the raw control character does not reach the
  output. (The schema pattern above is the primary defense for the
  `outstanding` / `workorder` fields; this hardens the print path for any
  state-derived string, including fields the pattern does not cover.)

- [ ] **SECURITY.md records both notes closed with the fix commit, and `bin/test`
  passes all tiers offline and keyless with zero fixture movement.** A new
  SECURITY.md entry closes the 2026-07-17c `airlock.py:79` NOTE
  (state-derived names reaching a read outside `workorders_dir`) and the
  carried-forward M9 `render/pdf.py` letterhead NOTE. `bin/test`
  (`short` + `unit` + `org`) is green, no tier gains a model, network, key, or
  wall-clock dependency, and the byte pin is green at the commit.

- [ ] **A `provider-neutral-authoring-driver` entry is added to BACKLOG.md.** It
  records the user decision (2026-07-21) that a provider-neutral authoring
  interface is wanted "soon, not this wave," cites `docs/EXTERNAL-CRITIQUE-2026-07-17.md`
  section 4 and the README's "the file exchange is the whole interface"
  position, and carries a concrete revisit criterion (first external consumer of
  the authoring interface, the packaging/release turn, or a MODEL-AB round 3).
  It passes the same specificity / revisit / why-deferred gates every BACKLOG
  entry must.

### Context

- **Adopted from `~/.claude/plans/we-ve-gotten-to-a-squishy-torvalds.md`** (the
  approved M13-M16 realism wave). This spec is M13, the wave's hygiene turn.
  Its candidate outcomes were reformulated into the criteria above; the plan's
  own scope note bounds it. At turn close the `### Proposal` step pulls the next
  milestone section (M14: email realism plus the email-first pilot) from that
  file, so read it for what comes next.

- **In scope, and nothing wider.** The two airlock path sinks
  (`airlock.py:79`, `:186`), the two unpatterned state fields (`state.py:69`,
  `:48`), the divergent `doc_id`-to-name copies (`review/corpus.py:44`,
  `render/scan.py:31`) unified onto the guarded pattern from
  `authoring/ingest.py:99-103` (`naming.check_filename`), terminal hygiene for
  state-derived strings, and the M9 letterhead escape (`render/pdf.py`,
  `render/styles.py:43`). **Out:** work-order content addressing, the
  `state.json` three-way split (`state-json-mixes-execution-and-provenance` in
  BACKLOG; M13 adds a field pattern, it does not split the file or bump the
  id), and any schema id bump. No new recipe knob, no new `seeds.py` stream, no
  ledger change.

- **The two-layer precedent to copy is already in the repo.** `DocIR.doc_id`
  got a schema pattern and `docir_path` (`authoring/ingest.py:92-103`) guards
  itself with `check_filename`, and `test_traversal_doc_id_is_rejected_at_the_schema_and_at_the_sink`
  (`tests/test_unit_airlock.py`) proves both layers independently ("a refactor
  of that ordering cannot reopen a traversal"). The state-value fix is the same
  shape applied to `OrgState.outstanding` values and `BatchRef.workorder`.
  `naming.py` already ships the primitives: `check_filename` (forbids `/`, `\`,
  control characters) and `strip_control` (neutralizes terminal control
  characters).

- **This is a validator tightening on a frozen fixture, which is the one risk.**
  Adding a `pattern` to an existing `orgsmith/state@1` field can reject a
  previously valid state. The mitigation is criterion 2: round-trip all eight
  committed states before the turn closes. The pattern must admit the
  `foundation_enrich` stage's underscore and the `author-NNNN.json` batch-ref
  form. Additive evolution is not suspended this turn (the carve-out that
  suspends the frozen-fixtures rule lands in the M14 spec commit, not here); the
  byte pin is the safety net for every change.

- **CI has WeasyPrint but no LibreOffice.** Render tests run in CI, so the
  hostile-charter-name PDF render test is CI-safe; the letterhead identity check
  is pure Python (compare the escape's output to the input for each committed
  charter) and needs no renderer at all. Keep validation of every committed
  fixture pure-Python, per CLAUDE.md.

- **Charter names verified this turn:** all eight (Northgate Talent Partners
  LLC / northgatetalent.com, Calderwood Partners LLC, Pinebrook Advisory Group
  LLC, Hollowell Patent Group PLLC, Brackenridge Civil Group Inc, Meridian
  Actuarial Advisors LLC, Saltmarsh Environmental Partners LLC, Verdant Health
  Advisory LLC) are plain ASCII with no HTML/CSS special characters, so the
  letterhead escape is output-neutral for the committed corpus.

- **House practices (zat.env).** Small committable increments with tests in the
  same increment. When fixing a bug, change only what is necessary; do not
  refactor surrounding code in the same change. If two consecutive fix attempts
  fail, revert to the last working state and re-evaluate. Do not modify a test
  to accommodate a regression. The airlock is not otherwise touched: Python
  still never calls a model or the network, and no LLM grades an LLM in any
  automated tier.

- **Verification (this turn).** `bin/test` all tiers green, keyless and offline;
  `org` tier revalidates the committed fleet; `PINNED = SLUGS` byte pin green;
  the three tamper tests (hostile `state.json` values, an ESC-bearing name
  through a print site, a hostile charter name through the letterhead) pass;
  SECURITY.md's two open notes closed.

---
*Prior spec (2026-07-17): M12a — the flagship's capability layer (business-day
calendar, engagement/revenue coherence, deterministic noise model, nested eval
splits, voice mitigation, reporting-line lint) proven on the `calderwood-partners`
pilot; all 9 criteria met.*

<!-- SPEC_META: {"date":"2026-07-21","title":"M13: path containment and letterhead escaping (realism-wave hygiene)","criteria_total":7,"criteria_met":0} -->
