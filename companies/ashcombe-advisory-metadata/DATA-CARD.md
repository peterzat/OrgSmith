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
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `2200000` |
| `finance.growth_rate` | `0.08` |
| `finance.expense_ratio` | `0.8` |
| `engagements` | `on` |
| `engagements.count` | `6` |
| `engagements.book_is_sample` | `True` |
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

- **Retrieval**: 44 questions, of which 0 are unanswerable (correct response: abstain). 57 incidental documents are marked acceptable across the suite.
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

The adversarial review board's findings against this org (42 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| blocker | `rf:document_plausibility-1` | Nearly every client-facing email addresses its first-name correspondent by full legal name mid-body, usually under a 'for the file' or 'for the record' formula, exposing the fact-planting machinery. |
| major | `rf:document_plausibility-2` | The mailbox holds only the firm's half of every conversation: all 45 .eml files are From an @ashcombeadvisory.com address, each thread strictly alternates the same two firm authors, and the client's turns exist only as recaps inside firm mail. |
| major | `rf:document_plausibility-3` | The Kirby-Taylor thread forgets its own state: the fact sheet is declared final and locked, then the next email in the same thread asks the client for the same quarterly figures as if they were never sent, then a discrepancy turns up in the already-locked sheet. |
| major | `rf:document_plausibility-4` | The Suarez-Jones thread contradicts its own timeline: a walk-through call scheduled for the coming week is thanked-for as 'last week' on the Monday that week begins, and a draft promised for Aug 5 finally goes out Aug 11 described as ahead of promise. |
| major | `rf:document_plausibility-5` | The firm overviews name clients, including the crisis-communications client, as marketing case studies while every engagement letter promises that the fact of the firm's involvement is itself confidential; the 2017 overview also narrates a month-old, still-active engagement in completed past tense. |
| major | `rf:document_plausibility-8` | All eight mundane internal emails across eight years fall on July 1-3, one per year, so the shared mailbox's entire internal life happens in a single week of the calendar. |
| major | `rf:finance-realism-1` | The Kirby-Taylor numbers thread contradicts itself: the fact sheet is declared final and twice-checked on June 3, the same quarterly figures are re-requested the same day, and a discrepancy against the public record surfaces three days later in figures already declared reconciled. |
| major | `rf:graph-acl-1` | Client contacts never author a single email: all four preserved 8-message engagement threads are exclusively outbound, strictly alternating two internal authors while the client's replies happen off-screen. |
| major | `rf:graph-acl-2` | Nearly every email names its own recipient by full name in the second person, a 'for the file / for the record' tic that recites the participant ledger where a human would say 'you'. |
| major | `rf:graph-acl-3` | Beyond the six single points of contact, no client-side human is ever named in eight years of communications work: executives are interviewed, spokespeople briefed, and boards consulted strictly anonymously. |
| major | `rf:graph-acl-4` | Every client counterpart carries an operations or finance title; a corporate-communications advisory never once corresponds with a communications, IR, marketing, or legal contact on any client side. |
| major | `rf:graph-acl-5` | The partner oversight every letter promises never appears in any interaction record: outside one 2018 engagement, no partner or senior advisor attends a meeting, joins a thread, or clears a statement anywhere in the corpus. |
| major | `rf:graph-acl-6` | The ACL is one flat grid, every active employee holding identical access to all 104 files, even though the crisis letter promises need-to-know internal handling for that very engagement. |
| major | `rf:narrative-1` | The Kirby-Taylor thread resets mid-stream: email 5 asks the client to send the quarterly figures that email 3 already acknowledged receiving and email 4, sent the same day, had already folded into a finished fact sheet. |
| major | `rf:narrative-2` | The Gallegos, Pope and Marsh thread replays its own opening stage: after interviews are penciled in and the coverage read is finished, later emails restart the coverage read, ask the client for interview names as if none existed, and put the not-yet-drafted interview guide back on the to-do list. |
| major | `rf:narrative-3` | In the Suarez-Jones thread the client call flips across a weekend from upcoming to already held: Friday's email places it next week, Monday's email thanks the client for it last week. |
| major | `rf:org_realism-1` | The firm's marketing overviews name engagement clients, including the crisis client, as case studies, directly contradicting its own engagement letters' promise that the fact of the engagement stays confidential. |
| major | `rf:org_realism-2` | Every engagement thread is two firm authors in perfect A/B alternation with zero client messages on file, a mechanical rhythm no real mailbox has. |
| major | `rf:xvoice-1` | Every author from Managing Partner to Office Manager writes in one literary register, built on the balanced antithesis and the aphoristic closing turn, so the corpus reads as one stylist wearing thirteen names. |
| major | `rf:xvoice-2` | Five kickoff memos by five different authors across seven years reuse the same signature first-person asides; these are personal framing sentences, not form fields, so it reads as one generator rather than a memo template. |
| major | `rf:xvoice-3` | All six engagements' opening client emails, by six different authors from 2017 to 2024, run the same script: open the thread to keep updates in one place, log the contacts for the file, report 'we have made a start', promise a steady cadence, ask one question, offer a short call. |
| major | `rf:xvoice-4` | First-person status-report narration recurs verbatim across different authors writing to different clients, past what a house report skeleton would explain; the metric flagged only d:0015/d:0024, but the pattern spans four authors. |
| major | `rf:xvoice-5` | Every author works the client approver's full name into the email body with the same notarial 'For the file / For the record' device, addressing the correspondent by their own full name mid-message; the fact placement is mandated, but the identical workaround across eight authors is the voice leak. |
| major | `rf:xvoice-6` | Distinctive personal asides recur nearly verbatim across different authors in unrelated genres years apart, which the same-genre similarity metric is structurally blind to. |
| minor | `rf:document_plausibility-6` | No executed letter ever names its governing jurisdiction, and the letterhead carries no address, leaving the firm with no geography across eight years of signed legal documents. |
| minor | `rf:document_plausibility-7` | The back half of the Barrera thread duplicates the transport headers as body text: each email opens with a 'To:/Cc:' paragraph above the salutation, a memo formatting habit no other thread has. |
| minor | `rf:finance-realism-2` | Four of the six engagement fees form an exact $500 ladder ($45,500 / $46,000 / $46,500 / $47,000) across seven years and four service lines, and the pricing runs inverted, with crisis communications the cheapest work in the book per month. |
| minor | `rf:finance-realism-3` | The budget section is the one part of the status reports that collapses to a single voice: four different authors across five years state the fee position in the same first-person sentence. |
| minor | `rf:graph-acl-7` | Distribution lists mirror the charter's three departments mechanically, giving a 12-person firm a 'Leadership Team' list with exactly one member; two of the three lists are never used by any email. |
| minor | `rf:graph-acl-8` | The name pool produced confusable near-collisions, sharpest an internal Office Manager Sandra Mcdonald and client contact Sandra Mcdaniel, both handling records and approvals in the same years. |
| minor | `rf:graph-acl-9` | Mundane office mail is authored by roster roulette: the Managing Partner sends the IT-maintenance notice, an analyst the parking update, an associate the timesheet reminder, while the Office Manager whose persona owns the mundane internal mail authors nothing. |
| minor | `rf:narrative-5` | The Gallegos coverage review's span shifts between documents: the kickoff memo and the analyst's first report say two years, later mail and the working-session minutes say eighteen months. |
| minor | `rf:narrative-6` | The 2017 firm overview, written one month into the five-month Barrera engagement, narrates it in the past tense as a quietly concluded success, while the contemporaneous engagement documents show the first messaging draft still in review and nothing yet public. |
| minor | `rf:org_realism-3` | The crisis engagement, the gravest matter in the book, is run by the firm's two most junior associates while the senior bench the overview advertises never appears in it, part of a 2021-2024 pattern where partners and advisors vanish from client work. |
| minor | `rf:org_realism-4` | File naming is mechanically uniform where a real share drifts: all seven status reports across 2017-2024 are 'v2 FINAL' and all three firm overviews are 'v3'. |
| minor | `rf:org_realism-5` | The 2017 firm overview presents the Barrera engagement as a completed, successful case study one month into its five-month term, while the live thread shows the first messaging draft still in revision that same week. |
| note | `rf:document_plausibility-10` | Foundation-level naming inherited by the prose: faker-style capitalization (Mcdonald, Mcdaniel for McDonald, McDaniel) plus the near-collision of internal records-keeper Sandra Mcdonald with client-side approver Sandra Mcdaniel reads as synthetic naming rather than coincidence. |
| note | `rf:document_plausibility-9` | Interpreting the flagged status-report overlap: it reads less like a firm template than one writer's idea, because four different authors on four unrelated engagements present the same three stock risks as bespoke judgment under a near-identical incipit. |
| note | `rf:finance-realism-4` | Money never misbehaves anywhere in the corpus: after each letter is signed, the fee reappears only as 'tracking within its fixed fee', and no invoice sent, payment made or chased, scope change priced, or fee pushback occurs in eight years of correspondence. |
| note | `rf:graph-acl-10` | Six of eighteen external graph entities are quota-filled orphans with no documentary presence at all. |
| note | `rf:narrative-4` | Three of the four multi-email engagement threads sampled (Kirby-Taylor, Suarez-Jones, Gallegos) contradict their own earlier messages, while the longform documents around them (kickoffs, minutes, status reports) stay mutually consistent; the continuity failures are concentrated in mid-thread email, as if each reply were written without the thread's accumulated state. |
| note | `rf:xvoice-7` | The high-overlap pairs the metric flagged within Julie Hill's own genres read as legitimate self-template reuse, and the surface voice layer does differentiate: greetings, closings, and list habits track the style specs, and meeting minutes are the one genre with genuinely distinct voices. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 2.3% | 54.7% | 0.563 | 0.492 |
| filename-only | distractors | 2.3% | 54.7% | 0.563 | 0.492 |
| filename-only | noise | 0.0% | 49.6% | 0.539 | 0.458 |
| filename-only | full | 0.0% | 49.6% | 0.539 | 0.458 |
| bm25 | core | 2.3% | 69.6% | 0.787 | 0.734 |
| bm25 | distractors | 2.3% | 68.3% | 0.787 | 0.723 |
| bm25 | noise | 0.0% | 64.8% | 0.756 | 0.673 |
| bm25 | full | 0.0% | 63.1% | 0.756 | 0.661 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| ashcombe-advisory | 255 | `aad96de5e97fde1462f6e55b0dbcffb37af9953b913f4efd3c25ecf3ee5bd837` |

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

