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

- **Retrieval**: 35 questions, of which 1 are unanswerable (correct response: abstain). 32 incidental documents are marked acceptable across the suite.
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

The adversarial review board's findings against this org (7 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cross-voice-email-openers` | The first client email of all five engagements opens with the same 'I am opening this thread so ... stay in one place' sentence, though each was written by a different person. |
| major | `rf:cross-voice-kickoff-scope` | The three opinion-type kickoff memos, each by a different agent, reach for the same verbatim scope-scaffolding sentences rather than expressing the shared method in independent words. |
| major | `rf:cross-voice-minutes` | Meeting minutes taken by two different people six years apart share verbatim narrative sentences that are prose, not form fields, so the match reads as one generator rather than two minute-takers. |
| major | `rf:graph-acl-1` | The Jackson Inc trademark-clearance kickoff assigns core searching to Matthew Parrish, who is not on the matter team and has no access to the matter folder. |
| major | `rf:narrative-consistency-1` | The Odonnell portfolio-review engagement carves office-action work out of scope in the letter, kickoff, and deck, then the status report and closing minutes report drafting and FILING office-action responses (and an examiner interview) as completed engagement work while still claiming to be within scope. |
| minor | `rf:doc-plausibility-list-marker` | A client email's two-item request list renders with both a dash bullet and an author-typed number on each line, a double list marker no genuine email carries. |
| minor | `rf:doc-plausibility-mail-salutation` | Both firm-wide internal notices are sent to the all-staff distribution list yet open with the salutation 'Sharon,' and are written entirely as one-to-one notes to the docketing manager, so a broadcast reads as a private message. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 2.9% | 70.7% | 0.615 | 0.583 |
| filename-only | distractors | 2.9% | 70.7% | 0.615 | 0.583 |
| filename-only | noise | 2.9% | 70.7% | 0.615 | 0.583 |
| filename-only | full | 2.9% | 70.7% | 0.615 | 0.583 |
| bm25 | core | 0.0% | 64.6% | 0.750 | 0.690 |
| bm25 | distractors | 0.0% | 64.7% | 0.750 | 0.691 |
| bm25 | noise | 0.0% | 64.6% | 0.750 | 0.690 |
| bm25 | full | 0.0% | 64.7% | 0.750 | 0.691 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| hollowell-ip | 181 | `0d7e53b35a3d2ea4375101ed18ba8c0a4c4a7d408e3d49d46fd6eda1f4678f8a` |

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

