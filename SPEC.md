# SPEC

## Spec — 2026-07-15 — M6: pre-fleet hardening (affiliation-aware docs, name screen, dev-mini regeneration)

**Goal:** Clear the deck before the era-naming and six-recipe-fleet turns by
adopting all three backlog items and the M5 review cleanups: multi-affiliation
external people appear in rendered documents under both employers
(era-appropriate per doc date), generated names are mechanically screened
against real firms before an org is committed, and dev-mini stops being the
grandfathered fixture.

### Acceptance Criteria

- [ ] `graph_targets.affiliations_in_docs` lands additively: defaults off on
  the existing schema id, `affiliations_in_docs: true` with
  `multi_affiliations: 0` is a charter error (tested), and the five untouched
  committed fixtures load, validate clean, and regenerate byte-identical
  pure-stage structure (determinism and org tiers stay green).
- [ ] With the knob on, an RNG-free fabric planting pass guarantees every
  multi-affiliation external person participates in at least one engagement
  on each side of their affiliation boundary, reassigning clients
  deterministically and rebuilding client-dependent engagement fields; a
  recipe whose date range or engagement count makes this impossible fails at
  fabric with an actionable message (both tested).
- [ ] With the knob on, an engagement's external participants always hold an
  affiliation to its client that covers the engagement window including the
  letter lead-in, and rendered signature blocks and authoring briefs show the
  employer matching each document's date (a rendered doc on each side of a
  boundary is tested for the era-correct employer name).
- [ ] AFF-01 recomputes clients and external participants from charter plus
  foundation and fails a tampered participant, a shifted affiliation window,
  or an undone reassignment; AFF-02 fails when a multi-affiliation person no
  longer appears under both employers or when affiliations are stripped with
  the knob on; both skip visibly only when the knob is off (corruption-tested
  in both directions).
- [ ] NAME-01 screens the charter name and domain, external org names, and
  all internal and external person names against a committed real-firm source
  list using deterministic, stdlib-only normalization and matching; the rule
  runs on every org with no grandfather, and all committed fixtures pass it
  (unit and org tiers).
- [ ] The name screen also gates generation: the charter and scaffold stages
  fail with an actionable message before any model pass when a name collides,
  and the recipe pre-commit checklist in docs/RECIPE-FORMAT.md and the /forge
  skill reference the check (screen tested positive and negative).
- [ ] SCAN-02's page-count read and LEG-01's OLE read yield findings instead
  of tracebacks on crafted artifacts, and the ingest and score failure
  printers strip control characters from untrusted strings before terminal
  output (tested with an escape-sequence probe; exit codes unchanged).
- [ ] dev-mini is regenerated from its recipe with the seed unchanged and
  `min_mentions_per_person: 1` added: the roster, engagement, and document
  identities reproduce exactly, the fixture now carries mention ground truth,
  the ACL overlay, and visibility evals, and it validates clean with MENT and
  GRAPH rules running (no mention grandfather skips).
- [ ] The mention grandfather mechanism survives dev-mini's regeneration: an
  org without mention ground truth still skips visibly (tested on a synthetic
  org), and the additive-evolution compat tests are rebased onto synthetic
  old-shape artifacts instead of reading dev-mini.
- [ ] A new fixture is committed whose recipe sets `multi_affiliations: 1`
  and `affiliations_in_docs: true` with engagements on both sides of the
  boundary; it validates clean with the AFF and NAME rules running unskipped,
  its extraction ground truth scores 100%, its graph carries dated works_at
  edges and the multi-affiliation ambiguity tag, and it uses modern formats
  only.
- [ ] The all-knobs test org exercises AFF-01 and AFF-02 alongside every
  other charter-gated rule (its visible skips remain exactly LEG-01).
- [ ] The five untouched fixtures re-emit their evals byte-identically,
  pyproject.toml's version matches `orgsmith.__version__`, and the docs
  (RECIPE-FORMAT.md knob reference, README rule count and fixture list)
  reflect the new knob, rules, and fixtures.
- [ ] From a fresh checkout, `bin/test` passes all tiers offline and keyless
  with all seven committed fixtures (CI configuration unchanged: still no
  LibreOffice).

### Context

- Adopted from `~/.claude/plans/pass-this-plan-output-vast-rabbit.md`; read
  it for the full design: the planting algorithm and its shared pure helpers,
  name-screen normalization and matching rules, the dev-mini regeneration
  procedure and test migrations, increment order, and risks. The plan was
  written today against HEAD; no drift.
- All three BACKLOG.md entries are annotated ACTIVE in this spec. They are
  deleted at turn close when shipped, leaving the register clear going into
  the era-naming and fleet turns. Era naming (`naming_style`, `it_maturity`)
  stays reserved for its own turn by explicit user decision.
- The doc-facing behavior must gate on the new knob, never on
  `multi_affiliations`: torchlake-engineering is frozen with
  `multi_affiliations: 1` and would fail a covering-affiliation check.
- The planting pass consumes no randomness. RNG-freeness is what lets AFF-01
  recompute assignments as tamper evidence; if tie-breaking randomness is
  ever wanted, it must come from a new seeds.py stream.
- The frozen-fixture rule is deliberately waived for dev-mini only, per the
  adopted backlog item. The other five committed fixtures must not be edited
  or regenerated; their ledgers and evals are the regression oracles.
- Model passes (dev-mini re-authoring, new fixture authoring) run only
  through /forge and forge-author; the airlock is unchanged. Both fixtures
  are modern-format only, so CI stays LibreOffice-free.
- M4's grandfathering lesson binds the AFF rules: skip only when the charter
  says the knob is off; a knob that is on with artifacts missing or tampered
  is a failure. NAME-01 deliberately has no grandfather: it reads only
  charter and foundation, which every org has.
- Known residual, documented rather than solved: an external person's email
  keeps the current-employer domain even on prior-era documents (the ledger
  owns a single email field).
- House practices (zat.env): small committable increments with tests in the
  same increment; verification stays the ceiling (validator and evals are
  deterministic oracles, never a model's opinion); no push or remote
  mutation without explicit user instruction.

---
*Prior spec (2026-07-15): M5 document formats (pptx, eml, scanned, legacy);
all 12 criteria met, shipped as v1.4.0.*

<!-- SPEC_META: {"date":"2026-07-15","title":"M6: pre-fleet hardening (affiliation-aware docs, name screen, dev-mini regeneration)","criteria_total":13,"criteria_met":0} -->
