# Security

## Security Review — 2026-07-17c (scope: paths)

**Summary:** Focused re-read of the airlock module and its unit tier
(`orgsmith/airlock.py`, `tests/test_unit_airlock.py`), the two files that own
the model boundary. Both were in the previous scan's file list, but that scan
read them as part of a 29-file sweep; this one reads the module as a whole,
against its own stated invariants. No BLOCK, no WARN, one NOTE: the module
asserts that work orders live under `-metadata/workorders/` but does not
enforce it on the read path, so a name out of a tampered `state.json` reaches
a file read outside that directory. Not exploitable in any current flow; filed
because it is the same shape as the `docir_path` NOTE the project chose to
close in July.

### Findings

**[NOTE] orgsmith/airlock.py:79 — `state.json`-derived names reach a file read
outside `workorders_dir`; the module's stated containment invariant is not
enforced at the sink.**

- **Attack vector:** Requires an attacker-supplied org tree (data, not code).
  `state.json` is committed with every org (7 under `companies/`) and the repo
  publishes publicly, so an org that arrives by fork, PR, or hand-off carries
  its own `state.outstanding` / `author_batches[].workorder` values. Neither
  field carries a pattern (`state.py:48`, `state.py:69`), so both survive
  validation as free strings. `outstanding_work_order` then builds
  `paths.workorders_dir / name` (`airlock.py:79`), and pathlib's `/` **discards
  the base when the right operand is absolute**, so `"/etc/passwd"` resolves to
  itself rather than under `workorders_dir`; `../` traversal reaches out the
  same way. `emit_work_order` hands the escaped path back to its caller
  (`airlock.py:97-100`), and `/forge` passes it to `forge-author`, whose first
  instruction is to read the work-order file it was given
  (`.claude/skills/forge-author/SKILL.md:16`). The read lands in model context.
  `match_outstanding` reaches the same sink and would surface file content
  through an uncaught `ValidationError`.
- **Evidence:** Confirmed by execution, not by reading. A `state.json` with
  `outstanding: {"foundation": "<abs path outside the org>"}` loads clean and
  `outstanding_work_order` returns that exact path, `startswith(workorders_dir)`
  False, contents readable by the caller. Secondary, same precondition: the
  un-repr'd interpolations at `airlock.py:84` (`{path}`), `:99` (`{existing}`)
  and `:197` (`{ref.workorder}`) would pass control characters from a tampered
  `state.json` straight to the terminal. Every *deliverable*-controlled
  interpolation in the module is already `!r`-quoted, which fully escapes
  ESC and newline (verified). The gap is state-derived strings only.
- **Why NOTE and not WARN:** an attacker who can write `state.json` in your
  tree can usually write `orgsmith/*.py` too, and win more directly. The gap
  only matters at a data-vs-code boundary that exists on paper (orgs are
  publishable artifacts) but that no real flow crosses today: operators
  generate their own orgs, downstream consumers use the fixtures for RAG rather
  than regeneration, and CI never reaches the airlock (only the model
  touchpoints call it: `foundation/contexts.py`, `foundation/ingest.py`,
  `authoring/ingest.py`). This is the *same* non-local safety the 2026-07-16
  `docir_path` NOTE described: not exploitable, but holding only by the good
  behavior of whoever wrote the state file.
- **Remediation:** Guard the sink the way `docir_path` now guards itself
  (`authoring/ingest.py:34-45`): resolve the candidate and require it under
  `workorders_dir`, or run the name through `check_filename` (which forbids
  `/`, `\`, and control characters) before joining. A pattern on
  `OrgState.outstanding` values and `BatchRef.workorder` would close it at the
  schema as well, matching the two-layer fix `DocIR.doc_id` received and the
  test at `test_unit_airlock.py:198`.

### Reviewed Surface

- **The airlock still cannot reach a model or the network.** `airlock.py`
  imports only `pathlib`, `typing`, and three local modules; neither file
  contains `subprocess`, `eval`, `exec`, `pickle`, `yaml.load`, `os.system`, a
  socket, or an HTTP client.
- **Nothing secret-shaped or PII-shaped has ever been in either file.** Swept
  `git log -p --follow --all` over both (4 commits on `airlock.py`), across all
  added lines rather than the net diff: zero hits for private-key blocks, JWTs,
  AWS/GitHub/Slack/Google/Anthropic key shapes, bearer tokens, quoted
  `api_key|password|secret|token=` assignments, connection strings, email
  addresses, IPs, and `/home/`, `/Users/` paths.
- **The concurrency guard is real, and it is the right primitive.**
  `_claim_work_order_path` claims by `touch(exist_ok=False)` (`O_CREAT|O_EXCL`),
  not check-then-write, so the kernel decides the race and the loser exits
  rather than destroying an order; `O_EXCL` also refuses to follow a planted
  symlink. `_next_serial` takes the max, not the count, and gates on
  `isascii() and isdigit()`, which is correct rather than paranoid:
  `"²".isdigit()` is True while `int("²")` raises, and `"٣"` parses as 3.
- **One candidate DoS was chased and disproved rather than filed.** `int(tail)`
  (`airlock.py:44`) is uncaught, and Python caps integer parsing at 4300 digits
  (CVE-2020-10735 backport, live on this 3.10.12), so a long enough serial would
  raise `ValueError` and break the docstring's promise that strays are "ignored
  rather than fatal". It is unreachable: the filesystem refuses any filename
  past 255 bytes, verified by attempting the write, so a 4301-digit serial
  cannot exist on disk. No finding.
- **Work orders carry no ledger values, and the model is not trusted as an
  oracle.** `test_unit_airlock.py:149-151` asserts no money/date surface form
  appears anywhere in a serialized order, and `match_outstanding` /
  `match_author_batch` check the deliverable's `work_order_id` against the
  order that is actually outstanding rather than believing it.
- **The tests write only under `tmp_path`.** `build_pure_stages`
  (`conftest.py:17-29`) roots every path at the fixture's `tmp_path` and touches
  the repo only to `copytree` the recipe out of it. No archive extraction, so
  no zip-slip surface.
- **Not re-verified, and named rather than implied:** the M9 `render/pdf.py`
  letterhead NOTE (recipe-author-controlled interpolation under
  `autoescape=False`) is against unchanged code outside this path scope and
  **carries forward open**. Dimensions with no surface in these two files:
  authentication/authorization, dependency and supply chain (no manifest in
  scope; `airlock.py` adds no third-party import), and infrastructure (no config
  in scope). That is a scope statement, not a clean bill. Sanity check:
  `tests/test_unit_airlock.py` passes 13/13.

### Accepted Risks

None.

---
*Prior review (2026-07-17b, scope paths, commit f897c63): swept the 29 files of
the pre-M12 turn (`62a5665..HEAD`, 11 commits) per-commit rather than against
the net diff; 0 BLOCK / 0 WARN / 0 NOTE. It cleared the new `emit-schemas` verb
(output filenames derive from `Literal` schema ids, not from input), read the
one `https://` in `schemas_export.py` as the JSON Schema dialect identifier
rather than a fetch, and read the 19 emitted schemas plus the verbatim external
critique as outbound disclosure into a public repo, finding only facts
`schemas.py` already publishes. It carried forward the M9 `render/pdf.py`
letterhead NOTE, which remains open.*

<!-- SECURITY_META: {"date":"2026-07-17","commit":"f538f0dc29a6eb2ae0929158b00ce9b614f36c62","scope":"paths","scanned_files":["orgsmith/airlock.py","tests/test_unit_airlock.py"],"block":0,"warn":0,"note":1} -->
