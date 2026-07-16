# Security

## Security Review — 2026-07-16 (scope: paths)

**Summary:** M11a scan of the turn's changed surface: the ACL overlay
(`acl.py`, employment-scoped grants), the hardened inbound airlock
(`ingest.py` + `schemas.py`, closing the M10 NOTE), the guarded charter write
(`charter.py`), roster growth (`foundation/scaffold.py`), and the five test
modules pinning them. No BLOCK, no WARN, no NOTE. **The M10 NOTE is closed and
independently verified this pass** (the M11a turn recorded the fix without a
re-scan; this is that re-scan). The airlock's one model-output-to-filesystem
sink is now guarded at two layers that fail independently, confirmed by
execution rather than by reading.

### Findings

No security issues identified in the reviewed scope.

### Reviewed Surface

- **The M10 NOTE is closed, verified by execution.** `DocIR.doc_id` now
  carries `Field(pattern=r"^d:\d{4}$")` (schemas.py:616) and `docir_path`
  guards its own derived basename with `check_filename`, raising `ValueError`
  (ingest.py:34-45). Both layers were exercised directly against `../../evil`,
  `d:0001/../../evil`, `/etc/passwd`, `..\..\evil`, embedded NUL, and the
  anchor-bypass payloads `d:0001\n` / `d:0001\nd:0002`: **every payload is
  rejected by each layer independently**, and a legitimate id still resolves
  inside `docir_dir`. Two details worth recording because they are load-bearing
  and non-obvious. First, pydantic 2.13.4 resolves `regex_engine` to the
  default `rust-regex`, whose `$` matches end-of-haystack only, so the classic
  `"d:0001\n"` trailing-newline bypass (which Python's `re` would accept, since
  its `$` also matches before a final newline) is rejected at the schema layer;
  the repo does not depend on that alone, because `check_filename`'s
  control-character rule rejects the same payload at the sink. Second, the
  fix's own comment is right that `check_relpath` would have been the wrong
  guard: it splits on `/` before checking components, so it accepts `"a/b"`.
  `check_filename` forbids `/` and `\`, which is what this sink needs. The
  safety is now local to each layer rather than a consequence of `run_ingest`'s
  check ordering, which is exactly what the NOTE asked for. Pinned by
  `tests/test_unit_airlock.py::test_traversal_doc_id_is_rejected_at_the_schema_and_at_the_sink`
  (module green, 8 passed).
- **`ingest.py` remains the only untrusted-input path in scope, and it
  holds.** Schema validation runs first (`StrictModel`, extra fields
  rejected); `work_order_id` is a dict lookup into `state.author_batches`
  (`match_author_batch`, airlock.py:121-140), never a path component; doc ids,
  placeholders, non-body facts, literal fact values, and mentions are all
  checked against the trusted work order and ledger fact index before the
  `if problems: return 1` gate at line 223, and the write loop runs only after
  it. `_PLACEHOLDER` (`\{\{fact:([^}]*)\}\}`) is a non-nesting star with no
  backtracking blowup, and `surface_in_text` calls `re.escape` on a
  work-order-derived surface.
- **Model-controlled text reaching a terminal or a persisted artifact is
  neutralized at every echo.** The rejection printer uses
  `strip_control(p, keep='')` (ingest.py:230) so a smuggled newline cannot
  forge a second line; the schema-error path strip_controls the
  `ValidationError` (ingest.py:160). `docir_path`'s `ValueError` interpolates
  the hostile id with `!r`, and `repr()` escapes control characters, so even
  an uncaught raise cannot drive the terminal. The one place model output
  persists into a human-read artifact, `deliverable.generator` ->
  `state.generators` (ingest.py:233-234) -> `review/report.py`, passes through
  `_cell`, which strips control characters and escapes both newlines and pipes
  so a forged markdown row is not expressible. Nothing gates on `generator`
  (grep-confirmed: `report.py` renders it, no validator rule reads it),
  consistent with its schema docstring calling it a record and not an oracle.
- **`acl.py` takes no untrusted input, so its rewrite is not an auth
  surface.** It is derived ground truth for grading someone else's system, not
  an enforcement point: no request, session, or principal from outside reaches
  it. Its four inputs are the charter (recipe, operator trust domain) and the
  foundation / engagements / manifest ledgers (pure-stage Python). The
  foundation is the only one the model touches at all, and enrichment merges
  `persona` only, which is enforced structurally rather than by convention
  (`PersonaEnrichment` is a `StrictModel` carrying two fields, so a payload
  setting `reports_to` is rejected at parse; pinned by
  `test_unit_airlock.py::test_enrichment_rejections`). `derive_acl` reads
  `employment.end`, `id`, and `reports_to`, none of them model-writable. The
  new employment scoping is a product-correctness decision, not a security
  boundary, and the ACL-02 invariant it leans on is sound by construction: the
  CEO-equivalent is `reports_to is None` and churn eligibility requires
  `reports_to is not None`, so the CEO can never depart and every document
  keeps a reader under all three posture branches.
- **`charter.py` parses recipes with `yaml.safe_load` (line 26),** not
  `yaml.load`, so a recipe cannot construct arbitrary objects. `Charter.slug`
  is pattern-constrained (`^[a-z0-9][a-z0-9-]*$`) and cross-checked against the
  recipe directory, so no slug reaches a path as a traversal. The new
  write-suppression guard compares rendered bytes and changes no trust
  boundary. Recipes are operator-authored and in-repo; consistent with every
  prior review, that is the established trust domain.
- **`scaffold.py` composes ids and emails through `_slugify`**
  (NFKD -> ascii -> `[^a-z0-9]+` collapse), and `Person.id` is additionally
  pattern-bound. Nothing it emits reaches a path, a shell, or a query. No
  network and no model call, per the airlock.
- **Secrets / dangerous sinks / PII: clean.** No `subprocess`, `eval`, `exec`,
  `os.system`, `pickle`, `open`, or `shell=True` anywhere in scope. Content
  grep for secret material is clean, and a `git log -p` sweep over the full
  history of every scoped module returns no secret-shaped line ever committed
  (the only hit is the `/etc/passwd` traversal payload in the test above). No
  credential-handling code exists in scope. No PII: the only literal emails are
  `example.com` (RFC 2606 reserved) in `test_unit_history.py:44,866`, phone
  numbers are drawn from the reserved fictional 555-01xx block
  (scaffold.py:36,158), and `_NICKNAMES` / `_EXT_TITLES` are generic word
  tables identifying nobody. "Goldman Sachs" (`test_unit_history.py:648`) is a
  firm name used as the negative fixture for the real-firm name screen, which
  is the test's purpose. File modes are 664.
- **Not re-verified, and named rather than implied:** the M9 `render/pdf.py`
  letterhead NOTE (recipe-author-controlled interpolation under
  `autoescape=False`) is against unchanged code outside this path scope and
  carries forward open. Dependency manifests are outside the scope too; noted
  only because `charter.py` consumes PyYAML, which is pinned at 6.0.3 and used
  safely.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-16, scope paths, commit 7cd134b): M10 concurrent-batch
airlock scan of `airlock.py`, `state.py`, `status.py`, `contexts.py`, and
`ingest.py`; 0 BLOCK / 0 WARN / 1 NOTE. The NOTE was a defense-in-depth
observation that `docir_path` derived a filesystem path from the
model-controlled, schema-unconstrained `DocIR.doc_id`, exploitable only if
`run_ingest`'s upstream work-order membership check were ever reordered after
the write loop. The M11a turn fixed it at both the schema and the sink and
recorded the resolution against the finding without re-scanning; this review
is that re-scan and confirms the closure by execution. It also carried forward
the M9 `render/pdf.py` letterhead NOTE, still open against unchanged
out-of-scope code.*

<!-- SECURITY_META: {"date":"2026-07-16","commit":"38d79aa2a0ebe2a049aca4849190980da359925d","scope":"paths","scanned_files":["orgsmith/acl.py","orgsmith/authoring/ingest.py","orgsmith/charter.py","orgsmith/foundation/scaffold.py","orgsmith/schemas.py","tests/test_org_regen.py","tests/test_unit_acl.py","tests/test_unit_airlock.py","tests/test_unit_history.py","tests/test_unit_resume.py"],"block":0,"warn":0,"note":0} -->
