# Data card: `calderwood-partners`

**Calderwood Partners LLC** (management consulting), founded 2007.

Derived from committed state by `python -m orgsmith data-card calderwood-partners`. Everything below is recomputed, including the parts that are unflattering.

## Corpus

- **218 documents**: 168 model-authored, 15 deterministic, 35 derived.
- **Formats**: 130 `.docx`, 38 `.eml`, 25 `.pdf`, 10 `.pptx`, 15 `.xlsx`.
- **Document dates**: 2008-01-15 to 2022-11-07.
- **Charter window**: 2008-01-01 to 2022-12-31.

## Feature matrix

Every capability knob in this org's recipe, with its value. A knob that is off is off by choice, and the validator skips its rule visibly rather than passing it silently.

| knob | value |
| --- | --- |
| `doc_culture` | `on` |
| `doc_culture.scanned_ratio` | `0.3` |
| `doc_culture.legacy_ratio` | `0.0` |
| `doc_culture.ocr_layer_rate` | `0.5` |
| `doc_culture.business_calendar` | `on` |
| `doc_culture.noise` | `on` |
| `doc_culture.noise.duplicates` | `15` |
| `doc_culture.noise.drafts` | `20` |
| `doc_culture.noise.version_chains` | `0` |
| `doc_culture.noise.misfiled` | `0` |
| `doc_culture.noise.stale_templates` | `0` |
| `doc_culture.noise.empty_dirs` | `0` |
| `doc_culture.noise.attachment_mismatch` | `0` |
| `doc_culture.noise.filename_variety` | `False` |
| `doc_culture.voice_diversify` | `True` |
| `doc_culture.mail` | `off` |
| `doc_culture.style_specs` | `True` |
| `finance` | `on` |
| `finance.base_revenue` | `2600000` |
| `finance.growth_rate` | `0.07` |
| `finance.expense_ratio` | `0.8` |
| `engagements` | `on` |
| `engagements.count` | `22` |
| `engagements.book_is_sample` | `True` |
| `graph_targets` | `on` |
| `graph_targets.external_orgs` | `12` |
| `graph_targets.external_people` | `14` |
| `graph_targets.min_mentions_per_person` | `2` |
| `graph_targets.surname_collisions` | `1` |
| `graph_targets.nickname_aliases` | `1` |
| `graph_targets.multi_affiliations` | `0` |
| `graph_targets.affiliations_in_docs` | `False` |
| `graph_targets.alias_agreement` | `False` |
| `hard_cases` | `on` |
| `hard_cases.signature_page_facts` | `1` |
| `hard_cases.filename_dates` | `1` |
| `roster_churn` | `on` |
| `roster_churn.departures` | `2` |
| `roster_churn.promotions` | `3` |
| `roster_churn.hires` | `12` |
| `acl_posture` | `departmental` |

## Questions

- **Retrieval**: 108 questions, of which 0 are unanswerable (correct response: abstain). 19 incidental documents are marked acceptable across the suite.
- Retrieval question families: `fact:date` 22, `fact:money` 22, `fact:text` 22, `firm` 1, `mention:alias` 1, `mention:person` 25, `workbook` 15.
- **Extraction**: 67 questions. Locations: `body` 65, `filename` 1, `signature_page` 1.
- Extraction difficulty tags: `scan:image-only` 6, `scan:ocr` 15.
- **Visibility**: 25 questions, one per internal person.

## Splits

| split | documents |
| --- | ---: |
| `core` | 183 |
| `distractors` | 183 |
| `noise` | 218 |
| `full` | 218 |

**Distractor gap = 0.** Authored documents that answer no retrieval or extraction question. A gap of zero means this org has no lexical distractors and its degradation curve is flat between `core` and `distractors`; the noise split still degrades it.

Splits are a retrieval and extraction device. The visibility suite is graded over the whole share by nature and contributes no documents to `core`.

## Access control

- **Posture**: `departmental`.
- **Grants**: 25, covering 0 to 218 documents each (median 43).
- Grants are access *as of the end of the corpus*, so a person the roster retires mid-history holds none. That makes a departed employee a scored visibility question with an empty expected set, not a case the answer key is blind to.

## Labels

- **Relevance-label policy version 1.0** (`docs/LABEL-POLICY.md`).
- **Equivalence clusters**: 15, covering 15 documents that carry byte-identical evidence to a canonical document. Returning a member in place of its canonical is correct.

## Known residuals

- **Value collision.** `f:E-2008-001.client`'s surface "Hughes Group" also appears in 6 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2009-001.client`'s surface "Brown and Sons" also appears in 7 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2009-002.client`'s surface "Key Group" also appears in 9 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2009-003.client`'s surface "Carroll, Merritt and Williams" also appears in 11 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2009-004.client`'s surface "Garza, Leblanc and Porter" also appears in 8 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2010-001.client`'s surface "Poole, Mcknight and Rush" also appears in 6 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2011-001.client`'s surface "Scott, Smith and Edwards" also appears in 6 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2011-002.client`'s surface "Stark-Wilson" also appears in 7 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2012-001.client`'s surface "Garcia-Werner" also appears in 5 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2013-001.fee`'s surface "$30,000" also appears in 2 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2013-001.client`'s surface "Walker-Murray" also appears in 8 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2015-001.fee`'s surface "$112,500" also appears in 5 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2016-001.fee`'s surface "$30,000" also appears in 3 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2016-001.client`'s surface "Hughes Group" also appears in 8 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2017-001.client`'s surface "Brown and Sons" also appears in 8 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2018-001.client`'s surface "Key Group" also appears in 11 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2019-001.fee`'s surface "$112,500" also appears in 2 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2019-001.client`'s surface "Carroll, Merritt and Williams" also appears in 8 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2019-002.client`'s surface "Garza, Leblanc and Porter" also appears in 11 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2019-003.client`'s surface "Poole, Mcknight and Rush" also appears in 8 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2020-001.client`'s surface "Scott, Smith and Edwards" also appears in 7 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2020-002.client`'s surface "Stark-Wilson" also appears in 8 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2021-001.client`'s surface "Garcia-Werner" also appears in 9 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.
- **Value collision.** `f:E-2022-001.client`'s surface "Walker-Murray" also appears in 12 document(s) outside its engagement. Returning those is still wrong; they are recorded so a scoring loss is not a mystery.

The adversarial review board's findings against this org (8 across 6 dimensions), published rather than fixed:

| severity | id | finding |
| --- | --- | --- |
| major | `rf:cross-voice-1` | The kickoff memos, though attributed to six different staff from Principal to Research Associate across 2008-2021, are built from one template and repeat the same idiosyncratic sentences verbatim, so the genre reads as a single author with names swapped rather than the different hands the charter explicitly promises ('no two memos are built from the same template'). |
| major | `rf:cross-voice-2` | The same single-hand fingerprint runs past the kickoff memos into other genres: engagement-email threads and analytical-review minutes repeat distinctive sentences verbatim across authors who, by design, never saw one another's work, so the whole corpus reads as one writer varying cadence rather than a firm of independent hands. |
| major | `rf:finance-realism-1` | Engagement fees run inverse to the seniority and size of the team staffed on them: the firm's Principal-led engagements are the cheapest in the book per month and priced below its own labor cost, while its all-junior engagements cost several times more, so the fees bear no relation to what the depicted work would cost. |
| major | `rf:graph-acl-mention-quota-1` | The person-mention pattern reads as a quota being filled: senders name themselves by full name inside their own emails, and recipients are re-addressed by full name mid-sentence after a first-name greeting. |
| major | `rf:org-realism-1` | Several client engagements are staffed and run end to end by Research Associates, the firm's most junior title, with no principal, engagement manager, or consultant on the team or in the room with the client, inverting the pyramid the firm's own overview promises. |
| minor | `rf:document-plausibility-1` | The firm's 'representative sample, not the whole book' disclaimer is inserted into a client engagement letter and an internal kickoff memo, two genres that would not carry it, making the constraint visible as a planted motif rather than natural document content. |
| minor | `rf:graph-acl-participant-locked-out-2` | Read access is stamped from the engagement participant graph, so a current employee named as a genuine participant in a document is denied access to it. |
| note | `rf:narrative-consistency-1` | The same mid-engagement plot beat -- a single merged cost line that cannot be split, which becomes the one blocker gating the baseline -- recurs as the central working-session problem across four unrelated clients over twelve years, so the engagements read less like independent histories than like one story retold. |

The board is the weakest instrument in this project: it shares blind spots with the generator, its false-positive rate is unmeasured, and it has been caught publishing a checkable falsehood. Read it sceptically.

## Keyless baselines

Where two deliberately dumb retrievers get to. Reference points, never targets: a question family a lexical baseline aces was measuring the filename.

| retriever | split | strict | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: |
| filename-only | core | 0.9% | 65.9% | 0.679 | 0.541 |
| filename-only | distractors | 0.9% | 65.9% | 0.679 | 0.541 |
| filename-only | noise | 0.9% | 63.6% | 0.626 | 0.507 |
| filename-only | full | 0.9% | 63.6% | 0.626 | 0.507 |
| bm25 | core | 0.0% | 71.5% | 0.802 | 0.746 |
| bm25 | distractors | 0.0% | 71.5% | 0.802 | 0.746 |
| bm25 | noise | 0.0% | 69.4% | 0.787 | 0.716 |
| bm25 | full | 0.0% | 69.4% | 0.787 | 0.716 |

## Integrity

| org | files | sha256 |
| --- | ---: | --- |
| calderwood-partners | 505 | `87701c7ca54aa2b347796fa6072a25e918b5a208bc14ca57a26cd5a6810dc053` |

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

