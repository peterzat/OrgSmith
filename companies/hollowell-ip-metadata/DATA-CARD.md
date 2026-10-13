# Data card: `hollowell-ip`

**Hollowell Patent Group PLLC** (intellectual property law), founded 2016.

Derived from committed state by `python -m orgsmith data-card hollowell-ip`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **64 documents**: 56 model-authored, 8 deterministic, 0 derived.
- **Formats**: 28 `.docx`, 22 `.eml`, 5 `.pdf`, 1 `.pptx`, 8 `.xlsx`.
- **Document dates**: 2018-01-15 to 2025-08-19.
- **Charter window**: 2018-01-01 to 2025-12-31.

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
| `finance.base_revenue` | `1320000` |
| `finance.growth_rate` | `0.08` |
| `finance.expense_ratio` | `0.73` |
| `engagements` | `on` |
| `engagements.count` | `5` |
| `engagements.book_is_sample` | `True` |
| `engagements.scope` | `off` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `5` |
| `graph_targets.external_people` | `5` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `0` |
| `graph_targets.nickname_aliases` | `1` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `graph_targets.alias_agreement` | `False` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `1` |
| `hard_cases.filename_dates` | `0` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `1` |
| `roster_churn.hires` | `4` |
| `acl_posture` | `departmental` |

## Questions

- **Retrieval**: 35 questions, of which 0 are unanswerable (correct response: abstain). 65 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 5, `fact:money` 5, `fact:text` 5, `firm` 1, `mention:alias` 1, `mention:person` 10, `workbook` 8.
- **Extraction**: 15 questions. Locations: `body` 14, `signature_page` 1.
- Extraction difficulty tags: none (no scans, no legacy binaries).
- **Visibility**: 10 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 60 |
| `distractors` | 64 |
| `noise` | 60 |
| `full` | 64 |

**Distractor gap = 4.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `departmental`.
- **Grants**: 10, covering 0 to 64 documents each (median 22).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 0, covering 0 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

The adversarial review board's findings against this org (40 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cdv-kickoff-moves` | The five kickoff memos, by five different authors over six years, make the same opening moves in the same order (what 'we owe' the client, 'our contact' by name and title, 'the fee is fixed, so') and two pairs close on the same couplet, so the memos read as one writer filling one form in varied words. |
| major | `rf:cdv-status-reskin` | Ashley Williams's 2024 trademark-clearance status report is Richard Henderson's 2020 freedom-to-operate report re-skinned section by section, and Henderson's two-tier contact closer reappears in David Chang's 2025 report, so three authors on three service lines share one report. |
| major | `rf:cdv-thread-openers` | Four of the five engagement threads, opened by four different people between 2019 and 2025, begin by announcing the thread itself, two of them in a near-identical pair of sentences, so the brief's instruction to set the thread up shows through as one writer's opener. |
| major | `rf:doc-plausibility-no-docket-or-date` | No email, letter, memo or set of minutes shows a docket or matter number, though the firm's own documents say every client update cites one, and no memo, minutes or status report states its own date. |
| major | `rf:doc-plausibility-no-identifiers` | Nothing the practice works on is ever identified or counted: no patent or application number, no mark, product, cited reference or examiner, and no count of families or references, so an IP practice's files read as if redacted. |
| major | `rf:doc-plausibility-no-location` | The firm has no location: all five engagement letters choose 'the law of the state in which our office is located' without naming the state, the letterhead carries only a web address, and the overviews' contact sections give no address, phone or email. |
| major | `rf:doc-plausibility-thread-regression` | In each of the three five-message client threads the final reply regresses against the history quoted directly beneath it, reporting as news a stage the thread passed days earlier and asking again for what was already supplied. |
| major | `rf:finance-1` | A US-only trademark clearance of one proposed name carries a $48,000 fixed fee, an order of magnitude above what clearance work is billed at and more than the firm charges for a full patent licensing diligence. |
| major | `rf:finance-2` | Travel runs at 6-8% of fees, about $20,000 per head a year, and exceeds Office & Facilities in FY2023 and FY2024: a consulting firm's travel line on a desk-bound patent prosecution boutique. |
| major | `rf:graph-1` | Two kickoff memos address a colleague by name and give them named work, but the ACL denies each of them the folder the memo is filed in, so the people graph and the permissions graph disagree about who is on the matter. |
| major | `rf:graph-2` | The corpus says the Docketing Manager enters and reconciles every matter's dates, yet she can read all eight FY financial summaries and not one engagement document. |
| major | `rf:narrative_consistency-1` | In all three five-message client threads, the last reply puts the matter back at an earlier stage than the thread's own first message and asks again for material already received. The rendered reply quotes the messages it contradicts directly beneath it. |
| major | `rf:narrative_consistency-2` | The engagement letter and kickoff memo give the Jackson Inc trademark analysis to associate Kelly Snyder. From the working session onward, patent agent Ashley Williams reviews the search reports and drafts the analysis, although her own kickoff memo says patent agents cannot do trademark work. |
| major | `rf:org_realism-1` | The firm's one trademark matter is run and substantively drafted by a patent agent, inside a self-described patent-only practice whose own kickoff memo says its patent agents cannot do trademark work. |
| minor | `rf:cdv-counsel-disclaimer` | Three patent agents on three engagements (2020, 2024, 2025) close their client updates on one disclaimer in paraphrase (no view yet; the partner will give it, in writing, once the work is done), so a line a real firm would either standardize or leave to each writer reads as one hand. |
| minor | `rf:cdv-midpoint-opener` | All five midpoint status reports, by five different authors, open by announcing that the work is at its midpoint and on schedule, the brief's position note restated as a topic sentence, and two carry 'midpoint' into a heading. |
| minor | `rf:cdv-partner-gloss` | When a partner steps into an agent's client thread, Heather Munoz in 2020 and Mary Bradley in 2024 make the same move in the same words: take up the second item of the agent's list and ask for the document itself, not a summary of it. |
| minor | `rf:cdv-persona-transplant` | Roster persona sketches are quoted into the documents as colleagues' narration or as firm doctrine, so one person's distinguishing habit turns up in another's mouth or in firm copy written before that person joined, and the habits stop marking anyone. |
| minor | `rf:cdv-self-nickname` | Joseph Walker's own minutes describe him from outside, by his nickname in one and with credit for his own care in the other, though both name him as the note-taker and narrate the team as 'we'. |
| minor | `rf:doc-plausibility-letter-form` | The managing partner's five engagement letters share no firm form: standard terms are redrafted in each, and the liability clause flips between disclaiming any limit and capping liability at fees paid. |
| minor | `rf:doc-plausibility-role-inversion` | Who writes what is inverted: non-attorney patent agents issue four of the five kickoff memos assigning work to partners and associates, while a partner or the managing partner writes seven of the nine sets of minutes with juniors in the room. |
| minor | `rf:finance-3` | Travel collapses in FY2020 and then comes back above its pre-pandemic level in FY2021, a year in which a firm like this was still mostly not traveling. |
| minor | `rf:finance-4` | Every financial summary labels the firm's only revenue line 'Consulting revenue', a term a patent law PLLC would not use for its legal fees. |
| minor | `rf:finance-5` | Office & Facilities repeats to the dollar for four years running, twice, which reads as a plug figure rather than an occupancy line. |
| minor | `rf:graph-3` | Each matter folder is restricted to its three-person team, so the Partner every prosecution staffer reports to cannot open the two most recent matters, though her own reports staff both. |
| minor | `rf:graph-4` | Every employee can read the personnel onboarding records and the one-to-one mail, but only two people can read the financial summaries, which puts sensitivity the wrong way round. |
| minor | `rf:graph-5` | The recipe's one nickname goes to an associate and appears only in minutes he wrote himself, where he calls himself 'Joe' in the third person while a second Joseph is in the room. |
| minor | `rf:graph-6` | Across 56 documents and seven years of patent work, the only people named are the ten staff and one business officer per client. Every inventor, examiner, client engineer, licensor's counsel and foreign associate goes unnamed, even in minutes of calls with them. |
| minor | `rf:narrative_consistency-3` | Until 10 May 2024 the Jackson Inc clearance concerns a single chosen name. From then on it covers a ranked slate of candidate marks, but no document records the client adding names, and by then the window the letter allowed for alternatives had already closed. |
| minor | `rf:narrative_consistency-4` | The Odonnell portfolio review's letter and kickoff memo exclude office-action work. The later status report and November minutes nonetheless have the firm drafting office-action responses and promising extensions, with Amanda Schwartz moved from title work onto the pending applications. |
| minor | `rf:narrative_consistency-5` | The Keith-Duarte minutes say Kelly Snyder's summaries already lead with the decision and its date, then assign her to recast them into that 'new format'. The next status report says they 'now' lead that way. |
| minor | `rf:narrative_consistency-6` | The September 2020 Middleton status report lists the file-history reading as complete, then calls it the largest open item later in the same report. Later documents treat that reading as ongoing work. |
| minor | `rf:org_realism-2` | The roster has no paralegal, legal assistant or office administrator, so the firm's housekeeping mail comes from fee earners while its one non-practitioner, the Docketing Manager, sends none. |
| minor | `rf:org_realism-3` | The firm has no home: no document names its city or state, every engagement letter avoids naming its governing law, and the signature blocks of a firm with one office carry four metro area codes. |
| minor | `rf:org_realism-4` | Prosecution Support is shaped as a five-month fixed-fee project that ends by handing live applications, one still under rejection, back to a client whose only contact is its General Manager, with no withdrawal or successor counsel. |
| minor | `rf:org_realism-5` | The client book reads as generated: five surname-compound company names, one styled like a law or accounting partnership, each instructed by a general business officer and never by in-house counsel or an engineer. |
| note | `rf:cdv-voice-present` | Sentence-level voice does differ by author and holds across years; the convergence in the findings above lies in per-genre rhetorical moves, and the structural metric's top pairs are mostly one person's own email habits, which is plausible. |
| note | `rf:doc-plausibility-doctrine-sound` | The doctrinal and procedural content is accurate for the genre and the year, so the defects above are structural omissions, not domain ignorance. |
| note | `rf:narrative_consistency-7` | Findings 1 through 4 each start at the first document of a new authoring work order, so a matter's history appears to break where its documents were split across batches. This is an observation about the pipeline; it claims no further defect. |
| note | `rf:org_realism-6` | Outside the trademark matter, titles and the agent/attorney boundary are handled the way a real patent boutique handles them, including the patent-agent-to-associate promotion. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 2.9% | 69.5% | 0.598 | 0.570 |
| filename-only | distractors | 2.9% | 69.5% | 0.598 | 0.570 |
| filename-only | noise | 2.9% | 69.5% | 0.598 | 0.570 |
| filename-only | full | 2.9% | 69.5% | 0.598 | 0.570 |
| bm25 | core | 2.9% | 63.5% | 0.771 | 0.663 |
| bm25 | distractors | 2.9% | 63.8% | 0.771 | 0.664 |
| bm25 | noise | 2.9% | 63.5% | 0.771 | 0.663 |
| bm25 | full | 2.9% | 63.8% | 0.771 | 0.664 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| hollowell-ip | 181 | `2ea7130ea6fcd9f072281e4941991f4462e0f588efa27b4dda59cc4ccff6cf97` |

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

