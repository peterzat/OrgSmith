# CODEREVIEW

## Review — 2026-08-02 (commit: b6becc7) — the regeneration and close

**Summary:** Full review of the M17 regeneration half: the CAL-01 business-day
fix in the noise planner, the checksum version derivation, two re-hosted test
files, the enriched exemplar recipe, the regenerated org, and the closing docs.
The prior entry's fix loop is folded in (its REVIEW_META recorded the pre-fix
commit; corrected here).

**External reviewers:** None configured.

### Findings

**[WARN, FIXED] README.md, CLAUDE.md — a published claim overstated what the
recipient exemption achieved.**

Both said the regenerated exemplar's person-to-person mail is "free of the
device." Measured against the committed org: no non-DL message plans a
recipient mention, so the *forcing mechanism* is genuinely gone, but 8 of 14
such messages still name a recipient in the message body, now by authorial
choice. "Free of the device" reads as "the names are absent," which is false.

Found by verifying the claim rather than repeating the board's. The first
measurement was itself wrong in the opposite direction (32 hits) because
`DocText` deliberately folds To/Cc display names into an `.eml`'s text, so it
was matching transport headers; the body-only count is 8/14.

Both files now state the mechanism claim precisely and tell a reader to count
planned mentions rather than grep bodies.

**[NOTE] orgsmith/docplan/planner.py — `_chain_member_date` narrows the
business-day ceiling, which makes `to_business_day`'s give-up path marginally
more reachable.**

Passing `ceil=src.date - 1 day` is deliberate and correct: it stops the
tie-break's forward step carrying a version member onto or past the document it
is a version of. The cost is that a pathological window (every candidate within
±7 days a weekend or declared holiday, floor pinned tight) returns the date
unchanged, per that function's documented contract, and CAL-01 then flags it
visibly. Confirmed reachable in a synthetic worst case; not reachable on any
committed org, all of which validate clean. The failure mode is a loud
validation error rather than a silent bad date, which is the right trade.

**[NOTE] tools/checksums.py — the manifest header version now imports from the
package.** This couples a tools script to `orgsmith` importing successfully.
Accepted deliberately: the hardcoded string it replaces had gone stale at 2.1.1
while the package moved, which is the defect that prompted it.

### Fixes Applied

- [WARN] `README.md`, `CLAUDE.md` — corrected the recipient-exemption claim to
  distinguish the forcing mechanism (closed) from the surface (8 of 14).

### Verified, not filed

- `_chain_member_date`'s blast radius was measured before the fix, not after:
  no frozen org has a derived attendance-genre document on a weekend, so the
  change is inert on the fleet. Re-planning the exemplar moved exactly one
  field across 76 documents (`d:0074` date, Saturday to the preceding Friday).
- Both re-hosted test files keep guard assertions so they cannot go vacuous:
  the grandfathering test requires at least one adopting and one
  non-adopting org, and the re-hosted MENT-03 probe asserts the specific
  target path and message content against a mutation it makes itself.
- The `Jim` closure was re-verified independently of the board: exactly one
  occurrence across 76 documents, in the one document whose plan places it.
- Regenerated org: 34 validator rules run, 0 errors; ground truth 100% on all
  four splits for both suites and 12/12 on visibility.

### Accepted Risks

None.

### Security

No new security surface since the prior scan (0 BLOCK / 0 WARN / 1 pre-existing
NOTE at `6bd7d77`). The regeneration adds data, not code paths; the two code
changes are a date computation and a version import, neither touching input
handling, subprocess, network, or a model-output sink. The prior scan's NOTE
(raw validator finding messages in `validate/__init__.py`) is unchanged and
carried forward in SECURITY.md.

### Test Baseline

All four tiers green: 16 short, 615 unit, 228 org (+27 skipped), 65 flagship
(+5 skipped). `python tools/checksums.py --check` current.

---
*Prior review (2026-08-02, commit 6bd7d77): the M17 answer-key turn; 1 BLOCK
(cluster canonicalization collapsing distinct required documents), 3 WARN, all
fixed; 1 NOTE left informational.*

<!-- REVIEW_META: {"date":"2026-08-02","commit":"b6becc7","reviewed_up_to":"b6becc7","base":"origin/main","tier":"full","block":0,"warn":1,"note":2} -->
