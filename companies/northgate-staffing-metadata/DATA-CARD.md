# Data card: `northgate-staffing`

**Northgate Talent Partners LLC** (executive search), founded 2013.

Derived from committed state by `python -m orgsmith data-card northgate-staffing`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **76 documents**: 54 model-authored, 9 deterministic, 13 derived.
- **Formats**: 42 `.docx`, 16 `.eml`, 7 `.pdf`, 2 `.pptx`, 9 `.xlsx`.
- **Document dates**: 2015-01-15 to 2023-11-26.
- **Charter window**: 2015-01-01 to 2023-12-31.

## Feature matrix

Every capability knob in this org's recipe, with its value. A knob that is off is off by choice, and the validator skips its rule visibly rather than passing it silently.

| knob | value |
| --- | --- |
| `doc_culture` | `on` |
| `doc_culture.scanned_ratio` | `0.5` |
| `doc_culture.legacy_ratio` | `0.0` |
| `doc_culture.ocr_layer_rate` | `0.34` |
| `doc_culture.business_calendar` | `on` |
| `doc_culture.noise` | `on` |
| `doc_culture.noise.duplicates` | `2` |
| `doc_culture.noise.drafts` | `2` |
| `doc_culture.noise.version_chains` | `2` |
| `doc_culture.noise.misfiled` | `1` |
| `doc_culture.noise.stale_templates` | `1` |
| `doc_culture.noise.empty_dirs` | `2` |
| `doc_culture.noise.attachment_mismatch` | `0` |
| `doc_culture.noise.filename_variety` | `True` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `on` |
| `doc_culture.mail.max_thread_depth` | `4` |
| `doc_culture.mail.mundane_emails` | `5` |
| `doc_culture.mail.attachments` | `1` |
| `doc_culture.mail.distribution_lists` | `1` |
| `doc_culture.mail.exempt_author_mentions` | `True` |
| `doc_culture.mail.exempt_recipient_mentions` | `True` |
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `1250000` |
| `finance.growth_rate` | `0.1` |
| `finance.expense_ratio` | `0.77` |
| `engagements` | `on` |
| `engagements.count` | `6` |
| `engagements.book_is_sample` | `True` |
| `engagements.scope` | `off` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `6` |
| `graph_targets.external_people` | `6` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `1` |
| `graph_targets.nickname_aliases` | `1` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `graph_targets.alias_agreement` | `True` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `1` |
| `hard_cases.filename_dates` | `1` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `2` |
| `roster_churn.hires` | `5` |
| `acl_posture` | `departmental` |

## Questions

- **Retrieval**: 41 questions, of which 0 are unanswerable (correct response: abstain). 42 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 6, `fact:money` 6, `fact:text` 6, `firm` 1, `mention:alias` 1, `mention:person` 12, `workbook` 9.
- **Extraction**: 19 questions. Locations: `body` 17, `filename` 1, `signature_page` 1.
- Extraction difficulty tags: `scan:image-only` 3, `scan:ocr` 6.
- **Visibility**: 12 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 58 |
| `distractors` | 63 |
| `noise` | 71 |
| `full` | 76 |

**Distractor gap = 5.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `departmental`.
- **Grants**: 12, covering 0 to 76 documents each (median 25).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 4, covering 4 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

The adversarial review board's findings against this org (37 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| blocker | `rf:narr-1` | The closing status report on the Hicks-Castillo benchmarking describes a different engagement from the five documents in front of it: a different unit of scope, a different count, a different client body, and none of the open items the October session left. |
| blocker | `rf:voice-1` | Two kickoff memos two years apart, signed by two different research associates, are the same memo re-skinned: same five numbered owners in the same order, same open-questions pair, and a three-paragraph close that runs sentence for sentence. |
| major | `rf:docplaus-1` | Both firm-wide mundane emails are addressed only to the all-staff list yet open by greeting one person by first name, then refer to that same person by full legal name in the third person. |
| major | `rf:docplaus-2` | The first client email attaches the firm's internal kickoff memo verbatim, a document that discusses how to manage that client and disputes his brief. |
| major | `rf:docplaus-3` | The demonstrator mail threads answer client replies that exist nowhere in the file, and each 'RE:' is threaded as a reply to the firm's own previous message rather than to the client. |
| major | `rf:docplaus-4` | The closing status report on the Hicks-Castillo benchmarking describes a materially different piece of work from the rest of that engagement's own file. |
| major | `rf:finance-1` | The ledger books 2020 as a normal 10% growth year and puts travel spend at its all-time high in 2020 and 2021, which is the wrong shape for a retained search boutique in those two years and the opposite of what the firm's own 2021 overview describes. |
| major | `rf:finance-2` | The Hicks-Castillo closing report delivers 57 benchmarked roles across five job families, plus an unplanned internal equity read and a free reissue, against the same unchanged fixed fee that every earlier document in the file says bought eleven positions. |
| major | `rf:graphacl-1` | Two kickoff memos address a colleague on the To/Cc line and hand them a task inside a folder that colleague cannot open. |
| major | `rf:graphacl-2` | Internal administrative mail is sent by whoever, not by the person who holds the function: four of the five internal emails come from someone other than the Office Manager, and each defers the actual ownership to somebody else. |
| major | `rf:narr-2` | Two of the five internal broadcast emails greet one person by first name and then, in the same short note, refer to that same person in the third person and tell the reader to go to them, so the note instructs its own addressee to contact himself. |
| major | `rf:orgreal-1` | On two engagements a Research Associate is the client's de facto lead: the periodic report the client reads goes out over the associate's name with no consultant on it, contradicting the engagement letter that named a consultant as the client's first call. |
| major | `rf:orgreal-2` | The 2023 roster is six Research Associates behind three working consultants, with the Research Consultant rung vacant since mid-2018 and not one associate promoted in seven years, at a firm whose entire business is other people's careers. |
| major | `rf:voice-2` | Every engagement-opening email follows one script across five different authors: status line, 'I am starting this thread so the running record lives in one place', two asks (ninety minutes for a session, a ruling on off-limits companies), then a conditional close trading a client deadline for a firm deliverable. |
| major | `rf:voice-3` | The 'one thing everything else waits on' construction the previous board flagged has survived the regeneration in paraphrase: fourteen documents nominate a single gating item, across eight authors, five genres and 2015-2023, with the wording varied just enough that the n-gram metric cannot see it. |
| major | `rf:voice-4` | Consecutive-engagement status reports by two different authors carry the same risk taxonomy in the same order with clause-level phrasing in common, so the status-report template collapse the previous board found is reduced rather than gone. |
| major | `rf:voice-5` | In the pair the similarity metric flagged, the copied passage is the 'Your Team' paragraph, and it transplants one consultant's distinguishing habit onto another, so the characterization reads as decoration rather than as a description of a person. |
| minor | `rf:docplaus-5` | A note sent to a single colleague carries a paragraph plainly written for the whole office. |
| minor | `rf:docplaus-6` | A Research Associate chases two colleagues for timesheets and speaks for the monthly close, which is the Office Manager's work in this firm. |
| minor | `rf:finance-3` | The P&L absorbs candidate and consultant travel wholly as firm cost, with a single revenue line and no reimbursement line, in a firm whose every engagement letter bills exactly that travel to the client at cost. |
| minor | `rf:finance-4` | Across eleven years the statements contain no down year, no lumpy expense and no one-off item: revenue, compensation and professional services rise in every single transition, and facilities moves only in two exact steps. |
| minor | `rf:graphacl-3` | The permission set has no residue: every one of the 12 read sets is reproducible in closed form from the participant ledger, with zero stale, courtesy, or leftover grants across nine years. |
| minor | `rf:graphacl-4` | Three of the six research associates are inert in the graph, and the two most inert are named exactly twice each, which is the recipe's minimum-mentions floor showing through. |
| minor | `rf:graphacl-5` | Every client has exactly one contact and their titles come from a two-value pool split evenly three and three, so no search in the book was retained by the kind of buyer the firm's own overviews say retains it. |
| minor | `rf:narr-3` | The General Counsel search reports more approaches than its own closed target lists can supply, and more sub-title candidates in conversation than the widened pass produced. |
| minor | `rf:narr-4` | The engagement letter for Davis and Sons hands James Grant, word for word, the personal habit the roster records as Jeffrey Patterson's, so the same Managing Director sells two clients the same distinguishing trait in two different men. |
| minor | `rf:narr-5` | Three of the six onboarding records place the joining date a week away from the start date the roster holds, and one of them names the wrong day of the week. |
| minor | `rf:narr-6` | The four-message client thread holds only Northgate's outbound side, yet the later messages answer things the client said, so the record depends on messages the file does not contain. |
| minor | `rf:narr-7` | The only use of James Grant's nickname in the whole corpus sits in the client-facing minutes he took himself, where he records one action under 'Jim' in the narrative and under 'James Grant' in the action table. |
| minor | `rf:orgreal-3` | The 2021 firm overview asks 'Who actually does the work?' and then names two junior researchers and no consultant at all. |
| minor | `rf:orgreal-4` | Four of the five internal administrative notices are sent by consultants, the Managing Director, or a research associate, at a firm that employs an Office Manager to do exactly that. |
| minor | `rf:orgreal-5` | Every client contact across six engagements and nine years is a Chief Operating Officer or a General Manager; no chief executive, head of HR, or board chair ever appears, and the board director search is run entirely through a management officer. |
| minor | `rf:voice-6` | The six onboarding records hit the same beats in the same order, including a 'from the outside this looks like clerical work' paragraph and the same hour with the Managing Director described as the one conversation nobody skips. |
| note | `rf:docplaus-7` | All six hire records land the same closing beat, and five of them refer to their own author in the third person while the sixth is in her first person. |
| note | `rf:finance-5` | No defect claimed: the deterministic review sample for this org contains no financial document, so the reading list handed to this dimension holds nothing from the Finance folder. |
| note | `rf:graphacl-6` | The internal correspondence graph has no work edges: every engagement email is outbound to the client and every internal email is administrative, in the org built as the fleet's mail-heavy exemplar. |
| note | `rf:voice-7` | Per-person voice is genuinely present in this corpus; what recurs is per-genre outline, so the defect sits at the level of what each document is asked to contain rather than at the level of how any one person writes. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 0.0% | 69.9% | 0.654 | 0.610 |
| filename-only | distractors | 0.0% | 69.9% | 0.654 | 0.610 |
| filename-only | noise | 0.0% | 68.4% | 0.649 | 0.598 |
| filename-only | full | 0.0% | 68.4% | 0.649 | 0.598 |
| bm25 | core | 0.0% | 71.5% | 0.752 | 0.715 |
| bm25 | distractors | 0.0% | 70.2% | 0.691 | 0.680 |
| bm25 | noise | 2.4% | 67.1% | 0.686 | 0.653 |
| bm25 | full | 2.4% | 66.5% | 0.641 | 0.625 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| northgate-staffing | 200 | `11a9358a35d9354dc9a8ef8a0ad00a5b9c83f8885752949a491a6b10a36e1b35` |

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

