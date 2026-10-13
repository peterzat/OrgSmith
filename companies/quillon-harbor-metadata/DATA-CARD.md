# Data card: `quillon-harbor`

**Quillon Harbor Advisors LLC** (mergers and acquisitions advisory), founded 2012.

Derived from committed state by `python -m orgsmith data-card quillon-harbor`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **77 documents**: 59 model-authored, 10 deterministic, 8 derived.
- **Formats**: 52 `.docx`, 8 `.pdf`, 7 `.pptx`, 10 `.xlsx`.
- **Document dates**: 2014-01-15 to 2023-11-28.
- **Charter window**: 2014-01-01 to 2023-12-31.

## Feature matrix

Every capability knob in this org's recipe, with its value. A knob that is off is off by choice, and the validator skips its rule visibly rather than passing it silently.

| knob | value |
| --- | --- |
| `doc_culture` | `on` |
| `doc_culture.scanned_ratio` | `0.0` |
| `doc_culture.legacy_ratio` | `0.0` |
| `doc_culture.ocr_layer_rate` | `0.0` |
| `doc_culture.business_calendar` | `on` |
| `doc_culture.business_calendar.engagement_starts` | `True` |
| `doc_culture.noise` | `on` |
| `doc_culture.noise.duplicates` | `2` |
| `doc_culture.noise.drafts` | `2` |
| `doc_culture.noise.version_chains` | `1` |
| `doc_culture.noise.misfiled` | `1` |
| `doc_culture.noise.stale_templates` | `1` |
| `doc_culture.noise.empty_dirs` | `2` |
| `doc_culture.noise.attachment_mismatch` | `0` |
| `doc_culture.noise.filename_variety` | `True` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `off` |
| `doc_culture.style_specs` | `True` |
| `doc_culture.client_facing_reports` | `True` |
| `doc_culture.outline_variety` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `3200000` |
| `finance.growth_rate` | `0.08` |
| `finance.expense_ratio` | `0.78` |
| `engagements` | `on` |
| `engagements.count` | `8` |
| `engagements.book_is_sample` | `True` |
| `engagements.scope` | `on` |
| `engagements.scope.unit` | `candidate companies` |
| `engagements.scope.comparator` | `comparable transactions` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `8` |
| `graph_targets.external_people` | `8` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `1` |
| `graph_targets.nickname_aliases` | `1` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `graph_targets.alias_agreement` | `True` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `0` |
| `hard_cases.filename_dates` | `0` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `3` |
| `roster_churn.hires` | `8` |
| `acl_posture` | `departmental` |

## Questions

- **Retrieval**: 90 questions, of which 0 are unanswerable (correct response: abstain). 10 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:count` 33, `fact:date` 8, `fact:money` 8, `fact:text` 8, `firm` 1, `mention:alias` 1, `mention:person` 21, `workbook` 10.
- **Extraction**: 57 questions. Locations: `body` 57.
- Extraction difficulty tags: none (no scans, no legacy binaries).
- **Visibility**: 21 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 69 |
| `distractors` | 69 |
| `noise` | 77 |
| `full` | 77 |

**Distractor gap = 0.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `departmental`.
- **Grants**: 21, covering 0 to 77 documents each (median 22).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 3, covering 3 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

- **Value collision.** `f:E-2016-001.pipeline-term-sheets-received`'s surface "4 term sheets received" also appears in 1 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2018-001.fee`'s surface "$118,000" also appears in 2 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2022-001.pipeline-term-sheets-received`'s surface "4 term sheets received" also appears in 3 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2023-001.fee`'s surface "$118,000" also appears in 3 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.

The adversarial review board's findings against this org (47 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| blocker | `rf:fin-1` | No mandate in this M&A firm's ten-year book carries a success fee. A full two-round sell-side auction, a carve-out sale and a growth equity raise are each priced as one flat fee of $39,000 to $71,500, which is roughly a few months of a lower-middle-market retainer and nothing at closing. |
| major | `rf:docplaus-1` | All eight engagement letters avoid naming their governing law, and the firm has no address anywhere in the corpus, so no letter says where the firm or the client is. |
| major | `rf:docplaus-2` | The sell-side, carve-out and growth-capital letters have no transaction or success fee, the clause that defines an M&A engagement letter, yet two of them carry tail provisions that only make sense for a contingent fee. |
| major | `rf:docplaus-3` | Two firm overviews name a client whose confidential mandate is still live, which an M&A advisor's marketing material never does, and one does it on the same page that promises targets are named only in privileged documents. |
| major | `rf:docplaus-4` | No Word document in the corpus states its own date: none of the 13 sets of minutes records when the meeting was held, no status report is dated, memo headers carry To/From/Re with no Date, and two kickoff memos have no header at all. |
| major | `rf:docplaus-5` | Memos and client reports refer to their own addressees in the third person by full name, which reads as a mention quota rather than someone writing to a colleague. |
| major | `rf:docplaus-6` | The generator's own consistency rules surface as in-world content: firm overviews market cross-document count reconciliation, status reports disclaim any relation between their own funnel counts, and a new analyst's first task is reconciling counts across documents. |
| major | `rf:docplaus-7` | The Armstrong, Silva and Dyer sale is described as a short, deliberate list and not an auction, while its own documents show a 145-party universe, 103 contacts and 14 final bids. |
| major | `rf:fin-2` | Taken as the firm's real prices, the documented fees imply an impossible deal count against its own P&L. The fees also do not track scope: the most work-heavy sale in the book is its cheapest mandate. |
| major | `rf:fin-3` | Revenue moves like a subscription business, not an advisory firm paid on a handful of closings. Outside the declared 2020 shock, growth is 7-9% every year and no quarter strays more than about 20% from its year's average, including record years the firm's own reports describe as a tightening market. |
| major | `rf:graph-1` | Five juniors are each given a named, substantive deal role in one engagement document and then drop out of the mandate with no handoff. None of them is on the ledger team, and none can read the folder of the document that names them. |
| major | `rf:graph-2` | The prose makes the Compliance Manager the reviewer of every mandate's paperwork and the person who controls folder access, yet she holds no read grant on any engagement document. |
| major | `rf:graph-3` | Every Advisory employee reports to Mark Allen, and the onboarding records have him choosing each analyst's mandates and reviewing their models. He can read two of the eight engagement folders, and the fairness-opinion committee the Hamilton letter promises has no member outside the team who can read the file. |
| major | `rf:graph-4` | Each client is exactly one named person. Across the 45 authored engagement documents, the owners, shareholders, counsel, controllers and lenders the deals turn on are never named, and every set of minutes lists the full ledger team plus that one contact. |
| major | `rf:graph-5` | The 2023 firm overview, which all staff can read and which is written for prospective clients, names Ingram, Bowers and Roth as a client while its strategic alternatives review is still running. The Ingram file itself limits knowledge of the review to one officer and the shareholders. |
| major | `rf:narrative-1` | The Armstrong sell-side documents call the buyer list short, deliberate and not an auction, but the figures beside that language are a 145-name universe, 103 parties contacted and 14 final bids, which is a broad auction. The authors were briefed the scope only as a placeholder and characterized a number they never saw. |
| major | `rf:narrative-2` | Two firm overviews name live, confidential mandates as client examples. The same documents say a target is named only in privileged material, and the engagement files describe those mandates as secret even from the clients' own staff. |
| major | `rf:org_realism-1` | The analyst title never moves: analysts onboarded in 2014, 2016 and 2017 are still introduced to clients as Analysts five to seven years later, listed beside a six-week hire with the same title, at a firm type where the analyst seat is a two-to-three-year rung. |
| major | `rf:org_realism-2` | A firm that calls confidentiality 'a way of writing' names live, secret mandates in its own marketing overview: the 2014 overview showcases a sell-side one month in whose owners have not told their employees, and the 2023 overview lists a strategic review two months into its term. |
| major | `rf:org_realism-3` | The client book reads as a list of law firms: five of eight clients, all operating companies, carry the 'Surname, Surname and Surname' style of a professional partnership, two carry the British public-company suffix 'PLC', and the surnames overlap the firm's own staff and each other. |
| major | `rf:voice-1` | Kickoff memos on the same outline, written by different people years apart, open their paragraphs with the same sentences, mostly the outline's slot wording turned into topic sentences, so they read as one writer filling in one form. |
| major | `rf:voice-2` | Status reports by four different authors on four engagements share sentences that go beyond what their outlines prescribe, including one telling the client that the counts are independent measures, which restates the authoring brief and is nothing a client needs to hear. |
| major | `rf:voice-3` | The firm's confidentiality convention is restated in 28 of 59 authored documents by 8 of 11 authors, nearly always in the charter's words 'sector and revenue band', including minutes and status reports where nothing calls for it, so it reads as a slogan the writer was told to carry, not a practice the firm simply follows. |
| minor | `rf:docplaus-10` | Persona sketches are transcribed into genres that would not carry them: an engagement letter, firm overviews, first-week onboarding records and minutes describe colleagues' habits. |
| minor | `rf:docplaus-11` | The eight executed engagement letters share no standard terms: each rewords its liability, confidentiality and governing-law clauses and retitles their headings, although the firm is said to keep a standard engagement letter. |
| minor | `rf:docplaus-12` | Every status report file is named 'v2 FINAL' and every firm overview 'v3', a version suffix stamped per genre rather than one that accumulated per document. |
| minor | `rf:docplaus-8` | Analysts are the authors of record on client status reports and on kickoff memos that set strategy and direct partners, and those documents do not read like an analyst's draft. |
| minor | `rf:docplaus-9` | Every status report restates the advisor's own fixed fee as an engagement budget, and two client decks list the engagement start date as a measure; both are planted facts given a slot no M&A report has. |
| minor | `rf:fin-4` | All ten client status reports restate the advisor's own fee as a budget line held steady. That is how a fixed-price consultancy reports budget burn. An M&A advisor reporting to a selling owner reports the process, not its fee. |
| minor | `rf:fin-5` | Every financial summary books the M&A firm's only revenue line as "Consulting revenue". An advisory boutique's books show advisory or transaction fees, usually split between retainers and success fees. |
| minor | `rf:fin-6` | In the management buyout, the company owned by the selling shareholders pays, reimburses and indemnifies the buyers' advisor, under a letter its CFO signs while he is one of the buyers. |
| minor | `rf:graph-6` | The firm overviews seem to name whoever needed a mention rather than the firm's leaders: the 2014 overview profiles a junior analyst and the chief of staff, and in ten years no overview names either of the other two partners. |
| minor | `rf:graph-7` | Name collisions fall exactly where a firm this focused on conflicts would comment, and nobody comments. An analyst named Duffy joins two weeks into the Browning, Duffy and Santos mandate and sits in its client session, and two Mccoys staff the same three-person team. |
| minor | `rf:narrative-3` | The Lawson recapitalization status report puts the final funnel stage (all four term sheets in hand, first round closed) five business days after the first lender call. The engagement letter allots outreach weeks 8 to 11 and proposals weeks 11 to 13, which works out to mid-September to early October. The prose explains the gap rather than fitting the calendar, and it leaves 28 of the 46 approved sources unapproached without saying so. |
| minor | `rf:narrative-4` | Both earlier versions in the d:0024 version chain are dated before the events their text reports. The noise stage dates chain members 2 to 7 days apart, counting back from the final, and copies the final's time-anchored text into them unchanged. |
| minor | `rf:org_realism-4` | On three of eight engagements the most junior person on the team writes both the kickoff work plan that assigns the partners their roles and the status report that goes to the client, although an associate or director sits on the same team. |
| minor | `rf:org_realism-5` | The advisory group runs two titles for one rung: the same letter introduces 'an Associate' and 'an Advisory Associate' with no difference in role, and only the plain Associate is ever promoted. |
| minor | `rf:org_realism-6` | The founders and shareholders who make every decision never appear: on the sell-side, recapitalization, growth raise and strategic review, the client is a single finance or operations officer who signs the letter and sits in every meeting, while 'the owners' remain an unnamed offstage group. |
| minor | `rf:org_realism-7` | The firm has no home: no overview, letterhead or letter names a city or state, all eight engagement letters set governing law by the circumlocution 'the state in which our principal office is located', and the roster scatters a one-office firm across six metro area codes. |
| minor | `rf:org_realism-8` | A partner's surname is printed 'Mccoy' rather than 'McCoy' in all 22 documents that name him, including letters the Managing Partner signs, and a same-surname partner and associate share a two-banker deal team without a word about it. |
| minor | `rf:voice-4` | Business records describe colleagues using the roster's persona sketches nearly word for word, in a novelist's register, so engagement letters, client-session minutes and first-week onboarding notes share one all-knowing narrator who already knows everyone's habits. |
| minor | `rf:voice-5` | All ten onboarding records carry the Managing Partner's byline (she is the author of 27 of 59 authored documents), yet nine refer to her in the third person and one in the first, so the series reads as an office voice that does not match its byline. |
| note | `rf:docplaus-13` | Deal mechanics and era detail are accurate and are the corpus's strongest feature; the defects above sit in framing, furniture and planted-fact slots, not in the substance of the work. |
| note | `rf:fin-7` | No defect claimed. Where a flat fee is the industry norm, the prose prices and papers it correctly, and era-specific financial detail is accurate. The fee defects above therefore trace to the ledger, not to the authors. |
| note | `rf:narrative-5` | Era references and in-text titles were checked across all 59 sampled documents and are consistent. Every name-and-title pairing matches the person's title history at the document date. The analyst who departed in 2017 is never mentioned afterward. No tool, idiom or event postdates its document. |
| note | `rf:org_realism-9` | No defect: every engagement team includes the Managing Partner or a Partner, and every dated title in the prose matches the person's title history on that date. |
| note | `rf:voice-6` | Sentence rhythm does differ by author, and the outline pool varied the headings, so the convergence in rf:voice-1 to rf:voice-3 lies in rhetorical moves and refrains, not rhythm; the metric's top structural pairs are the Managing Partner's own letters and onboarding notes, and they read as one signatory reusing her templates, which is plausible. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 1.1% | 76.3% | 0.673 | 0.641 |
| filename-only | distractors | 1.1% | 76.3% | 0.673 | 0.641 |
| filename-only | noise | 0.0% | 75.5% | 0.660 | 0.623 |
| filename-only | full | 0.0% | 75.5% | 0.660 | 0.623 |
| bm25 | core | 0.0% | 83.7% | 0.705 | 0.719 |
| bm25 | distractors | 0.0% | 83.7% | 0.705 | 0.719 |
| bm25 | noise | 1.1% | 82.9% | 0.689 | 0.696 |
| bm25 | full | 1.1% | 82.9% | 0.689 | 0.696 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| quillon-harbor | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Verify with `python tools/checksums.py --check`.

## Recommended uses

- Developing and regression-testing retrieval, extraction, people-graph, and access-control-aware systems against a corpus with a computed answer key.
- Measuring what a format transform costs you: the true page text of every degraded scan is archived beside it.
- Publishing a reproducible benchmark. Everything here is fictional and Apache-2.0.

## Non-claims

- **This is a specimen, not a sample.** It is chosen to contain the shapes a system has to handle, not to reproduce a real firm's document footprint. It is two to four orders of magnitude away from one, and the engagement book is a deliberate sample of the firm's own business.
- **Scoring well here does not establish scoring well on a real corpus.** Nothing in this project measures that transfer.
- **The realism numbers have no validated thresholds** and nothing about prose quality gates anything, deliberately.
- **The relevance labels are a documented policy, not ground truth about relevance.** `docs/LABEL-POLICY.md` states what the scan can and cannot see, including the misses.

