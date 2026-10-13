# Generation report: hollowell-ip

Derived artifact: re-emit with `python -m orgsmith report hollowell-ip`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

64 documents planned; 56 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-5-5 | xhigh |
| wo:author:0002 | claude-opus-5-5 | xhigh |
| wo:author:0003 | claude-opus-5-5 | xhigh |
| wo:author:0004 | claude-opus-5-5 | xhigh |
| wo:author:0005 | claude-opus-5-5 | xhigh |
| wo:author:0006 | claude-opus-5-5 | xhigh |
| wo:author:0007 | claude-opus-5-5 | xhigh |
| wo:author:0008 | claude-opus-5-5 | xhigh |
| wo:author:0009 | claude-opus-5-5 | xhigh |
| wo:author:0010 | claude-opus-5-5 | xhigh |
| wo:author:0011 | claude-opus-5-5 | xhigh |
| wo:foundation:0001 | claude-opus-5-5 | xhigh |

Model cost: 56 of 64 documents were authored by a model, across 12 work order(s).

The other 8 cost zero model tokens: 8 static (rendered from the deterministic ledgers) and 0 derived (copied or transformed from committed DocIR by the noise stages). Derived documents are added by re-running the pipeline, never by dispatching an authoring batch.

## Integrity dashboard

Recomputation against ground truth. These hold exactly or the org is broken -- and they say nothing about how real the prose reads. No realism number appears here.

Validator: 31 rules run, 0 error(s), 0 warning(s); skipped by charter knob: NOISE-01, MENT-03, SCOPE-01, OUT-01, AFF-01, AFF-02, SCAN-01, SCAN-02, LEG-01.

Eval suites derive from the ledgers and score 100% by construction (`python -m orgsmith score hollowell-ip --suite ... --answers ...` grades an external system). Structure re-derives byte-identically from the recipe (the org-tier byte pin).

## Realism dashboard

Measurement and judgment: lengths, similarity, voice ranges, and the board's opinion. Nothing here gates, no threshold is validated, and no integrity number appears here.

### Length against brief

56 authored documents, 26760 words, mean 478.

Off brief (outside 75%-150% of target):

| doc | genre | words | target | ratio |
| --- | --- | ---: | ---: | ---: |
| d:0059 | engagement_email | 63 | 250 | 0.25 |
| d:0058 | engagement_email | 75 | 250 | 0.30 |
| d:0020 | engagement_email | 94 | 250 | 0.38 |
| d:0019 | engagement_email | 114 | 250 | 0.46 |
| d:0018 | engagement_email | 120 | 250 | 0.48 |
| d:0047 | engagement_email | 129 | 250 | 0.52 |
| d:0008 | engagement_email | 142 | 250 | 0.57 |
| d:0048 | engagement_email | 148 | 250 | 0.59 |
| d:0009 | briefing_deck | 265 | 400 | 0.66 |
| d:0049 | engagement_email | 177 | 250 | 0.71 |
| d:0021 | engagement_email | 179 | 250 | 0.72 |
| d:0057 | engagement_email | 179 | 250 | 0.72 |
| d:0006 | engagement_email | 187 | 250 | 0.75 |

### Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.126).

### Structural similarity

The 10 strongest of 243 same-genre pairs, ranked by structure rather than by wording. `shape` compares the block skeleton and `openers` compares the first content word of each prose unit; neither carries an authored sentence, so a thorough paraphrase moves the lexical column and leaves these two standing. Jaccard is repeated here so the reader sees which axis found the pair. Nothing here gates and no cut point is validated (docs/REVIEW-CALIBRATION.md).

| doc a | doc b | genre | shape | openers | jaccard |
| --- | --- | --- | ---: | ---: | ---: |
| d:0020 | d:0032 | engagement_email | 0.9091 | 0.5455 | 0.0 |
| d:0018 | d:0020 | engagement_email | 0.8 | 0.6 | 0.0 |
| d:0048 | d:0059 | engagement_email | 0.6667 | 0.6667 | 0.0 |
| d:0018 | d:0032 | engagement_email | 0.7273 | 0.5455 | 0.0 |
| d:0046 | d:0057 | engagement_email | 0.7273 | 0.5455 | 0.0 |
| d:0006 | d:0018 | engagement_email | 0.9091 | 0.3636 | 0.0 |
| d:0002 | d:0025 | internal_email | 1.0 | 0.25 | 0.0 |
| d:0025 | d:0052 | internal_email | 1.0 | 0.25 | 0.0 |
| d:0046 | d:0048 | engagement_email | 0.8 | 0.4 | 0.003 |
| d:0046 | d:0060 | engagement_email | 1.0 | 0.2 | 0.0 |

243 pairs were scored; the artifact keeps the strongest 50 and this table shows the top 10. The full ranking is recomputable from committed DocIR (`orgsmith.review.structure.compute_pairs`); it is truncated here rather than dropped silently.

### Fee coverage

5 documented engagement(s), fees totalling $362,000, against $17,091,000 of lifetime revenue.

Documented fees are 2.1% of lifetime revenue.

The recipe declares the engagement book a sample (engagements.book_is_sample), so the firm overview presents these engagements as representative rather than complete. The gap between fees and revenue is expected and coherent.

### Cross-document voice

Pre-registered voice patterns over 56 authored documents. This is a RANGE across strict and loose readings, not a single count: no ledger owns whether two sentences are the same figure, so the strict rows disagree and the plain words sweep up ordinary English. Nothing here gates.

| pattern | reading | occurrences | docs |
| --- | --- | ---: | ---: |
| `antithesis-strict-now-than-later` | rather ... now/early ... than ... later/late (the temporal contrast, strictly read) | 0 | 0 |
| `antithesis-strict-now-than` | rather ... (now\|early\|first) ... than (the contrast without its second pole) | 0 | 0 |
| `antithesis-loose-rather-word-than` | rather <word> ... than (any near-adjacent rather/than pairing) | 0 | 0 |
| `antithesis-plain-rather-than` | the plain words 'rather than' (sweeps up ordinary English) | 5 | 5 |
| `two-asks-opener` | 'Two asks. First ... Second ...' engagement-email opener | 0 | 0 |
| `workstreams-heading` | a 'Workstreams' section heading (the kickoff-memo template) | 0 | 0 |
| `next-steps-heading` | a 'Next Steps' section heading (kickoff and deck closer) | 0 | 0 |

### Numbers no ledger owns

0 number(s) in authored prose that no ledger value accounts for, across 0 of 56 documents (distinct values per document; values under 10 and years not counted). The airlock keeps the model from transcribing a value the ledger owns; it does not keep it from inventing one, and an invented number is one the answer key cannot score. A measurement, never a gate.

### Per-author similarity proxies

Per-author 4-gram Jaccard proxies, computed with no model: within is an author's own doc pairs, cross is their docs against every other author's, early/late is the overlap of the author's first-half shingles with their second half in date order (consistency over time). Ranges beside the tic table above, never gates: similarity is structurally blind to template collapse (docs/REVIEW-CALIBRATION.md), so this is context for the board's voice reading, not a verdict.

| author | docs | within mean (min-max) | cross mean | early/late |
| --- | ---: | --- | ---: | ---: |
| p:ashley.williams | 5 | 0.0018 (0.0000-0.0067) | 0.0008 | 0.0043 |
| p:david.chang | 5 | 0.0025 (0.0000-0.0114) | 0.0008 | 0.0059 |
| p:heather.munoz | 10 | 0.0019 (0.0000-0.0188) | 0.0006 | 0.0049 |
| p:joseph.walker | 3 | 0.0057 (0.0000-0.0170) | 0.0006 | 0.0154 |
| p:kelly.snyder | 5 | 0.0007 (0.0000-0.0025) | 0.0004 | 0.0010 |
| p:mary.bradley | 21 | 0.0041 (0.0000-0.1260) | 0.0006 | 0.0486 |
| p:matthew.parrish | 1 | - | 0.0002 | - |
| p:richard.henderson | 6 | 0.0042 (0.0000-0.0288) | 0.0008 | 0.0032 |

### Review board

40 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:cdv-kickoff-moves | cross_document_voice | major | d:0005, d:0016, d:0031, d:0044, d:0055 | The five kickoff memos, by five different authors over six years, make the same opening moves in the same order (what 'we owe' the client, 'our contact' by name and title, 'the fee is fixed, so') and two pairs close on the same couplet, so the memos read as one writer filling one form in varied words. |
| rf:cdv-status-reskin | cross_document_voice | major | d:0023, d:0051, d:0062 | Ashley Williams's 2024 trademark-clearance status report is Richard Henderson's 2020 freedom-to-operate report re-skinned section by section, and Henderson's two-tier contact closer reappears in David Chang's 2025 report, so three authors on three service lines share one report. |
| rf:cdv-thread-openers | cross_document_voice | major | d:0006, d:0017, d:0045, d:0056 | Four of the five engagement threads, opened by four different people between 2019 and 2025, begin by announcing the thread itself, two of them in a near-identical pair of sentences, so the brief's instruction to set the thread up shows through as one writer's opener. |
| rf:doc-plausibility-no-docket-or-date | document_plausibility | major | corpus | No email, letter, memo or set of minutes shows a docket or matter number, though the firm's own documents say every client update cites one, and no memo, minutes or status report states its own date. |
| rf:doc-plausibility-no-identifiers | document_plausibility | major | corpus | Nothing the practice works on is ever identified or counted: no patent or application number, no mark, product, cited reference or examiner, and no count of families or references, so an IP practice's files read as if redacted. |
| rf:doc-plausibility-no-location | document_plausibility | major | d:0004, d:0015, d:0030, d:0043, d:0054, d:0037, d:0063 | The firm has no location: all five engagement letters choose 'the law of the state in which our office is located' without naming the state, the letterhead carries only a web address, and the overviews' contact sections give no address, phone or email. |
| rf:doc-plausibility-thread-regression | document_plausibility | major | d:0021, d:0049, d:0060, d:0017, d:0045, d:0056 | In each of the three five-message client threads the final reply regresses against the history quoted directly beneath it, reporting as news a stage the thread passed days earlier and asking again for what was already supplied. |
| rf:finance-1 | finance_realism | major | d:0043, d:0051 | A US-only trademark clearance of one proposed name carries a $48,000 fixed fee, an order of magnitude above what clearance work is billed at and more than the firm charges for a full patent licensing diligence. |
| rf:finance-2 | finance_realism | major | d:0001, d:0041, d:0053 | Travel runs at 6-8% of fees, about $20,000 per head a year, and exceeds Office & Facilities in FY2023 and FY2024: a consulting firm's travel line on a desk-bound patent prosecution boutique. |
| rf:graph-1 | graph_acl_naturalness | major | d:0005, d:0044 | Two kickoff memos address a colleague by name and give them named work, but the ACL denies each of them the folder the memo is filed in, so the people graph and the permissions graph disagree about who is on the matter. |
| rf:graph-2 | graph_acl_naturalness | major | d:0007, d:0025, d:0031 | The corpus says the Docketing Manager enters and reconciles every matter's dates, yet she can read all eight FY financial summaries and not one engagement document. |
| rf:narrative_consistency-1 | narrative_consistency | major | d:0017, d:0021, d:0045, d:0049, d:0056, d:0060 | In all three five-message client threads, the last reply puts the matter back at an earlier stage than the thread's own first message and asks again for material already received. The rendered reply quotes the messages it contradicts directly beneath it. |
| rf:narrative_consistency-2 | narrative_consistency | major | d:0043, d:0044, d:0048, d:0050, d:0051 | The engagement letter and kickoff memo give the Jackson Inc trademark analysis to associate Kelly Snyder. From the working session onward, patent agent Ashley Williams reviews the search reports and drafts the analysis, although her own kickoff memo says patent agents cannot do trademark work. |
| rf:org_realism-1 | org_realism | major | d:0007, d:0037, d:0043, d:0044, d:0050, d:0051 | The firm's one trademark matter is run and substantively drafted by a patent agent, inside a self-described patent-only practice whose own kickoff memo says its patent agents cannot do trademark work. |
| rf:cdv-counsel-disclaimer | cross_document_voice | minor | d:0021, d:0045, d:0051, d:0056, d:0060 | Three patent agents on three engagements (2020, 2024, 2025) close their client updates on one disclaimer in paraphrase (no view yet; the partner will give it, in writing, once the work is done), so a line a real firm would either standardize or leave to each writer reads as one hand. |
| rf:cdv-midpoint-opener | cross_document_voice | minor | d:0011, d:0023, d:0034, d:0051, d:0062 | All five midpoint status reports, by five different authors, open by announcing that the work is at its midpoint and on schedule, the brief's position note restated as a topic sentence, and two carry 'midpoint' into a heading. |
| rf:cdv-partner-gloss | cross_document_voice | minor | d:0018, d:0020, d:0046 | When a partner steps into an agent's client thread, Heather Munoz in 2020 and Mary Bradley in 2024 make the same move in the same words: take up the second item of the agent's list and ask for the document itself, not a summary of it. |
| rf:cdv-persona-transplant | cross_document_voice | minor | d:0007, d:0011, d:0029, d:0031, d:0042 | Roster persona sketches are quoted into the documents as colleagues' narration or as firm doctrine, so one person's distinguishing habit turns up in another's mouth or in firm copy written before that person joined, and the habits stop marking anyone. |
| rf:cdv-self-nickname | cross_document_voice | minor | d:0033, d:0035 | Joseph Walker's own minutes describe him from outside, by his nickname in one and with credit for his own care in the other, though both name him as the note-taker and narrate the team as 'we'. |
| rf:doc-plausibility-letter-form | document_plausibility | minor | d:0004, d:0015, d:0030, d:0043, d:0054 | The managing partner's five engagement letters share no firm form: standard terms are redrafted in each, and the liability clause flips between disclaiming any limit and capping liability at fees paid. |
| rf:doc-plausibility-role-inversion | document_plausibility | minor | d:0005, d:0016, d:0044, d:0055, d:0010, d:0013, d:0022, d:0024, d:0050, d:0061, d:0064 | Who writes what is inverted: non-attorney patent agents issue four of the five kickoff memos assigning work to partners and associates, while a partner or the managing partner writes seven of the nine sets of minutes with juniors in the room. |
| rf:finance-3 | finance_realism | minor | d:0014, d:0027, d:0036 | Travel collapses in FY2020 and then comes back above its pre-pandemic level in FY2021, a year in which a firm like this was still mostly not traveling. |
| rf:finance-4 | finance_realism | minor | d:0001, d:0003, d:0014, d:0027, d:0036, d:0040, d:0041, d:0053 | Every financial summary labels the firm's only revenue line 'Consulting revenue', a term a patent law PLLC would not use for its legal fees. |
| rf:finance-5 | finance_realism | minor | d:0001, d:0003, d:0014, d:0027, d:0036, d:0040, d:0041, d:0053 | Office & Facilities repeats to the dollar for four years running, twice, which reads as a plug figure rather than an occupancy line. |
| rf:graph-3 | graph_acl_naturalness | minor | d:0029, d:0042, d:0043, d:0055 | Each matter folder is restricted to its three-person team, so the Partner every prosecution staffer reports to cannot open the two most recent matters, though her own reports staff both. |
| rf:graph-4 | graph_acl_naturalness | minor | d:0012, d:0025, d:0039 | Every employee can read the personnel onboarding records and the one-to-one mail, but only two people can read the financial summaries, which puts sensitivity the wrong way round. |
| rf:graph-5 | graph_acl_naturalness | minor | d:0033, d:0035 | The recipe's one nickname goes to an associate and appears only in minutes he wrote himself, where he calls himself 'Joe' in the third person while a second Joseph is in the room. |
| rf:graph-6 | graph_acl_naturalness | minor | d:0013, d:0033, d:0058, d:0061 | Across 56 documents and seven years of patent work, the only people named are the ten staff and one business officer per client. Every inventor, examiner, client engineer, licensor's counsel and foreign associate goes unnamed, even in minutes of calls with them. |
| rf:narrative_consistency-3 | narrative_consistency | minor | d:0043, d:0044, d:0045, d:0047, d:0049, d:0050, d:0051 | Until 10 May 2024 the Jackson Inc clearance concerns a single chosen name. From then on it covers a ranked slate of candidate marks, but no document records the client adding names, and by then the window the letter allowed for alternatives had already closed. |
| rf:narrative_consistency-4 | narrative_consistency | minor | d:0004, d:0005, d:0009, d:0011, d:0013 | The Odonnell portfolio review's letter and kickoff memo exclude office-action work. The later status report and November minutes nonetheless have the firm drafting office-action responses and promising extensions, with Amanda Schwartz moved from title work onto the pending applications. |
| rf:narrative_consistency-5 | narrative_consistency | minor | d:0031, d:0033, d:0034 | The Keith-Duarte minutes say Kelly Snyder's summaries already lead with the decision and its date, then assign her to recast them into that 'new format'. The next status report says they 'now' lead that way. |
| rf:narrative_consistency-6 | narrative_consistency | minor | d:0023, d:0024, d:0026 | The September 2020 Middleton status report lists the file-history reading as complete, then calls it the largest open item later in the same report. Later documents treat that reading as ongoing work. |
| rf:org_realism-2 | org_realism | minor | d:0002, d:0052, d:0039, d:0038 | The roster has no paralegal, legal assistant or office administrator, so the firm's housekeeping mail comes from fee earners while its one non-practitioner, the Docketing Manager, sends none. |
| rf:org_realism-3 | org_realism | minor | d:0004, d:0015, d:0030, d:0043, d:0054, d:0006, d:0008, d:0017, d:0056, d:0038 | The firm has no home: no document names its city or state, every engagement letter avoids naming its governing law, and the signature blocks of a firm with one office carry four metro area codes. |
| rf:org_realism-4 | org_realism | minor | d:0030, d:0035 | Prosecution Support is shaped as a five-month fixed-fee project that ends by handing live applications, one still under rejection, back to a client whose only contact is its General Manager, with no withdrawal or successor counsel. |
| rf:org_realism-5 | org_realism | minor | d:0004, d:0015, d:0019, d:0030, d:0037, d:0043, d:0054 | The client book reads as generated: five surname-compound company names, one styled like a law or accounting partnership, each instructed by a general business officer and never by in-house counsel or an engineer. |
| rf:cdv-voice-present | cross_document_voice | note | corpus | Sentence-level voice does differ by author and holds across years; the convergence in the findings above lies in per-genre rhetorical moves, and the structural metric's top pairs are mostly one person's own email habits, which is plausible. |
| rf:doc-plausibility-doctrine-sound | document_plausibility | note | corpus | The doctrinal and procedural content is accurate for the genre and the year, so the defects above are structural omissions, not domain ignorance. |
| rf:narrative_consistency-7 | narrative_consistency | note | d:0011, d:0021, d:0049, d:0060 | Findings 1 through 4 each start at the first document of a new authoring work order, so a matter's history appears to break where its documents were split across batches. This is an observation about the pipeline; it claims no further defect. |
| rf:org_realism-6 | org_realism | note | d:0015, d:0022, d:0042, d:0054 | Outside the trademark matter, titles and the agent/attorney boundary are handled the way a real patent boutique handles them, including the patent-agent-to-associate promotion. |
