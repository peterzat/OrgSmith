# SPEC

## Spec — 2026-07-16 — M9: the document-supply model (genre registry, driver-derived supply, realistic lengths, folder taxonomy)

**Goal:** M8 gave the fabric a time dimension; the review board then said the
firm's *paper* still does not look like a business. The planner emits a fixed
`2E + 7 + pptx + eml` skeleton with three genres hard-capped (kickoffs for the
first two engagements, status reports for the first and last, financial
summaries for the last two years), `target_docs` merely checksums `format_mix`,
every authored document is ~130-350 words against real-world 800-1500, and the
whole share lives in three folders. Replace the skeleton with a declarative
genre registry whose rows are driven by the firm's actual activity
(engagements, fiscal years, hires, vendors), so document supply, folder
taxonomy, and per-genre length follow from what the firm *does*. This is the
keystone the rest of the v2.0 arc waits on: it is what makes `target_docs`
honest and the M12 flagship affordable. The freeze on `companies/` stays lifted,
so this arrives as the generator's only behavior; `dev-mini` is regenerated to
exercise it and stays the sole byte-pinned fixture until M11.

### Acceptance Criteria

- [ ] **A declarative genre registry is the single source of document supply.**
  Each genre is a registry row declaring its driver, cadence, folder, format,
  and target length; the planner builds the manifest by walking the registry,
  not by calling one hard-coded method per genre. The three caps are gone
  (`idx < 2`, `idx in (0, len(engs)-1)`, `fy_years[-2:]` in
  `docplan/planner.py`). The driver vocabulary includes at least one class the
  fixed skeleton could not express (a per-hire or per-vendor cadence, keyed off
  roster churn or the external orgs). Adding or removing a registry row changes
  the planned manifest with no other planner edit, proven by a unit test that
  drives the planner off a modified registry. Every new genre reuses an existing
  renderer/format (docx/pdf/xlsx/pptx/eml); M9 adds no new renderer.

- [ ] **Document supply is a pure function of the firm's drivers, and it
  scales.** For a synthetic charter, changing a driver moves the count in the
  declared direction: more engagements → proportionally more per-engagement
  docs; a longer `date_range` → more per-year docs; a hire or a vendor → the
  per-hire / per-vendor genre appears where before it could not. The old
  `2E + 7 + pptx + eml` identity no longer holds for any recipe. A synthetic
  charter with many engagements over a long span derives several hundred
  documents through the four pure stages alone (no model), byte-identically
  run-to-run and in well under a second, which is the machinery that makes a
  ~2,000-document flagship affordable at M12. Verified at the manifest level by
  deterministic tests.

- [ ] **`target_docs` becomes honest and the `format_mix` exact-sum constraint
  is replaced.** The open question is resolved in favor of the registry
  *deriving* the count and format distribution from drivers: the planner no
  longer asserts `len(manifest) == target_docs` or `counts == format_mix`, and
  `DocCulture` no longer rejects a recipe because `format_mix.total !=
  target_docs`. The manifest count equals the registry's computed supply,
  independent of `format_mix`. Because committed recipes set `format_mix`,
  `target_docs`, and friends and the schema is `extra="forbid"`, those fields
  stay *accepted* (repurposed as advisory/size hints or derived outputs, not
  dropped), so all seven committed recipes still parse and
  `test_committed_charter_redump_stays_additive` stays green. A recipe that
  wants to bound size does so through a driver/cadence knob, not a checksum,
  and that knob is documented in `docs/RECIPE-FORMAT.md`.

- [ ] **Per-genre target lengths are realistic and live in the registry.**
  Target words move out of `_TARGET_WORDS` (`authoring/contexts.py`) into the
  registry as a genre property and are raised to real-world bands: engagement
  letters 800-1500, and every other authored genre raised commensurately (memos,
  reports, minutes, overviews into the several-hundred-to-~1000 range) rather
  than left at the old 130-350. The airlock is unchanged: the brief still
  carries a single `target_words` per document, now sourced from the registry.
  The regenerated `dev-mini` authors its engagement letter materially longer
  than the old ~350-word target (measured by `orgsmith report` /
  GENERATION-REPORT.md, recorded in the turn).

- [ ] **The folder taxonomy extends beyond `Engagements / Finance / Firm`.** At
  least one new-driver genre lands in a new top-level share folder (e.g. a
  per-hire onboarding record under `People/`, or a per-vendor document under a
  vendor/admin folder), declared by the registry row rather than hard-coded in a
  planner method. Filenames stay realistic and pass `check_relpath`. The
  regenerated `dev-mini` share contains at least one folder beyond the original
  three, and its manifest and TOC reflect it.

- [ ] **The two engagement-letter rendering findings are settled.**
  `letterhead-duplicated-in-letters`: a rendered engagement letter shows the
  firm name once (in the letterhead), not doubled by an author-written
  firm-name heading, resolved either by the letter guidance in
  `authoring/contexts.py` or by the renderer suppressing a leading heading that
  duplicates the letterhead. `pdf-newline-flattening`: `render/pdf.py` honors an
  intra-paragraph `\n` as a line break the way the docx renderer does, so a
  multi-line addressee/address block no longer smears into one run-on line.
  Both are covered by a unit test on the renderer output and are visible on the
  regenerated `dev-mini` letter; both BACKLOG entries are closed at turn end.

- [ ] **Email-thread cadence is realistic.** Successive messages in the same
  engagement thread are spaced hours to days, not the current fixed 45 days
  (`docplan/planner.py:316`), so a thread reads as a thread. A synthetic recipe
  with multiple emails in one engagement produces plausible in-thread spacing,
  verified deterministically; the existing round-robin/wrap correctness tests
  (`tests/test_unit_eml.py`) still pass. Any added randomness draws from a NEW
  `seeds.py` stream. The `email-thread-spacing` BACKLOG entry is closed.

- [ ] **Determinism holds and the committed fleet survives the rewrite.** Every
  pass added this turn draws from its own NEW named `seeds.py` stream rather than
  reusing an existing one. `dev-mini` is regenerated end-to-end with the M9
  supply model and remains the sole byte-pinned fixture: its `foundation.json`,
  pure-stage ledgers, and `manifest.jsonl` regenerate byte-identically
  (`test_org_regen.py` pin tests green). The other six fixtures derive through
  all four pure stages without crashing under the new planner
  (`test_every_committed_recipe_still_derives`) and keep validating clean,
  scoring extraction ground truth at 100%, and reporting complete
  (`test_org_fleet.py`) — validation never re-runs the planner, so their frozen
  manifests are unaffected.

- [ ] **From a fresh checkout, `bin/test` passes all tiers offline and keyless**,
  with `org` under ~5s and `unit` under ~20s, and every document `docs/SCALE.md`,
  `README.md`, and `TESTING.md` states that M9 makes false is corrected: the
  fixed-skeleton description, the 236-word length figure now that lengths are
  raised, the "three folders" shape, and the fixture/count numbers. Baseline
  test counts and timing are recorded at turn close.

### Context

- **This consumes the M8 proposal (v1.7.0 shipped).** M8 landed roster churn,
  `title_history`/`title_at`, date-scoped person briefs, engagement elapsed
  position, a date-scoped firm digest, behavioral finance, staffing rotation,
  and era-appropriate names; `dev-mini` was regenerated as the sole byte-pinned
  fixture and its board confirmed the six targeted majors gone. The board then
  surfaced the paper-realism findings this turn acts on. Full history:
  `git log` since 2026-07-16, and the M8 spec summary below.

- **What "driver-derived" means, concretely.** Today each genre's count is
  wired into a planner method: engagement_letter once per engagement,
  kickoff_memo for `engs[:2]`, meeting_minutes once per engagement, status_report
  for `engs[0]` and `engs[-1]`, company_overview once mid-range,
  financial_summary for the last two fiscal years, briefing_deck/engagement_email
  off `format_mix`. M9 lifts these into registry rows: a driver names *what
  spawns the genre* (each engagement, each fiscal year in range, the firm on a
  period, each hire, each vendor) and a cadence names *how many per driver
  window*. The count then falls out of the firm's real activity, which is the
  whole point: a five-year firm with four engagements and two hires produces the
  documents that firm would produce, not a constant skeleton.

- **The `target_docs` / `format_mix` tension is the crux (proposal open
  question).** `DocCulture._check` requires `format_mix.total == target_docs`
  and the planner re-asserts `counts == want`; `test_unit_pure_stages.py:108`
  asserts `len(manifest) == target_docs`. Once format follows genre, an exact
  input sum cannot survive. Resolution: the registry derives supply; those
  fields become advisory (a size hint / derived report), not gates. They cannot
  be *removed* — six committed recipes set them and the schema forbids unknown
  fields, so removal would fail `test_every_committed_recipe_still_derives` and
  the redump-additive test. Repurpose in place. Update the tests that encode the
  old exact-sum contract (`test_unit_pure_stages.py`, `test_unit_compat.py`,
  and the `conftest.py` recipe-mix fixtures) rather than papering over them.

- **The six committed fixtures are frozen and must not be regenerated this
  turn.** Only `dev-mini` is byte-pinned (`test_org_regen.py::PINNED`). The
  other six were authored under the old skeleton; their committed manifests and
  rendered files are frozen and keep validating because validation reads
  artifacts and never re-runs the planner. The new planner only has to derive
  them without crashing (existence check). They regenerate wholesale at M11.
  This means the new planner must run on all seven recipes as written, including
  cindergrove's 1998 span and the ambiguity/scan/legacy knob clusters.

- **New genres reuse existing renderers.** To bound the surface, every genre M9
  adds maps to an existing format and renderer (docx/pdf/xlsx/pptx/eml). No new
  renderer, no new binary format. A per-hire onboarding memo is a docx; a
  per-vendor record is a docx or xlsx. This keeps the validator, evals, and
  legacy/scan paths unchanged except for recognizing the new genre/folder.

- **Degrade, do not crash, at the smallest recipe.** Like M8's churn, a driver
  the firm cannot host produces nothing rather than an error: a recipe with no
  hires (churn off) plants no per-hire docs; a recipe whose external orgs are
  all clients plants no per-vendor docs. The minimum recipe (headcount total 2,
  one engagement, one year) must still derive a coherent, non-empty manifest.

- **The airlock is unchanged and absolute.** Python still never calls a model
  and never touches the network. The registry is bundled data or code; lengths
  and folders are pure planner/brief fields. Facts stay load-bearing: every
  number, date, id, name, and relationship still comes from the ledgers, and the
  model still writes only surface prose around `{{fact:...}}` placeholders.
  Longer targets mean more prose *around* the same placeholders, never more
  facts invented by the model.

- **Length is load-bearing for scale, not just realism (`docs/SCALE.md`).** At
  today's ~236-word mean a flagship needs ~8,500 documents to defeat a 1M-token
  context; at realistic ~800-word lengths it needs ~2,000. Raising the targets
  is what makes M12 affordable, which is why M9 precedes it. SCALE.md's token
  table and the 236 figure need re-measuring/annotating once dev-mini is
  regenerated at the new lengths.

- **Determinism landmines carried from M8.** `foundation/scaffold.py` and the
  shared `rng(charter.seed, "foundation.scaffold")` stream still couple unrelated
  passes; any new M9 pass (per-hire spawning, email cadence jitter, cadence
  counts) draws from its own named stream so a later change to one does not
  silently move another. The freeze lift removes the byte-identity obligation
  against the six, but the per-stream discipline is explicitly NOT relaxed (it is
  what keeps a single generation reproducible and the dev-mini pin valid).

- **BACKLOG interactions.** Three entries are marked ACTIVE for this turn:
  `letterhead-duplicated-in-letters` and `pdf-newline-flattening` (criterion 6,
  both letter-rendering findings on the genre M9 re-renders) and
  `email-thread-spacing` (criterion 7). `recipe-growth-outruns-headcount` and
  `acl-blind-to-departure` stay deferred to M11 (the fleet reset), where the new
  recipes are made internally coherent and the ACL model is revisited;
  `charter-redump-drift` still wants its M11 decision and its additive test keeps
  passing here because new recipe fields are gained keys, not moved values;
  `board-negative-control` is M12; `org-tier-scaling-plan` is M10 and its
  revisit trigger (org tier crossing ~10s) is worth watching as dev-mini grows.

- **Where the board fits.** The paper-realism findings are the driver, but no
  metric and no board finding becomes a validator rule or a gate this turn. The
  deterministic manifest/brief/render tests are the oracle for every criterion
  above; running `/forge-review` on the regenerated `dev-mini` is optional
  enrichment, not a gate, and an empty or unchanged board report is a fine
  outcome.

- **House practices (zat.env).** Oracles beat proxies beat critics; the
  manifest and renderer tests carry these claims, not the board. Verification
  quality is the ceiling, so invest in the deterministic tests before the
  prompts/lengths. Small committable increments with tests in the same
  increment; verify the build and existing tests pass before starting, and fix
  any pre-existing failure first. A prompt or a knob that cannot name the
  failure mode it prevents is the first to delete. No push or remote mutation
  without explicit user instruction.

- Environment: Python 3.10-compatible (the box runs 3.10 though
  `.python-version` says 3.12); always `.venv/bin/python`. LibreOffice is on the
  generation box for legacy rendering but CI has none; validation stays pure
  Python.

---
*Prior spec (2026-07-16): M8 the firm gets a history (roster churn, behavioral
finance, staffing rotation, date-scoped briefs, era naming); all 11 criteria
met, shipped as v1.7.0.*

<!-- SPEC_META: {"date":"2026-07-16","title":"M9: the document-supply model (genre registry, driver-derived supply, realistic lengths, folder taxonomy)","criteria_total":9,"criteria_met":0} -->
