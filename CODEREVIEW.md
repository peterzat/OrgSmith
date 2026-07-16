# CODEREVIEW

## Review — 2026-07-16 (commit: 38d79aa)

**Summary:** Full-depth review of the unpushed M11a arc (nine commits,
`origin/main..HEAD`): the reference fleet's six new recipes, roster growth
(`RosterChurn.hires`), employment-scoped ACL grants, the guarded charter write,
the M10 security fix, and the live generation of `meridian-actuarial`. Scope
resolved as a refresh review (prior review `7cd134b`, 0 BLOCK, same base), but
the focus set turned out to equal the full set — `origin/main` is at `4067f3c`,
so the M10 arc is already pushed and everything unpushed is M11a. All 20 source
files were therefore reviewed at full depth, not as a refresh. `bin/test` green
and unmoved from the pre-change baseline: **422 passing** (12 short / 349 unit /
61 org), keyless and offline.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN findings.

The turn's four highest-risk changes each verified rather than read:

- **`_apply_growth_hires` (foundation/scaffold.py) is inert when off, which is
  what protects the byte pin.** It returns before drawing anything at
  `hires == 0`, and takes its own `Faker` and `rng` stream when on — the same
  discipline churn follows, and the reason `foundation.growth` cannot reorder a
  draw in `foundation.scaffold`. Confirmed by the pin itself: dev-mini's
  ledgers, manifest, and foundation are byte-identical across the change, and
  only its charter moved (one inert `"hires": 0`). Checked the id-collision
  surface the separate `Faker` creates: internal ids are `p:`, external people
  `xp:`, orgs `x:`, so a growth hire cannot collide with an external drawn from
  the shared instance (24 unique ids in the tracer).
- **`derive_acl`'s `readers & current` is correct and cannot strand a
  document.** `current` is roster-derived, so the intersection subsumes the old
  `if pid in readable` external guard rather than dropping it. ACL-02 holds by
  construction: the CEO-equivalent is `reports_to is None`, churn eligibility
  requires `reports_to is not None`, so the CEO can never depart and every
  document keeps a reader under all three posture branches. Independently
  confirmed by the chained `/security` pass.
- **The two ACL tests that changed were not weakened to accommodate the
  change.** `test_open_posture_grants_everything_to_current_staff` now asserts
  two things where it asserted one (current staff read everything AND departed
  staff read nothing) and guards against vacuity by requiring both sets
  non-empty; `test_departmental_posture_restricts` tightened each expected
  reader set by intersecting with `current`. The contract change is the spec's
  stated intent, and a new test names the departed-employee case directly.
- **Both new checks are fault-injection verified, per this project's own rule
  that a diff which cannot fail is decoration.** Reverting `brackenridge-civil`
  to `hires: 0` fails the coherence check with the full margin trail
  (21.3% -> 42.4%); removing the charter write guard fails the resume test on
  `st_mtime_ns`. Both reverted clean.

One NOTE:

**[NOTE] tests/test_org_regen.py:66-88 — `_COHERENCE_EXEMPT` names seven slugs
with no check that they still exist, so it cannot fail when it goes stale.**

  Evidence: `_COHERENCE_EXEMPT = {"dev-mini", "torchlake-engineering", ...}`
  feeds `FLEET = [s for s in RECIPES if s not in _COHERENCE_EXEMPT]`. Nothing
  asserts `_COHERENCE_EXEMPT <= set(RECIPES)`. The comment above it states the
  set "must shrink to {"dev-mini"} when the fleet turn lands", which is a
  comment, not a contract.
  Why it matters beyond tidiness: the same module already carries
  `test_every_committed_fixture_has_a_recipe` for precisely this reason —
  "without this check a deleted recipe would silently shrink the fleet under
  test instead of failing" — and CLAUDE.md's standing rule is grandfather by
  charter, not by absence. The concrete trap: the fleet turn deletes the six
  legacy recipes, the set keeps six dead entries, and if any future fleet
  recipe ever reuses one of those slugs (regenerating `fernhollow-partners` as
  a new fleet org is the obvious candidate) it is silently exempted from the
  coherence check with no signal.
  Suggested fix: assert `_COHERENCE_EXEMPT <= set(RECIPES)` in a test, so a
  deleted recipe forces the set to be pruned in the same commit.
  Not fixed here: NOTEs are not auto-fixed, and this one is a one-line test
  addition best made when the fleet turn prunes the set anyway.

### Fixes Applied

None. No BLOCK or WARN findings to fix.

### Accepted Risks

None.

---
*Prior review (2026-07-16, commit 7cd134b): refresh review of the M10
concurrent-batch airlock plus its live-authoring de-risk; 0 BLOCK / 0 WARN /
1 NOTE. That NOTE (`docir_path` deriving a write target from the
model-controlled, schema-unconstrained `DocIR.doc_id`) is **closed by this
turn** at both the schema and the sink, and independently re-verified by
execution in the chained `/security` pass. Three older M9 NOTEs persist against
unchanged code (pdf.py letterhead interpolation, render/__init__ docstring
drift, test_short brittleness); the first is re-confirmed open and outside this
turn's path scope.*

<!-- REVIEW_META: {"date":"2026-07-16","commit":"38d79aa","reviewed_up_to":"38d79aa2a0ebe2a049aca4849190980da359925d","base":"origin/main","tier":"full","block":0,"warn":0,"note":1} -->
