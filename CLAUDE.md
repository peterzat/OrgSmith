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

## Frozen-fixture carve-out, answer-key turn (M17): CLOSED as of 2026-08-02

The M17 carve-out is **closed**. `northgate-staffing` was regenerated once,
wholesale, under a recipe enriched with existing knobs (departmental ACL, mail
threads with mundane traffic and both mention exemptions, scans with an OCR
layer, signature-page and filename-date hard cases) plus
`graph_targets.alias_agreement`, then boarded and re-frozen. `PINNED = SLUGS`
is enforced fleet-wide again and was green at every commit, including mid-turn.

Additive evolution was never suspended and remains in force. Both knobs added
this turn (`graph_targets.alias_agreement`,
`mail.exempt_recipient_mentions`) landed default-off with inert schema
defaults on the existing `orgsmith/<kind>@<ver>` schema ids, drew nothing from
existing seed streams, and were proven inert against the frozen fleet before
the exemplar turned them on. A test now asserts both halves of that
grandfathering: an org that adopted a knob runs its rule clean, and an org
that did not still skips visibly. Any post-turn capability lands the same way.

`evals/`, `acl.json`, `GENERATION-REPORT.md`, `review/`, `baselines/`,
`DATA-CARD.md`, and PERMISSIONS.md remain derived and may always be
re-emitted. Regenerating a committed org's ledgers, manifest, or authored
prose again requires a fresh, user-approved carve-out.

**The mail demonstrators were deliberately left out** (user decision,
2026-08-02). `hollowell-ip` and `meridian-actuarial` still carry the
full-name-in-body device described below; the
`mail.exempt_recipient_mentions` knob that would close it is landed and
proven inert, but the orgs were not re-run. Their data cards record it.

Residual on the exemplar, recorded not fixed (board findings are published,
never prose-fixed): the recipient exemption removed the device from
person-to-person mail but not from distribution-list mail, where the To
header carries the list address rather than member names, so MENT-01 still
needs the body mention. The result is a broadcast that greets one person by
first name and then names them in full to the room. Closing that needs
either a mention model that understands list membership or a planner that
stops giving a broadcast a single participant, and it is its own unit of
work.

## Frozen-fixture carve-out, realism wave (M13-M16): CLOSED as of M16 (2026-07-28)

The realism-wave carve-out is **closed**. All eight fleet orgs plus `dev-mini`
were regenerated wholesale under the wave's knobs and re-frozen: the fixtures
are frozen again, `PINNED = SLUGS` is enforced fleet-wide
(`tests/test_org_regen.py`), and it was green at every mid-wave commit. Additive
evolution is **restored** exactly as at M11b: any post-wave capability lands as
a default-off recipe knob with inert schema defaults on the existing
`orgsmith/<kind>@<ver>` schema ids, drawing randomness only from NEW `seeds.py`
streams, proven inert against the frozen fleet (loads, validates clean, and
re-derives byte-identical structure) before any org turns it on. The per-stream
seed discipline was never relaxed. `evals/`, `acl.json`, `GENERATION-REPORT.md`,
`review/`, and PERMISSIONS.md remain derived and may always be re-emitted;
regenerating a committed org's ledgers, manifest, or authored prose again
requires a fresh, user-approved carve-out.

Known residual, recorded not fixed (board is read-only; fixing needs a new
carve-out): in the two mail demonstrators, forge-author workers put an email
recipient's full name in the message body to satisfy the ingest mention check.
The related `hollowell-ip` `To:/Cc:` duplicated-header banner is fixed as of
v2.1.1: the renderer strips an authored header banner from `.eml` bodies and
`doc_text` reads the transport headers, so MENT-01 still finds the recipient,
and a committed test asserts no fleet mail body carries a header banner. The
full-name-in-body device remains: a proper fix (exempt an email's recipient
from its required body mentions, the way `exempt_author_mentions` exempts the
author, then re-render the mail orgs) is its own unit of work.

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
