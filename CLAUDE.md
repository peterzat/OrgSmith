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
- **Additive evolution.** New capabilities are recipe knobs that default
  off, schema fields that default inert on the existing schema ids, and
  randomness drawn only from NEW `seeds.py` streams, so every committed
  fixture keeps loading, validating clean, and regenerating byte-identical
  structure. Prove a knob inert against the frozen fleet before any org
  turns it on.
- **Committed fixtures are frozen.** Never edit or regenerate a committed
  org's ledgers, manifest, or authored prose; that takes a fresh,
  user-approved carve-out. `PINNED = SLUGS` (`tests/test_org_regen.py`) is
  enforced fleet-wide and must be green at every commit. `charter.json`,
  `evals/`, `acl.json`, `review/`, `baselines/`, `GENERATION-REPORT.md`,
  `DATA-CARD.md`, and PERMISSIONS.md are derived and may always be
  re-emitted. Adding a new org is not a regeneration.
- **Grandfather by charter, never by artifact absence.** A validator rule
  skips visibly only when its recipe knob is off; a knob that is on with its
  artifact missing is a failure (tamper evidence). A fixture-hosted test
  whose host is deleted or moves must fail or be re-hosted, never skip into
  a silent pass.
- **Nothing that is not an oracle may gate.** `orgsmith/review/structure.py`,
  the unowned-number count, and every board or probe number are
  measurements: no threshold they produce enters a test tier or a validator
  rule. Ingest may reject only on an oracle (a ledger fact against the text).
- The user-facing product name appears in code only via `PRODUCT_NAME` in
  `orgsmith/__init__.py`. The pre-rename working name must not appear
  anywhere in the repo (enforced in `tests/test_short.py`).

## Freeze status

**A carve-out is OPEN (M17e, approved by the user 2026-10-13):** regenerate
`ashcombe-advisory`, `hollowell-ip` and `meridian-actuarial` once, wholesale,
to close the mail-mention device. No other org may move. History of every
carve-out, and of what each turn did and did not claim, is in
`docs/FREEZE-LOG.md`. Known residuals are recorded on the data cards and in
BACKLOG.md, never prose-fixed.

## Working on the fleet

- **Serialization traps.** `dump_json` serializes every model field, so a new
  field on `Fact`, `Engagement`, or `ManifestEntry` writes a key into every
  committed ledger and breaks the pin: avoid it (M17b put scope facts in the
  existing `facts` list for this reason). A new field on the charter's
  sub-models rewrites every `charter.json` and, through
  `datacard._knob_rows`, every data card; that is derived and allowed.
- **Re-emission order** when a derived artifact moves: `charter` for every
  org (if a charter field was added), then `report`, then
  `tools/checksums.py`, then `data-card` for every org (the cards quote their
  own checksum row). `emit-schemas` after any schema change.
- **Experiments run on pinned code.** A measurement that spans code changes
  runs from a git worktree pinned at its pre-registration commit, with the
  grading scripts hashed in the pre-registration (`docs/M17D-OPUS55-PROBE.md`).

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
