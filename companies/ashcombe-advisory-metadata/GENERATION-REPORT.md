# Generation report: ashcombe-advisory

Derived artifact: re-emit with `python -m orgsmith report ashcombe-advisory`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

104 documents planned; 79 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-5-5 | xhigh |
| wo:author:0002 | claude-opus-5-5 | xhigh |
| wo:author:0003 | claude-opus-5-5 | xhigh |
| wo:author:0004 | claude-opus-5-5 | xhigh |
| wo:author:0005 | claude-opus-5-5 | xhigh |
| wo:author:0006 | claude-opus-5-5 | xhigh |
| wo:author:0007 | claude-opus-5-5 | xhigh |
| wo:author:0008 | claude-opus-5-5 | xhigh |
| wo:author:0009 | claude-opus-5-5 | xhigh |
| wo:author:0010 | claude-opus-5-5 | xhigh |
| wo:author:0011 | claude-opus-5-5 | xhigh |
| wo:author:0012 | claude-opus-5-5 | xhigh |
| wo:author:0013 | claude-opus-5-5 | xhigh |
| wo:author:0014 | claude-opus-5-5 | xhigh |
| wo:author:0015 | claude-opus-5-5 | xhigh |
| wo:foundation:0001 | claude-opus-5-5 | xhigh |

Model cost: 79 of 104 documents were authored by a model, across 16 work order(s).

The other 25 cost zero model tokens: 8 static (rendered from the deterministic ledgers) and 17 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 32 rules run, 0 error(s), 0 warning(s); skipped by charter knob: MENT-03, SCOPE-01, OUT-01, AFF-01, AFF-02, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score ashcombe-advisory --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

79 authored documents, 30922 words, mean 391.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0008 | engagement_email | 74 | 250 | 0.30 |
| d:0005 | engagement_email | 83 | 250 | 0.33 |
| d:0080 | engagement_email | 93 | 250 | 0.37 |
| d:0078 | engagement_email | 101 | 250 | 0.40 |
| d:0006 | engagement_email | 105 | 250 | 0.42 |
| d:0049 | engagement_email | 114 | 250 | 0.46 |
| d:0083 | engagement_email | 114 | 250 | 0.46 |
| d:0013 | engagement_email | 117 | 250 | 0.47 |
| d:0011 | engagement_email | 118 | 250 | 0.47 |
| d:0079 | engagement_email | 119 | 250 | 0.48 |
| d:0084 | engagement_email | 119 | 250 | 0.48 |
| d:0066 | engagement_email | 131 | 250 | 0.52 |
| d:0070 | engagement_email | 132 | 250 | 0.53 |
| d:0082 | engagement_email | 135 | 250 | 0.54 |
| d:0012 | engagement_email | 144 | 250 | 0.58 |
| d:0068 | engagement_email | 147 | 250 | 0.59 |
| d:0010 | engagement_email | 153 | 250 | 0.61 |
| d:0065 | engagement_email | 155 | 250 | 0.62 |
| d:0053 | engagement_email | 156 | 250 | 0.62 |
| d:0081 | engagement_email | 156 | 250 | 0.62 |
| d:0036 | onboarding_record | 281 | 450 | 0.62 |
| d:0051 | engagement_email | 157 | 250 | 0.63 |
| d:0067 | engagement_email | 161 | 250 | 0.64 |
| d:0028 | onboarding_record | 298 | 450 | 0.66 |
| d:0047 | engagement_email | 181 | 250 | 0.72 |
| d:0060 | onboarding_record | 332 | 450 | 0.74 |
| d:0009 | briefing_deck | 296 | 400 | 0.74 |
| d:0034 | onboarding_record | 337 | 450 | 0.75 |

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0002 | d:0045 | engagement_letter | 0.1586 |

### Structural similarity

The 10 strongest of 682 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0048 | d:0071 | engagement_email | 1.0 | 0.8 | 0.0 |
| d:0006 | d:0012 | engagement_email | 0.8 | 0.8 | 0.0126 |
| d:0048 | d:0050 | engagement_email | 1.0 | 0.6 | 0.0106 |
| d:0048 | d:0069 | engagement_email | 0.8 | 0.8 | 0.0026 |
| d:0050 | d:0071 | engagement_email | 1.0 | 0.6 | 0.0 |
| d:0067 | d:0069 | engagement_email | 0.8 | 0.8 | 0.0056 |
| d:0069 | d:0071 | engagement_email | 0.8 | 0.8 | 0.0 |
| d:0008 | d:0013 | engagement_email | 0.8889 | 0.6667 | 0.0 |
| d:0078 | d:0084 | engagement_email | 0.8889 | 0.6667 | 0.0 |
| d:0019 | d:0062 | internal_email | 1.0 | 0.5 | 0.013 |

682 pairs were scored; the artifact keeps the strongest 50 and this table shows the top 10. The full ranking is recomputable from committed DocIR (`orgsmith.review.structure.compute_pairs`); it is truncated here rather than dropped silently.

### Fee coverage

6 documented engagement(s), fees totalling $346,000, against $31,974,000 of lifetime revenue.

Documented fees are 1.1% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 79 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 0 | 0 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 5 | 4 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Numbers no ledger owns

0 number(s) in authored prose that no ledger value accounts for, across 0 of 79 documents (distinct values per document; values under 10 and years not counted). The airlock keeps the model from transcribing a value the ledger owns; it does not keep it from inventing one, and an invented number is one the answer key cannot score. A measurement, never a gate.

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:amy.carter | 3 | 0.0040 (0.0010-0.0087) | 0.0007 | 0.0058 |
| p:christopher.walton | 2 | 0.0040 (0.0040-0.0040) | 0.0004 | 0.0040 |
| p:daniel.valenzuela | 7 | 0.0034 (0.0000-0.0215) | 0.0008 | 0.0086 |
| p:john.macias | 7 | 0.0014 (0.0000-0.0118) | 0.0007 | 0.0010 |
| p:julie.hill | 28 | 0.0055 (0.0000-0.1586) | 0.0005 | 0.0852 |
| p:kimberly.le | 1 | - | 0.0002 | - |
| p:laura.bradley | 6 | 0.0012 (0.0000-0.0051) | 0.0008 | 0.0051 |
| p:michael.morris | 16 | 0.0018 (0.0000-0.0282) | 0.0007 | 0.0067 |
| p:michelle.black | 2 | 0.0105 (0.0105-0.0105) | 0.0008 | 0.0105 |
| p:michelle.rose | 6 | 0.0029 (0.0000-0.0090) | 0.0005 | 0.0027 |
| p:sandra.mcdonald | 1 | - | 0.0004 | - |

### Review board

45 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:cross_document_voice-1 | cross_document_voice | major | d:0004, d:0021, d:0040, d:0047, d:0064, d:0077 | Six different engagement leads, 2017 to 2024, open their client threads with the same moves in the same order: the thread is declared the one place for status (five of six), then a 'where things stand' paragraph, then an ask for what is needed 'from your side' (usually counted), then a close of the form 'Once X, Y will Z'. |
| rf:docplaus-1 | document_plausibility | major | d:0009, d:0022, d:0038, d:0039, d:0040, d:0041, d:0042, d:0044, d:0055, d:0056 | No client document ever says what the client does or what happened to it: IR, media, positioning and crisis work is described with every concrete particular removed. |
| rf:docplaus-2 | document_plausibility | major | d:0004, d:0011, d:0013, d:0021, d:0040, d:0047, d:0053, d:0054, d:0064, d:0071, d:0077, d:0078, d:0083, d:0084 | Engagement threads are firm-only monologues: the client never writes a single message, two staff members strictly alternate on every thread, and they end up answering each other's questions to the client. |
| rf:docplaus-3 | document_plausibility | major | d:0003, d:0014, d:0015, d:0020, d:0034, d:0036, d:0042, d:0104 | Minutes, status reports, memos and onboarding records carry no date anywhere in the document; the date exists only in the filename. |
| rf:docplaus-4 | document_plausibility | major | d:0016, d:0019, d:0030, d:0033, d:0037, d:0057, d:0062, d:0087 | The 'mundane and constant' internal mailbox is exactly one email a year, every one dated in the first three days of July, so six of eight are about the Fourth of July. |
| rf:finance-1 | finance_realism | major | d:0018, d:0022, d:0024, d:0029, d:0038, d:0045, d:0061, d:0075 | Engagement fees do not follow the work. The nine-month investor relations program and the eight-month crisis engagement cost the same $46,500 to $47,000 as the four-month media program and reputation audit, while a five-month executive messaging project costs $102,000. |
| rf:graphacl-ash-1 | graph_acl_naturalness | major | d:0003, d:0007, d:0009, d:0015, d:0063, d:0072, d:0073 | Staff outside the engagement teams appear only where a two-mention floor put them: the Senior Advisor, Director of Operations and Office Manager are named together in the February 2017 Barrera kickoff and the March 2017 overview and almost nowhere else in eight years, and the standing roles those documents give them (and the one a 2023 kickoff gives Julie Bailey) leave no trace in any later document. |
| rf:graphacl-ash-2 | graph_acl_naturalness | major | d:0014, d:0041, d:0044, d:0055, d:0072, d:0085, d:0038, d:0039, d:0061, d:0063, d:0073, d:0023 | On five of six engagements the Managing Partner or Partner takes the minutes while associates and analysts sit in the room, and the junior lead writes the kickoff memo and the client status report even where the engagement letter says the senior leads the work, so who does what runs upside down. |
| rf:graphacl-ash-3 | graph_acl_naturalness | major | d:0005, d:0047, d:0048, d:0050, d:0065, d:0078, d:0083 | The engagement mail is a two-person relay addressed to a client who never writes: none of the 34 authored engagement emails is from a client, every eight-message thread alternates strictly between the same two Ashcombe senders, and the approvals the threads exist to record happen off the thread. |
| rf:graphacl-ash-4 | graph_acl_naturalness | major | d:0003, d:0009, d:0014, d:0015, d:0020, d:0049, d:0071 | Every client is exactly one person, drawn from an operations and finance title pool, who is the sole approver of everything; in a corporate communications and IR practice no client ever has a named head of communications, IR officer, CEO or counsel, and the second contacts the graph holds for two of those clients never appear. |
| rf:org-1 | org_realism | major | d:0003, d:0014, d:0015, d:0020, d:0038, d:0046, d:0053, d:0061, d:0071, d:0072, d:0075 | In all six engagements the client's only counterpart is an operations or finance officer. None is a head of communications or investor relations, a CEO, or counsel, and no other client executive is ever named. As a result a Director of Operations approves positioning language, decides which figures go public, and takes reporters' calls. |
| rf:org-2 | org_realism | major | d:0018, d:0021, d:0022, d:0038, d:0041, d:0075, d:0085 | Three of the six clients have three-surname partnership names that read as law or accounting firms. Yet they operate as listed companies, with shareholder registers, transfer agents, analyst coverage, and quarterly investor updates. |
| rf:org-3 | org_realism | major | d:0003, d:0009, d:0014, d:0022, d:0039, d:0045, d:0052, d:0055 | No client's business is ever stated. In none of the six engagement folders does the reader learn what a client makes or sells, or where it operates. 'The sector' appears wherever a real file would name the industry and the peers. |
| rf:cross_document_voice-2 | cross_document_voice | minor | d:0003, d:0010, d:0020, d:0039, d:0052, d:0056, d:0063, d:0065, d:0067, d:0068, d:0073 | Five authors in three genres announce a count before the items ('three things', 'two things from your side'). It is the banned 'Two asks. First... Second...' opener coming back in different words. |
| rf:cross_document_voice-3 | cross_document_voice | minor | d:0003, d:0020, d:0039, d:0046, d:0063, d:0076 | All six kickoff memos, each by a different author, end the same way: they name the one item everything else waits on, then ask the team for additions or corrections before that item goes to the client contact. |
| rf:cross_document_voice-4 | cross_document_voice | minor | d:0015, d:0024, d:0029, d:0042, d:0056, d:0073, d:0086, d:0023, d:0027, d:0041, d:0044 | All seven status reports and three of the eight minutes open by stating, in nearly the same words, where they fall in the engagement ('at about the halfway point', 'at about its midpoint', 'in its later phase'), usually followed by 'on plan' or 'on schedule'. Eight authors write the same first sentence. |
| rf:cross_document_voice-5 | cross_document_voice | minor | d:0003, d:0014, d:0015, d:0063, d:0025, d:0034, d:0036, d:0028 | Other authors describe colleagues in the exact words of the foundation.json persona sheet, so the same stock epithet follows a person from document to document. It reads as if one writer were working from a character bible. |
| rf:cross_document_voice-6 | cross_document_voice | minor | d:0005, d:0010, d:0048, d:0051, d:0065, d:0066, d:0068, d:0070, d:0078, d:0006, d:0049, d:0079, d:0083 | In-thread replies use only two openers: 16 of the 28 replies in the four multi-message threads name the colleague's previous message in their first sentence, and 9 more start 'Thank you for ...'. All six reply authors use one or both. |
| rf:cross_document_voice-7 | cross_document_voice | minor | d:0005, d:0082, d:0057, d:0019, d:0087, d:0030 | The personas written as the corpus's outliers (Julie Hill's one-line replies, Christopher Walton's dry notes with no greeting, Kimberly Le's clipped fragments, Sandra Mcdonald's bodies of bare confirmations) all write the same complete, courteous paragraphs as everyone else. |
| rf:docplaus-10 | document_plausibility | minor | d:0019, d:0057, d:0062, d:0070 | Each person's greeting and sign-off is fixed regardless of audience or hour, so a team-lunch broadcast closes 'Sincerely' and an afternoon reply opens 'Good morning'. |
| rf:docplaus-5 | document_plausibility | minor | d:0007, d:0032, d:0059 | The firm overviews read as the recipe narrative rather than a prospect-facing pitch: they explain the internal kickoff memo and email workflow, introduce the office manager, and omit founding year, location, contact details and any career credentials. |
| rf:docplaus-6 | document_plausibility | minor | d:0059 | The 2023 overview names a crisis-communications client in marketing copy, the one category of client a communications advisory anonymizes. |
| rf:docplaus-7 | document_plausibility | minor | d:0002, d:0018, d:0038, d:0045, d:0061, d:0075 | The six engagement letters re-draft their legal boilerplate from scratch each time, with substantive terms drifting letter to letter, and not one names the governing state. |
| rf:docplaus-8 | document_plausibility | minor | d:0002, d:0018, d:0038, d:0045, d:0061, d:0075 | Every executed letter shows the client countersigning on the letter's own date, including two Sundays, although each letter asks the client to sign and return it. |
| rf:docplaus-9 | document_plausibility | minor | d:0014, d:0028, d:0041, d:0044, d:0055, d:0072, d:0085 | The most senior person in the room keeps the minutes, and the managing partner writes every personnel onboarding record, including one for an operations hire who reports to the Director of Operations. |
| rf:finance-2 | finance_realism | minor | d:0018, d:0038, d:0045, d:0075, d:0026, d:0074 | The four comparable fees fall by exactly $500 per engagement from 2018 to 2024 while the firm's revenue grows by about 40 percent, so the fees read as a counting sequence rather than a rate card. |
| rf:finance-3 | finance_realism | minor | d:0038, d:0039 | The crisis letter sells open-ended, after-hours crisis counsel of no fixed length for a fixed fee paid in equal monthly installments. A crisis firm would not sign those terms, and they cannot be invoiced as written. |
| rf:finance-4 | finance_realism | minor | d:0031, d:0035, d:0043, d:0041, d:0044 | Travel snaps back past its pre-pandemic level in 2021. The FY2021 summary shows the firm's highest travel spend to that point, 22 percent above 2019, in a year whose client sessions in the sample were held by video. |
| rf:finance-5 | finance_realism | minor | d:0001, d:0017, d:0026, d:0031, d:0035, d:0043, d:0058, d:0074 | Office & Facilities is identical to the dollar across consecutive years, three years at one figure and then four at the next. That reads as a budget plug, not an actual occupancy cost. |
| rf:graphacl-ash-5 | graph_acl_naturalness | minor | d:0037, d:0033, d:0016, d:0030, d:0007, d:0019 | Office mail is sent by whoever was drawn rather than by the people who hold the function: neither the Director of Operations nor Pamela Rojas, Office Manager throughout, sends any of the eight internal emails, and an Associate polices his Partner's timesheet. |
| rf:graphacl-ash-6 | graph_acl_naturalness | minor | corpus | The Leadership Team distribution list has one member, the Managing Partner, because lists are cut one per department; the firm's other Partner and its Director of Operations, who reports to her, are outside it. |
| rf:graphacl-ash-7 | graph_acl_naturalness | minor | corpus | The graph keeps the departed Communications Analyst employed: her works_at edge never closes, while the roster ends her employment in 2020 and the ACL and distribution lists treat her as gone. |
| rf:narr-1 | narrative_consistency | minor | d:0093, d:0094, d:0095, d:0021 | The three working drafts of the Castaneda, Adams and Davis kickoff memo are dated before the engagement began but already describe its start in the past tense, and the v3 copy is the one the client received. |
| rf:narr-2 | narrative_consistency | minor | d:0007, d:0032, d:0059 | The firm overview reverses its stated policy on naming clients between versions, and no version acknowledges the change. |
| rf:narr-3 | narrative_consistency | minor | d:0084, d:0078, d:0079, d:0080 | The last message in the Gallegos, Pope and Marsh thread proposes, as if new, a leadership-interview sequence and press conversations that earlier messages in the same thread had already settled or reported under way. |
| rf:narr-4 | narrative_consistency | minor | d:0028, d:0025 | Two onboarding records are written as if the hire had not yet arrived, although each is dated a week after that person's start date in the roster. |
| rf:org-4 | org_realism | minor | d:0002, d:0075, d:0018, d:0045, d:0025, d:0036, d:0060, d:0037, d:0061 | Staff keep the same title from 2017 to 2024. 'Communications Associate' is the title both of a long-tenured staff member who runs an engagement day to day and of three new hires onboarded in 2019, 2021 and 2023. |
| rf:org-5 | org_realism | minor | d:0028 | Both recorded title changes read wrong. One is a lateral move into a departed colleague's title. The other leaves the three-person Operations team with two Office Managers and no Client Coordinator. |
| rf:org-6 | org_realism | minor | d:0016, d:0033, d:0037, d:0087, d:0007 | Office logistics mail comes from the Managing Partner, an Associate and an Analyst. The Office Manager and the Director of Operations, whose job this is, write none of the firm's eight internal emails. |
| rf:org-7 | org_realism | minor | d:0007, d:0032, d:0059 | None of the three firm overviews names Michael Morris, the firm's second partner. The 2017 edition profiles the Senior Advisor, the Director of Operations and the Office Manager, and the 2020 and 2023 editions promise every client a partner. |
| rf:org-8 | org_realism | minor | d:0030, d:0057, d:0087 | The phone numbers in email signatures spread a single-office, 15-person firm across six metro area codes, including colleagues who share a lobby, a garage and a main phone line. Each signature carries one number and there is no office line. |
| rf:org-9 | org_realism | minor | d:0028, d:0030, d:0045 | Both Mc- surnames are capitalized 'Mcdonald' and 'Mcdaniel', a title-casing artifact that shows up even in the employee's own signature and file name. The two names also belong to near-namesakes: staff member Sandra Mcdonald and client contact Sandra Mcdaniel. |
| rf:cross_document_voice-8 | cross_document_voice | note | d:0048, d:0071, d:0006, d:0012, d:0008, d:0013, d:0002, d:0045 | The pairs the report flags read as personal habit or firm template rather than generator collapse, and sentence rhythm does vary believably by author. The shared voice in this corpus is in the rhetorical moves above, which none of the similarity metrics measure. |
| rf:finance-6 | finance_realism | note | d:0035 | No defect claimed: the overall P&L fits an 11- to 15-person communications and IR boutique, and the declared 2020 reads correctly. The defects above sit in the fee schedule and in individual expense lines, not in the firm's scale. |
| rf:graphacl-ash-8 | graph_acl_naturalness | note | d:0018, d:0038 | The ACL half of this dimension carries no signal on this org: the open posture gives all 15 current staff the identical 104-document grant and the departed analyst none, which is a common real small-firm setup but sits beside engagement letters that promise need-to-know access. |
