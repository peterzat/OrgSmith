# Data card: `verdant-health`

**Verdant Health Advisory LLC** (healthcare consulting), founded 2018.

Derived from committed state by `python -m orgsmith data-card verdant-health`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **31 documents**: 25 model-authored, 6 deterministic, 0 derived.
- **Formats**: 19 `.docx`, 4 `.pdf`, 2 `.pptx`, 6 `.xlsx`.
- **Document dates**: 2020-01-15 to 2025-01-15.
- **Charter window**: 2020-01-01 to 2025-12-31.

## Feature matrix

Every capability knob in this org's recipe, with its value. A knob that is off is off by choice, and the validator skips its rule visibly rather than passing it silently.

| knob | value |
| --- | --- |
| `doc_culture` | `on` |
| `doc_culture.scanned_ratio` | `0.5` |
| `doc_culture.legacy_ratio` | `0.0` |
| `doc_culture.ocr_layer_rate` | `0.0` |
| `doc_culture.business_calendar` | `on` |
| `doc_culture.noise` | `off` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `off` |
| `doc_culture.style_specs` | `True` |
| `doc_culture.client_facing_reports` | `False` |
| `finance` | `on` |
| `finance.base_revenue` | `1080000` |
| `finance.growth_rate` | `0.06` |
| `finance.expense_ratio` | `0.75` |
| `engagements` | `on` |
| `engagements.count` | `4` |
| `engagements.book_is_sample` | `True` |
| `engagements.scope` | `off` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `4` |
| `graph_targets.external_people` | `4` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `0` |
| `graph_targets.nickname_aliases` | `0` |
| `graph_targets.multi_affiliations` | `1` |
| `graph_targets.affiliations_in_docs` | `True` |
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

- **Retrieval**: 26 questions, of which 0 are unanswerable (correct response: abstain). 2 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 4, `fact:money` 4, `fact:text` 4, `firm` 1, `mention:person` 7, `workbook` 6.
- **Extraction**: 12 questions. Locations: `body` 12.
- Extraction difficulty tags: `scan:image-only` 6.
- **Visibility**: 7 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 31 |
| `distractors` | 31 |
| `noise` | 31 |
| `full` | 31 |

**Distractor gap = 0.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `open`.
- **Grants**: 7, covering 0 to 31 documents each (median 31).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 0, covering 0 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

- **Value collision.** `f:E-2020-001.fee`'s surface "$53,000" also appears in 2 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2020-001.client`'s surface "Johnson, Cross and Gibbs" also appears in 5 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2021-001.client`'s surface "Johnson, Cross and Gibbs" also appears in 6 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2024-001.fee`'s surface "$53,000" also appears in 2 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.

The adversarial review board's findings against this org (8 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cross-voice-1` | The kickoff memos are one template worn by different authors: Barbara Freeman's (d:0020) and Susan Clark's (d:0027) are near-verbatim despite being written by different people for different engagements a year apart, which reads as one generator rather than two colleagues. |
| major | `rf:cross-voice-2` | The two 2023/2024 status reports, authored by different people (Barbara Freeman on d:0022, Susan Clark on d:0029), are the same document section for section, so the promised author differentiation collapses into a shared skeleton. |
| minor | `rf:doc-plausibility-1` | The Sullivan kickoff memo attributes the scanned consents to 'the health system's contracting office,' an entity never introduced, even though the client Sullivan, Hall and Kelly is the only organization in scope and is referred to as 'their' in the same sentence. |
| minor | `rf:org-realism-1` | The firm's named physician-compensation and fair-market-value specialist is absent from the same client's dedicated Physician Compensation Review, which is led instead by the service-line economics consultant. |
| minor | `rf:org-realism-2` | The Sullivan revenue-cycle kickoff blames scanned paperwork on 'the health system's contracting office,' an entity never introduced to the engagement, while the client status report attributes the identical documents to the client's own office. |
| note | `rf:cross-voice-3` | The one pair the similarity metric flagged, the Lopez and Sullivan engagement letters, reads as legitimate template reuse, not a defect, because both carry Laura Brown's signature; the real voice problem is the cross-author clones above, which synonym substitution hides from the 4-gram measure. |
| note | `rf:doc-plausibility-2` | The one flagged same-genre pair (the Lopez and Sullivan engagement letters) reads as authentic template reuse by one signing partner, not as generator monotony; no defect claimed. |
| note | `rf:narr-consistency-1` | Susan Clark, established as the firm's physician-compensation and fair-market-value specialist, does not appear on the one engagement that is a Physician Compensation Review; it is led instead by the service-line economist Daniel Alvarado with analyst Patricia Moore. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 3.9% | 72.1% | 0.750 | 0.671 |
| filename-only | distractors | 3.9% | 72.1% | 0.750 | 0.671 |
| filename-only | noise | 3.9% | 72.1% | 0.750 | 0.671 |
| filename-only | full | 3.9% | 72.1% | 0.750 | 0.671 |
| bm25 | core | 0.0% | 70.5% | 0.699 | 0.682 |
| bm25 | distractors | 0.0% | 70.5% | 0.699 | 0.682 |
| bm25 | noise | 0.0% | 70.5% | 0.699 | 0.682 |
| bm25 | full | 0.0% | 70.5% | 0.699 | 0.682 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| verdant-health | 105 | `48ff3deb97551ad234d1e86ff44b0faae4cacf4b0568188ce12208a15ce262e8` |

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

