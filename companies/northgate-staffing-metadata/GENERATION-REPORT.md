# Generation report: northgate-staffing

Derived artifact: re-emit with `python -m orgsmith report northgate-staffing`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

66 documents planned; 44 carry authored prose.

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

Model cost: 44 of 66 documents were authored by a model, across 10 work order(s).

The other 22 cost zero model tokens: 9 static (rendered from the deterministic ledgers) and 13 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 27 rules run, 0 error(s), 0 warning(s); skipped by charter knob: AFF-01, AFF-02, EML-02, EML-03, DL-01, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score northgate-staffing --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

44 authored documents, 25962 words, mean 590.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0025 | onboarding_record | 329 | 450 | 0.73 |
| d:0004 | briefing_deck | 293 | 400 | 0.73 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0002 | d:0035 | engagement_letter | 0.3248 |
| d:0002 | d:0027 | engagement_letter | 0.2979 |
| d:0027 | d:0035 | engagement_letter | 0.2786 |
| d:0008 | d:0031 | status_report | 0.2424 |
| d:0035 | d:0048 | engagement_letter | 0.1885 |

### Fee coverage

6 documented engagement(s), fees totalling $500,500, against $20,712,000 of lifetime revenue.

Documented fees are 2.4% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 44 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 2 | 2 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 75 | 34 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:david.weiss | 3 | 0.0130 (0.0039-0.0253) | 0.0009 | 0.0079 |
| p:james.grant | 5 | 0.0076 (0.0007-0.0159) | 0.0063 | 0.0129 |
| p:jason.bell | 3 | 0.0068 (0.0047-0.0083) | 0.0025 | 0.0096 |
| p:jeffrey.patterson | 4 | 0.0087 (0.0046-0.0148) | 0.0029 | 0.0126 |
| p:john.chang | 2 | 0.0431 (0.0431-0.0431) | 0.0020 | 0.0431 |
| p:kelly.chavez | 15 | 0.0212 (0.0000-0.3248) | 0.0016 | 0.1002 |
| p:nicole.donovan | 5 | 0.0074 (0.0000-0.0434) | 0.0045 | 0.0033 |
| p:sandra.fuentes | 7 | 0.0059 (0.0000-0.0286) | 0.0050 | 0.0118 |

### Review board

No board findings ingested. Run `/forge-review northgate-staffing` to dispatch the review board; the metrics above stand on their own without it.
