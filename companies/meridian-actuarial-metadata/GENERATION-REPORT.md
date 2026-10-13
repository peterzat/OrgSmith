# Generation report: meridian-actuarial

Derived artifact: re-emit with `python -m orgsmith report meridian-actuarial`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

72 documents planned; 63 carry authored prose.

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
| wo:foundation:0001 | claude-opus-5-5 | xhigh |

Model cost: 63 of 72 documents were authored by a model, across 14 work order(s).

The other 9 cost zero model tokens: 9 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 31 rules run, 0 error(s), 0 warning(s); skipped by charter knob: NOISE-01, MENT-03, SCOPE-01, OUT-01, AFF-01, AFF-02, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score meridian-actuarial --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

63 authored documents, 29834 words, mean 474.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0006 | engagement_email | 70 | 250 | 0.28 |
| d:0007 | engagement_email | 87 | 250 | 0.35 |
| d:0005 | engagement_email | 105 | 250 | 0.42 |
| d:0068 | engagement_email | 120 | 250 | 0.48 |
| d:0067 | engagement_email | 121 | 250 | 0.48 |
| d:0020 | engagement_email | 130 | 250 | 0.52 |
| d:0035 | engagement_email | 142 | 250 | 0.57 |
| d:0019 | engagement_email | 149 | 250 | 0.60 |
| d:0008 | engagement_email | 150 | 250 | 0.60 |
| d:0021 | engagement_email | 152 | 250 | 0.61 |
| d:0033 | engagement_email | 155 | 250 | 0.62 |
| d:0069 | engagement_email | 155 | 250 | 0.62 |
| d:0034 | engagement_email | 171 | 250 | 0.68 |
| d:0004 | engagement_email | 179 | 250 | 0.72 |

### Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.1306).

### Structural similarity

The 10 strongest of 329 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0005 | d:0007 | engagement_email | 1.0 | 0.5 | 0.0 |
| d:0028 | d:0042 | onboarding_record | 0.8333 | 0.6 | 0.0 |
| d:0032 | d:0033 | engagement_email | 0.9231 | 0.4706 | 0.0 |
| d:0014 | d:0043 | onboarding_record | 0.8333 | 0.5 | 0.0087 |
| d:0018 | d:0020 | engagement_email | 0.8889 | 0.4444 | 0.0084 |
| d:0019 | d:0021 | engagement_email | 0.8333 | 0.5 | 0.0314 |
| d:0020 | d:0022 | engagement_email | 0.8889 | 0.4444 | 0.0 |
| d:0028 | d:0061 | onboarding_record | 0.8333 | 0.5 | 0.0064 |
| d:0042 | d:0061 | onboarding_record | 0.8333 | 0.5 | 0.0048 |
| d:0066 | d:0068 | engagement_email | 0.8889 | 0.4444 | 0.003 |

329 pairs were scored; the artifact keeps the strongest 50 and this table shows the top 10. The full ranking is recomputable from committed DocIR (`orgsmith.review.structure.compute_pairs`); it is truncated here rather than dropped silently.

### Fee coverage

6 documented engagement(s), fees totalling $366,500, against $22,889,000 of lifetime revenue.

Documented fees are 1.6% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 63 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 0 | 0 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 12 | 11 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Numbers no ledger owns

29 number(s) in authored prose that no ledger value accounts for, across 10 of 63 documents (distinct values per document; values under 10 and years not counted). The airlock keeps the model from transcribing a value the ledger owns; it does not keep it from inventing one, and an invented number is one the answer key cannot score. A measurement, never a gate.

| doc | count | values |
| --- | ---: | --- |
| d:0040 | 6 | 20, 23, 41, 51, 67, 68 |
| d:0030 | 4 | 23, 27, 35, 41 |
| d:0056 | 4 | 23, 41, 51, 56 |
| d:0064 | 4 | 23, 25, 41, 56 |
| d:0009 | 3 | 23, 67, 68 |
| d:0016 | 2 | 23, 41 |
| d:0037 | 2 | 25, 35 |
| d:0044 | 2 | 23, 715 |
| d:0012 | 1 | 23 |
| d:0038 | 1 | 23 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:amanda.white | 1 | - | 0.0000 | - |
| p:david.sherman | 11 | 0.0021 (0.0000-0.0394) | 0.0009 | 0.0022 |
| p:jeffrey.ochoa | 6 | 0.0027 (0.0000-0.0173) | 0.0012 | 0.0051 |
| p:jennifer.johnson | 1 | - | 0.0001 | - |
| p:jennifer.vasquez | 8 | 0.0030 (0.0000-0.0222) | 0.0012 | 0.0050 |
| p:karen.harris | 5 | 0.0015 (0.0000-0.0045) | 0.0014 | 0.0039 |
| p:megan.dudley | 6 | 0.0060 (0.0000-0.0183) | 0.0009 | 0.0170 |
| p:michelle.banks | 3 | 0.0073 (0.0050-0.0097) | 0.0015 | 0.0097 |
| p:robert.lawrence | 22 | 0.0052 (0.0000-0.1306) | 0.0010 | 0.0564 |

### Review board

38 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:voice-1 | cross_document_voice | major | d:0003, d:0009, d:0016, d:0017, d:0025, d:0037, d:0040, d:0044, d:0052, d:0054, d:0060, d:0061, d:0065 | Every staff author restates the firm's three-part method in nearly the same sentence, in kickoff memos, status reports, minutes and onboarding records as well as letters and overviews, so the house rule reads as one writer's refrain rather than a practice the reports simply carry out. |
| rf:docplaus-1 | document_plausibility | major | corpus | Actuarial documents, which are normally full of numbers, contain none. Reconciliation emails, experience tabulations and a preliminary-results meeting give every count, rate and amount as a vague word, and the interim deliverables say up front that they contain no results. |
| rf:docplaus-2 | document_plausibility | major | d:0002, d:0016, d:0030, d:0044, d:0056, d:0064 | All six engagement letters leave out the terms an actuarial engagement letter exists to set: none gives a valuation or measurement date, none names the plan (d:0016 never says what kind of reserves it covers), and the governing-law clause never names a state. |
| rf:docplaus-3 | document_plausibility | major | d:0002, d:0010, d:0011, d:0012 | In the Howard and Sons deck, minutes and status report, the choice of mortality table is put to the client as its decision. For a 2016 single-employer funding valuation, the IRS prescribes that table. RP-2014/MP-2015 was a choice only for accounting figures, and the engagement letter excludes accounting work. |
| rf:docplaus-4 | document_plausibility | major | d:0004, d:0005, d:0006, d:0007, d:0008, d:0018, d:0019, d:0020, d:0021, d:0022, d:0032, d:0033, d:0034, d:0035, d:0036, d:0066, d:0067, d:0068, d:0069, d:0070 | Every engagement email thread is one-sided. Each has five messages that alternate between two firm staff, all addressed to the client, and the client's replies are referred to but never appear, either as messages or in the quoted text. |
| rf:graph-acl-1 | graph_acl_naturalness | major | d:0054, d:0016, d:0043, d:0052, d:0060, d:0072 | The firm's two actuaries split the book with no overlap: Jennifer Vasquez, who assigns and reviews every associate's work, can read none of the three engagements Robert Lawrence runs and is never named in them, so the second-actuary review the firm promises has no one able to open those files. |
| rf:graph-acl-2 | graph_acl_naturalness | major | d:0042, d:0045, d:0054 | The prose makes the Practice Manager the keeper of every engagement's letter, billing and file tracking, but the ACL gives Linda Hanna no read grant on any engagement document or financial summary, including the kickoff memo addressed to her. |
| rf:graph-acl-3 | graph_acl_naturalness | major | d:0017, d:0023, d:0025, d:0065, d:0071, d:0072 | Two associates outside the ledger team are put on a kickoff memo's To line with a substantive role, then never appear again in that engagement, and neither can read the folder that names them. |
| rf:graph-acl-4 | graph_acl_naturalness | major | d:0011, d:0018, d:0024, d:0035, d:0037, d:0066 | Each client is exactly one named person: all eight sets of minutes list the ledger team plus that one contact and nobody else, and when the firm asks a client for a second name it never arrives. |
| rf:narrative_consistency-1 | narrative_consistency | major | d:0009, d:0040, d:0054, d:0002, d:0030, d:0044, d:0056 | Every firm overview describes a practice built on public retirement systems, multiemployer funds and life insurers, but all four pension and retiree-benefit engagements on file are corporate plan-sponsor work that no overview offers. That includes the clients the overviews cite as examples. |
| rf:narrative_consistency-2 | narrative_consistency | major | d:0002, d:0010, d:0011, d:0012 | The Howard and Sons documents make the mortality table the client's largest open decision in a 2016 single-employer minimum-funding valuation. The engagement letter itself frames the funding assumptions as prescribed by law, and for that valuation the IRS did prescribe mortality. |
| rf:narrative_consistency-3 | narrative_consistency | major | d:0032, d:0033, d:0034, d:0036, d:0037, d:0038 | The Estes Group data thread contradicts itself on which year's file holds the renumbered records. The minutes and status report then close a first-year problem, and the most-recent-year departures, along with the layoff questions raised about them, drop out of the record. |
| rf:org_realism-1 | org_realism | major | d:0009, d:0040, d:0054, d:0002, d:0030, d:0044, d:0056 | The firm describes itself as a public-system, multiemployer and life-insurer practice, but none of its six engagements is for a public system or a multiemployer fund, and four are private single-employer corporate work that no overview lists as a service. |
| rf:org_realism-2 | org_realism | major | d:0017, d:0057, d:0065, d:0025, d:0060, d:0072, d:0037, d:0059, d:0071 | Who writes which engagement document runs against seniority: after 2016, associates and analysts issue the kickoff memos and client status reports that assign work to the lead actuary, while the Managing Actuary takes the minutes at every session he attends. |
| rf:voice-2 | cross_document_voice | minor | d:0011, d:0023, d:0037, d:0038, d:0048, d:0060, d:0071, d:0072 | Minutes, decks and status reports by six different authors open on the same pre-emptive disclaimer in the same slot and the same sentence frame ("no view was formed, and nothing here should be read as one"), a writer's fingerprint rather than the varied ways real colleagues hedge. |
| rf:voice-3 | cross_document_voice | minor | d:0002, d:0016, d:0030, d:0044, d:0056, d:0064 | The six engagement letters, all signed by Robert Lawrence, share one template but re-word its fixed legal terms every time, so the firm has no standard text for the clauses a real firm carries verbatim from letter to letter. |
| rf:docplaus-5 | document_plausibility | minor | d:0011, d:0024, d:0027, d:0037, d:0047, d:0049, d:0059, d:0071, d:0012, d:0025, d:0038, d:0048, d:0060, d:0072, d:0003, d:0017, d:0031, d:0045, d:0057, d:0065 | Minutes, status reports and kickoff memos carry no date in the document itself. The meeting date, report date or memo date appears only in the filename. |
| rf:docplaus-6 | document_plausibility | minor | d:0005, d:0007, d:0019, d:0021, d:0069 | Some senders open with 'Good morning' whatever time the email went out, including late in the afternoon. |
| rf:docplaus-7 | document_plausibility | minor | d:0002 | The Howard and Sons letter says counsel will sign the signature page, but the page is signed by the Managing Actuary and the client's Director of Operations. |
| rf:docplaus-8 | document_plausibility | minor | d:0040, d:0054 | The 2019 and 2022 firm overviews spend more words explaining their rule for naming clients than naming them, which reads like the generator explaining its own constraint rather than marketing copy. |
| rf:docplaus-9 | document_plausibility | minor | d:0044, d:0045, d:0065, d:0012, d:0038 | Several formal documents are dated on weekends or a federal holiday. The recipe's business calendar covers mail, meetings and engagement starts, but not these documents. |
| rf:finance_realism-1 | finance_realism | minor | d:0041, d:0050, d:0053, d:0055, d:0063, d:0043, d:0051, d:0052, d:0037, d:0047, d:0049 | Travel returns to above its pre-pandemic level in FY2021 and is twice that level by FY2023, while the firm's own records show it working from home into late 2021 and holding its client sessions by call or video. |
| rf:finance_realism-2 | finance_realism | minor | d:0044, d:0045, d:0047, d:0048, d:0002 | The Martinez LLC retiree medical valuation is priced at $118,500. That is the largest fee in the book and nearly four times the pension valuation, for a client small enough that its General Manager gathers the data himself. |
| rf:finance_realism-3 | finance_realism | minor | d:0001, d:0013, d:0026, d:0029, d:0041, d:0050, d:0053, d:0055, d:0063 | Office & Facilities is identical to the dollar for four consecutive years, twice. The occupancy line reads as a step function, not as a rent bill that also carries escalations, utilities and repairs. |
| rf:graph-acl-5 | graph_acl_naturalness | minor | d:0017, d:0025, d:0057, d:0060, d:0072 | Who writes an engagement's kickoff memo and client status report follows the order of the ledger's participant list rather than seniority, so associates issue the client report with the signing actuary credited last. |
| rf:graph-acl-6 | graph_acl_naturalness | minor | d:0015, d:0051, d:0062 | Office administration mail comes from analysts and associates while a Practice Manager is employed, and neither Practice Manager sends a single email in nine years. |
| rf:graph-acl-7 | graph_acl_naturalness | minor | d:0014, d:0028, d:0039, d:0051 | The ACL's open bucket makes personnel-file records and one-to-one mail readable by all eleven current staff, while engagement files are limited to three or four people and the financial summaries to one. |
| rf:narrative_consistency-4 | narrative_consistency | minor | d:0042, d:0009, d:0003 | Linda Hanna's onboarding record presents the Practice Manager job as a new role created by growth. That erases Carol Cooper, who held the same title and duties for more than five years and left weeks before Hanna started. |
| rf:narrative_consistency-5 | narrative_consistency | minor | d:0064, d:0066, d:0067, d:0069, d:0071, d:0072 | The ceded-premium discrepancy that takes up four of the five Gonzalez, Campbell and Kelly emails never appears again. The later documents also move from in-force treaty premiums to a reinsurer's proposed rate schedule without any document recording the change. |
| rf:org_realism-3 | org_realism | minor | d:0042, d:0009, d:0003 | Linda Hanna's onboarding record presents the Practice Manager role as newly needed, although Carol Cooper held that title and those duties from 2014 until five weeks before Hanna started, and no document mentions Cooper leaving or Hanna replacing her. |
| rf:org_realism-4 | org_realism | minor | d:0002, d:0012, d:0016, d:0044, d:0064 | The client side does not look like the people who commission actuarial work: five of six counterparts are operations generalists, and the two insurance clients carry names in the style of law partnerships. |
| rf:org_realism-5 | org_realism | minor | d:0004, d:0005, d:0015, d:0051 | The firm works out of one office suite, but its staff's email signatures carry phone numbers in five metro area codes, which suggests a multi-office firm. |
| rf:org_realism-6 | org_realism | minor | d:0009, d:0054, d:0002 | No firm overview ever names Jennifer Vasquez, the firm's only other actuary and every client's day-to-day contact, and the 2016 overview introduces the Practice Manager in her place, so the firm reads as a two-person shop. |
| rf:voice-4 | cross_document_voice | note | d:0003, d:0019, d:0020, d:0025, d:0036, d:0045, d:0066, d:0067, d:0069, d:0070 | The persona surface layer holds: greetings, closings, list-versus-paragraph habit and sentence length differ by author and persist across years, and the structural pairs the report flags read as personal habit or inherited template, not collapse; the one-writer signal sits beneath that surface, in rf:voice-1 and rf:voice-2. |
| rf:docplaus-10 | document_plausibility | note | corpus | The details that place each document in its year hold up throughout, and they are this corpus's strongest feature. |
| rf:docplaus-11 | document_plausibility | note | d:0005, d:0006, d:0007, d:0020, d:0068 | The engagement emails the length metric flags as short (28-72% of brief) read as the right length for mid-thread data questions. Here the 250-word target is off, not the emails. |
| rf:graph-acl-8 | graph_acl_naturalness | note | d:0042, d:0045, d:0061, d:0065 | The recipe's same-surname case never appears in the corpus: no document names both Linda Hanna and Nicole Hanna. |
| rf:narrative_consistency-6 | narrative_consistency | note | d:0011, d:0038, d:0049, d:0040, d:0054, d:0045, d:0043, d:0051, d:0052 | Dated references to tables, standards and events are accurate to each document's date, and titles and overview client citations match the roster and engagement dates. The anachronism half of this dimension came up clean. |
