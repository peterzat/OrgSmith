# Generation report: saltmarsh-environmental

Derived artifact: re-emit with `python -m orgsmith report saltmarsh-environmental`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

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
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

Model cost: 31 of 40 documents were authored by a model, across 8 work order(s).

The other 9 cost zero model tokens: 9 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 29 rules run, 0 error(s), 0 warning(s); skipped by charter knob: NOISE-01, EML-01, EML-02, EML-03, DL-01, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score saltmarsh-environmental --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

31 authored documents, 20426 words, mean 659.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0005 | d:0036 | engagement_letter | 0.199 |
| d:0022 | d:0029 | engagement_letter | 0.171 |

### Fee coverage

5 documented engagement(s), fees totalling $414,000, against $17,116,000 of lifetime revenue.

Documented fees are 2.4% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 31 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 1 | 1 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 5 | 5 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 31 | 20 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:angela.flynn | 13 | 0.0107 (0.0000-0.1990) | 0.0016 | 0.0699 |
| p:angela.williams | 3 | 0.0213 (0.0144-0.0293) | 0.0033 | 0.0228 |
| p:heather.morton | 4 | 0.0131 (0.0000-0.0539) | 0.0050 | 0.0033 |
| p:james.henderson | 1 | - | 0.0071 | - |
| p:john.sanchez | 5 | 0.0083 (0.0008-0.0612) | 0.0035 | 0.0020 |
| p:joseph.nichols | 1 | - | 0.0041 | - |
| p:mary.foster | 2 | 0.0048 (0.0048-0.0048) | 0.0019 | 0.0048 |
| p:william.schwartz | 2 | 0.0161 (0.0161-0.0161) | 0.0053 | 0.0161 |

### Review board

9 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:cross-voice-1 | cross_document_voice | major | d:0023, d:0030, d:0022, d:0032 | Documents attributed to different authors share distinctive, non-slogan sentences near-verbatim, so a cross-document read exposes one generator hand behind supposedly independent writers. |
| rf:fin-realism-1 | finance_realism | major | d:0003, d:0007, d:0021, d:0040, d:0035 | The firm insists across its records that it is five people, but its own financials (revenue past $2.1M, compensation past $1.23M) are the payroll and billings of a firm roughly twice that size. |
| rf:graph-acl-1 | graph_acl_naturalness | major | d:0040 | The 2021 firm overview's client showcase names the same client, Dyer and Sons, twice consecutively, because two of the five engagements it lists to demonstrate client range share that one client. |
| rf:narrative-consistency-1 | narrative_consistency | major | d:0021, d:0040 | The firm overviews insist on a static five-person headcount and deny any growth, contradicting the firm's own roster and onboarding records, which show it grew to nine employees over the span. |
| rf:narrative-consistency-2 | narrative_consistency | major | d:0040, d:0021 | Two of the five engagements are for the same client (Dyer and Sons), so the firm-overview client showcase presents that client as two distinct clients, listing 'Dyer and Sons' twice consecutively in the 2021 overview's representative-client list. |
| rf:org-realism-duplicate-client | org_realism | major | d:0040 | The 2021 firm overview's representative-client showcase names the same client twice because two sampled engagements share it, so the list reads 'Dyer and Sons, Dyer and Sons, Salazar-Mendoza, ...'. |
| rf:org-realism-headcount-five | org_realism | major | d:0021, d:0040, d:0033 | The firm overviews assert a fixed five-person headcount as a deliberate, unchanging identity, but the roster grows to nine active staff by 2021 and the corpus's own onboarding records document that growth. |
| rf:docplaus-1 | document_plausibility | minor | d:0014 | The Phase I engagement letter carries two adjacent, redundantly titled fee sections where the firm's four other engagement letters use a single fee treatment. |
| rf:org-realism-agency-clients-absent | org_realism | minor | d:0007, d:0021, d:0040 | Every firm overview foregrounds two public-agency client types (a port authority, a county conservation district) that never appear, and d:0040 claims its all-private example set represents 'a mix of public agencies and private landowners.' |
