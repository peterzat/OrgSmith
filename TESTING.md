# Durable test-architecture contract

Written by `/tester design` on 2026-07-16. Describes how this project
tests, what each tier promises, and what is deliberately left untested. A
fresh session should be able to run the suite and add a test from this
section alone.

## Cold-open

From a clean checkout, on a box with Pango (WeasyPrint's text stack):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
bin/test                      # short + unit + org; exit 0
```

Expect ~32s wall and 447 passing (14 short, 361 unit, 72 org) on a box
with LibreOffice; 441 passing + 6 skipped without it (measured by hiding
soffice from `PATH`, which is what CI sees). Both are green states,
see Environment axis. No API key, no network, no model: a
tier that wants any of those is a bug, not a setup problem. (M9 enlarged
the tracer -- `dev-mini` grew from 13 to 22 documents -- so every
dev-mini-based fixture, and the LibreOffice legacy fixture most of all,
does proportionally more work than the pre-M9 numbers. M11b replaced the
six pre-v2.0 fixtures with five larger ones and restored the byte pin
fleet-wide, so the org tier now re-derives seven orgs rather than two: it
grew 61 -> 72 even as six fixtures left.)

## Entry point

`bin/test [short|unit|org ...]`, default all three. One pytest invocation
per tier selected by marker; the script fails if any requested tier fails.
It takes tier names only and forwards no pytest arguments.

For the inner loop, call pytest directly. This is expected, not a
workaround:

```bash
.venv/bin/python -m pytest tests/test_unit_pure_stages.py -k finance
.venv/bin/python -m pytest -m unit --durations=10
```

`hooks/pre-push` runs `bin/test short` and blocks the push on failure;
install it once per clone with `bin/install-hooks`. CI
(`.github/workflows/ci.yml`) runs the full `bin/test` on every push and
pull request, and is the actual gate.

## Tiers

| tier | what earns the marker | count | budget | measured |
| --- | --- | --- | --- | --- |
| `short` | static and configuration checks: no model, no network, no key, version/pin/name invariants, and the `schemas/` export pin | 14 | < 1s | 0.22s |
| `unit` | deterministic logic, schemas, renderers, the airlock contract, ledger math, built on synthetic orgs in `tmp_path` | 361 (355 in CI) | ~20s | ~28s local / ~15s CI |
| `org` | full validation of every committed fixture under `companies/`, plus deriving **every recipe**, re-deriving **every fixture** byte-identically (`PINNED = SLUGS` since M11b restored the fleet-wide freeze), and checking fleet-recipe coherence | 72 | ~8s | 4.79s |

Budgets come from SPEC.md and are stated, not enforced: a wall-clock
assert on a shared runner is a flaky test, and this suite has none.
Measure with `--durations` before and after a change that adds fixtures or
knobs.

### When the `org` tier splits, and what splits it

Resolves BACKLOG `org-tier-scaling-plan` (2026-07-16, M11a). **Decision: no
split now, and the trigger is measured rather than guessed.**

**Re-measured 2026-07-17 (M11b), with the fleet turn landed.** The
projection above held almost exactly: it predicted 280 share files ≈ 3.8s,
and the actual fleet is **294 share files, 72 tests, ~3.9s steady-state**
(13.3 ms/file; the first run of a session reads ~5.2s cold, so measure warm
and measure more than once). The decision is unchanged -- **still no split**
-- but the headroom is now the story rather than the margin: the tier sits
roughly 1.1s under its own trigger, where at M11a it sat 2.9s under.

Original M11a measurement, kept for the trend: 153 share files, 61 tests,
**2.10s** — up from 1.36s / 104 files before `meridian-actuarial`. That was
**13.7 ms per share file** end to end (validation dominates; deriving all
thirteen recipes is ~60ms each and scales with recipe count, not file
count). Per-file cost is essentially flat across the fleet reset, which is
what makes the projection trustworthy going forward.

- **Trigger:** the `org` tier crossing **5s** measured warm (`bin/test
  org`), or any single committed org above ~150 files. M11b landed at ~3.9s
  and re-measured rather than assuming; the next turn that adds a fixture
  should do the same, because at 13.3 ms/file one more 50-doc org is ~0.7s
  and two would fire the trigger.
- **What splits it, when it fires: by job, not by size.** The `org` tier's
  job is "every committed fixture still validates against its ground truth",
  and that job wants the whole fleet — a subset tier that skips five of
  seven orgs is not a cheaper version of it, it is a different and weaker
  check, and the per-org spread (an image-only-scan org validates far
  cheaper per file than a prose-heavy one, because rules skip in bulk on
  pages with no extractable text) means a "representative" subset is not
  representative of cost either. What genuinely is a different job is the **flagship** (M12, ~2,000
  docs): validating it is a scale test, not a fixture regression check, and
  at 13.7 ms/file it alone is ~27s. It gets its own marker, excluded from
  the default `bin/test`, and runs in CI on its own.
- **Explicitly rejected:** trimming the fleet to keep the tier fast. The
  fixtures are the oracles; deleting coverage to buy 2 seconds inverts the
  point of having them.

Two facts before trusting the unit number: one module-scoped fixture
(`tests/test_unit_legacy.py::legacy_org`) owns ~14.5s of the ~26s local
unit tier (it converts every office doc through LibreOffice at ratio 1.0,
and M9's richer tracer gave it more office docs to convert) and is skipped
entirely in CI. Without it the tier is ~14.6s -- the CI-relevant number,
comfortably inside budget -- so the local run with LibreOffice now exceeds
the stated ~20s while the offline/CI gate does not. Measure both when a
change grows the tracer.

## Proxy and drift strategy

The hierarchy is **oracles beat proxies beat critics** (README, "Why we
think the output is any good"). It is unusually well kept here and this
contract does not relax it.

**Deterministic output must not drift; this is the load-bearing
invariant.** Enforced by `tests/test_org_regen.py` (added 2026-07-16): it
re-derives fixtures from `recipes/<slug>/ORG-CHARTER.md` and diffs
`foundation.json` (structure; personas are model-authored and blanked on
both sides), `ledger/*.json`, and `docplan/manifest.jsonl` byte-for-byte.

**The byte-pin covers the whole committed fleet again as of M11b**
(`PINNED = SLUGS`, seven orgs). It was scoped to `dev-mini` for M8..M10 and
to `{dev-mini, meridian-actuarial}` at M11a, because M8 lifted the freeze
and made v2.0 a breaking window: churn moved `foundation.json`, behavioral
finance moved `finance.json`, and rotation moved the manifest, so no pin
against the six pre-v2.0 fixtures' committed bytes could pass. That was
recorded at the time as "a real loss of coverage on six recipes, and it is
temporary". It was temporary: M11b retired those six, generated their
replacements on the v2.0 stack, and restored the pin fleet-wide. `PINNED`
is now `SLUGS` itself rather than a filtered literal, so a newly committed
org cannot be quietly left unpinned.

What survives fleet-wide, because it costs ~60ms and catches a different
class of break: `test_every_committed_recipe_still_derives` runs all four
pure stages on all seven recipes. A generator that crashes on
brackenridge's 1999 recipe or on a knob cluster no other fixture carries
is still caught. Since M11b restored `PINNED = SLUGS`, "the bytes moved" is
caught too, on every committed org rather than on the tracer alone.

**`charter.json` is pinned for current-schema fixtures as of 2026-07-16**
(M11a), which resolves `charter-redump-drift`. Two assertions, deliberately
at different strengths:

- `test_committed_charter_regenerates_byte_identical` (PINNED) puts
  `charter.json` in the byte diff beside the ledgers. `run_charter` now
  compares rendered bytes and writes only when the derivation actually
  moves, so a `/forge` resume can no longer dirty a frozen fixture. Compared
  on bytes rather than on the recipe's hash because charter.json is a
  function of the recipe AND the schema -- a recipe-hash guard would hide
  exactly the drift this resolves. Compared rather than blocked outright
  (what `run_scaffold` does): scaffold can afford the blunter guard because
  re-scaffolding would wipe merged enrichment prose, while re-deriving a
  charter loses nothing.

  The two halves close a loop worth naming: the pin keeps every committed
  charter equal to a fresh derive, so a committed charter is never stale, so
  a resume never rewrites one. The cost is that adding a charter field means
  re-dumping the pinned fixtures in the same commit -- one visible file per
  fixture, which is the point. `hires` (M11a) is the first to exercise it.
- `test_committed_charter_redump_stays_additive` (SLUGS) keeps the weaker
  never-drop-a-key, never-move-a-value invariant fleet-wide.

The split was not hedging, and M11b collapsed it. The drift was never a
code defect: the six pre-v2.0 fixtures' charters were written by an older
schema, so a fresh derive legitimately gained fields they never carried, and
no write guard could change that. Measured 2026-07-16: dev-mini
byte-identical, the other six drift -- fernhollow included, which was still
clean at M8, exactly the widening the backlog entry predicted. Those six
retired at M11b, so the weaker tier now has no subject: every committed
fixture is on the current schema and byte-pinned on its charter from birth,
and the two assertions have converged on the same seven orgs. The weaker
assertion is kept anyway, because it is the one that will still hold the
line the next time a charter field is added to a fixture generated before
it. The additive test
deliberately does not count today's gained keys, which would ratify the
drift instead of bounding it. Inertness is enforced by the sibling
assertions, not by introspecting defaults: a charter field whose default
were load-bearing would move the ledgers or the manifest.

**What this closed, measured by fault injection rather than argued.**
Adding `+ 1` to every expense line in `fabric/finance.py` (a corruption of
the ledger this project calls ground truth) passed the *entire*
pre-existing suite green; `test_org_regen.py` fails on it.
`finance.json`, `graph.json`, `mention_map.json`, and `manifest.jsonl` had
no regeneration coverage at all. A fleet diff that cannot fail is
decoration, so re-run an injection before trusting any future edit to this
module — but **not that one**, and this is a correction to the original
contract rather than a restatement of it.

**The `+ 1` injection proves less than it appears to.** Re-run 2026-07-16
against the scoped pin: it produces 17 fixture *errors*, not pin failures,
because `run_fabric` rejects the corrupted ledger against its own tie-out
before `test_org_regen.py` ever compares a byte. It would fail the same way
with no pin at all. It is a fine demonstration that tie-outs work and a
poor one that the diff does.

Use an injection that **ties out cleanly**, which is the only class the pin
is the sole detector of. Both of these are verified to fail the scoped pin
and to pass every other tier:

- Swap two `_EXPENSE_CATEGORIES` weights in `fabric/finance.py` (e.g.
  Travel 0.09 -> 0.08, Professional Services 0.08 -> 0.09). The total is
  unchanged, so every tie-out passes. Fails the ledger pin, 1 test.
- Add a stray `fake.first_name()` before the `is_ceo` assignment in
  `foundation/scaffold.py:_build_people`. This is the reordered-`Faker`-draw
  landmine the module docstring names, and it is semantically invisible:
  every name is still a plausible name. Fails foundation, ledgers, and
  manifest, 3 tests.

Coverage here was partial, not absent, and the difference matters when
deciding what else to add. Two unit tests already pin regeneration as a
side effect of testing knobs, and they caught both of the determinism
landmines M8 names (a reordered `Faker` draw, a re-used
`rng(seed, "foundation.scaffold")` stream):
`test_unit_graph_depth.py::test_default_knobs_leave_v1_roster_identical`
(dev-mini only, and only a projection: id, name, title, reports_to,
email, employment.start) and
`test_unit_affiliation_docs.py::test_knob_off_reproduces_committed_engagements_ledger`
(dev-mini and saltmarsh, `engagements.json` only). They are narrow and
incidental, so leave them alone: they fail with a knob-specific message
that names the actual cause, which a fleet-wide byte diff cannot.
`test_pure_stages_are_deterministic` remains the run-to-run check on
dev-mini and is not redundant with this: it catches nondeterminism within
one code version, which a diff against frozen bytes cannot see.

**Model output drifts by design and is never asserted.** Prose is
replaceable; facts are load-bearing and live in the ledgers. `orgsmith
report` computes proxies with no model (length against the brief's own
`target_words`, same-genre n-gram overlap) into GENERATION-REPORT.md.

**No proxy may become a gate.** This is a measured position, not caution:
in M7 the corpus that scored *lower* same-genre overlap was the worse one,
found twice independently. A similarity threshold would teach the
generator to paraphrase. The metric measures; nothing keys off it.

**The baselines that are safe to add diff against frozen committed bytes,
never against a tuned threshold.** Evals re-emission is tested per fixture
(`test_unit_evals_formats.py:156`, `test_unit_evals.py:468`), as is ACL
re-derivation (`test_unit_acl.py:93`) and now fleet regeneration
(`test_org_regen.py`). `acl.json` is excluded from the regeneration diff
for that reason: it is derived rather than a pure-stage output, and
`test_unit_acl.py` already owns it.

## Human evaluation

`/forge-review` dispatches a read-only board of fresh-context reviewers
across six dimensions; `docs/REVIEW-CALIBRATION.md` records its
calibration. It is the only mechanism reaching cross-document voice, which
no proxy can see, because nothing in the pipeline holds two authored
documents at once.

**It is prompt-enforced and structurally unreachable from the suite**, and
that is a hard rule (CLAUDE.md: "Never LLM-grades-LLM in automated test
tiers"). Three static short-tier tests hold the line:
`test_no_test_tier_invokes_the_review_board`,
`test_review_package_cannot_reach_a_model_or_the_network`, and
`test_no_tier_reads_a_model_api_key`. Board findings are committed beside
the org they judged and never become validator rules.

Known limit, recorded rather than smoothed over: the board has no negative
control, so its false-positive rate is unmeasured (BACKLOG:
`board-negative-control`).

## Environment axis

Two targets running different suites, deliberately.

- **CI (`ubuntu-latest`, no LibreOffice)** is the gate: all three tiers on
  every push and PR. Six legacy tests skip (441 passing + 6 skipped).
  Legacy *validation* is still covered here, by the org tier reading
  `brackenridge-civil`'s real `.doc`/`.xls`/`.ppt` binaries pure-Python
  (olefile, xlrd) with `soffice` absent -- a stronger check than the
  retired cindergrove gave it, since brackenridge runs legacy_ratio 1.0 and
  ships 35 OLE containers against cindergrove's partial mix. Verified
  2026-07-17.
- **Generation box (LibreOffice present)** is the only place legacy
  *conversion* (`render/legacy.py`, `soffice --headless`) is ever
  exercised. `python -m orgsmith doctor` reports `soffice ok`.

Consequence to hold: a regression in legacy conversion is green in CI and
surfaces only at the next legacy generation. Accepted, because generation
only ever happens on a box that runs those six tests.

## What not to test

- **Never an LLM grading an LLM, in any tier.** Not a preference; three
  static tests enforce it.
- **Never a metric threshold as a bar.** No `report` number and no board
  finding becomes a validator rule or an assert. Measured position, above.
- **Never the prose.** Assert on ledgers, manifests, and rendered
  extractable text. A test asserting what a document *says* is testing a
  replaceable artifact.
- **No wall-clock asserts.** Budgets are stated and measured, not gated.
- **No coverage-for-coverage.** The 29-rule validator is the oracle; line
  coverage over renderers adds no catch-power, and no coverage tool is
  configured on purpose.
- **Don't re-assert pydantic.** `test_unit_compat.py` pins *inert-default*
  behavior on existing schema ids, which is a real contract.
  Round-tripping a model to prove pydantic works is not.
- **Don't test soffice.** Legacy tests gate on `shutil.which("soffice")`
  and skip. Never mock the converter to make CI green.

## Adding a test

1. Pick the tier by what it touches: static/config to `short`; anything
   building a synthetic org in `tmp_path` to `unit`; anything reading
   `companies/` to `org`. Set `pytestmark = pytest.mark.<tier>` at module
   top. Two existing unit tests read `companies/` against this rule
   (`test_unit_graph_depth.py`, `test_unit_affiliation_docs.py`); they are
   knob tests that happen to use a committed ledger as their oracle. Follow
   the rule for new tests rather than the precedent, but re-tiering those
   two buys nothing and is not pending work.
2. Build orgs from `tests/conftest.py` helpers (`build_pure_stages`,
   `build_knobbed_stages`, `build_culture_stages`, `build_acl_stages`,
   `build_hardcase_stages`) rather than hand-rolling a recipe. They copy
   `recipes/dev-mini` into `tmp_path` and run the pure stages.
3. Need authored prose? Use `run_enrichment` / `run_authoring`, conftest's
   scripted deterministic stand-ins for the model. Never call a model.
4. New knob? Add a `build_*_stages` helper beside the others, and pin the
   knob-off default in `test_unit_compat.py` on the existing schema id.
5. Module-scoped fixtures are the tier's cost. Reuse an existing org
   fixture before building a new one. In `org`, `test_org_regen.py`'s
   `regenerated` fixture already holds the whole fleet re-derived into
   `tmp_path`; assert against that rather than re-running the stages.
6. Adding a fixture to `companies/` extends every parametrized test in the
   `org` tier automatically, including regeneration. A new fixture needs a
   committed recipe that reproduces it, or
   `test_every_committed_fixture_has_a_recipe` fails, by design: without
   that check a deleted recipe would silently shrink the fleet under test
   instead of failing.
