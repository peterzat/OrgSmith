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
  structure without regeneration or hand edits. This rule was SUSPENDED for
  the v2.0 window (M8-M11) by user decision and is **restored as of M11b**:
  the fleet is regenerated, re-frozen, and pinned fleet-wide again
  (`tests/test_org_regen.py`, `PINNED = SLUGS`). The `seeds.py` per-stream
  discipline was never relaxed — it is what keeps a single generation
  reproducible.
- **Committed fixtures are frozen.** Never edit or regenerate a committed
  org's ledgers, manifest, or authored prose. The M8-M11 carve-out for the
  v2.0 reset is **closed as of M11b**: the new seven-org fleet is generated
  and the pin is restored fleet-wide (`tests/test_org_regen.py`,
  `PINNED = SLUGS`), not scoped to `dev-mini`. `evals/`, `acl.json`,
  `GENERATION-REPORT.md`, and PERMISSIONS.md are derived and may always be
  re-emitted. Validator rules grandfather by CHARTER, not by artifact
  absence: skip visibly only when the recipe knob is off; a knob that is
  on with its artifact missing is a failure (tamper evidence), never a
  skip. The same rule applies to tests: a fixture-hosted test whose host is
  deleted must fail or be re-hosted, never skip itself into a silent pass.
- The user-facing product name appears in code only via `PRODUCT_NAME` in
  `orgsmith/__init__.py`. The pre-rename working name must not appear
  anywhere in the repo (enforced by a short-tier test; see
  `tests/test_short.py` for the check).

## Frozen-fixture carve-out, realism wave (M13-M16), opened 2026-07-21

The frozen-fixtures rule is suspended in the following scoped way and no
other: (1) the email pilot org `ashcombe-advisory` is a wave workbench and
may be regenerated or extended by M14 and M15 as knobs land; (2) `dev-mini`
may be regenerated exactly once, in M15; (3) the six remaining v2.0 fleet
orgs, the exemplar `northgate-staffing`, `calderwood-partners`, and the pilot
may be regenerated exactly once each, in M16, under recipes updated to the
wave's knobs. Regeneration is always wholesale (delete and re-run the full
pipeline from the recipe), never an in-place edit of ledgers, manifest, or
prose. `PINNED = SLUGS` stays enforced and must be green at every commit,
including mid-wave. Additive evolution is NOT suspended: every wave capability
still lands as a default-off knob with inert schema defaults and new seed
streams, proven inert against not-yet-regenerated fixtures before any org
turns it on. The carve-out closes when M16's re-freeze criterion lands, at
which point this paragraph is replaced by closure language mirroring M11b.
This supersedes the BACKLOG decision `fleet-regenerates-under-the-new-knobs`
(2026-07-17) by user decision; that entry's own revisit criteria have fired.

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
