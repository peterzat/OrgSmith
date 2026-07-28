# CODEREVIEW

## Review — 2026-07-28 (commit: f081c77)

**Summary:** Full review of the mail-banner completion + v2.1.1 patch
(`origin/main`..HEAD): re-render the four fleet emails (northgate 2, calderwood
2) left on the pre-banner-strip render path, widen the banner test to every
committed org with eml, promote "What it costs to generate" to a section
heading, and cut v2.1.1 (version bump + regenerated CHECKSUMS.md). No production
code logic changed — the only `orgsmith/*.py` edit is the `__version__` string.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN issues.

- `tests/test_unit_eml.py`: `test_committed_mail_body_carries_no_header_banner`
  now derives its org list from the committed set (every `-metadata` dir with a
  recipe) instead of the three hardcoded mail orgs, and asserts it checked at
  least one eml. This is the coverage gap that let the northgate/calderwood
  banners through; verified it now covers all committed eml and passes.
- Fixtures: the re-render is deterministic — only the 4 banner-bearing emails
  changed bytes (the banner-free eml are byte-identical), plus their state.json
  render-hash tracking. Fleet-wide banner count is 0; both orgs validate clean;
  org tier green.
- v2.1.1: version bumped in lockstep (pyproject == `__version__` == 2.1.1, the
  short-tier version test passes); `tools/checksums.py` header string updated to
  v2.1.1; `CHECKSUMS.md` regenerated (`--check` clean) so the northgate/calderwood
  rollups and the fleet digest reflect the re-rendered emails. Package code is
  unchanged from 2.1.0; the committed fleet is what moved.
- README: "What it costs to generate" promoted from a bold inline lead-in to a
  `###` heading under "How it works"; heading nesting verified.
- Security: no production code logic changed since the last scan (SECURITY.md,
  commit eff521e, covered `eml.py`/`rules.py`/`checksums.py`). The sole `.py`
  logic file touched, `tools/checksums.py`, changed only its header string
  literal; the rest are version strings, a regenerated data manifest, a test
  widening, and re-rendered fixtures. No new security surface; prior scan
  carried forward (0 BLOCK / 0 WARN / 1 pre-existing NOTE on `ManifestEntry.path`).

### Fixes Applied

None.

### Accepted Risks

None.

### Test Baseline

Full default suite green: 608 passing (14 short, 520 unit, 74 org). Flagship 20.

---
*Prior review (2026-07-28, commit eff521e): full review of the three M16 follow-up fixes and the v2.1.0 release cut, 0 BLOCK / 0 WARN / 2 NOTE.*

<!-- REVIEW_META: {"date":"2026-07-28","commit":"f081c77","reviewed_up_to":"f081c77b286b3e3f648d2d42ed0695ec387043b8","base":"origin/main","tier":"full","block":0,"warn":0,"note":1} -->
