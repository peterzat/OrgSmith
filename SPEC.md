# SPEC

## Spec — 2026-07-14 — M2: people-graph depth, golden evals, second fixture

**Goal:** Make the people graph a first-class, verifiable product surface:
recipe-dialable graph ambiguity (collisions, aliases, multi-affiliation),
mention ground truth tied to rendered text, and deterministic golden evals
(`emit-evals`/`score`) so external KB/people-graph systems can be graded
against a generated org with zero LLM involvement. A second committed org
proves recipe generality, the bug class the v1 review caught.

### Acceptance Criteria

- [x] Charter `graph_targets` gains ambiguity knobs (at minimum: minimum
  mentions per internal person, surname-collision count, nickname-alias
  count, multi-affiliation count), all additive with defaults that change
  nothing: the committed dev-mini org still validates clean without
  regeneration, and regenerating dev-mini from its unchanged recipe remains
  byte-identical for structure (existing determinism and org-tier tests stay
  green).
- [x] A second recipe with a different shape (different departments/titles,
  modern era) is committed under `recipes/` and its generated org under
  `companies/`, with: at least one surname-collision pair on the roster, at
  least one person whose nickname alias appears in rendered document text,
  and at least one external person with time-bounded affiliations to two
  organizations. The org validates clean and the org tier covers both
  fixtures.
- [x] Docplan emits a mention map (`ledger/mention_map.json`): per doc, the
  entities expected in it and the exact surface forms planted (full names,
  nicknames, org names). A validator rule fails when a planned surface form
  is absent from the doc's extractable text, and another fails when a
  mention references an entity absent from the graph ledger (no dangling
  mentions). Both proven by corruption tests.
- [x] A GRAPH validator family (>= 4 rules) runs in `orgsmith validate`:
  mention coverage vs the recipe's minimum-mentions knob, no orphan roster
  member (zero planned mentions), no dangling graph edge endpoints, and
  per-type edge counts within recipe-derived bounds. Each rule fails on a
  deliberately corrupted copy (tested).
- [x] Manifest evolution is additive: entries may carry planned mentions and
  key-fact location metadata while `orgsmith/manifest-entry@1` stays
  readable; the committed v1 dev-mini manifest still loads (compat test).
  Validator rules that need mention artifacts skip gracefully, with a
  visible notice, on orgs generated before this turn.
- [x] `python -m orgsmith emit-evals <slug>` writes `evals/retrieval.jsonl`
  (>= 12 questions per org, each with expected_docs and tags derived from
  planted facts and mentions), `evals/graph_expected.json` (canonical
  entities with alias credit plus typed edges), and `evals/README.md`
  documenting the answers-file contract so an external author needs no
  OrgSmith source. Re-emission is byte-identical.
- [x] `python -m orgsmith score <slug> --suite retrieval --answers <file>`:
  answers derived from ground truth score 100%; a deliberately wrong answers
  file scores below 100% with per-question attribution; the graph suite is
  scored as precision/recall with alias credit; a malformed answers file
  exits non-zero with an actionable message. All covered by unit tests.
- [x] Decoupling holds: `emit-evals` and `score` are pure functions of
  committed artifacts, run offline and keyless, involve no model anywhere,
  and `score` works when given only the `evals/` directory and an answers
  file copied to a location outside the repo (tested).
- [x] Hardening: WeasyPrint rendering cannot fetch remote resources (a
  document whose HTML references an external URL renders without any
  network access, tested), and CI workflow actions are pinned to commit
  SHAs.
- [x] From a fresh checkout, `bin/test` passes all tiers offline with both
  committed fixtures.

### Context

- Consumed from the 2026-07-14 turn-close proposal (M0+M1 shipped as public
  v1.0.0; two recipe-generality bugs found and fixed in review; retrospective
  correction: that turn ran at `/effort xhigh`).
- Bitter-lesson framing that binds this turn: verification quality is the
  ceiling. Mention-echo and fact-echo are proxies computed against rendered
  files; the eval suites are the oracle for external systems. Do not add LLM
  critics to automated paths; model passes stay inside skills. Generation
  and evaluation must not share session context: `emit-evals`, `score`, and
  `validate` read committed files only, and authoring continues to run
  through the airlock in forked worker contexts with file-derived resume.
- Additive evolution discipline: `seeds.py` streams are stable under new
  consumers; new scaffold features must draw from NEW seed streams gated by
  recipe knobs so unchanged recipes regenerate byte-identically. Schema
  changes must be optional-with-defaults on `orgsmith/manifest-entry@1`;
  landing mentions and key-fact location together now avoids a breaking
  bump when hard-case location policies arrive (next milestone).
- The committed dev-mini org is grandfathered: it predates mention ground
  truth and must not be regenerated this turn (its prose is keyed to its
  manifest). Capture the "regenerate dev-mini with mention ground truth"
  item in BACKLOG.md at turn close rather than doing it now.
- Second-recipe authoring runs through the same airlock flow as v1 (emit
  work order, author deliverable, ingest, render per batch). The name must
  not resemble a real firm; keep the plan's name-screen validator deferred.
- House practices: small committable increments with tests in the same
  increment; never modify committed fixtures by hand; no push without
  explicit user instruction this turn (leave the tree reviewed and
  gate-ready instead).

---
*Prior spec (2026-07-14): M0+M1 scaffold and dev-mini tracer bullet; all 10
criteria met, shipped as public v1.0.0.*

### Proposal (2026-07-14, M2 close)

**What happened.** M2 completed autonomously in one evening turn (10
commits, version 1.1.0, reviewed and gate-ready but NOT pushed): recipe
ambiguity knobs with byte-stable defaults, mention ground truth
(mention_map.json + manifest mentions) enforced at authoring ingest and
re-verified against rendered text, a 16-rule validator with visible
availability skips, golden evals (`emit-evals`/`score`) that grade external
systems from a bare `evals/` directory with alias credit, both v1 security
NOTEs closed, and a second committed fixture (torchlake-engineering, every
knob on) whose ground-truth answers score 16/16. Lessons:

- The interesting review catch was in the PROXY, not the data: substring
  mention matching let "Jen" pass via "Jennifer", so the alias check could
  succeed vacuously. Echo-proxies need adversarial review of the matcher
  itself; word-boundary semantics now live in one shared helper.
- Enforcing mentions at two layers (ingest on DocIR, validator on rendered
  text) made tightening the matcher safe to land against committed
  fixtures: the org tier proved both orgs genuinely contain standalone
  surfaces.
- Grandfathering with visible SKIP notices worked well: dev-mini stays
  untouched and honest about what it predates.

**Questions and directions for the next turn:**

- M3 hard cases is the natural next milestone: key_facts.location policies
  (signature-page-only, filename-only), the planting engine, and
  extraction/visibility eval suites. The `mention-ambiguity-tags` and
  `multi-affiliation-in-docs` BACKLOG entries ride the same schema wave.
- ACL overlay + PERMISSIONS.md pairs with the visibility suite; decide
  whether they land together or ACL leads.
- Release question for the user: v1.1.0 is tagged-ready (semver bumped,
  README current, review marker written). Push + GitHub release, or hold?
- BACKLOG has four entries (all kept at sweep); `regenerate-dev-mini-
  mentions` waits on a migration verb or the fleet turn.

<!-- SPEC_META: {"date":"2026-07-14","title":"M2: people-graph depth, golden evals, second fixture","criteria_total":10,"criteria_met":10} -->
