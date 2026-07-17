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

## Length against brief

44 authored documents, 29138 words, mean 662.

Every document is within 75%-150% of the words its brief asked for.

## Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.0751).

## Review board

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
