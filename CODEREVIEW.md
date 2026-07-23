# CODEREVIEW

## Review — 2026-07-23 (commit: 014c138)

**Summary:** Full review of the M15 turn: 18 commits, 39 non-fixture files
(+2964 / -169) plus 115 regenerated fixture files, covering organizational
noise v2 (six derived kinds, filename variety, attachment-version mismatch),
persona voice v2 (per-person style specs), the Integrity/Realism reporting
split, the zero-token `ashcombe-advisory` noise append, and the one-time
`dev-mini` regeneration. The prior review's `reviewed_up_to` (199f8eb) sits
behind `origin/main`, so every file in the push scope was reviewed at full
depth rather than as a refresh.

**External reviewers:** None configured.

### Findings

**[WARN] orgsmith/foundation/style.py:27-28 — `_HABITS` can draw two
mutually exclusive habits for the same person, and does so in a committed
ledger.**

  Evidence: `derive_style_specs` calls `r.sample(_HABITS, 2)` over a flat
  pool that contains both `"prefers numbered lists over bullet points"` and
  `"avoids lists entirely and writes in paragraphs"`. Both can be drawn for
  one person. Measured over 4000 per-person streams: 6.3%. It is present in
  the fixture committed this turn —
  `companies/dev-mini-metadata/ledger/style_specs.json`, `p:michelle.lopez`
  carries both. `_style_guidance` (`authoring/contexts.py:280`) joins the
  habits verbatim into the brief, so an affected author is told "You
  habitually: avoids lists entirely and writes in paragraphs; prefers
  numbered lists over bullet points." No brief in this turn actually shipped
  the contradiction — michelle.lopez authored no dev-mini document — which
  is luck, not design. M16 authors ~600 documents across eight orgs.

  Suggested fix: group the pool so mutually exclusive habits cannot co-occur
  (draw at most one from a list-formatting group), and re-emit
  `style_specs.json` for dev-mini (derived; excluded from the ledger byte pin
  and recomputed by STY-01, so re-emission is the sanctioned path). Add a
  unit test asserting no drawn pair is contradictory across many seeds.

**[WARN] orgsmith/docplan/planner.py:1085 — stale-template author selection
crashes with a raw `ValueError` when nobody is employed on the drawn date.**

  Evidence: `author = employed[srng.randrange(len(employed))]` indexes a
  list filtered by `p.employment.start <= date`, with no emptiness guard.
  The date is drawn from the first half of `date_range`, but the earliest
  roster start is `_mid_month(founded, 2)` (`foundation/scaffold.py:143`),
  so any recipe whose `date_range` begins in its founding year has a window
  where `employed` is empty. `date_range[0].year >= founded` is the only
  charter constraint, so this is a legal recipe. Reproduced: with
  `founded: 2019`, `date_range: [2019-01-01, 2023-12-31]`,
  `stale_templates: 2`, a 120-seed sweep gives 98 successes, 12 actionable
  `SystemExit`s, and **10 raw `ValueError: empty range for randrange()`**.
  This path constructs `ManifestEntry` directly rather than through `_add`,
  so it never reaches `_add`'s employment guard; every sibling over-demand
  case in the same diff (`_plan_chains`, `_plan_misfiles`,
  `expected_empty_dirs`) raises an actionable `SystemExit` instead.

  Suggested fix: draw the template date only from dates where someone is
  employed, or raise `SystemExit` naming the knob and the empty window, in
  the idiom the neighbouring planners already use. Add a regression test
  pinning one of the reproducing seeds.

**[WARN] orgsmith/validate/rules.py:482, 775 — the `.gitkeep` allowance is
name-scoped, not content-scoped, so arbitrary bytes in a planned empty
directory pass the full validator.** (Raised as NOTE by `/security`;
upgraded here because this diff introduced the exception and the gap is in
the repo's headline claim.)

  Evidence: NOISE-01 filters the directory listing by `p.name !=
  EMPTY_DIR_PLACEHOLDER` and MAN-01 adds `"<planned dir>/.gitkeep"` to
  sanctioned extras. Neither constrains size or bytes, and because the file
  is unmanifested no manifest-driven rule opens it. NOISE-01 and MAN-01 are
  the only rules that walk the share tree. The README sells "tamper evidence
  by construction" and CLAUDE.md requires knob-on-with-artifact-missing to
  fail; a sanctioned file whose contents nothing checks is the one place in
  the share where that no longer holds. The three committed placeholders in
  `ashcombe-advisory` are 0 bytes, so no fixture is affected today.

  Suggested fix: assert the placeholder is zero bytes in NOISE-01 (one
  line), with a unit test writing content into one and expecting a finding.

**[NOTE] orgsmith/review/report.py:63, 290, 314 — three table cells bypass
`_cell`.** (From `/security`.)

  Evidence: `state.generators` keys, `entry.authors[0]`, and the joined
  `ReviewFinding.docs` reach a markdown row without `strip_control` and pipe
  escaping, and none carries a schema pattern. Not model-reachable (ingest
  pins generator keys to a Python-generated `wo:<stage>:NNNN` and rejects a
  `docs` entry that is not a manifest doc_id) and not network-reachable; the
  exposure is a hand-tampered `-metadata` directory. Left as-is per the
  NOTE convention.

### Fixes Applied

All three WARN fixed by `/codefix` in `014c138`, each with a regression test.
The NOTE was left as-is per convention.

- **[WARN] `orgsmith/foundation/style.py`** — the flat `_HABITS` pool became
  `_HABIT_GROUPS`; at most one habit is drawn per exclusion group, the
  list-formatting pair being the one real group.
  `companies/dev-mini-metadata/ledger/style_specs.json` re-emitted (the only
  committed org with the knob on); `p:michelle.lopez` no longer carries the
  contradictory pair. Test `test_habits_are_never_self_contradictory` asserts
  the property over 3500 per-person streams **and** that the grouping strands
  no habit, so a fix that merely deleted an option would fail it.
- **[WARN] `orgsmith/docplan/planner.py`** — emptiness guard raising
  `SystemExit` that names `stale_templates`, the drawn date, the range, and
  the first roster start. Behaviour-preserving for every existing fixture:
  the guard fires only where `randrange(0)` already crashed, so no RNG stream
  moves. Test pins seed `20260715`.
- **[WARN] `orgsmith/validate/rules.py`** — NOISE-01 now also asserts the
  placeholder is zero bytes and reports its size. Test writes 16 bytes into
  one and asserts the placeholder is the sole finding, so it cannot pass by
  tripping the pre-existing "not empty" check instead.

Tests: baseline 14 / 509+6 / 74 / 20 → 14 / **512**+6 / 74 / 20. No
regressions; `PINNED = SLUGS` green throughout.

### Accepted Risks

None.

---
*Prior review (2026-07-22b, commit 199f8eb, light): M14 documentation
accuracy pass over four markdown files. No issues found; one editorial defect
introduced by the pass itself (four over-wrapped prose lines) was corrected
before the marker was written.*

<!-- REVIEW_META: {"date":"2026-07-23","commit":"014c138","reviewed_up_to":"014c138122d6cf91da64143b9957721a81fe8267","base":"origin/main","tier":"full","block":0,"warn":3,"note":1} -->
