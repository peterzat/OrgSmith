# Generation report: verdant-health

Derived artifact: re-emit with `python -m orgsmith report verdant-health`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

31 documents planned; 25 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-4-8[1m] | xhigh |
| wo:author:0002 | claude-opus-4-8[1m] | xhigh |
| wo:author:0003 | claude-opus-4-8[1m] | xhigh |
| wo:author:0004 | claude-opus-4-8[1m] | xhigh |
| wo:author:0005 | claude-opus-4-8[1m] | xhigh |
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

Model cost: 25 of 31 documents were authored by a model, across 6 work order(s).

The other 6 cost zero model tokens: 6 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 27 rules run, 0 error(s), 0 warning(s); skipped by charter knob: CAL-01, NOISE-01, EML-01, EML-02, EML-03, DL-01, STY-01, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score verdant-health --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

25 authored documents, 18191 words, mean 728.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.0749).

### Fee coverage

4 documented engagement(s), fees totalling $275,000, against $9,534,000 of lifetime revenue.

Documented fees are 2.9% of lifetime revenue.

The recipe does not declare the engagement book a sample, so the overview may present it as the firm's whole client list. A large fee/revenue gap here reads as the contradiction the board found (engagement-ledger-reads-as-whole-book).

### Cross-document voice

Pre-registered voice patterns over 25 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 1 | 1 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 16 | 11 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 59 | 22 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 9 | 8 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 6 | 6 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:barbara.freeman | 2 | 0.0088 (0.0088-0.0088) | 0.0027 | 0.0088 |
| p:daniel.alvarado | 8 | 0.0061 (0.0000-0.0411) | 0.0031 | 0.0042 |
| p:laura.brown | 8 | 0.0137 (0.0000-0.0749) | 0.0017 | 0.0546 |
| p:patricia.moore | 3 | 0.0174 (0.0083-0.0242) | 0.0026 | 0.0194 |
| p:susan.clark | 4 | 0.0096 (0.0000-0.0496) | 0.0029 | 0.0004 |

### Review board

No board findings ingested. Run `/forge-review verdant-health` to dispatch the review board; the metrics above stand on their own without it.
