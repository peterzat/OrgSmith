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

Validator: 29 rules run, 0 error(s), 0 warning(s); skipped by charter knob: NOISE-01, MENT-03, AFF-01, AFF-02, EML-01, EML-02, EML-03, DL-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score brackenridge-civil --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

31 authored documents, 19863 words, mean 641.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0008 | briefing_deck | 242 | 400 | 0.60 |
| d:0027 | onboarding_record | 294 | 450 | 0.65 |
| d:0016 | onboarding_record | 307 | 450 | 0.68 |
| d:0014 | onboarding_record | 317 | 450 | 0.70 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0021 | d:0040 | company_overview | 0.4533 |
| d:0005 | d:0036 | engagement_letter | 0.3542 |
| d:0007 | d:0040 | company_overview | 0.2482 |
| d:0018 | d:0031 | engagement_letter | 0.2156 |
| d:0007 | d:0021 | company_overview | 0.196 |
| d:0006 | d:0037 | kickoff_memo | 0.1628 |

### Structural similarity

The 10 strongest of 60 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0018 | d:0031 | engagement_letter | 0.9643 | 0.7037 | 0.2156 |
| d:0009 | d:0012 | meeting_minutes | 0.88 | 0.7407 | 0.0522 |
| d:0005 | d:0036 | engagement_letter | 0.8364 | 0.717 | 0.3542 |
| d:0018 | d:0036 | engagement_letter | 0.8519 | 0.6154 | 0.0255 |
| d:0005 | d:0018 | engagement_letter | 0.8772 | 0.5455 | 0.0259 |
| d:0021 | d:0040 | company_overview | 0.9167 | 0.5 | 0.4533 |
| d:0033 | d:0038 | meeting_minutes | 0.9231 | 0.4828 | 0.011 |
| d:0012 | d:0028 | meeting_minutes | 0.96 | 0.4444 | 0.0114 |
| d:0014 | d:0027 | onboarding_record | 1.0 | 0.4 | 0.0302 |
| d:0031 | d:0036 | engagement_letter | 0.8889 | 0.5 | 0.025 |

60 pairs were scored; the artifact keeps the strongest 50 and this table shows the top 10. The full ranking is recomputable from committed DocIR (`orgsmith.review.structure.compute_pairs`); it is truncated here rather than dropped silently.

### Fee coverage

5 documented engagement(s), fees totalling $399,000, against $11,376,000 of lifetime revenue.

Documented fees are 3.5% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 31 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 2 | 2 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 32 | 19 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 1 | 1 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 1 | 1 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:charles.olson | 3 | 0.0143 (0.0068-0.0212) | 0.0035 | 0.0131 |
| p:jason.jordan | 5 | 0.0087 (0.0008-0.0522) | 0.0049 | 0.0047 |
| p:jeffrey.perez | 2 | 0.0216 (0.0216-0.0216) | 0.0044 | 0.0216 |
| p:kimberly.branch | 1 | - | 0.0040 | - |
| p:linda.george | 3 | 0.0051 (0.0018-0.0113) | 0.0043 | 0.0021 |
| p:linda.nguyen | 4 | 0.0121 (0.0059-0.0218) | 0.0040 | 0.0138 |
| p:mark.todd | 12 | 0.0318 (0.0000-0.4533) | 0.0018 | 0.1997 |
| p:pamela.warren | 1 | - | 0.0051 | - |

### Review board

8 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:cross-voice-1 | cross_document_voice | major | d:0006, d:0019, d:0026, d:0032, d:0037 | The five kickoff memos are attributed to five different staff yet collapse into two verbatim molds, so one generator's hand shows through instead of five distinct writers. |
| rf:cross-voice-2 | cross_document_voice | major | d:0010, d:0023, d:0029, d:0034 | Status reports by four different authors reuse the same client-facing idioms word for word, so the reports read as one writer across all engagements. |
| rf:docplaus-1 | document_plausibility | major | d:0021, d:0040 | The firm overviews describe past engagements with the wrong service type, contradicting every other document in those same engagement folders. |
| rf:graph-acl-1 | graph_acl_naturalness | major | d:0005, d:0006, d:0009, d:0012, d:0013 | The Esparza-Lamb site-grading engagement is run and client-fronted entirely by two Design Technicians with no engineer on the team, the only one of the five engagements staffed that way, though both firm engineers were employed when it ran. |
| rf:narrative-1 | narrative_consistency | major | d:0040, d:0021, d:0018, d:0025, d:0036 | The firm-overview brochures describe three named past engagements as work in disciplines the engagements were not, contradicting each engagement's own letter and file. |
| rf:org-realism-1 | org_realism | major | d:0009, d:0012, d:0010, d:0013 | The Esparza-Lamb engagement's client design meetings and progress reports are conducted entirely by Design Technicians with no engineer present, unlike every later engagement, which is implausible for a firm whose drawings only leave under the Principal Engineer's seal. |
| rf:cross-voice-3 | cross_document_voice | minor | d:0009, d:0028 | Meeting minutes by two different authors close on the same templated sentence, another shared idiom that betrays a single hand. |
| rf:narrative-2 | narrative_consistency | minor | d:0013, d:0005 | The Esparza-Lamb final status report claims a delivered scope well beyond the grading-only scope its executed engagement letter set, while insisting scope never changed. |
