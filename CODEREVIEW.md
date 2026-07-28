# CODEREVIEW

## Review — 2026-07-28 (commit: eff521e)

**Summary:** Full review of the three follow-up fixes plus the release cut
(`origin/main`..HEAD): the hollowell mail-render blocker, the genre-spec brief
leak, and the v2.1.0 packaging. Code changes: `render/eml.py` (strip a leading
transport-header block from eml bodies), `validate/rules.py` (fold To/Cc header
display names into eml `doc_text`), `tools/checksums.py` (new), packaging
(`pyproject.toml`, `requirements.lock`, `Dockerfile`), a version bump, and three
reworded recipe briefs with re-derived charters. Fixtures: re-rendered eml,
re-derived charters, resume state.json, hollowell board refresh.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN issues.

- `render/eml.py` `strip_leading_header_block`: correct and precise — the regex
  matches only `Keyword: ` at line start for known header keywords, so a body
  opening "To all staff," or "Subject to review:" is untouched; it strips a
  contiguous top run plus one blank line; idempotent. Unit-tested directly and
  proven inert against the synthetic `eml_org` and the whole fleet (no body
  regressed). Applied in `_body_text`, covering both the knob-off and mail-block
  paths.
- `validate/rules.py` eml `doc_text`: folds To/Cc header display names into the
  extracted text so MENT-01 finds a recipient full name that (correctly) lives
  in the transport headers after the body banner is stripped. `get_all(..., [])`
  and `getaddresses` are used safely; it can only add mentions, never introduce
  a fact-value leak (header display names are person names, not fact values).
  Verified by the green org tier (no MENT-01/FACT-01 regression across the fleet).
- Item 2 (brief reword) is surgical: the three edits change only
  `charter.narrative`; foundation, ledger, and manifest re-derive byte-identically,
  so the byte pin holds with no re-authoring, and the committed overviews were
  verified not to parrot the leak.
- Packaging verified end to end: `pip install .` from a clean venv builds
  `orgsmith-2.1.0` and installs all 16 deps; the `orgsmith` console script and
  `real_firms.txt` package data work from outside the repo; the Dockerfile builds
  and `orgsmith doctor` reports green inside it (weasyprint ok, soffice ok);
  `tools/checksums.py --check` confirms CHECKSUMS.md is current.
- NOTE (security, pre-existing, not introduced here): `ManifestEntry.path` is an
  unconstrained `str`, so a tampered `manifest.jsonl` with a `/`-absolute or
  `..` path makes validators stat/open outside the share tree. Only a NOTE: no
  write sink, no finding echoes read content (no exfiltration), the airlock
  removes any network channel, and MAN-01 flags a traversal path loudly rather
  than passing it. Fix (future): reject leading `/` and `..` at the schema or in
  `load_manifest`. `SECURITY.md` carries the detail.
- NOTE: version jumped 1.7.0 → 2.1.0 to align the package with the fleet's v2.x
  line (the README calls this v2.1); deliberate, pinned in lockstep, and the
  version test passes.

### Fixes Applied

None.

### Accepted Risks

None.

### Test Baseline

Full default suite green: 608 passing (14 short, 520 unit, 74 org), keyless and
offline. Flagship 20. Security (`/security` on the three changed source files):
0 BLOCK / 0 WARN / 1 NOTE (the pre-existing manifest-path note above).

---
*Prior review (2026-07-28, commit dcd8c91): full review of the M16 fleet-regeneration push, 0 BLOCK / 0 WARN / 2 NOTE.*

<!-- REVIEW_META: {"date":"2026-07-28","commit":"eff521e","reviewed_up_to":"eff521e04c75df5ac839bf8da48cd0ea94608ec8","base":"origin/main","tier":"full","block":0,"warn":0,"note":2} -->
