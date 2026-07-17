# Board calibration

A critic is only worth reading if you know what it catches. This records
the board's first run against two labeled positives that were identified
by hand, before the board existed, in `fernhollow-partners`.

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
