# SPEC

## Spec — 2026-07-14 — OrgSmith M0+M1: scaffold and dev-mini tracer bullet

**Goal:** Bootstrap OrgSmith from an empty directory to a working tracer bullet: the project scaffold (M0) and a dev-mini synthetic org generated end-to-end through the airlock pipeline (M1), proving the load-bearing mechanics (work-order/ingest contract, session resume, ledger-grounded rendering, deterministic validation) before any real recipe is attempted.

### Acceptance Criteria

- [x] `/forge dev-mini` runs the full pipeline (charter, foundation scaffold plus one enrichment pass, docplan, author loop, render, assemble, validate) and produces `companies/dev-mini/` with 12-15 rendered docs including at least one .docx, one WeasyPrint PDF, and one .xlsx, plus a TOC listing every doc, and `companies/dev-mini-metadata/` holding the ground truth used (charter, foundation, manifest, DocIR, state). Every rendered file opens in its native reader (python-docx, pypdf or pypdfium2, openpyxl).
- [x] Resume works: killing the session mid-authoring and re-running `/forge dev-mini` completes generation with no duplicated and no lost docs (manifest entries and rendered files match 1:1, per-doc hashes in state.json are consistent, completed stages and docs are not redone).
- [x] Airlock holds: the `orgsmith` package makes no model or network calls (every stage runs offline; model passes happen only in skills), and `--emit-context`/`--next-batch` writes a self-contained, schema-valid work-order JSON. Re-issuing without an intervening ingest returns the same outstanding work order instead of creating a second.
- [x] `--ingest` rejects, with non-zero exit and an actionable message: schema-invalid deliverables, deliverables referencing unknown doc ids, and foundation enrichment that alters protected fields (ids, dates, reporting lines). Accepted deliverables are merged and reflected in `status --json`.
- [x] `python -m orgsmith validate companies/dev-mini` exits 0 with at least 6 rules active, including a fact-echo rule (every manifest facts_ref value appears in the doc's extractable text). Deliberately corrupting the generated org (delete a rendered file; change a planted fact value in the manifest) makes a matching rule fail with non-zero exit.
- [x] Unit tests prove the grounding mechanics: rendering fails loudly on an unresolved or unknown `{{fact:...}}` placeholder, and an xlsxwriter workbook written with `write_formula(..., value=...)` reads back (via openpyxl, no recompute) cached values equal to the ledger-computed numbers.
- [x] Pure stages are idempotent: re-running charter, foundation scaffold, or docplan on unchanged inputs produces byte-identical output (ids, names, tree, and manifest are stable under the recipe seed).
- [x] From a clean checkout, `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` succeeds, and `bin/test` passes (short and unit tiers) with no API keys; tests run offline.
- [x] M0 scaffold present: README.md, LICENSE (all rights reserved with source-available-for-viewing wording), CLAUDE.md, docs/RECIPE-FORMAT.md draft, pyproject.toml, pinned and commented requirements.txt / requirements-dev.txt, .gitignore, bin/setup-deps, bin/install-hooks; the installed pre-push hook runs `bin/test short` and blocks the push when it fails; the user-facing product name appears in code only via `PRODUCT_NAME` in `orgsmith/__init__.py`.
- [x] The project is a git repository with incremental local commits (scaffold committed before tracer work). No remote creation or push happens without explicit user confirmation.

### Context

Adopted from plan `~/.claude/plans/we-re-making-a-plan-virtual-sedgewick.md`; read it for the full architecture (stages, schemas, package layout, milestones M0-M7). This turn covers M0 and M1 only. Foundation/fabric depth, hard cases and golden evals, render breadth (pptx, scans, legacy, .eml), the adversarial review loop, and the six-company fleet are later milestones and out of scope here.

Constraints the implementer needs:

- Airlock pattern: Python never calls a model. Every model touchpoint is a CLI verb pair (`--emit-context`/`--next-batch` writes a self-contained work-order JSON; `--ingest` validates with pydantic and merges). Skills are the only reader/writer of work orders; content generation consumes the logged-in Claude Code session, no API keys anywhere.
- Skills live in-repo under `.claude/skills/` (deliberate deviation from the global-skills norm; here the skills are the product). This turn ships `/forge` v0 and the `forge-author` forked worker only.
- `orgsmith/schemas.py` holds all inter-stage pydantic contracts (the keystone file). `state.json` is committed; resume state is always file-derived, never conversation memory.
- `recipes/dev-mini` (~5 people, 12-15 docs) is the permanent tracer fixture; its generated org is intended as a committed fixture for the future `org` test tier.
- Environment: this box runs Python 3.10 (`.python-version` says 3.12; code stays 3.10-compatible). Pango is present, so WeasyPrint installs via pip. LibreOffice is absent and not needed for M1; the `doctor` verb probes and records capabilities rather than failing.
- House practices that bind here: verification over prompting (validator quality is the ceiling on generation quality; invest there first); never LLM-grades-LLM in automated test tiers (model passes happen only inside skills); small committable increments with tests in the same increment; when a fix attempt fails twice, revert and re-evaluate.
- Notices: "Copyright (c) 2026 Peter Zatloukal. All rights reserved." in LICENSE, README footer, and pyproject author. No per-file headers. License terms beyond that are TBD.
- GitHub: creating the private remote and any push are user-gated at execution time. `git init` and local commits proceed without asking.
- Mid-turn user redirections (2026-07-14, after the criteria above were set): the LICENSE criterion was satisfied as written at M0, then the user redirected licensing to Apache-2.0 with copyright retained (NOTICE file added); the user explicitly authorized creating the private remote, then flipping it public, pushing, and tagging v1.0.0 with semver adopted (version 1.0.0). The remote-gating criterion is checked off on the strength of those explicit instructions.

<!-- SPEC_META: {"date":"2026-07-14","title":"OrgSmith M0+M1: scaffold and dev-mini tracer bullet","criteria_total":10,"criteria_met":10} -->
