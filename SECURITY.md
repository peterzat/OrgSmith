# Security

## Security Review — 2026-07-16 (scope: paths)

**Summary:** M10 concurrent-batch airlock scan: the work-order plumbing
(`airlock.py`), the resume-state models (`state.py`), the status surface
(`status.py`), the outbound author work-order builder (`contexts.py`), and the
inbound deliverable validator (`ingest.py`). These five files were not in any
prior review's scope (the M9 pass explicitly excluded the ingest modules). No
BLOCKs and no WARNs. One NOTE: `ingest.py`'s single model-output-to-filesystem
sink (`docir_path`) derives a path from the model-controlled, schema-
unconstrained `DocIR.doc_id`, made safe today only by an upstream membership
check in the same function, not by a guard at the sink or a schema pattern.
**That NOTE is fixed as of the M11a turn (2026-07-16); see its Resolution
below. No re-scan was run: the fix is recorded against the finding rather
than as a new review entry.**
The airlock holds: model output is the only untrusted input in scope, and every
value it carries into a sink (doc ids, work-order ids, facts, mentions,
placeholders) is validated against the trusted work order / ledgers before any
write, and every terminal echo of model-controlled text is `strip_control`ed.

### Findings

**[NOTE — FIXED 2026-07-16] orgsmith/authoring/ingest.py:34,228 (with
orgsmith/schemas.py:590) — `docir_path` builds a filesystem path from the
model-controlled, schema-unconstrained `DocIR.doc_id`; safe today only by
non-local check ordering.**

  Attack vector: none reachable at HEAD. A malicious deliverable could set a
  `DocIR.doc_id` such as `../../evil` (the field has no schema pattern), and
  `docir_path` (ingest.py:34) maps it to a write target by stripping only `:`
  (`doc_id.replace(':', '')`), not `/` or `..`, then `run_ingest` writes
  `dump_json(doc)` to that path (ingest.py:228-229). The traversal does NOT
  reach the write because `run_ingest` first computes
  `unknown = set(got) - set(briefs)` (ingest.py:161-163) and returns 1 on any
  non-empty `problems` (ingest.py:213-221) BEFORE the write loop (line 227), so
  every written `doc.doc_id` is provably a key of `briefs` = the trusted
  work-order doc ids, which the manifest constrains to `^d:\d{4}$`
  (`ManifestEntry.doc_id`, schemas.py:517). This confirms the prior reviews'
  "the model never controls a path" for this newly-in-scope sink. It is a
  defense-in-depth NOTE, not an exploitable finding: the safety is non-local
  (it depends on the `unknown` check running, and running before the write),
  and unlike `ManifestEntry.doc_id` the `DocIR.doc_id` the sink consumes
  carries no pattern of its own.
  Evidence: ingest.py:34 `return paths.docir_dir / f"{doc_id.replace(':', '')}.json"`;
  ingest.py:228 `target = docir_path(paths, doc.doc_id)` inside the post-gate
  write loop; schemas.py:590 `doc_id: str` (no `Field(pattern=...)`) versus
  schemas.py:517 `doc_id: str = Field(pattern=r"^d:\d{4}$")`. `docir_path`'s
  other three callers (render/__init__.py:123, validate/rules.py:139,
  review/corpus.py:92) all pass a manifest `entry.doc_id`, which is already
  pattern-constrained; ingest.py:228 is the only caller passing a model-
  controlled id.
  Remediation: add `Field(pattern=r"^d:\d{4}$")` to `DocIR.doc_id` in
  schemas.py so the schema layer rejects a hostile id before any check runs
  (mirrors `ManifestEntry.doc_id`), and/or have `docir_path` take the basename
  / run `check_relpath` on the derived name so the sink is self-guarding rather
  than caller-guarded. Either is a one-line change; no urgency.

  **Resolution (2026-07-16, M11a):** both layers, since they fail
  independently. `DocIR.doc_id` now carries `Field(pattern=r"^d:\d{4}$")`
  (schemas.py), so a hostile deliverable is rejected by
  `AuthoringDeliverable.model_validate_json` at ingest.py:154 — before
  `match_author_batch` and before the `unknown` check that was previously the
  only thing standing between the id and the write loop. `docir_path`
  (ingest.py:34) additionally guards itself with `check_filename` on the
  derived basename and raises `ValueError` on a problem, so the sink is safe
  for any future caller regardless of the schema. One correction to the
  remediation as written: `check_relpath` is the **wrong** guard here — it
  splits on `/` before checking each component, so it accepts `"a/b"`;
  `check_filename` is what forbids `/` and `\`. Pinned by
  `tests/test_unit_airlock.py::test_traversal_doc_id_is_rejected_at_the_schema_and_at_the_sink`,
  which asserts rejection at both layers for `../../evil`,
  `d:0001/../../evil`, `/etc/passwd`, and `..\..\evil`, that a legitimate id
  still resolves inside `docir_dir`, and that no rejected attempt writes
  anything. Full suite green: 12 short / 342 unit / 40 org.

### Reviewed Surface

- The airlock's inbound boundary (`ingest.py`) is the only untrusted-input
  path in scope. `AuthoringDeliverable.model_validate_json` (ingest.py:144)
  schema-validates first (unknown fields rejected by `StrictModel`). Every
  model-controlled value that could reach a sink is checked against trusted
  state before it is used or written: `work_order_id` must be an outstanding
  key in `state.author_batches` (`match_author_batch`, airlock.py:126-131) and
  is used only as a dict key and a stored-order equality check, never a path;
  `doc_id`s must match the work order (`unknown`/`missing`, ingest.py:161-166);
  placeholders, non-body facts, literal fact values, and mentions are all
  validated against the ledger fact index (ingest.py:65-72, 101-136, 182-211);
  and the write loop runs only after `if problems: return 1`. The stored
  `deliverable.generator` (ingest.py:223-224) is recorded, never trusted as an
  oracle (per its schema docstring); no in-scope code uses it as a gate.
- Terminal-injection from model-controlled strings is defended. Both echoes of
  deliverable text run through `strip_control`: the schema-error path keeps
  `\n\t` (ingest.py:150, harmless — ESC/CR are category Cc and become U+FFFD),
  and the per-problem path uses `keep=''` so an embedded newline cannot forge a
  second output line (ingest.py:220). The JSON status branch uses `json.dumps`
  (status.py:51); its human branch prints only Python-derived ids/paths
  (`wo:author:NNNN`, serial filenames), never model text.
- `contexts.py` builds OUTBOUND work orders only and consumes no deliverable.
  Its inputs are the charter, foundation, engagements, and manifest — all pure-
  stage ledgers, trusted. It withholds ledger values from briefs by design
  (`_brief_summary`, `FactBrief` carries a hint but never the rendered value),
  which is the airlock's fact-leak discipline, not a gap. The one model-to-
  model flow (a prior pass's `persona` into the next brief, contexts.py:232) is
  inside the operator's own trust domain and gates nothing; consistent with
  prior reviews, not a concrete finding.
- `airlock.py`/`state.py`/`status.py` construct paths only from Python-derived
  serial filenames (`emit_work_order`, `emit_author_batch`) or from strings
  stored in `state.json` (`outstanding[stage]`, `BatchRef.workorder`). Those
  stored strings are never derived from model output — they are set by the emit
  functions to computed basenames — so the `paths.workorders_dir / name` joins
  (airlock.py:29,132) are not a model-reachable traversal. `state.json` itself
  is Python-written and committed; tampering it is a local-filesystem
  compromise, outside the airlock threat model (model deliverables are the sole
  untrusted input).
- Secrets / dangerous sinks / PII: pattern grep over all five files is clean
  (no secret/token/key material); there is no `subprocess`/`eval`/`exec`/
  `os.system`/`pickle`/`open`/`shell=True` anywhere in scope; no real names,
  emails, or phone numbers are hardcoded (all such data flows through ledgers
  at runtime). `git log` over the five modules shows only M9/M10 feature
  commits, no secret-shaped diffs. No credential-handling code is present, so
  no deep `git log -p` secret sweep was warranted.
- Out of security scope but noted for the reader: `emit_author_batch`'s
  serial-numbering (airlock.py:108) is safe only under sequential emission (the
  orchestrator is the single serial writer, per the M10 design); a concurrent
  double-emit would be a local correctness race, not an externally-reachable
  vulnerability, so it is not a security finding.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-16, scope paths, commit c013c06): M9 document-supply
scan of the genre registry, registry-driven planner, date-scoped work orders,
and the reworked PDF renderer; 0 BLOCK / 0 WARN / 1 NOTE (the `render/pdf.py`
letterhead interpolated unescaped under `autoescape=False`, recipe-author-
controlled with egress blocked, carried unchanged from every prior review).
That NOTE's file is outside the current path scope and was not re-verified.*

<!-- SECURITY_META: {"date":"2026-07-16","commit":"7cd134b78e678943b2f865e95c08b6996aea9401","scope":"paths","scanned_files":["orgsmith/airlock.py","orgsmith/authoring/contexts.py","orgsmith/authoring/ingest.py","orgsmith/state.py","orgsmith/status.py"],"block":0,"warn":0,"note":1} -->
