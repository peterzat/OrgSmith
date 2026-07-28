"""HTTP adapters for bring-your-own-token authoring.

One entry point, `call_provider`, dispatching on the provider's shape. Two
shapes cover every registry entry: OpenAI Chat Completions and Anthropic
Messages. Standard library only (`urllib`), so BYO mode adds no runtime
dependency to the project.

Fail-open contract (mirrors zat.env's review adapters): any operational
failure, a missing key, a connection error, a non-2xx response, or an empty
or malformed body, logs one line to stderr and returns None. The function
never raises for an operational failure. The caller (the driver loop) decides
what a None means; for authoring it is a hard stop, because a missing
document breaks the pipeline, unlike a missing review finding.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from .config import Provider, base_url_for, base_url_scheme_ok, key_for

ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MAX_TOKENS = 8192


def _log(message: str) -> None:
    print(message, file=sys.stderr)


def _post_json(url: str, *, headers: dict[str, str], body: dict, timeout: int):
    """POST a JSON body and return the parsed JSON response, or raise the
    underlying urllib error. Kept separate so tests can monkeypatch
    `urllib.request.urlopen` at one seam."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_provider(
    provider: Provider,
    *,
    system: str,
    user: str,
    model: str,
    timeout: int = 120,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str | None:
    """Return the assistant's text, or None on any operational failure.

    Dispatches on `provider.shape`. Never raises for a network/HTTP/parse
    failure: it logs one stderr line tagged with the provider name and returns
    None.
    """
    key = key_for(provider)
    if provider.key_required and not key:
        _log(f"[{provider.name}] no api key ({provider.key_env}); skipping")
        return None
    base_url = base_url_for(provider)
    if not base_url:
        _log(f"[{provider.name}] no base_url ({provider.base_url_env}); skipping")
        return None
    if not base_url_scheme_ok(base_url):
        _log(
            f"[{provider.name}] refusing non-http(s) base_url "
            f"({provider.base_url_env}); skipping"
        )
        return None
    base_url = base_url.rstrip("/")

    try:
        if provider.shape == "anthropic":
            return _call_anthropic(
                base_url, key, system=system, user=user, model=model,
                timeout=timeout, max_tokens=max_tokens, name=provider.name,
            )
        return _call_openai_compatible(
            base_url, key, system=system, user=user, model=model,
            timeout=timeout, max_tokens=max_tokens, name=provider.name,
        )
    except urllib.error.HTTPError as err:
        detail = _error_detail(err)
        _log(f"[{provider.name}] http {err.code}{detail}; skipping")
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        _log(f"[{provider.name}] request failed ({err}); skipping")
        return None
    except (ValueError, KeyError, IndexError, TypeError) as err:
        _log(f"[{provider.name}] malformed response ({err}); skipping")
        return None


def _error_detail(err: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(err.read().decode("utf-8"))
        message = payload.get("error", {})
        if isinstance(message, dict):
            message = message.get("message")
        if message:
            return f": {message}"
    except (ValueError, OSError, AttributeError):
        pass
    return ""


def _call_openai_compatible(
    base_url: str, key: str | None, *, system: str, user: str, model: str,
    timeout: int, max_tokens: int, name: str,
) -> str | None:
    headers = {}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
    }
    payload = _post_json(
        f"{base_url}/chat/completions", headers=headers, body=body, timeout=timeout
    )
    choices = payload.get("choices") or []
    if not choices:
        _log(f"[{name}] empty response (no choices); skipping")
        return None
    text = (choices[0].get("message") or {}).get("content")
    if not text or not text.strip():
        _log(f"[{name}] empty response (no content); skipping")
        return None
    return text


def _call_anthropic(
    base_url: str, key: str | None, *, system: str, user: str, model: str,
    timeout: int, max_tokens: int, name: str,
) -> str | None:
    headers = {"anthropic-version": ANTHROPIC_VERSION}
    if key:
        headers["x-api-key"] = key
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    payload = _post_json(
        f"{base_url}/messages", headers=headers, body=body, timeout=timeout
    )
    blocks = payload.get("content") or []
    parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
    text = "".join(parts)
    if not text.strip():
        _log(f"[{name}] empty response (no text content); skipping")
        return None
    return text
