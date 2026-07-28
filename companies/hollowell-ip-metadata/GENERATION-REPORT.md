# Generation report: hollowell-ip

Derived artifact: re-emit with `python -m orgsmith report hollowell-ip`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

64 documents planned; 56 carry authored prose.

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
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

Model cost: 56 of 64 documents were authored by a model, across 12 work order(s).

The other 8 cost zero model tokens: 8 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 29 rules run, 0 error(s), 0 warning(s); skipped by charter knob: NOISE-01, AFF-01, AFF-02, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score hollowell-ip --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

56 authored documents, 26915 words, mean 481.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0020 | engagement_email | 101 | 250 | 0.40 |
| d:0019 | engagement_email | 105 | 250 | 0.42 |
| d:0018 | engagement_email | 109 | 250 | 0.44 |
| d:0008 | engagement_email | 115 | 250 | 0.46 |
| d:0059 | engagement_email | 131 | 250 | 0.52 |
| d:0057 | engagement_email | 141 | 250 | 0.56 |
| d:0058 | engagement_email | 151 | 250 | 0.60 |
| d:0048 | engagement_email | 153 | 250 | 0.61 |
| d:0046 | engagement_email | 175 | 250 | 0.70 |
| d:0009 | briefing_deck | 295 | 400 | 0.74 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0004 | d:0030 | engagement_letter | 0.3474 |
| d:0006 | d:0032 | engagement_email | 0.3064 |
| d:0015 | d:0054 | engagement_letter | 0.2346 |
| d:0015 | d:0043 | engagement_letter | 0.1888 |

### Fee coverage

5 documented engagement(s), fees totalling $362,000, against $17,141,000 of lifetime revenue.

Documented fees are 2.1% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 56 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 1 | 1 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 7 | 6 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 86 | 30 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:ashley.williams | 5 | 0.0202 (0.0013-0.0599) | 0.0025 | 0.0337 |
| p:david.chang | 5 | 0.0037 (0.0000-0.0165) | 0.0025 | 0.0042 |
| p:heather.munoz | 10 | 0.0038 (0.0000-0.0619) | 0.0025 | 0.0049 |
| p:joseph.walker | 3 | 0.0105 (0.0000-0.0316) | 0.0011 | 0.0285 |
| p:kelly.snyder | 8 | 0.0034 (0.0000-0.0354) | 0.0022 | 0.0031 |
| p:mary.bradley | 14 | 0.0217 (0.0000-0.3474) | 0.0009 | 0.1941 |
| p:matthew.parrish | 1 | - | 0.0000 | - |
| p:richard.henderson | 10 | 0.0087 (0.0000-0.0790) | 0.0022 | 0.0319 |

### Review board

7 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:cross-voice-email-openers | cross_document_voice | major | d:0006, d:0017, d:0032, d:0045, d:0056 | The first client email of all five engagements opens with the same 'I am opening this thread so ... stay in one place' sentence, though each was written by a different person. |
| rf:cross-voice-kickoff-scope | cross_document_voice | major | d:0016, d:0044, d:0055 | The three opinion-type kickoff memos, each by a different agent, reach for the same verbatim scope-scaffolding sentences rather than expressing the shared method in independent words. |
| rf:cross-voice-minutes | cross_document_voice | major | d:0010, d:0061 | Meeting minutes taken by two different people six years apart share verbatim narrative sentences that are prose, not form fields, so the match reads as one generator rather than two minute-takers. |
| rf:graph-acl-1 | graph_acl_naturalness | major | d:0044 | The Jackson Inc trademark-clearance kickoff assigns core searching to Matthew Parrish, who is not on the matter team and has no access to the matter folder. |
| rf:narrative-consistency-1 | narrative_consistency | major | d:0004, d:0011, d:0013 | The Odonnell portfolio-review engagement carves office-action work out of scope in the letter, kickoff, and deck, then the status report and closing minutes report drafting and FILING office-action responses (and an examiner interview) as completed engagement work while still claiming to be within scope. |
| rf:doc-plausibility-list-marker | document_plausibility | minor | d:0060 | A client email's two-item request list renders with both a dash bullet and an author-typed number on each line, a double list marker no genuine email carries. |
| rf:doc-plausibility-mail-salutation | document_plausibility | minor | d:0002, d:0052 | Both firm-wide internal notices are sent to the all-staff distribution list yet open with the salutation 'Sharon,' and are written entirely as one-to-one notes to the docketing manager, so a broadcast reads as a private message. |
