# Security

## Security Review — 2026-07-14 (scope: changes-only)

**Summary:** Review of the 12 commits since the last audit
(`b94d7f5..9d60f44`, the M2 milestone; working tree clean, so the pending
branch delta is the scope). No new vulnerabilities. Both hardening items
from the prior audit are verified remediated: manifest paths are now
re-validated on every load, and the WeasyPrint fetcher refuses all
non-`data:` URLs (tested, including `file://`). CI actions are SHA-pinned.
One residual NOTE carries forward.

### Findings

**[NOTE] orgsmith/render/pdf.py:37,63 — letterhead lines still rendered
unescaped (residual from prior review; no current attack vector)**

  Attack vector: None concrete. The letterhead is `charter.name` and
  `www.{charter.domain}` (styles.py:43), interpolated raw into the HTML
  template under `Environment(autoescape=False)` (pdf.py:72). The only
  party who controls the charter is the recipe author, who already authors
  the entire document set; with the new `no_remote_fetcher` blocking
  `http:`, `https:`, and `file:` (pdf.py:18-26, tested in
  tests/test_unit_hardening.py), injected markup can no longer egress or
  read local files, so injection gains an attacker nothing beyond content
  they already control. Retained as informational hardening only.
  Evidence: pdf.py:37 (`content: "{{ letterhead0 }}"` inside a CSS
  string), pdf.py:63 (raw `{{ letterhead0 }}` in body), pdf.py:72
  (`autoescape=False`); all block content is escaped in `_blocks_to_html`.
  Remediation: `html.escape()` the letterhead lines (and CSS-escape the
  `@top-left` string) when building the template context. One-line change,
  no urgency.

### Resolved Since Prior Review

- **[WARN 2026-07-14] manifest paths trusted at consumption** — Fixed.
  `check_relpath` now rejects absolute paths, empty components, and `..`
  (orgsmith/naming.py:42-46), and `load_manifest` re-runs it on every
  entry at load, raising on failure (orgsmith/artifacts.py:60-66). All
  consumers that join `entry.path` to the filesystem (render, validate,
  assemble, emit-evals) load through this chokepoint. Verified by
  executing the check against `/etc/x.docx`, `../../x.docx`, `a/../x.docx`,
  `//srv/share/x.docx`, and `a/./x.docx`: all rejected; normal paths pass.
- **[NOTE 2026-07-14] WeasyPrint default fetcher could egress** — Fixed.
  `no_remote_fetcher` serves only `data:` URIs and raises before any
  socket exists (orgsmith/render/pdf.py:18-26); covered by unit tests for
  `http:`, `https:`, `file:`, and `ftp:` plus an end-to-end render with
  blocked resources (tests/test_unit_hardening.py). The letterhead-escape
  half of that NOTE remains open as the residual NOTE above.
- **[NOTE 2026-07-14] CI actions pinned to mutable tags** — Fixed.
  `actions/checkout` and `actions/setup-python` are pinned to full commit
  SHAs (.github/workflows/ci.yml:11-12). The SHA-to-version comments were
  not verifiable offline, but pinning to immutable objects is the property
  sought.

### Reviewed Surface (this delta)

- New external-input surface `score --answers <file>` / `--evals-dir`:
  answers parsed with strict pydantic models, malformed input exits 2 with
  a message; file contents are compared as strings only and never joined
  to the filesystem (orgsmith/evals/score.py). No injection path.
- `emit-evals` writes only under the org's own `evals/` dir derived from
  the CLI slug; charter slugs are pattern-constrained
  (`^[a-z0-9][a-z0-9-]*$`, schemas.py:120). No path escape.
- New fixture `companies/torchlake-engineering*` and its workorder/eval
  records: all identities synthetic (Faker names, 555-01xx fictional
  phones, invented domains e.g. `torchlakeeng.com`, same convention as the
  audited dev-mini fixture); docx/xlsx/pdf metadata carries synthetic
  creators only, no local usernames or paths (verified by unzipping core
  properties and scanning PDF objects).
- Secret scan: cumulative diff and per-commit `git log -p` over the range
  matched zero credential patterns. The one `file:///etc/passwd` string is
  a hardening-test asset.
- Mention enforcement at ingest tightens validation of model output
  (placeholder-resolved matching, orgsmith/authoring/ingest.py); no new
  trust placed in model output.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-14, scope full, commit b94d7f5): first full audit
of the package, skills, tests, and config; no secrets, injection, or auth
issues; one WARN (manifest paths trusted at consumption, arbitrary file
write if a tampered third-party org is rendered) and two NOTEs (WeasyPrint
default fetcher enabled, CI actions on mutable tags), all three remediated
in the delta reviewed above.*

<!-- SECURITY_META: {"date":"2026-07-14","commit":"9d60f44273b769fd8b5721701f579980128b6307","scope":"changes-only","block":0,"warn":0,"note":1} -->
