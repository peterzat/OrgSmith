# CODEREVIEW

## Review — 2026-07-14 (commit: 09d6596)

**Summary:** M2 turn review, scope origin/main..HEAD (13 commits): graph
ambiguity knobs, mention planning + mention_map ground truth, MENT/GRAPH
validator families with visible skips, golden evals (emit-evals/score),
no-network PDF hardening, CI SHA pins, and the committed
torchlake-engineering fixture. Tests green before and after the fix cycle
(short 5 / unit 65 / org 4); fresh-clone verification green; both committed
orgs validate clean under the post-fix stricter rules.

**External reviewers:** None configured.

### Findings

```
[WARN] orgsmith/validate/rules.py (MENT-01) + orgsmith/authoring/ingest.py —
mention surfaces matched by substring containment, so a nickname that
prefixes the full name ("Jen" in "Jennifer") satisfied the check
vacuously. FIXED.

[WARN] orgsmith/artifacts.py:60 — the load-time manifest path rejection
(v1 security fix) had no negative test. FIXED.
```

NOTE (from /security, informational): PDF letterhead lines render
unescaped; input is the trusted recipe charter and the fetcher blocks all
egress, so no vector. NOTE: `score` keeps the last entry when an answers
file repeats a question id rather than flagging the duplicate.

Security (changes-only scan at this commit range): 0 BLOCK / 0 WARN /
1 NOTE; all three v1 findings verified remediated (manifest path
re-validation, WeasyPrint fetcher block, CI SHA pins). See SECURITY.md.

### Fixes Applied

Both WARNs, via /codefix (commit 09d6596):
- Shared `surface_in_text` helper (word-boundary lookarounds around the
  escaped surface) in orgsmith/schemas.py, used by MENT-01 and the ingest
  mention check.
- Negative tests: schema-valid manifest lines with absolute and
  parent-directory paths make load_manifest raise.

### Accepted Risks

None.

---
*Prior review (2026-07-14, commit 6b4eef5): first full-tree review; 4 WARNs
found and auto-fixed, 0 BLOCKs.*

<!-- REVIEW_META: {"date":"2026-07-14","commit":"09d6596","reviewed_up_to":"09d6596ff002165e379ed01ce8b648eb54b0b1e8","base":"origin/main","tier":"full","block":0,"warn":2,"note":2} -->
