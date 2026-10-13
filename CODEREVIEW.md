# CODEREVIEW

## Review — 2026-10-13 (commit: 03f6442) — M17d: M18 readiness, the tenth org, v2.4.0

**Review scope:** Full review (the prior review's commit `1c0e132` is already
in `origin/main`, so the refresh focus set covers the whole range). 31 commits,
300 files. Code read in full: `orgsmith/` (schemas, fabric engagements and
finance, docplan planner, authoring contexts and ingest, review digest and
numbers, state lock, CLI, validator rules), `drivers/`, `tools/`, the four
skills, and every new or changed test. The `quillon-harbor` fixture was checked
structurally (validates clean, knobs effective, existing orgs differ from
`origin/main` only in derived `charter.json`, `DATA-CARD.md`, and
`GENERATION-REPORT.md`) and scanned by `/security`; its authored prose was not
re-read.

**Summary:** Five default-off generator knobs (business-day engagement starts,
oversight titles, scope by service, era shocks, scope-aware briefs), the REND-01
doubled-noun ingest check, the unowned-number measurement, the state lock, the
board digest, BYO effort and truncation handling, the skill-command short-tier
test, the tenth committed org, and v2.4.0. Two WARNs, both in new knobs, and
both latent: neither fires on any committed org. Both were fixed by `/codefix`
in one cycle, each with a unit test, and the full suite is unchanged apart from
the two new tests.

**External reviewers:**
None configured.

**Built-in review:**
`/code-review high`: 10 findings, 10 kept after Step 6 (3 merged with inline
findings, 1 kept as a WARN, 6 as NOTEs). One detail was rejected after
checking: its claim that a base-year shock also inflates later years' Travel.

### Findings

**[WARN, fixed] `orgsmith/fabric/finance.py:103-105, 118-119` — an era shock on the
expense base year permanently resizes every later year's expenses. (also
claude-code)**
  Evidence: the shock is applied to `year_revenues[year]` inside the revenue
  loop, and the expense anchors are then calibrated on
  `base_rev = year_revenues[base_year]` (`base_year = founded + 1`). A shock
  declared on that year therefore sizes Compensation, Office & Facilities,
  Professional Services, and Other for the firm's whole life. Reproduced on the
  committed `quillon-harbor` charter with the shock moved to 2013
  (revenue 0.6, travel 0.4): 2014 revenue is unchanged (3,419,000) but 2014
  Compensation drops from 1,752,400 to 1,051,400 and total expenses from
  2,755,150 to 1,769,230, and every later year stays about 40% low. That
  breaks the stated contract (`EraShock` docstring, `orgsmith/schemas.py:342-
  352`: "Multipliers apply to the year's drawn values and to nothing else...
  the following year returns to it"; SPEC criterion: "the following year
  returning to trend"). `tests/test_unit_era_shock.py` only exercises 2020, so
  the base-year case is untested. (The built-in's claim that Travel is also
  inflated is wrong: Travel's anchor and its `year_revenue / base_rev` ratio
  cancel, so non-shock Travel is unchanged.) A shock small enough to round the
  base year's revenue to 0 would also divide by zero in the Travel line.
  Latent: no committed org shocks its base year (`quillon-harbor` shocks 2020).
  Suggested fix: calibrate the anchors on the base year's UNSHOCKED revenue
  (keep the pre-shock value alongside `year_revenues`), so the shock touches
  only its own year's drawn values; this is byte-identical for every committed
  org. Add a unit test that shocks `founded + 1` and asserts every later year's
  expenses match the unshocked build.

**[WARN, fixed] `orgsmith/fabric/engagements.py:303-316`, `orgsmith/validate/rules.py:1101-1119` —
an `oversight_titles` entry that no charter title matches makes the knob
silently inert and OVR-01 pass vacuously. (claude-code)**
  Evidence: `oversight_candidates` filters people by
  `p.title_at(eng.start) in titles`, and nothing checks the configured titles
  against `charter.titles` (the source of every staff title,
  `orgsmith/foundation/scaffold.py:118-131`). A typo (`[Partners]` for
  `Partner`) leaves every engagement with no eligible senior, `assign_oversight`
  adds nobody, and OVR-01 runs (the knob is on) and yields nothing because
  `eligible` is empty. The org ships with the knob on and the defect it exists
  to fix unfixed, which is the silent pass CLAUDE.md's grandfathering rule
  forbids ("a knob that is on with its artifact missing is a failure").
  Latent: `quillon-harbor`'s `[Partner, Managing Partner]` both appear in its
  titles, and all eight of its engagements carry a senior.
  Suggested fix: reject an `oversight_titles` entry that appears in no
  `charter.titles` list (a check on the charter model, or at charter parse),
  so a typo fails at the charter stage. Add a unit test for the rejection.
  Committed charters are unaffected (only `quillon-harbor` sets the knob).

**[NOTE] `orgsmith/schemas.py:670-675` — the new title check echoes unknown
titles raw.** From the `/security` post-fix re-check. A crafted `charter.json`
in a received tree reaches `validate` as an uncaught `ValueError` whose message
carries the titles unescaped, bypassing `strip_control`. Reproduced on a
scratch copy (terminal escape sequences reached stderr). The run still exits
non-zero, and the exposure is not new: an unexpected `charter.json` key and
`_check_scope_services` (line 522) print raw the same way. Local fix:
`strip_control(t, keep="")` on each title (and in `_check_scope_services`). Complete fix:
sanitize the validation error where `validate` loads a received tree, as
ingest already does (`orgsmith/authoring/ingest.py:396-399`).

**[NOTE] `orgsmith/schemas.py:361-364` — `EraShock.quarters` accepts `inf`.**
From the `/security` post-fix re-check. `q > 0` admits `.inf`, which turns
the normalized quarter weights into NaN and crashes `_split_exact`. Only an
operator's own recipe reaches it. `math.isfinite` in the validator closes it.
(The same re-check notes a pre-existing divide-by-zero for a `base_revenue`
of 500 or less, which rounds the base year's revenue to 0. That predates this
range.)

**[NOTE] `orgsmith/review/numbers.py:44` — a run of more than 4300 digits in
authored prose crashes `report`.** From `/security`. `int()` on a 4301+ digit
match raises `ValueError` under Python 3.10.12's integer-string limit, and
nothing in the schema or ingest bounds a digit run. Fix in `numbers.py` only
(skip or cap matches longer than about 18 digits); `tools/probe_numbers.py`
shares the line but its sha256 is pinned in the pre-registration.

**[NOTE] `orgsmith/docplan/planner.py:377-427` — the closing-stage post-pass
states a funnel's final tally before that stage completes. (also claude-code)**
Already on the register as `closing-stage-reported-early` (BACKLOG.md), with
a real observed case (`d:0024`). Two things the entry does not say: the
`_scope_refs_for` docstring (`planner.py:335-347`) still claims position
gating makes the divergence "inexpressible rather than merely unlikely", which
is no longer true of the closing document; and the post-pass changes the
output of an existing knob (`engagements.scope`) rather than landing behind a
new one. That is inert for the frozen fleet only because no committed org had
scope on before this turn.

**[NOTE] `drivers/config.py:115`, `drivers/forge_external.py:404` — a 64000
output cap on a non-streaming request with a 600s timeout. (also claude-code)**
The Anthropic shape sends `max_tokens=64000` through a non-streaming `urlopen`
with a 600s timeout. The API sends nothing until the reply is finished, so a
reply that actually approaches the cap (adaptive thinking spends from it) can
exceed 600s and surface as a generic network failure, not as the named
truncation. Verified against the API reference: `output_config.effort` is GA
with no beta header, accepts `low` through `max`, and Claude Opus 5.5 defaults
to `medium`, so the effort plumbing itself is correct. Streaming, or a cap and
timeout sized together, would close it.

**[NOTE] `drivers/providers.py:173` — effort and the 64000 cap are sent for
any `ORGSMITH_ANTHROPIC_MODEL`. (claude-code)** An override to an older model
that rejects `output_config.effort` (Sonnet 4.5, Haiku 4.5) now gets HTTP 400 on
every request where v2.3.0 worked. It fails loud, and the docs steer users to
frontier models.

**[NOTE] `drivers/config.py:74` — OpenAI-shape providers, including `local`,
now default to 16384 output tokens. (claude-code)** A small-context local
server can reject `max_tokens=16384` plus a long work order. Fails loud,
`--max-tokens` overrides it, and `--check` now prints the cap.

**[NOTE] `tools/ab_control.py:38` — `ARM_KNOBS` does not know the M17d knobs.
(claude-code)** The docstring's command runs against the live
`recipes/quillon-harbor`, which now carries `scope_by_service`,
`oversight_titles`, `engagement_starts`, and `era_shocks`; the derived control
would strip `engagements.scope` but keep `scope_by_service`, so it would still
plant scope facts. The tool's tests moved to the frozen M17c recipe, so nothing
catches this. Mitigated by "experiments run on pinned code", but the tool could
refuse a recipe carrying knobs it has not classified.

**[NOTE] `orgsmith/authoring/ingest.py:250-252` — `_noun_stem` does not match
`-ies`/`-es` plurals to their singulars.** `companies`/`company`,
`businesses`/`business`, and `processes`/`process` stem differently, so the
check is weaker than the criterion's "singular or plural". Low impact: a
modifier word still matches ("comparable company" after "N comparable
companies" is caught by "comparable").

**[NOTE] `orgsmith/review/numbers.py:33` — decimals, times, and similar split
into integer fragments. (claude-code)** "4.25%" counts 25 and "10:30" counts
10 and 30. This follows the pre-registered counting rule exactly, and it is a
measurement that never gates.

**[NOTE] `orgsmith/authoring/ingest.py:279`, `orgsmith/review/numbers.py` —
duplicated parsing. (claude-code)** The noun read off a count's rendered
surface duplicates `orgsmith/evals/emit.py:count_noun`, and `numbers_in`
copies `tools/probe_numbers.py`. The second copy is pinned by a test and the
tool by its hash, which is a reason worth stating where the copy is defined.

**[NOTE] `orgsmith/fabric/engagements.py:282-286` — the `services is None`
branch of `plant_scope_facts` has only test callers. (claude-code)** Both
production callers (`build_engagements`, `scope_01`) pass `scope_services(...)`,
and the two paths differ when `scope` is None and `scope_by_service` is set
(`{}` against `{eid: []}`).

### Verified clean

- **No committed org's ledgers, manifest, or authored prose moved.** Against
  `origin/main`, the nine existing orgs differ only in `charter.json` (the new
  knob fields at their inert defaults: 7 lines added and 3 removed per org,
  5 and 2 for `dev-mini`), `DATA-CARD.md`, and `GENERATION-REPORT.md`, all
  derived.
- **The knobs are inert when off and effective when on.** The new streams
  (`fabric.engagements.scope_by_service`, `fabric.engagements.oversight`) are
  new names. The start shift is RNG-free and runs before the duration draw.
  Oversight is an append-only post-pass. `has_scope` and `profile_for_service`
  reduce to the M17b behavior when `scope_by_service` is empty. On
  `quillon-harbor`, all eight engagement starts are business days
  (2016-07-05 follows the declared 2016-07-04) and every engagement carries an
  eligible senior.
- **State lock** covers every verb that calls `save_state` except `doctor`,
  which is excluded on purpose. Reentrancy is per resolved path, and the
  concurrency test races real subprocesses.
- **Board digest** excludes exactly what the board writes (`review/` and
  `GENERATION-REPORT.md`; `report` and `review --sample/--ingest` write
  nothing else), and the skill verifies before `report`.
- **Docs:** every relative link in the changed Markdown resolves. CLAUDE.md is
  99 lines, and the validator has 40 rules, as the skill and README now say.

### Tests

Baseline before the fix loop: short 19, unit 824, org 261 passed with 30
skipped, flagship 71 passed with 5 skipped, all keyless and offline. After
`/codefix`: short 19, unit 826 (the two new tests), org 261 passed with 30
skipped, flagship 71 passed with 5 skipped. The org tier includes
`PINNED = SLUGS`, so the committed fleet still re-derives byte-identical. The
30 org-tier skips are the documented per-org feature-off parametrizations
(for example "poses no unanswerable question"), not silent skips of a hosted
fixture.

### Security

`/security` over the 263-file surface since `c5b9994`: 0 BLOCK, 0 WARN,
1 NOTE (the 4300-digit `report` crash above). No secret in the scoped files,
the range diff, or the rendered Office and PDF files; dependency pins are
unchanged from `aef75a9`. The post-fix re-check over the four files
`/codefix` touched found nothing in the fixes themselves and added one NOTE
(the raw title echo above). SECURITY.md now records 0/0/2 and is uncommitted.

### Fixes Applied

- **[WARN] `orgsmith/fabric/finance.py:95-124`** (also claude-code): the
  revenue loop now keeps each year's pre-shock revenue in `trend_revenues`,
  and `base_rev` reads from it, so a shock changes only its own year's drawn
  values. This also removes the divide-by-zero for a base-year shock that
  rounds revenue to 0. New test:
  `test_a_shock_on_the_expense_base_year_leaves_every_other_year_untouched`
  (`tests/test_unit_era_shock.py`), which shocks dev-mini's first full year
  and asserts every other year equals the unshocked build. Re-reviewed:
  committed orgs are unaffected (only `quillon-harbor` declares a shock, on
  2020), and the shock year's Travel still tracks its shocked revenue, as the
  comment says.
- **[WARN] `orgsmith/schemas.py:664-675`** (claude-code): `Charter._check`
  rejects an `oversight_titles` entry that is not in any `charter.titles`
  list or the scaffold's generic fallbacks (`Director, {dept}`,
  `{dept} Associate`). Re-reviewed against `orgsmith/foundation/scaffold.py`:
  those are the only title sources (promotions move up the same lists, and
  enrichment does not touch titles). New test:
  `test_an_oversight_title_no_one_can_hold_is_rejected_at_parse`
  (`tests/test_unit_oversight.py`). All ten committed charters still load.

The changes are uncommitted: `orgsmith/fabric/finance.py`,
`orgsmith/schemas.py`, `tests/test_unit_era_shock.py`,
`tests/test_unit_oversight.py`, plus `CODEREVIEW.md` and `SECURITY.md`.

### Accepted Risks

None.

---
*Prior review (2026-08-10, commit 1c0e132): light review of a README picker-table
correction and a BACKLOG entry. One WARN (a wiki-link syntax GitHub does not
render), applied by the author.*

<!-- REVIEW_META: {"date":"2026-10-13","commit":"03f6442","reviewed_up_to":"03f6442553c9989f3cdb0742af2c3639d5d74c13","base":"origin/main","tier":"full","block":0,"warn":2,"note":12} -->
