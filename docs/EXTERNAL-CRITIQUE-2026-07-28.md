# External critique, 2026-07-28: findings and disposition

An outside reviewer cloned the repository, parsed all 66 documents of the
exemplar `northgate-staffing`, ran the validator, and reported. Its verdict:
**a strong integration fixture and corpus-generation research project, but
Northgate is not yet a trustworthy general-purpose benchmark.**

This is the second such review. The first is in
[`EXTERNAL-CRITIQUE-2026-07-17.md`](EXTERNAL-CRITIQUE-2026-07-17.md), which
reproduces its reviewer's reply verbatim.

## What this document is, and is not

**The reviewer's own text is not reproduced here.** It was delivered in a
planning session and was not recoverable when this file was written. Rather
than paraphrase someone's words and present the paraphrase as a quotation,
this document records only what the project can stand behind itself: the
findings as we verified them against the repository, our verdicts, and what
we did about each one. Everything below is our account, not the reviewer's.

That is a real loss. The 2026-07-17 document's most useful property is that
the critique is kept unedited, errors included, so a reader can judge the
review as well as the response. This one cannot offer that, and a reader
should weight it accordingly: it is a self-report of criticism received.

**Every material claim below was verified against the repository before this
document was written**, at `06cfc53` for the findings and at the commits
named in the disposition table for the fixes.

## The central finding

Not prose realism this time. The named defect was that **the evaluation
layer mistook planned provenance for rendered truth**: the answer key was
derived from what the generator planned to plant, not from what the final
documents visibly contain.

That is the right diagnosis, it is the most serious thing anyone has said
about this project, and every consequence below follows from it.

## Findings, verified

### 1. Derived copies were invisible to the answer key by construction

`schemas.py` forbids facts and mentions on derived documents, and
`evals/emit.py` stripped them from the answer manifest. Three of northgate's
13 derived documents are byte-identical to their sources (`d:0054` and
`d:0055` exact duplicates, `d:0065` a misfile of `d:0031` into `Finance/`),
so returning the byte-identical copy of the Coleman engagement letter for
"which documents state the fixed fee?" scored 40/41. **The system was
punished for returning a document that literally contains the answer.**

Verified true. This is the clearest defect in the set, and the one with no
defensible reading.

### 2. Mention gold was planned-only

`emit.py` read `mention_map` and never read rendered text. Sandra Fuentes
renders in 23 documents; `q:0030` listed 17, omitting six onboarding
records. `d:0006`'s prose calls James Weiss "simply Jim" twice while the
ledger alias and `q:0032`'s single-document gold bind "Jim" to James Grant.

Verified true, **and this is one of the two places the critique undershot.**
It read the mention disagreements as a wrong ledger. They are not: the
ledger is internally consistent and the prose is faithful to a persona that
claimed another person's alias. What was wrong was the *policy* — the answer
key had no way to say "this document also contains the evidence, and
returning it is not an error." That is a labeling gap, closed by acceptable
sets, not a data error to be corrected in a ledger.

The `Jim` collision itself is northgate's own published headline residual,
caught independently by four of six review-board reviewers before this
critique arrived.

### 3. Scoring was an exact-set unit test

Binary set equality, no ranking, no partial credit. Extraction computed
value and source correctness separately and then ANDed them, so "right value,
wrong document" was indistinguishable from "wrong value." The people graph
stripped all 22 participant edges at emit, because they point at engagement
ids an answer file had no way to name, and ignored edge dates entirely.

Verified true.

### 4. The split collapse

`build_splits` unioned visibility gold into the answer set, and ACL-02
guarantees every document is readable by someone, so every authored document
always landed in `core`.

Verified true, **and this is the second place the critique undershot.** It
read this as a northgate quirk. It is fleet-wide and structural: `core ==
distractors` on all nine committed orgs, measured at `06cfc53` — northgate
53/53, ashcombe 87/87, calderwood 183/183, hollowell 64/64, meridian 72/72,
saltmarsh 40/40, brackenridge 40/40, verdant 31/31, dev-mini 23/23. The
advertised four-point degradation curve had been a two-point one everywhere,
on every org, since splits shipped.

Finding this while checking the critique is the strongest argument in this
document for taking outside review seriously: the reviewer pointed at one
org and the defect was in all of them.

### 5. The exemplar demonstrated none of the headline hard cases

`northgate-staffing` had no scans, no legacy binaries, no signature-page or
filename-date facts, no mail threads, and an open ACL under which 11 people
read all 66 documents and one departed person reads none. Every one of those
capabilities was an existing, proven recipe knob on some other fleet org.

Verified true. The org a newcomer is told to read demonstrated the least.

### 6. No baselines, no data cards

Nothing told a consumer whether a question was meaningful or merely
structurally easy, and no per-org artifact stated the label policy, feature
coverage, or known contradictions.

Verified true.

### 7. Expanded question families

The critique asked for more question families. Partially adopted: unanswerable
questions landed this turn. Cross-document, temporal, and superseded-value
families were declined for now, because they need ledger fact histories with
validity intervals — already ruled a schema turn of its own in `BACKLOG.md`
(`noise-kinds-deliberately-excluded`).

### 8. External validity

Blind splits, leaderboards, confidence intervals, and a transfer program were
raised again, as in the 2026-07-17 review. Declined again, for the reasons in
`BACKLOG.md` (`external-validity-program`): it is a research program, not a
milestone, and it presumes a positioning decision made the other way. The
cheap slice was adopted instead (baselines and data cards), and every data
card states the non-claim explicitly.

## Disposition

| Finding | Disposition | Where |
| --- | --- | --- |
| 1. Derived copies invisible to the key | **Adopted.** Equivalence clusters, verified by hash at emit; a returned member satisfies its canonical, and the required set is never rewritten (membership is directional) | `evals/clusters.json`, `docs/LABEL-POLICY.md` |
| 2. Mention gold planned-only | **Adopted.** Scan-derived acceptable sets on mention and alias questions | `acceptable_docs`, `docs/LABEL-POLICY.md` |
| 2b. The `Jim` collision | **Adopted, twice.** Recorded mechanically as a diagnostic; made impossible by construction under a new knob | `evals/diagnostics.json`, `graph_targets.alias_agreement`, MENT-03 |
| 3. Exact-set scoring | **Adopted.** Macro P/R/F1, Recall@5/@10, MRR, nDCG@10; extraction value and attribution reported separately; engagements became graph entities so participant edges score; optional dated-edge credit | `orgsmith/evals/score.py` |
| 4. Split collapse | **Adopted, wider than reported.** Visibility gold no longer enters `core`; splits documented as a retrieval and extraction device | `docs/EVAL-SPLITS.md` |
| 5. Exemplar demonstrates nothing | **Adopted.** northgate regenerated under an enriched recipe; README gained per-capability pointers to the org that exercises each | this turn's carve-out |
| 6. No baselines, no data cards | **Adopted.** Two keyless retrievers per org per split; a data card per org | `docs/BASELINES.md`, `DATA-CARD.md` |
| 7. Expanded question families | **Partially adopted.** Unanswerable questions land; fact-history families deferred to their own schema turn | `answerable: false` |
| 8. External validity program | **Declined again.** Cheap slice adopted; transfer program stays out | `BACKLOG.md` |
| Onboarding (53 vs 66, doctor exit code) | **Adopted.** README count fixed; doctor scopes its probes by intent | README, `orgsmith/doctor.py` |

## Two deliberate gold changes

Both are recorded rather than absorbed, because they change what a previously
correct answer scores.

**Transmittal emails moved from gold to equivalence.** A transmittal carrying
a document byte-identically used to be unioned into `expected_docs` wherever
that document was an answer, which put an email in the canonical answer set
for a fact that lives in a memo. It is a cluster member instead. This changed
ashcombe's emitted gold.

**Splits changed fleet-wide**, per finding 4.

## What this turn did not do

- It did not reproduce the reviewer's text, for the reason at the top.
- It did not regenerate `hollowell-ip` or `meridian-actuarial`. The
  recipient-mention exemption knob that would close their full-name-in-body
  device is landed and proven inert, but the orgs were not re-run; their data
  cards record the device.
- It did not add a negative control for the review board. That remains open
  (`BACKLOG.md`, `board-negative-control`), though one finding class — the
  alias collision — moved from critic to oracle this turn.
