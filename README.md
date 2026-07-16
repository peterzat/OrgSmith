# OrgSmith

Generate a complete, fictional company: a browsable file share full of real
`.docx`, `.pdf`, `.xlsx`, `.pptx`, and `.eml` documents (degraded scans and
pre-2007 `.doc`/`.xls`/`.ppt` binaries included, when the recipe asks),
plus a ground-truth ledger that knows every fact planted in them.

```
companies/dev-mini/
├── TOC.md
├── Engagements/
│   ├── Johnson and Sons/
│   │   ├── 2019.07.07 - Engagement Letter - Johnson and Sons - EXECUTED.pdf
│   │   ├── 2019.07.20 - Kickoff Memo - Operational Review.docx
│   │   ├── Meeting Minutes 2019-08-27 - Johnson and Sons.docx
│   │   └── 2019.09.07 - Status Report - Johnson and Sons v2 FINAL.docx
│   ├── Dean PLC/ ...
│   └── Reeves, Miller and Thompson/ ...
├── Finance/
│   ├── FY2018 Financial Summary.xlsx  ... through FY2022
├── Firm/
│   ├── Firm Overview 2019 v3.docx
│   └── Firm Overview 2022 v3.docx
└── People/
    └── 2020.11.08 - Onboarding - Cynthia Ball.docx

companies/dev-mini-metadata/     <- ground truth for all of the above
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
The writer is whatever model your Claude Code session is set to: OrgSmith
pins none. Use the strongest you have. That is measured rather than folklore
([docs/MODEL-AB.md](docs/MODEL-AB.md)), and `doctor` prints your session's
effort against the authoring floor and warns when you are under it.

The result reads like a real firm wrote it: engagement letters on letterhead
with signature blocks, meeting minutes that name every attendee, spreadsheets
whose formulas recompute to the values the finance ledger says. The
`-metadata` directory is the answer key.

**Seven companies are already generated and committed here. Browse them
now: [`companies/`](companies/)** — real files and their answer keys, in the
browser, nothing to clone or install. You can also write a recipe and
generate your own.

## Who this is for

You are building something that has to operate over a real organization's
documents — retrieval, extraction, a people graph, an agent that navigates
a file share — and you need a corpus to develop against. Your options today
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
  *location class* — so you can score "found it in the body" separately from
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
  text at all — each with the *true* page text archived as ground truth, so
  you can measure exactly what your OCR pipeline lost.

`score` grades an external system's answers against any suite with
per-question attribution, from nothing but the `evals/` directory. Ground
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

**Browse the fleet in your browser: [`companies/`](companies/).** All seven
are committed and public, so every `<slug>/` is a real file share you can
click through and every `<slug>-metadata/` is its answer key, sitting right
next to it. Nothing to clone, install, or authenticate.

Document spans below are the real dates on the files, not the window the
recipe allowed:

| company | docs | share | answer key |
| --- | --- | --- | --- |
| 5-person consultancy, 2019–2023 | 22 | [dev-mini](companies/dev-mini/) | [key](companies/dev-mini-metadata/) |
| 6-person engineering firm, 2019–2024 | 11 | [torchlake-engineering](companies/torchlake-engineering/) | [key](companies/torchlake-engineering-metadata/) |
| 5-person appraisal practice, 2019–2020 | 11 | [quillbrook-appraisal](companies/quillbrook-appraisal/) | [key](companies/quillbrook-appraisal-metadata/) |
| 5-person law practice, 2018–2021 | 11 | [bramblewood-legal](companies/bramblewood-legal/) | [key](companies/bramblewood-legal-metadata/) |
| 5-person strategy consultancy, 2022–2025 | 16 | [gladepoint-strategies](companies/gladepoint-strategies/) | [key](companies/gladepoint-strategies-metadata/) |
| 5-person ops consultancy, 1998–2004, legacy binaries and scans | 14 | [cindergrove-advisors](companies/cindergrove-advisors/) | [key](companies/cindergrove-advisors-metadata/) |
| 5-person financial advisory, 2020–2025 | 19 | [fernhollow-partners](companies/fernhollow-partners/) | [key](companies/fernhollow-partners-metadata/) |

Seven companies, 1998–2025, ~3.9 MB of share plus ~1.3 MB of ground truth:

| | fleet |
| --- | --- |
| companies | 7 |
| people (internal) | 36 |
| planned documents | 104 (87 model-authored + 17 deterministic workbooks) |
| engagements | 19 |
| mean words per authored doc | transitional (see below) |
| whole fleet as tokens | ~30K |

The fleet is mid-rebuild (the v2.0 arc, M8-M11). `dev-mini` is regenerated
under the M9 document-supply model and authors at **mean 717 words**; the
six frozen fixtures retain their pre-M9 lengths (the old ~236-word era)
until the M11 fleet reset, so the fleet mean is a transitional mix. Each
org's current numbers live in its `GENERATION-REPORT.md`.

Per company: 5–6 people, 11–22 documents, 2–4 engagements, a 3–7 year span.

By format: 52 `.docx`, 19 `.pdf`, 15 `.xlsx`, 8 `.doc`, 3 `.pptx`, 2 `.xls`,
4 `.eml`, 1 `.ppt`.

By genre: 19 engagement letters, 21 sets of meeting minutes, 15 kickoff
memos, 15 status reports, 17 financial summaries, 8 firm overviews, 4
briefing decks, 4 email threads, 1 onboarding record. (`dev-mini`'s share
of these grew when M9 regenerated it; the six frozen fixtures are unchanged
until M11.)

### Where that sits against a real firm

A real five-person professional-services firm over five years does not
produce 14 documents. It produces, very roughly:

- **Email in the tens of thousands.** Five people sending even 20 messages a
  working day is ~125,000 messages over five years. OrgSmith ships **4
  `.eml` files across the entire fleet.** Real firms are email-dominant
  corpora; this one is document-dominant. That is the single largest
  fidelity gap.
- **Files in the thousands to hundreds of thousands**, most of them junk:
  drafts, near-duplicate versions, dead templates, misfiled scans, someone's
  lunch menu. OrgSmith ships 11–22 documents per company, each one
  deliberate and none of them junk.
- **Documents 3–6× longer — now being fixed.** Real engagement letters run
  800–1,500 words; the fleet's old authored mean was **236 words** against
  briefs asking 130–350. The model was roughly hitting its targets; the
  targets were wrong. **M9 raised them**: length is a per-genre property of
  the genre registry, engagement letters now target 1,100, and the
  regenerated `dev-mini` authors at **mean 717 words** with clause-bearing
  letters. The six frozen fixtures are raised at the M11 reset. Measured and
  published in every org's `GENERATION-REPORT.md`.

There is no honest way to call 14 documents a sample of that. What it is: a
corpus where **every** hard case you care about is present, labeled, and
checkable. If your extractor cannot find a fee that exists only on the
signature page of a degraded scan, it will fail here, on 19 documents, in
1.7 seconds, with an exact answer key — instead of failing silently on
50,000 real ones.

### What is not modeled today

Our own adversarial review board read the flagship fixture,
`fernhollow-partners`, and said it better than we could. These are its
actual committed findings — all rated major, all in
`companies/fernhollow-partners-metadata/review/findings/`:

- **Nobody's career moves.** "Across the corpus's five-year span nobody is
  hired, promoted, or leaves... which leaves Ryan Strong an Analyst five and
  a half years after joining a firm that has no other analyst to be junior
  to."
- **The contracts are not contracts.** "All four engagement letters are
  countersigned EXECUTED contracts that allocate no risk: no termination
  clause, no limitation of liability, no indemnification, no governing law
  or dispute resolution, no retainer, and no incorporation of standard terms
  by reference."
- **The org graph is flat where a real one is lopsided.** "Every engagement
  across five years is staffed by exactly the same three people and every
  engagement document names all three."
- **Finance is too clean.** "Every expense line is a frozen percentage of
  revenue in all eight years... which no real P&L does" — so Office &
  Facilities compounds to +89% for a firm whose own ground truth says the
  same five people never left the same office.
- **The firm doesn't template what a real firm would template.** The
  conventions "cluster by authoring batch rather than by client, year, or
  recipient" — the generator's context resets are more legible in the output
  than the firm's five employees are.

**This is where the generator stood when the board read it, and the roadmap
was scoped directly from this list.** Four of those five findings drove the
next milestone (M8), which has now landed: the frozen roster, the flat
staffing graph, and the lockstep finance are fixed in the generator, as its
default behavior rather than as opt-in knobs. A regenerated org now hires,
promotes, and loses people, staffs engagements with varying teams, and
computes each expense line from what drives it. The board read
`fernhollow-partners`, and **fernhollow is not regenerated this turn** — the
committed fleet is rebuilt wholesale at the v2.0 fleet reset (M11), so the
findings above still describe the committed fernhollow you can browse, not
the generator that would produce it today. M9 has since landed the
document-supply model: the generator now drives document volume from the
firm's real activity (no fixed skeleton), authors at realistic per-genre
lengths, and gives engagement letters the standard clauses a real one
carries. [SPEC.md](SPEC.md) is the current unit of
work and says exactly what it commits to. Each turn's board findings stay
committed next to the org they judged. Cross-document voice is the genuinely
hard one, and it has no scheduled fix.

Out of scope by choice rather than pending: multi-org document exchange,
litigation-style volume, real duplicate/version chains, personal and
off-topic content, adversarial or malicious documents, and any human editing
pass. Email volume is the largest gap above and sits in between: the recipe's
`format_mix` does dial the email share, but no committed fixture leans that
way, and the planner currently spaces successive messages in a thread 45 days
apart, so email-dominant realism needs more than turning the knob up.

**Choose accordingly.** If you need volume, noise distribution, or email
realism, this is the wrong tool today. If you need labeled hard cases,
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
- The model writes documents with `{{fact:...}}` placeholders and is never
  shown the underlying values. Python substitutes them at render time, so a
  number cannot be mistranscribed. Ingest rejects deliverables that miss a
  required placeholder, invent people, or write a literal value where a
  placeholder belongs.
- After rendering, a 29-rule validator ties every document back to the
  ledger: planted facts and planned name mentions appear verbatim in
  extractable text, hard-case location policies hold (a
  signature-page-only fee appears on exactly that pdf page and nowhere
  else; a filename-only date never appears in document text), access
  grants and PERMISSIONS.md match a recomputation from the recipe's ACL
  posture, workbook formulas recompute to ledger values, mail headers
  recompute exactly from the ledgers, scan flags and legacy assignments
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
```

Long runs checkpoint into `state.json`: kill the session mid-generation,
re-run `/forge <slug>`, and it resumes exactly where it stopped with no
duplicated or lost documents. Structure is fully seeded; the same recipe
regenerates the same org (ids, names, tree, numbers), with only the
model-authored prose varying.

## Why we think the output is any good

Any generator can claim quality. The question a researcher should ask is:
*what would catch you if you were wrong?* OrgSmith's answer is a deliberate
hierarchy, taken from [The Bitter Lesson of Agentic
Coding](https://agent-hypervisor.ai/posts/bitter-lesson-of-agentic-coding/):
**oracles beat proxies beat critics**, and you should know which one you are
relying on for any given claim.

**Oracles — strongest, and where all the facts live.** An oracle recomputes
the answer from ground truth. The 29-rule validator and the eval suites are
oracles: they do not ask whether a document *seems* right, they recompute
what it must contain from the ledgers and fail the org if it doesn't. This
is why the airlock exists — the model never sees a value it is placing, so
"the model transcribed the fee wrong" is not a bug class that can occur. It
is structurally impossible rather than tested-for.

**Proxies — weaker, cheap, and blind to different things than you are.**
`orgsmith report` computes corpus metrics with no model: each document's
length against the words its brief actually asked for, and same-genre n-gram
overlap. A proxy catches what the generator cannot see about itself. Ours
immediately found real literal reuse across two engagement letters that no
human reader in the project had noticed.

**Critics — weakest, and treated as such.** `/forge-review` dispatches a
board of fresh-context reviewers across six dimensions. A critic shares
blind spots with the generator that produced the text, so the board's scope
is exactly what no proxy reaches — above all **cross-document voice**, the
one dimension no author can ever self-check, because nothing in the pipeline
holds two authored documents at once. Every document is written by a fresh
worker that has never seen a sibling.

Three consequences worth being explicit about:

**Nothing that is not an oracle is allowed to gate.** No metric and no board
finding is a validator rule. Thresholds are unknown, and "when a measure
becomes a target, it stops being a good measure" — a similarity rule would
just teach the generator to paraphrase. The metric measures, the board
judges, the human decides.

**Generation and evaluation are structurally separated, not politely
separated.** Agents asked to grade their own work confidently praise it. So
the board is read-only and never authored what it reviews; `bin/test` cannot
reach the board at all (a static test proves no tier can); and no LLM grades
an LLM anywhere in an automated path.

**We publish what the critic said about us.** The board's findings against
the flagship fixture are committed to this repo, unflattering ones included
— the frozen roster, the too-clean finance, the batch-legible conventions
quoted above. `docs/REVIEW-CALIBRATION.md` records the board being
calibrated against two hand-labeled defects before its findings were relied
on, including the case where it **overruled the metric** (judging a flagged
similar pair to be realistic template reuse) and the case where it caught
what the metric provably cannot see.

### The evidence, concretely

- **306 tests** across three tiers (`bin/test`), keyless and offline; the
  `org` tier validates every committed fixture in ~1.7s.
- **Determinism is enforced, not hoped for.** The same recipe regenerates
  byte-identical structure. Committed fixtures are frozen and every
  capability added since has had to keep them loading, validating, and
  regenerating unchanged — which is why derived artifacts (`evals/`,
  `acl.json`, PERMISSIONS.md, `GENERATION-REPORT.md`) are recomputed rather
  than stored.
- **Tamper evidence by construction.** Rules grandfather by *charter*, not
  by artifact absence: a knob that is on with its ground truth missing is a
  failure, so stripping the answer key out of a distributed org cannot pass
  validation.
- **The model choice is measured, not asserted.** See below.
- **The whole project is built this way.** Spec-driven turns, adversarial
  review with builder/verifier separation, and a pre-push gate that blocks
  unreviewed code — via [zat.env](https://github.com/peterzat/zat.env).
  `SPEC.md`, `CODEREVIEW.md`, and `SECURITY.md` are in the repo; read them
  to see what the review actually caught.

**What this does not prove.** The board has been calibrated on one org, one
model, one run, with no negative control — so its false-positive rate is
unmeasured. The metrics have no validated thresholds. Nothing here
establishes that a system which scores well on OrgSmith scores well on a
real corpus; the fidelity gaps above are the reason to doubt it. These
limits are recorded in `docs/REVIEW-CALIBRATION.md` rather than smoothed
over.

## Design principles

Five rules have survived every milestone so far and govern new work:

- **Facts are load-bearing; prose is replaceable.** Every number, date,
  id, name, and relationship comes from deterministic ledgers; the model
  writes only surface prose around `{{fact:...}}` placeholders it cannot
  resolve.
- **Verification is the ceiling.** The validator and the eval suites are
  oracles computed from ground truth, never another model's opinion; no
  LLM grades an LLM anywhere in an automated path.
- **Additive evolution, restored after a v2.0 breaking window.** The
  standing rule: new capabilities arrive as schema fields that default
  inert and randomness drawn from new seed streams, so every committed
  fixture keeps loading, validating, and regenerating byte-identical
  structure. That rule is deliberately suspended for the v2.0 arc (M8-M11):
  the realism work defaults on rather than off, and the committed fleet is
  regenerated wholesale rather than held byte-identical. It is restored,
  and the fleet re-frozen, when the new fleet lands at M11.
- **Derive, don't store.** Anything recomputable from the ledgers (eval
  suites, ACL grants, ambiguity tags, PERMISSIONS.md) is emitted at read
  time, which is how frozen fixtures gain new capabilities without
  regeneration.
- **Grandfather by charter, not by absence.** Validator rules skip only
  when the recipe says a feature is off; a missing artifact with the knob
  on is a failure, so stripping ground truth from a distributed org can
  never pass validation.

## Quick start

**Just want the data?** Clone the repo. The seven companies under
`companies/` are ready to use, with their answer keys beside them. No venv,
no model, no API key.

To validate, score, or generate:

```bash
git clone https://github.com/peterzat/OrgSmith.git && cd OrgSmith
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt   # WeasyPrint needs system Pango
bin/test                                        # short + unit + org tiers, offline
```

```bash
python -m orgsmith validate fernhollow-partners      # 29 rules against ground truth
python -m orgsmith report fernhollow-partners        # corpus metrics -> GENERATION-REPORT.md
python -m orgsmith score fernhollow-partners \
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
all.

Use the strongest model available for authoring passes. That is measured,
not folklore: the same recipe authored twice, at the same seed and so
against byte-identical ledgers and briefs, produced one corpus a blind
reviewer said would "take a deliberate effort to catch out" and one it
rejected outright as too thin to survive first contact — at 60% of the
words its briefs asked for. **Both passed all 29 validator rules with
zero errors**, which is exactly why the quality instrument exists. See
[docs/MODEL-AB.md](docs/MODEL-AB.md).

Nothing downstream can detect a weak authoring pass from the artifacts, so
OrgSmith surfaces the setting before tokens are spent rather than gating
on it: `python -m orgsmith doctor` prints the session effort against the
authoring floor (stated once, in `orgsmith/effort.py`) and warns when you
are below it, `/forge` reports the model and effort in Step 0, and each
batch records what actually authored it.

## What is in the box today

- The full pipeline, end to end, proven on seven committed fixtures:
  `dev-mini` (a 5-person consultancy, 22 documents, three engagements,
  2019-2023, with mention ground truth, the ACL overlay, and visibility
  evals); `torchlake-engineering` (a 6-person engineering firm, 11
  documents, 2019-2024) generated with every ambiguity knob on: a
  surname-collision pair, a nickname alias planted in rendered minutes,
  and an external contact with a mid-history employer change;
  `quillbrook-appraisal` (a 5-person appraisal practice, 11 documents,
  2019-2020) generated with the hard-case knobs on;
  `bramblewood-legal` (a 5-person law practice, 11 documents, 2018-2021)
  generated with a departmental ACL posture; `gladepoint-strategies`
  (a 5-person strategy consultancy, 16 documents, 2022-2025) whose mix
  adds a briefing deck and email threads; and `cindergrove-advisors`
  (a 5-person operations consultancy founded 1995, 14 documents,
  1998-2004) generated with the scan and legacy knobs on: every office
  doc a real pre-2007 binary, two engagement letters rasterized as
  degraded scans (one with a synthetic OCR layer, one image-only). Its
  roster still carries modern seeded names: era-appropriate naming now
  exists (M8) but cindergrove predates it and is not regenerated until the
  v2.0 fleet reset (M11). And `fernhollow-partners` (a 5-person financial
  advisory boutique, 19 documents, four engagements, 2020-2025)
  generated with `affiliations_in_docs` on: one client contact signs an
  early engagement letter under one employer and appears in late
  documents under another, era-correct per document date, with dated
  works_at edges and the multi-affiliation ambiguity tag in its answer
  key.
- Access-control ground truth: the recipe's `acl_posture` derives
  `ledger/acl.json` (exactly which internal people may read which
  documents: matter teams plus the CEO-equivalent for engagement folders,
  finance restricted to its owners) plus a human-readable PERMISSIONS.md
  in the share root, both enforced by validator rules that recompute the
  grants from the posture.
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
- The airlock, checkpoint/resume, the 29-rule validator, capability
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

M8 landed roster churn, behavioral finance, staffing rotation,
date-scoped briefs, and era-appropriate naming; M9 landed the
document-supply model: a genre registry that drives document volume from
the firm's engagements, fiscal years, and hires (no fixed skeleton),
realistic per-genre lengths, and a folder taxonomy beyond
`Engagements/Finance/Firm`. `dev-mini` is regenerated to exercise both.
Next, in rough order (see SPEC.md): parallel authoring and the scale fixes
(M10), a committed reference fleet spanning sectors and eras (M11), and one
flagship org large enough to defeat a context window (M12). See
[docs/SCALE.md](docs/SCALE.md) for how big those should be and why.

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
[zat.env](https://github.com/peterzat/zat.env) (spec-driven turns,
adversarial code review, pre-push gates), using Claude Fable 5 at
`/effort xhigh`. The committed dev-mini org was authored the same way,
through the same airlock shipped in this repo.

## License

Apache-2.0. Copyright (c) 2026 Peter Zatloukal. See LICENSE and NOTICE.
