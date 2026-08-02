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
| `doc_culture.noise` | `off` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `on` |
| `doc_culture.mail.max_thread_depth` | `5` |
| `doc_culture.mail.mundane_emails` | `4` |
| `doc_culture.mail.attachments` | `0` |
| `doc_culture.mail.distribution_lists` | `1` |
| `doc_culture.mail.exempt_author_mentions` | `True` |
| `doc_culture.mail.exempt_recipient_mentions` | `False` |
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `1400000` |
| `finance.growth_rate` | `0.1` |
| `finance.expense_ratio` | `0.75` |
| `engagements` | `on` |
| `engagements.count` | `6` |
| `engagements.book_is_sample` | `True` |
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

- **Retrieval**: 40 questions, of which 0 are unanswerable (correct response: abstain). 36 incidental documents are marked acceptable across the suite.
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

The adversarial review board's findings against this org (9 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:document-plausibility-thread-state-regression` | In three of the four five-message engagement threads, the final email restarts the data-intake narrative, contradicting the resolved state the earlier messages in the same strictly-linear In-Reply-To chain had already established; read top to bottom the thread's state snaps backward at the last message. |
| major | `rf:graph-acl-1` | Each kickoff memo that has to give a non-engagement colleague a second mention puts that person on the memo's To-line and assigns them engagement work, but the who-can-read-what ground truth grants them no access to any document of that engagement, including the memo addressed to them. |
| major | `rf:narrative-consistency-thread-regression` | In three of the four multi-message engagement email threads, the final message reverts the data-intake state to an earlier point, re-raising items the thread had already closed and describing already-reconciled data as freshly arrived, so the thread stops progressing at its last reply. |
| major | `rf:org-realism-1` | The firm's measurement/assumption/conclusion credo is not just embodied but explicitly restated in near-identical words in almost every document across every genre, which reads as a generator returning to one idea rather than a firm with a house discipline. |
| major | `rf:org-realism-2` | Two midpoint status reports for different clients, engagement types, and authors are near-clones that share whole distinctive sentences verbatim, reading as one generated template rather than a firm's reused format. |
| major | `rf:org-realism-3` | Engagement emails repeatedly address the recipient by full legal name inside the body, as a reliance-documentation device, which no one does when writing to that person. |
| major | `rf:xvoice-1` | The firm's measurement/assumption/conclusion credo is narrated in near-identical triadic wording in almost every document, across all six genres and every author, including short engagement emails and meeting minutes where a real writer would not pause to recite the firm's writing philosophy. |
| major | `rf:xvoice-2` | Beyond the credo, a small bank of signature aphorisms recurs verbatim across different authors and genres, including two distinct personas emitting identical sentences, reading as one writer's phrasebook rather than twelve independent hands. |
| major | `rf:xvoice-3` | The two midpoint status reports d:0012 (Vasquez, 2016) and d:0072 (Harris, 2024) are the same document with domain nouns swapped, yet fall below the report's same-genre similarity threshold, so only a voice read catches the template collapse. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 2.5% | 72.1% | 0.613 | 0.600 |
| filename-only | distractors | 2.5% | 72.1% | 0.613 | 0.600 |
| filename-only | noise | 2.5% | 72.1% | 0.613 | 0.600 |
| filename-only | full | 2.5% | 72.1% | 0.613 | 0.600 |
| bm25 | core | 2.5% | 66.7% | 0.724 | 0.700 |
| bm25 | distractors | 2.5% | 66.3% | 0.723 | 0.696 |
| bm25 | noise | 2.5% | 66.7% | 0.724 | 0.700 |
| bm25 | full | 2.5% | 66.3% | 0.723 | 0.696 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| meridian-actuarial | 198 | `8b51f15336ac3d257313770426218c4fac254810d45be33dbe363f45e1e0d121` |

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

