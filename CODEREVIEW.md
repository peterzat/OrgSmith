# CODEREVIEW

## Review — 2026-08-02 (commit: e35e6eb) — M17b, the batch-boundary turn

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

### Accepted Risks

None.

---
*Prior review (2026-08-02, b6becc7): the M17 regeneration and close; 0 BLOCK,
1 WARN fixed (README/CLAUDE.md overstated what the mail recipient exemption
achieved), 2 NOTEs accepted (the `_chain_member_date` business-day ceiling,
and `tools/checksums.py` importing the package version).*

<!-- REVIEW_META: {"date":"2026-08-02","commit":"e35e6eb","reviewed_up_to":"e35e6eb180aff01202061e51b9cda08160ddc206","base":"origin/main","tier":"full","block":0,"warn":7,"note":0} -->
