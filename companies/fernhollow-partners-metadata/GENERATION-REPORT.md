# Generation report: fernhollow-partners

Derived artifact: re-emit with `python -m orgsmith report fernhollow-partners`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

19 documents planned; 17 carry authored prose.

## Provenance

Generator: unrecorded. This org was authored before its model and effort were recorded, or by a pass that did not report them. Self-reported when present; never verified from artifacts.

## Length against brief

17 authored documents, 3889 words, mean 229.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0004 | briefing_deck | 128 | 180 | 0.71 |

## Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0001 | d:0008 | engagement_letter | 0.2524 |

## Review board

26 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:voice-1 | cross_document_voice | major | d:0001, d:0008, d:0013, d:0016 | Michael White signs four engagement letters that share no letter format; the firm's most templated document is rebuilt from scratch each time, and the conventions cluster by authoring batch rather than by client, year, or recipient. |
| rf:voice-2 | cross_document_voice | major | d:0005, d:0012, d:0014, d:0017 | All four sets of meeting minutes run one narrative skeleton -- Sandra opens, a colleague walks through a schedule, an untraceable figure gets flagged, the client agrees to chase it -- across two different minute-takers, five years, and four separate authoring batches. |
| rf:docplaus-1 | document_plausibility | major | d:0001, d:0008, d:0013, d:0016 | All four engagement letters are countersigned EXECUTED contracts that allocate no risk: no termination clause, no limitation of liability, no indemnification, no governing law or dispute resolution, no retainer, and no incorporation of standard terms by reference. |
| rf:docplaus-2 | document_plausibility | major | d:0007, d:0001 | A firm selling independent valuations for financial reporting never once names a credential, a valuation standard, or a restriction on use, across six years of documents. |
| rf:docplaus-3 | document_plausibility | major | d:0017 | Minutes written in the first person by their own named minute-taker, who appears in the third person in the byline of the same document. |
| rf:finance-1 | finance_realism | major | d:0015, d:0019 | Every expense line is a frozen percentage of revenue in all eight years, so the two shipped workbooks show all six line items and net income growing by exactly the same 12.00% year over year, which no real P&L does. |
| rf:finance-2 | finance_realism | major | corpus | Office & Facilities compounds 11% a year to +89% while the firm's own ground truth says the same five people sat in the same office the whole time; rent is a step-fixed lease cost and cannot track revenue. |
| rf:graph-1 | graph_acl_naturalness | major | corpus | Every engagement across five years is staffed by exactly the same three people and every engagement document names all three, so the internal contact graph is perfectly flat where a real firm's is lopsided. |
| rf:narr-1 | narrative_consistency | major | d:0007 | The 2022 firm overview describes the follow-the-finance-lead pattern as the firm's established norm and credits Woods LLC with a readiness workstream, but the only instance of that pattern and the only readiness engagement both begin after the document's date, and Woods never had readiness work at all. |
| rf:narr-2 | narrative_consistency | major | d:0011 | The NRM briefing deck calls itself a midpoint briefing and says the program is past its midpoint, contradicting the start date and duration printed in the same bullet list on the same slide; the deck lands at 25 percent of the engagement. |
| rf:orgreal-1 | org_realism | major | d:0001, d:0008, d:0013, d:0016, d:0017 | Across the corpus's five-year span nobody is hired, promoted, or leaves: the same Director, Senior Associate and Analyst staff all four engagements under identical titles, which leaves Ryan Strong an Analyst five and a half years after joining a firm that has no other analyst to be junior to. |
| rf:voice-3 | cross_document_voice | minor | d:0006, d:0018, d:0004, d:0011 | Same-author, same-genre pairs have identical section architecture with every heading reworded, which is the signature of reconstruction from scratch rather than a professional reusing her own file. |
| rf:voice-4 | cross_document_voice | minor | d:0003, d:0010 | The two engagement emails are one email with the nouns swapped, down to a verbatim framing sentence and the same recipient list in the same order. |
| rf:voice-5 | cross_document_voice | minor | d:0005, d:0006, d:0017, d:0018 | Persona-sheet wording surfaces as literal prose, and one person's characteristic trait floats onto whoever happens to be on stage. |
| rf:voice-6 | cross_document_voice | minor | d:0017, d:0018 | The firm's own legal name loses 'LLC' in the last two documents only, in exactly the roster and byline slots where the earlier documents spell it out. |
| rf:docplaus-4 | document_plausibility | minor | d:0016, d:0003, d:0010 | People are addressed by full name in salutations where real correspondence uses a first name or an honorific and surname, including a director addressing her own two direct reports. |
| rf:finance-3 | finance_realism | minor | corpus | Travel spend rose 9.86% in 2020 for a boutique whose work is on-site diligence, the one year business travel stopped; the ledger has no trace of the pandemic in any line. |
| rf:graph-2 | graph_acl_naturalness | minor | d:0001, d:0008, d:0013, d:0016 | The Managing Partner co-signs all four engagement letters but holds zero participant edges, so the graph records no relationship at all between him and any client contact. |
| rf:graph-3 | graph_acl_naturalness | minor | d:0008 | The org's one multi-affiliation is modeled with zero slack: Golden changes employer on consecutive days and executes an engagement letter with her old advisors six days into the new job. |
| rf:narr-3 | narrative_consistency | minor | d:0003, d:0004, d:0005 | The same first-review milestone on the Woods valuation is reported complete, then back in progress, then complete again across four weeks, in three documents all reported by Sandra Perez. |
| rf:orgreal-2 | org_realism | minor | d:0007, d:0011 | The Managing Partner is a signature and a review promise only, never present in a working session, status report or readout across four engagements, which is how a partner behaves at a 500-person firm rather than at a five-person boutique. |
| rf:voice-7 | cross_document_voice | note | d:0001, d:0008 | Interpreting the report's one flagged pair: d:0001/d:0008 is the only pair in the corpus that reads as a real firm reusing its template, so the single similarity flag is a false alarm and the actual defect is inverted. |
| rf:graph-4 | graph_acl_naturalness | note | corpus | The three zero-mention external entities read as a genuine contact list rather than a gap; recording this as a strength so it does not get 'fixed'. |
| rf:graph-5 | graph_acl_naturalness | note | corpus | With acl_posture open, all five people hold byte-identical 19-document grants, so this fixture exercises the graph half of this dimension and none of the ACL half. |
| rf:narr-4 | narrative_consistency | note | d:0004, d:0005, d:0006 | The Woods valuation ran June to November 2020 and carries no trace of the conditions of its own moment; recorded as an omission, not a contradiction, since nothing in the corpus states anything false. |
| rf:orgreal-3 | org_realism | note | corpus | One of the three declared client organizations and two of the four external contacts never appear in any document, so the firm's documented client base across five years is two companies and two people. |
