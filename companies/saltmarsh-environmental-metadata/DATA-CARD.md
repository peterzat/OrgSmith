# Data card: `saltmarsh-environmental`

**Saltmarsh Environmental Partners LLC** (environmental consulting), founded 2011.

Derived from committed state by `python -m orgsmith data-card saltmarsh-environmental`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **40 documents**: 31 model-authored, 9 deterministic, 0 derived.
- **Formats**: 25 `.docx`, 5 `.pdf`, 1 `.pptx`, 9 `.xlsx`.
- **Document dates**: 2013-01-15 to 2021-06-22.
- **Charter window**: 2013-01-01 to 2021-12-31.

## Feature matrix

Every capability knob in this org's recipe, with its value. A knob that is off is off by choice, and the validator skips its rule visibly rather than passing it silently.

| knob | value |
| --- | --- |
| `doc_culture` | `on` |
| `doc_culture.scanned_ratio` | `0.6` |
| `doc_culture.legacy_ratio` | `0.0` |
| `doc_culture.ocr_layer_rate` | `0.5` |
| `doc_culture.business_calendar` | `on` |
| `doc_culture.noise` | `off` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `off` |
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `1150000` |
| `finance.growth_rate` | `0.08` |
| `finance.expense_ratio` | `0.74` |
| `engagements` | `on` |
| `engagements.count` | `5` |
| `engagements.book_is_sample` | `True` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `5` |
| `graph_targets.external_people` | `5` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `0` |
| `graph_targets.nickname_aliases` | `0` |
| `graph_targets.multi_affiliations` | `1` |
| `graph_targets.affiliations_in_docs` | `True` |
| `graph_targets.alias_agreement` | `False` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `1` |
| `hard_cases.filename_dates` | `1` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `1` |
| `roster_churn.hires` | `4` |
| `acl_posture` | `departmental` |

## Questions

- **Retrieval**: 35 questions, of which 0 are unanswerable (correct response: abstain). 5 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 5, `fact:money` 5, `fact:text` 5, `firm` 1, `mention:person` 10, `workbook` 9.
- **Extraction**: 16 questions. Locations: `body` 14, `filename` 1, `signature_page` 1.
- Extraction difficulty tags: `scan:ocr` 9.
- **Visibility**: 10 questions, one per internal person.

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

- **Posture**: `departmental`.
- **Grants**: 10, covering 0 to 40 documents each (median 17).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 0, covering 0 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

- **Value collision.** `f:E-2015-001.client`'s surface "Dyer and Sons" also appears in 4 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2016-001.client`'s surface "Dyer and Sons" also appears in 6 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.

The adversarial review board's findings against this org (9 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cross-voice-1` | Documents attributed to different authors share distinctive, non-slogan sentences near-verbatim, so a cross-document read exposes one generator hand behind supposedly independent writers. |
| major | `rf:fin-realism-1` | The firm insists across its records that it is five people, but its own financials (revenue past $2.1M, compensation past $1.23M) are the payroll and billings of a firm roughly twice that size. |
| major | `rf:graph-acl-1` | The 2021 firm overview's client showcase names the same client, Dyer and Sons, twice consecutively, because two of the five engagements it lists to demonstrate client range share that one client. |
| major | `rf:narrative-consistency-1` | The firm overviews insist on a static five-person headcount and deny any growth, contradicting the firm's own roster and onboarding records, which show it grew to nine employees over the span. |
| major | `rf:narrative-consistency-2` | Two of the five engagements are for the same client (Dyer and Sons), so the firm-overview client showcase presents that client as two distinct clients, listing 'Dyer and Sons' twice consecutively in the 2021 overview's representative-client list. |
| major | `rf:org-realism-duplicate-client` | The 2021 firm overview's representative-client showcase names the same client twice because two sampled engagements share it, so the list reads 'Dyer and Sons, Dyer and Sons, Salazar-Mendoza, ...'. |
| major | `rf:org-realism-headcount-five` | The firm overviews assert a fixed five-person headcount as a deliberate, unchanging identity, but the roster grows to nine active staff by 2021 and the corpus's own onboarding records document that growth. |
| minor | `rf:docplaus-1` | The Phase I engagement letter carries two adjacent, redundantly titled fee sections where the firm's four other engagement letters use a single fee treatment. |
| minor | `rf:org-realism-agency-clients-absent` | Every firm overview foregrounds two public-agency client types (a port authority, a county conservation district) that never appear, and d:0040 claims its all-private example set represents 'a mix of public agencies and private landowners.' |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 2.9% | 68.6% | 0.814 | 0.679 |
| filename-only | distractors | 2.9% | 68.6% | 0.814 | 0.679 |
| filename-only | noise | 2.9% | 68.6% | 0.814 | 0.679 |
| filename-only | full | 2.9% | 68.6% | 0.814 | 0.679 |
| bm25 | core | 2.9% | 70.8% | 0.676 | 0.676 |
| bm25 | distractors | 2.9% | 70.8% | 0.676 | 0.676 |
| bm25 | noise | 2.9% | 70.8% | 0.676 | 0.676 |
| bm25 | full | 2.9% | 70.8% | 0.676 | 0.676 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| saltmarsh-environmental | 126 | `c827f02b73df438c4d43bd0c6c5305124d3a804042bcaa0206ea6670ac4c3b2e` |

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

