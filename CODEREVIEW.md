# CODEREVIEW

## Review — 2026-08-03 (commit: 9dcc15c) — M17c deterministic scaffolding

**Review scope:** Refresh review against `origin/main`. The prior review's
commit (`f0aacdc`) predates every file in this diff, so all seven are in the
focus set and none qualified for interaction-only treatment. Full depth
throughout: `recipes/quillon-harbor/ORG-CHARTER.md`, `tools/ab_control.py`,
`tools/ab_compare.py`, `tests/test_unit_ab_control.py`,
`tests/test_unit_ab_structure.py`, `docs/M17C-EVIDENCE-STANDARD.md`,
`BACKLOG.md`.

**Summary:** The M17c turn's deterministic half: one recipe, a tool that
derives the control arm from it, a tool that proves the two arms differ only
in the declared knobs, and the pre-registered evidence standard. No existing
code is modified, so regression risk is confined to the new recipe joining
`RECIPES` in `test_org_regen.py` (verified: org tier 228 -> 230, green).
One BLOCK and three WARN, all resolved.

**Tests:** 16 short, 735 unit, 230 org (+27 skipped), 65 flagship (+5
skipped). Baseline before this work was 16/716/228(+27)/65(+5); the deltas
are nineteen new unit tests and the two org-tier tests the new recipe adds.
No regression at any point.

**External reviewers:** None configured.

### Findings

**[BLOCK] tools/ab_control.py:102 — the tool reports success while
destroying the treatment recipe when its source and destination roots
coincide.**

Found by `/security` (filed there as a non-security footgun) and confirmed.
`src` is `<source-root>/recipes/<slug>/ORG-CHARTER.md` with `--source-root`
defaulting to `.`, and `dest` is `<root>/recipes/<slug>/ORG-CHARTER.md`.
Nothing compares them, so `python tools/ab_control.py quillon-harbor --root .`
strips the knobs out of the committed treatment recipe in place.

Reproduced against a copy:

```
before: knobs present?  3
control arm: stripped doc_culture.outline_variety,
             doc_culture.client_facing_reports, engagements.scope -> ...
after:  knobs present?  0
```

Three things make this worse than a bad flag. The run prints its normal
success line while doing it. The double-derive guard cannot help, because
`removed` is non-empty on the run that does the damage; it fires only on the
*next* run. And that guard's message then reads "That recipe is already a
control arm", which a reader takes as "nothing to do" rather than "your
treatment arm is gone".

The outcome is precisely the failure `test_deriving_from_a_control_arm_is_an_error`
exists to prevent: both arms become controls, ~20 authoring batches are spent,
and the experiment reports a null result that is an artifact of the tooling.
Git recovers the file, which is the only reason this is not worse, but nothing
in the run tells you to look.

Suggested fix: refuse when `src.resolve() == dest.resolve()`, before writing.

**[WARN] tools/ab_compare.py:249 — the tool prints "identity fields
identical" on paths where it never compared them.**

`compare()` returns early at line 119 (manifest lengths differ) and line 127
(manifest order diverged) before `counts` is ever populated, so no
`manifest:<field>` message reaches `unattributed`. `main()` then derives its
headline line from the *absence* of those messages:

```python
identical = [f for f in IDENTITY_FIELDS
             if not any(u.startswith(f"manifest:{f} ") for u in unattributed)]
print(f"identity fields identical: {', '.join(identical)}")
```

Reproduced by truncating one arm's manifest to 76 of 77 lines:

```
identity fields identical: doc_id, genre, date, authors, path, format,
                           engagement, title, rev, authoring

UNATTRIBUTED differences (1):
  manifest length differs: 77 vs 76. ...
exit=1
```

The two arms do not even contain the same number of documents, and the first
line of the report certifies all ten identity fields as identical. The exit
code is correct, so nothing automated is misled; a human reading the output
top-down is. This tool exists to certify that the comparison is controlled,
which makes a false reassurance in its headline the one output it must never
produce.

Suggested fix: have `compare()` report whether the identity check actually
ran (a third return value, or a sentinel entry in `unattributed`), and print
"identity fields: NOT CHECKED (bailed before the per-entry comparison)" on
the early-return paths.

**[WARN] tools/ab_compare.py — the pre-registered discriminating analyses are
not implemented, only the one the standard calls weakest.**

`docs/M17C-EVIDENCE-STANDARD.md` (committed in the same commit) names three
analyses and is explicit that the headline structural comparison is "weak
evidence" because dealing skeletons and enforcing what they forbid makes a
shape drop close to mechanically guaranteed. The two it calls discriminating
are:

1. treatment pairs whose documents share an outline id, against control pairs;
2. the lexical axis (same-genre 4-gram Jaccard) across arms.

`--structure` implements neither. There is no code reading
`render_params.outline` to group pairs, and no `jaccard`/`shingles` import.

This is not a bug and criterion four does not ask for more. It is a
methodological risk specific to a pre-registered experiment: the value of
fixing the standard before the data is that the analyses cannot be chosen to
suit the numbers, and that guarantee is only as good as the analyses being
*implemented* before the numbers exist too. Both arms are still unauthored,
so the window to close this cleanly is open now and shuts the moment the
first batch lands.

Suggested fix: implement both before authoring starts. Larger than the fix
loop's per-fix budget; tracked as follow-up work rather than delegated to
`/codefix`.

**Resolved after the fix loop, by the author rather than by `/codefix`, and
that carries a caveat recorded below.** `outline_of`, `split_by_outline` and
`lexical_scores` now implement both analyses, wired into `--structure`, with
five tests in `tests/test_unit_ab_discriminating.py`. One design point worth
keeping: `lexical_scores` keeps pairs scoring zero, where `metrics.compute`
drops them. Dropping is right for a reading list and wrong here, because two
arms with different counts of non-overlapping pairs would then have different
denominators for a reason unrelated to the treatment.

**[WARN] tests/test_unit_ab_control.py:113 — the test's name and docstring
promise an error path it never exercises, and it carries a dead assignment.**

```python
def test_deriving_from_a_control_arm_is_an_error():
    """Running the tool twice must not silently yield two identical arms."""
    _, control_text = None, strip_arm_knobs(_recipe_text())[0]
    _, removed = strip_arm_knobs(control_text)
    assert removed == []
```

The error lives in `ab_control.main()`, which raises `SystemExit` when
`removed` is empty. This test never calls `main()`; it asserts only the
precondition that guard keys on. The name claims coverage of the failure
mode the docstring describes as "quiet and expensive" (two knob-off corpora
authored at full cost and reported as a null result), and a reader auditing
which failure modes are covered would be misled by it.

`_, control_text = None, ...` also binds `_` to `None` for no reason.

Suggested fix: call `main()` against a stripped recipe and assert it exits
non-zero, or rename to `test_stripping_an_already_stripped_recipe_is_a_noop`
and drop the dead binding. The first is better: it covers the guard.

### Fixes Applied

Cycle 1 (`/codefix`), both verified by re-review:

- **[WARN] tools/ab_compare.py:249** — `compare()` now returns a third value,
  whether the identity check ran, `False` on both early-return paths.
  `main()` prints "identity fields: NOT CHECKED (bailed before the per-entry
  comparison)" instead of deriving "identical" from an absent complaint.
  Re-ran the original repro: the false headline is gone, and healthy arms
  still report all ten fields identical.
- **[WARN] tests/test_unit_ab_control.py:113** — the test now writes a
  stripped recipe to `tmp_path` and drives `ab_control.main()`, asserting a
  non-zero exit and that no derived recipe was written. Dead `_ = None`
  binding dropped.
- Added `tests/test_unit_ab_compare.py` (4 tests) covering the corrected
  behavior. No caller of `compare()` was left on the old two-value signature.

Cycle 2 (`/codefix`), verified by re-review:

- **[BLOCK] tools/ab_control.py:102** — `main()` now refuses when
  `src.resolve() == dest.resolve()`, before `mkdir` and before writing, with
  `dest` computed ahead of `strip_arm_knobs` so the refusal is reached first.
  New test drives `main()` with `--root == --source-root` and asserts both a
  non-zero exit and that the treatment recipe survives byte-for-byte.
  Verified by hand: `--root .` now exits 1 and leaves `recipes/` clean
  (`git status` empty); deriving into a separate root still strips all three
  knobs and exits 0.

After the loop, by the author: the deferred WARN (both discriminating
analyses), with tests.

**Review-integrity caveat.** The deferred WARN was fixed by the author, not
by `/codefix` in a forked context, so `outline_of`, `split_by_outline`,
`lexical_scores` and their report wiring have not had an independent
reviewer. The builder/verifier separation the rest of this entry relies on
does not cover them. They should be the focus set of the next refresh
review. Known gap in their coverage: like `arm_pairs`, `lexical_scores` is
tested at the arithmetic level only, because exercising it end to end
requires authored prose that does not exist yet.

### Accepted Risks

None.

---
*Prior review (2026-08-02, commit f0aacdc): refresh review of the M17b NOTE
closures (the `validate` printer sanitizer and the `count_noun` guard); one
WARN on the sanitizer dropping the f-string's type coercion plus two NOTEs
carried from `/security`, all fixed at the user's instruction before pushing.
0 BLOCK.*

<!-- REVIEW_META: {"date":"2026-08-03","commit":"9dcc15c","reviewed_up_to":"9dcc15c","base":"origin/main","tier":"refresh","block":1,"warn":3,"note":0} -->
