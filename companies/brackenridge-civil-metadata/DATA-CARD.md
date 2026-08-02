# Data card: `brackenridge-civil`

**Brackenridge Civil Group Inc** (civil engineering), founded 1996.

Derived from committed state by `python -m orgsmith data-card brackenridge-civil`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **40 documents**: 31 model-authored, 9 deterministic, 0 derived.
- **Formats**: 24 `.doc`, 5 `.pdf`, 2 `.ppt`, 9 `.xls`.
- **Document dates**: 1999-01-15 to 2007-08-13.
- **Charter window**: 1999-01-01 to 2007-12-31.

## Feature matrix

Every capability knob in this org's recipe, with its value. A knob that is off is off by choice, and the validator skips its rule visibly rather than passing it silently.

| knob | value |
| --- | --- |
| `doc_culture` | `on` |
| `doc_culture.scanned_ratio` | `0.5` |
| `doc_culture.legacy_ratio` | `1.0` |
| `doc_culture.ocr_layer_rate` | `0.5` |
| `doc_culture.business_calendar` | `on` |
| `doc_culture.noise` | `off` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `off` |
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `740000` |
| `finance.growth_rate` | `0.06` |
| `finance.expense_ratio` | `0.76` |
| `engagements` | `on` |
| `engagements.count` | `5` |
| `engagements.book_is_sample` | `True` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `5` |
| `graph_targets.external_people` | `5` |
| `graph_targets.min_mentions_per_person` | `2` |
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
| `roster_churn.hires` | `3` |
| `acl_posture` | `open` |

## Questions

- **Retrieval**: 34 questions, of which 0 are unanswerable (correct response: abstain). 4 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 5, `fact:money` 5, `fact:text` 5, `firm` 1, `mention:person` 9, `workbook` 9.
- **Extraction**: 15 questions. Locations: `body` 15.
- Extraction difficulty tags: `format:legacy` 15, `scan:image-only` 3, `scan:ocr` 3.
- **Visibility**: 9 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 40 |
| `distractors` | 40 |
| `noise` | 40 |
| `full` | 40 |

**Distractor gap = 0.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `open`.
- **Grants**: 9, covering 0 to 40 documents each (median 40).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 0, covering 0 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

The adversarial review board's findings against this org (8 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cross-voice-1` | The five kickoff memos are attributed to five different staff yet collapse into two verbatim molds, so one generator's hand shows through instead of five distinct writers. |
| major | `rf:cross-voice-2` | Status reports by four different authors reuse the same client-facing idioms word for word, so the reports read as one writer across all engagements. |
| major | `rf:docplaus-1` | The firm overviews describe past engagements with the wrong service type, contradicting every other document in those same engagement folders. |
| major | `rf:graph-acl-1` | The Esparza-Lamb site-grading engagement is run and client-fronted entirely by two Design Technicians with no engineer on the team, the only one of the five engagements staffed that way, though both firm engineers were employed when it ran. |
| major | `rf:narrative-1` | The firm-overview brochures describe three named past engagements as work in disciplines the engagements were not, contradicting each engagement's own letter and file. |
| major | `rf:org-realism-1` | The Esparza-Lamb engagement's client design meetings and progress reports are conducted entirely by Design Technicians with no engineer present, unlike every later engagement, which is implausible for a firm whose drawings only leave under the Principal Engineer's seal. |
| minor | `rf:cross-voice-3` | Meeting minutes by two different authors close on the same templated sentence, another shared idiom that betrays a single hand. |
| minor | `rf:narrative-2` | The Esparza-Lamb final status report claims a delivered scope well beyond the grading-only scope its executed engagement letter set, while insisting scope never changed. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 2.9% | 71.6% | 0.853 | 0.729 |
| filename-only | distractors | 2.9% | 71.6% | 0.853 | 0.729 |
| filename-only | noise | 2.9% | 71.6% | 0.853 | 0.729 |
| filename-only | full | 2.9% | 71.6% | 0.853 | 0.729 |
| bm25 | core | 2.9% | 69.7% | 0.735 | 0.706 |
| bm25 | distractors | 2.9% | 69.7% | 0.735 | 0.706 |
| bm25 | noise | 2.9% | 69.7% | 0.735 | 0.706 |
| bm25 | full | 2.9% | 69.7% | 0.735 | 0.706 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| brackenridge-civil | 127 | `298fb75d6a2fa186de4f3c37a347183927af1897344d7fe726f664d0f9a9941a` |

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

