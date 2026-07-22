# Generation report: calderwood-partners

Derived artifact: re-emit with `python -m orgsmith report calderwood-partners`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

218 documents planned; 168 carry authored prose.

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
| wo:author:0010 | claude-opus-4-8[1m] | xhigh |
| wo:author:0011 | claude-opus-4-8[1m] | xhigh |
| wo:author:0012 | claude-opus-4-8[1m] | xhigh |
| wo:author:0013 | claude-opus-4-8[1m] | xhigh |
| wo:author:0014 | claude-opus-4-8[1m] | xhigh |
| wo:author:0015 | claude-opus-4-8[1m] | xhigh |
| wo:author:0016 | claude-opus-4-8[1m] | xhigh |
| wo:author:0017 | claude-opus-4-8[1m] | xhigh |
| wo:author:0018 | claude-opus-4-8[1m] | xhigh |
| wo:author:0019 | claude-opus-4-8[1m] | xhigh |
| wo:author:0020 | claude-opus-4-8[1m] | xhigh |
| wo:author:0021 | claude-opus-4-8[1m] | xhigh |
| wo:author:0022 | claude-opus-4-8[1m] | xhigh |
| wo:author:0023 | claude-opus-4-8[1m] | xhigh |
| wo:author:0024 | claude-opus-4-8[1m] | xhigh |
| wo:author:0025 | claude-opus-4-8[1m] | xhigh |
| wo:author:0026 | claude-opus-4-8[1m] | xhigh |
| wo:author:0027 | claude-opus-4-8[1m] | xhigh |
| wo:author:0028 | claude-opus-4-8[1m] | xhigh |
| wo:author:0029 | claude-opus-4-8[1m] | xhigh |
| wo:author:0030 | claude-opus-4-8[1m] | xhigh |
| wo:author:0031 | claude-opus-4-8[1m] | xhigh |
| wo:author:0032 | claude-opus-4-8[1m] | xhigh |
| wo:author:0033 | claude-opus-4-8[1m] | xhigh |
| wo:author:0034 | claude-opus-4-8[1m] | xhigh |
| wo:author:0035 | claude-opus-4-8[1m] | xhigh |
| wo:author:0036 | claude-opus-4-8[1m] | xhigh |
| wo:author:0037 | claude-opus-4-8[1m] | xhigh |
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 28 rules run, 0 error(s), 0 warning(s); skipped by charter knob: AFF-01, AFF-02, EML-02, EML-03, DL-01, STY-01, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score calderwood-partners --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

168 authored documents, 98907 words, mean 589.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0017 | onboarding_record | 300 | 450 | 0.67 |
| d:0008 | engagement_email | 168 | 250 | 0.67 |
| d:0009 | engagement_email | 171 | 250 | 0.68 |
| d:0020 | briefing_deck | 281 | 400 | 0.70 |
| d:0005 | onboarding_record | 319 | 450 | 0.71 |
| d:0004 | onboarding_record | 321 | 450 | 0.71 |
| d:0060 | briefing_deck | 288 | 400 | 0.72 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0050 | d:0091 | engagement_letter | 0.3495 |
| d:0023 | d:0120 | engagement_letter | 0.298 |
| d:0120 | d:0137 | engagement_letter | 0.2763 |
| d:0016 | d:0026 | engagement_letter | 0.263 |
| d:0102 | d:0110 | engagement_letter | 0.2609 |
| d:0157 | d:0171 | engagement_letter | 0.2584 |
| d:0120 | d:0127 | engagement_letter | 0.2491 |
| d:0080 | d:0169 | onboarding_record | 0.2489 |
| d:0070 | d:0119 | company_overview | 0.2427 |
| d:0050 | d:0075 | engagement_letter | 0.2409 |
| d:0075 | d:0091 | engagement_letter | 0.2258 |
| d:0023 | d:0137 | engagement_letter | 0.223 |
| d:0006 | d:0050 | engagement_letter | 0.2043 |
| d:0127 | d:0137 | engagement_letter | 0.1987 |
| d:0023 | d:0127 | engagement_letter | 0.1973 |
| d:0016 | d:0135 | engagement_letter | 0.1909 |
| d:0137 | d:0141 | engagement_letter | 0.1869 |
| d:0016 | d:0023 | engagement_letter | 0.179 |
| d:0026 | d:0135 | engagement_letter | 0.1742 |
| d:0122 | d:0129 | engagement_email | 0.1738 |
| d:0010 | d:0070 | company_overview | 0.1679 |
| d:0006 | d:0159 | engagement_letter | 0.1607 |
| d:0120 | d:0141 | engagement_letter | 0.1562 |
| d:0006 | d:0091 | engagement_letter | 0.1561 |
| d:0026 | d:0120 | engagement_letter | 0.1539 |
| d:0023 | d:0026 | engagement_letter | 0.1528 |
| d:0070 | d:0166 | company_overview | 0.1512 |

### Fee coverage

22 documented engagement(s), fees totalling $1,545,000, against $68,226,000 of lifetime revenue.

Documented fees are 2.3% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 168 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 9 | 9 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 228 | 112 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 2 | 2 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 2 | 2 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 5 | 5 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:brenda.clayton | 5 | 0.0034 (0.0000-0.0219) | 0.0013 | 0.0004 |
| p:brenda.rodriguez | 13 | 0.0039 (0.0000-0.0314) | 0.0012 | 0.0114 |
| p:cynthia.hart | 3 | 0.0013 (0.0011-0.0015) | 0.0024 | 0.0020 |
| p:daniel.cisneros | 3 | 0.0074 (0.0055-0.0100) | 0.0021 | 0.0121 |
| p:daniel.leach | 7 | 0.0075 (0.0000-0.0420) | 0.0012 | 0.0120 |
| p:deborah.allen | 5 | 0.0022 (0.0000-0.0076) | 0.0012 | 0.0055 |
| p:deborah.gordon | 9 | 0.0040 (0.0000-0.0591) | 0.0012 | 0.0069 |
| p:deborah.jimenez | 7 | 0.0037 (0.0000-0.0295) | 0.0011 | 0.0122 |
| p:james.green | 3 | 0.0010 (0.0000-0.0029) | 0.0013 | 0.0025 |
| p:jason.torres | 13 | 0.0026 (0.0000-0.0277) | 0.0014 | 0.0061 |
| p:john.vasquez | 3 | 0.0028 (0.0013-0.0043) | 0.0012 | 0.0034 |
| p:joseph.reed | 3 | 0.0095 (0.0024-0.0192) | 0.0013 | 0.0171 |
| p:julie.parks | 5 | 0.0021 (0.0000-0.0081) | 0.0011 | 0.0053 |
| p:julie.ramsey | 46 | 0.0183 (0.0000-0.3495) | 0.0004 | 0.1172 |
| p:julie.vasquez | 3 | 0.0025 (0.0012-0.0037) | 0.0015 | 0.0023 |
| p:mary.parker | 7 | 0.0043 (0.0000-0.0331) | 0.0014 | 0.0028 |
| p:matthew.parrish | 7 | 0.0036 (0.0000-0.0362) | 0.0011 | 0.0033 |
| p:melissa.casey | 8 | 0.0026 (0.0000-0.0218) | 0.0017 | 0.0108 |
| p:michael.walker | 6 | 0.0016 (0.0000-0.0065) | 0.0008 | 0.0042 |
| p:nicole.griffin | 5 | 0.0057 (0.0000-0.0291) | 0.0016 | 0.0023 |
| p:pamela.miller | 3 | 0.0021 (0.0012-0.0029) | 0.0014 | 0.0025 |
| p:steven.hunt | 4 | 0.0074 (0.0034-0.0159) | 0.0014 | 0.0059 |

### Review board

No board findings ingested. Run `/forge-review calderwood-partners` to dispatch the review board; the metrics above stand on their own without it.
