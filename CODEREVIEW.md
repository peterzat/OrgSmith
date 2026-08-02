# CODEREVIEW

## Review — 2026-08-02 (commit: f0aacdc) — M17b NOTE closures (refresh)

**Review scope:** Refresh review. Focus: 11 file(s) changed since the prior
review (commit `e35e6eb`) — the fix pass and the two NOTE closures. 18
already-reviewed file(s) checked for interactions only.

**Summary:** The nine focus files carrying the fix pass were reviewed and
verified at full depth in the prior entry below. New material this pass is
the two NOTE closures: the `validate` printer sanitizer and the `count_noun`
guard. One WARN on the printer change itself, plus the two NOTEs `/security` returned this pass, all fixed at the user's instruction to clear notes before pushing.

**External reviewers:** None configured.

### Findings

**[WARN] orgsmith/validate/__init__.py — the sanitizer dropped the type
coercion the f-string provided, in the printer whose job is never to fail.**

The line it replaced was
`print(f"{f['severity']} {f['rule']} [{f['target']}] {f['message']}")`, and an
f-string coerces anything. `strip_control` iterates its argument, so it
requires a `str`:
```
str       : ok
PosixPath : TypeError: 'PosixPath' object is not iterable
int       : TypeError: 'int' object is not iterable
```
No live bug: an AST scan of all 74 `yield (message, target)` sites in
`rules.py` shows every target is a `str` today (`e.path`, `entry.path`,
`eng.id`, `fact.id`, string literals, `str(ctx.paths.share_dir)`, and `rel`
from `expected_empty_dirs() -> list[str]`). Verified rather than assumed.

The risk is latent and specific: rules build paths as
`ctx.paths.share_dir / rel` constantly, and `rules.py:717` already wraps a
target in an explicit `str(...)` — evidence that yielding a non-`str` is a
mistake somebody has already made once. Before this change that mistake
printed fine; now it raises out of the validator's own reporting path, which
is the one place that must survive bad input, and it would do so only on the
org that triggers the finding.

Suggested fix: coerce before sanitizing (`strip_control(str(...), keep="")`),
restoring exactly the robustness the f-string had. Cheaper than an ongoing
convention that every rule author must remember.

**[NOTE -> fixing, at the user's instruction] orgsmith/naming.py
(`strip_control`) — neutralizes control characters but not the bidi format
characters that visually reorder a terminal line.**

From `/security` this pass. `strip_control` acts only on
`unicodedata.category(ch) == "Cc"`. U+202E RIGHT-TO-LEFT OVERRIDE, the
isolates U+2066-U+2069 and U+200B are category **Cf** and pass through
unchanged, so the printer just hardened against ANSI escapes still lets a
hostile ledger string reverse the remainder of the line it prints. Same
read-the-wrong-thing outcome by a different mechanism (Trojan Source,
CVE-2021-42574): a tampered path or principal can be made to display as an
untampered one. `review/report.py`'s `_cell` calls the same sanitizer and
inherits the same gap on the artifact that PERSISTS.

Measured before filing: **no `Cf` character appears anywhere in the repo** —
not in any committed org artifact, recipe, doc, or source file — so widening
the sanitizer moves no committed byte and cannot change a rendered report.

Suggested fix: widen `strip_control` to treat category `Cf` as control. One
change covers the validate printer, `_cell`, and every other caller, which is
the same argument that put the previous fix at the printer rather than at
each interpolation site.

**[NOTE -> fixing, at the user's instruction] orgsmith/review/report.py:310 —
the integrity dashboard escapes a finding's message but not its target.**

From `/security` this pass, and the worse of the two because the sink
persists. `_integrity_lines` writes
`f"- {f['rule']} [{f['target']}] {_cell(f['message'])}"` into
GENERATION-REPORT.md. A MAN-01 target is a raw filesystem name from
`share_dir.rglob("*")` — `check_relpath` guards manifest entries, not strays
— so a stray file whose name embeds a newline forges a second list item, and
a `|` breaks a row wherever the pattern is reused in a table. `_cell`'s own
docstring is the argument: "this artifact PERSISTS: unlike a rejection
printer that scrolls past, a forged row here is what a human reads later."

Suggested fix: `_cell(f['target'])`, matching the message beside it.

### Fixes Applied

- [WARN] `orgsmith/validate/__init__.py` — `str()` before `strip_control` at
  all six interpolation sites, restoring the coercion the f-string provided.
  Regression test added (`test_findings_printer_survives_a_non_str_target`),
  proven non-vacuous against the pre-fix printer.
- [NOTE] `orgsmith/naming.py` — `strip_control` neutralizes Unicode category
  `Cf` as well as `Cc`, closing the bidi-reordering gap for the validate
  printer, `_cell`, and every later caller at once. Two tests added (a bidi
  override is neutralized; `keep` is still honored).
- [NOTE] `orgsmith/review/report.py` — a finding's target now goes through
  `_cell(str(...))` beside its message. Test added in
  `tests/test_unit_review.py`.

### Verified, not filed

- **The `Cf` widening moves no committed byte.** Surveyed every text artifact
  under `companies/`, plus `recipes/`, `docs/`, `orgsmith/` and `tests/`: no
  `Cf` character appears anywhere in the repo. Confirmed downstream by the
  org and flagship tiers staying at 228 (+27) and 65 (+5) across all three
  fix cycles, and by `strip_control` leaving clean text identical.
- **Every fix in this entry carries a test, each proven non-vacuous** by
  reverting the fix and watching it fail. Four added across the cycles
  (unit 712 -> 716): the non-`str` target, the bidi override, `strip_control`
  still honoring `keep`, and `_integrity_lines` escaping a target that
  carries a newline and a pipe. The last needed a monkeypatched `collect` to
  reach it at all, because the error branch never fires on a committed org.
- **Three cycles used, which is the skill's limit**, and the third produced
  no new finding. Stopping here is the process working, not a budget
  exhausted mid-problem.

### Accepted Risks

None.

---

## Prior entry — 2026-08-02 (commit: e35e6eb) — M17b, the batch-boundary turn

**Summary:** Full-depth review of the ten M17b commits: the structural
similarity axis, engagement scope facts with SCOPE-01, position-gated scope
citation, scope eval prompts, the client-facing-report knob, per-document
section skeletons with OUT-01, ingest outline conformance, and the close. No
fixture was regenerated, which the diff confirms: nothing under a
`companies/*/ledger`, `docplan`, or `docir` path moved.

Seven WARNs, no BLOCKs, all fixed over two cycles. They clustered on two
themes rather than on the mechanisms themselves: the new code is correct on
the paths that run, and what was weak was (a) input validation at the recipe
boundary, where a malformed `ScopeProfile` defeated the invariant the design
rests on, and (b) three published guarantees that overstated what the code
delivers. The seventh is the fix pass's own test debt. Every finding was
reproduced before being filed and re-verified after the fix.

Test suite across both cycles: 16 short / 708 unit / 228 org (+27 skipped) /
65 flagship (+5 skipped). The org and flagship tiers never moved, which is
the check that matters here: the fixes are inert against the frozen fleet.

**External reviewers:** None configured.

### Findings

**[WARN, FIXED] orgsmith/schemas.py (`ScopeProfile._check`) — the distinctness
guard checked phrases, but SLUGS become fact ids.**

`_check` rejected duplicate `pipeline` phrases with the comment "they become
fact ids". They do not: `stage_slug()` does. Reproduced:
```
pipeline=["candidates screened", "Candidates  Screened!"]   # accepted
slugs   -> ['candidates-screened', 'candidates-screened']   # DUPLICATE ids
```
It failed loudly but at a distance — `fact_index()` raising
`ValueError: duplicate fact id` at the end of `build_engagements`, naming a
fact id and giving no hint that two recipe phrases collided.

Second hole in the same guard: `pipeline` items carried no `min_length`, so
an empty or punctuation-only phrase was accepted and produced a rendered
surface that is a **bare numeral** (`f:E-2019-001.pipeline- -> '40 '`). That
defeats the one invariant the design rests on (`render_count`: a bare numeral
matches inside `$11,000` and inside every date, and `build_diagnostics` scans
every planted value corpus-wide). `unit`/`comparator` were weak the same way:
`min_length=1` admits `" "`.

Fixed: `_check` now slugs every noun phrase and rejects empty slugs
(`unit`, `comparator`, each stage) and duplicate stage slugs. Verified: all
three malformed profiles are rejected at parse with an actionable message,
and a valid profile still parses.

**[WARN, FIXED] orgsmith/validate/rules.py (`scope_01`) — the rule crashed
instead of reporting when a funnel value was tampered to a non-integer.**

The value-drift loop yielded a finding but did not `continue`, so execution
reached the monotonicity comparison with a mixed-type list:
```
TypeError: '>' not supported between instances of 'int' and 'str'
```
The already-yielded finding was lost with it, because `collect()`
materializes the generator. A validator that dies on the tamper it exists to
detect is neither a finding nor a visible skip.

Fixed: a type guard reports non-integer stage values as a finding and stops
comparing. Verified: the same tamper now yields 2 findings (the drift and the
type) instead of a traceback.

**[WARN, FIXED] orgsmith/validate/rules.py (`scope_01`) — an EXTRA planted
count fact was invisible.**

`got` was filtered to `f.id in want`, making the comparison one-directional.
An injected `f:E-2019-001.pipeline-fabricated` produced **0 findings**, though
the rule's docstring and the spec criterion both say it compares ids
"exactly".

Blast radius was bounded and is worth keeping on the record: an injected fact
with no manifest host produces no eval question (`build_extraction` skips
unhosted facts, verified), so the answer key was never at risk. The gap was
tamper evidence only.

Fixed: the id set is compared both ways. Verified: the injected fact now
yields "the ledger carries 1 count fact(s) the charter does not plant".

**[WARN, FIXED] orgsmith/docplan/planner.py (`_participant_ids`) and
docs/RECIPE-FORMAT.md — the stated reason for scoping `client_facing_reports`
to one genre was factually wrong.**

Both said the knob is genre-scoped "because the row is also read by the ACL
and the participant-scoped posture: widening it wholesale would grant every
client contact read access to internal reports."

`derive_acl` never reads manifest or rule participants. It reads
`eng.internal_participants` off the engagement ledger (`acl.py:115`); `acl.py`
contains no reference to `entry.participants`. The knob has no ACL effect in
either form. The independent `/security` pass reached the same conclusion
from the authorization side. The second half was also unsupported:
`participants="team"` is used by exactly one genre, so "widening the row" and
"scoping to the genre" were the same change.

Fixed: both sites now state the real constraint — `participants` is the
vocabulary the eml renderer derives `To`/`Cc` from, which is load-bearing for
mail genres and not for `status_report` — and record that there is no ACL
effect.

**[WARN, FIXED] orgsmith/docplan/registry.py (`assign_outlines` docstring) —
the cycle guarantee was overstated.**

It claimed "no variant repeats within any k consecutive documents of a
genre". Searched over 400 seeds with `status_report` (k=4):
```
seed=0: positions 6 and 8 (distance 2 < k=4) share a variant
```
The true property, verified over the same seeds: every ALIGNED block of k
picks is a permutation of the pool — which yields "the first `min(k, n)` are
all different", exactly what the B3 count guarantee needs. The code was
correct and the tests assert the true property; only the stated bound was
wrong. The same overclaim was in the B3 commit message.

Fixed: property (1) restated as the aligned-block permutation plus its
corollary, naming the counterexample so nobody re-derives the stronger claim.

**[WARN, FIXED] orgsmith/authoring/contexts.py — a brief could carry
self-contradictory structural guidance.**

`_outline_guidance` was appended after `_GENRE_GUIDANCE` without amending it,
so on a real emitted work order:
```
d:0003 kickoff_memo outline=km-narrative forbids=('list','table')
   genre guidance: "...then a list of workstreams..."
   outline block:  "This document must contain NO list, table block ...
                    A deliverable carrying one is rejected."
```
The author was told to write a list and told the deliverable is rejected if
it contains one, resolved only by a later override sentence. M16's own
finding — carried into this spec's context — is that brief-level instructions
only reliably stop literal strings, which is why this turn moved the fix into
the plan; leaning on an override sentence reintroduced the weak mechanism at
the last step. Bounded (ingest rejects the list, so no bad document lands) but
it costs a worker a rejected round trip on a document the plan set up to fail.

Fixed: when an outline is present the genre text is prefixed as a default,
explicitly superseded, so the framing precedes the clause it overrides rather
than contradicting it afterwards. Verified on `d:0003`, and knob-off briefs
carry no such framing.

**[WARN, FIXED] tests/ — none of the four new behaviours introduced by the
fix pass was asserted by a test.**

The fixes added four error branches and one brief-text change, and no test
covers any of them:
```
grep -rn "slug distinctly|must carry alphanumeric|does not plant|
          not integers|SUPERSEDED" tests/   ->  no matches
```
Each was verified by hand during re-review, which does not persist. This
repo's own convention (CLAUDE.md) is that changed functionality carries tests
in the same increment, and three of the four are validator branches — the
component whose whole value is being trustworthy. The `ScopeProfile` guard in
particular is the only thing standing between a malformed recipe and a corpus
of bare-numeral surfaces.

Fixed: seven tests added (unit tier 701 -> 708). Four `ScopeProfile`
rejection tests (slug collision, punctuation-only stage phrase, blank `unit`,
blank `comparator`), two SCOPE-01 branch tests, and one brief-framing test.
Two are worth naming because they close the exact regression each fix was
for: the non-integer test asserts the drift finding SURVIVES alongside the
type finding rather than being lost to a traceback, and the framing test
also asserts the contradiction it defuses is real, so it cannot pass
vacuously if the outline pools change.

### Fixes Applied

- [WARN] `orgsmith/schemas.py` — `ScopeProfile._check` validates slugs, not
  phrases: rejects empty slugs on `unit`/`comparator`/stages and duplicate
  stage slugs.
- [WARN] `orgsmith/validate/rules.py` — `scope_01` reports non-integer funnel
  values as a finding instead of raising `TypeError`.
- [WARN] `orgsmith/validate/rules.py` — `scope_01` compares the count-fact id
  set both ways, catching injected facts.
- [WARN] `orgsmith/docplan/planner.py`, `docs/RECIPE-FORMAT.md` — corrected
  the `client_facing_reports` rationale (eml `To`/`Cc` vocabulary; no ACL
  effect).
- [WARN] `orgsmith/docplan/registry.py` — restated the `assign_outlines`
  cycle guarantee as aligned-block permutation.
- [WARN] `orgsmith/authoring/contexts.py` — genre guidance is framed as a
  superseded default when an outline is present.
- [WARN] `tests/test_unit_scope_facts.py`, `tests/test_unit_outlines.py` —
  seven tests covering every branch the fix pass introduced.

### Verified, not filed

- **The fixes are inert against the frozen fleet.** No committed org carries
  a `count` fact or an `outline` render param, so SCOPE-01's new reverse
  id-set check and the brief framing cannot fire on the fleet; the org and
  flagship tiers are unchanged at 228 (+27) and 65 (+5) across both fix
  cycles, and `emit-schemas` plus `checksums.py --check` report no derived
  drift (a pydantic validator does not surface in the JSON Schema export).
- **`assign_outlines`'s stated priority order was checked, not assumed.**
  With the cycle emptied when full, the previous pick is always inside it,
  so `ids - cycle - {blocked}` is non-empty for k >= 2 and the third and
  fourth relaxation levels are unreachable — which is what makes the cycle
  and adjacency properties absolute rather than best-effort.
- **OUT-01's recompute order matches the planner's deal order.** The planner
  deals over `self.planned` before `_plan_noise` runs; OUT-01 recomputes over
  the full manifest sorted the same way. All four noise-creation sites pass
  `authoring="derived"`, and `assign_outlines` skips non-batchable rows
  before drawing, so interleaved noise cannot perturb the per-genre draw
  sequence. `_plan_noise` mutates no existing entry's date or path.
- **`TESTING.md` counts corrected** (952 total, 708 unit, and the tiers
  table) after the fix pass added seven tests. Recorded here because it is a
  review-adjacent doc edit, not a code change.

### Notes closed after the review, at the user's instruction

Both were standing NOTEs rather than review findings; recorded here because
they changed code after the review's marker was written.

- **[NOTE, FIXED] `orgsmith/validate/__init__.py` — the human findings
  printer emitted unconstrained ledger strings raw.** SECURITY.md's carried
  NOTE, open across two reviews. Validating an org tree obtained from
  someone else is supported, and findings quote fields pydantic does not
  constrain (`LedgerCheck.name`, `GraphEdge.src`, `AclGrant.person`,
  `Person.reports_to`), so a smuggled ANSI escape reached the terminal and
  could rewrite or hide earlier findings. Fixed at the printer, not at each
  interpolation site, so rules that do not quote with `!r` are covered and a
  later rule cannot reintroduce it; `keep=""` also stops a smuggled newline
  forging a finding line. `--json` stays raw for tooling. Two tests added,
  the first proven to fail against the pre-fix printer.
- **[NOTE, FIXED] `orgsmith/evals/emit.py` (`count_noun`) — `IndexError` on
  a spaceless rendered surface.** Recorded by the security pass as
  "robustness, not security" and deferred here. Reachable only from a
  hand-edited ledger, but it is the same class as the SCOPE-01 crash fixed
  above: a traceback where a clean result belongs. Now uses `partition`, so
  `emit-evals` completes and SCOPE-01 reports the tamper.

The two NOTEs from the prior review are deliberately NOT fixed: both were
recorded as accepted design trades, not defects. `_chain_member_date`'s
narrowed business-day ceiling is correct and its failure mode is a loud
CAL-01 error; `tools/checksums.py` importing the package version is what
stopped the hardcoded string going stale.

Suite after these: 16 short / 712 unit / 228 org (+27 skipped) / 65 flagship
(+5 skipped). Org and flagship unchanged again.

### Accepted Risks

None.

---
*Prior review (2026-08-02, b6becc7): the M17 regeneration and close; 0 BLOCK,
1 WARN fixed (README/CLAUDE.md overstated what the mail recipient exemption
achieved), 2 NOTEs accepted (the `_chain_member_date` business-day ceiling,
and `tools/checksums.py` importing the package version).*

<!-- REVIEW_META: {"date":"2026-08-02","commit":"f0aacdc","reviewed_up_to":"f0aacdca02396f413ba07f9d164583bf5576c18b","base":"origin/main","tier":"refresh","block":0,"warn":1,"note":2} -->
