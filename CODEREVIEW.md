# CODEREVIEW

## Review — 2026-07-15 (commit: 1830a11)

**Summary:** M3 turn review, scope origin/main..HEAD (7 commits, 68 files,
+4915/-84): location policies (`signature_page`, `filename`) as additive
schema evolution, the hard_cases recipe knobs with fabric policy assignment
and a docplan placement gate, end-to-end enforcement (ingest rejections,
render-time signature-page fee injection with a forced page break, the
3-rule LOC validator family with per-page pdf extraction), the extraction
eval suite (emit + score with per-question attribution), ambiguity-class
tags with per-class graph recall, and the committed quillbrook-appraisal
fixture generated through the airlock with both hard-case knobs on. Tests
green before (short 5 / unit 65 / org 4) and after (short 5 / unit 92 /
org 6); fresh-clone verification green at HEAD; all three committed orgs
validate clean; ground-truth extraction answers score 100% on all three.

**External reviewers:** None configured.

### Findings

```
[NOTE] orgsmith/evals/emit.py (_ambiguity_tags) — surname collisions are
derived from the last whitespace token of a person's name; a generated
name carrying a suffix could mis-tag a collision. No instance in any
committed fixture (dev-mini asserts zero tags), and tags live in derived,
re-emittable artifacts.

[NOTE] orgsmith/authoring/ingest.py (_check_hard_cases) —
date.fromisoformat(fact.value) on a filename-date fact raises an
unhandled ValueError if the org's own ledger has been hand-tampered with
a non-ISO value, crashing ingest with a traceback instead of a clean
rejection. The ledger is the org's own trusted artifact; robustness, not
a vulnerability.
```

Security (changes-only scan at this range, recorded in SECURITY.md at
commit 1830a11): 0 BLOCK / 0 WARN / 2 NOTE, both informational and
verified at HEAD (answers-file strings printed raw in score's failure
report; letterhead lines rendered unescaped with no concrete vector).

### Fixes Applied

None required; no BLOCK or WARN findings.

### Accepted Risks

None.

---
*Prior review (2026-07-14, commit 589c6bc): light refresh of the M3
spec turn-open (BACKLOG.md annotation only); no findings. Before that,
the M2 full review at 09d6596 found and fixed 2 WARNs.*

<!-- REVIEW_META: {"date":"2026-07-15","commit":"1830a11","reviewed_up_to":"1830a112d82a7ff1f9caffd07e57a6a9b9883e10","base":"origin/main","tier":"full","block":0,"warn":0,"note":2} -->
