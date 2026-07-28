# Security

## Security Review — 2026-07-28 (scope: paths)

**Summary:** Reviewed `orgsmith/distributions.py`, the M15 distributional
dashboard that reads the committed fleet and writes `docs/DISTRIBUTIONS.md`.
No BLOCK, no WARN, no NOTE. The one variable string that reaches the
human-read artifact is `charter.slug`, pattern-locked at the schema; every
other table cell is an integer or a float with a numeric format spec, and
authored prose is reduced to a word count before it can reach the output.

### Findings

No security issues identified.

### Reviewed surface and scope

- **Markdown injection into the derived dashboard is not reachable.** The
  threat this file inherits from prior reviews is a tampered `-metadata/`
  forging or breaking a row in a derived artifact a human reads later
  (`DISTRIBUTIONS.md` is re-emittable for a distributed org, distributions.py:1-13).
  Every value `_row` and `_delta` interpolate is numeric except `d['slug']`,
  which is `charter.slug`, pattern-locked to `^[a-z0-9][a-z0-9-]*$`
  (schemas.py:430): no `|`, no newline. The `_wave_before_after` per-row slug
  is a `WAVE_BASELINE_M15` constant key and the aggregate slug is the constant
  `**fleet**`, so neither is attacker-controlled. `ManifestEntry` string
  fields (`format`, `authoring`, `engagement`, `doc_id`, `render_params`) are
  used only for counting and as internal dict keys, never printed
  (distributions.py:62-73).
- **Authored prose never reaches the table.** DocIR is read only through
  `word_count`, which returns an integer (distributions.py:66,
  corpus.py:48-68), so a `|` or newline in model-authored text cannot escape
  into the output. This keeps the airlock's "prose is replaceable, facts are
  load-bearing" boundary intact on the reporting side.
- **No path escape in `committed_slugs`.** The slug is a `glob("*-metadata")`
  basename, a single path component with no `/`, and every load resolves under
  `companies/<slug>-metadata/` via `OrgPaths` (distributions.py:42-51,
  paths.py:40-41). A pathological `..-metadata` directory yields slug `..`,
  but `meta_dir` is then the literal `companies/..-metadata` (not parent
  traversal, since `..-metadata` is not `..`), so reads stay inside the
  planted directory. No arbitrary-file read out of the tree.
- **Airlock intact; no secrets, no real PII.** The file calls no model and no
  network. It hardcodes no credentials (content clean, git history is two
  structural commits), and the only proper nouns are the synthetic org slugs
  in `WAVE_BASELINE_M15`, which are the product. The single `print` emits an
  org count and the output path, no sensitive content (distributions.py:228).
- **Dependency/supply-chain and infrastructure dimensions** were not in scope
  for this single-file run: no manifests, CI configs, or Dockerfiles are in
  the file list. The file itself imports only `pathlib` and internal modules.

### Accepted Risks

None.

---
*Prior review (2026-07-23, scope M15 paths, commit 4da693ef): reviewed fifteen
M15 files including this one and found no BLOCK/WARN; two NOTEs, both at the
tampered-publishable-artifact boundary and both in other files. Three
`report.py` table cells bypass the `_cell` escape (still open per the NOTE
convention), and the `.gitkeep` allowance was scoped by filename rather than
content (since fixed in codereview 014c138: NOISE-01 now asserts the
placeholder is zero bytes).*

<!-- SECURITY_META: {"date":"2026-07-28","commit":"f3fbef627bbe0cbc99ce6ca10bfc8f232cc6dd00","scope":"paths","scanned_files":["orgsmith/distributions.py"],"block":0,"warn":0,"note":0} -->
