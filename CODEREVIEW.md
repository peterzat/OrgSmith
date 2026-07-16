# CODEREVIEW

## Review — 2026-07-16 (commit: 7cd134b)

**Summary:** Refresh review of the unpushed M10 arc (the concurrent-batch
airlock for parallel authoring) plus this turn's live-authoring de-risk, scope
`origin/main..HEAD` with focus since the prior review (c013c06, M9). Focus set,
full depth: `orgsmith/airlock.py` (emit/match/clear_author_batch),
`orgsmith/state.py` (BatchRef + author_batches), `orgsmith/authoring/contexts.py`
(pick_batch exclude), `orgsmith/authoring/ingest.py` (per-batch match/clear),
`orgsmith/status.py` (author_batches surfacing), the `/forge` and `/forge-author`
skills, the M10 unit tests, and `docs/SCALE.md`. The review is corroborated by an
end-to-end live run this turn: dev-mini authored through the real `/forge` loop
with concurrent forge-author workers (three batches outstanding at once, disjoint,
ingested out of emission order), `validate` clean, structure byte-identical to the
committed fixture. `bin/test` green: 393 passing (12 short / 341 unit / 40 org).

**External reviewers:** None configured.

### Findings

No BLOCK or WARN findings. The M10 concurrent-batch airlock is clean on every
dimension checked:

- **Correctness (verified live, not just read).** `emit_author_batch` numbers
  work orders by globbing `author-*.json` (reply files start with `reply-`, so
  they do not inflate the serial); `pick_batch` excludes `state.covered_docs()`
  so concurrent batches are disjoint and draining partitions the manifest exactly
  once; `ingest` clears only the batch whose `work_order_id` matched and marks the
  stage `done` only when the last outstanding batch lands. All four behaviors were
  exercised on real data this turn (4 disjoint batches over 17 docs, 3 outstanding
  concurrently, reverse-order ingest, done-on-last) and match the code.
- **Additivity / regression.** `author_batches` defaults empty via
  `Field(default_factory=dict)`, so all seven committed `state.json` still load
  under the unchanged `orgsmith/state@1` id (org tier green, and the live run
  re-derived dev-mini byte-identical in structure). The single-outstanding
  `outstanding` path (foundation enrichment) is untouched.
- **Failure paths.** `match_author_batch` raises `SystemExit` with an actionable
  message when the id is not outstanding, the stored order file is missing, or the
  stored order's id does not round-trip, so a bad or double ingest fails loudly
  before any write.
- **Airlock preserved.** Python still makes no model or network call; concurrency
  lives entirely in the `/forge` skill (multiple Agent dispatches in one message),
  and the CLI stays a single serial writer of `state.json`. Confirmed by the
  chained `/security` pass.

One NOTE from the chained `/security` scan (recorded in SECURITY.md):

[NOTE] orgsmith/authoring/ingest.py:34,228 (with orgsmith/schemas.py:590) —
`docir_path()` derives a write target from the model-controlled `DocIR.doc_id`,
which has no schema pattern (unlike `ManifestEntry.doc_id`'s `^d:\d{4}$`).
Not exploitable at HEAD: `run_ingest` rejects any `doc_id` not in the trusted
work order (the `unknown` set) before the write loop runs, so every written id is
a work-order id. Defense-in-depth only; cheap future hardening is a
`Field(pattern=...)` on `DocIR.doc_id` or a basename guard on `docir_path`. Not
fixed this turn: it is a NOTE, and unmotivated by the de-risk's run.

Three NOTEs from the prior (M9) review persist against unchanged code and are not
re-listed here: pdf.py letterhead interpolation, render/__init__ docstring drift,
and test_short brittleness. See the prior entry.

### Fixes Applied

None. No BLOCK or WARN findings to fix.

### Accepted Risks

None.

---
*Prior review (2026-07-16, commit c013c06): full review of the unpushed M8+M9
arc (genre registry, registry-driven planner, per-genre lengths, PDF letter
fixes); 0 BLOCK / 0 WARN / 3 NOTE, no fixes required.*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"7cd134b","reviewed_up_to":"7cd134b78e678943b2f865e95c08b6996aea9401","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":1} -->
