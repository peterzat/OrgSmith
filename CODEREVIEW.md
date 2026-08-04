# CODEREVIEW

## Review — 2026-08-04 (commit: 836a1dd) — M17c replicate arm and noise floor

**Review scope:** Full review (the prior entry records `block: 1`, so the
refresh conditions do not hold). Three files changed since `origin/main`:
`tools/ab_compare.py`, `tests/test_unit_ab_discriminating.py`,
`docs/M17C-EVIDENCE-STANDARD.md`.

**Summary:** Adds a third arm (a control replicate at the same seed) and a
`noise_floor()` to give the control-to-treatment gap a magnitude to clear,
plus the mid-run within-batch caveat in the evidence standard. One BLOCK in
`noise_floor` itself: as written it can report zero noise on runs that moved
substantially, which is the one direction this measurement must never fail in.

**Tests:** 16 short, 739 unit, 230 org (+27 skipped). No regression (737 before the fix; the deltas are the two new tests).

**External reviewers:** None configured.

### Findings

**[BLOCK] tools/ab_compare.py — `noise_floor` compares distribution summaries
where a paired per-pair comparison is available, and can report zero noise on
runs where every pair moved.**

The control and its replicate share a recipe and a seed, so their manifests
are byte-identical (verified: `cmp` on the two `manifest.jsonl` files passes).
Every pair key `(doc_a, doc_b)` therefore exists in *both* arms, and the two
runs can be compared pair by pair. `noise_floor` instead summarizes each arm
separately and subtracts the summaries:

```python
a = _dist([(p.shape + p.openers) / 2 for p in control])
b = _dist([(p.shape + p.openers) / 2 for p in replicate])
return {k: abs(a[k] - b[k]) for k in ("mean", "p50", "p75", "p90") if k in a}
```

Summary statistics cancel. Demonstrated:

```
truth: every pair moved by 0.30 between the two runs
noise_floor reports: {'mean': 0.0, 'p50': 0.0, 'p75': 0.0, 'p90': 0.0}
a paired per-pair mean |delta| would report: 0.3
```

Why this is a BLOCK rather than a refinement. The replicate exists for exactly
one purpose: to be the bar a control-to-treatment gap must clear before the
turn may claim the outline work did anything. A floor that reads 0.0 when
per-pair movement is 0.30 fails **toward** significance. A treatment gap that
is entirely authoring nondeterminism would clear a floor of zero and be
written up as an effect. That is the false conclusion the user spent ten extra
authoring batches specifically to prevent, and the turn's whole claim to being
a controlled experiment rests on this number.

Suggested fix: report both, because they answer different questions and the
gap between them is itself the diagnostic.

- Keep the aggregate delta: it is the like-for-like comparator for the
  treatment's own aggregate delta, computed by the same estimator.
- Add a paired per-pair spread over the shared pair keys (mean and p90 of
  `|score_control(pair) - score_replicate(pair)|`). When this is large while
  the aggregate delta is near zero, cancellation is hiding real volatility,
  and the aggregate comparison should not be trusted on its own.

Both are magnitudes to read, never thresholds; the existing docstring
prohibition against turning this into a significance test still stands and
should be carried onto the new value.

### Fixes Applied

`/codefix`, verified by re-review against the finding's own demonstration:

- **[BLOCK] tools/ab_compare.py** — `noise_floor` keeps the aggregate delta
  per statistic (the like-for-like comparator for the treatment's own
  aggregate delta) and adds a paired per-pair spread over the pair keys the
  arms share: `paired_n`, `paired_mean`, `paired_p90`. Re-ran the case that
  demonstrated the bug: aggregate mean/p50/p75/p90 still read 0.0, and
  `paired_mean`/`paired_p90` now read 0.30, so the cancellation is visible
  instead of silent. The print block splits into `aggregate:` and `paired (N
  shared pair keys):`, and an unmeasured paired spread is flagged "NOT a
  measured zero" rather than omitted silently. The never-a-threshold
  prohibition is carried onto both values.
- Two tests added, including the finding's exact scenario.

Author-applied afterwards, and recorded rather than folded in silently:

- `docs/M17C-EVIDENCE-STANDARD.md` gained an **amendment log**. `/codefix`
  deliberately left the file alone on the grounds that editing a
  pre-registration post-hoc compromises what makes it evidence, which is the
  right instinct; but the header claimed the document was fixed before
  authoring while it had in fact been amended twice mid-run. An inaccurate
  provenance claim inside the pre-registration is worse than a visible
  amendment log, so the log now dates every amendment against the state of
  the run and states that none changed what counts as evidence.

### Carried, not fixed

- `SECURITY.md` cites `tools/ab_compare.py` line numbers (257, 262) that this
  change shifts. The referenced code is unmodified, so the finding is intact
  and only the citations are stale. Left for the next `/security` pass rather
  than hand-edited, since editing a scan's own record outside a scan is how
  that record stops being trustworthy.

### Accepted Risks

None.

---
*Prior review (2026-08-03, commit 9dcc15c): the M17c deterministic scaffolding
(recipe, control derivation, attribution check, pre-registered standard). One
BLOCK, `ab_control.py` destroying the treatment recipe when source and
destination coincided, and three WARN, all fixed across two `/codefix` cycles
plus one author-applied fix whose review-integrity caveat is carried forward
below. `/security` clean at 0/0/0.*

<!-- REVIEW_META: {"date":"2026-08-04","commit":"836a1dd","reviewed_up_to":"836a1dd","base":"origin/main","tier":"full","block":1,"warn":0,"note":0} -->
