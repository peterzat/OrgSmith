# OrgSmith project conventions

## What this is

Frontier-model-powered generator of complete synthetic organizations. Read
README.md for the product shape and SPEC.md for the current unit of work.

## Hard rules

- **Airlock:** Python in `orgsmith/` never calls a model and never touches
  the network. Model touchpoints are exactly the CLI verb pairs
  `--emit-context`/`--next-batch` (writes a JSON work order) and
  `--ingest <file>` (validates and merges a deliverable). Skills are the
  only reader/writer of work orders.
- **Facts are load-bearing; prose is replaceable.** All numbers, dates, ids,
  names, and relationships come from the deterministic ledgers. The model
  writes surface prose with `{{fact:...}}` placeholders. Never let generated
  text carry a literal value that the ledger owns.
- **Resume state is file-derived, never conversation memory.** Everything a
  stage needs is a pure function of committed files plus `state.json`.
- **Never LLM-grades-LLM in automated test tiers.** Model passes happen only
  inside skills.
- `orgsmith/schemas.py` is the keystone: ALL inter-stage contracts live
  there as pydantic models with `orgsmith/<kind>@<ver>` schema ids.
- **Additive evolution — SUSPENDED for the v2.0 window (M8-M11).** The
  standing rule: new capabilities are recipe knobs that default off, schema
  fields that default inert on the existing schema ids, and randomness
  drawn only from NEW `seeds.py` streams, so every committed fixture keeps
  loading, validating clean, and regenerating byte-identical structure
  without regeneration or hand edits. For the v2.0 arc this is deliberately
  relaxed by user decision: the realism knobs default ON with one code
  path, and the fleet is regenerated rather than held byte-identical.
  Restore this rule at M11 when the new fleet is frozen. The `seeds.py`
  per-stream discipline is NOT relaxed — it is what keeps a single
  generation reproducible, which still holds.
- **Committed fixtures are frozen — EXCEPT during the v2.0 reset.** The
  standing rule: never edit or regenerate a committed org's ledgers,
  manifest, or authored prose. During M8-M11 the fleet is being rebuilt, so
  regeneration is expected; `dev-mini` is the only byte-pinned fixture until
  M11 restores the pin fleet-wide (see `tests/test_org_regen.py`, `PINNED`).
  `evals/`, `acl.json`, and PERMISSIONS.md are derived and may always be
  re-emitted. Validator rules grandfather by CHARTER, not by artifact
  absence: skip visibly only when the recipe knob is off; a knob that is
  on with its artifact missing is a failure (tamper evidence), never a
  skip.
- The user-facing product name appears in code only via `PRODUCT_NAME` in
  `orgsmith/__init__.py`. The pre-rename working name must not appear
  anywhere in the repo (enforced by a short-tier test; see
  `tests/test_short.py` for the check).

## Environment

- This box runs Python 3.10; `.python-version` says 3.12. Code stays
  3.10-compatible (no `match` on types we ship, no 3.11+ stdlib).
- Always `python3 -m venv .venv`; run everything via `.venv/bin/python`.
- LibreOffice is required on the generation box for legacy-format
  rendering (`legacy_ratio` recipes convert .docx/.xlsx/.pptx to
  .doc/.xls/.ppt via `soffice --headless` at render time only). Install:
  `sudo apt-get install --no-install-recommends -y libreoffice-writer
  libreoffice-calc libreoffice-impress`, then confirm `python -m orgsmith
  doctor` reports `soffice ok`. CI deliberately has NO LibreOffice:
  validation of every committed fixture (including legacy files) must
  stay pure Python (olefile, xlrd, stdlib email, python-pptx, pypdf).

## Testing

- `bin/test [short|unit|org]` (default: all tiers). Marker-based pytest,
  keyless and offline. `org` tier validates the committed fleet under
  `companies/`.
- Skills-in-repo deviation: `.claude/skills/` is versioned here because the
  skills ARE the product, unlike the house norm of global skills.

## Git

- Commit in small increments with tests in the same increment. Do not push
  or modify remote state without explicit user confirmation.
