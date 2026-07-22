# Generation report: northgate-staffing

Derived artifact: re-emit with `python -m orgsmith report northgate-staffing`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

53 documents planned; 44 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-4-8[1m] | xhigh |
| wo:author:0002 | claude-opus-4-8[1m] | xhigh |
| wo:author:0003 | claude-opus-4-8[1m] | xhigh |
| wo:author:0004 | claude-opus-4-8[1m] | xhigh |
| wo:author:0005 | claude-opus-4-8[1m] | xhigh |
| wo:author:0006 | claude-opus-4-8[1m] | xhigh |
| wo:author:0007 | claude-opus-4-8[1m] | xhigh |
| wo:author:0008 | claude-opus-4-8[1m] | xhigh |
| wo:author:0009 | claude-opus-4-8[1m] | xhigh |
| wo:foundation:0001 | claude-opus-4-8[1m] | xhigh |

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 24 rules run, 0 error(s), 0 warning(s); skipped by charter knob: CAL-01, NOISE-01, AFF-01, AFF-02, EML-02, EML-03, DL-01, STY-01, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score northgate-staffing --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

44 authored documents, 29138 words, mean 662.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.0751).

### Fee coverage

6 documented engagement(s), fees totalling $500,500, against $20,712,000 of lifetime revenue.

Documented fees are 2.4% of lifetime revenue.

The recipe does not declare the engagement book a sample, so the overview may present it as the firm's whole client list. A large fee/revenue gap here reads as the contradiction the board found (engagement-ledger-reads-as-whole-book).

### Cross-document voice

Pre-registered voice patterns over 44 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 3 | 3 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 11 | 10 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 24 | 20 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 146 | 43 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 4 | 4 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 6 | 6 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 8 | 8 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:david.weiss | 3 | 0.0150 (0.0039-0.0344) | 0.0012 | 0.0052 |
| p:james.grant | 5 | 0.0011 (0.0000-0.0027) | 0.0017 | 0.0013 |
| p:jason.bell | 3 | 0.0067 (0.0023-0.0151) | 0.0014 | 0.0024 |
| p:jeffrey.patterson | 4 | 0.0034 (0.0009-0.0074) | 0.0012 | 0.0047 |
| p:john.chang | 2 | 0.0119 (0.0119-0.0119) | 0.0015 | 0.0119 |
| p:kelly.chavez | 15 | 0.0105 (0.0000-0.0751) | 0.0009 | 0.0529 |
| p:nicole.donovan | 5 | 0.0057 (0.0000-0.0312) | 0.0015 | 0.0011 |
| p:sandra.fuentes | 7 | 0.0030 (0.0000-0.0187) | 0.0014 | 0.0052 |

### Review board

28 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:xdv-1 | cross_document_voice | major | corpus | The 'I would rather X now than Y later' antithesis is the whole firm's verbal tic: 34 occurrences across 26 of 44 documents, in every author, every genre, and every year from 2015 to 2023. |
| rf:xdv-2 | cross_document_voice | major | d:0003, d:0011, d:0020, d:0028, d:0036, d:0049 | All six kickoff memos are the same document: six different authors across eight years each produced a literal 'Workstreams' heading, then 'Next Steps', then a closing 'one last thing' aphorism. |
| rf:xdv-3 | cross_document_voice | major | d:0005, d:0012, d:0021, d:0029, d:0037 | All five engagement emails, by five different authors to five different clients over five years, run the identical three-beat structure, and four contain the literal string 'Two asks. First... Second...'. |
| rf:xdv-4 | cross_document_voice | major | d:0002, d:0010, d:0019, d:0027, d:0035, d:0048 | Every engagement letter's team section reads the roster's internal persona notes out to the client, which is not a thing a firm writes to a company it has just signed. |
| rf:xdv-5 | cross_document_voice | major | d:0008, d:0015, d:0023, d:0031, d:0039, d:0051 | The six status reports are interchangeable: six engagements of different kinds across eight years all sit at the identical midpoint with the identical single risk. |
| rf:docplaus-1 | document_plausibility | major | d:0027, d:0035, d:0048 | Three of the six executed engagement letters carry two adjacent, near-duplicate fee headings, a section-assembly artifact no counter-signed contract would retain. |
| rf:docplaus-2 | document_plausibility | major | d:0050, d:0014 | Two sets of minutes record client-attended working sessions held on a US federal holiday and on the Saturday of Memorial Day weekend, with no acknowledgment in either. |
| rf:fin-1 | finance_realism | major | d:0044, d:0045, d:0032 | The firm overviews assert their engagement list is the firm's complete book of business, which contradicts the revenue on the firm's own financial summaries by roughly twenty-fold. |
| rf:fin-2 | finance_realism | major | d:0043, d:0044, d:0045 | The firm posts three consecutive years of record revenue across 2020-2022, a window in which its own engagement record shows no engagements at all. |
| rf:graph-acl-1 | graph_acl_naturalness | major | d:0042, d:0046 | Both research associates hired after 2019 are told in their onboarding records that they report to the Managing Director, but the ledger reports them to the Principal, who is not named in either document. |
| rf:graph-acl-2 | graph_acl_naturalness | major | d:0024, d:0003, d:0006 | The surname collision is announced as a working hazard in one onboarding record but never occurs: the other Weiss last appears two years before it is written and never appears again in six remaining years, and the two men share no document. |
| rf:narrcon-1 | narrative_consistency | major | d:0006, d:0032, d:0044 | All three firm overviews present the six documented engagements as the firm's complete lifetime client history, which the finance ledger contradicts by roughly fortyfold. |
| rf:narrcon-2 | narrative_consistency | major | d:0006, d:0032, d:0044 | Across 2015, 2018 and 2021 the firm's overviews never once name either Principal, instead naming the Office Manager and two research associates who never appear on a single engagement. |
| rf:orgreal-1 | org_realism | major | d:0040, d:0042, d:0046, d:0044 | The firm hires three researchers during a three-and-a-half-year stretch in which its own documents record no live engagement, and their onboarding records describe urgent live work that the engagement book does not contain. |
| rf:orgreal-2 | org_realism | major | d:0048, d:0049 | Six of the firm's eleven staff are Research Associates supporting three consultants, and in seven years nobody has ever been promoted off the research bench or left it. |
| rf:orgreal-3 | org_realism | major | d:0019, d:0020, d:0022, d:0035, d:0006 | Every client counterparty is a COO or General Manager with no CEO, board chair or CHRO anywhere, and the independent-director search is bought and controlled by the management it is meant to oversee. |
| rf:xdv-6 | cross_document_voice | minor | d:0002, d:0010, d:0019, d:0027, d:0035, d:0048 | The engagement letters are inverted: the legal boilerplate is freshly re-drafted for every client while the personal opening is templated, which is the opposite of how a firm's letters accrete. |
| rf:xdv-7 | cross_document_voice | minor | d:0016, d:0024, d:0025, d:0040, d:0042, d:0046 | All six onboarding records run one formula, and each exists mainly to dramatize its subject's persona blurb: one interview anecdote, affirmed as the reason for the offer, then the same discretion sermon delivered fresh. |
| rf:docplaus-3 | document_plausibility | minor | d:0002, d:0019, d:0048, d:0010 | The executed letters carry rhetorical asides inside the operative boilerplate, the one register where a retained-search letter is expected to go flat. |
| rf:graph-acl-3 | graph_acl_naturalness | minor | corpus | Across six retained searches in nine years the client contact is never once a CEO, board chair, CFO or CHRO, and the six contacts' titles fall in perfect blocks of three sorted by engagement date. |
| rf:narrcon-3 | narrative_consistency | minor | d:0016, d:0024, d:0025, d:0040, d:0042, d:0046 | Every onboarding record is written as if on the employee's first day but is dated exactly one week after their roster start date. |
| rf:orgreal-4 | org_realism | minor | d:0044 | The 2021 firm overview names only the two most recently hired associates as 'our research bench' while three other Research Associates are serving on that bench the same day. |
| rf:xdv-8 | cross_document_voice | note | d:0007, d:0014, d:0030, d:0033, d:0050 | The meeting minutes are the one genre where voice genuinely separates, and they show what the rest of the corpus is missing. |
| rf:docplaus-4 | document_plausibility | note | d:0008, d:0015, d:0023, d:0031, d:0039, d:0051 | Every status report in the corpus opens by declaring it stands at the midpoint and then reflects on the midpoint as a stage; no defect claimed, but it is a shared structural move the similarity metric cannot see. |
| rf:fin-3 | finance_realism | note | d:0043, d:0045 | The 2020 travel expense line rises sharply in a year when this firm's travel should have collapsed, and no document in the corpus acknowledges the pandemic. |
| rf:graph-acl-4 | graph_acl_naturalness | note | corpus | The open posture yields a perfectly uniform access matrix, which puts candid written assessments of named individuals on the all-hands share; no defect claimed, since the posture is a recipe knob and the grants conform to it. |
| rf:narrcon-4 | narrative_consistency | note | corpus | Kelly Chavez is the signature on all six engagement letters and the protagonist of all three overviews, but appears as a participant in none of the twenty engagement working documents across nine years. |
| rf:orgreal-5 | org_realism | note | corpus | All six clients are named as eponymous professional partnerships, and none is the regional health system the charter's stated client mix calls for. |
