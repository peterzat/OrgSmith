# drivers/ — out-of-airlock authoring drivers

Bring-your-own-token authoring for OrgSmith. This package drives the same
deterministic `orgsmith` CLI verbs the Claude Code skills drive, but the model
that authors is a provider you configure (OpenAI, Anthropic, Google,
OpenRouter, or any OpenAI-compatible endpoint, including free-tier and local
models) instead of the ambient Claude Code session.

It lives outside `orgsmith/` on purpose: the airlock forbids the core package
from calling a model or the network, so the code that does belongs here.

Off by default. Nothing happens until you select a provider.

```bash
# See what is configured (spends no token):
python -m drivers.forge_external --check

# Generate an org end to end via the configured provider:
python -m drivers.forge_external dev-mini
```

Full documentation, provider table, and the manual smoke recipe are in
[`docs/BYO-AUTHORING.md`](../docs/BYO-AUTHORING.md). Config template:
[`providers.env.example`](providers.env.example).
