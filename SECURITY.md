# Security

## Security Review — 2026-07-28 (scope: paths)

**Summary:** Reviewed the new bring-your-own-token authoring driver
(`drivers/config.py`, `drivers/providers.py`, `drivers/forge_external.py`), the
first out-of-airlock code that reads API keys, makes network requests, and
processes model output. No BLOCK, no WARN. One NOTE: outbound requests target a
configurable `base_url` with no scheme allowlist (defense-in-depth only, no
reachable attack vector). Key handling, subprocess use, and model-output
validation are all sound.

### Findings

- **[NOTE] providers.py:38-43, 121-123, 148-149 (via config.py:177-178) —
  outbound request base_url has no scheme allowlist.** `base_url_for` returns
  whatever is in `ORGSMITH_<PROVIDER>_BASE_URL` (or the hardcoded https default),
  and `_post_json` hands `f"{base_url}/chat/completions"` (or `/messages`)
  straight to `urllib.request.urlopen`, which also handles `file://`, `ftp://`,
  etc. Today this is not an attack vector: `base_url` is set only from the
  process environment or the user's own `~/.config/orgsmith/providers.env`, and
  no work-order content, model output, or other untrusted input flows into it,
  so an actor who could change `base_url` already controls the environment. This
  is recorded as defense in depth: if a future change ever lets untrusted input
  influence the endpoint, an `http(s)`-only guard should be in place first.
  - Attack vector: none reachable in the current design (self-configuration
    only). Filed as NOTE, not WARN, for that reason.
  - Remediation: in `base_url_for` (or `call_provider`) reject any base_url whose
    scheme is not `http`/`https` before the request, and keep `http` for the
    local/self-hosted case.

### Reviewed surface and scope

- **Key handling never exposes a secret.** Keys are read from the environment
  (`key_for`, config.py:190-191), seeded optionally from a gitignored
  `providers.env` that lives outside the repo. `--check` prints key *presence*
  only, never the value (forge_external.py:367-368). Every `_log` line carries
  the env-var *name*, not the value (providers.py:63, 67, and the shape helpers).
  `load_provider_env` returns the applied mapping "for logging/tests" but the
  caller discards it (forge_external.py:410), so values are never printed. Keys
  travel only in the `Authorization: Bearer`/`x-api-key` headers
  (providers.py:112, 141), never in argv, a file, or the prompt. Git history of
  all three files is one commit with no secret-pattern hits; `providers.env` and
  `drivers/providers.env` are both gitignored; `providers.env.example` ships only
  commented `sk-...`-style placeholders.
- **No command injection.** `run_cli` builds a fixed argv list and calls
  `subprocess.run` with no `shell=True` (forge_external.py:164-169); the verb is
  a driver-owned literal and the slug/paths become single argv elements that
  cannot break out to a shell. `reply_path` is derived from the work-order `id`
  (forge_external.py:188), which comes from orgsmith's own deterministic emission
  (trusted airlock core), not from the model reply.
- **Model output reaches no dangerous sink unvalidated.** The provider reply is
  parsed by `extract_json` (a single O(n) brace scanner honoring string
  literals, forge_external.py:102-138 — no regex, no ReDoS, input bounded by
  `max_tokens`), then schema-validated with `deliverable_cls.model_validate`
  *before* it is written to disk and *before* `orgsmith ... --ingest` re-validates
  it inside the airlock (forge_external.py:217-225). A `None` adapter result is a
  hard stop, not a silent skip (forge_external.py:201-205). The model never
  influences a file path or a command.
- **TLS verification is intact.** `urllib.request.urlopen` verifies https
  certificates by default and the code adds no override (no
  `ssl._create_unverified_context`, `CERT_NONE`, `check_hostname=False`, or
  custom `context=`). All four named-provider defaults are https.
- **Fail-open adapters do not leak internals.** `call_provider` catches
  network/HTTP/parse errors and logs one line with the provider name, status
  code, and the provider's own error `message` (providers.py:81-103); no Python
  traceback, no key, no local path. The repair-loop `feedback` sent back to the
  provider is orgsmith's ingest-rejection text over *synthetic* org data (the
  whole product is fictional organizations), which the user has explicitly opted
  to send to their chosen endpoint, so it is not a data-exposure finding.
- **No new dependencies, no PII.** The driver imports stdlib plus the existing
  `pydantic` and the pure `orgsmith.schemas`; nothing to pin or CVE-check. No
  auth/session surface (local CLI). No real names, emails, or phone numbers in
  the three files; the only proper nouns are provider hostnames and env-var
  names.

### Accepted Risks

None.

---
*Prior review (2026-07-28, scope paths, commit eff521e0): reviewed the .eml
renderer, the v0 validator catalog, and the checksum-manifest generator;
0 BLOCK / 0 WARN / 1 NOTE. The standing NOTE (out of scope here) is that
`ManifestEntry.path` in `orgsmith/validate/rules.py` is resolved against the
share tree without a relative-path constraint, a traversal gap with no reachable
harmful sink under the airlock (no write, no content echo, no network, and
`man_01` flags a non-share path loudly).*

<!-- SECURITY_META: {"date":"2026-07-28","commit":"cf9ee69687a13955284f7ccb714c46d42559b43c","scope":"paths","scanned_files":["drivers/config.py","drivers/forge_external.py","drivers/providers.py"],"block":0,"warn":0,"note":1} -->
