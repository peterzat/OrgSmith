# Security

## Security Review — 2026-07-28 (scope: paths)

**Summary:** Re-reviewed the three out-of-airlock driver files
(`drivers/config.py`, `drivers/providers.py`, `drivers/forge_external.py`) over
the delta since the last security baseline (`cf9ee69`..`9927e03`). The only
security-relevant change is the `base_url` http(s) scheme allowlist that
resolves the prior standing NOTE; the `forge_external.py` change is a whitespace
reflow of the system-prompt string with no logic impact. No BLOCK, no WARN, no
NOTE. Zero open findings.

### Findings

No security issues identified in the reviewed scope.

### Verified this turn

- **The `base_url` scheme allowlist (the prior NOTE's fix) is sound and
  enforced at the sink.** `config.base_url_scheme_ok` (config.py:36-37) accepts
  only `http`/`https` via `urlparse().scheme`; empirically it rejects `file:`,
  `ftp:`, `gopher:`, empty, `None`, and protocol-relative (`//host`), and
  correctly normalizes case and leading-whitespace. It runs at the real request
  boundary in `call_provider` (providers.py:69-74) before any `_post_json` /
  `urllib.request.urlopen` call, and there is no code path to `_post_json` that
  skips it. It also feeds `missing_requirements` (config.py:214-218) so `--check`
  reports NOT READY with a non-zero exit (forge_external.py:370-373) and the drive
  path refuses (forge_external.py:433-444). The appended `/chat/completions` /
  `/messages` suffix cannot change the already-validated scheme.
- **The endpoint is still operator-controlled only, so this remains defense in
  depth.** `base_url_for` (config.py:188-189) reads solely
  `ORGSMITH_<PROVIDER>_BASE_URL` or a hardcoded https default; no work-order
  content or model output reaches it.
- **No secret leak, in tree or history.** Pattern scan of the last five commits
  touching these files is clean. `providers.env` and `drivers/providers.env` are
  gitignored (.gitignore:20-21); the only tracked env artifact is
  `providers.env.example`, all lines commented, shipping only truncated
  `sk-...`-style placeholders. Keys are read from the environment
  (`key_for`, config.py:201-202), sent only in `Authorization: Bearer` /
  `x-api-key` headers, and never logged. The new refuse-scheme log line
  (providers.py:70-73) prints the env-var name, not the value or key. `--check`
  prints key presence only (forge_external.py:367-368); `load_provider_env`'s
  applied-value mapping is discarded by the caller (forge_external.py:410).
- **No command injection, no model-output-to-sink, TLS intact.** `run_cli`
  builds a fixed argv with no `shell=True` (forge_external.py:164-169);
  `reply_path` derives from the airlock-emitted work-order `id`
  (forge_external.py:187-188), not model output. The reply is parsed by the O(n)
  brace scanner `extract_json` then `model_validate`'d before disk and re-validated
  by `orgsmith --ingest` (forge_external.py:207-225). No TLS override anywhere.
- **No new dependencies, no PII.** Stdlib plus existing `pydantic` /
  `orgsmith.schemas`. Proper nouns are provider hostnames and env-var names only.

### Accepted Risks

None.

---
*Prior review (2026-07-28, scope paths, commit cf9ee69): first review of the
new bring-your-own-token authoring driver (the same three files), the first
out-of-airlock code to read keys, make network requests, and process model
output; 0 BLOCK / 0 WARN / 1 NOTE. The one NOTE (configurable `base_url` with no
scheme allowlist) is resolved as of this turn's `base_url_scheme_ok` guard. Key
handling, fixed-argv subprocess use, and pre-ingest model-output validation were
all found sound. In the same window the long-standing `ManifestEntry.path`
traversal NOTE was closed as not reachable (`load_manifest` runs
`naming.check_relpath` at load, refusing absolute or `..`-bearing paths before any
rule resolves them).*

<!-- SECURITY_META: {"date":"2026-07-28","commit":"9927e03b33306854ea716f2f4b08a2fe7d6ec04c","scope":"paths","scanned_files":["drivers/config.py","drivers/forge_external.py","drivers/providers.py"],"block":0,"warn":0,"note":0} -->
