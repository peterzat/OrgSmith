# Generation report: ashcombe-advisory

Derived artifact: re-emit with `python -m orgsmith report ashcombe-advisory`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

104 documents planned; 79 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-4-8 | xhigh |
| wo:author:0002 | claude-opus-4-8 | xhigh |
| wo:author:0003 | claude-opus-4-8 | xhigh |
| wo:author:0004 | claude-opus-4-8 | xhigh |
| wo:author:0005 | claude-opus-4-8 | xhigh |
| wo:author:0006 | claude-opus-4-8 | xhigh |
| wo:author:0007 | claude-opus-4-8 | xhigh |
| wo:author:0008 | claude-opus-4-8 | xhigh |
| wo:author:0009 | claude-opus-4-8 | xhigh |
| wo:author:0010 | claude-opus-4-8 | xhigh |
| wo:author:0011 | claude-opus-4-8 | xhigh |
| wo:author:0012 | claude-opus-4-8 | xhigh |
| wo:author:0013 | claude-opus-4-8 | xhigh |
| wo:author:0014 | claude-opus-4-8 | xhigh |
| wo:author:0015 | claude-opus-4-8 | xhigh |
| wo:foundation:0001 | claude-opus-4-8 | xhigh |

Model cost: 79 of 104 documents were authored by a model, across 16 work order(s).

The other 25 cost zero model tokens: 8 static (rendered from the deterministic ledgers) and 17 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 29 rules run, 0 error(s), 0 warning(s); skipped by charter knob: AFF-01, AFF-02, STY-01, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score ashcombe-advisory --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

79 authored documents, 28814 words, mean 365.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0008 | engagement_email | 67 | 250 | 0.27 |
| d:0067 | engagement_email | 71 | 250 | 0.28 |
| d:0066 | engagement_email | 78 | 250 | 0.31 |
| d:0005 | engagement_email | 79 | 250 | 0.32 |
| d:0006 | engagement_email | 80 | 250 | 0.32 |
| d:0049 | engagement_email | 89 | 250 | 0.36 |
| d:0050 | engagement_email | 94 | 250 | 0.38 |
| d:0065 | engagement_email | 103 | 250 | 0.41 |
| d:0071 | engagement_email | 103 | 250 | 0.41 |
| d:0070 | engagement_email | 109 | 250 | 0.44 |
| d:0080 | engagement_email | 114 | 250 | 0.46 |
| d:0010 | engagement_email | 115 | 250 | 0.46 |
| d:0068 | engagement_email | 117 | 250 | 0.47 |
| d:0013 | engagement_email | 120 | 250 | 0.48 |
| d:0048 | engagement_email | 120 | 250 | 0.48 |
| d:0079 | engagement_email | 120 | 250 | 0.48 |
| d:0069 | engagement_email | 121 | 250 | 0.48 |
| d:0012 | engagement_email | 125 | 250 | 0.50 |
| d:0054 | engagement_email | 126 | 250 | 0.50 |
| d:0011 | engagement_email | 127 | 250 | 0.51 |
| d:0084 | engagement_email | 129 | 250 | 0.52 |
| d:0053 | engagement_email | 137 | 250 | 0.55 |
| d:0078 | engagement_email | 138 | 250 | 0.55 |
| d:0083 | engagement_email | 144 | 250 | 0.58 |
| d:0052 | engagement_email | 147 | 250 | 0.59 |
| d:0044 | meeting_minutes | 359 | 600 | 0.60 |
| d:0042 | status_report | 509 | 850 | 0.60 |
| d:0082 | engagement_email | 150 | 250 | 0.60 |
| d:0051 | engagement_email | 153 | 250 | 0.61 |
| d:0081 | engagement_email | 155 | 250 | 0.62 |
| d:0041 | meeting_minutes | 376 | 600 | 0.63 |
| d:0039 | kickoff_memo | 409 | 650 | 0.63 |
| d:0004 | engagement_email | 161 | 250 | 0.64 |
| d:0022 | briefing_deck | 265 | 400 | 0.66 |
| d:0014 | meeting_minutes | 420 | 600 | 0.70 |
| d:0064 | engagement_email | 176 | 250 | 0.70 |
| d:0023 | meeting_minutes | 434 | 600 | 0.72 |
| d:0009 | briefing_deck | 292 | 400 | 0.73 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0002 | d:0018 | engagement_letter | 0.418 |
| d:0002 | d:0038 | engagement_letter | 0.3679 |
| d:0038 | d:0045 | engagement_letter | 0.3304 |
| d:0018 | d:0038 | engagement_letter | 0.3074 |
| d:0002 | d:0045 | engagement_letter | 0.2866 |
| d:0018 | d:0045 | engagement_letter | 0.2771 |
| d:0002 | d:0075 | engagement_letter | 0.2258 |
| d:0003 | d:0020 | kickoff_memo | 0.2251 |
| d:0018 | d:0075 | engagement_letter | 0.184 |
| d:0038 | d:0075 | engagement_letter | 0.1819 |
| d:0045 | d:0075 | engagement_letter | 0.1704 |

### Fee coverage

6 documented engagement(s), fees totalling $346,000, against $32,164,000 of lifetime revenue.

Documented fees are 1.1% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 79 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 6 | 6 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 13 | 11 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 32 | 23 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 106 | 49 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 1 | 1 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 11 | 7 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 9 | 9 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:amy.carter | 8 | 0.0025 (0.0000-0.0203) | 0.0009 | 0.0039 |
| p:christopher.walton | 2 | 0.0000 (0.0000-0.0000) | 0.0004 | 0.0000 |
| p:daniel.valenzuela | 7 | 0.0009 (0.0000-0.0074) | 0.0013 | 0.0009 |
| p:john.macias | 7 | 0.0010 (0.0000-0.0081) | 0.0006 | 0.0067 |
| p:julie.hill | 16 | 0.0311 (0.0000-0.4180) | 0.0004 | 0.1113 |
| p:kimberly.le | 6 | 0.0020 (0.0000-0.0206) | 0.0004 | 0.0016 |
| p:laura.bradley | 6 | 0.0022 (0.0000-0.0118) | 0.0010 | 0.0033 |
| p:melissa.zimmerman | 5 | 0.0009 (0.0000-0.0049) | 0.0005 | 0.0010 |
| p:michael.morris | 6 | 0.0052 (0.0000-0.0204) | 0.0018 | 0.0105 |
| p:michelle.black | 2 | 0.0206 (0.0206-0.0206) | 0.0015 | 0.0206 |
| p:michelle.rose | 11 | 0.0011 (0.0000-0.0146) | 0.0008 | 0.0004 |
| p:nancy.suarez | 2 | 0.0388 (0.0388-0.0388) | 0.0014 | 0.0388 |
| p:sandra.mcdonald | 1 | - | 0.0001 | - |

### Review board

17 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:voice-1 | cross_document_voice | blocker | d:0003, d:0020, d:0063, d:0076 | Four kickoff memos attributed to four different advisors are one templated hand, down to a first-person aphorism reproduced word for word across two of them. |
| rf:graphacl-internal-note-to-client | graph_acl_naturalness | blocker | d:0064 | The Suarez-Jones kickoff email is an internal-only planning note but is delivered to the client as the primary recipient. |
| rf:narrative-1 | narrative_consistency | blocker | d:0064, d:0065, d:0066, d:0067, d:0005, d:0006, d:0048, d:0049, d:0050, d:0078, d:0079, d:0080 | In four of the six engagement threads, emails written as internal staff-to-staff handoffs are delivered to the client, so the client's own inbox carries the firm's private deliberation, including a message that says the client must not see it. |
| rf:voice-2 | cross_document_voice | major | corpus | The 'I/we would rather X than Y' antithesis is a single writer's reflex worn by every persona, including the ones the roster casts as brisk, dry, or logistics-only, so it reads as one hand rather than a house style. |
| rf:voice-3 | cross_document_voice | major | d:0057, d:0078, d:0044, d:0063 | Nearly every author lands a paragraph on a polished antithetical maxim, a flourish uniform across personas who are cast as not writing that way. |
| rf:voice-4 | cross_document_voice | major | d:0014, d:0023, d:0055, d:0024, d:0042, d:0056 | Meeting minutes and status reports by different authors share identical section openers that the same-genre similarity metric did not surface. |
| rf:docplaus-1 | document_plausibility | major | d:0030, d:0057, d:0016, d:0033, d:0037 | In the mundane internal emails the sender routinely refers to himself or herself by full name in the third person, which no real author writing their own note would do. |
| rf:graphacl-fullname-surface | graph_acl_naturalness | major | d:0005, d:0008, d:0030, d:0033, d:0037, d:0068 | Across the mailbox, correspondents and the sender's own self are named by full first-and-last name where real email uses a first name or a pronoun, a mention-planting seam. |
| rf:graphacl-recipient-scope | graph_acl_naturalness | major | d:0057, d:0062, d:0087 | The To: line of the mundane internal emails does not match the audience the body is written for. |
| rf:org-realism-1 | org_realism | major | d:0059, d:0018, d:0061, d:0086 | Every client is named like a professional-services partnership, contradicting the firm's own description of its clients as public and pre-IPO operating companies. |
| rf:org-realism-2 | org_realism | major | d:0045, d:0038, d:0002, d:0061 | Across all six documented clients the sole counterpart is an Operations or Finance officer; no client has a communications, IR, or marketing lead, even for the media-relations and crisis engagements. |
| rf:voice-5 | cross_document_voice | minor | d:0010, d:0021, d:0040, d:0047, d:0064 | The engagement emails, the firm's most persona-driven writing, share a cloned request-and-schedule scaffold across authors. |
| rf:docplaus-2 | document_plausibility | minor | d:0073 | A status report prepared by John Macias switches between first person and naming himself in the third person within a single closing paragraph. |
| rf:finance-realism-1 | finance_realism | minor | d:0018, d:0038, d:0061 | Fixed engagement fees barely move with scope or duration: the longest, most senior programs are priced at roughly half the monthly rate of the shortest ones, inverting how professional-services fees usually scale. |
| rf:narrative-2 | narrative_consistency | minor | d:0030 | An internal note refers to its own sender by full name in the third person, so the writer appears to be talking about someone else. |
| rf:org-realism-3 | org_realism | minor | d:0041, d:0072 | The advisory hierarchy is a flat spoke: the one Partner carries all eleven advisory reports while the Senior Advisor, Advisor, and Senior Associate supervise no one, and the highest-stakes engagements are led by associate-level staff. |
| rf:graphacl-unused-lists | graph_acl_naturalness | note | corpus | Of the three distribution lists in the ledger, only all-staff@ is ever a recipient; the other two carry no traffic and one has a single member. |
