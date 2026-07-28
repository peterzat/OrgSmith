# CODEREVIEW

## Review — 2026-07-28 (commit: 9927e03)

**Review scope:** Refresh review. Focus: the fit-and-finish turn since the prior
review (commit cf9ee69), five files of new work (`drivers/config.py`,
`drivers/providers.py`, `tests/test_short.py`, `tests/test_unit_driver.py`, plus
a one-line reflow in `drivers/forge_external.py`) and the doc reconciliations
(`README.md`, `CLAUDE.md`, `BACKLOG.md`). The BYO driver reviewed at cf9ee69 is
unchanged except the hardening below.

**Summary:** A wrap-up turn that closes and hardens the bring-your-own-token
path, tidies the M16 aftermath, and does a README voice pass. Small code
surface: an `http(s)`-only `base_url` allowlist and a drift-guard test. The rest
is documentation.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN issues.

- **`base_url` scheme allowlist (drivers/config.py, drivers/providers.py).**
  `base_url_scheme_ok` accepts only `http`/`https` via `urlparse().scheme`;
  `missing_requirements` reports a bad scheme (so `--check` exits non-zero), and
  `call_provider` returns `None` before opening a connection. Verified the named
  providers' https defaults still resolve ready and the `local` case still
  accepts `http`. `/security` re-scanned the driver delta and closed its prior
  NOTE (0/0/0).
- **Authoring-guidance drift guard (tests/test_short.py).** Pins the driver's
  writing-quality system prompt in sync with `forge-author/SKILL.md` by asserting
  a set of core rule signatures appears in both, mirroring the existing
  board-dimension pin. Catches the documented MVP drift risk.
- **Backlog prune / doc reconciliation.** BACKLOG.md dropped six resolved
  entries (five M16-closed plus the BYO item); 11 open entries retained. CLAUDE.md
  and README no longer claim the hollowell `To:/Cc:` banner is unfixed (it was
  fixed in v2.1.1). Two internal contradictions the README voice pass surfaced
  were corrected against ground truth: the current exemplar's board findings are
  8 (6 major), matching `review/findings/` and the "what is not modeled" section,
  not the stale 28/16; and the M13-M16 wave is recorded as closed, not "underway".
- **README voice pass.** All 111 em-dashes removed per house style, with the
  comma-splices a mechanical pass would create fixed by hand and the "which
  fixture proves what" table's em-dash N/A cells restored to clean blank cells.
  Content preserved (words 9565 -> 9489, the drop is the de-comma'd table cells).
- **Note (informational, not a defect):** the README's approximate test totals
  ("602 tests", "~510-test unit tier") were left unchanged per the turn's
  preserve-numbers scope; they now understate the suite by the ~45 driver tests
  added across the BYO and fit-and-finish turns. Worth a deliberate refresh in a
  future turn, not this one.

### Fixes Applied

None.

### Accepted Risks

None.

### Security

`/security` re-scanned the changed driver files (delta since cf9ee69):
0 BLOCK / 0 WARN / 0 NOTE. The prior `base_url` NOTE is resolved by the allowlist
and verified at the sink; the standing `ManifestEntry.path` traversal NOTE was
closed as not reachable (`load_manifest` runs `naming.check_relpath` at load).
SECURITY.md carries zero open findings.

### Test Baseline

Full `bin/test` green: 16 short, 563 unit, 74 org, 20 flagship. Keyless and
offline; the frozen fleet re-derives byte-identical (no fixture regenerated).

---
*Prior review (2026-07-28, commit cf9ee69): full review of the bring-your-own-token
authoring driver (new `drivers/` package); 0 BLOCK / 0 WARN / 1 NOTE.*

<!-- REVIEW_META: {"date":"2026-07-28","commit":"9927e03","reviewed_up_to":"9927e03b33306854ea716f2f4b08a2fe7d6ec04c","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":0} -->
