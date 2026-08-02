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

Model cost: 168 of 218 documents were authored by a model, across 38 work order(s).

The other 50 cost zero model tokens: 15 static (rendered from the deterministic ledgers) and 35 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 30 rules run, 0 error(s), 0 warning(s); skipped by charter knob: MENT-03, AFF-01, AFF-02, EML-02, EML-03, DL-01, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score calderwood-partners --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

168 authored documents, 99668 words, mean 593.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0167 | status_report | 507 | 850 | 0.60 |
| d:0021 | engagement_email | 157 | 250 | 0.63 |
| d:0068 | engagement_email | 176 | 250 | 0.70 |
| d:0020 | briefing_deck | 285 | 400 | 0.71 |
| d:0037 | briefing_deck | 287 | 400 | 0.72 |
| d:0017 | onboarding_record | 324 | 450 | 0.72 |
| d:0019 | engagement_email | 180 | 250 | 0.72 |
| d:0005 | onboarding_record | 331 | 450 | 0.74 |
| d:0052 | briefing_deck | 299 | 400 | 0.75 |
| d:0003 | onboarding_record | 337 | 450 | 0.75 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0058 | d:0065 | engagement_letter | 0.4365 |
| d:0023 | d:0058 | engagement_letter | 0.4254 |
| d:0065 | d:0102 | engagement_letter | 0.3924 |
| d:0006 | d:0091 | engagement_letter | 0.3884 |
| d:0006 | d:0050 | engagement_letter | 0.3843 |
| d:0023 | d:0141 | engagement_letter | 0.3811 |
| d:0093 | d:0173 | engagement_email | 0.3594 |
| d:0091 | d:0171 | engagement_letter | 0.3402 |
| d:0026 | d:0135 | engagement_letter | 0.3387 |
| d:0016 | d:0157 | engagement_letter | 0.3354 |
| d:0006 | d:0127 | engagement_letter | 0.3278 |
| d:0023 | d:0065 | engagement_letter | 0.3265 |
| d:0024 | d:0157 | engagement_letter | 0.3263 |
| d:0016 | d:0024 | engagement_letter | 0.3255 |
| d:0084 | d:0157 | engagement_letter | 0.3244 |
| d:0058 | d:0102 | engagement_letter | 0.3229 |
| d:0006 | d:0159 | engagement_letter | 0.3211 |
| d:0016 | d:0084 | engagement_letter | 0.3175 |
| d:0016 | d:0177 | engagement_letter | 0.3098 |
| d:0075 | d:0137 | engagement_letter | 0.3085 |
| d:0058 | d:0141 | engagement_letter | 0.3066 |
| d:0157 | d:0177 | engagement_letter | 0.3062 |
| d:0050 | d:0159 | engagement_letter | 0.3059 |
| d:0065 | d:0141 | engagement_letter | 0.3039 |
| d:0024 | d:0084 | engagement_letter | 0.3006 |
| d:0091 | d:0159 | engagement_letter | 0.2978 |
| d:0084 | d:0177 | engagement_letter | 0.2966 |
| d:0024 | d:0177 | engagement_letter | 0.2917 |
| d:0127 | d:0159 | engagement_letter | 0.2855 |
| d:0096 | d:0119 | company_overview | 0.2849 |
| d:0023 | d:0102 | engagement_letter | 0.2845 |
| d:0050 | d:0091 | engagement_letter | 0.282 |
| d:0050 | d:0127 | engagement_letter | 0.2784 |
| d:0091 | d:0127 | engagement_letter | 0.2751 |
| d:0102 | d:0110 | engagement_letter | 0.2658 |
| d:0070 | d:0096 | company_overview | 0.2515 |
| d:0016 | d:0023 | engagement_letter | 0.2471 |
| d:0006 | d:0171 | engagement_letter | 0.244 |
| d:0159 | d:0171 | engagement_letter | 0.2413 |
| d:0102 | d:0141 | engagement_letter | 0.2382 |
| d:0023 | d:0024 | engagement_letter | 0.2329 |
| d:0060 | d:0069 | briefing_deck | 0.2294 |
| d:0016 | d:0058 | engagement_letter | 0.2262 |
| d:0050 | d:0171 | engagement_letter | 0.2262 |
| d:0127 | d:0171 | engagement_letter | 0.2248 |
| d:0023 | d:0084 | engagement_letter | 0.223 |
| d:0023 | d:0177 | engagement_letter | 0.2229 |
| d:0058 | d:0177 | engagement_letter | 0.2229 |
| d:0016 | d:0075 | engagement_letter | 0.2205 |
| d:0023 | d:0157 | engagement_letter | 0.2188 |
| d:0075 | d:0084 | engagement_letter | 0.2178 |
| d:0075 | d:0177 | engagement_letter | 0.2136 |
| d:0075 | d:0157 | engagement_letter | 0.2133 |
| d:0024 | d:0058 | engagement_letter | 0.2091 |
| d:0058 | d:0157 | engagement_letter | 0.2052 |
| d:0065 | d:0110 | engagement_letter | 0.2048 |
| d:0024 | d:0075 | engagement_letter | 0.2023 |
| d:0024 | d:0141 | engagement_letter | 0.2015 |
| d:0141 | d:0177 | engagement_letter | 0.2015 |
| d:0058 | d:0084 | engagement_letter | 0.1999 |
| d:0006 | d:0120 | engagement_letter | 0.1995 |
| d:0016 | d:0141 | engagement_letter | 0.1973 |
| d:0120 | d:0127 | engagement_letter | 0.1973 |
| d:0024 | d:0065 | engagement_letter | 0.1952 |
| d:0141 | d:0157 | engagement_letter | 0.1931 |
| d:0102 | d:0177 | engagement_letter | 0.1919 |
| d:0050 | d:0120 | engagement_letter | 0.1917 |
| d:0065 | d:0157 | engagement_letter | 0.1907 |
| d:0065 | d:0177 | engagement_letter | 0.1903 |
| d:0016 | d:0065 | engagement_letter | 0.1884 |
| d:0084 | d:0141 | engagement_letter | 0.1875 |
| d:0065 | d:0084 | engagement_letter | 0.1847 |
| d:0084 | d:0102 | engagement_letter | 0.1845 |
| d:0091 | d:0120 | engagement_letter | 0.1844 |
| d:0120 | d:0159 | engagement_letter | 0.1837 |
| d:0024 | d:0102 | engagement_letter | 0.1836 |
| d:0102 | d:0157 | engagement_letter | 0.1835 |
| d:0016 | d:0102 | engagement_letter | 0.1823 |
| d:0105 | d:0112 | engagement_email | 0.1788 |
| d:0009 | d:0054 | engagement_email | 0.1772 |
| d:0023 | d:0075 | engagement_letter | 0.1753 |
| d:0058 | d:0110 | engagement_letter | 0.1751 |
| d:0063 | d:0071 | meeting_minutes | 0.173 |
| d:0058 | d:0075 | engagement_letter | 0.1698 |
| d:0137 | d:0157 | engagement_letter | 0.1686 |
| d:0120 | d:0171 | engagement_letter | 0.1685 |
| d:0079 | d:0147 | status_report | 0.1671 |
| d:0067 | d:0105 | engagement_email | 0.1667 |
| d:0094 | d:0130 | onboarding_record | 0.1641 |
| d:0024 | d:0137 | engagement_letter | 0.162 |
| d:0084 | d:0137 | engagement_letter | 0.16 |
| d:0137 | d:0177 | engagement_letter | 0.1586 |
| d:0016 | d:0137 | engagement_letter | 0.1577 |
| d:0023 | d:0110 | engagement_letter | 0.1545 |
| d:0098 | d:0175 | status_report | 0.1528 |
| d:0070 | d:0119 | company_overview | 0.151 |
| d:0075 | d:0141 | engagement_letter | 0.1508 |

### Structural similarity

The 10 strongest of 2072 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0098 | d:0175 | status_report | 1.0 | 0.8571 | 0.1528 |
| d:0091 | d:0171 | engagement_letter | 0.9524 | 0.9 | 0.3402 |
| d:0050 | d:0091 | engagement_letter | 1.0 | 0.85 | 0.282 |
| d:0006 | d:0091 | engagement_letter | 0.9048 | 0.9 | 0.3884 |
| d:0050 | d:0171 | engagement_letter | 0.9524 | 0.85 | 0.2262 |
| d:0127 | d:0171 | engagement_letter | 0.9524 | 0.85 | 0.2248 |
| d:0094 | d:0169 | onboarding_record | 0.8 | 1.0 | 0.1013 |
| d:0122 | d:0162 | engagement_email | 1.0 | 0.8 | 0.0496 |
| d:0006 | d:0127 | engagement_letter | 0.9048 | 0.85 | 0.3278 |
| d:0024 | d:0157 | engagement_letter | 1.0 | 0.7368 | 0.3263 |

2072 pairs were scored; the artifact keeps the strongest 50 and this table shows the top 10. The full ranking is recomputable from committed DocIR (`orgsmith.review.structure.compute_pairs`); it is truncated here rather than dropped silently.

### Fee coverage

22 documented engagement(s), fees totalling $1,545,000, against $68,226,000 of lifetime revenue.

Documented fees are 2.3% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 168 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 2 | 2 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 4 | 4 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 19 | 17 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 304 | 131 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 4 | 4 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 5 | 5 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:brenda.clayton | 5 | 0.0046 (0.0000-0.0242) | 0.0015 | 0.0004 |
| p:brenda.rodriguez | 13 | 0.0046 (0.0000-0.0377) | 0.0013 | 0.0137 |
| p:cynthia.hart | 3 | 0.0028 (0.0012-0.0051) | 0.0022 | 0.0044 |
| p:daniel.cisneros | 3 | 0.0063 (0.0011-0.0131) | 0.0020 | 0.0117 |
| p:daniel.leach | 7 | 0.0055 (0.0000-0.0417) | 0.0018 | 0.0084 |
| p:deborah.allen | 5 | 0.0095 (0.0000-0.0388) | 0.0023 | 0.0055 |
| p:deborah.gordon | 9 | 0.0038 (0.0000-0.0249) | 0.0024 | 0.0122 |
| p:deborah.jimenez | 7 | 0.0044 (0.0000-0.0392) | 0.0014 | 0.0137 |
| p:james.green | 3 | 0.0051 (0.0013-0.0095) | 0.0022 | 0.0082 |
| p:jason.torres | 13 | 0.0064 (0.0000-0.0989) | 0.0022 | 0.0191 |
| p:john.vasquez | 3 | 0.0061 (0.0052-0.0071) | 0.0019 | 0.0072 |
| p:joseph.reed | 3 | 0.0064 (0.0000-0.0160) | 0.0020 | 0.0139 |
| p:julie.parks | 5 | 0.0101 (0.0000-0.0573) | 0.0026 | 0.0321 |
| p:julie.ramsey | 46 | 0.0324 (0.0000-0.4365) | 0.0005 | 0.1765 |
| p:julie.vasquez | 3 | 0.0055 (0.0000-0.0165) | 0.0031 | 0.0133 |
| p:mary.parker | 7 | 0.0026 (0.0000-0.0167) | 0.0018 | 0.0030 |
| p:matthew.parrish | 7 | 0.0031 (0.0000-0.0375) | 0.0022 | 0.0022 |
| p:melissa.casey | 8 | 0.0057 (0.0000-0.0516) | 0.0023 | 0.0226 |
| p:michael.walker | 6 | 0.0034 (0.0000-0.0218) | 0.0017 | 0.0053 |
| p:nicole.griffin | 5 | 0.0118 (0.0000-0.0860) | 0.0026 | 0.0088 |
| p:pamela.miller | 3 | 0.0027 (0.0000-0.0059) | 0.0031 | 0.0050 |
| p:steven.hunt | 4 | 0.0045 (0.0009-0.0083) | 0.0026 | 0.0064 |

### Review board

8 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:cross-voice-1 | cross_document_voice | major | d:0007, d:0051, d:0092, d:0128, d:0160, d:0172 | The kickoff memos, though attributed to six different staff from Principal to Research Associate across 2008-2021, are built from one template and repeat the same idiosyncratic sentences verbatim, so the genre reads as a single author with names swapped rather than the different hands the charter explicitly promises ('no two memos are built from the same template'). |
| rf:cross-voice-2 | cross_document_voice | major | d:0009, d:0054, d:0122, d:0145, d:0041, d:0142 | The same single-hand fingerprint runs past the kickoff memos into other genres: engagement-email threads and analytical-review minutes repeat distinctive sentences verbatim across authors who, by design, never saw one another's work, so the whole corpus reads as one writer varying cadence rather than a firm of independent hands. |
| rf:finance-realism-1 | finance_realism | major | d:0084, d:0102, d:0026 | Engagement fees run inverse to the seniority and size of the team staffed on them: the firm's Principal-led engagements are the cheapest in the book per month and priced below its own labor cost, while its all-junior engagements cost several times more, so the fees bear no relation to what the depicted work would cost. |
| rf:graph-acl-mention-quota-1 | graph_acl_naturalness | major | d:0008, d:0009, d:0053, d:0054, d:0030 | The person-mention pattern reads as a quota being filled: senders name themselves by full name inside their own emails, and recipients are re-addressed by full name mid-sentence after a first-name greeting. |
| rf:org-realism-1 | org_realism | major | d:0102, d:0106, d:0107, d:0174, d:0175, d:0119 | Several client engagements are staffed and run end to end by Research Associates, the firm's most junior title, with no principal, engagement manager, or consultant on the team or in the room with the client, inverting the pyramid the firm's own overview promises. |
| rf:document-plausibility-1 | document_plausibility | minor | d:0177, d:0178 | The firm's 'representative sample, not the whole book' disclaimer is inserted into a client engagement letter and an internal kickoff memo, two genres that would not carry it, making the constraint visible as a planted motif rather than natural document content. |
| rf:graph-acl-participant-locked-out-2 | graph_acl_naturalness | minor | d:0007, d:0181 | Read access is stamped from the engagement participant graph, so a current employee named as a genuine participant in a document is denied access to it. |
| rf:narrative-consistency-1 | narrative_consistency | note | d:0012, d:0131, d:0055, d:0163 | The same mid-engagement plot beat -- a single merged cost line that cannot be split, which becomes the one blocker gating the baseline -- recurs as the central working-session problem across four unrelated clients over twelve years, so the engagements read less like independent histories than like one story retold. |
