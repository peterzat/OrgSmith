# Generation report: brackenridge-civil

Derived artifact: re-emit with `python -m orgsmith report brackenridge-civil`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

40 documents planned; 31 carry authored prose.

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
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

Model cost: 31 of 40 documents were authored by a model, across 9 work order(s).

The other 9 cost zero model tokens: 9 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 26 rules run, 0 error(s), 0 warning(s); skipped by charter knob: CAL-01, NOISE-01, AFF-01, AFF-02, EML-01, EML-02, EML-03, DL-01, STY-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score brackenridge-civil --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

31 authored documents, 21662 words, mean 699.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.1095).

### Fee coverage

5 documented engagement(s), fees totalling $399,000, against $11,376,000 of lifetime revenue.

Documented fees are 3.5% of lifetime revenue.

The recipe does not declare the engagement book a sample, so the overview may present it as the firm's whole client list. A large fee/revenue gap here reads as the contradiction the board found (engagement-ledger-reads-as-whole-book).

### Cross-document voice

Pre-registered voice patterns over 31 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 1 | 1 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 3 | 3 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 12 | 10 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 60 | 28 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 7 | 5 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 7 | 7 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:charles.olson | 3 | 0.0136 (0.0108-0.0186) | 0.0020 | 0.0186 |
| p:jason.jordan | 5 | 0.0141 (0.0016-0.0786) | 0.0036 | 0.0085 |
| p:jeffrey.perez | 2 | 0.0110 (0.0110-0.0110) | 0.0027 | 0.0110 |
| p:kimberly.branch | 1 | - | 0.0050 | - |
| p:linda.george | 3 | 0.0038 (0.0007-0.0083) | 0.0031 | 0.0014 |
| p:linda.nguyen | 4 | 0.0122 (0.0014-0.0316) | 0.0026 | 0.0147 |
| p:mark.todd | 12 | 0.0146 (0.0000-0.1095) | 0.0018 | 0.0607 |
| p:pamela.warren | 1 | - | 0.0033 | - |

### Review board

No board findings ingested. Run `/forge-review brackenridge-civil` to dispatch the review board; the metrics above stand on their own without it.
