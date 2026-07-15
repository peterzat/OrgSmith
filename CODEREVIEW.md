# CODEREVIEW

## Review — 2026-07-15 (commit: df11e42)

**Summary:** M4 turn review, scope origin/main..HEAD (9 commits): the
acl_posture knob and orgsmith/acl@1 ledger, the acl verb with
PERMISSIONS.md rendered into the share, the 3-rule ACL validator family,
the visibility eval suite (emit + score on the shared doc-set contract),
and the bramblewood-legal fixture (departmental posture, grants from 11
docs down to 3). Tests green before (short 5 / unit 92 / org 6) and after
the fix cycles (short 5 / unit 115 / org 8); fresh-clone verification
green; all four committed orgs validate clean; visibility ground truth
scores 5/5 on the new fixture.

**External reviewers:** None configured.

### Findings

```
[WARN] orgsmith/validate/rules.py (acl_03) — render_permissions was
called with the untrusted on-disk ACL ledger; a grant naming an unknown
principal raised an unhandled KeyError and crashed the entire validate
run instead of yielding findings (reproduced on a corrupted copy of
bramblewood-legal). FIXED.

[WARN] orgsmith/validate/rules.py (_needs_acl, MAN-01) — from the
/security M4-range scan: deleting ledger/acl.json from a departmental org
silently skipped ACL-01/02/03 under the false grandfather reason, and
MAN-01 whitelisted PERMISSIONS.md unconditionally, so a stripped or
forged distribution validated clean. FIXED.
```

Security (M4-range scan at this range, recorded in SECURITY.md): 0 BLOCK,
1 WARN (the skip-evasion above, remediated and re-verified this review),
2 informational NOTEs carried forward. Fixture PII, secrets, supply
chain, and the airlock all verified clean.

### Fixes Applied

Both WARNs, via /codefix (commit df11e42):
- acl_03 renders the PERMISSIONS.md comparison from the recomputed
  expected ledger (trusted, roster-derived), never from acl.json;
  regression test runs the full rule set against a ghost-principal
  ledger and asserts findings, not a traceback.
- _needs_acl skips only when the ledger is absent AND the posture is
  open; a non-open org with no ledger now fails all three ACL rules with
  a missing-ledger finding, and MAN-01 whitelists PERMISSIONS.md only
  when an ACL ledger exists. Corruption tests: stripped ledger on a
  departmental org (4 findings, exit 1, no skips) and stray
  PERMISSIONS.md on a pre-ACL org (MAN-01 finding). Both re-verified
  independently by the reviewer against fresh corrupted copies.

### Accepted Risks

None.

---
*Prior review (2026-07-15, commit 1830a11): M3 full review; 0 BLOCK / 0
WARN / 2 NOTEs; security changes-only scan clean.*

<!-- REVIEW_META: {"date":"2026-07-15","commit":"df11e42","reviewed_up_to":"df11e428c123b9e55d9abe99d2e0c99323c79ec7","base":"origin/main","tier":"full","block":0,"warn":2,"note":0} -->
