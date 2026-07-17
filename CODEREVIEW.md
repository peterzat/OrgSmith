# CODEREVIEW

## Review — 2026-07-17b (commit: 59870b5)

**Summary:** The pre-M12 turn: `62a5665..HEAD`, 15 commits, 29 files. Absorbs an
external critique (`docs/EXTERNAL-CRITIQUE-2026-07-17.md`), fixes the three
defects in it that verified, restructures the README around the exemplar, and
logs ten BACKLOG entries scoping M12. `bin/test` **447** passing (14 short /
361 unit / 72 org), up from 440; 441 + 6 skipped without LibreOffice. Byte pin
green fleet-wide; no committed ledger moved.

**Reviewer separation:** the author wrote everything here, so the review was
delegated to a fresh-context adversary instructed to recompute every number
against the repo rather than read for plausibility. It reported 1 BLOCK, 2
WARN, 2 NOTE; all are fixed (the metadata footer records what remains,
which is nothing), and it also independently confirmed a false
positive the author had already caught. The author caught four more before it
reported. **Every finding in this review, from either side, died on a command
rather than on a careful reading** — which is the whole lesson of the range:
each false claim looked right, and several had already survived a board pass,
a prior review, and a docs pass.

### Findings

**[BLOCK] TESTING.md:271 — "434 passing + 6 skipped" after the count-update
pass.** *(fixed; found by the adversary)*

  Commit `3c0a1d0` is titled "Record the new counts: 440 -> 445", updated lines
  18-19 and 53-55, and missed the third site. The adversary measured rather
  than inferred it: `soffice` hidden from `PATH`, `pytest -m "short or unit or
  org"`, counted progress characters because `addopts = "-q"` suppresses the
  summary — exactly 439 `.` and 6 `s` at the time.
  Why it matters: this is the same failure mode as the two README BLOCKs from
  the prior review — a stale number surviving the very pass that updated its
  siblings — and it landed inside the document whose job is to be the source of
  truth for the gate. Three occurrences, one updated pass, one missed.
  Fix: all four sites now agree at 447 / 441 + 6, both re-measured.

**[BLOCK] README — claimed our recipe coherence test would reject a tuning it
accepts.** *(fixed before the commit landed; author)*

  A sentence arguing no recipe setting closes the fee/revenue gap said the
  absurd-low-revenue tuning "this repo's own recipe coherence test would
  reject". It would not:
  `test_fleet_recipe_growth_headcount_and_span_describe_one_firm` asserts
  `margins[-1] < _NET_MARGIN_CEILING` (0.40) — a ceiling with no floor
  (`tests/test_org_regen.py:112,252`). A twelve-person firm turning over less
  than one salary posts a deeply negative margin and passes.
  Why it matters: the false claim was invoked as evidence *for* another claim,
  propping up the divergence argument with a fiction. Found by opening the test
  instead of trusting the memory of it. The adversary independently confirmed
  both the ceiling-only reading and the correction.
  Fix: the README says the true thing and names the gap. Logged as
  `recipe-coherence-test-has-no-floor`.

**[BLOCK] README — the board's "34 occurrences" published as a ledger fact,
under a sentence promising every quoted finding was ledger-verified.** *(fixed;
author)*

  The count is semantic, not arithmetic: the board's own evidence includes
  "This is easy to do from the start and impossible to retrofit" (`d:0011`) —
  the rhetorical move without the construction. No ledger owns "is this the
  same figure".
  Why it matters more than the number: the README's credibility rests on the
  rule that a finding which cannot be confirmed against a ledger is reported as
  opinion. This was the one finding that had escaped the rule, and it survived
  the M11b board pass, the review that BLOCKed two other false README numbers,
  and a full docs pass — because it looks like a measurement.

**[WARN] airlock — the docstring promised a guarantee the code did not
deliver.** *(fixed; found by the adversary)*

  `emit_author_batch` claimed `_fresh_work_order_path` "turns that race into a
  failed run rather than a lost order". It did not: `exists()` returned a path
  and `write_model` ran in the caller, so two dispatchers could both see the
  serial free, both write, and one order would be silently lost — precisely the
  loss `_next_serial` exists to prevent. The check narrowed the window without
  closing it.
  Why it matters: an overstated safety claim is worse than none, because it
  stops the next reader from looking. Note the neighbouring `_next_serial`
  docstring was honest about the same risk; the guarantee crept in one function
  over.
  Fix: the code now delivers the sentence rather than the sentence being
  softened. Renamed `_claim_work_order_path`, and the claim *is* the creation —
  `touch(exist_ok=False)`, `O_CREAT | O_EXCL` — so the kernel picks the winner
  and the loser exits. Pinned by `test_claim_work_order_path_claims_by_creating`.

**[WARN] The voice-tic number was published wrong three times.** *(fixed)*

  First as the board's 34 presented as fact (above). The correction published
  "20 across 17, the reproducible floor" — one arbitrary regex dressed as a
  bound, using a pattern never printed; caught by the author trying to
  reproduce it. The next correction published "a strict temporal reading finds
  5", which the adversary could not reproduce either, getting 3 and 11 from two
  equally natural strict patterns.
  Why it matters: that is the finding, not a slip. Measured over the 44
  authored documents, the count runs from single digits (strict, and mutually
  disagreeing) to 146 across 43 of 44 (the plain words `rather than`, once per
  200 words). Any single number is taste wearing a decimal point.
  Fix: the README cites the spread and the one count reproducible without being
  told the pattern.

**[WARN] docs/SCALE.md — "the flagship row is measured rather than projected".**
*(fixed; author)*

  No 2,000-document org exists; 2,000 x 694 is arithmetic. What M11b bought is
  that the multiplicand is measured fleet-wide. The old wording said the same of
  a "fourth row" and was wrong for the same reason — prose left behind by a
  change to the thing it describes, which is the defect this same commit range
  was fixing elsewhere in the same file.

### Notes

- **[NOTE] `_next_serial` crashed on exactly what its docstring promised to
  tolerate.** *(fixed; adversary)* It said unparseable names are ignored, then
  gated on `tail.isdigit()` and called `int(tail)`. `"²".isdigit()` is `True`
  and `int("²")` raises; `"٣"` would have parsed as 3. So the gate both crashed
  on a stray and silently interpreted one. `isascii()` before `isdigit()`,
  pinned by `test_next_serial_tolerates_strays_rather_than_interpreting_them`.
  Pathological, but a function that fails the promise in its own docstring is a
  docstring nobody should trust.
- **[NOTE] Soft levers named next to the voice finding.** *(fixed; adversary)*
  `Charter.narrative` and `Person.persona` sit adjacent to the voice collapse.
  Neither fixes it — the board's point is that twelve sharply-different personas
  already converge on one figure — but the section's own standard is to name the
  knobs in the neighbourhood, so it now does.
- **[NOTE] Reviewer false positive, the fifth, and confirmed as such by the
  adversary.** An exploration reported `BACKLOG.md`'s `$500,500` as a miscount a
  prior review had already BLOCKed. It is correct: `$500,500` is lifetime fees
  against `$20,712,000` lifetime revenue (2.42%). The README's `$425,500` is a
  different quantity — the five engagements the 2021 overview calls the whole
  business. The same report's *other* half was right (the "four of six
  reviewers" miscount), which is the most expensive kind of wrong. Verified
  before acting, per the standing rule.
- **[NOTE] Advertised an unbuilt feature for one edit.** A README line said
  duplicate/version chains "left this list at M12", which reads as shipped.
  M11b criterion 4's rule is that no commit leaves the repo advertising what it
  does not have. Rephrased before the commit.
- **[NOTE] Three pre-existing defects fixed, all the same species.**
  `docs/SCALE.md` contradicted itself about M12's own sizing (ordinals left
  dangling when the rows they pointed at were deleted); the README advertised a
  45-day email spacing M9 removed; `BACKLOG.md` miscounted the board's
  reviewers. Each is prose that outlived the thing it described. The email one
  has a measured cost: the external critique read that line and reported a fixed
  defect as live.
- **[NOTE] What the adversary verified clean** is most of the value and does not
  fit here: 445-at-the-time exact, northgate 53, 19/19 contracts with no miss or
  double-count, emit-schemas byte-stable and matching the commit, the pin failing
  on drift, all 11 `.eml` "Email 1", every recipe's `format_mix.eml` <= its
  engagement count, `$500,500`/`$425,500`, 1.6-5.1% (min 1.59 meridian, max 5.05
  dev-mini), 36% weekend (19/53), 1,299-day gap, the whole fleet table, the SCALE
  token table at 1.33 tok/word, ~334 and 38 batches, every link and anchor. It
  also proved the new serial tests fail against the old code, and enumerated the
  full `Charter` surface to confirm the README's divergence claim holds against
  all five findings.

**[WARN] tests/test_short.py:88-91 — the remediation advice loops when a schema
is retired.** *(fixed by /codefix)*

  Evidence: `test_committed_schemas_match_the_models` asserts
  `committed == expected` and fails with "missing {...}, extra {...}; run
  emit-schemas". But `run_emit_schemas` only writes; it never prunes
  (`schemas_export.py:80-84`). Reproduced: plant `retired@1.json` in the output
  directory, re-run `emit-schemas`, and the stray survives. So for the `extra`
  half of that assertion, the instruction the test prints does not fix the
  failure it prints it for, and the reader loops.
  Reachable only when a schema id is removed or renamed — which has never
  happened (all 19 ids are still `@1` after eleven milestones) but is exactly
  what a version bump does, and M12 is the first turn likely to need one.
  Why not fix by pruning: `--out` is an arbitrary operator-chosen directory, and
  a command that silently deletes unrecognized files out of a path you handed it
  is worse than a stale file.
  Fix: the message now routes each half of the assertion to the action that
  clears it — re-emit for `missing`, delete by hand for `extra`, with the reason
  stated inline. Verified through the real assertion path (planted stray) rather
  than by reading the f-string.
  **The finding cited the wrong line and /codefix caught it.** Line 94 is the
  *second* assertion (content drift), whose "run emit-schemas" advice is correct
  — a stale-content failure genuinely is fixed by re-emitting. The looping
  assertion is the set comparison at 88-91. Recorded because a reviewer citing
  the wrong line is the same defect class as everything else in this review:
  a plausible reference that nobody re-derived.

- **[NOTE] `orgsmith/airlock.py:79` — the work-order read path does not enforce
  the directory the module docstring promises.** *(from `/security`; not fixed —
  NOTEs are not auto-fixed)* `state.outstanding` and `BatchRef.workorder` carry
  no pattern (`state.py:48,69`), so they validate as free strings and reach
  `paths.workorders_dir / name`. Pathlib discards the base when the right operand
  is absolute, so a `state.json` naming `/etc/passwd` resolves to itself, and
  `/forge` hands that path to a worker whose first instruction is to read it.
  Confirmed by execution, not by reading. NOTE because anyone who can write
  `state.json` can usually write `orgsmith/*.py` and win more directly — but the
  boundary is real on paper (every org commits its `state.json` and orgs are
  publishable artifacts), and `docir_path` already took exactly this guard after
  an identical NOTE. Left for a human decision rather than fixed inside a review
  of unrelated work.

### Fixes Applied

All BLOCK and WARN findings fixed. Tests 440 -> 447: 5 unit (work-order serial,
the claim-by-creation race, stray tolerance), 2 short (schema export pin). The
final WARN was fixed by `/codefix` in a forked context rather than by the
reviewer, per builder/verifier separation — and it repaid that separation
immediately by catching the reviewer's own wrong line citation.

### Security

0 BLOCK / 0 WARN / 0 NOTE (`SECURITY.md`, `62a5665..HEAD`, scope `paths`, 29
files). Swept per-commit with `git log -p` rather than the net diff. Product
code changed this time, so the sweep read `schemas_export.py`'s path handling
(filenames derive from `Literal` schema ids, not input; `--out` crosses no
privilege boundary) and its one `https://` string (the JSON Schema dialect
identifier, written into a file, never fetched — no client, no network import).
Outbound disclosure was the real surface: the verbatim external critique
publishes into a public repo and contains nothing non-public.

### Accepted Risks

- **The adversary reviewed a moving tree.** HEAD advanced four commits while it
  worked and it said so, re-pinning its findings to the then-current commit.
  Three of those commits were self-corrections of things it was mid-way through
  flagging, so its independence on those is partial: it confirmed fixes rather
  than finding the defects cold.

---
*Prior review (2026-07-17, `f7f945c`): the docs pass — 1 BLOCK / 1 WARN / 4
NOTE, all fixed. The BLOCK was a false "all 29 rules" claim left standing in
the document the README cites as authoritative, after the same sentence had
already been fixed in the README.*

<!-- REVIEW_META: {"date":"2026-07-17","commit":"59870b5","reviewed_up_to":"f538f0dc29a6eb2ae0929158b00ce9b614f36c62","base":"origin/main","tier":"full","block":0,"warn":0,"note":6} -->
