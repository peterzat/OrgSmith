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

Validator: 30 rules run, 0 error(s), 0 warning(s); skipped by charter knob: NOISE-01, MENT-03, EML-01, EML-02, EML-03, DL-01, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score verdant-health --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

25 authored documents, 17431 words, mean 697.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0019 | d:0026 | engagement_letter | 0.246 |

### Structural similarity

The 10 strongest of 42 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0019 | d:0026 | engagement_letter | 0.9259 | 0.8462 | 0.246 |
| d:0021 | d:0023 | meeting_minutes | 0.9286 | 0.75 | 0.0515 |
| d:0006 | d:0009 | meeting_minutes | 0.8696 | 0.5926 | 0.0354 |
| d:0028 | d:0030 | meeting_minutes | 0.8667 | 0.5625 | 0.0515 |
| d:0002 | d:0010 | engagement_letter | 0.898 | 0.5106 | 0.0503 |
| d:0022 | d:0029 | status_report | 0.8571 | 0.4918 | 0.126 |
| d:0002 | d:0026 | engagement_letter | 0.7547 | 0.549 | 0.0273 |
| d:0023 | d:0030 | meeting_minutes | 0.8966 | 0.375 | 0.1046 |
| d:0002 | d:0019 | engagement_letter | 0.717 | 0.5098 | 0.0293 |
| d:0010 | d:0019 | engagement_letter | 0.8 | 0.4167 | 0.0169 |

### Fee coverage

4 documented engagement(s), fees totalling $275,000, against $9,534,000 of lifetime revenue.

Documented fees are 2.9% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 25 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 3 | 3 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 72 | 23 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 1 | 1 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:barbara.freeman | 2 | 0.0197 (0.0197-0.0197) | 0.0072 | 0.0197 |
| p:daniel.alvarado | 8 | 0.0131 (0.0000-0.1046) | 0.0033 | 0.0015 |
| p:laura.brown | 8 | 0.0184 (0.0000-0.2460) | 0.0016 | 0.0306 |
| p:patricia.moore | 3 | 0.0213 (0.0163-0.0258) | 0.0033 | 0.0209 |
| p:susan.clark | 4 | 0.0097 (0.0000-0.0354) | 0.0055 | 0.0015 |

### Review board

8 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:cross-voice-1 | cross_document_voice | major | d:0003, d:0020, d:0027 | The kickoff memos are one template worn by different authors: Barbara Freeman's (d:0020) and Susan Clark's (d:0027) are near-verbatim despite being written by different people for different engagements a year apart, which reads as one generator rather than two colleagues. |
| rf:cross-voice-2 | cross_document_voice | major | d:0022, d:0029 | The two 2023/2024 status reports, authored by different people (Barbara Freeman on d:0022, Susan Clark on d:0029), are the same document section for section, so the promised author differentiation collapses into a shared skeleton. |
| rf:doc-plausibility-1 | document_plausibility | minor | d:0027 | The Sullivan kickoff memo attributes the scanned consents to 'the health system's contracting office,' an entity never introduced, even though the client Sullivan, Hall and Kelly is the only organization in scope and is referred to as 'their' in the same sentence. |
| rf:org-realism-1 | org_realism | minor | d:0002, d:0010, d:0011 | The firm's named physician-compensation and fair-market-value specialist is absent from the same client's dedicated Physician Compensation Review, which is led instead by the service-line economics consultant. |
| rf:org-realism-2 | org_realism | minor | d:0027, d:0029 | The Sullivan revenue-cycle kickoff blames scanned paperwork on 'the health system's contracting office,' an entity never introduced to the engagement, while the client status report attributes the identical documents to the client's own office. |
| rf:cross-voice-3 | cross_document_voice | note | d:0019, d:0026 | The one pair the similarity metric flagged, the Lopez and Sullivan engagement letters, reads as legitimate template reuse, not a defect, because both carry Laura Brown's signature; the real voice problem is the cross-author clones above, which synonym substitution hides from the 4-gram measure. |
| rf:doc-plausibility-2 | document_plausibility | note | d:0019, d:0026 | The one flagged same-genre pair (the Lopez and Sullivan engagement letters) reads as authentic template reuse by one signing partner, not as generator monotony; no defect claimed. |
| rf:narr-consistency-1 | narrative_consistency | note | d:0002, d:0009, d:0010, d:0011, d:0013 | Susan Clark, established as the firm's physician-compensation and fair-market-value specialist, does not appear on the one engagement that is a Physician Compensation Review; it is led instead by the service-line economist Daniel Alvarado with analyst Patricia Moore. |
