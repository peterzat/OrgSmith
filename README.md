# OrgSmith

Generate a complete, fictional company: a browsable file share full of real
`.docx`, `.pdf`, `.xlsx`, `.pptx`, and `.eml` documents (degraded scans and
pre-2007 `.doc`/`.xls`/`.ppt` binaries included, when the recipe asks),
plus a ground-truth ledger that knows every fact planted in them.

```
companies/northgate-staffing/
├── TOC.md
├── Engagements/
│   ├── Roach, Moss and Hall/
│   │   ├── 2015.08.17 - Engagement Letter - Roach, Moss and Hall - EXECUTED.pdf
│   │   ├── 2015.08.30 - Kickoff Memo - CFO Search.docx
│   │   ├── 2015.09.20 - Briefing Deck - Roach, Moss and Hall.pptx
│   │   ├── 2015.09.24 - Email 1 - CFO Search - Roach, Moss and Hall.eml
│   │   ├── Meeting Minutes 2015-10-05 - Roach, Moss and Hall.docx
│   │   └── 2015.10.15 - Status Report - Roach, Moss and Hall v2 FINAL.docx
│   ├── Sanchez-Baker/ ...
│   └── Hicks-Castillo/ ...              <- and three more searches
├── Finance/
│   ├── FY2014 Financial Summary.xlsx    ... through FY2022
├── Firm/
│   ├── Firm Overview 2015 v3.docx
│   ├── Firm Overview 2018 v3.docx
│   └── Firm Overview 2021 v3.docx
└── People/
    └── 2016.07.24 - Onboarding - Jason Bell.docx   <- and five more

companies/northgate-staffing-metadata/   <- ground truth for all of the above
├── foundation.json              # roster, org chart, personas, clients
├── ledger/                      # finance series, engagements, people graph
├── docplan/manifest.jsonl       # every doc: genre, date, authors, planted facts
├── docir/                       # authored text with facts still as placeholders
├── evals/                       # golden suites: retrieval, extraction, graph
└── state.json                   # resumable pipeline state
```

The documents are written by a frontier LLM, but every fact in them was
planted by deterministic Python before any prose existed. The model writes
only the text around `{{fact:...}}` placeholders whose values it is never
shown, so a fee or a date cannot be mistranscribed into a document.

OrgSmith runs as Claude Code skills rather than against an API, so authoring
bills to the Claude subscription you already have, needs no API keys, and the
deterministic stages (ledgers, rendering, validation) cost no tokens at all.
The writer is whatever model your session is set to, and OrgSmith pins none, so
[which one you pick is the one choice that changes your
corpus](#which-model-should-write-your-documents). We measured that rather
than guessed.

The result reads like a real firm wrote it: engagement letters on letterhead
with signature blocks, meeting minutes that name every attendee, spreadsheets
whose formulas recompute to the values the finance ledger says. The
`-metadata` directory is the answer key.

**Start here: [`northgate-staffing`](companies/northgate-staffing/).** The
firm above, 76 documents across eight years (63 authored and static, plus 13
derived noise files), its [answer key](companies/northgate-staffing-metadata/),
and its [data card](companies/northgate-staffing-metadata/DATA-CARD.md), which
states in one page what it exercises and what it does not. Real files in your
browser, nothing to clone, install, or authenticate. It is the org we consider
our best current example, so it is also the one our review board was pointed
at, and [every flaw it found is published
below](#what-is-not-modeled-today).

Six more companies are committed beside it, [the fleet](#what-ships-today)
exists to show breadth (1999–2025, legacy binaries, degraded scans,
departmental ACLs), not to be browsed end to end. You can also write a recipe
and generate your own.

## Who this is for

You are building something that has to operate over a real organization's
documents (retrieval, extraction, a people graph, an agent that navigates
a file share), and you need a corpus to develop against. Your options today
are limited:

- **Real corpora** are confidential, single-instance, and carry no ground
  truth. You cannot publish your benchmark, your collaborator cannot
  reproduce it, and "did the extractor get the fee right?" is answered by a
  human squinting at a PDF.
- **Public corpora** (Enron and its descendants) are real, which is their
  virtue and their problem: one organization, one era, one format profile,
  and still no answer key. Nobody labeled which message mentions which
  person under which alias.
- **Ad-hoc LLM generation** gives you plausible text with no ground truth
  at all. The model that wrote "the fee was $120,000" is the only record
  that the fee was $120,000, and if it wrote $12,000 in the spreadsheet
  nothing notices.

OrgSmith targets the specific gap: **a corpus you can publish, regenerate,
and check answers against.** Because deterministic code planted every fact
before any prose existed, every question has a computed answer:

- **Retrieval / RAG.** Which documents answer this question? The suite ships
  the expected document set per question.
- **Extraction.** What was the fee on E-2021-003, and where does it live?
  The suite ships the exact expected value, the source documents, and the
  *location class*, so you can score "found it in the body" separately from
  "found it on the signature page of a scanned PDF."
- **People-graph / entity resolution.** Who works with whom, who is the same
  person under a nickname, who changed employers mid-history? The answer key
  carries alias credit and per-ambiguity-class recall.
- **Access-control-aware systems.** Given this person's permissions, exactly
  which documents may they see? The visibility suite ships the exact set per
  person, recomputed from the recipe's ACL posture.
- **Heterogeneous "ugly" format handling.** This is the part most synthetic
  corpora skip entirely. Recipes can produce genuine pre-2007 OLE binaries,
  PDFs rasterized and degraded to look scanned, an invisible synthetic OCR
  layer with realistic corruptions, and image-only scans with no extractable
  text at all, each with the *true* page text archived as ground truth, so
  you can measure exactly what your OCR pipeline lost.

`score` grades an external system's answers against any suite with
per-question attribution, from nothing but the `evals/` directory. Retrieval
reports a strict exact-set headline plus macro precision/recall/F1 and the
rank-aware metrics (Recall@5, Recall@10, MRR, nDCG@10) computed from your
answer list's own order; extraction reports value accuracy and attribution
accuracy separately rather than only their conjunction; the people graph
reports per-edge-kind recall and optional dated-edge credit. Two keyless
retrievers ([docs/BASELINES.md](docs/BASELINES.md)) put a floor under all of
it, so you can tell a hard question from a structurally easy one. What counts
as a right answer is a versioned contract:
[docs/LABEL-POLICY.md](docs/LABEL-POLICY.md). Ground
truth scores 100% by construction, which is the sanity check that the
harness is measuring what you think.

This matters double if an AI is writing your retrieval system: an agent's
feedback loop is only as honest as the corpus it verifies against.

## Scale and representativeness

**OrgSmith generates specimens, not samples.** A committed org is a small,
fully-labeled artifact chosen to contain the *shapes* your system has to
handle. It is not a statistically faithful reproduction of a real company's
document footprint, and it is roughly two to four orders of magnitude away
from being one.

### What ships today

All eight fleet orgs are committed and public in [`companies/`](companies/):
every `<slug>/` is a real file share you can click through and every
`<slug>-metadata/` is its answer key, sitting right next to it. A ninth
committed org, the test fixture [`dev-mini`](companies/dev-mini/), sits beside
them. **If you are here to eyeball the output, read
[`northgate-staffing`](companies/northgate-staffing/) and stop.** The rest of
the table is here to show the axes the generator moves along (era, sector, ACL
posture, format mix, mail, noise), not to be read end to end.

**Unless you came for a specific hard case, in which case the exemplar is the
wrong org.** It is a clean, open-ACL, all-modern-format firm, and it
deliberately leaves most of the difficulty knobs off. Go straight to the org
that exercises what you need:

| you want | read |
| --- | --- |
| degraded scans with a synthetic OCR layer | [`saltmarsh-environmental`](companies/saltmarsh-environmental/), [`verdant-health`](companies/verdant-health/) |
| pre-2007 `.doc`/`.xls`/`.ppt` binaries | [`brackenridge-civil`](companies/brackenridge-civil/) |
| real multi-message mail threads | [`ashcombe-advisory`](companies/ashcombe-advisory/), [`hollowell-ip`](companies/hollowell-ip/), [`meridian-actuarial`](companies/meridian-actuarial/) |
| a restricted (departmental) ACL | [`calderwood-partners`](companies/calderwood-partners/), [`hollowell-ip`](companies/hollowell-ip/), [`meridian-actuarial`](companies/meridian-actuarial/), [`saltmarsh-environmental`](companies/saltmarsh-environmental/) |
| a fee that lives only on a signature page, or a date only in a filename | [`meridian-actuarial`](companies/meridian-actuarial/) |
| duplicate/draft/misfile noise around the answers | [`northgate-staffing`](companies/northgate-staffing/), [`calderwood-partners`](companies/calderwood-partners/), [`ashcombe-advisory`](companies/ashcombe-advisory/) |
| scale (218 documents) | [`calderwood-partners`](companies/calderwood-partners/) |

Every org's data card states its own feature matrix, so the table above is a
shortcut rather than the record.

Document spans below are the real dates on the files, not the window the
recipe allowed:

| company | docs | share | answer key | data card |
| --- | --- | --- | --- | --- |
| **the exemplar**, a 12-person executive search firm, 2015–2023, departmental ACL, mail threads, scans, both hard cases, the full noise suite | 76 | [northgate-staffing](companies/northgate-staffing/) | [key](companies/northgate-staffing-metadata/) | [card](companies/northgate-staffing-metadata/DATA-CARD.md) |
| 25-person management consultancy, 2008–2022, the largest here, duplicate/draft noise | 218 | [calderwood-partners](companies/calderwood-partners/) | [key](companies/calderwood-partners-metadata/) | [card](companies/calderwood-partners-metadata/DATA-CARD.md) |
| 16-person comms advisory, 2017–2024, the email pilot: real threads plus the full noise suite | 104 | [ashcombe-advisory](companies/ashcombe-advisory/) | [key](companies/ashcombe-advisory-metadata/) | [card](companies/ashcombe-advisory-metadata/DATA-CARD.md) |
| 12-person actuarial consultancy, 2016–2024, a roster that grows, real mail threads | 72 | [meridian-actuarial](companies/meridian-actuarial/) | [key](companies/meridian-actuarial-metadata/) | [card](companies/meridian-actuarial-metadata/DATA-CARD.md) |
| 10-person patent boutique, 2018–2025, real mail threads | 64 | [hollowell-ip](companies/hollowell-ip/) | [key](companies/hollowell-ip-metadata/) | [card](companies/hollowell-ip-metadata/DATA-CARD.md) |
| 9-person civil engineering firm, 1999–2007, every office doc a pre-2007 binary | 40 | [brackenridge-civil](companies/brackenridge-civil/) | [key](companies/brackenridge-civil-metadata/) | [card](companies/brackenridge-civil-metadata/DATA-CARD.md) |
| 10-person environmental consultancy, 2013–2021, scans and a departmental ACL | 40 | [saltmarsh-environmental](companies/saltmarsh-environmental/) | [key](companies/saltmarsh-environmental-metadata/) | [card](companies/saltmarsh-environmental-metadata/DATA-CARD.md) |
| 7-person healthcare advisory, 2020–2025 | 31 | [verdant-health](companies/verdant-health/) | [key](companies/verdant-health-metadata/) | [card](companies/verdant-health-metadata/DATA-CARD.md) |
| 7-person consultancy, 2019–2023, the test fixture | 23 | [dev-mini](companies/dev-mini/) | [key](companies/dev-mini-metadata/) | [card](companies/dev-mini-metadata/DATA-CARD.md) |

Eight fleet companies (plus `dev-mini`), 1999–2025: ~33 MB of browsable share, plus ~14 MB of ground truth beside it.

| | fleet |
| --- | --- |
| companies | 8 (+ `dev-mini`) |
| people (internal) | 101 |
| planned documents | 645 (507 model-authored + 73 deterministic workbooks + 65 derived noise) |
| engagements | 59 |
| mean words per authored doc | ~540 |
| mean length against what the brief asked | ~1.0 |

This is the fleet after the M13-M16 realism wave: each org was regenerated once,
wholesale, under recipes with the wave's knobs turned on (a business-day
calendar, a sample-book prose posture, a per-author style/voice layer, and,
where the recipe declares them, real mail threads and organizational noise),
then re-frozen. Every org is built on the full stack: rosters that hire,
promote, and lose people; expense lines each computed from what drives them;
document volume driven by the firm's real activity rather than a fixed skeleton.
Every org was authored by `claude-opus-4-8[1m]` at effort `xhigh`, and **every
authored document lands close to the words its brief asked for**. Each org
records what actually authored it, batch by batch, in its `GENERATION-REPORT.md`,
and ships its six-dimension adversarial board findings beside it.

Per company: 7–25 people, 31–218 documents, 4–22 engagements, a 5–15 year span.

By format: 314 `.docx`, 147 `.eml`, 65 `.pdf`, 64 `.xlsx`, 24 `.doc`, 20
`.pptx`, 9 `.xls`, 2 `.ppt`.

By genre: 126 engagement emails, 105 sets of meeting minutes, 76 status
reports, 73 financial summaries, 67 kickoff memos, 66 engagement letters, 64
onboarding records, 28 firm overviews, 22 briefing decks, 21 internal emails.

#### The largest org: calderwood-partners

[`calderwood-partners`](companies/calderwood-partners/) began as the M12
capability pilot and is now a regenerated member of the fleet (M16). It is the
largest committed org: **218 documents** (168 model-authored, 15 static
workbooks, 35 derived noise) for a 22-person, 25-seat management consulting firm
across 2008–2022, generated through the live airlock on `claude-opus-4-8[1m]` at
effort `xhigh`. It is the org to read for scale and for the duplicate/draft
noise distribution: a business-day calendar, an engagement book declared a
sample, deterministic duplicates and drafts, and the style/voice layer. Its
measurements and six-dimension board findings are in its
[`GENERATION-REPORT.md`](companies/calderwood-partners-metadata/GENERATION-REPORT.md),
and it validates clean (29 rules run, 0 errors). The full window-defeating
flagship is M18; this is the same capability at a tenth the scale.

#### The M14 email pilot

[`ashcombe-advisory`](companies/ashcombe-advisory/) began as the M14
email-first pilot and is now a regenerated member of the fleet (M16): a 16-seat
corporate communications and investor-relations advisory across 2017–2024, 104
documents, generated through the live airlock on `claude-opus-4-8[1m]` at effort
`xhigh`. It is the org to read for email realism. Under the optional
`doc_culture.mail` block, its engagement mail runs as real threads, **45
`.eml`, the largest mail presence in the fleet, across 6 threads up to depth
8**, with minute-granularity send times in declared business hours,
`In-Reply-To`/`References` chains, RE: subjects, derived quoted-history tails, a
deterministic To/Cc split, promotion-aware signature blocks, transmittal emails
carrying a kickoff memo as a byte-identical MIME attachment, a mundane
internal-email genre, and three distribution lists. It validates clean (30 rules
run, 0 errors) and scores 100% on all four eval splits. Its six-dimension board
findings ship in its
[`GENERATION-REPORT.md`](companies/ashcombe-advisory-metadata/GENERATION-REPORT.md).
The regeneration turned on `exempt_author_mentions`, so a mundane-email author
no longer names themselves in the third person; the recipient full-name device
that this required in the body remains a fleet-wide realism gap (above).

It is also the M15 noise workbench. **17 of its 104 documents are derived**
and cost zero model tokens: two exact duplicates, three drafts, three version
chains whose members diverge (so hash dedupe cannot collapse them), two
misfiled copies sitting in the wrong client folder, two dead templates full of
bracketed dummy fields, and three junk directories. One transmittal attaches
`_v3` of a kickoff memo while the share holds the final, so an agent that
trusts the attachment is reading a superseded document. Filenames decorate
themselves the way real shares do (`Copy of …`, `… (1)`, `… FINAL FINAL`,
`… EXECUTED DO NOT USE`). The whole layer landed as a pipeline re-run over the
committed DocIR: no authoring batch was dispatched, and its
`GENERATION-REPORT.md` states that cost as a count, not a claim. Every derived
document is labeled in the manifest and excluded from the `core` and
`distractors` eval splits automatically, so noise is ground truth rather than
a scoring hazard.

### Where that sits against a real firm

A real ten-person professional-services firm over eight years does not
produce 40 documents. It produces, very roughly:

- **Email in the tens of thousands.** Ten people sending even 20 messages a
  working day is ~400,000 messages over eight years. The fleet now ships **137
  `.eml` files** with real multi-message threads on three orgs (up to depth 8):
  email volume and thread mechanics were the largest fidelity gap. M14 addressed
  the *mechanics* (not
  the volume) with a committed email-first pilot, `ashcombe-advisory`: real
  threads with minute-granularity timing, `In-Reply-To`/`References` chains,
  quoted history, a To/Cc split, promotion-aware signatures, transmittal
  attachments, and mundane internal traffic. It ships 42 authored `.eml`
  (53% of its authored documents) across 6 threads up to depth 8. Volume
  remains document-dominant, by design (specimens, not samples).
- **Files in the thousands to hundreds of thousands**, most of them junk:
  drafts, near-duplicate versions, dead templates, misfiled scans, someone's
  lunch menu. OrgSmith ships 22–218 documents per company. Junk is now a
  recipe knob rather than an absence: `calderwood-partners` carries 35
  derived duplicates and drafts, and the noise workbench
  [`ashcombe-advisory`](#the-m14-email-pilot) carries 17 across six kinds
  (duplicates, drafts, diverging version chains, misfiles, dead templates,
  junk directories). Every junk file is labeled in the manifest and kept out
  of the clean eval splits, which is the part a real share cannot do for you.
  The gap that remains is proportion: real shares are mostly junk, and these
  are not.
- **A book of business far larger than the documented one.** Every org's
  engagement ledger is a deliberate sample: fees across it come to 1.6–5.1%
  of the revenue on the same firm's own financial summaries. Our review
  board caught the corpus mistaking that sample for the whole business, and
  the arithmetic is published rather than smoothed over (`BACKLOG.md`,
  `engagement-ledger-reads-as-whole-book`).
- **Documents 3–6× longer, fixed.** Real engagement letters run 800–1,500
  words; the pre-v2.0 fleet's authored mean was **236 words** against briefs
  asking 130–350. The model was roughly hitting its targets; the targets
  were wrong. M9 made length a per-genre property of the genre registry and
  raised engagement letters to 1,100. The fleet now authors clause-bearing
  engagement letters at **1,000–1,300 words**; the overall authored mean is
  **~540 words**, pulled down deliberately by the short email threads the
  realism wave added, and this length gap is closed.

There is no honest way to call 40 documents a sample of that. What it is: a
corpus where **every** hard case you care about is present, labeled, and
checkable. If your extractor cannot find a fee that exists only on the
signature page of a degraded scan, it will fail here, on 40 documents, in
under two seconds, with an exact answer key, instead of failing silently on
50,000 real ones.

### What is not modeled today

Our own adversarial review board read the exemplar above,
`northgate-staffing`, and said it better than we could. As of M17 that
exemplar is **regenerated again**, this time with the difficulty knobs on that
it used to leave off: a departmental ACL, real mail threads with mundane
internal traffic, scans with and without an OCR layer, a fee that lives only
on a signature page, a date that lives only in a filename, and the
alias-agreement discipline. So this section is not a list of knobs left off.
It is what the board found with them on.

The current findings are **2 blockers, 15 major, 16 minor, 4 notes across six
dimensions**, all in `companies/northgate-staffing-metadata/review/findings/`,
against a corpus that validates clean: 34 rules run, 3 skipped, 0 errors.

That is a lot more findings than the previous exemplar's eight, and the
increase is the point rather than a regression. The old org left most of the
hard knobs off, so most of the surface a reviewer could criticize did not
exist; turning them on created mail threads, a real access posture, and six
more engagements' worth of prose to be wrong about. A corpus that exercises
more has more to find. Read the count as coverage, not as decay, and read the
findings themselves rather than the number.

**First, what the wave closed on the exemplar itself.** The defects this
section used to quote at length are gone from `northgate-staffing`, fixed by
regenerating it rather than by our say-so:

- **The weekend and holiday meetings are gone** (`doc_culture.business_calendar`).
  The recipe now declares a calendar; validator rule CAL-01 keeps every
  `meeting_minutes` and engagement email on a business day. The previously-cited
  Saturday 2016-05-28 and 2023-07-04 (US Independence Day) client working
  sessions **no longer occur**. Those dates appear nowhere in the corpus.
- **The overview no longer overstates the book** (`engagements.book_is_sample`).
  Where the 2021 overview once called five engagements "a deliberately short
  list" of the firm's entire client base, it now reads "a representative
  handful, offered as examples... and not as a full account of our book." The
  underlying fee/revenue gap is unchanged by design (the knob fixes prose
  posture, not the ledger: documented fees are still ~2.4% of lifetime
  revenue), but no document now claims the sample is the whole business.
- **The reporting-line drift is gone**, fixed in the generator for every org.
  Onboarding prose that names a supervisor the ledger's `reports_to` edge
  contradicts is rejected at ingest (`authoring/ingest.py::_check_reporting_line`),
  verified live on the freshly authored prose.
- **The blatant template tics are gone.** The `Two asks. First… Second…`
  opener and the `Workstreams`→`Next Steps`→epigram kickoff skeleton the board
  used to count on every author do not appear in the regenerated exemplar; the
  `style_specs` + `voice_diversify` layer removed the named constructions.

**And what M17 closed on top of that.**

- **The `Jim` collision is gone by construction.** The retired exemplar's
  headline residual, caught independently by four of six reviewers, was a
  nickname the ledger registered to one James while a different James's
  model-authored persona claimed it, so the firm overview called the wrong man
  Jim and the prose faithfully reported a source that disagreed with itself.
  `graph_targets.alias_agreement` now rejects that at both ends: a persona
  claiming somebody else's registered nickname fails enrichment ingest, and
  authored prose using one where the plan placed no mention fails authoring
  ingest, with `MENT-03` enforcing the same on committed state. This turn's
  narrative reviewer verified the result independently: "Jim" occurs exactly
  once in 76 documents, in the one document whose plan places it. The alias is
  also recorded mechanically in `evals/diagnostics.json`, so the same class of
  defect is now visible without a board at all.
- **The exemplar poses the hard cases it used to advertise and skip.** A fee
  that lives only on a signature page, a date that lives only in a filename,
  scans with and without an OCR layer, a departmental ACL where twelve people
  hold read sets ranging from 0 to 76 documents, and mail that runs as real
  threads.

**Then, what the board found once those were fixed.** With the loud, checkable
defects closed, the board had to find subtler things, and the residue is more
honest about where the generator actually stands:

- **Cross-document voice is still the hard one, and it has no scheduled fix.**
  The M17 regeneration improved the *per-person* half measurably: three
  reviewers' minutes now read as three visibly different writers, and the
  five-status-reports-on-one-template collapse is reduced. What replaced it is
  the *per-genre outline*. Two kickoff memos by two authors two years apart are
  the same memo re-skinned, sharing sentences verbatim; six engagement-opening
  emails run one script across five authors. The same-genre n-gram metric saw
  one of those pairs and missed the rest, which is exactly why the board
  exists. Every document is authored by a fresh worker that never saw a
  sibling, so no author can self-check for it, and it is the one finding class
  present in **every org in the fleet**.
- **A document that describes a different engagement from its own folder.** The
  Hicks-Castillo closing report says five job families and 57 roles where the
  five documents before it in the same folder say eleven positions against a
  twenty-two-company comparison group. Three reviewers reached it independently
  from three dimensions. No planted fact is contradicted and the validator is
  clean, because position counts are prose rather than ledger facts, which is
  precisely the gap: the oracle cannot see a corpus contradicting itself in the
  space the ledger does not own.
- **The people-graph filler still shows a seam.** To satisfy a minimum-mentions
  target, a kickoff memo can name and task a colleague who is not an engagement
  participant, and the participant-scoped ACL then denies that same person read
  access to the very document that tasks them. Two mechanisms derived
  independently and never reconciled. It survived the regeneration.
- **The firm has no 2020.** Revenue rises 10% with no soft quarter, and the two
  largest travel years in an eleven-year ledger are the two years the sector
  could not fly, in a corpus whose own 2021 overview says more first meetings
  now happen over video. The finance model is a smooth growth curve with no
  shocks in it, which is the `event-simulation` entry in `BACKLOG.md` arriving
  as a finding.

**What M17b built in response, and what it does not yet claim.** The two
blockers above are one fact at two scales: every document is authored by a
fresh-context worker that never sees a sibling, so the corpus diverges where
continuity is required and converges where variation is required. M17b is the
capability turn that answers both, and **no fixture was regenerated for it**,
so every finding quoted above is still present in the committed exemplar. The
proof is the next flagship generation, not this turn.

- **Against divergence:** `engagements.scope` (default off) makes an
  engagement's unit of work, comparison group and funnel into planted facts,
  so a document cites a ledger object instead of inventing a number, and a
  document cites a funnel stage only once its own date says the stage is
  complete. Two reports on one engagement then state the same quantity because
  they cite the same fact id. `SCOPE-01` recomputes the planting from the
  charter; ingest rejects a literal count in prose. The Hicks-Castillo failure
  becomes inexpressible rather than merely unlikely.
- **Against convergence:** `doc_culture.outline_variety` (default off) has the
  plan deal each authored document a section skeleton from a per-genre pool,
  with no two consecutive same-genre documents sharing one, and authoring
  ingest enforces the skeleton it briefed -- including what an outline
  *forbids*, which is what stops "the same five numbered owners in the same
  order" recurring. What this proves today is plumbing and block-shape counts
  under a scripted author. **Whether real prose stops converging is settled by
  the next generation, and "impossible by construction" would be an overclaim:
  a finite pool cycles, and the guarantee is no adjacent and no
  within-engagement repeat.**
- **Against the measurement gap:** a structural similarity axis
  (`orgsmith/review/structure.py`) scores same-genre pairs on block skeleton
  and on positional openers, neither of which a paraphrase moves. Calibrated
  against this board's own findings in `docs/REVIEW-CALIBRATION.md`: it ranks
  the `rf:voice-1` blocker 5th of 161 pairs where the lexical metric does not
  flag it at all, and it **misses** `rf:voice-4` entirely at rank 78. It never
  gates.
- **Not addressed, and no keyless proxy will address it:** `rf:voice-3`, a
  single rhetorical move recurring in fourteen documents across eight authors
  and five genres, paraphrased each time. It is not a pair, not a shape, and
  not an n-gram. Recognizing it needs semantics, which is what the board is
  for.

**One fleet-wide artifact, half closed, and be precise about which half.**
The ingest mention check requires an email author to spell the recipient's
full legal name in the body, so the mail orgs put it there.
`mail.exempt_recipient_mentions` (M17) stops the planner *requiring* it, and on
the regenerated exemplar no person-to-person message plans a recipient mention
at all: the mechanism is gone.

The surface is not. Eight of the exemplar's fourteen person-to-person messages
still name a recipient in the body, now because an author chose to rather than
because a check demanded it, which is often what a real note does when a
colleague is copied. So the honest claim is that the *forcing* is closed, not
that the names are absent, and anyone measuring this should count planned
mentions rather than grep the bodies.

It is **not** closed on distribution-list mail. A broadcast's `To` header
carries the list address rather than member names, so `MENT-01` still needs the
body mention, and the result is a note that greets one person by first name and
then names them in full to the room (`BACKLOG.md`,
`mundane-broadcast-names-a-recipient-in-the-body`). Nor is it closed on
`hollowell-ip` and `meridian-actuarial`, which were not regenerated this turn;
their data cards record it. The related `To:/Cc:` banner bug was fixed in
v2.1.1 and a committed test asserts no fleet mail body carries a header banner.

**What we think is important about this exemplar.** The point of regenerating
`northgate-staffing` under the newest version of the framework is not that the
board fell silent. It did not. It is *which* findings survived. Everything the
generator can settle by construction (a business-day calendar, a sample-book
prose posture, reporting lines that match the graph, the named template
constructions), the wave settled cleanly and measurably, by turning a knob and
regenerating. What is left is the class of problem no ledger can adjudicate:
whether thirteen documents read as thirteen hands or one, and whether the
firm's own structured facts agree with each other before the prose ever renders
them. That is the honest frontier. A synthetic-org generator earns trust by
making its remaining failures smaller and more specific over time, and the
exemplar's residue is now a voice problem and a fact-consistency problem rather
than a calendar bug and an overstated brochure. The roadmap is scoped directly
from what is left.

Read the board sceptically, including here: it is the weakest instrument in
this repo, it has been caught publishing a checkable falsehood, and its
false-positive rate is unmeasured ([what this does not
prove](#what-this-does-not-prove)). Every finding quoted above was re-verified
against a ledger or the rendered artifact before it was published: the "Jim"
collision against `foundation.json` and the two documents, the duplicated
header against the rendered `.eml`, the calendar fix against the manifest. The
one thing no ledger can settle, whether two sentences are the same voice, is
labelled as the board's judgment, not rounded up into a fact.

**You can check that rather than take it: all eight orgs ship their own board
findings and their own numbers**, in each `GENERATION-REPORT.md`. The
regenerated fleet's documented fees run **1.1% to 3.5% of lifetime revenue**;
every overview now declares its book a sample, so the paperwork and the
financials describe one firm even where the gap persists.

That last part is where the fix bit hardest, and it is worth knowing why.
Fixing the lockstep finance made every recipe's *own* incoherence visible:
once compensation tracks a roster instead of tracking fees, a firm that
compounds revenue with a headcount that never moves posts a net margin
climbing toward 50%, which no professional-services firm does. The model was
right and the recipes were wrong. So each fleet recipe is now tuned until
its growth, headcount, and span describe one firm, measured from its own
finance ledger, recorded in the recipe, and re-checked on every test run
(`test_fleet_recipe_growth_headcount_and_span_describe_one_firm`). This is
the pattern worth stealing: when a fix reveals that your inputs were wrong,
the fix is not to soften the model.

[SPEC.md](SPEC.md) is the current unit of work and says exactly what it
commits to. Each turn's board findings stay committed next to the org they
judged. Cross-document voice is the genuinely hard one, and it has no
scheduled fix.

Out of scope by choice rather than pending: multi-org document exchange,
litigation-style volume, personal and off-topic content, adversarial or
malicious documents, and any human editing pass. Real duplicate and version
chains were on this list until M12 scoped them in: a flagship meant to test
retrieval needs a realistic denominator, and today every committed document is
deliberate. Not built yet; it is scope, not a feature.

Email thread mechanics were the largest gap above; M14 built the *mechanics*
and the M13-M16 wave turned them on across the fleet. Real threads (multi-turn
`.eml` with `In-Reply-To`/`References`, `RE:` subjects, To/Cc split, alternating
senders, promotion-aware signatures) now ship under the optional
`doc_culture.mail` block on the two mail demonstrators `hollowell-ip` and
`meridian-actuarial` (22 and 26 `.eml`, max thread depth 5 apiece) plus the
email-first pilot [`ashcombe-advisory`](#the-m14-email-pilot) (45 `.eml`, depth
8). What is still open is *volume*: even the pilot is document-dominant, and no
corpus here approaches an email-dominant one. The wave also surfaced a rendering
artifact on `hollowell-ip` (a duplicated recipient block in the mail bodies),
fixed in v2.1.1 (above).

**Choose accordingly.** If you need email or document *volume*, or a realistic
noise distribution, this is still the wrong tool today; if you need thread
*mechanics*, three orgs now carry them. If you need labeled hard cases,
format heterogeneity, reproducibility, and a corpus you can legally publish,
it is a good one. See [docs/SCALE.md](docs/SCALE.md) for the size targets
and the measurements behind them, including why a 2,000-document org at
today's lengths would still fit inside a 1M-token context window and
therefore prove nothing about retrieval.

## How it works

OrgSmith runs inside a [Claude Code](https://claude.com/claude-code)
session. Deterministic Python owns every fact; the model authors only
surface prose, through an airlock:

- Python never calls a model and never touches the network. Every model
  touchpoint is a CLI verb pair: `--emit-context`/`--next-batch` writes a
  self-contained JSON work order; `--ingest` validates the deliverable
  (pydantic + lints) and merges it. Skills are the only reader/writer of
  work orders.
- **That file exchange is the whole interface.** OrgSmith ships Claude Code
  skills as its driver, but nothing in the package knows what wrote a
  deliverable: anything that reads a `WorkOrder` and writes back an
  `AuthoringDeliverable` drives the pipeline: another harness, a plain API
  script, a local model, a replay of a previous run, or a human with a text
  editor. Both contracts are published as JSON Schema in
  [`schemas/`](schemas/) (`python -m orgsmith emit-schemas`), so you do not
  need to import Python to read them.
- **Bring your own token (optional, off by default).** That interface ships
  with a reference driver in [`drivers/`](drivers/):
  `python -m drivers.forge_external <slug>` generates a whole org through a
  provider you configure (OpenAI, Anthropic, Google, OpenRouter, or any
  OpenAI-compatible endpoint, including free-tier and local models). The point
  is cost and portability: author the model passes on a free-subscription
  token (a free Gemini or OpenRouter tier, or a local model at zero API cost)
  or your own key, instead of consuming Claude Code usage, and reproduce a
  corpus without the harness at all. See
  [`docs/BYO-AUTHORING.md`](docs/BYO-AUTHORING.md). The airlock is unchanged:
  the driver lives outside `orgsmith/`, which still never calls a model or
  touches the network.
- The model writes documents with `{{fact:...}}` placeholders and is never
  shown the underlying values. Python substitutes them at render time, so a
  number cannot be mistranscribed. Ingest rejects deliverables that miss a
  required placeholder, invent people, or write a literal value where a
  placeholder belongs.
- After rendering, a 37-rule validator ties every document back to the
  ledger: planted facts and planned name mentions appear verbatim in
  extractable text, hard-case location policies hold (a
  signature-page-only fee appears on exactly that pdf page and nowhere
  else; a filename-only date never appears in document text), access
  grants and PERMISSIONS.md match a recomputation from the recipe's ACL
  posture, workbook formulas recompute to ledger values, mail headers,
  signature blocks, and transmittal attachments recompute exactly from the
  ledgers and distribution lists expand for visibility, scan flags and
  legacy assignments
  recompute from the recipe (with raster pages, OCR-layer presence, and
  true-text archives verified), legacy binaries are real OLE containers,
  affiliation-aware client and participant assignments recompute from
  the charter (with every multi-affiliation person appearing under both
  employers), no generated name collides with a screened real firm,
  authors were employed on the date they wrote, org charts are acyclic,
  the people graph has no orphans or dangling edges, every file opens in
  its native reader, and every file carries a machine-readable
  synthetic-provenance marker.

```
charter -> foundation -> fabric -> docplan -> author -> render -> assemble
 (recipe)   (roster)    (ledgers)  (manifest)  (model)   (files)    (TOC)
              overlays:  acl (grants + PERMISSIONS.md)
              oracles:   validate / emit-evals / score / status / doctor
              contracts: emit-schemas (JSON Schema for every stage boundary)
```

Long runs checkpoint into `state.json`: kill the session mid-generation,
re-run `/forge <slug>`, and it resumes exactly where it stopped with no
duplicated or lost documents. Structure is fully seeded; the same recipe
regenerates the same org (ids, names, tree, numbers), with only the
model-authored prose varying.

### What it costs to generate

Roughly: only the authoring passes spend model tokens; the deterministic stages
(charter, foundation, fabric, docplan, render, assemble, validate) and the noise
stages spend zero by construction. The
exemplar `northgate-staffing` is 44 model-authored documents (~26,000 words)
across 11 batches: one persona-enrichment pass plus ten authoring work orders,
each a fresh-context worker that reads its work order and the schema contract,
authors four to six documents with extended reasoning, and self-checks. Measured
against this fleet's runs, a batch consumes on the order of 90k-130k tokens end
to end, roughly 80% input (the work order, ledger context, and sibling documents
read for voice) and 20% output (extended-reasoning plus the DocIR deliverable).
At retail Claude Opus rates ($15/M input, $75/M output) that is about $2.50-$3.50
a batch, so **on the order of $30 to author the exemplar**, call it $25-$40. Two
things move it: prompt-caching the shared schema and ledger context across a
batched run cuts the input half materially, and the figure is dominated by
extended-reasoning output at the `xhigh` effort we author on. The adversarial
board is a separate spend of similar size (six reviewers each read the whole
corpus once) and is review, not generation. Across the eight-org, ~600-document
fleet the generation cost scales with authored-document count, from ~15 batches
for the smallest orgs to ~37 for `calderwood-partners`.

## Why we think the output is any good

Any generator can claim quality. The question a researcher should ask is:
*what would catch you if you were wrong?* OrgSmith's answer is a deliberate
hierarchy, taken from [The Bitter Lesson of Agentic
Coding](https://agent-hypervisor.ai/posts/bitter-lesson-of-agentic-coding/):
**oracles beat proxies beat critics**, and you should know which one you are
relying on for any given claim.

**Oracles, strongest, and where all the facts live.** An oracle recomputes
the answer from ground truth. The 37-rule validator and the eval suites are
oracles: they do not ask whether a document *seems* right, they recompute
what it must contain from the ledgers and fail the org if it doesn't. This
is why the airlock exists: the model never sees a value it is placing, so
"the model transcribed the fee wrong" is not a bug class that can occur. It
is structurally impossible rather than tested-for.

**Proxies, weaker, cheap, and blind to different things than you are.**
`orgsmith report` computes corpus metrics with no model: each document's
length against the words its brief actually asked for, and same-genre n-gram
overlap. A proxy catches what the generator cannot see about itself. Ours
immediately found real literal reuse across two engagement letters that no
human reader in the project had noticed.

**Critics, weakest, and treated as such.** `/forge-review` dispatches a
board of fresh-context reviewers across six dimensions. A critic shares
blind spots with the generator that produced the text, so the board's scope
is exactly what no proxy reaches, above all **cross-document voice**, the
one dimension no author can ever self-check, because nothing in the pipeline
holds two authored documents at once. Every document is written by a fresh
worker that has never seen a sibling.

Three consequences worth being explicit about:

**Nothing that is not an oracle is allowed to gate.** No metric and no board
finding is a validator rule. Thresholds are unknown, and "when a measure
becomes a target, it stops being a good measure": a similarity rule would
just teach the generator to paraphrase. The metric measures, the board
judges, the human decides.

**Generation and evaluation are structurally separated, not politely
separated.** Agents asked to grade their own work confidently praise it. So
the board is read-only and never authored what it reviews; `bin/test` cannot
reach the board at all (a static test proves no tier can); and no LLM grades
an LLM anywhere in an automated path.

**We publish what the critic said about us.** Every org ships the board's
findings next to the documents they judge, unflattering ones included (8
of them against the current exemplar, 6 rated major), quoted at length
[above](#what-is-not-modeled-today). Two of those drove BACKLOG entries
carrying the arithmetic that proves them. The board's findings against the
*retired* exemplar drove milestones M8 and M9, and are why the frozen
roster, the clause-less contracts, and the lockstep finance are gone.
`docs/REVIEW-CALIBRATION.md` records the board being calibrated against two
hand-labeled defects before its findings were relied on, including the case
where it **overruled the metric** (judging a flagged similar pair to be
realistic template reuse) and the case where it caught what the metric
provably cannot see.

### Two dashboards, and the line between them

The hierarchy above is a claim about instruments. The reporting enforces it
as a layout: every org's
[`GENERATION-REPORT.md`](companies/ashcombe-advisory-metadata/GENERATION-REPORT.md)
carries two dashboards with a hard line between them, and no number is
allowed to appear in the other's context.

**Integrity** is recomputation against ground truth: validator results, the
eval suites scoring 100% *by construction* (the answer key is derived from
the same ledgers the documents are, so anything less is a broken org, not a
weak one), and the byte pin. These hold exactly or the org is broken. They
say nothing whatever about how real the prose reads, and reporting them as
if they did is the single most available way to overstate a synthetic
corpus.

**Realism** is measurement and judgment: length against brief, same-genre
similarity, per-author voice ranges, fee coverage, and the review board's
findings. Nothing here has a validated threshold, nothing here gates, and a
number moving in a direction we like is not evidence that it should have.
Fleet-wide distributions live in
[`docs/DISTRIBUTIONS.md`](docs/DISTRIBUTIONS.md), corpus shape per org plus
an aggregate, with reference lines that restate this README's
order-of-magnitude prose about real firms rather than any sampled
population. They are context for reading the gap, not a score
(`external-validity-program` in `BACKLOG.md` is open, and this does not
close it).

The practical test of the line: an integrity number can only ever be "holds"
or "the org is broken", so it deserves no celebration; a realism number can
move a long way and still not mean the corpus got better. Keeping them in
separate boxes makes it hard to quote one as the other.

### The evidence, concretely

- **886 tests** across the default three tiers (`bin/test`), keyless and
  offline (859 pass; the 27 skips are property tests stepping over orgs whose
  recipe leaves the feature under test off, each naming the org and the
  reason), plus a fourth `flagship` tier (70 tests) for the two
  large pilot orgs (`calderwood-partners` and the M14 email pilot
  `ashcombe-advisory`), run on their own so the everyday loop stays fast;
  the `org` tier validates the
  eight fleet fixtures (plus `dev-mini`), derives every recipe, re-derives every
  fixture's structure byte-identically, re-derives every answer key and every
  baseline summary, and checks each fleet recipe's internal
  coherence in ~11s, while `bin/test flagship` re-validates the two largest,
  `calderwood-partners` and `ashcombe-advisory`, in ~12s.
- **Determinism is enforced, not hoped for.** The same recipe regenerates
  byte-identical structure. Committed fixtures are frozen and every
  capability added since has had to keep them loading, validating, and
  regenerating unchanged, which is why derived artifacts (`evals/`,
  `acl.json`, PERMISSIONS.md, `GENERATION-REPORT.md`) are recomputed rather
  than stored.
- **Tamper evidence by construction.** Rules grandfather by *charter*, not
  by artifact absence: a knob that is on with its ground truth missing is a
  failure, so stripping the answer key out of a distributed org cannot pass
  validation.
- **The model choice is measured, not asserted.** See below.
- **The whole project is built this way.** Spec-driven turns, adversarial
  review with builder/verifier separation, and a pre-push gate that blocks
  unreviewed code, via [zat.env](https://github.com/peterzat/zat.env).
  `SPEC.md`, `CODEREVIEW.md`, and `SECURITY.md` are in the repo; read them
  to see what the review actually caught.

### What this does not prove

The board has been calibrated on one org, one model, one run, with no
negative control, so its false-positive rate is unmeasured, and it is not
zero. We have caught it inventing a checkable
falsehood: during the Round 2 A/B a reviewer asserted that two corpora
rendered byte-identical prose when all 22 documents differed, and it
attributed one arm's sentence to the other. That is one instance, not a
rate, and it is the reason every board finding quoted in this README was
re-verified against a ledger before publication. Treat the board as the
weakest instrument here, because it is.

The metrics have no validated thresholds either. And nothing here
establishes that a system which scores well on OrgSmith scores well on a
real corpus; the fidelity gaps above are the reason to doubt it. These
limits live in `docs/REVIEW-CALIBRATION.md`, `docs/MODEL-AB.md`, and
`BACKLOG.md` rather than being smoothed over.

## Which model should write your documents?

Short answer: **the strongest one you have, and the cheaper model is
probably not cheaper.** Long answer, because this is the one choice that
changes your corpus and the one thing no artifact can tell you about
afterward.

OrgSmith pins no model. The writer is whatever your Claude Code session is
set to, which makes this your decision on every run. It is also a decision
the rest of the system is structurally blind to: the validator checks that
documents agree with their ledgers, and a thin, lifeless, perfectly accurate
corpus agrees with its ledgers completely.

So we measured it twice, at the same seed, against byte-identical ledgers
and briefs, changing only the model. Full write-up and limits in
[docs/MODEL-AB.md](docs/MODEL-AB.md).

**Round 1, Opus 4.8 against Haiku 4.5.** One corpus a blind reviewer said
would "take a deliberate effort to catch out"; the other it rejected
outright as too thin to survive first contact, at **60% of the words its
briefs asked for**, with 8 of 9 documents off brief. Both corpora passed
every validator rule that ran, with zero errors. The folklore was right, and
the gap is not subtle. But Haiku is a small, fast, cheap model, so this
establishes that the axis is real, not where a strong mid-tier model sits
on it.

**Round 2, Opus 4.8 against Sonnet 5.** Run because Round 1 licenses no
conclusion about a mid-tier model, and because "Opus is overkill for placing
prose around placeholders" is a reasonable hypothesis that deserved a number
rather than a dismissal. The quality gap turned out to be modest: **0.853 of
brief against 0.967**, with 4 of 22 documents off brief against 0. Sonnet is
mildly terse, not thin. Nothing like Haiku's collapse. On quality alone it
would be a defensible choice.

**The cost case is what failed instead.** Sonnet spent **1.89x the tokens**
for byte-identical work: it made more tool calls, re-read more, and
self-checked more, while producing 0.86x the words. Sonnet 5 is priced at
exactly 0.6x Opus 4.8 on *both* halves ($3/$15 per MTok against $5/$25), so
the arithmetic is short:

| pricing | arithmetic | result |
| --- | --- | --- |
| standard | 1.89 × 0.6 | **13% more expensive than Opus** |
| introductory ($2/$10, through 2026-08-31) | 1.89 × 0.4 | 24% cheaper |

At standard rates **the cheaper-per-token model is the more expensive choice
for this workload**, and the only window where it saves anything is
promotional and expiring. For a fleet that gets byte-pinned and lives for
years, that is not a trade worth 12% thinner prose.

The transferable lesson is not about Sonnet, which is a capable model that
will write you a decent corpus. It is that **a per-token price is not a
cost.** For an agentic authoring workload the token multiplier can move
further than the rate card does, and it moves in the direction nobody quotes
you. If you pick a model on price, measure the tokens it actually spends on
*your* workload.

### How we guard a choice we refuse to gate

This is where OrgSmith's philosophy gets concrete, because the obvious move
(a test that fails when the corpus reads thin) is one we deliberately do
not make.

**No test asserts prose quality, and none ever will.** Quality has no
validated threshold here, and the moment a similarity or length number
becomes a bar, the generator learns to satisfy the bar rather than the
intent: a similarity rule teaches it to paraphrase. That is Goodhart, and
`bin/test` is kept free of it by construction: no tier may touch a model,
the network, a key, or a wall clock, and a static test proves no tier can
reach the review board at all. What the tests *do* guard is that the
deterministic half cannot drift underneath you: the same recipe re-derives
every committed org byte-identically, so if a change moves a ledger, the
suite says so in seconds.

Instead of gating, four cheap mechanisms make a weak pass *visible*:

- **Preflight, before tokens are spent.** `doctor` prints your session's
  effort against the authoring floor (stated once, in `orgsmith/effort.py`)
  and warns when you are under it. `/forge` reports the model and effort in
  Step 0. This is the only moment the choice is free.
- **A free detector, after.** `report` computes each document's length
  against the words its brief actually asked for, with no model and no
  tokens. It separated Round 1's arms decisively (1.16 vs 0.60) and Round
  2's clearly (0.967 vs 0.853). It is the cheapest quality signal in the
  system, and reading it before you trust a fresh org costs nothing.
- **Provenance as a record, never a check.** Every batch records the model
  and effort that authored it. Round 1 is exactly why it is not a check: the
  weaker model *misreported its own effort* and skipped a stamp entirely.
  Had any rule trusted that field, it would now be enforcing a value the
  model made up.
- **A human reads the number.** The metric measures, the board judges, the
  human decides. That sequence is the whole design.

**The honest caveats, because this section argues for spending more money.**
Both rounds are n = 1 (one org and one run per arm), and the effort axis was
never independently varied. They establish a default with evidence behind
it, not an effect size.

And the 13% figure is softer than it looks. It holds only if both arms spend
tokens in the same input/output/cache mix, and we have evidence they do not:
Sonnet re-read more (proportionally more input and cache-read tokens, the
cheap components) while producing fewer words (fewer output tokens, the
expensive one). That skew makes 1.135x an *over*-estimate of Sonnet's true
cost, and a blended-price shift of ~12% would drop it under 1.0 and flip the
headline. We cannot settle it from the artifacts: the harness reports one
undifferentiated token total per worker. So the defensible claim is narrower
than "Sonnet is more expensive": it is that **Sonnet's 0.6x rate card does
not buy you a 0.6x bill, the gap is most of the way to erasing the discount,
and nobody should assume the direction without measuring.** Full derivation
and limits in [docs/MODEL-AB.md](docs/MODEL-AB.md).

## Design principles

Five rules have survived every milestone so far and govern new work:

- **Facts are load-bearing; prose is replaceable.** Every number, date,
  id, name, and relationship comes from deterministic ledgers; the model
  writes only surface prose around `{{fact:...}}` placeholders it cannot
  resolve.
- **Verification is the ceiling.** The validator and the eval suites are
  oracles computed from ground truth, never another model's opinion; no
  LLM grades an LLM anywhere in an automated path.
- **Additive evolution.** New capabilities arrive as schema fields that
  default inert and randomness drawn from new seed streams, so every
  committed fixture keeps loading, validating, and regenerating
  byte-identical structure. This rule was deliberately suspended for the
  v2.0 arc (M8-M11), when the realism work defaulted on rather than off and
  the fleet was regenerated wholesale. **That window is now closed:** the
  new fleet landed at M11 and every committed org is byte-pinned again.
- **Derive, don't store.** Anything recomputable from the ledgers (eval
  suites, ACL grants, ambiguity tags, PERMISSIONS.md) is emitted at read
  time, which is how frozen fixtures gain new capabilities without
  regeneration.
- **Grandfather by charter, not by absence.** Validator rules skip only
  when the recipe says a feature is off; a missing artifact with the knob
  on is a failure, so stripping ground truth from a distributed org can
  never pass validation.

## Quick start

**Just want the data?** Clone the repo. The eight companies (plus `dev-mini`)
under `companies/` are ready to use, with their answer keys beside them. No
venv, no model, no API key.

To validate, score, or generate:

```bash
git clone https://github.com/peterzat/OrgSmith.git && cd OrgSmith
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt   # WeasyPrint needs system Pango
bin/test                                        # short + unit + org tiers, offline
```

**Install the package.** As of v2.1.0 the tool is pip-installable with a console
entry point: `pip install .` from a clean venv builds the `orgsmith` package and
puts `orgsmith` on your PATH (so `orgsmith doctor`, `orgsmith validate <slug>`,
etc. work without the repo root). `requirements.lock` pins the exact tested
dependency set (versions, not hashes; the residual float is stated there). For a
reproducible generation environment including LibreOffice, `docker build -t
orgsmith .` builds the [Dockerfile](Dockerfile) and `docker run --rm orgsmith`
runs `orgsmith doctor` green. `CHECKSUMS.md` carries a SHA-256 rollup of the
eight committed orgs.

```bash
python -m orgsmith validate northgate-staffing       # every rule its recipe enables
python -m orgsmith report northgate-staffing         # corpus metrics -> GENERATION-REPORT.md
python -m orgsmith score northgate-staffing \
    --suite extraction --answers my_system.json      # grade your system
```

Generating orgs with legacy formats (`legacy_ratio` recipes producing
`.doc`/`.xls`/`.ppt`) additionally needs LibreOffice on the generation
machine (`sudo apt-get install --no-install-recommends libreoffice-writer
libreoffice-calc libreoffice-impress`); `python -m orgsmith doctor` reports
whether `soffice` is available. Validating and scoring existing orgs,
including legacy files, never needs it.

Then open Claude Code in the repo and run:

```
/forge dev-mini          # regenerate the tracer org
/forge-review dev-mini   # dispatch the adversarial board (optional)
```

To make your own company, write a recipe (see
[docs/RECIPE-FORMAT.md](docs/RECIPE-FORMAT.md)) under `recipes/<slug>/` and
run `/forge <slug>`. A recipe is one Markdown file: headcount, date range,
document mix, finance profile, and a prose brief that sets the firm's
voice.

**Which model writes the documents?** Whatever model your Claude Code
session is running; OrgSmith pins nothing and needs no API keys, so
generation bills to your existing plan. Deterministic stages (scaffold,
ledgers, rendering, validation) run as plain Python and cost no tokens at
all. Use the strongest model you have, and read
[Which model should write your documents?](#which-model-should-write-your-documents)
before deciding a cheaper one saves you anything. Measured, it did not.

## What is in the box today

### Which fixture proves what

The fleet table [above](#what-ships-today) says what each org *is*. This says
what each one *exercises*, so you can pick the fixture that stresses the part
of your system you care about. Every row is read from that org's committed
charter. Most columns have a validator rule that recomputes them from the
recipe and fails the org on a mismatch: `ACL-01/02/03`, `LEG-01`,
`SCAN-01/02`, `LOC-01/02/03` (the hard cases), `AFF-01/02`, `EML-01`,
`MENT-01/02` (the ambiguity surfaces). Decks are the exception: they are
covered by the generic "every file opens in its native reader" rule
(`FILE-01`) rather than by a deck-specific recompute.

Since the M13-M16 realism wave, every fleet org also declares a business-day
calendar, a sample-book prose posture, and the per-author style/voice layer;
those are fleet-wide, so they are not columns here. The columns are what still
*differs* between orgs.

| org | ACL | legacy | scans | OCR | sig-page fee | filename date | surname | nickname | multi-affil | decks | mail | noise | hires/departs/promos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ashcombe-advisory` | open |  |  |  |  |  |  | ✓ |  | ✓ | ✓ | ✓ | 3/1/2 |
| `brackenridge-civil` | open | **1.0** | 0.5 | 0.5 |  |  |  |  |  | ✓ |  |  | 3/1/1 |
| `calderwood-partners` | departmental |  | 0.3 | 0.5 | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ | 12/2/3 |
| `hollowell-ip` | departmental |  |  |  | ✓ |  |  | ✓ |  | ✓ | ✓ |  | 4/1/1 |
| `meridian-actuarial` | departmental |  |  |  | ✓ | ✓ | ✓ |  |  | ✓ | ✓ |  | 5/1/2 |
| `northgate-staffing` | departmental |  | 0.5 | 0.34 | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | 5/1/2 |
| `saltmarsh-environmental` | departmental |  | 0.6 | 0.5 | ✓ | ✓ |  |  | ✓ | ✓ |  |  | 4/1/1 |
| `verdant-health` | open |  | 0.5 |  |  |  |  |  | ✓ | ✓ |  |  | 1/1/1 |
| `dev-mini` | open |  |  |  |  |  |  |  |  |  |  |  | 1/1/1 |

Reading it: **`brackenridge-civil`** is the ugly-format org, `legacy_ratio`
at 1.0 means *every* office document is a real pre-2007 OLE container (24
`.doc`, 9 `.xls`, 2 `.ppt`), half its PDFs are degraded scans, and half of
those carry a synthetic OCR layer. **`saltmarsh-environmental`** and
**`verdant-health`** are where a contact changes employer mid-history, with
dated `works_at` edges and era-correct resolution per document date.
**`meridian-actuarial`** and, since M17, the exemplar
**`northgate-staffing`** carry both hard-case knobs, so a fee lives only on a
signature page and a date lives only in a filename. **`hollowell-ip`**,
**`meridian-actuarial`**, **`ashcombe-advisory`**, and
**`northgate-staffing`** are where engagement mail runs as real threads (the
`doc_culture.mail` block); **`northgate-staffing`**,
**`calderwood-partners`**, and **`ashcombe-advisory`**
carry the organizational-noise suite (duplicates, drafts, misfiles). The
exemplar is the only org carrying all four of a departmental ACL, threads,
scans, and both hard cases at once, which is what makes it the one to read
first. **`dev-mini`**
is deliberately bare: it is the regression oracle the ~600-test unit tier builds
on, so it stays small and cheap rather than proving breadth. Its one exception
is `style_specs`, on since M15: the per-person voice ledger is cheap, and a
tracer is the right place to prove it end to end.

- The full pipeline, end to end, proven on all eight, every one generated on
  the full stack through the live airlock and byte-pinned.
- Access-control ground truth: the recipe's `acl_posture` derives
  `ledger/acl.json` (exactly which internal people may read which
  documents: matter teams plus the CEO-equivalent for engagement folders,
  finance restricted to its owners) plus a human-readable PERMISSIONS.md
  in the share root, both enforced by validator rules that recompute the
  grants from the posture. Grants are access *as of the end of the
  corpus*, so someone the roster retires mid-history holds none, which
  makes "does your system correctly deny a departed employee?" a scored
  visibility question with an empty expected set, rather than a case the
  answer key is blind to.
- Hard-case fact planting: recipe knobs place facts where extractors have
  to work for them. A signature-page-only fee is injected at render time
  onto the final page of the engagement letter and appears nowhere else
  in the corpus; a filename-only meeting date exists solely in the
  minutes filename, with ingest rejecting any deliverable that states the
  date in text in any form.
- People-graph ground truth: recipe-dialable graph knobs, a mention map
  recording exactly which documents name which entities (and with what
  surface form), and validator rules that fail the org when a planned
  mention is missing from extractable text.
- Golden evals: `emit-evals` derives retrieval questions, an extraction
  suite (one question per planted fact: exact expected value, source
  documents, and its location class), a visibility suite (per internal
  person, the exact document set their access allows), and a people-graph
  answer key (with alias credit and per-ambiguity-class recall) from the
  ledgers, and `score` grades an external system's answers with
  per-question attribution, from nothing but the `evals/` directory.
  Deterministic, no model involved; ground-truth answers score 100% by
  construction.
- Renderers: `.docx` (python-docx: letterhead, PAGE-field footers,
  signature blocks, real core properties), `.pdf` (WeasyPrint with
  paged-media letterhead, pikepdf metadata, remote fetches blocked),
  `.xlsx` (xlsxwriter with real formulas plus cached values that tie to
  the ledger), `.pptx` (python-pptx decks, one slide per heading), and
  `.eml` (stdlib email; every header a pure function of the ledgers,
  byte-identical on re-render).
- Format transforms: recipe-dialable scans (pdfs rasterized and degraded
  deterministically per seed, with an invisible synthetic OCR text layer
  whose corruptions never touch planted surfaces, and the true page text
  archived as ground truth) and legacy conversion (oldest office docs
  become verified `.doc`/`.xls`/`.ppt` via LibreOffice at generation
  time; validation reads them back pure-Python via olefile and xlrd).
- The airlock, checkpoint/resume, the 37-rule validator, capability
  probing (`doctor`), and machine-readable pipeline status (`status
  --json`).
- The quality instrument, which measures the one thing the validator
  cannot: whether the prose reads like a real firm wrote it. `report`
  computes deterministic corpus metrics with no model (each document's
  length against the words its brief asked for, same-genre n-gram
  overlap) and writes GENERATION-REPORT.md; `/forge-review` dispatches a
  read-only board of fresh-context reviewers across six dimensions,
  including the cross-document voice check no author can perform on
  itself, because nothing in the pipeline holds two authored documents at
  once. Neither gates: the metric measures, the board judges, the human
  decides. Each batch records the model and effort that authored it, as a
  report and never as a check.
- Skills: `/forge` (orchestrator), `forge-author` (per-batch worker with
  a fresh context, which is what lets large orgs span sessions), and
  `/forge-review` + `forge-reviewer` (the board).

## Where this is going

**The v2.0 arc is closed.** It was scoped directly from what the review
board said about the retired exemplar, and it ran four milestones:

| | what landed |
| --- | --- |
| **M8** | Roster churn, behavioral finance, staffing rotation, date-scoped briefs, era-appropriate naming. The firm gets a history. |
| **M9** | The document-supply model: a genre registry driving volume from the firm's engagements, fiscal years, and hires (no fixed skeleton), realistic per-genre lengths, and a folder taxonomy beyond `Engagements/Finance/Firm`. |
| **M10** | Parallel authoring: a bounded K-wide window of concurrent authors over a serial, single-writer merge. This is what makes a fleet-sized run a few hours instead of a few days. |
| **M11** | The fleet reset: six new recipes (civil engineering, environmental, actuarial, IP law, executive search, healthcare; 1999–2025), all generated through the live airlock, the six pre-v2.0 fixtures retired, and the byte pin restored fleet-wide, which re-freezes the fixtures and restores additive evolution. |

**M12a landed the capability layer.** The findings the board raised against the
fleet became recipe knobs, each defaulting off so the frozen fleet stays
byte-pinned: a business-day calendar (CAL-01), an engagement book declared a
sample, a deterministic noise model (duplicates and drafts derived from
authored documents with no model pass, NOISE-01), nested eval splits
(core / distractors / noise / full for a retrieval degradation curve), a
cheap cross-document-voice mitigation measured as a range, and a
generator-wide fix so prose can no longer contradict a ledger reporting line.
The pilot org **`calderwood-partners`** (218 documents, every knob on)
proves the stack end to end and is committed and browsable beside the fleet.

**The realism wave (M13-M16) is closed.** M13 closed the path-safety and
letterhead-escaping hygiene; **M14 landed email realism**, with the committed
email-first pilot `ashcombe-advisory` (real threads, minute-granularity
timing, quoted history, promotion-aware signatures, transmittal attachments,
and distribution lists). M15 added organizational noise, persona voice, and a
distributional dashboard, and M16 regenerated the whole fleet under the wave's
knobs, re-froze it, and cut the v2.1 release.

**M17 made the answer key tell the truth about the rendered corpus.** An
external reviewer cloned the repo, parsed all 66 exemplar documents, ran the
validator, and found that the evaluation layer mistook planned provenance for
rendered truth: a byte-identical duplicate of an expected document scored as
an error, mention gold came from the plan rather than from the text, scoring
was an exact-set unit test with no ranking, and the advertised four-point
degradation curve was two-point on every org. The turn added equivalence
clusters, scan-derived acceptable sets, ranked metrics, keyless baselines,
per-org data cards, a versioned label policy, and a validator rule (EVAL-01)
that re-derives the committed answer key. The critique and its disposition
are in [docs/EXTERNAL-CRITIQUE-2026-07-28.md](docs/EXTERNAL-CRITIQUE-2026-07-28.md).

**Next: M18, one flagship org large enough to defeat a context
window.** The whole committed fleet is ~280 documents; you can fit that in a
1M-token context and answer questions about it without retrieving anything,
which means it cannot prove a retrieval system works. The pilots are the right
capabilities at a fraction of the scale; the flagship spends the ~1.3 days of
authoring the full size costs. See [docs/SCALE.md](docs/SCALE.md) for how big
that has to be and why resume becomes the only reason it is possible.

Known and logged rather than hidden: `BACKLOG.md` carries the board's
unmeasured false-positive rate and the remaining fleet-wide findings M12a did
not close (the empty engagement book most of all). Cross-document voice now
has a measured mitigation but no single number for its size, and stays the
genuinely hard one.

## Provenance and safety

Everything generated is fictional. Every rendered file carries a synthetic
marker in its native metadata (docx/xlsx custom properties, PDF document
info), and a validator rule fails the org if one is missing. Generated names
are screened against a real-firm list at generation time and by a validator
rule, so a fixture cannot ship a company name that collides with a real one.
See NOTICE.

## Built with

OrgSmith is itself an agentically coded project: designed and implemented
in [Claude Code](https://claude.com/claude-code) running
[zat.env](https://github.com/peterzat/zat.env), spec-driven turns,
adversarial code review with builder/verifier separation, and a pre-push
gate that blocks unreviewed code.

The committed fleet was authored through the same airlock this repo ships,
by `claude-opus-4-8[1m]` (all eight fleet orgs and `dev-mini` at `/effort
xhigh`). Every org's `GENERATION-REPORT.md` records what actually wrote
it, batch by batch, self-reported, and treated as a record rather than an
oracle for the reason [Round 1
found](#which-model-should-write-your-documents).

## License

Apache-2.0. Copyright (c) 2026 Peter Zatloukal. See LICENSE and NOTICE.
