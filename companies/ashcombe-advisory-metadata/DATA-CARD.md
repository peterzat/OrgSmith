# Data card: `ashcombe-advisory`

**Ashcombe Advisory Partners LLC** (corporate communications advisory), founded 2014.

Derived from committed state by `python -m orgsmith data-card ashcombe-advisory`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **104 documents**: 79 model-authored, 8 deterministic, 17 derived.
- **Formats**: 41 `.docx`, 45 `.eml`, 8 `.pdf`, 2 `.pptx`, 8 `.xlsx`.
- **Document dates**: 2017-01-15 to 2024-07-01.
- **Charter window**: 2017-01-01 to 2024-12-31.

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
| `doc_culture.noise.drafts` | `3` |
| `doc_culture.noise.version_chains` | `3` |
| `doc_culture.noise.misfiled` | `2` |
| `doc_culture.noise.stale_templates` | `2` |
| `doc_culture.noise.empty_dirs` | `3` |
| `doc_culture.noise.attachment_mismatch` | `1` |
| `doc_culture.noise.filename_variety` | `True` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `on` |
| `doc_culture.mail.max_thread_depth` | `8` |
| `doc_culture.mail.mundane_emails` | `8` |
| `doc_culture.mail.attachments` | `2` |
| `doc_culture.mail.distribution_lists` | `3` |
| `doc_culture.mail.exempt_author_mentions` | `True` |
| `doc_culture.mail.exempt_recipient_mentions` | `True` |
| `doc_culture.mail.broadcasts_address_the_list` | `True` |
| `doc_culture.style_specs` | `True` |
| `doc_culture.client_facing_reports` | `False` |
| `doc_culture.outline_variety` | `False` |
| `doc_culture.overview_cites_finished_work` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `2200000` |
| `finance.growth_rate` | `0.08` |
| `finance.expense_ratio` | `0.8` |
| `engagements` | `on` |
| `engagements.count` | `6` |
| `engagements.book_is_sample` | `True` |
| `engagements.scope` | `off` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `8` |
| `graph_targets.external_people` | `10` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `0` |
| `graph_targets.nickname_aliases` | `1` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `graph_targets.alias_agreement` | `False` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `0` |
| `hard_cases.filename_dates` | `0` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `2` |
| `roster_churn.hires` | `3` |
| `acl_posture` | `open` |

## Questions

- **Retrieval**: 44 questions, of which 0 are unanswerable (correct response: abstain). 125 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 6, `fact:money` 6, `fact:text` 6, `firm` 1, `mention:alias` 1, `mention:person` 16, `workbook` 8.
- **Extraction**: 18 questions. Locations: `body` 18.
- Extraction difficulty tags: none (no scans, no legacy binaries).
- **Visibility**: 16 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 79 |
| `distractors` | 87 |
| `noise` | 96 |
| `full` | 104 |

**Distractor gap = 8.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `open`.
- **Grants**: 16, covering 0 to 104 documents each (median 104).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 6, covering 6 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

The adversarial review board's findings against this org (45 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cross_document_voice-1` | Six different engagement leads, 2017 to 2024, open their client threads with the same moves in the same order: the thread is declared the one place for status (five of six), then a 'where things stand' paragraph, then an ask for what is needed 'from your side' (usually counted), then a close of the form 'Once X, Y will Z'. |
| major | `rf:docplaus-1` | No client document ever says what the client does or what happened to it: IR, media, positioning and crisis work is described with every concrete particular removed. |
| major | `rf:docplaus-2` | Engagement threads are firm-only monologues: the client never writes a single message, two staff members strictly alternate on every thread, and they end up answering each other's questions to the client. |
| major | `rf:docplaus-3` | Minutes, status reports, memos and onboarding records carry no date anywhere in the document; the date exists only in the filename. |
| major | `rf:docplaus-4` | The 'mundane and constant' internal mailbox is exactly one email a year, every one dated in the first three days of July, so six of eight are about the Fourth of July. |
| major | `rf:finance-1` | Engagement fees do not follow the work. The nine-month investor relations program and the eight-month crisis engagement cost the same $46,500 to $47,000 as the four-month media program and reputation audit, while a five-month executive messaging project costs $102,000. |
| major | `rf:graphacl-ash-1` | Staff outside the engagement teams appear only where a two-mention floor put them: the Senior Advisor, Director of Operations and Office Manager are named together in the February 2017 Barrera kickoff and the March 2017 overview and almost nowhere else in eight years, and the standing roles those documents give them (and the one a 2023 kickoff gives Julie Bailey) leave no trace in any later document. |
| major | `rf:graphacl-ash-2` | On five of six engagements the Managing Partner or Partner takes the minutes while associates and analysts sit in the room, and the junior lead writes the kickoff memo and the client status report even where the engagement letter says the senior leads the work, so who does what runs upside down. |
| major | `rf:graphacl-ash-3` | The engagement mail is a two-person relay addressed to a client who never writes: none of the 34 authored engagement emails is from a client, every eight-message thread alternates strictly between the same two Ashcombe senders, and the approvals the threads exist to record happen off the thread. |
| major | `rf:graphacl-ash-4` | Every client is exactly one person, drawn from an operations and finance title pool, who is the sole approver of everything; in a corporate communications and IR practice no client ever has a named head of communications, IR officer, CEO or counsel, and the second contacts the graph holds for two of those clients never appear. |
| major | `rf:org-1` | In all six engagements the client's only counterpart is an operations or finance officer. None is a head of communications or investor relations, a CEO, or counsel, and no other client executive is ever named. As a result a Director of Operations approves positioning language, decides which figures go public, and takes reporters' calls. |
| major | `rf:org-2` | Three of the six clients have three-surname partnership names that read as law or accounting firms. Yet they operate as listed companies, with shareholder registers, transfer agents, analyst coverage, and quarterly investor updates. |
| major | `rf:org-3` | No client's business is ever stated. In none of the six engagement folders does the reader learn what a client makes or sells, or where it operates. 'The sector' appears wherever a real file would name the industry and the peers. |
| minor | `rf:cross_document_voice-2` | Five authors in three genres announce a count before the items ('three things', 'two things from your side'). It is the banned 'Two asks. First... Second...' opener coming back in different words. |
| minor | `rf:cross_document_voice-3` | All six kickoff memos, each by a different author, end the same way: they name the one item everything else waits on, then ask the team for additions or corrections before that item goes to the client contact. |
| minor | `rf:cross_document_voice-4` | All seven status reports and three of the eight minutes open by stating, in nearly the same words, where they fall in the engagement ('at about the halfway point', 'at about its midpoint', 'in its later phase'), usually followed by 'on plan' or 'on schedule'. Eight authors write the same first sentence. |
| minor | `rf:cross_document_voice-5` | Other authors describe colleagues in the exact words of the foundation.json persona sheet, so the same stock epithet follows a person from document to document. It reads as if one writer were working from a character bible. |
| minor | `rf:cross_document_voice-6` | In-thread replies use only two openers: 16 of the 28 replies in the four multi-message threads name the colleague's previous message in their first sentence, and 9 more start 'Thank you for ...'. All six reply authors use one or both. |
| minor | `rf:cross_document_voice-7` | The personas written as the corpus's outliers (Julie Hill's one-line replies, Christopher Walton's dry notes with no greeting, Kimberly Le's clipped fragments, Sandra Mcdonald's bodies of bare confirmations) all write the same complete, courteous paragraphs as everyone else. |
| minor | `rf:docplaus-10` | Each person's greeting and sign-off is fixed regardless of audience or hour, so a team-lunch broadcast closes 'Sincerely' and an afternoon reply opens 'Good morning'. |
| minor | `rf:docplaus-5` | The firm overviews read as the recipe narrative rather than a prospect-facing pitch: they explain the internal kickoff memo and email workflow, introduce the office manager, and omit founding year, location, contact details and any career credentials. |
| minor | `rf:docplaus-6` | The 2023 overview names a crisis-communications client in marketing copy, the one category of client a communications advisory anonymizes. |
| minor | `rf:docplaus-7` | The six engagement letters re-draft their legal boilerplate from scratch each time, with substantive terms drifting letter to letter, and not one names the governing state. |
| minor | `rf:docplaus-8` | Every executed letter shows the client countersigning on the letter's own date, including two Sundays, although each letter asks the client to sign and return it. |
| minor | `rf:docplaus-9` | The most senior person in the room keeps the minutes, and the managing partner writes every personnel onboarding record, including one for an operations hire who reports to the Director of Operations. |
| minor | `rf:finance-2` | The four comparable fees fall by exactly $500 per engagement from 2018 to 2024 while the firm's revenue grows by about 40 percent, so the fees read as a counting sequence rather than a rate card. |
| minor | `rf:finance-3` | The crisis letter sells open-ended, after-hours crisis counsel of no fixed length for a fixed fee paid in equal monthly installments. A crisis firm would not sign those terms, and they cannot be invoiced as written. |
| minor | `rf:finance-4` | Travel snaps back past its pre-pandemic level in 2021. The FY2021 summary shows the firm's highest travel spend to that point, 22 percent above 2019, in a year whose client sessions in the sample were held by video. |
| minor | `rf:finance-5` | Office & Facilities is identical to the dollar across consecutive years, three years at one figure and then four at the next. That reads as a budget plug, not an actual occupancy cost. |
| minor | `rf:graphacl-ash-5` | Office mail is sent by whoever was drawn rather than by the people who hold the function: neither the Director of Operations nor Pamela Rojas, Office Manager throughout, sends any of the eight internal emails, and an Associate polices his Partner's timesheet. |
| minor | `rf:graphacl-ash-6` | The Leadership Team distribution list has one member, the Managing Partner, because lists are cut one per department; the firm's other Partner and its Director of Operations, who reports to her, are outside it. |
| minor | `rf:graphacl-ash-7` | The graph keeps the departed Communications Analyst employed: her works_at edge never closes, while the roster ends her employment in 2020 and the ACL and distribution lists treat her as gone. |
| minor | `rf:narr-1` | The three working drafts of the Castaneda, Adams and Davis kickoff memo are dated before the engagement began but already describe its start in the past tense, and the v3 copy is the one the client received. |
| minor | `rf:narr-2` | The firm overview reverses its stated policy on naming clients between versions, and no version acknowledges the change. |
| minor | `rf:narr-3` | The last message in the Gallegos, Pope and Marsh thread proposes, as if new, a leadership-interview sequence and press conversations that earlier messages in the same thread had already settled or reported under way. |
| minor | `rf:narr-4` | Two onboarding records are written as if the hire had not yet arrived, although each is dated a week after that person's start date in the roster. |
| minor | `rf:org-4` | Staff keep the same title from 2017 to 2024. 'Communications Associate' is the title both of a long-tenured staff member who runs an engagement day to day and of three new hires onboarded in 2019, 2021 and 2023. |
| minor | `rf:org-5` | Both recorded title changes read wrong. One is a lateral move into a departed colleague's title. The other leaves the three-person Operations team with two Office Managers and no Client Coordinator. |
| minor | `rf:org-6` | Office logistics mail comes from the Managing Partner, an Associate and an Analyst. The Office Manager and the Director of Operations, whose job this is, write none of the firm's eight internal emails. |
| minor | `rf:org-7` | None of the three firm overviews names Michael Morris, the firm's second partner. The 2017 edition profiles the Senior Advisor, the Director of Operations and the Office Manager, and the 2020 and 2023 editions promise every client a partner. |
| minor | `rf:org-8` | The phone numbers in email signatures spread a single-office, 15-person firm across six metro area codes, including colleagues who share a lobby, a garage and a main phone line. Each signature carries one number and there is no office line. |
| minor | `rf:org-9` | Both Mc- surnames are capitalized 'Mcdonald' and 'Mcdaniel', a title-casing artifact that shows up even in the employee's own signature and file name. The two names also belong to near-namesakes: staff member Sandra Mcdonald and client contact Sandra Mcdaniel. |
| note | `rf:cross_document_voice-8` | The pairs the report flags read as personal habit or firm template rather than generator collapse, and sentence rhythm does vary believably by author. The shared voice in this corpus is in the rhetorical moves above, which none of the similarity metrics measure. |
| note | `rf:finance-6` | No defect claimed: the overall P&L fits an 11- to 15-person communications and IR boutique, and the declared 2020 reads correctly. The defects above sit in the fee schedule and in individual expense lines, not in the firm's scale. |
| note | `rf:graphacl-ash-8` | The ACL half of this dimension carries no signal on this org: the open posture gives all 15 current staff the identical 104-document grant and the departed analyst none, which is a common real small-firm setup but sits beside engagement letters that promise need-to-know access. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 2.3% | 55.0% | 0.563 | 0.494 |
| filename-only | distractors | 2.3% | 55.0% | 0.563 | 0.494 |
| filename-only | noise | 0.0% | 49.8% | 0.539 | 0.459 |
| filename-only | full | 0.0% | 49.8% | 0.539 | 0.459 |
| bm25 | core | 0.0% | 66.4% | 0.792 | 0.702 |
| bm25 | distractors | 0.0% | 65.9% | 0.790 | 0.695 |
| bm25 | noise | 0.0% | 62.9% | 0.795 | 0.657 |
| bm25 | full | 0.0% | 62.7% | 0.795 | 0.654 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `280d5a1979cad16fff3b02f9e49d05d97ba6e16a2a9f17e051a0e874fd111e79` |

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

