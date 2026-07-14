# OrgSmith

OrgSmith generates complete synthetic organizations. Given a recipe
(`ORG-CHARTER.md`), it produces a browsable document store for a plausible
fictional company (real .docx/.pdf/.xlsx files with realistic filenames,
folder trees, and letterheads) plus a `-metadata` ground-truth directory
(personas, ledgers, canonical facts, document manifest, and machine-readable
state) that records every fact the generator planted.

Agentic tooling that operates across an organization's data corpus needs
realistic development and test corpora. Real corpora are confidential,
single-instance, and carry no ground truth. A synthetic org is shareable,
generable in variants, and, because the generator knows every fact it
planted, ships with deterministic evals for whatever knowledge-base,
people-graph, or RAG system is built over it.

## How it works

OrgSmith runs inside a Claude Code session. Content generation consumes the
logged-in user's plan via project skills; there are no API keys anywhere.
Deterministic scaffolding, rendering, and validation are Python; the model
authors only surface prose.

The pipeline is a facts-first staged design with an "airlock" between Python
and the model:

- A deterministic ledger owns all facts (people, dates, money, engagements).
- Python never calls a model. Every model touchpoint is a CLI verb pair:
  `--emit-context` / `--next-batch` writes a self-contained JSON work order;
  `--ingest <file>` validates the model's deliverable and merges it.
- The model writes surface text with `{{fact:...}}` placeholders; Python
  resolves them at render time, so a number can never be mistranscribed.
- Every document is validated against the ledger after rendering.

Stages (verbs of `python -m orgsmith`):

```
charter -> foundation -> fabric -> docplan -> author -> render -> assemble
                                     |
                          validate / status / doctor
```

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
bin/test                      # short + unit + org tiers, offline, no keys
.venv/bin/python -m orgsmith doctor
```

To generate an org inside a Claude Code session, invoke the `/forge` skill
with a recipe slug (e.g. `/forge dev-mini`). `recipes/dev-mini` is the
permanent tracer fixture: a ~5-person firm with 12-15 documents.

## Layout

```
recipes/<slug>/ORG-CHARTER.md      # input recipes
orgsmith/                          # the generator package
companies/<slug>/                  # generated file share (committed fixtures)
companies/<slug>-metadata/         # ground truth for that org
.claude/skills/                    # the model-facing skills (the product's UI)
docs/                              # format and architecture docs
tests/  bin/  hooks/               # test tiers, helper scripts, git hooks
```

Everything under `companies/` is fictional and machine-generated. Every
rendered file carries a machine-readable synthetic-provenance marker.

---

Copyright (c) 2026 Peter Zatloukal. All rights reserved. See LICENSE.
