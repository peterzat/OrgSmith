# Generation report: meridian-actuarial

Derived artifact: re-emit with `python -m orgsmith report meridian-actuarial`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

72 documents planned; 63 carry authored prose.

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
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

Model cost: 63 of 72 documents were authored by a model, across 14 work order(s).

The other 9 cost zero model tokens: 9 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 29 rules run, 0 error(s), 0 warning(s); skipped by charter knob: NOISE-01, AFF-01, AFF-02, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score meridian-actuarial --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

63 authored documents, 28968 words, mean 460.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0007 | engagement_email | 83 | 250 | 0.33 |
| d:0006 | engagement_email | 105 | 250 | 0.42 |
| d:0005 | engagement_email | 106 | 250 | 0.42 |
| d:0004 | engagement_email | 118 | 250 | 0.47 |
| d:0035 | engagement_email | 144 | 250 | 0.58 |
| d:0033 | engagement_email | 153 | 250 | 0.61 |
| d:0032 | engagement_email | 157 | 250 | 0.63 |
| d:0034 | engagement_email | 160 | 250 | 0.64 |
| d:0021 | engagement_email | 178 | 250 | 0.71 |
| d:0043 | onboarding_record | 336 | 450 | 0.75 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0025 | d:0048 | status_report | 0.2981 |
| d:0030 | d:0064 | engagement_letter | 0.2463 |
| d:0002 | d:0030 | engagement_letter | 0.2339 |
| d:0030 | d:0044 | engagement_letter | 0.1657 |
| d:0002 | d:0064 | engagement_letter | 0.1528 |

### Fee coverage

6 documented engagement(s), fees totalling $366,500, against $23,004,000 of lifetime revenue.

Documented fees are 1.6% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 63 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 1 | 1 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 12 | 12 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 64 | 39 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 1 | 1 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:amanda.white | 1 | - | 0.0000 | - |
| p:david.sherman | 12 | 0.0031 (0.0000-0.0504) | 0.0020 | 0.0041 |
| p:jeffrey.ochoa | 6 | 0.0075 (0.0000-0.0833) | 0.0031 | 0.0044 |
| p:jennifer.johnson | 1 | - | 0.0001 | - |
| p:jennifer.vasquez | 8 | 0.0065 (0.0000-0.0588) | 0.0025 | 0.0074 |
| p:karen.harris | 5 | 0.0117 (0.0010-0.0427) | 0.0028 | 0.0138 |
| p:megan.dudley | 9 | 0.0046 (0.0000-0.0285) | 0.0021 | 0.0168 |
| p:michelle.banks | 6 | 0.0062 (0.0000-0.0368) | 0.0018 | 0.0034 |
| p:robert.lawrence | 15 | 0.0249 (0.0000-0.2463) | 0.0013 | 0.1383 |

### Review board

9 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:xvoice-1 | cross_document_voice | major | corpus | The firm's measurement/assumption/conclusion credo is narrated in near-identical triadic wording in almost every document, across all six genres and every author, including short engagement emails and meeting minutes where a real writer would not pause to recite the firm's writing philosophy. |
| rf:xvoice-2 | cross_document_voice | major | corpus | Beyond the credo, a small bank of signature aphorisms recurs verbatim across different authors and genres, including two distinct personas emitting identical sentences, reading as one writer's phrasebook rather than twelve independent hands. |
| rf:xvoice-3 | cross_document_voice | major | d:0012, d:0072 | The two midpoint status reports d:0012 (Vasquez, 2016) and d:0072 (Harris, 2024) are the same document with domain nouns swapped, yet fall below the report's same-genre similarity threshold, so only a voice read catches the template collapse. |
| rf:document-plausibility-thread-state-regression | document_plausibility | major | d:0008, d:0022, d:0036 | In three of the four five-message engagement threads, the final email restarts the data-intake narrative, contradicting the resolved state the earlier messages in the same strictly-linear In-Reply-To chain had already established; read top to bottom the thread's state snaps backward at the last message. |
| rf:graph-acl-1 | graph_acl_naturalness | major | d:0003, d:0045, d:0065 | Each kickoff memo that has to give a non-engagement colleague a second mention puts that person on the memo's To-line and assigns them engagement work, but the who-can-read-what ground truth grants them no access to any document of that engagement, including the memo addressed to them. |
| rf:narrative-consistency-thread-regression | narrative_consistency | major | d:0069, d:0070, d:0007, d:0008, d:0034, d:0036 | In three of the four multi-message engagement email threads, the final message reverts the data-intake state to an earlier point, re-raising items the thread had already closed and describing already-reconciled data as freshly arrived, so the thread stops progressing at its last reply. |
| rf:org-realism-1 | org_realism | major | corpus | The firm's measurement/assumption/conclusion credo is not just embodied but explicitly restated in near-identical words in almost every document across every genre, which reads as a generator returning to one idea rather than a firm with a house discipline. |
| rf:org-realism-2 | org_realism | major | d:0025, d:0048 | Two midpoint status reports for different clients, engagement types, and authors are near-clones that share whole distinctive sentences verbatim, reading as one generated template rather than a firm's reused format. |
| rf:org-realism-3 | org_realism | major | d:0019, d:0020, d:0021, d:0022, d:0046 | Engagement emails repeatedly address the recipient by full legal name inside the body, as a reliance-documentation device, which no one does when writing to that person. |
