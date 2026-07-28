# SPEC

## Spec — 2026-07-23 — M16: regenerate the fleet under the wave's knobs, re-freeze, cut the release

**Goal:** Close the realism wave. Turn the M13-M15 capabilities on across the
whole committed fleet by regenerating all eight orgs once each under updated
recipes, prove the two capability-only mail-brief fixes on real fixtures,
board the regenerated fleet, re-freeze (restore `PINNED = SLUGS` fleet-wide
and replace the carve-out with M11b-style closure), and cut a versioned
release with an installable package and a reproducible generation container.

### Acceptance Criteria

- [x] **Recipes updated to the wave's final knobs.** The six fleet recipes
  gain the baseline realism layer (`business_calendar`, `book_is_sample`,
  `style_specs`, `voice_diversify`) plus their demonstrators: real mail
  threads (`doc_culture.mail`) on `hollowell-ip` and `meridian-actuarial`,
  and the full organizational-noise suite on the exemplar
  `northgate-staffing`. `ashcombe-advisory` and `calderwood-partners` gain the
  baseline knobs they lack (both add `style_specs`; `ashcombe` adds
  `voice_diversify` and `exempt_author_mentions`). Every updated recipe passes
  `test_fleet_recipe_growth_headcount_and_span_describe_one_firm` (growth,
  headcount, and span describe one firm; terminal net margin under the 0.40
  ceiling) and derives with no error. No recipe brief recites its own genre
  specifications as firm philosophy (closes `recipe-brief-leaks-genre-spec`).

- [x] **All eight orgs regenerated wholesale, live through the airlock.** Each
  org is deleted and re-run end to end from its recipe via `/forge` on
  `claude-opus-4-8[1m]` at effort `xhigh` (never an in-place edit of ledgers,
  manifest, or prose); each validates green (every rule its recipe enables, 0
  errors), scores 100% on all four eval splits (`core`, `distractors`,
  `noise`, `full`), and is committed with its `GENERATION-REPORT.md`. The same
  recipe re-derives each org's structure (`foundation.json`, `ledger/`,
  `docplan/manifest.jsonl`, charter) byte-identically. `PINNED = SLUGS` is
  green at every commit, including between orgs mid-wave.

- [x] **Weekend and holiday meetings gone.** Every regenerated fleet org
  declares a `business_calendar`; `CAL-01` passes; no `meeting_minutes` and no
  engagement mail lands on a weekend or a declared holiday. The exemplar's
  previously-cited Saturday 2016-05-28 and 2023-07-04 client working sessions
  no longer occur. Closes `docplan-has-no-business-day-calendar` for the
  regenerated fleet.

- [x] **Overviews stop overstating the book.** Every regenerated fleet org
  declares its engagement ledger a sample (`book_is_sample`); no firm overview
  claims its engagements are the whole business, and no overview contradicts
  the finance ledger's revenue by an order of magnitude. Closes
  `engagement-ledger-reads-as-whole-book` for the regenerated fleet.

- [x] **Reporting-line drift cleared in prose.** Regenerated onboarding and
  org-describing prose names no supervisor the ledger's `reports_to` edge
  contradicts, verified live on fresh prose by the M12 ingest check
  (`authoring/ingest.py::_check_reporting_line`). Closes `reporting-line-drift`
  for the regenerated fleet.

- [x] **Voice mitigation fleet-wide, measured never gated.** `style_specs` and
  `voice_diversify` are on for every regenerated fleet org; per-author proxy
  metrics and same-genre similarity are reported as ranges in each
  `GENERATION-REPORT.md` and aggregated in `docs/DISTRIBUTIONS.md`; no voice or
  realism number gates any test tier (the static no-LLM-grades-LLM guard stays
  green). `cross-document-voice` stays measured and published as the standing
  hard problem; the fleet-wide mitigation's effect is recorded as a range, not
  asserted as a fix.

- [x] **The two mail-brief fixes proven on regenerated fixtures.** (a) On a
  regenerated org with mail threads (`ashcombe-advisory`, `hollowell-ip`,
  `meridian-actuarial`), a client-delivered reply reads in a client-appropriate
  register: the board reads the regenerated prose and the
  internal-note-delivered-to-the-client finding does not recur (closes the
  fixture half of `mail-audience-internal-vs-external`). (b) With
  `exempt_author_mentions` on (`ashcombe-advisory`), a mundane-email author no
  longer names themselves in the third person in the body; the render-time
  signature still names the author and validation still passes (closes the
  fixture half of `mundane-email-author-self-names`).

- [x] **The board reads all eight.** `/forge-review` dispatches the
  six-dimension board across all eight regenerated orgs; findings merge into
  each org's `GENERATION-REPORT.md`. Every finding quoted anywhere outside the
  raw `review/findings/` files is hand-verified against a ledger before
  publication (the wave's standing rule, because `board-negative-control`
  stays open and the false-positive rate stays unmeasured). The board remains
  read-only and never authored what it reviewed; the static test proving no
  automated tier can reach the board stays green.

- [x] **Re-freeze.** `PINNED = SLUGS` is enforced fleet-wide with every
  regenerated org pinned; CLAUDE.md's realism-wave carve-out paragraph is
  replaced with closure language mirroring M11b (additive evolution restored:
  any post-wave capability defaults off with inert schema defaults and new
  `seeds.py` streams, proven inert against the frozen fleet before any org
  turns it on). The README's fleet numbers, the "which fixture proves what"
  knob table, the "what is not modeled today" findings, `docs/DISTRIBUTIONS.md`,
  and TESTING.md's cold-open counts all move together to the regenerated
  reality, with no stale pre-regeneration number or retired-defect quote
  surviving anywhere in tree.

- [x] **The wave's deltas are visible in git.** The M15-committed frozen-fleet
  distributions are compared against the regenerated fleet in
  `docs/DISTRIBUTIONS.md` as a committed before/after (weekend rate, fee/revenue
  prose posture, per-author voice ranges, noise proportion), so the effect of
  turning the wave's knobs on is a diff rather than a claim.

- [x] **Release cut.** `pyproject.toml` gains `[build-system]`,
  `[project.scripts]` (a console entry point for `orgsmith`), and
  `[project.dependencies]` so `pip install .` succeeds from a clean venv;
  runtime dependencies are hash-locked (or the residual float is stated
  explicitly); a container image builds the generation environment
  (WeasyPrint/Pango plus LibreOffice) and `python -m orgsmith doctor` reports
  green inside it; a versioned `v2.1` tag with a committed checksum manifest of
  the eight orgs is created. DOI-backed archival is out (it requires an
  external service and cannot be done offline) and stays in
  `packaging-and-archival`. Closes the local half of `packaging-and-archival`.

- [x] **Tests, docs, cost, and provenance.** Full `bin/test` (short + unit +
  org + `flagship`) green, keyless and offline, with the byte pin green at
  every commit including mid-wave; `docs/RECIPE-FORMAT.md` reflects any
  knob-surface changes; the pre-rename working name appears nowhere
  (`test_short` green). Each org's `GENERATION-REPORT.md` records the model,
  effort, and batch count that authored it; the total batch/token cost of the
  ~600-document regeneration is recorded (README or the reports) as a measured
  figure once the run completes, not a pre-estimate.

### Context

- **Consumed from the 2026-07-23 M15-close proposal**, itself the last turn of
  the approved M13-M16 realism wave (`~/.claude/plans/we-ve-gotten-to-a-squishy-torvalds.md`).
  The wave's capabilities all exist and are proven inert (M12-M15); M16 does
  no new capability work — it turns knobs on via recipe edits and regenerates.
  The two mail-brief fixes are the one exception: they exist gated and
  unit-tested since M15 with `exempt_author_mentions: false` everywhere, and
  their fixture proof was scoped to here.

- **The knob assignment (user decision, 2026-07-23).** Chosen strategy:
  baseline realism fleet-wide plus targeted demonstrators, so the "each
  fixture proves a different axis" table stays meaningful rather than every
  org carrying everything.

  | org | business_calendar | book_is_sample | style_specs | voice_diversify | mail threads | noise |
  | --- | --- | --- | --- | --- | --- | --- |
  | `brackenridge-civil` | ✓ | ✓ | ✓ | ✓ | — | — |
  | `hollowell-ip` | ✓ | ✓ | ✓ | ✓ | ✓ | — |
  | `meridian-actuarial` | ✓ | ✓ | ✓ | ✓ | ✓ | — |
  | `northgate-staffing` (exemplar) | ✓ | ✓ | ✓ | ✓ | — | ✓ |
  | `saltmarsh-environmental` | ✓ | ✓ | ✓ | ✓ | — | — |
  | `verdant-health` | ✓ | ✓ | ✓ | ✓ | — | — |
  | `ashcombe-advisory` (pilot) | ✓ | ✓ | ✓ (add) | ✓ (add) | ✓ + `exempt_author_mentions` | ✓ (full) |
  | `calderwood-partners` (pilot) | ✓ | ✓ | ✓ (add) | ✓ | — | dup/drafts |

  `exempt_author_mentions: true` goes wherever a mail block carries
  `mundane_emails > 0`. The exemplar finally carries organizational noise; the
  two mail demonstrators (`hollowell`, `meridian`) are where the fleet's
  engagement mail becomes real threads rather than single "Email 1" messages.

- **The exemplar's identity changes, and the README moves with it.** The
  README's "what is not modeled today" section quotes `northgate-staffing`'s
  specific defects at length (the Saturday and July-4 meetings, "$425,500 vs
  $2,469,000", the "Two asks" and "Workstreams" tics, the reporting-line
  drift). Regenerating northgate with `business_calendar`, `book_is_sample`,
  the voice layer, and noise fixes three of those on the exemplar itself, so
  every one of those quotes goes stale and must be rewritten to the
  regenerated reality — the board finds new things, and the section says what
  they are. This is the largest doc-drift surface in the turn (criterion 9).

- **Pressure-test edges.** (1) Prose is model-authored and is *not*
  byte-pinned — only structure is (`foundation`, `ledger`, `manifest`,
  charter). Regeneration commits new prose and re-pins the new structure;
  "regenerates byte-identically" always means structure, never prose. (2)
  Turning a knob on (a calendar, sample posture, noise) legitimately moves the
  manifest and ledgers, because it is a wholesale re-run under a *new* recipe;
  the new committed structure becomes the new pin baseline and re-derives from
  the new recipe. This is expected, not a pin break. (3) `PINNED = SLUGS` is
  green *at every commit*: regenerate one org fully (delete, re-run, validate,
  report, board), commit it, confirm the pin, then move to the next — the
  working tree may hold a half-regenerated org between commits, but no commit
  ever ships one. (4) `book_is_sample` fixes the overview *prose posture*; it
  does not couple `base_revenue` to the engagement book, so
  `recipe-coherence-test-has-no-floor` stays hypothetical and is not adopted.

- **Board scope (user decision, 2026-07-23): all eight.** The largest board
  surface yet. `board-negative-control` stays open — boarding a fresh fleet is
  not a measured false-positive rate — so the standing mitigation holds: every
  finding carried into any README, report summary, or doc is re-verified
  against a ledger by hand before it is published. `concurrent-workers-share-one-scratchpad`
  bites a board dispatched across more than one org at once; `/forge-review` is
  per-slug, so eight single-org boards is eight isolated runs, not one
  cross-org dispatch — but each `/forge` and `/forge-review` worker must still
  namespace its scratch by work order.

- **Release scope (user decision, 2026-07-23): re-freeze plus cut the
  release.** `pip install .`, hash-locked deps, a generation container, and a
  `v2.1` tag with checksums (criterion 11). DOI archival is out (offline
  constraint). `provider-neutral-authoring-driver` stays deferred despite the
  packaging turn: its own entry scopes it out of the M13-M16 wave, and no
  external consumer yet exists to shape its adapter surface.

- **Cost.** ~600 documents of live authoring across eight orgs — the largest
  authoring turn in the project. `/forge` is resumable from `state.json`, so a
  killed session resumes with no duplicated or lost documents; the wave
  proceeds org by org, committing each as it lands so the pin stays green and a
  crash never loses more than one in-flight org.

- **The airlock is untouched.** Python never calls a model or the network; no
  LLM grades an LLM in any automated tier; the noise stages spend zero tokens
  by construction. CI has no LibreOffice, no model, no network, no key, no wall
  clock — every committed fixture (legacy binaries included) validates
  pure-Python. LibreOffice is required on the *generation* box for
  `brackenridge-civil`'s legacy binaries and inside the release container;
  `python -m orgsmith doctor` must report `soffice ok` before its regeneration.

- **House practices (zat.env).** Small committable increments with tests in
  the same increment; run the relevant tier after each functional change. If
  two consecutive fix attempts fail, revert and re-evaluate. Never modify a
  test to accommodate a regression. Do not remove, reword, or reorder
  acceptance criteria; only check them off when verified.

- **Execution (user directed autonomous implementation + push).** Order:
  update the eight recipes and confirm each derives and coheres; regenerate
  org by org (recipe edit → `/forge` → validate → score → report → board →
  commit, pin green each time); then re-freeze (CLAUDE.md closure, README/docs
  reconciliation, DISTRIBUTIONS before/after); then cut the release (packaging,
  container, tag). Final `push` triggers the pre-push `/codereview` gate; run
  it when it blocks.

---
*Prior spec (2026-07-22): M15 — organizational noise v2, persona voice v2, and
the two-dashboard split; 15/15 criteria met, dev-mini regenerated once and the
frozen-fleet distributions committed so this turn can show deltas.*

### Proposal (2026-07-28)

**What happened.** M16 closed, 12/12. All eight fleet orgs were regenerated
wholesale under the realism wave's knobs (business calendar, sample book,
style/voice, mail threads, noise), validated 100%, byte-pinned, and boarded
across six dimensions; the carve-out closed and the fleet re-froze. The docs
reconciled to the regenerated reality (README "what is not modeled," the
exemplar commentary, a retail-cost estimate ~$30, a committed DISTRIBUTIONS
before/after). Then three follow-up fixes landed: the hollowell duplicated-header
mail blocker (the renderer strips a `To:/Cc:` body banner; eml `doc_text` now
reads the transport headers so MENT-01 still finds the recipient), the
genre-spec brief leak (three briefs reworded, charters re-derived surgically with
no re-authoring), and the **v2.1.0** release cut (`pip install .`, a generation
Dockerfile built and verified green, `CHECKSUMS.md`, a pushed `v2.1.0` tag).
Everything pushed; suite green (14/520/74 + 20 flagship).

**Questions and directions.**
- **M17, the window-defeating flagship?** The long-planned ~2,000-document org
  that makes retrieval genuinely hard (a real denominator inside a 1M-token
  window). The README and the calderwood pilot point straight here — what recipe
  shape and cost envelope?
- **The mail full-name-in-body device.** The render-strip fixed hollowell's
  banner, but meridian/ashcombe still weave the recipient's full name into prose
  ("for the file, [Full Name]"). Now that `doc_text` reads the headers, the
  authoring guidance could drop the device — a re-render or a re-gen question.
- **board-negative-control** stays open: boarding a fresh fleet is not a measured
  false-positive rate, and a negative control is overdue.
- **provider-neutral-authoring-driver:** the package ships now, so an external
  consumer could finally shape the adapter surface.
- Minor: the hollowell list-marker double-bullet, the mail-audience capability
  half (mixed internal/external threads), and the security NOTE (constrain
  `ManifestEntry.path` against `/`-absolute and `..`).

**Backlog Sweep** (pending approval):
- **Delete:** `recipe-brief-leaks-genre-spec` — closed this turn (briefs reworded).
- **Delete:** `engagement-ledger-reads-as-whole-book` — closed (book_is_sample fleet-wide).
- **Delete:** `docplan-has-no-business-day-calendar` — closed (business_calendar + CAL-01).
- **Delete:** `reporting-line-drift` — closed for the regenerated fleet (ingest check).
- **Delete:** `mundane-email-author-self-names` — closed (exempt_author_mentions).

<!-- SPEC_META: {"date":"2026-07-23","title":"M16: regenerate the fleet under the wave's knobs, re-freeze, cut the release","criteria_total":12,"criteria_met":12} -->
