# Data card: `northgate-staffing`

**Northgate Talent Partners LLC** (executive search), founded 2013.

Derived from committed state by `python -m orgsmith data-card northgate-staffing`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **66 documents**: 44 model-authored, 9 deterministic, 13 derived.
- **Formats**: 42 `.docx`, 6 `.eml`, 7 `.pdf`, 2 `.pptx`, 9 `.xlsx`.
- **Document dates**: 2015-01-15 to 2023-11-26.
- **Charter window**: 2015-01-01 to 2023-12-31.

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
| `doc_culture.noise.drafts` | `2` |
| `doc_culture.noise.version_chains` | `2` |
| `doc_culture.noise.misfiled` | `1` |
| `doc_culture.noise.stale_templates` | `1` |
| `doc_culture.noise.empty_dirs` | `2` |
| `doc_culture.noise.attachment_mismatch` | `0` |
| `doc_culture.noise.filename_variety` | `True` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `off` |
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `1250000` |
| `finance.growth_rate` | `0.1` |
| `finance.expense_ratio` | `0.77` |
| `engagements` | `on` |
| `engagements.count` | `6` |
| `engagements.book_is_sample` | `True` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `6` |
| `graph_targets.external_people` | `6` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `1` |
| `graph_targets.nickname_aliases` | `1` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `0` |
| `hard_cases.filename_dates` | `0` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `1` |
| `roster_churn.promotions` | `2` |
| `roster_churn.hires` | `5` |
| `acl_posture` | `open` |

## Questions

- **Retrieval**: 41 questions, of which 0 are unanswerable (correct response: abstain). 7 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 6, `fact:money` 6, `fact:text` 6, `firm` 1, `mention:alias` 1, `mention:person` 12, `workbook` 9.
- **Extraction**: 18 questions. Locations: `body` 18.
- Extraction difficulty tags: none (no scans, no legacy binaries).
- **Visibility**: 12 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 53 |
| `distractors` | 53 |
| `noise` | 66 |
| `full` | 66 |

**Distractor gap = 0.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `open`.
- **Grants**: 12, covering 0 to 66 documents each (median 66).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 3, covering 3 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

- **Alias disagreement.** `Firm/Firm Overview 2015 v3.docx` uses the nickname "Jim", which the ledger registers to `p:james.grant`, with no planned mention. The structured layer and the prose disagree and the prose reports its source faithfully.

The adversarial review board's findings against this org (8 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cross-voice-closer-1` | Documents across every genre and ostensible author close by isolating 'the single/one thing' that governs what happens next, a structural tic no set of fresh, sibling-blind authors would independently share; it even survives into the registers that otherwise read as distinct voices. |
| major | `rf:cross-voice-nickname-1` | The corpus contradicts itself on which of the two men named James is nicknamed 'Jim': the firm overview gives the nickname to James Weiss (Office Manager), the Roach minutes to James Grant (Senior Consultant), so a reader tracking the roster hits a plain contradiction the disambiguation was meant to prevent. |
| major | `rf:cross-voice-status-1` | The five executive-search status reports collapse onto one template despite carrying five different first-person authors; the flagged pair d:0008 (Sandra) and d:0031 (James) are near-identical paragraph for paragraph, and all five open their risk section with the same frame naming the same two risks, which reads as one generator wearing name tags rather than a firm reusing author-neutral boilerplate. |
| major | `rf:graph-acl-1` | The nickname 'Jim' is attached to two different people: the firm overview assigns it to Office Manager James Weiss (framing it as the disambiguator between the roster's two Jameses), while the meeting minutes assign the same nickname to Principal James Grant. |
| major | `rf:narrative-consistency-jim-nickname` | The nickname "Jim" is attached to two different people across the corpus: the Firm Overview gives it to Office Manager James Weiss and says it is what keeps him distinct from the other James, while the CFO-search meeting minutes give the same nickname to Senior Consultant James Grant. |
| major | `rf:org-realism-jim-1` | The internal nickname "Jim" is attached to two different colleagues named James, and the document that introduces it presents the nickname as the device that keeps the two Jameses apart, so the second use directly contradicts it. |
| minor | `rf:cross-voice-kickoff-1` | Four kickoff memos by four different consultants, plus the firm overview, share the same signature opener and the same specification-gates-everything line, so a phrase meant to sound like an individual's framing reads as a house macro pasted by everyone. |
| note | `rf:graph-acl-2` | Every client-side sponsor the firm interfaces with holds one of only two titles, split in a clean chronological block, which reads as an assigned pool rather than an organic book of relationships. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 0.0% | 68.8% | 0.691 | 0.627 |
| filename-only | distractors | 0.0% | 68.8% | 0.691 | 0.627 |
| filename-only | noise | 0.0% | 66.3% | 0.653 | 0.595 |
| filename-only | full | 0.0% | 66.3% | 0.653 | 0.595 |
| bm25 | core | 0.0% | 70.7% | 0.713 | 0.693 |
| bm25 | distractors | 0.0% | 70.7% | 0.713 | 0.693 |
| bm25 | noise | 0.0% | 67.5% | 0.642 | 0.623 |
| bm25 | full | 0.0% | 67.5% | 0.642 | 0.623 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| northgate-staffing | 168 | `22400c18e9ce898bbf3a3c203c87f0e3b42f721806472ea2c6f152f1c02d18d4` |

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

