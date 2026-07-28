# CODEREVIEW

## Review — 2026-07-28 (commit: afa211a)

**Review scope:** Refresh review. Focus: the model-choice updates since the
prior review (commit 9927e03), three files (`drivers/config.py`,
`drivers/providers.env.example`, `docs/BYO-AUTHORING.md`). Everything else is
unchanged.

**Summary:** Folds the live BYO test's findings into the defaults and docs. The
only code change is the OpenAI and OpenRouter default model ids (`gpt-4o` ->
`gpt-4.1`) plus comments; the rest is the config template and documentation.

**External reviewers:** None configured.

### Findings

No BLOCK or WARN issues.

- **Default model bump (drivers/config.py).** `PROVIDERS["openai"]` and
  `PROVIDERS["openrouter"]` default to `gpt-4.1` instead of `gpt-4o`, grounded
  in the live `dev-mini` run where `gpt-4o` could not hold the placeholder and
  mention discipline within the repair budget and `gpt-4.1` produced a
  validate-clean org. `gpt-4.1` is a real, available model id (used in that
  run). No logic change: `model_for` still prefers `ORGSMITH_<NAME>_MODEL` /
  `ORGSMITH_AUTHOR_MODEL` over the default, so any pinned config is unaffected.
  No test asserts the registry default (`_resolved` passes an explicit model),
  so the suite is unaffected.
- **Model-choice guidance (providers.env.example, docs/BYO-AUTHORING.md).** A
  "Model choice" doc section and per-provider template comments recommend the
  strong tier of each family. OpenAI is the measured anchor; the Anthropic /
  Google / OpenRouter / local recommendations are explicitly labeled
  by-analogy, not separately measured, which is the honest framing.

### Fixes Applied

None.

### Accepted Risks

None.

### Security

No security-relevant code changed since the last scan (9927e03): the
`drivers/config.py` delta is default model-id strings and comments, with no new
key, network, subprocess, or model-output surface. The prior `/security` scan of
`config.py` (0 BLOCK / 0 WARN / 0 NOTE) is carried forward; SECURITY.md's zero
open findings stand.

### Test Baseline

Full `bin/test` green: 16 short, 563 unit, 74 org, 20 flagship. Keyless and
offline; no fixture regenerated.

---
*Prior review (2026-07-28, commit 9927e03): refresh review of the fit-and-finish
turn (BYO hardening, backlog prune, doc reconciliation, README voice pass);
0 BLOCK / 0 WARN / 0 NOTE.*

<!-- REVIEW_META: {"date":"2026-07-28","commit":"afa211a","reviewed_up_to":"afa211a9e4fae205ce9e9d14932ad2c30c107efa","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":0} -->
