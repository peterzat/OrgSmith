# Security

## Security Review — 2026-07-22 (scope: paths, M14 email realism surface)

**Summary:** Reviewed the eleven files that carry the M14 email work (thread
mechanics, MIME transmittal attachments, distribution lists, quoted history).
One WARN: the new `attach_path` render-param reaches a `share_dir` file read
(and, in render, an embed into the output `.eml`) without the `check_relpath`
containment that every other manifest path receives. It is a defense-in-depth
gap at the same data-versus-code boundary the M13 review closed for
`state.json`, not a live exploit in the honest pipeline.

### Findings

**[WARN] `orgsmith/render/__init__.py:316` and `orgsmith/validate/rules.py:1096`
— manifest `render_params["attach_path"]` joined to `share_dir` without path
containment.**

- Attack vector: OrgSmith treats a generated org (including its `-metadata/`
  ground truth) as a publishable artifact, so a distributed org's
  `docplan/manifest.jsonl` is an input the recipient's `render` and `validate`
  runs trust. Every other share join uses `entry.path`, which
  `check_relpath` guards at load (`orgsmith/artifacts.py:89`, rejecting `..`
  and absolute paths). The M14 transmittal path is the one exception: an `eml`
  entry's `render_params["attach_path"]` is joined and read with no such
  guard. A crafted or tampered manifest entry with
  `"attach_path": "/home/victim/.ssh/id_rsa"` (or `"../../../../etc/passwd"`)
  makes the render stage read that file and embed its bytes verbatim as a MIME
  attachment in the rendered `.eml` (`orgsmith/render/__init__.py:316`
  `attach_file = paths.share_dir / str(ap)`, `:324` `attach_file.read_bytes()`,
  `:342-347` embed via `render_eml`). If the recipient republishes the
  rendered corpus, that is an exfiltration primitive for any file the
  generating user can read. `validate`'s EML-03 rule performs the same
  unguarded read for a byte-compare (`orgsmith/validate/rules.py:1096`
  `src = ctx.paths.share_dir / str(e.render_params["attach_path"])`, `:1102`
  `src.read_bytes()`).
- Evidence: `pathlib` join semantics confirmed — `share_dir / "/etc/passwd"`
  resolves to `/etc/passwd`, and `share_dir / "../../../../etc/passwd"`
  resolves out of the share; `check_relpath` rejects both but accepts the
  honest relative path (`Engagements/<client>/<kickoff>.docx`). Committed
  honest-flow values are all in-share relative paths, so the current fleet is
  not affected; the gap is the missing guard, not a tainted fixture.
- Not reachable from model output or the network. `render_params` is
  planner-written, never model-authored (the model controls only DocIR, whose
  `doc_id` is pattern-locked and whose blocks reach message bodies, not
  headers or paths). This is strictly the tampered-publishable-artifact
  boundary.
- Severity note: rated one notch above the analogous M13 `state.json` NOTE
  because the render sink embeds the traversal-read bytes into a distributable
  file rather than consuming them internally. Downgrade to NOTE if parity with
  the prior entry is preferred; the remediation is the same either way.
- Remediation: run `check_relpath(str(ap))` on `attach_path` where the
  manifest is loaded (`orgsmith/artifacts.py` `load_manifest`, beside the
  existing `entry.path` check) so both the render and validate sinks inherit
  the guard, or guard each join at the sink. Refuse absolute and `..`
  components exactly as `entry.path` is refused.
- **Resolved in `6b67c12`** (the `/codereview` fix loop): `load_manifest`
  (`orgsmith/artifacts.py:93-95`) now runs `check_relpath` on a manifest
  entry's `attach_path` beside `entry.path`, so both the render and validate
  sinks inherit containment. This finding is closed; recorded here as the
  M14 security surface.

### Reviewed surface and scope

- **The airlock holds.** No file in scope calls a model or the network; Python
  still never authors. M14's model-facing change is that reply *bodies* are
  authored, while threading headers, To/Cc partition, signature blocks, and
  quoted history are all render-derived from the ledgers (`render/eml.py`
  `expected_headers` / `mail_signature` / `quote_history`), and ingest still
  rejects an authored sigblock in `eml`. The single model-output-to-filesystem
  path (`docir_path`) stays guarded by `naming.doc_id_filename`.
- **`.eml` files are never transmitted.** They are synthetic corpus artifacts
  written to disk, so CRLF in a header-bound value (`entry.title` to Subject,
  a tampered `dl` to To) yields malformed file content, not a mail-delivery
  injection. Considered and not filed as a finding: there is no MTA sink.
- **Distribution lists are derived ground truth, not access enforcement.**
  `derive_distribution_lists` and DL-01 recompute address/members/visibility
  from charter plus roster; nothing in scope enforces access, so there is no
  authz bypass surface here.
- **No secrets, no real PII.** The in-scope files hardcode no credentials; the
  synthetic names, emails, and domains are the product, not leaked PII.
- **Dependency/supply-chain and infra dimensions** were out of scope for this
  path-scoped run (no manifests or configs in the file list).

### Accepted Risks

None.

---
*Prior review (2026-07-21, scope M13 path containment and letterhead escaping,
commit 66b87b9): closed both carried-open notes in depth. `state.json`-derived
work-order names were contained at schema (`WorkOrderName` pattern), sink
(`contained_join`), and terminal (`strip_control`); charter-tainted letterhead
was context-escaped per-context before the `autoescape=False` PDF template
(`_css_string`, `html.escape`). 0 BLOCK / 0 WARN / 0 NOTE.*

<!-- SECURITY_META: {"date":"2026-07-22","commit":"92d8acb8dc32bb08e9d4a19ad8fcce5f16c0dc20","scope":"paths","scanned_files":["orgsmith/acl.py","orgsmith/artifacts.py","orgsmith/authoring/contexts.py","orgsmith/docplan/planner.py","orgsmith/docplan/registry.py","orgsmith/evals/emit.py","orgsmith/paths.py","orgsmith/render/__init__.py","orgsmith/render/eml.py","orgsmith/schemas.py","orgsmith/validate/rules.py"],"block":0,"warn":1,"note":0} -->
