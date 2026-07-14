# OrgSmith

Generate a complete, fictional company: a browsable file share full of real
`.docx`, `.pdf`, and `.xlsx` documents, plus a ground-truth ledger that
knows every fact planted in them.

```
companies/dev-mini/
├── TOC.md
├── Engagements/
│   ├── Weaver-Reeves/
│   │   ├── 2019.07.07 - Engagement Letter - Weaver-Reeves - EXECUTED.pdf
│   │   ├── 2019.07.20 - Kickoff Memo - Operational Review.docx
│   │   ├── Meeting Minutes 2019-08-27 - Weaver-Reeves.docx
│   │   └── 2019.10.03 - Status Report - Weaver-Reeves v2 FINAL.docx
│   ├── Johnson PLC/ ...
│   └── Foley Group/ ...
├── Finance/
│   ├── FY2021 Financial Summary.xlsx
│   └── FY2022 Financial Summary.xlsx
└── Firm/
    └── Firm Overview 2021 v3.docx

companies/dev-mini-metadata/     <- ground truth for all of the above
├── foundation.json              # roster, org chart, personas, clients
├── ledger/                      # finance series, engagements, people graph
├── docplan/manifest.jsonl       # every doc: genre, date, authors, planted facts
├── docir/                       # authored text with facts still as placeholders
└── state.json                   # resumable pipeline state
```

The documents are written by a frontier LLM and read like a real firm wrote
them: engagement letters on letterhead with signature blocks, meeting
minutes that name every attendee, spreadsheets whose formulas recompute to
the values the finance ledger says. The `-metadata` directory is the answer
key.

## Why

If you are building anything that operates over an organization's documents
(knowledge bases, RAG pipelines, people-graph extraction, agents that
navigate file shares) you need corpora to develop and test against. Real
corpora are confidential, single-instance, and carry no ground truth.

A synthetic org is shareable, regenerable in variants, and, because the
generator planted every fact, comes with a deterministic answer key: which
documents mention which people, what the fee on that engagement was, which
spreadsheet cell ties to which ledger line. "Did my extractor find the fee
in the signature page?" becomes a checkable assertion instead of a vibe.

This matters double for agentically coded projects: when an AI is writing
your retrieval system, high-fidelity test corpora with ground truth are
what make its feedback loop honest.

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
- After rendering, a 19-rule validator ties every document back to the
  ledger: planted facts and planned name mentions appear verbatim in
  extractable text, hard-case location policies hold (a
  signature-page-only fee appears on exactly that pdf page and nowhere
  else; a filename-only date never appears in document text), workbook
  formulas recompute to ledger values, authors were employed on the date
  they wrote, org charts are acyclic, the people graph has no orphans or
  dangling edges, every file opens in its native reader, and every file
  carries a machine-readable synthetic-provenance marker.

```
charter -> foundation -> fabric -> docplan -> author -> render -> assemble
 (recipe)   (roster)    (ledgers)  (manifest)  (model)   (files)    (TOC)
                            validate / status / doctor
```

Long runs checkpoint into `state.json`: kill the session mid-generation,
re-run `/forge <slug>`, and it resumes exactly where it stopped with no
duplicated or lost documents. Structure is fully seeded; the same recipe
regenerates the same org (ids, names, tree, numbers), with only the
model-authored prose varying.

## Quick start

```bash
git clone https://github.com/peterzat/OrgSmith.git && cd OrgSmith
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt   # WeasyPrint needs system Pango
bin/test                                        # short + unit + org tiers, offline
```

Then open Claude Code in the repo and run:

```
/forge dev-mini        # regenerate the tracer org
```

To make your own company, write a recipe (see
[docs/RECIPE-FORMAT.md](docs/RECIPE-FORMAT.md)) under `recipes/<slug>/` and
run `/forge <slug>`. A recipe is one Markdown file: headcount, date range,
document mix, finance profile, and a prose brief that sets the firm's
voice.

**Which model writes the documents?** Whatever model your Claude Code
session is running; OrgSmith pins nothing and needs no API keys, so
generation bills to your existing plan. Content quality tracks the model:
use the strongest one available to you with a high effort setting for
authoring passes. Deterministic stages (scaffold, ledgers, rendering,
validation) run as plain Python and cost no tokens at all.

## What is in the box today

- The full pipeline, end to end, proven on three committed fixtures:
  `dev-mini` (a 5-person consultancy, 13 documents, three engagements,
  2019-2022); `torchlake-engineering` (a 6-person engineering firm, 11
  documents, 2018-2024) generated with every ambiguity knob on: a
  surname-collision pair, a nickname alias planted in rendered minutes,
  and an external contact with a mid-history employer change; and
  `quillbrook-appraisal` (a 5-person appraisal practice, 11 documents,
  2016-2020) generated with the hard-case knobs on.
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
  documents, and its location class), and a people-graph answer key (with
  alias credit and per-ambiguity-class recall) from the ledgers, and
  `score` grades an external system's answers with per-question
  attribution, from nothing but the `evals/` directory. Deterministic, no
  model involved; ground-truth answers score 100% by construction.
- Renderers: `.docx` (python-docx: letterhead, PAGE-field footers,
  signature blocks, real core properties), `.pdf` (WeasyPrint with
  paged-media letterhead, pikepdf metadata, remote fetches blocked), and
  `.xlsx` (xlsxwriter with real formulas plus cached values that tie to
  the ledger).
- The airlock, checkpoint/resume, the 19-rule validator, capability
  probing (`doctor`), and machine-readable pipeline status (`status
  --json`).
- Skills: `/forge` (orchestrator) and `forge-author` (per-batch worker
  with a fresh context, which is what lets large orgs span sessions).

On the roadmap, in rough order: an ACL overlay (PERMISSIONS.md) with a
visibility eval suite, more formats (`.pptx`, `.eml` mail archives,
scanned-and-degraded PDFs with synthetic OCR layers, legacy
`.doc`/`.xls`/`.ppt`), an adversarial review board, and a committed
six-company fleet from a 1988 boutique law firm to a modern B2B SaaS.

## Provenance and safety

Everything generated is fictional. Every rendered file carries a synthetic
marker in its native metadata (docx/xlsx custom properties, PDF document
info), and a validator rule fails the org if one is missing. See NOTICE.

## Built with

OrgSmith is itself an agentically coded project: designed and implemented
in [Claude Code](https://claude.com/claude-code) running
[zat.env](https://github.com/peterzat/zat.env) (spec-driven turns,
adversarial code review, pre-push gates), using Claude Fable 5 at
`/effort xhigh`. The committed dev-mini org was authored the same way,
through the same airlock shipped in this repo.

## License

Apache-2.0. Copyright (c) 2026 Peter Zatloukal. See LICENSE and NOTICE.
