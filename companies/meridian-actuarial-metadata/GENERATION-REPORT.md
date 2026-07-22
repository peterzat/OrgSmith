# Generation report: meridian-actuarial

Derived artifact: re-emit with `python -m orgsmith report meridian-actuarial`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

49 documents planned; 40 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-4-8[1m] | xhigh |
| wo:author:0002 | claude-opus-4-8[1m] | xhigh |
| wo:author:0003 | claude-opus-4-8[1m] | xhigh |
| wo:author:0004 | claude-opus-4-8[1m] | xhigh |
| wo:author:0005 | claude-opus-4-8[1m] | xhigh |
| wo:author:0006 | claude-opus-4-8[1m] | xhigh |
| wo:author:0007 | claude-opus-4-8[1m] | xhigh |
| wo:author:0008 | claude-opus-4-8[1m] | xhigh |
| wo:author:0009 | claude-opus-4-8[1m] | xhigh |
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

Model cost: 40 of 49 documents were authored by a model, across 10 work order(s).

The other 9 cost zero model tokens: 9 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 24 rules run, 0 error(s), 0 warning(s); skipped by charter knob: CAL-01, NOISE-01, AFF-01, AFF-02, EML-02, EML-03, DL-01, STY-01, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score meridian-actuarial --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

40 authored documents, 26993 words, mean 675.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.1262).

### Fee coverage

6 documented engagement(s), fees totalling $366,500, against $23,004,000 of lifetime revenue.

Documented fees are 1.6% of lifetime revenue.

The recipe does not declare the engagement book a sample, so the overview may present it as the firm's whole client list. A large fee/revenue gap here reads as the contradiction the board found (engagement-ledger-reads-as-whole-book).

### Cross-document voice

Pre-registered voice patterns over 40 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 1 | 1 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 5 | 4 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 22 | 14 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 88 | 33 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 1 | 1 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 7 | 6 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 8 | 8 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:david.sherman | 6 | 0.0041 (0.0000-0.0287) | 0.0029 | 0.0052 |
| p:jeffrey.ochoa | 3 | 0.0037 (0.0023-0.0060) | 0.0034 | 0.0033 |
| p:jennifer.vasquez | 6 | 0.0068 (0.0000-0.0272) | 0.0024 | 0.0127 |
| p:karen.harris | 2 | 0.0056 (0.0056-0.0056) | 0.0019 | 0.0056 |
| p:megan.dudley | 5 | 0.0113 (0.0000-0.0356) | 0.0024 | 0.0255 |
| p:michelle.banks | 3 | 0.0063 (0.0000-0.0177) | 0.0027 | 0.0126 |
| p:robert.lawrence | 15 | 0.0120 (0.0000-0.1262) | 0.0014 | 0.0589 |

### Review board

No board findings ingested. Run `/forge-review meridian-actuarial` to dispatch the review board; the metrics above stand on their own without it.
