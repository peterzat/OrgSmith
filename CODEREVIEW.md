# CODEREVIEW

## Review — 2026-08-02 (commit: 6bd7d77)

**Summary:** The M17 answer-key turn: 16 commits since `06cfc53` adding the
shared doc-text reader, equivalence clusters, scan-derived acceptable sets,
diagnostics, unanswerable questions, ranked scoring, keyless baselines, per-org
data cards, EVAL-01, MENT-03, the doctor split, and the mail recipient
exemption. Full-depth review: the prior review's `reviewed_up_to` (`afa211a`)
precedes the base (`origin/main` = `06cfc53`), so the already-reviewed set is
empty. One BLOCK, three WARN, one NOTE; all four actionable findings fixed and
re-verified.

**External reviewers:** None configured.

### Findings

**[BLOCK, FIXED] orgsmith/evals/score.py — canonicalizing `expected_docs`
collapsed two genuinely distinct required documents, so a system that missed
one of them scored correct.**

Cluster membership is symmetric for `byte_copy` members (identical bytes) but
**directional** for `attachment` members: a transmittal email carries the
memo's bytes, so the email contains the memo's evidence, but the memo does not
contain the email's body. A transmittal is frequently required in its own
right, because its body states facts and names people.

On `ashcombe-advisory`, `q:0003` requires 16 documents including both
`2017.02.18 - Kickoff Memo …` and its transmittal `2017.03.15 - Email 1 …`.
Canonicalizing both sides collapsed the pair, so an answer omitting the
transmittal entirely (15 docs) scored the question CORRECT. Verified against
the committed fleet before the fix. The required set also silently shrank from
16 to 15, inflating the recall, MRR, and nDCG denominators.

This is a false accept in an eval harness, and it sat inside the commit that
claims to have fixed exactly that class of defect.

Fix: `_cover()` replaces canonicalize-both-sides. The required set is the
question's own `expected_docs` and is never rewritten; clusters only let an
answer *satisfy* a requirement. A required document covers itself (test first),
a cluster member covers its required canonical (second), acceptable documents
are dropped, everything else is extra. The condensed list for the ranked
metrics is built the same way. Applied to `_score_docset` and
`score_extraction`.

Verified: ground truth still scores 44/44 on ashcombe; omitting the required
transmittal from `q:0003` now fails with the transmittal reported missing.

**[WARN, FIXED] README.md, TESTING.md — published test counts were stale.**
README claimed 879/850; the docs commit recorded the counts before a later
commit added 7 unit tests. Re-measured and republished: 16 short, 615 unit, 226
org (+29 skipped) = 857 passed / 886 collected; flagship 65 (+5 skipped).

**[WARN, FIXED] orgsmith/docplan/planner.py — unguarded `doc["render_params"]`
where the same file treats the key as optional.** `_add(**kw)` appends whatever
kwargs it is given and three call sites pass no `render_params`; `plan_scans`
reads the same key with `.get`. Currently unreachable for those docs, but one
new eml call site would crash the planner. Now `doc.get("render_params", {})`.

**[WARN, FIXED] orgsmith/validate/rules.py — the validator imported a private
helper (`_mask`) from `evals.emit`.** The masking rule is now a shared contract
between the emitter and MENT-03, and the two must agree or they disagree about
the same document. Promoted to `orgsmith/doctext.py::mask_surfaces`, beside the
other shared text primitives; `emit.py`, `rules.py`, and the unit test import
it by its public name.

**[NOTE, not fixed] orgsmith/evals/emit.py — the alias scan over external
people is dead code.** `build_diagnostics` reads `getattr(person, "aliases",
[])` over `foundation.external_people`, but `ExternalPerson` has no `aliases`
field, so that half of the loop can never yield a sighting. Informational; left
as-is per the review's own instruction.

### Fixes Applied

- [BLOCK] `orgsmith/evals/score.py` — coverage-based grading (`_cover`)
  replacing canonicalization of the required set, in both suites and in the
  ranked/macro metrics and failure reporting.
- [WARN] `README.md:663`, `TESTING.md:19,63,301` — re-measured test counts.
- [WARN] `orgsmith/docplan/planner.py:770` — defensive `.get`.
- [WARN] `orgsmith/validate/rules.py`, `orgsmith/doctext.py`,
  `orgsmith/evals/emit.py` — `_mask` promoted to public `mask_surfaces`.

Two tests encoded the collapsed semantics and were corrected rather than
relaxed: `test_transmittal_is_an_equivalence_member_not_gold` and
`test_a_byte_identical_copy_of_a_required_doc_is_accepted`. Each now scopes its
substitution probe to questions that do not also require the copy in its own
right, with a guard assertion so the probe cannot become vacuous, and the mail
test gained a directional half asserting that omitting a required transmittal
reports it missing. Verified by reading both.

Derived artifacts recomputed: baselines for all nine orgs (only ashcombe
moved), `docs/BASELINES.md`, the data cards, and `CHECKSUMS.md`.
`docs/LABEL-POLICY.md` and the disposition row in
`docs/EXTERNAL-CRITIQUE-2026-07-28.md` stated the collapsed rule as the
contract and were corrected. `LABEL_POLICY_VERSION` deliberately not bumped:
the label semantics are unchanged, only the grading of an answer against them.

### Accepted Risks

None.

### Security

`/security` scanned the 15 in-airlock files (~2,400 added lines) over
`9927e03`..`6bd7d77`: **0 BLOCK / 0 WARN / 1 NOTE**. The NOTE is pre-existing
and not introduced this turn: `validate/__init__.py:69` prints validator
finding messages raw, and those messages interpolate unconstrained ledger
strings (`GraphEdge.src`, `AclGrant.person`, `LedgerCheck.detail`), while every
other verb routes untrusted strings through `strip_control`. It requires
validating a hostile org tree from a third party. Recorded in SECURITY.md.

Cleared explicitly: the new cluster-hashing and attachment-byte reads stay
inside the share (`load_manifest` re-checks `entry.path` and `attach_path` with
`check_relpath` at every load); `score --evals-dir`, the new third-party input
path, only reads and sanitizes its failure lines; board summaries reaching
`DATA-CARD.md` pass through `_cell`, which blocks table-row forgery; the one
subprocess (`tools/checksums.py`) uses a fixed argv with no shell.

### Test Baseline

All four tiers green: 16 short, 615 unit, 226 org (+29 skipped), 65 flagship
(+5 skipped). Keyless and offline. `python tools/checksums.py --check` current.

---
*Prior review (2026-07-28, commit afa211a): refresh review of the BYO
model-choice updates (default model ids and documentation); 0 BLOCK / 0 WARN /
0 NOTE.*

<!-- REVIEW_META: {"date":"2026-08-02","commit":"6bd7d77","reviewed_up_to":"6bd7d77","base":"origin/main","tier":"full","block":1,"warn":3,"note":1} -->
