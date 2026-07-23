# Security

## Security Review — 2026-07-23 (scope: paths, M15 noise/voice/dashboard surface)

**Summary:** Reviewed the fifteen files carrying the M15 work (six derived
noise kinds, filename variety, attachment-version mismatch, per-person style
specs, per-author proxy metrics, the two-dashboard report split, the
distributional dashboard). No BLOCK, no WARN. Two NOTEs, both at the
tampered-publishable-artifact boundary the M13 and M14 reviews established:
three GENERATION-REPORT.md table cells bypass the `_cell` escape that the
rest of the table uses, and the new `.gitkeep` allowance is scoped by
filename rather than by content, so it is the one unmanifested file in the
share whose bytes no rule constrains.

### Findings

**[NOTE] `orgsmith/review/report.py:63`, `:290`, `:314` — three report table
cells bypass `_cell`.**

- Attack vector: `report` is a derived artifact that may be re-emitted for a
  frozen fixture (report.py:3-13), so a distributed org's `-metadata/` is
  input a recipient's `report` run trusts. Three values reach a markdown
  table row without `_cell`: the `state.generators` key (`:63`,
  `dict[str, Generator]` in `state.py`, no pattern on the key), the author id
  `r.author` (`:290`, from `ManifestEntry.authors`, typed `list[str]` with no
  pattern), and the joined `ReviewFinding.docs` (`:314`, `list[str]`, no
  pattern). A `|` or a newline in any of them forges or breaks a row in a
  persistent artifact a human reads later, which is exactly the threat
  `_cell`'s own docstring names (`:36-46`).
- Evidence: `_cell` is applied to `gen.model`, `gen.effort`, `t.description`,
  `f['message']`, and `f.summary`, and skipped on the three above.
  `entry.path` cells are safe for a different reason: `check_relpath` rejects
  control characters and `naming.FORBIDDEN_CHARS` contains `|`, so a manifest
  path cannot carry either. `doc_id` and `ReviewFinding.id` are
  pattern-locked, and `charter.slug` (the `distributions` table's only
  variable cell) is pattern-locked too, so no other table is affected.
- Not reachable from model output. `match_author_batch` /
  `match_outstanding` pin the generator key to a Python-generated
  `wo:<stage>:NNNN` before `state.generators` is written
  (`authoring/ingest.py:290`, `foundation/ingest.py:66`), and
  `review --ingest` rejects a `docs` entry that is not a manifest doc_id
  (`review/ingest.py`). The gap is that `load_findings` re-reads the stored
  file without that membership check and no schema pattern backstops any of
  the three. Not reachable from the network.
- Remediation: wrap all three in `_cell`, matching the rest of the row.

**[NOTE] `orgsmith/validate/rules.py:482` and `:774-777` — the `.gitkeep`
allowance is scoped by filename, not by content.**

- Attack vector: M15's empty-directory noise kind needs one placeholder per
  planned junk directory because git cannot store an empty directory, and
  render always writes zero bytes (`render/__init__.py:411`). NOISE-01
  filters the directory listing by NAME (`rules.py:482`) and MAN-01 adds the
  path to its sanctioned-extras set (`:774-777`); neither constrains the
  file's bytes. Because the file is unmanifested, no manifest-driven rule
  (FILE-01, PROV-01, FACT-01) ever opens it, and only two rules walk the
  share tree at all (`:482`, `:760`). An org redistributed with arbitrary
  bytes in `<planned-empty-dir>/.gitkeep` therefore passes the full
  validator, which is the recipient's tamper oracle.
- Evidence: the three committed placeholders in `ashcombe-advisory`
  (`Engagements/Suarez-Jones/Backup/.gitkeep`,
  `Engagements/Kirby-Taylor/Archive/.gitkeep`,
  `Engagements/Kirby-Taylor/New folder/.gitkeep`) are 0 bytes, so no
  committed fixture is affected; the gap is the missing check. The allowance
  itself cannot widen: both halves derive the directory list from
  `expected_empty_dirs`, so a `.gitkeep` outside a charter-planned directory
  is still an unmanifested-file finding.
- Impact is bounded and the severity reflects it: the file is inert data in a
  corpus of arbitrary documents, never executed, rendered, or read by any
  stage. This is a hole in the manifest-versus-share 1:1 tamper invariant,
  not a live exploit.
- Remediation: in NOISE-01, require the placeholder to be zero bytes
  (`p.stat().st_size == 0`) rather than only tolerating its name.

### Reviewed surface and scope

- **The airlock holds.** No file in scope calls a model or the network. M15's
  capability layers are all Python-derived: `derive_style_specs` draws every
  field from module constants via per-person `foundation.style` streams and
  is explicitly never model-authored, and the noise kinds derive from
  committed DocIR or from the manifest entry alone. The one
  model-output-to-filesystem path (`docir_path`) is unchanged and still
  guarded by `naming.doc_id_filename`.
- **Path containment holds on the new sinks.** The M15 noise planners build
  paths outside `_add`'s `check_relpath` call, but every one is derived from
  an already-checked source path plus a constant decoration grammar
  (`_VARIETY`, `_noise_path`) or from a code-constant `title_prefix`, and
  `load_manifest` re-checks `path` (and, since M14, `attach_path`) at every
  load, so both the render and validate sinks inherit containment. The new
  `mkdir` + `.gitkeep` write in render and the `iterdir` in NOISE-01 resolve
  through `expected_empty_dirs`, whose candidates are manifest folder paths
  plus a constant name list.
- **No prompt-injection path into the new brief text.** `_style_guidance`
  interpolates only ledger-derived style fields, all drawn from constants in
  `foundation/style.py`; `_mail_audience` interpolates external-person names,
  which enrichment cannot write (ingest fills `persona` and nothing else).
  Model-authored `persona` prose still rides forward into later authoring
  briefs, which is pre-existing and bounded: it can steer prose only, while
  facts, mentions, headers, filenames, and paths stay ledger-owned and are
  re-checked at ingest and by the validator.
- **The ACL misfile rule is ground truth, not enforcement.** `derive_acl`
  granting a misfile its destination folder's reader set is a deliberate
  ground-truth statement; nothing in scope enforces access, so there is no
  authz bypass surface.
- **No secrets, no real PII.** The in-scope files hardcode no credentials,
  and the M15 commit range adds none. The synthetic names, emails, and
  domains are the product.
- **Dependency/supply-chain and infrastructure dimensions were not covered**
  by this path-scoped run: no dependency manifests, CI configs, or
  Dockerfiles are in the file list.

### Accepted Risks

None.

---
*Prior review (2026-07-22, scope M14 email realism, commit 92d8acb): one WARN,
the transmittal `render_params["attach_path"]` reaching a `share_dir` read and
an `.eml` embed without the `check_relpath` containment every other manifest
path receives. Fixed in `6b67c12` by guarding `attach_path` in `load_manifest`
beside `entry.path`, so both the render and validate sinks inherit the check.
0 BLOCK / 1 WARN / 0 NOTE, closed.*

<!-- SECURITY_META: {"date":"2026-07-23","commit":"4da693ef421c8a6f6b7c8fc5c40534b683711e68","scope":"paths","scanned_files":["orgsmith/acl.py","orgsmith/artifacts.py","orgsmith/authoring/contexts.py","orgsmith/cli.py","orgsmith/distributions.py","orgsmith/docplan/planner.py","orgsmith/foundation/style.py","orgsmith/paths.py","orgsmith/render/__init__.py","orgsmith/render/noise.py","orgsmith/review/metrics.py","orgsmith/review/report.py","orgsmith/schemas.py","orgsmith/validate/__init__.py","orgsmith/validate/rules.py"],"block":0,"warn":0,"note":2} -->
