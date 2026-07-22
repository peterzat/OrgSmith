# Generation report: dev-mini

Derived artifact: re-emit with `python -m orgsmith report dev-mini`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

22 documents planned; 17 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-4-8[1m] | max |
| wo:author:0002 | claude-opus-4-8[1m] | max |
| wo:author:0003 | claude-opus-4-8[1m] | max |
| wo:author:0004 | claude-opus-4-8[1m] | max |
| wo:foundation:0001 | claude-opus-4-8[1m] | max |

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 23 rules run, 0 error(s), 0 warning(s); skipped by charter knob: CAL-01, NOISE-01, AFF-01, AFF-02, EML-01, EML-02, EML-03, DL-01, STY-01, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score dev-mini --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

17 authored documents, 12196 words, mean 717.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0002 | d:0008 | engagement_letter | 0.355 |
| d:0008 | d:0015 | engagement_letter | 0.3103 |
| d:0002 | d:0015 | engagement_letter | 0.2808 |

### Fee coverage

3 documented engagement(s), fees totalling $292,000, against $5,778,000 of lifetime revenue.

Documented fees are 5.1% of lifetime revenue.

The recipe does not declare the engagement book a sample, so the overview may present it as the firm's whole client list. A large fee/revenue gap here reads as the contradiction the board found (engagement-ledger-reads-as-whole-book).

### Cross-document voice

Pre-registered voice patterns over 17 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 2 | 2 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 4 | 4 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 49 | 17 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 4 | 4 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 3 | 3 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:cynthia.ball | 2 | 0.0067 (0.0067-0.0067) | 0.0086 | 0.0067 |
| p:daniel.jones | 6 | 0.0738 (0.0000-0.3550) | 0.0028 | 0.1671 |
| p:jennifer.fletcher | 4 | 0.0092 (0.0000-0.0477) | 0.0084 | 0.0030 |
| p:robert.miller | 3 | 0.0081 (0.0009-0.0221) | 0.0098 | 0.0015 |
| p:susan.wiley | 2 | 0.0475 (0.0475-0.0475) | 0.0041 | 0.0475 |

### Review board

No board findings ingested. Run `/forge-review dev-mini` to dispatch the review board; the metrics above stand on their own without it.
