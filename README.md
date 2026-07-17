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
The writer is whatever model your session is set to — OrgSmith pins none, so
[which one you pick is the one choice that changes your
corpus](#which-model-should-write-your-documents), and we measured it rather
than guessed.

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
| 12-person executive search firm, 2015–2023, the largest here | 53 | [northgate-staffing](companies/northgate-staffing/) | [key](companies/northgate-staffing-metadata/) |
| 12-person actuarial consultancy, 2016–2024, a roster that grows | 49 | [meridian-actuarial](companies/meridian-actuarial/) | [key](companies/meridian-actuarial-metadata/) |
| 10-person patent boutique, 2018–2025 | 45 | [hollowell-ip](companies/hollowell-ip/) | [key](companies/hollowell-ip-metadata/) |
| 9-person civil engineering firm, 1999–2007, every office doc a pre-2007 binary | 40 | [brackenridge-civil](companies/brackenridge-civil/) | [key](companies/brackenridge-civil-metadata/) |
| 10-person environmental consultancy, 2013–2021, scans and a departmental ACL | 40 | [saltmarsh-environmental](companies/saltmarsh-environmental/) | [key](companies/saltmarsh-environmental-metadata/) |
| 7-person healthcare advisory, 2020–2025 | 31 | [verdant-health](companies/verdant-health/) | [key](companies/verdant-health-metadata/) |
| 6-person consultancy, 2019–2023, the test fixture | 22 | [dev-mini](companies/dev-mini/) | [key](companies/dev-mini-metadata/) |

Seven companies, 1999–2025: ~16 MB of browsable share, plus ~5 MB of ground truth beside it.

| | fleet |
| --- | --- |
| companies | 7 |
| people (internal) | 66 |
| planned documents | 280 (225 model-authored + 55 deterministic workbooks) |
| engagements | 34 |
| mean words per authored doc | ~690 |
| mean length against what the brief asked | 0.998 |

This is the v2.0 fleet, generated in one arc and frozen. Every org is built
on the full stack: rosters that hire, promote, and lose people; expense
lines each computed from what drives them; document volume driven by the
firm's real activity rather than a fixed skeleton. Every org was authored by
`claude-opus-4-8[1m]` — the six fleet orgs at effort `xhigh`, `dev-mini` at
`max` — and **every one of the 225 authored documents lands within 25% of
the words its brief asked for**. Each org records what actually authored it,
batch by batch, in its `GENERATION-REPORT.md`.

Per company: 6–12 people, 22–53 documents, 3–6 engagements, a 5–9 year span.

By format: 146 `.docx`, 46 `.xlsx`, 34 `.pdf`, 24 `.doc`, 11 `.eml`, 9
`.xls`, 8 `.pptx`, 2 `.ppt`.

By genre: 55 financial summaries, 51 sets of meeting minutes, 37 status
reports, 34 engagement letters, 34 kickoff memos, 29 onboarding records, 19
firm overviews, 11 email threads, 10 briefing decks.

### Where that sits against a real firm

A real ten-person professional-services firm over eight years does not
produce 40 documents. It produces, very roughly:

- **Email in the tens of thousands.** Ten people sending even 20 messages a
  working day is ~400,000 messages over eight years. OrgSmith ships **11
  `.eml` files across the entire fleet.** Real firms are email-dominant
  corpora; this one is document-dominant. That is the single largest
  fidelity gap, and it has not moved.
- **Files in the thousands to hundreds of thousands**, most of them junk:
  drafts, near-duplicate versions, dead templates, misfiled scans, someone's
  lunch menu. OrgSmith ships 22–53 documents per company, each one
  deliberate and none of them junk.
- **A book of business far larger than the documented one.** Every org's
  engagement ledger is a deliberate sample: fees across it come to 1.6–5.1%
  of the revenue on the same firm's own financial summaries. Our review
  board caught the corpus mistaking that sample for the whole business, and
  the arithmetic is published rather than smoothed over (`BACKLOG.md`,
  `engagement-ledger-reads-as-whole-book`).
- **Documents 3–6× longer — fixed.** Real engagement letters run 800–1,500
  words; the pre-v2.0 fleet's authored mean was **236 words** against briefs
  asking 130–350. The model was roughly hitting its targets; the targets
  were wrong. M9 made length a per-genre property of the genre registry and
  raised engagement letters to 1,100. The v2.0 fleet authors at **mean ~690
  words** with clause-bearing letters, and this is now the one gap on this
  list that is closed.

There is no honest way to call 40 documents a sample of that. What it is: a
corpus where **every** hard case you care about is present, labeled, and
checkable. If your extractor cannot find a fee that exists only on the
signature page of a degraded scan, it will fail here, on 40 documents, in
under two seconds, with an exact answer key — instead of failing silently on
50,000 real ones.

### What is not modeled today

Our own adversarial review board read the flagship org, `northgate-staffing`,
and said it better than we could. These are its actual committed findings —
**16 major across six dimensions**, all in
`companies/northgate-staffing-metadata/review/findings/`, against a corpus
that validates clean: 24 rules run, 5 skipped for knobs it leaves off, 0
errors:

- **The firm's own paperwork says it has five clients. Its books say
  otherwise.** "The firm has been retained for five engagements to date...
  That is a deliberately short list," says the 2021 firm overview — five
  fees totalling $425,500 — while the FY2021 financial summary shipping in
  the same corpus posts **$2,469,000 for that one year**, and lifetime
  revenue reaches $20.7M. Two of the six reviewers drew this contradiction
  independently, on different dimensions, and a third independently reached
  the premise under it. It is real: fees are **1.6% to 5.1% of revenue in
  every org in this fleet**.
- **Meetings that could not have happened.** Minutes record a client working
  session on **Saturday 2016-05-28**, and another on **2023-07-04, US
  Independence Day**, with the client's General Manager attending. Neither
  remarks on it. The cause: 36% of documents land on a weekend, because the
  planner draws dates with no business-day calendar.
- **Every genre collapses to one template across authors.** Four of five
  engagement emails, by four different people, contain the literal string
  "Two asks. First… Second…". All six kickoff memos carry a "Workstreams"
  heading, then "Next Steps," then a closing epigram — six authors who never
  saw each other's work. "I would rather X now than Y later" appears **34
  times across 26 of 44 documents**, every author, every year.
- **The org grows staff it has no work for.** The engagement book is empty
  for 1,299 days while three people are hired into it, one onboarded with
  "She is walking into live work rather than a quiet stretch."
- **The people graph drifts from the ledger it describes.** Two onboarding
  records tell the hire she reports to the Managing Director; `foundation.json`
  reports her to the Principal, who is unnamed in both documents.

**This is where the generator stands today, and the roadmap is scoped
directly from this list.** Two of these are already logged with the
arithmetic that proves them (`BACKLOG.md`:
`engagement-ledger-reads-as-whole-book`,
`docplan-has-no-business-day-calendar`). Note what the board is *not*
saying: the previous flagship's findings — a roster where nobody is ever
hired or promoted, engagement letters with no termination or liability
clause, a staffing graph where every engagement has the same three people,
and expense lines frozen as a fixed share of revenue — are **gone**, fixed
in the generator by M8 and M9 as default behavior rather than opt-in knobs.
The board had to find new things to hate, and did.

Read the board sceptically, including here — it is the weakest instrument in
this repo, it has been caught publishing a checkable falsehood, and its
false-positive rate is unmeasured ([what this does not
prove](#what-this-does-not-prove)). Every finding quoted above was
re-verified against a ledger before it was published.

**You can check that rather than take it: every org above ships its own
board findings and its own numbers.** All seven are built on the whole v2.0
stack — rosters that grow, one person leaving and being backfilled, people
promoted, expense lines each computed from what drives them.

That last part is where the fix bit hardest, and it is worth knowing why.
Fixing the lockstep finance made every recipe's *own* incoherence visible:
once compensation tracks a roster instead of tracking fees, a firm that
compounds revenue with a headcount that never moves posts a net margin
climbing toward 50%, which no professional-services firm does. The model was
right and the recipes were wrong. So each fleet recipe is now tuned until
its growth, headcount, and span describe one firm — measured from its own
finance ledger, recorded in the recipe, and re-checked on every test run
(`test_fleet_recipe_growth_headcount_and_span_describe_one_firm`). This is
the pattern worth stealing: when a fix reveals that your inputs were wrong,
the fix is not to soften the model.

[SPEC.md](SPEC.md) is the current unit of work and says exactly what it
commits to. Each turn's board findings stay committed next to the org they
judged. Cross-document voice is the genuinely hard one, and it has no
scheduled fix.

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

**We publish what the critic said about us.** Every org ships the board's
findings next to the documents they judge, unflattering ones included — 28
of them against the current flagship, 16 rated major, quoted at length
[above](#what-is-not-modeled-today). Two of those drove BACKLOG entries
carrying the arithmetic that proves them. The board's findings against the
*previous* flagship drove milestones M8 and M9, and are why the frozen
roster, the clause-less contracts, and the lockstep finance are gone.
`docs/REVIEW-CALIBRATION.md` records the board being calibrated against two
hand-labeled defects before its findings were relied on, including the case
where it **overruled the metric** (judging a flagged similar pair to be
realistic template reuse) and the case where it caught what the metric
provably cannot see.

### The evidence, concretely

- **440 tests** across three tiers (`bin/test`), keyless and offline; the
  `org` tier validates all seven committed fixtures, derives every recipe,
  re-derives every fixture's structure byte-identically, and checks each
  fleet recipe's internal coherence in ~4.8s.
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

### What this does not prove

The board has been calibrated on one org, one model, one run, with no
negative control, so its false-positive rate is unmeasured — and it is not
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

**Round 1 — Opus 4.8 against Haiku 4.5.** One corpus a blind reviewer said
would "take a deliberate effort to catch out"; the other it rejected
outright as too thin to survive first contact, at **60% of the words its
briefs asked for**, with 8 of 9 documents off brief. Both corpora passed
every validator rule that ran, with zero errors. The folklore was right, and
the gap is not subtle. But Haiku is a small, fast, cheap model, so this
establishes that the axis is real — not where a strong mid-tier model sits
on it.

**Round 2 — Opus 4.8 against Sonnet 5.** Run because Round 1 licenses no
conclusion about a mid-tier model, and because "Opus is overkill for placing
prose around placeholders" is a reasonable hypothesis that deserved a number
rather than a dismissal. The quality gap turned out to be modest: **0.853 of
brief against 0.967**, with 4 of 22 documents off brief against 0. Sonnet is
mildly terse, not thin. Nothing like Haiku's collapse. On quality alone it
would be a defensible choice.

**The cost case is what failed instead.** Sonnet spent **1.89x the tokens**
for byte-identical work — it made more tool calls, re-read more, and
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
— a test that fails when the corpus reads thin — is one we deliberately do
not make.

**No test asserts prose quality, and none ever will.** Quality has no
validated threshold here, and the moment a similarity or length number
becomes a bar, the generator learns to satisfy the bar rather than the
intent: a similarity rule teaches it to paraphrase. That is Goodhart, and
`bin/test` is kept free of it by construction — no tier may touch a model,
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
Both rounds are n = 1, one org and one run per arm, and the effort axis was
never independently varied — they establish a default with evidence behind
it, not an effect size.

And the 13% figure is softer than it looks. It holds only if both arms spend
tokens in the same input/output/cache mix, and we have evidence they do not:
Sonnet re-read more (proportionally more input and cache-read tokens, the
cheap components) while producing fewer words (fewer output tokens, the
expensive one). That skew makes 1.135x an *over*-estimate of Sonnet's true
cost, and a blended-price shift of ~12% would drop it under 1.0 and flip the
headline. We cannot settle it from the artifacts: the harness reports one
undifferentiated token total per worker. So the defensible claim is narrower
than "Sonnet is more expensive" — it is that **Sonnet's 0.6x rate card does
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
before deciding a cheaper one saves you anything — measured, it did not.

## What is in the box today

### Which fixture proves what

The fleet table [above](#what-ships-today) says what each org *is*. This says
what each one *exercises*, so you can pick the fixture that stresses the part
of your system you care about. Every row is read from that org's committed
charter. Most columns have a validator rule that recomputes them from the
recipe and fails the org on a mismatch — `ACL-01/02/03`, `LEG-01`,
`SCAN-01/02`, `LOC-01/02/03` (the hard cases), `AFF-01/02`, `EML-01`,
`MENT-01/02` (the ambiguity surfaces). Decks are the exception: they are
covered by the generic "every file opens in its native reader" rule
(`FILE-01`) rather than by a deck-specific recompute.

| org | ACL | legacy | scans | OCR | sig-page fee | filename date | surname | nickname | multi-affil | decks | mail | hires/departs/promos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `brackenridge-civil` | open | **1.0** | 0.5 | 0.5 | — | — | — | — | — | ✓ | — | 3/1/1 |
| `hollowell-ip` | departmental | — | — | — | ✓ | — | — | ✓ | — | ✓ | ✓ | 4/1/1 |
| `meridian-actuarial` | departmental | — | — | — | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | 5/1/2 |
| `northgate-staffing` | open | — | — | — | — | — | ✓ | ✓ | — | ✓ | ✓ | 5/1/2 |
| `saltmarsh-environmental` | departmental | — | 0.6 | 0.5 | ✓ | ✓ | — | — | ✓ | ✓ | — | 4/1/1 |
| `verdant-health` | open | — | 0.5 | — | — | — | — | — | ✓ | ✓ | — | 1/1/1 |
| `dev-mini` | open | — | — | — | — | — | — | — | — | — | — | 0/1/1 |

Reading it: **`brackenridge-civil`** is the ugly-format org — `legacy_ratio`
at 1.0 means *every* office document is a real pre-2007 OLE container (24
`.doc`, 9 `.xls`, 2 `.ppt`), half its PDFs are degraded scans, and half of
those carry a synthetic OCR layer. **`saltmarsh-environmental`** and
**`verdant-health`** are where a contact changes employer mid-history, with
dated `works_at` edges and era-correct resolution per document date.
**`meridian-actuarial`** carries both hard-case knobs, so a fee lives only on
a signature page and a date lives only in a filename. **`dev-mini`** is
deliberately bare: it is the regression oracle the ~356-test unit tier builds
on, so it stays small and cheap rather than proving breadth.

- The full pipeline, end to end, proven on all seven, every one generated on
  the v2.0 stack through the live airlock and byte-pinned.
- Access-control ground truth: the recipe's `acl_posture` derives
  `ledger/acl.json` (exactly which internal people may read which
  documents: matter teams plus the CEO-equivalent for engagement folders,
  finance restricted to its owners) plus a human-readable PERMISSIONS.md
  in the share root, both enforced by validator rules that recompute the
  grants from the posture. Grants are access *as of the end of the
  corpus*, so someone the roster retires mid-history holds none — which
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

## Where this is going

**The v2.0 arc is closed.** It was scoped directly from what the review
board said about the old flagship, and it ran four milestones:

| | what landed |
| --- | --- |
| **M8** | Roster churn, behavioral finance, staffing rotation, date-scoped briefs, era-appropriate naming. The firm gets a history. |
| **M9** | The document-supply model: a genre registry driving volume from the firm's engagements, fiscal years, and hires (no fixed skeleton), realistic per-genre lengths, and a folder taxonomy beyond `Engagements/Finance/Firm`. |
| **M10** | Parallel authoring: a bounded K-wide window of concurrent authors over a serial, single-writer merge. This is what makes a fleet-sized run a few hours instead of a few days. |
| **M11** | The fleet reset: six new recipes (civil engineering, environmental, actuarial, IP law, executive search, healthcare; 1999–2025), all generated through the live airlock, the six pre-v2.0 fixtures retired, and the byte pin restored fleet-wide — which re-freezes the fixtures and restores additive evolution. |

**Next: M12, one flagship org large enough to defeat a context window.**
Today's whole fleet is ~280 documents; you can fit that in a 1M-token
context and answer questions about it without retrieving anything, which
means it cannot prove a retrieval system works. See
[docs/SCALE.md](docs/SCALE.md) for how big that has to be, what it costs at
measured per-batch rates, and why resume stops being a convenience and
becomes the only reason it is possible.

Known and logged rather than hidden: `BACKLOG.md` carries the two fleet-wide
board findings above (the engagement book read as the whole business; dates
drawn with no business-day calendar), the board's unmeasured false-positive
rate, and three more. Cross-document voice is the genuinely hard one and has
no scheduled fix.

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
[zat.env](https://github.com/peterzat/zat.env) — spec-driven turns,
adversarial code review with builder/verifier separation, and a pre-push
gate that blocks unreviewed code.

The committed fleet was authored through the same airlock this repo ships,
by `claude-opus-4-8[1m]` (the six fleet orgs at `/effort xhigh`, `dev-mini`
at `max`). Every org's `GENERATION-REPORT.md` records what actually wrote
it, batch by batch — self-reported, and treated as a record rather than an
oracle for the reason [Round 1
found](#which-model-should-write-your-documents).

## License

Apache-2.0. Copyright (c) 2026 Peter Zatloukal. See LICENSE and NOTICE.
