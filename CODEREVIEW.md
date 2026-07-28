# CODEREVIEW

## Review — 2026-07-28 (commit: cf9ee69)

**Summary:** Full review of the bring-your-own-token authoring driver
(`origin/main`..HEAD, two commits): a new out-of-airlock `drivers/` package
(config/registry, two stdlib-HTTP provider adapters, the WorkOrder ->
provider -> Deliverable loop with a `--check` preflight), its offline keyless
tests, a short-tier guard that `orgsmith/` never imports `drivers/`, packaging
and `.gitignore` updates, plus the spec/docs/README/backlog/`/forge`-skill
prose. No file under `orgsmith/` changed, so the airlock and the committed
fleet are untouched.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN issues.

- **Airlock boundary holds.** All provider/key/network code lives in
  `drivers/`, outside the `orgsmith/` package the airlock constrains. The
  dependency is one-way (driver imports `orgsmith.schemas`; nothing in
  `orgsmith/` imports `drivers`), now enforced by
  `tests/test_short.py::test_orgsmith_never_imports_the_out_of_airlock_driver`.
  The keyless-suite guard stays green: `tests/test_unit_driver.py` names no
  provider key literal (it routes through `PROVIDERS[...].key_env`).
- **Off-by-default verified.** With no provider selected, `--check` prints the
  OFF state and exits 0, and the driver's drive path exits 0 mutating nothing;
  the `/forge` BYO branch is inert unless `ORGSMITH_AUTHOR_PROVIDER` is set.
- **Fail-open adapter / fail-loud loop.** `call_provider` returns `None` on
  any missing key, network, non-2xx, or empty/malformed response and never
  raises; the driver treats `None` as a hard stop and re-prompts on `--ingest`
  rejection up to `--max-retries`, then fails loudly. Deliverables are
  schema-validated against `orgsmith.schemas` before ingest and re-validated by
  the airlock's `--ingest`. Covered by unit tests (both shapes, degradation,
  repair, stamping, extraction).
- **[NOTE] drivers/providers.py:33-43 (via drivers/config.py:177-178) — no
  scheme allowlist on the configurable `base_url` handed to
  `urllib.request.urlopen`.** Defense-in-depth only, no reachable vector:
  `base_url` comes solely from the process environment or the user's own
  gitignored `providers.env`; no work-order content or model output flows into
  it. Recorded (SECURITY.md) so a `http(s)`-only guard lands before any future
  change makes the endpoint reachable from untrusted input. Not fixed here to
  keep the review scope minimal.

### Fixes Applied

None.

### Accepted Risks

None new. The prior standing NOTE on `ManifestEntry.path`
(`orgsmith/validate/rules.py`) is out of this change's scope and unaffected.

### Test Baseline

Full default suite green: 644 passing (15 short, 555 unit, 74 org). Flagship 20.
`bin/test` stays keyless and offline; the ~35 new driver tests mock HTTP and the
`orgsmith` subprocess.

### Security

`/security` scanned the three new driver files: 0 BLOCK / 0 WARN / 1 NOTE (the
`base_url` scheme-allowlist note above). Keys are read from the environment
only, never logged (presence-only in `--check`) and never written to argv,
file, or prompt; `subprocess.run` uses a fixed argv list with no `shell=True`;
TLS verification is never overridden; `providers.env` is gitignored and the
committed template ships only commented placeholders.

---
*Prior review (2026-07-28, commit f081c77): full review of the mail-banner
completion and the v2.1.1 patch; 0 BLOCK / 0 WARN / 1 NOTE, no production logic
changed.*

<!-- REVIEW_META: {"date":"2026-07-28","commit":"cf9ee69","reviewed_up_to":"cf9ee69687a13955284f7ccb714c46d42559b43c","base":"origin/main","tier":"full","block":0,"warn":0,"note":1} -->
