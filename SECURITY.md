# Security

## Security Review — 2026-07-28 (scope: paths)

**Summary:** Reviewed the .eml renderer (`orgsmith/render/eml.py`), the v0
validator catalog (`orgsmith/validate/rules.py`), and the checksum-manifest
generator (`tools/checksums.py`). No BLOCK, no WARN. One NOTE: the validator
resolves the unconstrained `ManifestEntry.path` string against the share tree,
a path-traversal gap with no reachable harmful sink under the airlock. All
three files are offline, keyless, and network-free.

### Findings

- **[NOTE] rules.py (many sites, e.g. :66, :705, :726, :792) — tampered
  manifest path resolved against the filesystem without a relative-path
  constraint.** `ManifestEntry.path` is an unconstrained `str` (schemas.py:781,
  a comment says "share-relative" but nothing enforces it), and every rule
  resolves it with `ctx.paths.share_dir / e.path`. Because `pathlib`'s `/`
  lets an absolute right-hand operand replace the base and `..` segments
  escape, a `manifest.jsonl` line with `path: "/etc/passwd"` or a `../` prefix
  makes the validators stat and open a file outside the share tree.
  - Attack vector: an actor who can edit committed `-metadata/docplan/manifest.jsonl`
    (the same tamper capability the validator exists to detect) plants a
    traversal or absolute path; the next `validate` run reads that file.
  - Why it is only a NOTE (no reachable harmful sink): (1) no rule uses
    `e.path` for a write; (2) no finding echoes the read file's *contents* —
    findings carry only ledger-derived expected surfaces (`fact_01`
    rules.py:714, `ment_01` :830) plus parser error strings, so an out-of-tree
    read is not exfiltrated; (3) the airlock means no network channel to
    exfiltrate to; (4) `man_01` (rules.py:807-810) flags any planned path that
    is not a share-relative on-disk file as "manifest doc missing from share",
    so the traversal fails validation loudly rather than passing silently.
  - Remediation: constrain the field at the boundary — a `Field(pattern=...)`
    on `ManifestEntry.path` (or a check in `load_manifest`, artifacts.py:94)
    that rejects a leading `/` and any `..` segment — so a traversal path is
    refused at load time instead of being resolved against the filesystem.

### Reviewed surface and scope

- **eml.py header injection has no dangerous sink.** Header values flow from
  the ledgers into `EmailMessage` under `policy.SMTP` (`expected_headers`
  eml.py:77-138, `render_eml` :199-205). Even a tampered `title` (Subject),
  `people[...]["email"]` (From/To), or `domain` (Message-ID) carrying control
  characters cannot escalate: these .eml files are synthetic fixtures written
  to disk, never handed to an MTA or any network transport (airlock), and
  EML-01 (rules.py:1176) recomputes every header from the ledger via the same
  helper, so a tampered header that diverges from the ledger is a validation
  failure. No SMTP-injection reachability.
- **Model-authored prose reaches no injection sink in scope.** The .eml body
  is set through `msg.set_content` (eml.py:205), which encodes the part and
  cannot fold authored text up into the header block; `strip_leading_header_block`
  uses a simple anchored regex (eml.py:27-29) with no catastrophic
  backtracking. In rules.py, extracted document text is only string-compared
  against expected surfaces (`surface_in_text` uses `re.escape`, schemas.py:885);
  there is no `eval`, shell, SQL, or template sink.
- **Validator findings are printed, not embedded, within scope.** `run_validate`
  prints findings as text or JSON (validate/__init__.py:64-72). The markdown
  embedding of finding strings into `GENERATION-REPORT.md` happens in
  `review/report.py` (out of scope here and already a standing NOTE from prior
  reviews about `_cell` escaping), not in the three reviewed files.
- **checksums.py is injection-free.** `subprocess.run` is called with a fixed
  argument list (no `shell=True`) over a hardcoded `ORGS` allowlist
  (checksums.py:19-31); it reads only `git ls-files`-tracked paths and writes a
  table of hardcoded slugs, integer counts, and hex digests (checksums.py:64-67),
  none of which are attacker-controlled free text. No command or markdown
  injection.
- **No secrets, no real PII.** None of the three files call a model or the
  network. Content is clean (the one secret-pattern grep hit was the word
  "tokens" in an eml.py docstring), git history is structural, and the only
  proper nouns are the synthetic org slugs and `PRODUCT_NAME`, which are the
  product.
- **Dimensions considered and not reported.** Third-party parsers in rules.py
  (python-docx, openpyxl, python-pptx, pypdf, pikepdf, xlrd, olefile) parse
  committed fixtures; an XXE or zip-bomb payload would require the same
  committed-fixture write access as the tamper model, the airlock blocks any
  external-DTD/network exfiltration, and no finding echoes parsed content — so
  the residual impact is below the reporting bar and parser-config certainty
  is under the 80% threshold. Dependency-manifest and infrastructure
  dimensions were out of scope for this path-scoped run (no manifests, CI
  configs, or Dockerfiles in the file list).

### Accepted Risks

None.

---
*Prior review (2026-07-28, scope paths, commit f3fbef62): reviewed
`orgsmith/distributions.py`, the M15 distributional dashboard; 0 BLOCK / 0 WARN
/ 0 NOTE. Markdown injection into the derived dashboard was unreachable — the
only variable cell is the pattern-locked `charter.slug`, every other cell is
numeric, and authored prose reaches the table only through an integer word
count.*

<!-- SECURITY_META: {"date":"2026-07-28","commit":"eff521e04c75df5ac839bf8da48cd0ea94608ec8","scope":"paths","scanned_files":["orgsmith/render/eml.py","orgsmith/validate/rules.py","tools/checksums.py"],"block":0,"warn":0,"note":1} -->
