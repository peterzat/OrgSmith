# Generation report: northgate-staffing

Derived artifact: re-emit with `python -m orgsmith report northgate-staffing`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

76 documents planned; 54 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-5 | xhigh |
| wo:author:0002 | claude-opus-5 | xhigh |
| wo:author:0003 | claude-opus-5 | xhigh |
| wo:author:0004 | claude-opus-5 | xhigh |
| wo:author:0005 | claude-opus-5 | xhigh |
| wo:author:0006 | claude-opus-5 | xhigh |
| wo:author:0007 | claude-opus-5 | xhigh |
| wo:author:0008 | claude-opus-5 | xhigh |
| wo:author:0009 | claude-opus-5 | xhigh |
| wo:author:0010 | claude-opus-5 | xhigh |
| wo:author:0011 | claude-opus-5 | xhigh |
| wo:author:0012 | claude-opus-5 | xhigh |
| wo:author:0013 | claude-opus-5 | xhigh |
| wo:foundation:0001 | claude-opus-5 | xhigh |

Model cost: 54 of 76 documents were authored by a model, across 14 work order(s).

The other 22 cost zero model tokens: 9 static (rendered from the deterministic ledgers) and 13 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 34 rules run, 0 error(s), 0 warning(s); skipped by charter knob: AFF-01, AFF-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score northgate-staffing --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

54 authored documents, 30841 words, mean 571.

Every document is within 75%-150% of the words its brief asked for.

### Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0011 | d:0029 | engagement_letter | 0.2409 |

### Fee coverage

6 documented engagement(s), fees totalling $500,500, against $20,712,000 of lifetime revenue.

Documented fees are 2.4% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 54 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 9 | 8 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 57 | 33 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:david.weiss | 4 | 0.0038 (0.0000-0.0142) | 0.0011 | 0.0023 |
| p:james.grant | 7 | 0.0009 (0.0000-0.0058) | 0.0017 | 0.0020 |
| p:james.weiss | 1 | - | 0.0004 | - |
| p:jason.bell | 4 | 0.0000 (0.0000-0.0000) | 0.0010 | 0.0000 |
| p:jeffrey.patterson | 4 | 0.0046 (0.0010-0.0119) | 0.0019 | 0.0060 |
| p:john.chang | 2 | 0.0151 (0.0151-0.0151) | 0.0014 | 0.0151 |
| p:kelly.chavez | 16 | 0.0112 (0.0000-0.2409) | 0.0006 | 0.0682 |
| p:nicole.donovan | 7 | 0.0020 (0.0000-0.0172) | 0.0014 | 0.0018 |
| p:sandra.fuentes | 9 | 0.0024 (0.0000-0.0233) | 0.0012 | 0.0018 |

### Review board

37 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:voice-1 | cross_document_voice | blocker | d:0021, d:0039 | Two kickoff memos two years apart, signed by two different research associates, are the same memo re-skinned: same five numbered owners in the same order, same open-questions pair, and a three-paragraph close that runs sentence for sentence. |
| rf:narr-1 | narrative_consistency | blocker | d:0063, d:0062, d:0061 | The closing status report on the Hicks-Castillo benchmarking describes a different engagement from the five documents in front of it: a different unit of scope, a different count, a different client body, and none of the open items the October session left. |
| rf:voice-2 | cross_document_voice | major | d:0005, d:0013, d:0022, d:0031, d:0040, d:0059 | Every engagement-opening email follows one script across five different authors: status line, 'I am starting this thread so the running record lives in one place', two asks (ninety minutes for a session, a ruling on off-limits companies), then a conditional close trading a client deadline for a firm deliverable. |
| rf:voice-3 | cross_document_voice | major | corpus | The 'one thing everything else waits on' construction the previous board flagged has survived the regeneration in paraphrase: fourteen documents nominate a single gating item, across eight authors, five genres and 2015-2023, with the wording varied just enough that the n-gram metric cannot see it. |
| rf:voice-4 | cross_document_voice | major | d:0034, d:0046 | Consecutive-engagement status reports by two different authors carry the same risk taxonomy in the same order with clause-level phrasing in common, so the status-report template collapse the previous board found is reduced rather than gone. |
| rf:voice-5 | cross_document_voice | major | d:0011, d:0029 | In the pair the similarity metric flagged, the copied passage is the 'Your Team' paragraph, and it transplants one consultant's distinguishing habit onto another, so the characterization reads as decoration rather than as a description of a person. |
| rf:docplaus-1 | document_plausibility | major | d:0009, d:0051 | Both firm-wide mundane emails are addressed only to the all-staff list yet open by greeting one person by first name, then refer to that same person by full legal name in the third person. |
| rf:docplaus-2 | document_plausibility | major | d:0005, d:0003 | The first client email attaches the firm's internal kickoff memo verbatim, a document that discusses how to manage that client and disputes his brief. |
| rf:docplaus-3 | document_plausibility | major | d:0040, d:0041, d:0042, d:0043, d:0032 | The demonstrator mail threads answer client replies that exist nowhere in the file, and each 'RE:' is threaded as a reply to the firm's own previous message rather than to the client. |
| rf:docplaus-4 | document_plausibility | major | d:0063, d:0061, d:0062, d:0060 | The closing status report on the Hicks-Castillo benchmarking describes a materially different piece of work from the rest of that engagement's own file. |
| rf:finance-1 | finance_realism | major | d:0048, d:0050, d:0053, d:0055, d:0052 | The ledger books 2020 as a normal 10% growth year and puts travel spend at its all-time high in 2020 and 2021, which is the wrong shape for a retained search boutique in those two years and the opposite of what the firm's own 2021 overview describes. |
| rf:finance-2 | finance_realism | major | d:0057, d:0061, d:0062, d:0063 | The Hicks-Castillo closing report delivers 57 benchmarked roles across five job families, plus an unplanned internal equity read and a free reissue, against the same unchanged fixed fee that every earlier document in the file says bought eleven positions. |
| rf:graphacl-1 | graph_acl_naturalness | major | d:0003, d:0058 | Two kickoff memos address a colleague on the To/Cc line and hand them a task inside a folder that colleague cannot open. |
| rf:graphacl-2 | graph_acl_naturalness | major | d:0009, d:0051, d:0056 | Internal administrative mail is sent by whoever, not by the person who holds the function: four of the five internal emails come from someone other than the Office Manager, and each defers the actual ownership to somebody else. |
| rf:narr-2 | narrative_consistency | major | d:0009, d:0051 | Two of the five internal broadcast emails greet one person by first name and then, in the same short note, refer to that same person in the third person and tell the reader to go to them, so the note instructs its own addressee to contact himself. |
| rf:orgreal-1 | org_realism | major | d:0020, d:0021, d:0024, d:0057, d:0061, d:0063 | On two engagements a Research Associate is the client's de facto lead: the periodic report the client reads goes out over the associate's name with no consultant on it, contradicting the engagement letter that named a consultant as the client's first call. |
| rf:orgreal-2 | org_realism | major | d:0017, d:0025, d:0027, d:0047, d:0049, d:0054 | The 2023 roster is six Research Associates behind three working consultants, with the Research Consultant rung vacant since mid-2018 and not one associate promoted in seven years, at a firm whose entire business is other people's careers. |
| rf:voice-6 | cross_document_voice | minor | d:0017, d:0025, d:0027, d:0047, d:0049, d:0054 | The six onboarding records hit the same beats in the same order, including a 'from the outside this looks like clerical work' paragraph and the same hour with the Managing Director described as the one conversation nobody skips. |
| rf:docplaus-5 | document_plausibility | minor | d:0026 | A note sent to a single colleague carries a paragraph plainly written for the whole office. |
| rf:docplaus-6 | document_plausibility | minor | d:0056 | A Research Associate chases two colleagues for timesheets and speaks for the monthly close, which is the Office Manager's work in this firm. |
| rf:finance-3 | finance_realism | minor | d:0002, d:0035, d:0053 | The P&L absorbs candidate and consultant travel wholly as firm cost, with a single revenue line and no reimbursement line, in a firm whose every engagement letter bills exactly that travel to the client at cost. |
| rf:finance-4 | finance_realism | minor | d:0001, d:0010, d:0019, d:0028, d:0037, d:0048, d:0050, d:0053, d:0055 | Across eleven years the statements contain no down year, no lumpy expense and no one-off item: revenue, compensation and professional services rise in every single transition, and facilities moves only in two exact steps. |
| rf:graphacl-3 | graph_acl_naturalness | minor | corpus | The permission set has no residue: every one of the 12 read sets is reproducible in closed form from the participant ledger, with zero stale, courtesy, or leftover grants across nine years. |
| rf:graphacl-4 | graph_acl_naturalness | minor | d:0052, d:0047, d:0049 | Three of the six research associates are inert in the graph, and the two most inert are named exactly twice each, which is the recipe's minimum-mentions floor showing through. |
| rf:graphacl-5 | graph_acl_naturalness | minor | d:0035, d:0006, d:0023 | Every client has exactly one contact and their titles come from a two-value pool split evenly three and three, so no search in the book was retained by the kind of buyer the firm's own overviews say retains it. |
| rf:narr-3 | narrative_consistency | minor | d:0046, d:0040, d:0044 | The General Counsel search reports more approaches than its own closed target lists can supply, and more sub-title candidates in conversation than the widened pass produced. |
| rf:narr-4 | narrative_consistency | minor | d:0011, d:0029 | The engagement letter for Davis and Sons hands James Grant, word for word, the personal habit the roster records as Jeffrey Patterson's, so the same Managing Director sells two clients the same distinguishing trait in two different men. |
| rf:narr-5 | narrative_consistency | minor | d:0047, d:0049, d:0054 | Three of the six onboarding records place the joining date a week away from the start date the roster holds, and one of them names the wrong day of the week. |
| rf:narr-6 | narrative_consistency | minor | d:0040, d:0041, d:0042, d:0043 | The four-message client thread holds only Northgate's outbound side, yet the later messages answer things the client said, so the record depends on messages the file does not contain. |
| rf:narr-7 | narrative_consistency | minor | d:0007 | The only use of James Grant's nickname in the whole corpus sits in the client-facing minutes he took himself, where he records one action under 'Jim' in the narrative and under 'James Grant' in the action table. |
| rf:orgreal-3 | org_realism | minor | d:0052 | The 2021 firm overview asks 'Who actually does the work?' and then names two junior researchers and no consultant at all. |
| rf:orgreal-4 | org_realism | minor | d:0009, d:0045, d:0051, d:0056 | Four of the five internal administrative notices are sent by consultants, the Managing Director, or a research associate, at a firm that employs an Office Manager to do exactly that. |
| rf:orgreal-5 | org_realism | minor | d:0002, d:0011, d:0020, d:0023, d:0029, d:0038, d:0057 | Every client contact across six engagements and nine years is a Chief Operating Officer or a General Manager; no chief executive, head of HR, or board chair ever appears, and the board director search is run entirely through a management officer. |
| rf:voice-7 | cross_document_voice | note | corpus | Per-person voice is genuinely present in this corpus; what recurs is per-genre outline, so the defect sits at the level of what each document is asked to contain rather than at the level of how any one person writes. |
| rf:docplaus-7 | document_plausibility | note | d:0017, d:0025, d:0027, d:0047, d:0049, d:0054 | All six hire records land the same closing beat, and five of them refer to their own author in the third person while the sixth is in her first person. |
| rf:finance-5 | finance_realism | note | corpus | No defect claimed: the deterministic review sample for this org contains no financial document, so the reading list handed to this dimension holds nothing from the Finance folder. |
| rf:graphacl-6 | graph_acl_naturalness | note | corpus | The internal correspondence graph has no work edges: every engagement email is outbound to the client and every internal email is administrative, in the org built as the fleet's mail-heavy exemplar. |
