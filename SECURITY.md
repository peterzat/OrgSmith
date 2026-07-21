# Security

## Security Review — 2026-07-21 (scope: M13 path containment and letterhead escaping)

**Summary:** M13 closes the two notes carried open into this milestone. Both
were non-exploitable in any current flow but held only by the good behavior of
whoever wrote the input, at a data-versus-code boundary that exists on paper
(orgs are publishable artifacts). Each is now fixed rather than accepted, in
depth: at the schema, at the sink, and at the render context. No new BLOCK,
WARN, or NOTE.

### Findings closed

**[CLOSED] `state.json`-derived work-order names reached a file read outside
`workorders_dir`** (was NOTE, 2026-07-17c, `orgsmith/airlock.py:79`). Neither
`OrgState.outstanding` values nor `BatchRef.workorder` carried a pattern, so a
tampered `state.json` (a value the module joins under `workorders_dir`, where
pathlib discards the base for an absolute operand and `../` traverses out)
survived validation as a free string and reached `outstanding_work_order` /
`match_author_batch`. Closed with the same two-layer shape `DocIR.doc_id`
received:

- Schema (commit 1adbb5a): both fields are now constrained to
  `^[A-Za-z0-9_-]+\.json$` (`orgsmith/state.py`, `WorkOrderName`), which admits
  every name the generator writes and rejects separators, `..`, absolute paths,
  and control characters at load. No `orgsmith/state@1` bump; all eight
  committed states load, validate, and round-trip byte-identically
  (`tests/test_unit_paths.py`).
- Sink (commit 1adbb5a): `naming.contained_join` guards the join, so a value
  that reaches the sink anyway (validation bypassed, or a future pattern
  relaxation) is refused rather than resolving outside `workorders_dir`.
- Terminal (commit 1adbb5a): the state-derived path interpolations in
  `airlock.py`'s messages now pass through `strip_control` or `repr`, so a
  control character in a tampered name cannot rewrite terminal output. Proven by
  a test driving an ESC-bearing name to a print site.

Supporting hardening (commit 59a17c8): the three doc_id-to-filename sinks
(`authoring/ingest.py`, `review/corpus.py`, `render/scan.py`) now share one
guarded helper, `naming.doc_id_filename`, so the containment is uniform rather
than present at the one sink that remembered to check.

**[CLOSED] Charter-tainted letterhead reached a CSS and an HTML context under
`autoescape=False`** (was the carried-forward M9 NOTE, `orgsmith/render/pdf.py`).
The PDF template renders with `autoescape=False` because `body` is pre-built,
already-escaped HTML, but `letterhead0` and `letterhead_rest` (the charter name
and domain, tainted via `render/styles.py`) reached a CSS `content:` string and
two HTML `div` contexts unescaped. Closed (commit 66b87b9) by escaping per
context in Python before the template runs: `_css_string` for the `@top-left`
content (backslash-escapes the string delimiter and hex-escapes control
characters) and `html.escape` for the divs. Both are the identity on all eight
committed charters (plain ASCII), so committed letterhead output is unchanged; a
charter name carrying `"`, `<`, or `&` now renders a well-formed PDF showing the
literal name (`tests/test_unit_paths.py`).

### Reviewed surface and scope

- **The airlock still cannot reach a model or the network.** M13 adds no
  third-party import to `airlock.py`; it imports `naming` (stdlib-only) for the
  join guard. Python still never calls a model, and no LLM grades an LLM in any
  automated tier.
- **The fix is a validator tightening on `orgsmith/state@1`, not a schema id
  bump.** It is safe only because the pattern admits every committed value, which
  the round-trip test enforces over all eight orgs.
- **CI stays pure Python where it must.** The letterhead identity check is pure
  Python (no renderer); the hostile-charter render test uses WeasyPrint, which is
  present in CI (only LibreOffice is absent).
- **`bin/test` is green on all tiers** (short, unit, org, flagship), keyless and
  offline, with zero fixture movement (the byte pin holds).

### Accepted Risks

None.

---
*Prior review (2026-07-17c, scope paths, commit f538f0d): read `airlock.py` and
its unit tier as a whole against the module's own invariants; 0 BLOCK / 0 WARN /
1 NOTE (the state-path containment gap, closed above), and carried forward the
M9 `render/pdf.py` letterhead NOTE (also closed above). The concurrency guard
(`touch(exist_ok=False)`) and the `isascii() and isdigit()` serial gate were
read as correct and are unchanged.*

<!-- SECURITY_META: {"date":"2026-07-21","commit":"66b87b9","scope":"m13-path-containment-and-letterhead","scanned_files":["orgsmith/state.py","orgsmith/airlock.py","orgsmith/naming.py","orgsmith/render/pdf.py","orgsmith/render/styles.py","orgsmith/review/corpus.py","orgsmith/render/scan.py","orgsmith/authoring/ingest.py"],"block":0,"warn":0,"note":0} -->
