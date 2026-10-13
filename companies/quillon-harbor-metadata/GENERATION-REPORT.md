# Generation report: quillon-harbor

Derived artifact: re-emit with `python -m orgsmith report quillon-harbor`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

77 documents planned; 59 carry authored prose.

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
| wo:author:0016 | claude-opus-5-5 | xhigh |
| wo:author:0017 | claude-opus-5-5 | xhigh |
| wo:author:0018 | claude-opus-5-5 | xhigh |
| wo:author:0019 | claude-opus-5-5 | xhigh |
| wo:foundation:0001 | claude-opus-5-5 | xhigh |

Model cost: 59 of 77 documents were authored by a model, across 20 work order(s).

The other 18 cost zero model tokens: 10 static (rendered from the deterministic ledgers) and 8 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 31 rules run, 0 error(s), 0 warning(s); skipped by charter knob: AFF-01, AFF-02, EML-01, EML-02, EML-03, DL-01, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score quillon-harbor --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

59 authored documents, 37310 words, mean 632.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0027 | onboarding_record | 309 | 450 | 0.69 |
| d:0005 | onboarding_record | 323 | 450 | 0.72 |
| d:0026 | onboarding_record | 326 | 450 | 0.72 |
| d:0028 | onboarding_record | 331 | 450 | 0.74 |
| d:0019 | onboarding_record | 336 | 450 | 0.75 |

### Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.0692).

### Structural similarity

The 10 strongest of 245 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0020 | d:0064 | engagement_letter | 0.9048 | 0.6316 | 0.0591 |
| d:0011 | d:0058 | engagement_letter | 0.92 | 0.5833 | 0.0305 |
| d:0011 | d:0064 | engagement_letter | 0.8261 | 0.5116 | 0.0247 |
| d:0027 | d:0042 | onboarding_record | 0.75 | 0.5714 | 0.0124 |
| d:0042 | d:0048 | onboarding_record | 0.75 | 0.5714 | 0.0062 |
| d:0002 | d:0011 | engagement_letter | 0.7755 | 0.5385 | 0.0321 |
| d:0002 | d:0058 | engagement_letter | 0.8235 | 0.4815 | 0.0599 |
| d:0058 | d:0064 | engagement_letter | 0.8333 | 0.4444 | 0.0354 |
| d:0020 | d:0051 | engagement_letter | 0.8636 | 0.4 | 0.0524 |
| d:0002 | d:0064 | engagement_letter | 0.6809 | 0.5714 | 0.0319 |

245 pairs were scored; the artifact keeps the strongest 50 and this table shows the top 10. The full ranking is recomputable from committed DocIR (`orgsmith.review.structure.compute_pairs`); it is truncated here rather than dropped silently.

### Fee coverage

8 documented engagement(s), fees totalling $666,000, against $54,129,000 of lifetime revenue.

Documented fees are 1.2% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 59 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 0 | 0 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 13 | 8 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 2 | 2 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Numbers no ledger owns

3 number(s) in authored prose that no ledger value accounts for, across 1 of 59 documents (distinct values per document; values under 10 and years not counted). The airlock keeps the model from transcribing a value the ledger owns; it does not keep it from inventing one, and an invented number is one the answer key cannot score. A measurement, never a gate.

| doc | count | values |
| --- | ---: | --- |
| d:0020 | 3 | 11, 13, 17 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:angela.cole | 3 | 0.0012 (0.0000-0.0036) | 0.0008 | 0.0029 |
| p:heather.delacruz | 27 | 0.0057 (0.0000-0.0692) | 0.0008 | 0.0494 |
| p:john.bauer | 2 | 0.0164 (0.0164-0.0164) | 0.0012 | 0.0164 |
| p:kelly.brown | 2 | 0.0007 (0.0007-0.0007) | 0.0013 | 0.0007 |
| p:mark.allen | 4 | 0.0050 (0.0000-0.0152) | 0.0008 | 0.0027 |
| p:melissa.jacobson | 3 | 0.0090 (0.0038-0.0133) | 0.0006 | 0.0086 |
| p:rachel.brown | 4 | 0.0034 (0.0000-0.0073) | 0.0009 | 0.0025 |
| p:richard.mccoy | 4 | 0.0091 (0.0037-0.0228) | 0.0012 | 0.0067 |
| p:robert.turner | 3 | 0.0041 (0.0032-0.0052) | 0.0012 | 0.0058 |
| p:sandra.norman | 3 | 0.0085 (0.0044-0.0119) | 0.0010 | 0.0076 |
| p:thomas.mccoy | 4 | 0.0132 (0.0021-0.0571) | 0.0011 | 0.0042 |

### Review board

47 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:fin-1 | finance_realism | blocker | d:0002, d:0008, d:0012, d:0040, d:0045, d:0058, d:0062 | No mandate in this M&A firm's ten-year book carries a success fee. A full two-round sell-side auction, a carve-out sale and a growth equity raise are each priced as one flat fee of $39,000 to $71,500, which is roughly a few months of a lower-middle-market retainer and nothing at closing. |
| rf:voice-1 | cross_document_voice | major | d:0013, d:0052, d:0021, d:0059, d:0003, d:0041 | Kickoff memos on the same outline, written by different people years apart, open their paragraphs with the same sentences, mostly the outline's slot wording turned into topic sentences, so they read as one writer filling in one form. |
| rf:voice-2 | cross_document_voice | major | d:0016, d:0036, d:0062, d:0012, d:0038 | Status reports by four different authors on four engagements share sentences that go beyond what their outlines prescribe, including one telling the client that the counts are independent measures, which restates the authoring brief and is nothing a client needs to hear. |
| rf:voice-3 | cross_document_voice | major | corpus | The firm's confidentiality convention is restated in 28 of 59 authored documents by 8 of 11 authors, nearly always in the charter's words 'sector and revenue band', including minutes and status reports where nothing calls for it, so it reads as a slogan the writer was told to carry, not a practice the firm simply follows. |
| rf:docplaus-1 | document_plausibility | major | d:0002, d:0011, d:0020, d:0032, d:0040, d:0051, d:0058, d:0064 | All eight engagement letters avoid naming their governing law, and the firm has no address anywhere in the corpus, so no letter says where the firm or the client is. |
| rf:docplaus-2 | document_plausibility | major | d:0002, d:0040, d:0058 | The sell-side, carve-out and growth-capital letters have no transaction or success fee, the clause that defines an M&A engagement letter, yet two of them carry tail provisions that only make sense for a contingent fee. |
| rf:docplaus-3 | document_plausibility | major | d:0004, d:0066, d:0068, d:0006 | Two firm overviews name a client whose confidential mandate is still live, which an M&A advisor's marketing material never does, and one does it on the same page that promises targets are named only in privileged documents. |
| rf:docplaus-4 | document_plausibility | major | d:0007, d:0010, d:0015, d:0017, d:0023, d:0035, d:0037, d:0044, d:0046, d:0054, d:0061, d:0067, d:0069, d:0062, d:0068, d:0021, d:0059 | No Word document in the corpus states its own date: none of the 13 sets of minutes records when the meeting was held, no status report is dated, memo headers carry To/From/Re with no Date, and two kickoff memos have no header at all. |
| rf:docplaus-5 | document_plausibility | major | d:0013, d:0041, d:0052, d:0059, d:0065, d:0068 | Memos and client reports refer to their own addressees in the third person by full name, which reads as a mention quota rather than someone writing to a colleague. |
| rf:docplaus-6 | document_plausibility | major | d:0016, d:0029, d:0036, d:0048, d:0049, d:0062, d:0066 | The generator's own consistency rules surface as in-world content: firm overviews market cross-document count reconciliation, status reports disclaim any relation between their own funnel counts, and a new analyst's first task is reconciling counts across documents. |
| rf:docplaus-7 | document_plausibility | major | d:0002, d:0003, d:0006, d:0007, d:0012 | The Armstrong, Silva and Dyer sale is described as a short, deliberate list and not an auction, while its own documents show a 145-party universe, 103 contacts and 14 final bids. |
| rf:fin-2 | finance_realism | major | d:0009, d:0063, d:0002, d:0040, d:0064 | Taken as the firm's real prices, the documented fees imply an impossible deal count against its own P&L. The fees also do not track scope: the most work-heavy sale in the book is its cheapest mandate. |
| rf:fin-3 | finance_realism | major | d:0001, d:0009, d:0018, d:0025, d:0031, d:0039, d:0047, d:0050, d:0057, d:0063, d:0062, d:0068 | Revenue moves like a subscription business, not an advisory firm paid on a handful of closings. Outside the declared 2020 shock, growth is 7-9% every year and no quarter strays more than about 20% from its year's average, including record years the firm's own reports describe as a tightening market. |
| rf:graph-1 | graph_acl_naturalness | major | d:0003, d:0030, d:0033, d:0034, d:0044, d:0046, d:0059, d:0061, d:0062 | Five juniors are each given a named, substantive deal role in one engagement document and then drop out of the mandate with no handoff. None of them is on the ledger team, and none can read the folder of the document that names them. |
| rf:graph-2 | graph_acl_naturalness | major | d:0026, d:0029, d:0042, d:0030, d:0056 | The prose makes the Compliance Manager the reviewer of every mandate's paperwork and the person who controls folder access, yet she holds no read grant on any engagement document. |
| rf:graph-3 | graph_acl_naturalness | major | d:0019, d:0027, d:0030, d:0051 | Every Advisory employee reports to Mark Allen, and the onboarding records have him choosing each analyst's mandates and reviewing their models. He can read two of the eight engagement folders, and the fairness-opinion committee the Hamilton letter promises has no member outside the team who can read the file. |
| rf:graph-4 | graph_acl_naturalness | major | corpus | Each client is exactly one named person. Across the 45 authored engagement documents, the owners, shareholders, counsel, controllers and lenders the deals turn on are never named, and every set of minutes lists the full ledger team plus that one contact. |
| rf:graph-5 | graph_acl_naturalness | major | d:0066, d:0068, d:0069 | The 2023 firm overview, which all staff can read and which is written for prospective clients, names Ingram, Bowers and Roth as a client while its strategic alternatives review is still running. The Ingram file itself limits knowledge of the review to one officer and the shareholders. |
| rf:narrative-1 | narrative_consistency | major | d:0002, d:0003, d:0006, d:0007 | The Armstrong sell-side documents call the buyer list short, deliberate and not an auction, but the figures beside that language are a 145-name universe, 103 parties contacted and 14 final bids, which is a broad auction. The authors were briefed the scope only as a placeholder and characterized a number they never saw. |
| rf:narrative-2 | narrative_consistency | major | d:0004, d:0003, d:0006, d:0007, d:0066, d:0068 | Two firm overviews name live, confidential mandates as client examples. The same documents say a target is named only in privileged material, and the engagement files describe those mandates as secret even from the clients' own staff. |
| rf:org_realism-1 | org_realism | major | d:0005, d:0051, d:0054, d:0019, d:0027, d:0060, d:0061, d:0062, d:0064 | The analyst title never moves: analysts onboarded in 2014, 2016 and 2017 are still introduced to clients as Analysts five to seven years later, listed beside a six-week hire with the same title, at a firm type where the analyst seat is a two-to-three-year rung. |
| rf:org_realism-2 | org_realism | major | d:0004, d:0003, d:0007, d:0066, d:0068 | A firm that calls confidentiality 'a way of writing' names live, secret mandates in its own marketing overview: the 2014 overview showcases a sell-side one month in whose owners have not told their employees, and the 2023 overview lists a strategic review two months into its term. |
| rf:org_realism-3 | org_realism | major | d:0021, d:0041, d:0044, d:0026, d:0066 | The client book reads as a list of law firms: five of eight clients, all operating companies, carry the 'Surname, Surname and Surname' style of a professional partnership, two carry the British public-company suffix 'PLC', and the surnames overlap the firm's own staff and each other. |
| rf:voice-4 | cross_document_voice | minor | d:0002, d:0017, d:0027, d:0028, d:0049, d:0067 | Business records describe colleagues using the roster's persona sketches nearly word for word, in a novelist's register, so engagement letters, client-session minutes and first-week onboarding notes share one all-knowing narrator who already knows everyone's habits. |
| rf:voice-5 | cross_document_voice | minor | d:0005, d:0019, d:0026, d:0027, d:0028, d:0030, d:0042, d:0048, d:0056, d:0060 | All ten onboarding records carry the Managing Partner's byline (she is the author of 27 of 59 authored documents), yet nine refer to her in the third person and one in the first, so the series reads as an office voice that does not match its byline. |
| rf:docplaus-10 | document_plausibility | minor | d:0002, d:0004, d:0029, d:0026, d:0027, d:0028, d:0017, d:0067 | Persona sketches are transcribed into genres that would not carry them: an engagement letter, firm overviews, first-week onboarding records and minutes describe colleagues' habits. |
| rf:docplaus-11 | document_plausibility | minor | d:0002, d:0011, d:0020, d:0032, d:0040, d:0051, d:0058, d:0064, d:0026 | The eight executed engagement letters share no standard terms: each rewords its liability, confidentiality and governing-law clauses and retitles their headings, although the firm is said to keep a standard engagement letter. |
| rf:docplaus-12 | document_plausibility | minor | d:0008, d:0012, d:0016, d:0024, d:0036, d:0038, d:0045, d:0055, d:0062, d:0068, d:0004, d:0029, d:0049, d:0066 | Every status report file is named 'v2 FINAL' and every firm overview 'v3', a version suffix stamped per genre rather than one that accumulated per document. |
| rf:docplaus-8 | document_plausibility | minor | d:0013, d:0016, d:0045, d:0059, d:0062, d:0065 | Analysts are the authors of record on client status reports and on kickoff memos that set strategy and direct partners, and those documents do not read like an analyst's draft. |
| rf:docplaus-9 | document_plausibility | minor | d:0008, d:0012, d:0016, d:0024, d:0036, d:0038, d:0045, d:0055, d:0062, d:0068, d:0006, d:0043 | Every status report restates the advisor's own fixed fee as an engagement budget, and two client decks list the engagement start date as a measure; both are planted facts given a slot no M&A report has. |
| rf:fin-4 | finance_realism | minor | d:0008, d:0012, d:0016, d:0024, d:0036, d:0038, d:0045, d:0055, d:0062, d:0068 | All ten client status reports restate the advisor's own fee as a budget line held steady. That is how a fixed-price consultancy reports budget burn. An M&A advisor reporting to a selling owner reports the process, not its fee. |
| rf:fin-5 | finance_realism | minor | d:0001, d:0009, d:0018, d:0025, d:0031, d:0039, d:0047, d:0050, d:0057, d:0063 | Every financial summary books the M&A firm's only revenue line as "Consulting revenue". An advisory boutique's books show advisory or transaction fees, usually split between retainers and success fees. |
| rf:fin-6 | finance_realism | minor | d:0032 | In the management buyout, the company owned by the selling shareholders pays, reimburses and indemnifies the buyers' advisor, under a letter its CFO signs while he is one of the buyers. |
| rf:graph-6 | graph_acl_naturalness | minor | d:0004, d:0029, d:0049, d:0066 | The firm overviews seem to name whoever needed a mention rather than the firm's leaders: the 2014 overview profiles a junior analyst and the chief of staff, and in ten years no overview names either of the other two partners. |
| rf:graph-7 | graph_acl_naturalness | minor | d:0030, d:0032, d:0033, d:0044, d:0021 | Name collisions fall exactly where a firm this focused on conflicts would comment, and nobody comments. An analyst named Duffy joins two weeks into the Browning, Duffy and Santos mandate and sits in its client session, and two Mccoys staff the same three-person team. |
| rf:narrative-3 | narrative_consistency | minor | d:0020, d:0023, d:0024 | The Lawson recapitalization status report puts the final funnel stage (all four term sheets in hand, first round closed) five business days after the first lender call. The engagement letter allots outreach weeks 8 to 11 and proposals weeks 11 to 13, which works out to mid-September to early October. The prose explains the gap rather than fitting the calendar, and it leaves 28 of the 46 approved sources unapproached without saying so. |
| rf:narrative-4 | narrative_consistency | minor | d:0074, d:0075, d:0023, d:0024 | Both earlier versions in the d:0024 version chain are dated before the events their text reports. The noise stage dates chain members 2 to 7 days apart, counting back from the final, and copies the final's time-anchored text into them unchanged. |
| rf:org_realism-4 | org_realism | minor | d:0013, d:0016, d:0045, d:0064, d:0065, d:0068 | On three of eight engagements the most junior person on the team writes both the kickoff work plan that assigns the partners their roles and the status report that goes to the client, although an associate or director sits on the same team. |
| rf:org_realism-5 | org_realism | minor | d:0020, d:0023 | The advisory group runs two titles for one rung: the same letter introduces 'an Associate' and 'an Advisory Associate' with no difference in role, and only the plain Associate is ever promoted. |
| rf:org_realism-6 | org_realism | minor | d:0002, d:0010, d:0012, d:0023, d:0064, d:0069 | The founders and shareholders who make every decision never appear: on the sell-side, recapitalization, growth raise and strategic review, the client is a single finance or operations officer who signs the letter and sits in every meeting, while 'the owners' remain an unnamed offstage group. |
| rf:org_realism-7 | org_realism | minor | d:0002, d:0011, d:0020, d:0032, d:0040, d:0051, d:0058, d:0064, d:0004, d:0029, d:0049, d:0066 | The firm has no home: no overview, letterhead or letter names a city or state, all eight engagement letters set governing law by the circumlocution 'the state in which our principal office is located', and the roster scatters a one-office firm across six metro area codes. |
| rf:org_realism-8 | org_realism | minor | d:0011, d:0032, d:0033, d:0021 | A partner's surname is printed 'Mccoy' rather than 'McCoy' in all 22 documents that name him, including letters the Managing Partner signs, and a same-surname partner and associate share a two-banker deal team without a word about it. |
| rf:voice-6 | cross_document_voice | note | corpus | Sentence rhythm does differ by author, and the outline pool varied the headings, so the convergence in rf:voice-1 to rf:voice-3 lies in rhetorical moves and refrains, not rhythm; the metric's top structural pairs are the Managing Partner's own letters and onboarding notes, and they read as one signatory reusing her templates, which is plausible. |
| rf:docplaus-13 | document_plausibility | note | d:0033, d:0034, d:0037, d:0051, d:0048, d:0062 | Deal mechanics and era detail are accurate and are the corpus's strongest feature; the defects above sit in framing, furniture and planted-fact slots, not in the substance of the work. |
| rf:fin-7 | finance_realism | note | d:0011, d:0034, d:0051, d:0064, d:0069 | No defect claimed. Where a flat fee is the industry norm, the prose prices and papers it correctly, and era-specific financial detail is accurate. The fee defects above therefore trace to the ledger, not to the authors. |
| rf:narrative-5 | narrative_consistency | note | corpus | Era references and in-text titles were checked across all 59 sampled documents and are consistent. Every name-and-title pairing matches the person's title history at the document date. The analyst who departed in 2017 is never mentioned afterward. No tool, idiom or event postdates its document. |
| rf:org_realism-9 | org_realism | note | d:0011, d:0032, d:0003, d:0020 | No defect: every engagement team includes the Managing Partner or a Partner, and every dated title in the prose matches the person's title history on that date. |
