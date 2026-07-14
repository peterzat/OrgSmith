# SPEC

## Spec — 2026-07-14 — M3: hard-case planting and extraction evals

**Goal:** Make planted facts hard to find on purpose. Key facts gain location
policies (signature-page-only, filename-only) driven by recipe knobs and
enforced end to end (docplan, authoring ingest, render, validator), and
`emit-evals`/`score` gain an extraction suite so external extractors are
graded on every planted fact, with planted-ambiguity classes tagged so
disambiguation is scoreable rather than only retrieval.

### Acceptance Criteria

- [ ] Location policies `signature_page` and `filename` land as additive
  evolution on `orgsmith/manifest-entry@1` (and the ledger `Fact`): committed
  v1 and M2 manifests still load (compat test), both committed orgs validate
  clean without regeneration, and existing determinism and org-tier tests
  stay green (unchanged recipes regenerate byte-identical structure).
- [ ] Recipes gain `hard_cases` knobs (at minimum: signature-page-only fact
  count and filename-only date count), documented in docs/RECIPE-FORMAT.md,
  defaulting to zero with no effect: an org generated with the knobs off
  contains only `body` facts. A recipe requesting more hard-case placements
  than eligible facts or documents exist fails at the docplan stage with an
  actionable message (tested).
- [ ] Signature-page-only planting holds end to end on page-addressable
  documents (pdf): the fact's rendered surface appears on its document's
  signature page and on no other page's extractable text; authoring ingest
  rejects a deliverable whose body text carries that fact's placeholder or a
  literal rendition of its value; a validator rule fails a corrupted copy in
  both directions (fact leaked into body, fact missing from the signature
  page), proven by corruption tests.
- [ ] Filename-only planting holds end to end: the date fact's rendered
  surface appears in the document's filename and nowhere in its extractable
  text; a validator rule fails a corrupted copy in both directions (surface
  present in body, filename missing the surface), proven by corruption tests.
- [ ] `python -m orgsmith emit-evals <slug>` additionally writes
  `evals/extraction.jsonl`: one question per planted fact carrying the
  expected value (exact rendered surface), expected source documents, and a
  location tag. Emission works for all orgs, including both existing
  committed fixtures (whose facts are all `body`); re-emission is
  byte-identical; `evals/README.md` documents the extraction answers
  contract.
- [ ] `python -m orgsmith score <slug> --suite extraction --answers <file>`:
  answers derived from ground truth score 100% on every committed org; a
  deliberately wrong answers file scores below 100% with per-question
  attribution; a malformed answers file exits non-zero with an actionable
  message; scoring stays a pure function of committed artifacts, offline and
  keyless, working from only the `evals/` directory plus an answers file
  outside the repo (all unit-tested).
- [ ] Planted-ambiguity classes (surname-collision, nickname-alias,
  multi-affiliation) appear as tags in emitted eval ground truth, derived
  from the ledgers for any org that exhibits them, including committed
  torchlake-engineering without regenerating its frozen artifacts; `score`
  reports a per-class breakdown alongside the overall score when tags are
  present (unit-tested).
- [ ] A recipe with hard-case knobs on and its generated org are committed
  under `recipes/` and `companies/`, containing at least one
  signature-page-only fact and at least one filename-only date fact in
  rendered documents; the org validates clean, the org tier covers all
  committed fixtures, and its ground-truth extraction answers score 100%.
- [ ] From a fresh checkout, `bin/test` passes all tiers offline with all
  committed fixtures.

### Context

- Consumed from the 2026-07-14 M2-close proposal. M2 shipped mention ground
  truth, the 16-rule validator, golden retrieval/graph evals, and the
  torchlake-engineering fixture; version 1.1.0 is reviewed and gate-ready
  but NOT pushed. The push/release decision remains with the user.
- Scope decision this turn: ACL overlay, PERMISSIONS.md, and the visibility
  eval suite are deferred to the next turn as a pair (visibility scoring
  needs the ACL overlay to exist). This turn is the extraction half of the
  hard-case milestone.
- BACKLOG adoption: `mention-ambiguity-tags` is ACTIVE in this spec
  (criterion 7). Its sibling `multi-affiliation-in-docs` stays deferred; its
  revisit criterion fires once ambiguity tagging lands, so expect it at the
  next turn boundary. Class tags are limited to what the knobs actually
  plant today; the cross-org-duplicate class waits for a knob that plants it.
- Committed fixtures are frozen: ledgers, manifests, and authored prose are
  never edited by hand and torchlake is not regenerated this turn. The
  `evals/` directories are derived artifacts and may be re-emitted (that is
  how torchlake gains extraction questions and ambiguity tags). dev-mini
  stays grandfathered with visible skip notices, the pattern that worked in
  M2.
- Additive evolution discipline: new scaffold behavior draws from NEW seed
  streams gated by recipe knobs so unchanged recipes regenerate
  byte-identically; schema changes stay optional-with-defaults on
  `orgsmith/manifest-entry@1`. The M2 review lesson binds here too: the
  interesting bugs live in the PROXY, so matcher and validator semantics
  (page scoping, filename absence checks) deserve adversarial tests in both
  directions, not just happy-path presence checks.
- Signature-page scoping is only verifiable where extraction is
  page-addressable, which today means pdf (docx extraction has no page
  boundaries). The planting engine must only assign filename policy to
  facts whose rendered surface is filename-safe (date facts qualify).
- The new fixture's authoring runs through the same airlock flow as v1 and
  M2 (emit work order, author, ingest, render per batch, via /forge). No
  LLM grading in automated test tiers: `emit-evals`, `score`, and
  `validate` read committed files only. The fixture's name must not
  resemble a real firm; the name-screen validator stays deferred.
- House practices: small committable increments with tests in the same
  increment; verify the suite is green before starting; no push or remote
  mutation without explicit user instruction.

---
*Prior spec (2026-07-14): M2 people-graph depth, golden evals, second
fixture; all 10 criteria met, shipped as v1.1.0, gate-ready, not pushed.*

<!-- SPEC_META: {"date":"2026-07-14","title":"M3: hard-case planting and extraction evals","criteria_total":9,"criteria_met":0} -->
