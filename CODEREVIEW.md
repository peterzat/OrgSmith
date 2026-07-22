# CODEREVIEW

## Review — 2026-07-22b (commit: 199f8eb, light)

**Summary:** Light review of the M14 documentation accuracy and editorial
pass: 4 plain-markdown files against `origin/main` (`CLAUDE.md`, `README.md`,
`docs/RECIPE-FORMAT.md`, `docs/SCALE.md`), plus the review-output files
`TESTING.md`, `SECURITY.md`, and this file. No code or configuration changed,
so per the light-review tier the test suite, `/security` chain, external
reviewers, and fix loop are skipped; the scope is broken references, secret
leaks in prose, and factual accuracy.

**External reviewers:** Skipped (light review).

### Findings

No issues found.

Checked, with the verification that backs each:

- **Factual accuracy.** Every changed number was re-measured against the live
  code rather than carried over: `len(RULES)` is 34 (the README's three
  "31-rule validator" mentions and TESTING.md's "29-rule" were stale);
  `bin/test` is 545 passing + 6 soffice-skipped (551 with LibreOffice), unit
  465/459, org 72, flagship 20 over two orgs; `validate northgate-staffing`
  reports 24 run / 10 skipped (was documented as 7 skipped before EML-02,
  EML-03, and DL-01 began skipping there). The `ashcombe-advisory` generator
  stamp is `claude-opus-4-8`, not the fleet's `claude-opus-4-8[1m]`, so the
  README claim was corrected to match the committed record.
- **References.** All README markdown links resolve to existing paths and all
  in-page anchors resolve to real headings (scripted check, 0 broken). The new
  `#the-m14-email-pilot` cross-link resolves.
- **No secrets.** The diff is prose, recipe-knob documentation, and milestone
  labels; no credentials, tokens, or private paths.
- **Right change.** The M12b -> M17 renumbering is now consistent across
  README and `docs/SCALE.md` (previously the same milestone carried two
  names), and `docs/RECIPE-FORMAT.md` gained the `mail.distribution_lists`
  knob and DL-01, which shipped in M14 but were undocumented.

### Fixes Applied

One editorial defect introduced by the pass itself, corrected before the
marker was written: four prose lines exceeded the surrounding ~76-column wrap
(`CLAUDE.md` carve-out clause 3, `docs/SCALE.md` two flagship sentences,
`README.md` flagship-tier bullet). Reflowed to match each file's existing
wrapping. Cosmetic only; markdown renders identically either way.

### Accepted Risks

None.

---
*Prior review (2026-07-22, commit 92d8acb, full): M14 email realism, 12
commits. Three parallel adversarial reviewers plus `/security` found 1 BLOCK
(a mail-block reply could crash render with FileNotFoundError when a thread
predecessor was unauthored), 3 WARN (unguarded `attach_path` join reaching a
`share_dir` read — SEC-1; `_next_send` able to emit two identical Date
headers at the range-end wall; a department name outside the `dl:` id charset
crashing distribution-list derivation), and 2 NOTE. All BLOCK/WARN fixed by
`/codefix` in `6b67c12` with a regression test for the BLOCK; NOTEs left as-is.
Tests green and byte pin held throughout.*

<!-- REVIEW_META: {"date":"2026-07-22b","commit":"199f8eb","reviewed_up_to":"199f8eb","base":"origin/main","tier":"light","block":0,"warn":0,"note":0} -->
