# Board calibration

A critic is only worth reading if you know what it catches. This records
the board's first run against two labeled positives that were identified
by hand, before the board existed, in `fernhollow-partners`.

> **Two calibrations live here now.** The original run below calibrates the
> *board* (a model pass) against hand-labeled positives. The M17b section at
> the end calibrates the *structural axis* (a keyless proxy) against the
> board's own findings, which is the only direction that works: the board is
> not reproducible, so it can be a yardstick for a proxy but a proxy can
> never be a yardstick for it.

> **`fernhollow-partners` was retired by the M11b fleet reset (2026-07-17)
> and is no longer in the repo.** This document is kept as the historical
> record of the run: the calibration happened against that org, and the
> limits below are the limits of *that* run. It has not been re-run against
> the v2.0 fleet, so everything here describes a board calibrated on a
> corpus you can no longer open. Read the limits accordingly — and note that
> a false positive has since been measured (below).

The rule this run was held to: **a board that misses both is not
calibrated**, and its findings may not be relied on until it is tuned or
its limits are written down.

Run: 2026-07-16, against the committed fixture at v1.5.0. Six reviewers,
fresh context each, `claude-opus-4-8[1m]` at effort `xhigh` (self-reported
per reviewer). 26 findings: 11 major, 10 minor, 5 notes.

**Reviewers were not told what the labeled positives were.** They were
given the validator output, the sample, and their dimension. Naming the
answer would have made this a demonstration, not a calibration.

## The two positives

| pair | what it is | 4-gram Jaccard | metric | board |
| --- | --- | ---: | --- | --- |
| d:0001 / d:0008 | literal reuse: near-verbatim clauses | 0.2524 | **flags** (only pair over threshold, fleet-wide) | **surfaced**, verdict inverted |
| d:0001 / d:0016 | same rhetorical moves, different wording | 0.0459 | **misses** (below 0.15) | **surfaced**, exact evidence |

Both surfaced. The board is calibrated.

### d:0001 / d:0008 — surfaced, and the verdict inverted

Caught by `cross_document_voice` as `rf:voice-7`, a **note**, quoting the
shared confidentiality clause. But the reviewer did not agree it was a
defect:

> d:0001/d:0008 is the only pair in the corpus that reads as a real firm
> reusing its template, so the single similarity flag is a false alarm and
> the actual defect is inverted.

This is the board doing exactly the job the metric cannot. High same-genre
similarity was always ambiguous — real firms reuse engagement-letter
templates — and resolving that ambiguity was the board's assignment, not
the metric's. The metric measured, the board judged.

### d:0001 / d:0016 — surfaced, by a different dimension than expected

The n-gram metric provably misses this pair: at 0.0459 it sits near the
corpus noise floor, six times below the flag threshold, indistinguishable
from two unrelated letters.

The board surfaced it anyway — not from `cross_document_voice`, where it
was expected, but from `graph_acl_naturalness` (`rf:graph-1`, major),
which quoted precisely the evidence identified by hand during spec
drafting:

> "Sandra Perez, Director, **leads** the engagement day to day and is your
> first call..." (d:0001, 2020)
>
> "Sandra Perez, Director, **will run** the engagement day to day and is
> your first call..." (d:0016, 2024)

One verb apart, four years apart, and invisible to the metric. That the
finding arrived through the staffing lane rather than the voice lane is
worth recording: the dimensions overlap in practice, and a defect will
surface through whichever reviewer's question happens to point at it. Do
not read a dimension's findings as the complete set for that topic.

## What the run says about the instrument

**The proxy and the critic found different things, as designed.** The one
pair the metric flagged fleet-wide, the board judged realistic. The pair
the board rated most damning, the metric could not see. Neither subsumes
the other. This is the measured case for building both.

**The board's central claim is one no proxy could reach.** Its thesis,
arrived at independently: documents a real firm would template *don't*
repeat, while documents no template governs repeat *exactly* — and both
failures track authoring batch boundaries rather than author, client, or
year. A same-genre similarity metric can only flag prose that repeats. It
is structurally blind to prose that *fails* to repeat where house style
requires it.

**Reading the metric.** A flagged pair is not a defect and an unflagged
corpus is not clean. `SIMILAR_JACCARD = 0.15` is a reading-list threshold,
chosen to surface the known positive without noise on a 17-doc org. It has
no meaning as a quality bar and must never become a validator rule.

## Limits, recorded

- **One org, one model, one run.** Calibrated on `fernhollow-partners`
  only. A different org, model, or effort is uncalibrated territory.
- **The ACL half of `graph_acl_naturalness` was untestable here.**
  fernhollow's posture was `open`, so all five internal people got
  byte-identical grants and the dimension carried no ACL signal
  (`rf:graph-5`). Calibrating it needs a partitioning posture.
- **No negative control, and a false positive has since been measured.**
  Nothing here established what the board reports on a corpus with no
  defects, so its false-positive rate is unmeasured. It is not zero: during
  the MODEL-AB Round 2 A/B (2026-07-17, `docs/MODEL-AB.md`) a reviewer
  asserted that two corpora rendered byte-identical prose when all 22
  documents differed, and attributed one arm's sentence to the other. One
  instance is not a rate, but it is no longer a hypothetical, and it is why
  every board finding quoted in the README is re-verified against a ledger
  before publication. BACKLOG `board-negative-control` tracks the real fix. The
  reviewers did decline findings explicitly and one recorded an organic
  pattern as a strength "so it doesn't get fixed" (`rf:graph-4`), which is
  evidence of restraint but not a measurement of it.
- **The board is not reproducible.** It is a model pass. Findings are
  ingested and stored precisely because they cannot be regenerated
  byte-for-byte the way `evals/` can.

## Discrepancies found while calibrating

The Jaccard figures identified during spec drafting (0.228 for
d:0001/d:0008, 0.037 for d:0001/d:0016) do **not** reproduce under the
shipped metric, which reports 0.2524 and 0.0459. The gap is tokenization:
the shipped metric strips `{{fact:...}}` placeholders before shingling
(they are scaffolding the model never wrote) and folds case. No variant
tried reproduces the original decimals.

Every structural claim the spec rested on those numbers survives: d:0001/
d:0008 is the top same-genre pair fleet-wide by a wide margin, and
d:0001/d:0016 sits near the noise floor and is missed. The decimals were
never the point; they are recorded here so nobody re-derives them and
concludes the metric changed.

Same story for corpus length: the spec's "mean 226 words across 81
authored docs" measures 81 docs (exact) at **mean 236** under the shipped
counter, which reads a placeholder as the one word it renders to. The
finding is unaffected: the corpus is thin against briefs of 130-350, and
real engagement letters run 800-1500.

---

## The structural axis, calibrated against the M17 board (2026-08-02)

A second calibration, in the same register and held to the same rule: an
instrument is only worth reading if you know what it misses.

**What is being calibrated.** `orgsmith/review/structure.py` (M17b) scores
same-genre pairs on `shape` (the block skeleton) and `openers` (the first
content word of each prose unit). Neither token carries an authored
sentence, so a thorough paraphrase moves neither. It exists because the
4-gram metric could not see the defect the M17 board called a blocker.

**Against what.** The frozen `northgate-staffing` exemplar as committed at
v2.2.0, and the six `cross_document_voice` findings its board returned. 54
authored documents, 161 same-genre pairs among them. Read-only: no fixture
moved to produce these numbers, and the doc-id anchors are legitimate here
precisely because the exemplar is frozen.

**Corpus context.** Median 4-gram Jaccard is **0.0031** and the maximum is
0.2409: the lexical axis is compressed against its floor with almost no
dynamic range left. The structural mean runs median **0.4688**, max 0.8334
(shape median 0.6667, openers median 0.3158).

### Where the board's findings rank

Ranked by the mean of the two axes, out of 161 pairs. "Flagged today" is
whether the shipped lexical threshold (`SIMILAR_JACCARD = 0.15`) fires.

| finding | pair(s) | structural rank | jaccard | jaccard rank | flagged today |
| --- | --- | ---: | ---: | ---: | --- |
| **`rf:voice-1`** (blocker) | d:0021 / d:0039 | **5** | 0.0620 | 5 | no |
| `rf:voice-5` (major) | d:0011 / d:0029 | **2** | 0.2409 | 1 | yes |
| `rf:voice-6` (minor) | 15 pairs over 6 onboarding records | **3, 6, 8, 9, 10**, then 14-104 | 0.0023-0.0585 | 6-94 | no |
| `rf:voice-2` (major) | 15 pairs over 6 engagement emails | **1**, then 15-154 | 0.0000-0.0743 | 3-138 | no |
| `rf:voice-4` (major) | d:0034 / d:0046 | **78** | 0.0248 | 21 | no |
| `rf:voice-3` (major) | none (corpus-wide) | out of reach | - | - | no |
| `rf:voice-7` (note) | none (corpus-wide) | out of reach | - | - | no |

### What it catches

**The blocker, which the lexical metric does not flag.** `rf:voice-1` is
two kickoff memos two years apart by two authors, "the same memo
re-skinned." It lands at structural rank 5 of 161 (shape 0.8485). Its
Jaccard is 0.0620, well under the 0.15 flag, so the shipped report never
surfaced it. This is the pair the axis was built for.

**Five of `rf:voice-6`'s fifteen pairs in the top ten**, best at rank 3
(d:0017/d:0047, shape 1.0000 — an identical skeleton). The board called
these six onboarding records "the same beats in the same order," which is a
shape claim, and the axis reads it as one.

**`rf:voice-2`'s strongest pair at rank 1** fleet-wide (d:0031/d:0040,
shape 1.0000).

### What it misses, and why

**`rf:voice-4` at rank 78 of 161 — a clean miss.** Two status reports
sharing "the same risk taxonomy in the same order with clause-level
phrasing in common." Its shape is 0.4000, below the corpus median, because
the two reports differ in block count and paragraph length while agreeing
on the *content* of their sections. Openers catch it partly (0.5517) and
shape drags the mean down. The lexical axis misses it too (rank 21,
unflagged), so this defect is currently invisible to both proxies and was
found only by the board.

**`rf:voice-2` as a family.** The axis surfaces its strongest pair at rank
1 but scatters the other fourteen from 15 to 154. A six-document family
sharing a script is not a property of any one pair, and a pairwise
instrument cannot express it. Reading the top of the list will find the
family's tip, never its extent.

**`rf:voice-3` is out of reach by construction, and no keyless proxy will
reach it.** The finding is a single rhetorical move — nominating one gating
item everything else waits on — recurring in fourteen documents across
eight authors, five genres, and 2015-2023, paraphrased each time. It is not
a pair (the docs are cross-genre), not a shape (it is one sentence inside
documents with different skeletons), and not an n-gram (that is what
"paraphrased" means). Recognizing it needs semantics. **Do not read a clean
structural table as evidence that this class of defect is absent.** It is
the class the board exists for, and M17b's outline work does not address it
either.

**The two axes disagree, and that is the argument for keeping both.**
`rf:voice-6`'s best lexical pair (d:0027/d:0049, Jaccard 0.0585, rank 6) is
structural rank 104; its best structural pair (d:0017/d:0047, rank 3) is
lexical rank 7. Neither ordering subsumes the other, which is why the
report prints both columns side by side rather than replacing one.

### Limits, recorded

- **One org, one board run, one measurement.** Calibrated against
  `northgate-staffing` only. Every number above is a measurement of that
  corpus on 2026-08-02, not a property of the instrument.
- **The board is the yardstick, and it is itself uncalibrated on this org.**
  Its false-positive rate is unmeasured (BACKLOG `board-negative-control`),
  so "the axis missed `rf:voice-4`" assumes `rf:voice-4` is real. It was
  read and found plausible; it was not independently verified.
- **No threshold is proposed and none should be inferred.** The report
  prints a fixed number of rows precisely because there is no validated cut
  point. Nothing here may become a validator rule or a test assert: a high
  shape score is often correct, since two status reports from one firm
  *should* share a skeleton.
- **Ranks will move.** They are computed over the pairs of one frozen
  corpus. Regenerating the exemplar invalidates every rank in this section
  while leaving the caught/missed structure of the finding intact.
- **Prediction versus measurement.** The M17b plan predicted ranks 1/4/5/6
  for four named pairs, from a prototype with different bucket edges and a
  different stoplist, and it paired `rf:voice-4` with d:0016 rather than the
  board's d:0046. The shipped instrument measures 2/5/3/78 against the
  board's actual doc sets. The plan's numbers are superseded; they are named
  here so nobody re-derives them and concludes the code changed.
