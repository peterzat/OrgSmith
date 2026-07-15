# CODEREVIEW

## Review — 2026-07-15 (commit: 50eeefa)

**Summary:** Refresh review of the M5 opening increments plus the doc
pass, scope origin/main..HEAD (6 commits; focus: 8 files changed since the
prior review at df11e42). Code surface: FormatMix pptx/eml fields and
DocCulture scan/legacy/OCR ratios with cross-validation (additive,
compat-tested against all four committed fixtures), six new exactly-pinned
dependencies promoted to doctor's required set. Docs surface: LibreOffice
requirements in CLAUDE.md/README/forge preflight, README design-principles
section, pipeline diagram and rule-count corrections (22 verified against
the RULES registry). Tests green at HEAD (short 5 / unit 117 / org 8).
The knobs currently have no pipeline consumers by design; consumers land
in the remaining M5 increments per SPEC.md.

**External reviewers:** None configured.

### Findings

No issues found.

### Fixes Applied

None.

### Accepted Risks

None.

Security (paths scan at this range, recorded in SECURITY.md at commit
50eeefa): 0 BLOCK / 0 WARN / 2 carried NOTEs. New dependencies verified
pinned and matching installed versions, no known CVEs at knowledge cutoff;
their untrusted-parse surface arrives with later M5 increments and gets
scanned when that code lands. The M4 ACL skip-evasion WARN re-verified
remediated at HEAD.

---
*Prior review (2026-07-15, commit df11e42): M4 full review; 2 WARNs
(acl_03 crash on tampered ledger, ACL grandfather skip-evasion) found and
fixed via /codefix; 0 BLOCKs.*

<!-- REVIEW_META: {"date":"2026-07-15","commit":"50eeefa","reviewed_up_to":"50eeefa28e77e0eab7f32e0298e2488d4cbb15b7","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":0} -->
