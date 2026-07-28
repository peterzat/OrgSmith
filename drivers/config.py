"""Provider registry and configuration for bring-your-own-token authoring.

Pure and network-free: this module decides WHICH provider authors and with
what model/base_url/effort, but never makes a request (that is
`drivers.providers`). Configuration is off by default and opt-in, mirroring
zat.env's external-reviewer contract:

- A provider is selected only when `ORGSMITH_AUTHOR_PROVIDER` is set (or a
  `--provider` flag is passed). Unset means BYO mode is inert.
- Keys and overrides come from the process environment, optionally seeded
  from an `.env`-style file at `~/.config/orgsmith/providers.env` (override
  the path with `ORGSMITH_PROVIDERS_ENV`, mainly for test isolation). Values
  already present in the real environment win over the file.

The file lives outside the repository so a key can never be committed; a
shipped `providers.env.example` documents every knob with all lines
commented, so cloning the repo turns nothing on.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_EFFORT = "high"

# Outbound requests may only go to an http(s) endpoint. base_url is operator-set
# (env or the user's providers.env), so this is defense in depth, not a guard
# against untrusted input: it refuses a stray file:/ftp:/gopher: scheme before it
# reaches urllib, so a config typo fails loud instead of hitting a local file.
ALLOWED_URL_SCHEMES = ("http", "https")


def base_url_scheme_ok(url: str | None) -> bool:
    return bool(url) and urlparse(url).scheme in ALLOWED_URL_SCHEMES


@dataclass(frozen=True)
class Provider:
    """One registry entry. Two adapter shapes cover every provider:

    - ``openai``: the OpenAI Chat Completions API (``POST
      {base_url}/chat/completions``, ``Authorization: Bearer``). OpenAI,
      OpenRouter, Google's OpenAI-compatible endpoint, and any local
      Ollama/LM Studio or third-party OpenAI-compatible host all speak it.
    - ``anthropic``: the Anthropic Messages API (``POST {base_url}/messages``,
      ``x-api-key`` + ``anthropic-version``).

    ``base_url`` and ``model`` are overridable per provider via
    ``<base_url_env>`` and ``<model_env>``, so any other OpenAI-compatible
    host (xAI, DeepSeek, Mistral, Together, Groq, ...) works by config alone,
    with no code change: point the generic ``local`` entry at its base_url.
    """

    name: str
    shape: str  # "openai" | "anthropic"
    default_base_url: str  # "" means the user must supply one via base_url_env
    key_env: str
    default_model: str  # "" means the user must supply one via model_env
    base_url_env: str
    model_env: str
    key_required: bool = True  # local/self-hosted endpoints may need no key


# The four named providers plus a generic OpenAI-compatible `local` entry. The
# default model ids are a convenience only; every one is overridable, and
# `--check` prints the effective model so a stale default is visible before a
# token is spent. The OpenAI/OpenRouter defaults are `gpt-4.1`, not `gpt-4o`:
# in a live dev-mini run gpt-4o could not satisfy OrgSmith's placeholder and
# mention discipline within the repair budget, while gpt-4.1 produced a
# validate-clean org (one repair round per batch). Every default here is the
# strong tier of its family (Anthropic Sonnet 5, Gemini 2.5 Pro); the cheap
# tier (Gemini Flash, a small local model) will miss the same discipline gpt-4o
# did. Those non-OpenAI recommendations are by analogy, not separately measured.
# See docs/BYO-AUTHORING.md.
# Reasoning models that reject `max_tokens` (OpenAI o-series) are best driven
# through the `local`/generic entry with a body override, or an upstream
# OpenAI-compatible gateway.
PROVIDERS: dict[str, Provider] = {
    "openai": Provider(
        name="openai",
        shape="openai",
        default_base_url="https://api.openai.com/v1",
        key_env="OPENAI_API_KEY",
        default_model="gpt-4.1",
        base_url_env="ORGSMITH_OPENAI_BASE_URL",
        model_env="ORGSMITH_OPENAI_MODEL",
    ),
    "anthropic": Provider(
        name="anthropic",
        shape="anthropic",
        default_base_url="https://api.anthropic.com/v1",
        key_env="ANTHROPIC_API_KEY",
        default_model="claude-sonnet-5",
        base_url_env="ORGSMITH_ANTHROPIC_BASE_URL",
        model_env="ORGSMITH_ANTHROPIC_MODEL",
    ),
    "google": Provider(
        name="google",
        shape="openai",
        default_base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        key_env="GOOGLE_API_KEY",
        default_model="gemini-2.5-pro",
        base_url_env="ORGSMITH_GOOGLE_BASE_URL",
        model_env="ORGSMITH_GOOGLE_MODEL",
    ),
    "openrouter": Provider(
        name="openrouter",
        shape="openai",
        default_base_url="https://openrouter.ai/api/v1",
        key_env="OPENROUTER_API_KEY",
        default_model="openai/gpt-4.1",
        base_url_env="ORGSMITH_OPENROUTER_BASE_URL",
        model_env="ORGSMITH_OPENROUTER_MODEL",
    ),
    "local": Provider(
        name="local",
        shape="openai",
        default_base_url="",  # e.g. http://localhost:11434/v1 (Ollama)
        key_env="ORGSMITH_LOCAL_API_KEY",
        default_model="",
        base_url_env="ORGSMITH_LOCAL_BASE_URL",
        model_env="ORGSMITH_LOCAL_MODEL",
        key_required=False,
    ),
}


def default_providers_env_path() -> Path:
    return Path.home() / ".config" / "orgsmith" / "providers.env"


def providers_env_path() -> Path:
    override = os.environ.get("ORGSMITH_PROVIDERS_ENV")
    return Path(override) if override else default_providers_env_path()


def load_provider_env(env: dict[str, str] | None = None) -> dict[str, str]:
    """Seed the process environment from the providers.env file.

    Parses simple ``KEY=VALUE`` lines, ignoring blanks and ``#`` comments and
    stripping an optional surrounding pair of quotes from the value. A value
    already present in ``env`` (the real environment) is left untouched, so a
    shell export overrides the file. Returns the mapping that was applied
    (only the keys this call set), for logging/tests. A missing file is not an
    error: it simply seeds nothing, which is the off-by-default state.
    """
    target = os.environ if env is None else env
    path = providers_env_path()
    applied: dict[str, str] = {}
    if not path.exists():
        return applied
    for raw in path.read_text("utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if not key or key in target:
            continue
        target[key] = value
        applied[key] = value
    return applied


def selected_provider_name(explicit: str | None = None) -> str | None:
    """The chosen provider name, or None (the off-by-default gate)."""
    name = explicit or os.environ.get("ORGSMITH_AUTHOR_PROVIDER")
    name = name.strip() if name else None
    return name or None


def select_provider(explicit: str | None = None) -> Provider | None:
    """Resolve the selected provider, or None when nothing is selected.

    Raises KeyError on an unknown provider name so a typo fails loudly rather
    than silently falling back to the harness.
    """
    name = selected_provider_name(explicit)
    if name is None:
        return None
    if name not in PROVIDERS:
        raise KeyError(
            f"unknown provider {name!r}; known: {', '.join(sorted(PROVIDERS))}"
        )
    return PROVIDERS[name]


def base_url_for(provider: Provider) -> str | None:
    return os.environ.get(provider.base_url_env) or provider.default_base_url or None


def model_for(provider: Provider) -> str | None:
    return (
        os.environ.get(provider.model_env)
        or os.environ.get("ORGSMITH_AUTHOR_MODEL")
        or provider.default_model
        or None
    )


def key_for(provider: Provider) -> str | None:
    return os.environ.get(provider.key_env) or None


def author_effort() -> str:
    return os.environ.get("ORGSMITH_AUTHOR_EFFORT", DEFAULT_EFFORT)


def missing_requirements(provider: Provider) -> list[str]:
    """What a selected provider still needs before it can author. Empty means
    ready. Used by `--check` to fail loud when a provider is chosen but not
    fully configured."""
    missing: list[str] = []
    base = base_url_for(provider)
    if base is None:
        missing.append(f"base_url ({provider.base_url_env})")
    elif not base_url_scheme_ok(base):
        missing.append(f"base_url must be http/https ({provider.base_url_env})")
    if model_for(provider) is None:
        missing.append(f"model ({provider.model_env})")
    if provider.key_required and key_for(provider) is None:
        missing.append(f"api key ({provider.key_env})")
    return missing
