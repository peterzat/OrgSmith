# CODEREVIEW

## Review — 2026-07-14 (commit: 6b4eef5)

**Summary:** First-ever review (empty-tree base): the entire committed tree,
106 files, +7,941 lines, covering the M0 scaffold through v1 packaging
(pipeline stages, airlock, renderers, validator, skills, committed dev-mini
org, docs, Apache-2.0 relicense). Test baseline short 5 / unit 30 / org 2,
green before and after the fix cycle; the committed dev-mini org regenerates
byte-identically after the fixes.

**External reviewers:** None configured.

### Findings

```
[WARN] orgsmith/docplan/planner.py:64 — author-employment check ran on the
pre-clamp date; clamping could move a doc date before the checked author's
start and desync filename dates from manifest dates (latent; not triggered
by dev-mini). FIXED.

[WARN] orgsmith/fabric/engagements.py:60 — on short charter date ranges the
end clamp could invert the engagement window (end < start), crashing fabric.
FIXED.

[WARN] docs/RECIPE-FORMAT.md:12 — nested triple-backtick fences terminated
the outer example block early on GitHub. FIXED.

[WARN] orgsmith/render/__init__.py:59 — manifest paths were joined to the
filesystem without load-time re-validation; rendering a tampered org was an
arbitrary-file-write primitive (from /security). FIXED.
```

NOTE (from /security, informational, not auto-fixed): WeasyPrint's default
URL fetcher stays enabled (latent gap in the "no network" guarantee, only
reachable via trusted letterhead strings); CI actions are pinned to mutable
major-version tags rather than commit SHAs.

### Fixes Applied

All four WARNs, via /codefix (commit 6b4eef5):
- docplan clamps dates to the charter range before the employment check and
  builds every filename from the clamped date.
- fabric caps seeded engagement starts at range_end - 104d and fails ranges
  shorter than 149 days with an actionable recipe error.
- RECIPE-FORMAT.md example wrapped in a four-backtick fence.
- check_relpath rejects empty and parent-directory components; load_manifest
  re-validates every entry.path, so render/validate refuse tampered
  manifests.

Verified by behavioral checks (short-range recipe builds or fails loudly,
forced out-of-range docs land in range with employed authors, path traversal
rejected) and a full green test run matching the baseline.

### Accepted Risks

None.

<!-- REVIEW_META: {"date":"2026-07-14","commit":"6b4eef5","reviewed_up_to":"6b4eef595c1beabe3e50cd817146755bb927be49","base":"empty-tree","tier":"full","block":0,"warn":4,"note":2} -->
