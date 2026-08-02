# Generation report: ashcombe-advisory

Derived artifact: re-emit with `python -m orgsmith report ashcombe-advisory`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

104 documents planned; 79 carry authored prose.

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
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

Model cost: 79 of 104 documents were authored by a model, across 16 work order(s).

The other 25 cost zero model tokens: 8 static (rendered from the deterministic ledgers) and 17 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 31 rules run, 0 error(s), 0 warning(s); skipped by charter knob: MENT-03, AFF-01, AFF-02, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score ashcombe-advisory --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

79 authored documents, 28967 words, mean 367.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0013 | engagement_email | 75 | 250 | 0.30 |
| d:0011 | engagement_email | 84 | 250 | 0.34 |
| d:0005 | engagement_email | 91 | 250 | 0.36 |
| d:0008 | engagement_email | 97 | 250 | 0.39 |
| d:0012 | engagement_email | 102 | 250 | 0.41 |
| d:0006 | engagement_email | 110 | 250 | 0.44 |
| d:0010 | engagement_email | 118 | 250 | 0.47 |
| d:0054 | engagement_email | 119 | 250 | 0.48 |
| d:0067 | engagement_email | 126 | 250 | 0.50 |
| d:0065 | engagement_email | 127 | 250 | 0.51 |
| d:0052 | engagement_email | 131 | 250 | 0.52 |
| d:0070 | engagement_email | 131 | 250 | 0.52 |
| d:0084 | engagement_email | 131 | 250 | 0.52 |
| d:0083 | engagement_email | 137 | 250 | 0.55 |
| d:0050 | engagement_email | 141 | 250 | 0.56 |
| d:0053 | engagement_email | 144 | 250 | 0.58 |
| d:0051 | engagement_email | 146 | 250 | 0.58 |
| d:0071 | engagement_email | 146 | 250 | 0.58 |
| d:0082 | engagement_email | 147 | 250 | 0.59 |
| d:0066 | engagement_email | 152 | 250 | 0.61 |
| d:0081 | engagement_email | 154 | 250 | 0.62 |
| d:0068 | engagement_email | 156 | 250 | 0.62 |
| d:0080 | engagement_email | 157 | 250 | 0.63 |
| d:0003 | kickoff_memo | 417 | 650 | 0.64 |
| d:0039 | kickoff_memo | 429 | 650 | 0.66 |
| d:0049 | engagement_email | 167 | 250 | 0.67 |
| d:0069 | engagement_email | 167 | 250 | 0.67 |
| d:0048 | engagement_email | 174 | 250 | 0.70 |
| d:0063 | kickoff_memo | 459 | 650 | 0.71 |
| d:0004 | engagement_email | 177 | 250 | 0.71 |
| d:0047 | engagement_email | 178 | 250 | 0.71 |
| d:0078 | engagement_email | 178 | 250 | 0.71 |
| d:0079 | engagement_email | 182 | 250 | 0.73 |
| d:0060 | onboarding_record | 331 | 450 | 0.74 |
| d:0041 | meeting_minutes | 444 | 600 | 0.74 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0002 | d:0061 | engagement_letter | 0.3612 |
| d:0002 | d:0045 | engagement_letter | 0.308 |
| d:0004 | d:0064 | engagement_email | 0.2756 |
| d:0003 | d:0063 | kickoff_memo | 0.2738 |
| d:0061 | d:0075 | engagement_letter | 0.2425 |
| d:0015 | d:0024 | status_report | 0.2382 |
| d:0045 | d:0061 | engagement_letter | 0.2297 |
| d:0034 | d:0060 | onboarding_record | 0.2168 |
| d:0002 | d:0075 | engagement_letter | 0.1894 |
| d:0032 | d:0059 | company_overview | 0.184 |
| d:0036 | d:0060 | onboarding_record | 0.1647 |
| d:0045 | d:0075 | engagement_letter | 0.1613 |

### Structural similarity

The 10 strongest of 682 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0003 | d:0063 | kickoff_memo | 0.9412 | 0.8 | 0.2738 |
| d:0002 | d:0045 | engagement_letter | 0.9818 | 0.7547 | 0.308 |
| d:0010 | d:0012 | engagement_email | 1.0 | 0.6667 | 0.0337 |
| d:0002 | d:0061 | engagement_letter | 0.9091 | 0.7547 | 0.3612 |
| d:0041 | d:0044 | meeting_minutes | 0.9091 | 0.7429 | 0.0566 |
| d:0049 | d:0051 | engagement_email | 1.0 | 0.6 | 0.0099 |
| d:0050 | d:0054 | engagement_email | 1.0 | 0.6 | 0.012 |
| d:0066 | d:0070 | engagement_email | 1.0 | 0.6 | 0.0145 |
| d:0067 | d:0069 | engagement_email | 1.0 | 0.6 | 0.0246 |
| d:0067 | d:0071 | engagement_email | 1.0 | 0.6 | 0.0591 |

682 pairs were scored; the artifact keeps the strongest 50 and this table shows the top 10. The full ranking is recomputable from committed DocIR (`orgsmith.review.structure.compute_pairs`); it is truncated here rather than dropped silently.

### Fee coverage

6 documented engagement(s), fees totalling $346,000, against $32,164,000 of lifetime revenue.

Documented fees are 1.1% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 79 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 1 | 1 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 6 | 6 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 61 | 37 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 1 | 1 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:amy.carter | 8 | 0.0082 (0.0000-0.0591) | 0.0021 | 0.0108 |
| p:christopher.walton | 2 | 0.0084 (0.0084-0.0084) | 0.0003 | 0.0084 |
| p:daniel.valenzuela | 7 | 0.0051 (0.0000-0.0411) | 0.0032 | 0.0034 |
| p:john.macias | 7 | 0.0042 (0.0000-0.0145) | 0.0027 | 0.0059 |
| p:julie.hill | 16 | 0.0214 (0.0000-0.3612) | 0.0003 | 0.1164 |
| p:kimberly.le | 6 | 0.0046 (0.0000-0.0233) | 0.0006 | 0.0071 |
| p:laura.bradley | 6 | 0.0031 (0.0000-0.0099) | 0.0017 | 0.0047 |
| p:melissa.zimmerman | 5 | 0.0049 (0.0000-0.0120) | 0.0006 | 0.0075 |
| p:michael.morris | 6 | 0.0059 (0.0000-0.0387) | 0.0017 | 0.0210 |
| p:michelle.black | 2 | 0.0226 (0.0226-0.0226) | 0.0009 | 0.0226 |
| p:michelle.rose | 11 | 0.0035 (0.0000-0.0408) | 0.0010 | 0.0011 |
| p:nancy.suarez | 2 | 0.0566 (0.0566-0.0566) | 0.0005 | 0.0566 |
| p:sandra.mcdonald | 1 | - | 0.0001 | - |

### Review board

42 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:document_plausibility-1 | document_plausibility | blocker | corpus | Nearly every client-facing email addresses its first-name correspondent by full legal name mid-body, usually under a 'for the file' or 'for the record' formula, exposing the fact-planting machinery. |
| rf:xvoice-1 | cross_document_voice | major | corpus | Every author from Managing Partner to Office Manager writes in one literary register, built on the balanced antithesis and the aphoristic closing turn, so the corpus reads as one stylist wearing thirteen names. |
| rf:xvoice-2 | cross_document_voice | major | d:0003, d:0039, d:0046, d:0063, d:0076 | Five kickoff memos by five different authors across seven years reuse the same signature first-person asides; these are personal framing sentences, not form fields, so it reads as one generator rather than a memo template. |
| rf:xvoice-3 | cross_document_voice | major | d:0004, d:0021, d:0040, d:0047, d:0064, d:0077 | All six engagements' opening client emails, by six different authors from 2017 to 2024, run the same script: open the thread to keep updates in one place, log the contacts for the file, report 'we have made a start', promise a steady cadence, ask one question, offer a short call. |
| rf:xvoice-4 | cross_document_voice | major | d:0015, d:0022, d:0024, d:0042, d:0056 | First-person status-report narration recurs verbatim across different authors writing to different clients, past what a house report skeleton would explain; the metric flagged only d:0015/d:0024, but the pattern spans four authors. |
| rf:xvoice-5 | cross_document_voice | major | d:0005, d:0047, d:0052, d:0065, d:0068 | Every author works the client approver's full name into the email body with the same notarial 'For the file / For the record' device, addressing the correspondent by their own full name mid-message; the fact placement is mandated, but the identical workaround across eight authors is the voice leak. |
| rf:xvoice-6 | cross_document_voice | major | d:0007, d:0015, d:0022, d:0073 | Distinctive personal asides recur nearly verbatim across different authors in unrelated genres years apart, which the same-genre similarity metric is structurally blind to. |
| rf:document_plausibility-2 | document_plausibility | major | corpus | The mailbox holds only the firm's half of every conversation: all 45 .eml files are From an @ashcombeadvisory.com address, each thread strictly alternates the same two firm authors, and the client's turns exist only as recaps inside firm mail. |
| rf:document_plausibility-3 | document_plausibility | major | d:0049, d:0050, d:0051, d:0052 | The Kirby-Taylor thread forgets its own state: the fact sheet is declared final and locked, then the next email in the same thread asks the client for the same quarterly figures as if they were never sent, then a discrepancy turns up in the already-locked sheet. |
| rf:document_plausibility-4 | document_plausibility | major | d:0066, d:0067, d:0068, d:0071 | The Suarez-Jones thread contradicts its own timeline: a walk-through call scheduled for the coming week is thanked-for as 'last week' on the Monday that week begins, and a draft promised for Aug 5 finally goes out Aug 11 described as ahead of promise. |
| rf:document_plausibility-5 | document_plausibility | major | d:0002, d:0007, d:0032, d:0059 | The firm overviews name clients, including the crisis-communications client, as marketing case studies while every engagement letter promises that the fact of the firm's involvement is itself confidential; the 2017 overview also narrates a month-old, still-active engagement in completed past tense. |
| rf:document_plausibility-8 | document_plausibility | major | d:0016, d:0019, d:0030, d:0033, d:0037, d:0057, d:0062, d:0087 | All eight mundane internal emails across eight years fall on July 1-3, one per year, so the shared mailbox's entire internal life happens in a single week of the calendar. |
| rf:finance-realism-1 | finance_realism | major | d:0050, d:0051, d:0052, d:0054 | The Kirby-Taylor numbers thread contradicts itself: the fact sheet is declared final and twice-checked on June 3, the same quarterly figures are re-requested the same day, and a discrepancy against the public record surfaces three days later in figures already declared reconciled. |
| rf:graph-acl-1 | graph_acl_naturalness | major | d:0004, d:0049, d:0068, d:0079 | Client contacts never author a single email: all four preserved 8-message engagement threads are exclusively outbound, strictly alternating two internal authors while the client's replies happen off-screen. |
| rf:graph-acl-2 | graph_acl_naturalness | major | d:0005, d:0008, d:0052, d:0071, d:0082, d:0030, d:0057 | Nearly every email names its own recipient by full name in the second person, a 'for the file / for the record' tic that recites the participant ledger where a human would say 'you'. |
| rf:graph-acl-3 | graph_acl_naturalness | major | d:0068, d:0070, d:0072, d:0085 | Beyond the six single points of contact, no client-side human is ever named in eight years of communications work: executives are interviewed, spokespeople briefed, and boards consulted strictly anonymously. |
| rf:graph-acl-4 | graph_acl_naturalness | major | d:0002, d:0038, d:0045, d:0061, d:0075 | Every client counterpart carries an operations or finance title; a corporate-communications advisory never once corresponds with a communications, IR, marketing, or legal contact on any client side. |
| rf:graph-acl-5 | graph_acl_naturalness | major | d:0003, d:0038, d:0041, d:0046 | The partner oversight every letter promises never appears in any interaction record: outside one 2018 engagement, no partner or senior advisor attends a meeting, joins a thread, or clears a statement anywhere in the corpus. |
| rf:graph-acl-6 | graph_acl_naturalness | major | d:0038 | The ACL is one flat grid, every active employee holding identical access to all 104 files, even though the crisis letter promises need-to-know internal handling for that very engagement. |
| rf:narrative-1 | narrative_consistency | major | d:0049, d:0050, d:0051 | The Kirby-Taylor thread resets mid-stream: email 5 asks the client to send the quarterly figures that email 3 already acknowledged receiving and email 4, sent the same day, had already folded into a finished fact sheet. |
| rf:narrative-2 | narrative_consistency | major | d:0077, d:0079, d:0081, d:0082 | The Gallegos, Pope and Marsh thread replays its own opening stage: after interviews are penciled in and the coverage read is finished, later emails restart the coverage read, ask the client for interview names as if none existed, and put the not-yet-drafted interview guide back on the to-do list. |
| rf:narrative-3 | narrative_consistency | major | d:0067, d:0068 | In the Suarez-Jones thread the client call flips across a weekend from upcoming to already held: Friday's email places it next week, Monday's email thanks the client for it last week. |
| rf:org_realism-1 | org_realism | major | d:0002, d:0038, d:0007, d:0032, d:0059 | The firm's marketing overviews name engagement clients, including the crisis client, as case studies, directly contradicting its own engagement letters' promise that the fact of the engagement stays confidential. |
| rf:org_realism-2 | org_realism | major | corpus | Every engagement thread is two firm authors in perfect A/B alternation with zero client messages on file, a mechanical rhythm no real mailbox has. |
| rf:document_plausibility-6 | document_plausibility | minor | d:0002, d:0018, d:0038, d:0045, d:0061, d:0075 | No executed letter ever names its governing jurisdiction, and the letterhead carries no address, leaving the firm with no geography across eight years of signed legal documents. |
| rf:document_plausibility-7 | document_plausibility | minor | d:0010, d:0011, d:0012, d:0013 | The back half of the Barrera thread duplicates the transport headers as body text: each email opens with a 'To:/Cc:' paragraph above the salutation, a memo formatting habit no other thread has. |
| rf:finance-realism-2 | finance_realism | minor | d:0018, d:0038, d:0045, d:0061, d:0075 | Four of the six engagement fees form an exact $500 ladder ($45,500 / $46,000 / $46,500 / $47,000) across seven years and four service lines, and the pricing runs inverted, with crisis communications the cheapest work in the book per month. |
| rf:finance-realism-3 | finance_realism | minor | d:0015, d:0024, d:0042, d:0056 | The budget section is the one part of the status reports that collapses to a single voice: four different authors across five years state the fee position in the same first-person sentence. |
| rf:graph-acl-7 | graph_acl_naturalness | minor | corpus | Distribution lists mirror the charter's three departments mechanically, giving a 12-person firm a 'Leadership Team' list with exactly one member; two of the three lists are never used by any email. |
| rf:graph-acl-8 | graph_acl_naturalness | minor | d:0028, d:0029, d:0045 | The name pool produced confusable near-collisions, sharpest an internal Office Manager Sandra Mcdonald and client contact Sandra Mcdaniel, both handling records and approvals in the same years. |
| rf:graph-acl-9 | graph_acl_naturalness | minor | d:0033, d:0037, d:0087 | Mundane office mail is authored by roster roulette: the Managing Partner sends the IT-maintenance notice, an analyst the parking update, an associate the timesheet reminder, while the Office Manager whose persona owns the mundane internal mail authors nothing. |
| rf:narrative-5 | narrative_consistency | minor | d:0076, d:0078, d:0081, d:0085 | The Gallegos coverage review's span shifts between documents: the kickoff memo and the analyst's first report say two years, later mail and the working-session minutes say eighteen months. |
| rf:narrative-6 | narrative_consistency | minor | d:0007, d:0009 | The 2017 firm overview, written one month into the five-month Barrera engagement, narrates it in the past tense as a quietly concluded success, while the contemporaneous engagement documents show the first messaging draft still in review and nothing yet public. |
| rf:org_realism-3 | org_realism | minor | d:0007, d:0038, d:0041, d:0044 | The crisis engagement, the gravest matter in the book, is run by the firm's two most junior associates while the senior bench the overview advertises never appears in it, part of a 2021-2024 pattern where partners and advisors vanish from client work. |
| rf:org_realism-4 | org_realism | minor | d:0015, d:0024, d:0029, d:0042, d:0056, d:0073, d:0086, d:0007, d:0032, d:0059 | File naming is mechanically uniform where a real share drifts: all seven status reports across 2017-2024 are 'v2 FINAL' and all three firm overviews are 'v3'. |
| rf:org_realism-5 | org_realism | minor | d:0007, d:0011 | The 2017 firm overview presents the Barrera engagement as a completed, successful case study one month into its five-month term, while the live thread shows the first messaging draft still in revision that same week. |
| rf:xvoice-7 | cross_document_voice | note | corpus | The high-overlap pairs the metric flagged within Julie Hill's own genres read as legitimate self-template reuse, and the surface voice layer does differentiate: greetings, closings, and list habits track the style specs, and meeting minutes are the one genre with genuinely distinct voices. |
| rf:document_plausibility-10 | document_plausibility | note | d:0028, d:0045 | Foundation-level naming inherited by the prose: faker-style capitalization (Mcdonald, Mcdaniel for McDonald, McDaniel) plus the near-collision of internal records-keeper Sandra Mcdonald with client-side approver Sandra Mcdaniel reads as synthetic naming rather than coincidence. |
| rf:document_plausibility-9 | document_plausibility | note | d:0015, d:0024, d:0042, d:0056 | Interpreting the flagged status-report overlap: it reads less like a firm template than one writer's idea, because four different authors on four unrelated engagements present the same three stock risks as bespoke judgment under a near-identical incipit. |
| rf:finance-realism-4 | finance_realism | note | corpus | Money never misbehaves anywhere in the corpus: after each letter is signed, the fee reappears only as 'tracking within its fixed fee', and no invoice sent, payment made or chased, scope change priced, or fee pushback occurs in eight years of correspondence. |
| rf:graph-acl-10 | graph_acl_naturalness | note | corpus | Six of eighteen external graph entities are quota-filled orphans with no documentary presence at all. |
| rf:narrative-4 | narrative_consistency | note | corpus | Three of the four multi-email engagement threads sampled (Kirby-Taylor, Suarez-Jones, Gallegos) contradict their own earlier messages, while the longform documents around them (kickoffs, minutes, status reports) stay mutually consistent; the continuity failures are concentrated in mid-thread email, as if each reply were written without the thread's accumulated state. |
