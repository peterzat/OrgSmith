# SPEC

## Spec — 2026-07-16 — M7: the quality instrument (review board, generation provenance, model/effort policy)

**Goal:** Build the first instrument that measures the one thing OrgSmith
promises and does not check: whether the generated prose reads like a real firm
wrote it. Pair a deterministic corpus-metrics proxy with a read-only adversarial
board, record which model and effort authored each org, and settle the size
targets in writing — so the fleet is minted against measured quality instead of
an untracked session setting.

### Acceptance Criteria

- [x] `orgsmith review --sample <slug>` emits a deterministic stratified sample
  (all longform, all planted-fact docs, plus strata across genre × format ×
  decade) drawn from a NEW `seeds.py` stream; two runs are byte-identical, and
  every existing stream is untouched (all seven fixtures still regenerate
  byte-identical pure-stage structure; determinism and compat tests stay green).
  Degrades without crashing when a genre holds one doc, when the org has fewer
  docs than the strata request, and when some docs are unauthored (sampling
  authored docs only); an org with zero authored docs fails with an actionable
  message naming the stage to run.

- [x] `orgsmith report <slug>` computes deterministic corpus metrics with **no
  model**: per-doc word count against the `target_words` the brief asked for, and
  same-genre cross-document n-gram similarity. Verified against a labeled
  positive that exists today: the fernhollow-partners `d0001`/`d0008` engagement
  letters (4-gram Jaccard 0.228, the highest same-genre pair in that fixture)
  appear in the flagged set. Re-running rewrites identical bytes.

- [x] GENERATION-REPORT.md is a derived artifact under
  `companies/<slug>-metadata/`, re-emittable for frozen fixtures, and **never
  enters the share tree or the manifest** — a report written into the share would
  break MAN-01's manifest↔files 1:1 check and the format-mix quota. It renders
  with metrics alone when no board findings have been ingested.

- [x] Generation provenance is recorded as a **record, not an oracle**:
  deliverables carry an optional generator field (the model and effort `/forge`
  dispatched with); ingest stores it per batch in `state.json`; the field
  defaults inert on the existing schema ids so all seven committed fixtures load
  and validate unchanged; an org with no record reports "unrecorded" and fails
  nothing. **No validator rule references it** — it is self-reported and
  unverifiable from artifacts, so a rule would fake a guarantee the system cannot
  make.

- [x] No authoring pass can complete silently: the model and effort are both
  surfaced to the user **before any tokens are spent** and recorded in the org.
  `/forge` Step 0 reports the session model and effort and warns when below the
  documented authoring floor. The floor is stated in exactly one place and
  referenced elsewhere. (Outcome, not mechanism: whether the floor is enforced by
  a per-worker effort lever or by preflight warning plus provenance is an
  implementation choice to be verified against the harness, not assumed.)

- [x] `orgsmith review --ingest <file>` validates findings against a new
  `orgsmith/review-finding@1` schema all-or-nothing, like the authoring ingest:
  it rejects an unknown dimension, an unknown severity, a duplicate finding id,
  and a target doc id absent from the manifest; it reports every problem across
  the file and writes nothing unless the file is clean. Every untrusted string is
  control-stripped with `keep=""` before terminal output (escape-sequence probe
  test; exit codes unchanged).

- [x] `/forge-review <slug>` spawns fresh-context reviewers across the five
  planned dimensions (org realism, finance realism, narrative consistency /
  anachronism, document plausibility, graph and ACL naturalness) **plus
  cross-document voice** — the dimension no fresh-context worker can ever
  self-check, because nothing in the pipeline holds two authored documents at
  once. Reviewers receive validator output first and are instructed not to
  re-litigate deterministic rules. The skill never edits ledgers, manifests,
  prose, or rendered files.

- [x] The board is **calibrated before it is trusted**, against two labeled
  positives measured during spec drafting: fernhollow `d0001`/`d0008` (literal
  reuse, which the metric also catches) and `d0001`/`d0016` (same block structure
  and rhetorical moves, different wording — which the n-gram metric provably
  misses at 4-gram Jaccard 0.037). The outcome for each is recorded: surfaced, or
  documented as a miss with rationale. A board that misses both is not calibrated
  and must be tuned or its limits written down before its findings are relied on.

- [x] `bin/test` never invokes the board, and a test proves it: no tier reaches
  the review or report model-facing entry points, and all tiers stay keyless and
  offline.

- [x] All seven committed fixtures load, validate clean with an unchanged skip
  set, and re-emit their evals byte-identically. No ledger, manifest, or authored
  prose is edited or regenerated.

- [x] `docs/SCALE.md` records the size targets and the reasoning behind them —
  fixtures stay small (regression oracles), a reference fleet at table sizes
  proves breadth, and a single later flagship org carries scale — grounded in the
  measurements that settle it: ~16ms of org-tier cost per validated file, ~30KB
  per modern-format doc, the strictly serial authoring wall, and the
  context-window threshold below which a corpus is not a retrieval problem at
  all. It states that M7 documents these targets and does not build the fleet.

- [x] A documented model/effort A/B: one **non-committed** org authored twice
  under different model and effort settings, both boarded, outcome recorded —
  turning the README's "use the strongest model available" from folklore into a
  default with evidence behind it. If the A/B is inconclusive, that is recorded
  as the finding rather than resolved by assertion.

- [x] From a fresh checkout, `bin/test` passes all tiers offline and keyless,
  with `unit` under ~20s and `org` under ~5s (baseline today: short 0.4s / unit
  17.1s / org 1.7s). CI configuration unchanged: still no LibreOffice.

### Context

- Adopted from `~/.claude/plans/we-ve-done-several-turns-rippling-cosmos.md`;
  read it for the full assessment, the size reasoning, and the sequencing
  argument. Written today against HEAD (44114b4); no drift.

- **The gap this turn closes.** 29 validator rules and 250 tests verify that
  documents agree with their ledgers. None looks at whether the prose is good.
  `tests/conftest.py:203` ships the proof: a scripted author double emitting
  `"Scripted body for status_report dated 2020-09-26..."` passes every ingest
  check and all 29 rules. Its own comment says where realism is supposed to live
  — *"realism comes from the real skills"* — and that layer has no test tier, no
  rubric, and no observer. Of `forge-author`'s six quality bullets, four are
  machine-enforced; the two that carry the product's value proposition ("the
  reader must believe a person at this firm wrote it in that year"; "nothing may
  sound like the same person wrote every document") are enforced by nothing.

- **Proxy and critic find different things — this is measured, not assumed.**
  zat.env's design posture is "more proxy, less critic": critics are cheap and
  weak because they share blind spots with the generator, while proxies catch
  what the generator cannot see. That posture is respected here and it also sets
  the boundary. During spec drafting, a 4-gram shingle metric over
  fernhollow-partners ranked `d0001`/`d0008` top at 0.228 — real literal reuse
  that a human reader had not noticed. The same metric scores `d0001`/`d0016` at
  0.037, yet those two are the pair a reader flags: identical block-kind
  sequence, identical rhetorical moves ("Sandra Perez, Director, [leads/will run]
  the engagement day to day and is your first call"), different wording. **The
  proxy caught what the reader missed; the reader caught what the proxy misses.**
  Neither subsumes the other, which is why this turn builds both and why the
  board's scope is exactly what no proxy reaches. Note the ambiguity the board
  must resolve rather than the metric: real firms genuinely do reuse engagement-
  letter templates, so high same-genre similarity may be realistic. The metric
  measures, the board judges, the human decides. Do not promote either into a
  validator rule this turn — thresholds are unknown, and a rule would fail frozen
  fixtures.

- **Provenance is a record, not an oracle.** Stated as a criterion above and
  repeated here because it is the load-bearing design call: the generator field
  is self-reported and cannot be recomputed from artifacts, so it is categorically
  unlike SCAN-01, LEG-01, or AFF-01, which recompute their claim as tamper
  evidence. Making provenance a rule would both fake that guarantee and fail all
  seven existing fixtures. Report it; never gate on it.

- **The corpus is thin by specification, and nothing checks it.** Measured mean
  across all 81 authored docs: 226 words. `_TARGET_WORDS` (`contexts.py:70`)
  briefs engagement_letter=350, status_report=300, meeting_minutes=220; real
  engagement letters run 800–1500. The model is roughly hitting its targets — the
  targets are wrong. Separately, `target_words` is **never read back**: its only
  two references are its schema default (`schemas.py:542`) and its assignment into
  the brief (`contexts.py:239`). M7 measures this; **raising the targets is M8.**
  Measure before fixing.

- **Scope discipline.** Deliberately out: the `forge-fix` loop (M8, designed
  against real findings rather than imagined ones); raising `_TARGET_WORDS`, voice
  variety, and era naming (M8 — era naming lands after the board precisely because
  anachronism hunting is one of the board's dimensions, so the board is what
  verifies it); parallel authoring and routine/bespoke doc classes (M9); the
  reference fleet (M10); the flagship org (M11); eval difficulty beyond today's
  single-hop lookups (any time — evals are derived, so it applies retroactively
  and is never urgent).

- **Airlock unchanged.** Python still never calls a model or touches the network.
  The board is a skill; `review --ingest` is a validate-and-merge verb of the same
  shape as `author --ingest`. `bin/test` must never reach it — hence the negative
  test. "Never LLM-grades-LLM in automated test tiers" reads as a *permission* for
  skills that nothing has taken up; this turn takes it up, on the skill side of
  the line only.

- **Frozen fixtures.** GENERATION-REPORT.md joins `evals/`, `acl.json`, and
  PERMISSIONS.md as a derived artifact and may be emitted for committed orgs.
  Ledgers, manifests, and authored prose stay frozen. The A/B org is deliberately
  not committed, so it raises no frozen-fixture question.

- **Additive evolution.** New schema fields default inert on existing schema ids;
  new randomness comes only from the new `review.sample` stream. `state.json`
  already varies with prose (it carries `authored_hash`), so recording the
  generator does not disturb the byte-identical guarantee, which covers
  pure-stage structure.

- **Answers three of the four M6 proposal questions.** Era naming → M8 (deferred
  by this spec's sequencing, reversing the reserved-next-turn note in the M6
  Context, by explicit user decision this turn). Fleet scoping → `docs/SCALE.md`,
  where the plan's own contradiction (decision line "fleet ≈2,000 docs" vs recipe
  table ≈360) is resolved by separating breadth from scale. Adversarial review
  board → this turn; note that the proposal framed it as "still wanted, or is the
  deterministic oracle carrying that weight?", and both options there are
  structural — the oracle cannot carry prose weight by construction, so the
  question as posed could not reach the answer. **Still open and uncarried:**
  charter re-dump drift (a committed fixture's `charter.json` gains inert default
  fields when re-derived; harmless today because frozen fixtures are never
  re-written). Worth a `/spec backlog` entry if it should survive this turn.

- **Open review items carried in.** CODEREVIEW.md at HEAD is 0 BLOCK / 0 WARN
  with two NOTEs: `render/__init__.py:28-48` (a `people_index` docstring claiming
  an EML-01 contract that no longer holds — no drift today, but any title- or
  org-derived eml header would make renderer and checker drift silently) and
  `render/pdf.py:37,64` (letterhead lines unescaped under `autoescape=False`;
  recipe-author controlled, no concrete vector).

- **House practices (zat.env).** Verification is the ceiling — but the ceiling it
  sets is over facts; prose has no floor today, which is what this turn installs.
  Small committable increments with tests in the same increment. Precision over
  recall: an empty board report is a valid outcome, and the board must stay silent
  rather than manufacture findings to fill a template. Two kinds of enforcement:
  hard gates for irreversible actions, prompt instructions elsewhere — the board
  is prompt-enforced by nature, which is exactly why it must never gate CI. No
  push or remote mutation without explicit user instruction.

- Environment: Python 3.10-compatible (the box runs 3.10 though `.python-version`
  says 3.12); always `.venv/bin/python`.

---
*Prior spec (2026-07-15): M6 pre-fleet hardening (affiliation-aware docs, name
screen, dev-mini regeneration); all 13 criteria met, shipped as v1.5.0.*

<!-- SPEC_META: {"date":"2026-07-16","title":"M7: the quality instrument (review board, generation provenance, model/effort policy)","criteria_total":13,"criteria_met":13} -->
