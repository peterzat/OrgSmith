# Data card: `meridian-actuarial`

**Meridian Actuarial Advisors LLC** (actuarial consulting), founded 2014.

Derived from committed state by `python -m orgsmith data-card meridian-actuarial`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **72 documents**: 63 model-authored, 9 deterministic, 0 derived.
- **Formats**: 29 `.docx`, 26 `.eml`, 6 `.pdf`, 2 `.pptx`, 9 `.xlsx`.
- **Document dates**: 2016-01-15 to 2024-09-25.
- **Charter window**: 2016-01-01 to 2024-12-31.

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
| `doc_culture.noise` | `off` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `on` |
| `doc_culture.mail.max_thread_depth` | `5` |
| `doc_culture.mail.mundane_emails` | `4` |
| `doc_culture.mail.attachments` | `0` |
| `doc_culture.mail.distribution_lists` | `1` |
| `doc_culture.mail.exempt_author_mentions` | `True` |
| `doc_culture.mail.exempt_recipient_mentions` | `True` |
| `doc_culture.mail.broadcasts_address_the_list` | `True` |
| `doc_culture.style_specs` | `True` |
| `doc_culture.client_facing_reports` | `False` |
| `doc_culture.outline_variety` | `False` |
| `doc_culture.overview_cites_finished_work` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `1400000` |
| `finance.growth_rate` | `0.1` |
| `finance.expense_ratio` | `0.75` |
| `engagements` | `on` |
| `engagements.count` | `6` |
| `engagements.book_is_sample` | `True` |
| `engagements.scope` | `off` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `6` |
| `graph_targets.external_people` | `6` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `1` |
| `graph_targets.nickname_aliases` | `0` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `graph_targets.alias_agreement` | `False` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `1` |
| `hard_cases.filename_dates` | `1` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `2` |
| `roster_churn.hires` | `5` |
| `acl_posture` | `departmental` |

## Questions

- **Retrieval**: 40 questions, of which 0 are unanswerable (correct response: abstain). 82 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 6, `fact:money` 6, `fact:text` 6, `firm` 1, `mention:person` 12, `workbook` 9.
- **Extraction**: 19 questions. Locations: `body` 17, `filename` 1, `signature_page` 1.
- Extraction difficulty tags: none (no scans, no legacy binaries).
- **Visibility**: 12 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 68 |
| `distractors` | 72 |
| `noise` | 68 |
| `full` | 72 |

**Distractor gap = 4.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `departmental`.
- **Grants**: 12, covering 0 to 72 documents each (median 27).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 0, covering 0 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

The adversarial review board's findings against this org (38 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:docplaus-1` | Actuarial documents, which are normally full of numbers, contain none. Reconciliation emails, experience tabulations and a preliminary-results meeting give every count, rate and amount as a vague word, and the interim deliverables say up front that they contain no results. |
| major | `rf:docplaus-2` | All six engagement letters leave out the terms an actuarial engagement letter exists to set: none gives a valuation or measurement date, none names the plan (d:0016 never says what kind of reserves it covers), and the governing-law clause never names a state. |
| major | `rf:docplaus-3` | In the Howard and Sons deck, minutes and status report, the choice of mortality table is put to the client as its decision. For a 2016 single-employer funding valuation, the IRS prescribes that table. RP-2014/MP-2015 was a choice only for accounting figures, and the engagement letter excludes accounting work. |
| major | `rf:docplaus-4` | Every engagement email thread is one-sided. Each has five messages that alternate between two firm staff, all addressed to the client, and the client's replies are referred to but never appear, either as messages or in the quoted text. |
| major | `rf:graph-acl-1` | The firm's two actuaries split the book with no overlap: Jennifer Vasquez, who assigns and reviews every associate's work, can read none of the three engagements Robert Lawrence runs and is never named in them, so the second-actuary review the firm promises has no one able to open those files. |
| major | `rf:graph-acl-2` | The prose makes the Practice Manager the keeper of every engagement's letter, billing and file tracking, but the ACL gives Linda Hanna no read grant on any engagement document or financial summary, including the kickoff memo addressed to her. |
| major | `rf:graph-acl-3` | Two associates outside the ledger team are put on a kickoff memo's To line with a substantive role, then never appear again in that engagement, and neither can read the folder that names them. |
| major | `rf:graph-acl-4` | Each client is exactly one named person: all eight sets of minutes list the ledger team plus that one contact and nobody else, and when the firm asks a client for a second name it never arrives. |
| major | `rf:narrative_consistency-1` | Every firm overview describes a practice built on public retirement systems, multiemployer funds and life insurers, but all four pension and retiree-benefit engagements on file are corporate plan-sponsor work that no overview offers. That includes the clients the overviews cite as examples. |
| major | `rf:narrative_consistency-2` | The Howard and Sons documents make the mortality table the client's largest open decision in a 2016 single-employer minimum-funding valuation. The engagement letter itself frames the funding assumptions as prescribed by law, and for that valuation the IRS did prescribe mortality. |
| major | `rf:narrative_consistency-3` | The Estes Group data thread contradicts itself on which year's file holds the renumbered records. The minutes and status report then close a first-year problem, and the most-recent-year departures, along with the layoff questions raised about them, drop out of the record. |
| major | `rf:org_realism-1` | The firm describes itself as a public-system, multiemployer and life-insurer practice, but none of its six engagements is for a public system or a multiemployer fund, and four are private single-employer corporate work that no overview lists as a service. |
| major | `rf:org_realism-2` | Who writes which engagement document runs against seniority: after 2016, associates and analysts issue the kickoff memos and client status reports that assign work to the lead actuary, while the Managing Actuary takes the minutes at every session he attends. |
| major | `rf:voice-1` | Every staff author restates the firm's three-part method in nearly the same sentence, in kickoff memos, status reports, minutes and onboarding records as well as letters and overviews, so the house rule reads as one writer's refrain rather than a practice the reports simply carry out. |
| minor | `rf:docplaus-5` | Minutes, status reports and kickoff memos carry no date in the document itself. The meeting date, report date or memo date appears only in the filename. |
| minor | `rf:docplaus-6` | Some senders open with 'Good morning' whatever time the email went out, including late in the afternoon. |
| minor | `rf:docplaus-7` | The Howard and Sons letter says counsel will sign the signature page, but the page is signed by the Managing Actuary and the client's Director of Operations. |
| minor | `rf:docplaus-8` | The 2019 and 2022 firm overviews spend more words explaining their rule for naming clients than naming them, which reads like the generator explaining its own constraint rather than marketing copy. |
| minor | `rf:docplaus-9` | Several formal documents are dated on weekends or a federal holiday. The recipe's business calendar covers mail, meetings and engagement starts, but not these documents. |
| minor | `rf:finance_realism-1` | Travel returns to above its pre-pandemic level in FY2021 and is twice that level by FY2023, while the firm's own records show it working from home into late 2021 and holding its client sessions by call or video. |
| minor | `rf:finance_realism-2` | The Martinez LLC retiree medical valuation is priced at $118,500. That is the largest fee in the book and nearly four times the pension valuation, for a client small enough that its General Manager gathers the data himself. |
| minor | `rf:finance_realism-3` | Office & Facilities is identical to the dollar for four consecutive years, twice. The occupancy line reads as a step function, not as a rent bill that also carries escalations, utilities and repairs. |
| minor | `rf:graph-acl-5` | Who writes an engagement's kickoff memo and client status report follows the order of the ledger's participant list rather than seniority, so associates issue the client report with the signing actuary credited last. |
| minor | `rf:graph-acl-6` | Office administration mail comes from analysts and associates while a Practice Manager is employed, and neither Practice Manager sends a single email in nine years. |
| minor | `rf:graph-acl-7` | The ACL's open bucket makes personnel-file records and one-to-one mail readable by all eleven current staff, while engagement files are limited to three or four people and the financial summaries to one. |
| minor | `rf:narrative_consistency-4` | Linda Hanna's onboarding record presents the Practice Manager job as a new role created by growth. That erases Carol Cooper, who held the same title and duties for more than five years and left weeks before Hanna started. |
| minor | `rf:narrative_consistency-5` | The ceded-premium discrepancy that takes up four of the five Gonzalez, Campbell and Kelly emails never appears again. The later documents also move from in-force treaty premiums to a reinsurer's proposed rate schedule without any document recording the change. |
| minor | `rf:org_realism-3` | Linda Hanna's onboarding record presents the Practice Manager role as newly needed, although Carol Cooper held that title and those duties from 2014 until five weeks before Hanna started, and no document mentions Cooper leaving or Hanna replacing her. |
| minor | `rf:org_realism-4` | The client side does not look like the people who commission actuarial work: five of six counterparts are operations generalists, and the two insurance clients carry names in the style of law partnerships. |
| minor | `rf:org_realism-5` | The firm works out of one office suite, but its staff's email signatures carry phone numbers in five metro area codes, which suggests a multi-office firm. |
| minor | `rf:org_realism-6` | No firm overview ever names Jennifer Vasquez, the firm's only other actuary and every client's day-to-day contact, and the 2016 overview introduces the Practice Manager in her place, so the firm reads as a two-person shop. |
| minor | `rf:voice-2` | Minutes, decks and status reports by six different authors open on the same pre-emptive disclaimer in the same slot and the same sentence frame ("no view was formed, and nothing here should be read as one"), a writer's fingerprint rather than the varied ways real colleagues hedge. |
| minor | `rf:voice-3` | The six engagement letters, all signed by Robert Lawrence, share one template but re-word its fixed legal terms every time, so the firm has no standard text for the clauses a real firm carries verbatim from letter to letter. |
| note | `rf:docplaus-10` | The details that place each document in its year hold up throughout, and they are this corpus's strongest feature. |
| note | `rf:docplaus-11` | The engagement emails the length metric flags as short (28-72% of brief) read as the right length for mid-thread data questions. Here the 250-word target is off, not the emails. |
| note | `rf:graph-acl-8` | The recipe's same-surname case never appears in the corpus: no document names both Linda Hanna and Nicole Hanna. |
| note | `rf:narrative_consistency-6` | Dated references to tables, standards and events are accurate to each document's date, and titles and overview client citations match the roster and engagement dates. The anachronism half of this dimension came up clean. |
| note | `rf:voice-4` | The persona surface layer holds: greetings, closings, list-versus-paragraph habit and sentence length differ by author and persist across years, and the structural pairs the report flags read as personal habit or inherited template, not collapse; the one-writer signal sits beneath that surface, in rf:voice-1 and rf:voice-2. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 0.0% | 71.5% | 0.613 | 0.593 |
| filename-only | distractors | 0.0% | 71.5% | 0.613 | 0.593 |
| filename-only | noise | 0.0% | 71.5% | 0.613 | 0.593 |
| filename-only | full | 0.0% | 71.5% | 0.613 | 0.593 |
| bm25 | core | 0.0% | 65.6% | 0.746 | 0.690 |
| bm25 | distractors | 0.0% | 65.0% | 0.746 | 0.687 |
| bm25 | noise | 0.0% | 65.6% | 0.746 | 0.690 |
| bm25 | full | 0.0% | 65.0% | 0.746 | 0.687 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| meridian-actuarial | 200 | `5a140496e0c1f7576298f74dbf4c8cc43faed0e78baa94322f2afb530b0d9031` |

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

