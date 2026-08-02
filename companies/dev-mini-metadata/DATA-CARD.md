# Data card: `dev-mini`

**Pinebrook Advisory Group LLC** (management consulting), founded 2018.

Derived from committed state by `python -m orgsmith data-card dev-mini`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **23 documents**: 18 model-authored, 5 deterministic, 0 derived.
- **Formats**: 15 `.docx`, 3 `.pdf`, 5 `.xlsx`.
- **Document dates**: 2019-01-15 to 2023-01-15.
- **Charter window**: 2019-01-01 to 2023-12-31.

## Feature matrix

Every capability knob in this org's recipe, with its value. A knob that is off is off by choice, and the validator skips its rule visibly rather than passing it silently.

| knob | value |
| --- | --- |
| `doc_culture` | `on` |
| `doc_culture.scanned_ratio` | `0.0` |
| `doc_culture.legacy_ratio` | `0.0` |
| `doc_culture.ocr_layer_rate` | `0.0` |
| `doc_culture.business_calendar` | `off` |
| `doc_culture.noise` | `off` |
| `doc_culture.voice_diversify` | `False` |
| `doc_culture.mail` | `off` |
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `850000` |
| `finance.growth_rate` | `0.07` |
| `finance.expense_ratio` | `0.8` |
| `engagements` | `on` |
| `engagements.count` | `3` |
| `engagements.book_is_sample` | `False` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `3` |
| `graph_targets.external_people` | `3` |
| `graph_targets.min_mentions_per_person` | `1` |
| `graph_targets.surname_collisions` | `0` |
| `graph_targets.nickname_aliases` | `0` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `graph_targets.alias_agreement` | `False` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `0` |
| `hard_cases.filename_dates` | `0` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `1` |
| `roster_churn.hires` | `1` |
| `acl_posture` | `open` |

## Questions

- **Retrieval**: 22 questions, of which 0 are unanswerable (correct response: abstain). 2 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 3, `fact:money` 3, `fact:text` 3, `firm` 1, `mention:person` 7, `workbook` 5.
- **Extraction**: 9 questions. Locations: `body` 9.
- Extraction difficulty tags: none (no scans, no legacy binaries).
- **Visibility**: 7 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 23 |
| `distractors` | 23 |
| `noise` | 23 |
| `full` | 23 |

**Distractor gap = 0.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `open`.
- **Grants**: 7, covering 0 to 23 documents each (median 23).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 0, covering 0 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

None recorded. This org has no board findings committed and its corpus-wide scan found no fact-value disagreement.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 9.1% | 71.8% | 0.818 | 0.729 |
| filename-only | distractors | 9.1% | 71.8% | 0.818 | 0.729 |
| filename-only | noise | 9.1% | 71.8% | 0.818 | 0.729 |
| filename-only | full | 9.1% | 71.8% | 0.818 | 0.729 |
| bm25 | core | 0.0% | 74.4% | 0.773 | 0.748 |
| bm25 | distractors | 0.0% | 74.4% | 0.773 | 0.748 |
| bm25 | noise | 0.0% | 74.4% | 0.773 | 0.748 |
| bm25 | full | 0.0% | 74.4% | 0.773 | 0.748 |

## Recommended uses

- Developing and regression-testing retrieval, extraction, people-graph, and access-control-aware systems against a corpus with a computed answer key.
- Measuring what a format transform costs you: the true page text of every degraded scan is archived beside it.
- Publishing a reproducible benchmark. Everything here is fictional and Apache-2.0.

## Non-claims

- **This is a specimen, not a sample.** It is chosen to contain the shapes a system has to handle, not to reproduce a real firm's document footprint. It is two to four orders of magnitude away from one, and the engagement book is a deliberate sample of the firm's own business.
- **Scoring well here does not establish scoring well on a real corpus.** Nothing in this project measures that transfer.
- **The realism numbers have no validated thresholds** and nothing about prose quality gates anything, deliberately.
- **The relevance labels are a documented policy, not ground truth about relevance.** `docs/LABEL-POLICY.md` states what the scan can and cannot see, including the misses.

