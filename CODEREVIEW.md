# CODEREVIEW

## Review — 2026-07-22 (commit: 92d8acb)

**Summary:** M14 email realism, `origin/main..HEAD`, 12 commits. Code surface
~15 `orgsmith/` files plus tests, recipe, docs; the bulk of the 268-file diff
is the generated-and-validated `ashcombe-advisory` pilot org (data, not
hand-authored code). Reviewed against `origin/main`. New: the optional
`doc_culture.mail` block (threaded engagement mail, quoted history,
promotion-aware signatures, mundane genre, transmittal attachments,
distribution lists as a derived ledger), EML-02/EML-03/DL-01 validators, and a
FACT-01/MENT-01 pdf layout-extraction fallback. Tests green at review start:
`bin/test` 458 passed + 6 skipped (soffice), org 72, flagship 20. Byte pin
green fleet-wide + flagship. Three parallel adversarial reviewers plus the
`/security` scan produced the findings below.

**External reviewers:** None configured.

**Security:** `/security` run on the 11 changed code files (surface changed
since the M13 scan at 66b87b9). 0 BLOCK / 1 WARN / 0 NOTE; the WARN is SEC-1
below. Airlock intact (no scoped file calls a model or the network; threading
headers, To/Cc, signatures, quoted history are all render-derived from
ledgers; the sole model-output-to-filesystem path stays guarded).

### Findings

[BLOCK] orgsmith/render/__init__.py:127-137 (and _full_mail_body :52-78, call site :226) — a mail-block reply renders even when a thread predecessor is unauthored, crashing render with FileNotFoundError.
  Evidence: the main render `todo` loop adds an eml entry on its OWN
  `authored_hash` alone (`if doc_state.authored_hash is None: pending += 1;
  continue`), never checking predecessors. `_full_mail_body` then recurses up
  the thread and reads each predecessor's DocIR unconditionally
  (`DocIR.model_validate_json(docir_path(paths, entry.doc_id).read_text(...))`).
  Threads split across batches (`BATCH_SIZE = 6` in authoring/contexts.py) with
  contiguous thread_pos ranges. Under concurrent K-batch authoring (/forge
  Step 3) or an interrupted-then-resumed session, a later-pos batch can be
  ingested while an earlier-pos batch is not; rendering the higher-pos reply
  recurses to the unauthored predecessor and `read_text()` raises
  FileNotFoundError, aborting the whole render stage instead of leaving the
  thread pending. Regression: pre-M14 each eml rendered from its own DocIR only.
  Failure scenario: engagement with 9 batchable docs → batch1 = [kickoff,
  letter, minutes, pos0, pos1, pos2], batch2 = [pos3, pos4, pos5]; batch2
  ingests, batch1's worker fails; `render` crashes on pos5 → pos2's missing
  DocIR.
  Suggested fix: in the render todo loop, defer a mail-block reply
  (`thread_pos > 0`) to pending when any thread predecessor's `authored_hash`
  is None (mirror the transmittal deferral), so a partially-authored thread
  leaves its tail pending and browsable rather than crashing.

[WARN] orgsmith/artifacts.py:82-95 (load_manifest) — the M14 transmittal `attach_path` (a render_params value) joins `share_dir` without the `check_relpath` guard every `entry.path` gets. (SEC-1)
  Evidence: `load_manifest` guards `entry.path` with `check_relpath` (:89), but
  the render sink (`render/__init__.py:316` `attach_file = paths.share_dir /
  str(ap)` → `.read_bytes()` → embedded into the .eml) and the validate sink
  (`validate/rules.py:1096` `src = ctx.paths.share_dir / str(attach_path)` →
  `.read_bytes()`) join an unguarded `render_params["attach_path"]`. A
  generated org's `-metadata/` manifest is a publishable artifact; a tampered
  `"attach_path": "../../../../etc/passwd"` or an absolute path makes a
  recipient's `render` read that file and embed its bytes verbatim into the
  output `.eml` (an exfiltration primitive on republish). Not reachable from
  model output or the network (render_params is planner-written). Committed
  fixtures are all clean in-share paths.
  Suggested fix: guard `attach_path` with `check_relpath` in `load_manifest`
  beside the `entry.path` check, so both render and validate sinks inherit
  containment.

[WARN] orgsmith/docplan/planner.py:447 (_next_send fallback) — the range-end-wall fallback can return an (date, minute) pair equal to the previous message, violating the documented strictly-increasing contract.
  Evidence: `return cur_date, min(cur_min + 1, day_hi - 1)` — when the thread
  is pinned at the last business day (date cannot advance) and `cur_min` has
  already reached `day_hi - 1`, `min(cur_min + 1, day_hi - 1) == cur_min`, so
  two messages carry an identical Date header. Reachable for a depth-≥3 thread
  whose opener sits at the range-end wall. Low downstream impact (threading
  headers/quoted history key off thread_pos, not the date; filenames stay
  unique), but it breaks the "always strictly increasing" invariant the
  docstring promises. Committed fixtures do not hit the wall (byte-safe fix).
  Suggested fix: guarantee a strictly-greater send in the wall fallback (e.g.
  `cur_date, cur_min + 1` bounded to a valid minute), or narrow the docstring.

[WARN] orgsmith/acl.py:50-58 (derive_distribution_lists) — a department name containing any character outside `[a-z0-9.-]` (after space/slash replacement) produces a `dl:` id that fails the DistributionList pattern, raising ValidationError at generation (run_acl) and validation (dl_01).
  Evidence: `local = dept.lower().replace(" ", "-").replace("/", "-")` then
  `DistributionList(id=f"dl:{local}", ...)`; `DistributionList.id` is
  `pattern=r"^dl:[a-z0-9.\-]+$"`. A dept `"R&D"` / `"Sales & Marketing"` yields
  `dl:r&d` / `dl:sales-&-marketing` → ValidationError. No committed charter
  uses such a dept (byte-safe), but a valid recipe with `distribution_lists >
  0` and an `&`/`(`/`'` in a dept name crashes.
  Suggested fix: sanitize `local` to the id charset (e.g.
  `re.sub(r"[^a-z0-9.-]+", "-", ...).strip("-")`) or reuse a `naming` sanitizer.

[NOTE] orgsmith/docplan/planner.py:590-596 (_emit_mundane) — mundane filenames have no dedupe; two notes sharing a business-day date and a subject (subjects cycle mod 10) collide and `build()` hard-fails with `docplan: duplicate path`. Requires `mundane_emails` far above the date-range length in days; no realistic recipe hits it, and it fails loudly. Left as-is.

[NOTE] orgsmith/render/eml.py:198-208 (eml_attachment_bytes) — `BytesParser(...).parse(open(path, "rb"))` does not close the file handle. Resource hygiene only. Optional.

### Fixes Applied

All four BLOCK/WARN findings fixed by /codefix, re-reviewed, and covered:

- **[BLOCK]** `render/__init__.py` — the render todo loop now defers a
  mail-block reply (`send_minute` set, `thread_pos > 0`) to pending when any
  thread predecessor's `authored_hash` is None, mirroring the transmittal
  deferral, so a thread split across batches (or a resumed session) stays
  browsable instead of crashing on a missing predecessor DocIR. Regression test
  added: `tests/test_unit_mail.py::test_render_defers_reply_when_a_thread_predecessor_is_unauthored`
  (unauthors an opener, deletes its DocIR, asserts render returns 0 and defers
  the thread).
- **[WARN/SEC-1]** `artifacts.py` `load_manifest` — `attach_path` now passes
  `check_relpath` beside `entry.path`, so the render and validate sinks inherit
  path containment.
- **[WARN]** `docplan/planner.py` `_next_send` — the wall fallback is bounded
  to 1439 (not `day_hi - 1`), so the send is strictly later than the previous
  message, honoring the strictly-increasing contract.
- **[WARN]** `acl.py` `derive_distribution_lists` — the DL local-part is now
  `re.sub(r"[^a-z0-9.-]+", "-", dept.lower()).strip("-")`, so a dept name with
  `&`/`(`/`'` yields a valid `dl:` id instead of a ValidationError.

Byte-safe: committed fixtures don't hit the wall, use only clean dept names,
and carry honest in-share `attach_path`s, so no committed bytes moved (byte pin
green fleet-wide + flagship). Full suite green after fixes: `bin/test` 458 + 6
skipped, org 72, flagship 20. The two NOTEs are left as-is (loud-failing and
unreachable in practice; resource hygiene only).

### Accepted Risks

None.

---
*Prior review (2026-07-17c, commit 1bf2c1d): M12a capability layer + calderwood
pilot; 11 commits, tests green, 0 unresolved BLOCK. Base was the empty tree
(first push); the M14 base is now origin/main.*

<!-- REVIEW_META: {"date":"2026-07-22","commit":"92d8acb","reviewed_up_to":"92d8acb","base":"origin/main","tier":"full","block":0,"warn":0,"note":2} -->
