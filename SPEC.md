# SPEC

## Spec — 2026-07-14 — M3: hard-case planting and extraction evals

**Goal:** Make planted facts hard to find on purpose. Key facts gain location
policies (signature-page-only, filename-only) driven by recipe knobs and
enforced end to end (docplan, authoring ingest, render, validator), and
`emit-evals`/`score` gain an extraction suite so external extractors are
graded on every planted fact, with planted-ambiguity classes tagged so
disambiguation is scoreable rather than only retrieval.

### Acceptance Criteria

- [x] Location policies `signature_page` and `filename` land as additive
  evolution on `orgsmith/manifest-entry@1` (and the ledger `Fact`): committed
  v1 and M2 manifests still load (compat test), both committed orgs validate
  clean without regeneration, and existing determinism and org-tier tests
  stay green (unchanged recipes regenerate byte-identical structure).
- [x] Recipes gain `hard_cases` knobs (at minimum: signature-page-only fact
  count and filename-only date count), documented in docs/RECIPE-FORMAT.md,
  defaulting to zero with no effect: an org generated with the knobs off
  contains only `body` facts. A recipe requesting more hard-case placements
  than eligible facts or documents exist fails at the docplan stage with an
  actionable message (tested).
- [x] Signature-page-only planting holds end to end on page-addressable
  documents (pdf): the fact's rendered surface appears on its document's
  signature page and on no other page's extractable text; authoring ingest
  rejects a deliverable whose body text carries that fact's placeholder or a
  literal rendition of its value; a validator rule fails a corrupted copy in
  both directions (fact leaked into body, fact missing from the signature
  page), proven by corruption tests.
- [x] Filename-only planting holds end to end: the date fact's rendered
  surface appears in the document's filename and nowhere in its extractable
  text; a validator rule fails a corrupted copy in both directions (surface
  present in body, filename missing the surface), proven by corruption tests.
- [x] `python -m orgsmith emit-evals <slug>` additionally writes
  `evals/extraction.jsonl`: one question per planted fact carrying the
  expected value (exact rendered surface), expected source documents, and a
  location tag. Emission works for all orgs, including both existing
  committed fixtures (whose facts are all `body`); re-emission is
  byte-identical; `evals/README.md` documents the extraction answers
  contract.
- [x] `python -m orgsmith score <slug> --suite extraction --answers <file>`:
  answers derived from ground truth score 100% on every committed org; a
  deliberately wrong answers file scores below 100% with per-question
  attribution; a malformed answers file exits non-zero with an actionable
  message; scoring stays a pure function of committed artifacts, offline and
  keyless, working from only the `evals/` directory plus an answers file
  outside the repo (all unit-tested).
- [x] Planted-ambiguity classes (surname-collision, nickname-alias,
  multi-affiliation) appear as tags in emitted eval ground truth, derived
  from the ledgers for any org that exhibits them, including committed
  torchlake-engineering without regenerating its frozen artifacts; `score`
  reports a per-class breakdown alongside the overall score when tags are
  present (unit-tested).
- [x] A recipe with hard-case knobs on and its generated org are committed
  under `recipes/` and `companies/`, containing at least one
  signature-page-only fact and at least one filename-only date fact in
  rendered documents; the org validates clean, the org tier covers all
  committed fixtures, and its ground-truth extraction answers score 100%.
- [x] From a fresh checkout, `bin/test` passes all tiers offline with all
  committed fixtures.

### Context

- Consumed from the 2026-07-14 M2-close proposal. Scope decision this turn:
  ACL overlay, PERMISSIONS.md, and the visibility eval suite were deferred
  to the next turn as a pair (visibility scoring needs the ACL overlay).
- BACKLOG adoption: `mention-ambiguity-tags` was ACTIVE in this spec
  (criterion 7) and shipped.

---
*Prior spec (2026-07-14): M2 people-graph depth, golden evals, second
fixture; all 10 criteria met, shipped as v1.1.0.*

### Proposal (2026-07-15, M3 close)

**What happened.** M3 completed in one overnight turn (7 commits) and
shipped same-day as v1.2.0 (pushed, tagged, GitHub release): location
policies as additive schema evolution, `hard_cases` recipe knobs with a
no-RNG fabric assignment and a docplan gate that fails over-demanding
recipes actionably, three-layer enforcement (briefs exclude non-body facts,
ingest rejects placeholder/literal/long-form leaks, a 3-rule LOC validator
family checks per-page pdf text and filenames both directions), the
extraction eval suite with per-question attribution, ambiguity-class tags
with per-class graph recall, and a third committed fixture
(quillbrook-appraisal, both hard-case knobs on, extraction ground truth
7/7). Review: 0 BLOCK / 0 WARN / 2 NOTEs. Lessons:

- Deriving ambiguity tags at emit time instead of storing them in
  mention_map let frozen torchlake gain tags with zero regeneration:
  "derive, don't store" is the cheap way to upgrade committed fixtures.
- Render-owned injection (fee line plus forced page break) is what made
  "on the signature page and nowhere else" a checkable per-page property.
- The forge workers found a real prompt bug: the work-order example showed
  placeholders without the `f:` prefix and both workers misread it once.
  M2's lesson generalizes: bugs live in the proxy AND the instructions.

**Questions and directions for the next turn:**

- M4: ACL overlay + PERMISSIONS.md + visibility eval suite, deferred from
  M3 as a pair. Key design question: what does the ACL model look like
  (per-folder posture from the reserved `acl_posture` recipe knob,
  dept/role-derived, or per-doc), and what does a visibility question ask?
- `multi-affiliation-in-docs` (revisit fired): era-appropriate dual-employer
  appearances need affiliation-aware participant selection in fabric; could
  ride M4 or the fleet turn.
- Sequencing beyond M4: formats (pptx, eml, scanned PDFs) vs the six-org
  fleet; the name-screen validator is due before fleet authoring.

### Revisit candidates

- `multi-affiliation-in-docs`: its revisit criterion ("M3 ambiguity tagging
  lands") fired this turn.

### Backlog Sweep

- **Delete:** `mention-ambiguity-tags` — shipped this turn (spec 2026-07-14
  criterion 7: ambiguity classes tagged in emitted evals, per-class recall
  in score).

<!-- SPEC_META: {"date":"2026-07-14","title":"M3: hard-case planting and extraction evals","criteria_total":9,"criteria_met":9} -->
