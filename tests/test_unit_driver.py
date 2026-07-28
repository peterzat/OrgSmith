"""Unit tier: the bring-your-own-token authoring driver, offline and keyless.

Every test mocks the network (`urllib.request.urlopen`) and the orgsmith
subprocess (`drivers.forge_external.run_cli`), so nothing here spends a token,
opens a socket, or needs a provider credential. The driver lives in the
out-of-airlock `drivers/` package; the airlock scans in test_short.py do not
reach it. This file names no provider key literal on purpose (it reaches every
key env through `PROVIDERS[...].key_env`), so the keyless-suite guard stays
green.
"""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.request

import pytest

from drivers import config, forge_external, providers
from drivers.config import PROVIDERS, Provider
from drivers.forge_external import (
    DriverError,
    Resolved,
    author_and_ingest,
    check,
    extract_json,
)
from orgsmith.paths import org_paths
from orgsmith.schemas import AuthoringDeliverable, EnrichmentDeliverable

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _clean_env(tmp_path, monkeypatch):
    """Isolate every test from the real environment and the real config file:
    point at an absent providers.env and clear any provider selection, keys,
    and overrides that might leak in."""
    monkeypatch.setenv("ORGSMITH_PROVIDERS_ENV", str(tmp_path / "absent.env"))
    for name in (
        "ORGSMITH_AUTHOR_PROVIDER",
        "ORGSMITH_AUTHOR_MODEL",
        "ORGSMITH_AUTHOR_EFFORT",
    ):
        monkeypatch.delenv(name, raising=False)
    for p in PROVIDERS.values():
        monkeypatch.delenv(p.key_env, raising=False)
        monkeypatch.delenv(p.base_url_env, raising=False)
        monkeypatch.delenv(p.model_env, raising=False)
    yield


# --- config: load + selection ----------------------------------------------


def test_load_provider_env_parses_and_respects_existing(tmp_path, monkeypatch):
    envfile = tmp_path / "providers.env"
    envfile.write_text(
        "# a comment\n\n"
        "ORGSMITH_AUTHOR_PROVIDER=openai\n"
        'ORGSMITH_OPENAI_MODEL="gpt-4o-mini"\n'
        "PRESENT=fromfile\n",
        "utf-8",
    )
    monkeypatch.setenv("ORGSMITH_PROVIDERS_ENV", str(envfile))
    target = {"PRESENT": "fromenv"}
    applied = config.load_provider_env(env=target)
    assert applied["ORGSMITH_AUTHOR_PROVIDER"] == "openai"
    assert applied["ORGSMITH_OPENAI_MODEL"] == "gpt-4o-mini"  # quotes stripped
    assert "PRESENT" not in applied  # already set: shell env wins over file
    assert target["PRESENT"] == "fromenv"


def test_load_provider_env_missing_file_is_noop(tmp_path, monkeypatch):
    monkeypatch.setenv("ORGSMITH_PROVIDERS_ENV", str(tmp_path / "nope.env"))
    assert config.load_provider_env(env={}) == {}


def test_select_provider_off_by_default():
    assert config.select_provider() is None


def test_select_provider_named(monkeypatch):
    monkeypatch.setenv("ORGSMITH_AUTHOR_PROVIDER", "anthropic")
    assert config.select_provider().name == "anthropic"


def test_select_provider_explicit_overrides_env(monkeypatch):
    monkeypatch.setenv("ORGSMITH_AUTHOR_PROVIDER", "openai")
    assert config.select_provider("google").name == "google"


def test_select_provider_unknown_raises(monkeypatch):
    monkeypatch.setenv("ORGSMITH_AUTHOR_PROVIDER", "bogus")
    with pytest.raises(KeyError):
        config.select_provider()


def test_env_overrides_base_url_and_model(monkeypatch):
    p = PROVIDERS["openai"]
    monkeypatch.setenv(p.base_url_env, "https://example.test/v1")
    monkeypatch.setenv(p.model_env, "custom-model")
    assert config.base_url_for(p) == "https://example.test/v1"
    assert config.model_for(p) == "custom-model"


def test_missing_requirements_reports_absent_key(monkeypatch):
    p = PROVIDERS["openai"]
    monkeypatch.delenv(p.key_env, raising=False)
    assert any("api key" in m for m in config.missing_requirements(p))


def test_local_requires_base_url_but_not_key():
    p = PROVIDERS["local"]
    missing = config.missing_requirements(p)
    assert any("base_url" in m for m in missing)
    assert not any("api key" in m for m in missing)


# --- prompt assembly --------------------------------------------------------


def test_user_prompt_embeds_work_order_verbatim():
    wo = '{"id": "wo:author:0001", "instructions": "AUTHOR EVERYTHING"}'
    prompt = forge_external._user_prompt(wo, None)
    assert wo in prompt
    assert "instructions" in prompt


def test_user_prompt_includes_feedback_on_repair():
    prompt = forge_external._user_prompt("{}", "missing required placeholders: f:x")
    assert "was rejected" in prompt
    assert "f:x" in prompt


def test_system_prompt_enforces_placeholders_and_json_only():
    assert "{{fact:" in forge_external.SYSTEM_PROMPT
    assert "ONLY" in forge_external.SYSTEM_PROMPT


# --- deliverable extraction -------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        ('{"a": 1}', {"a": 1}),
        ("```json\n{\"a\": 1}\n```", {"a": 1}),
        ("Here you go:\n{\"a\": {\"b\": 2}}\nThanks!", {"a": {"b": 2}}),
        ('{"s": "has a } brace inside"}', {"s": "has a } brace inside"}),
    ],
)
def test_extract_json_ok(text, expected):
    assert extract_json(text) == expected


@pytest.mark.parametrize("text", ["no json here", "{unbalanced", "{'not': json}"])
def test_extract_json_bad(text):
    with pytest.raises(DriverError):
        extract_json(text)


# --- author_and_ingest: stamping, validation, repair ------------------------


def _resolved(provider_name="openai", model="gpt-4o", max_retries=2):
    return Resolved(
        provider=PROVIDERS[provider_name],
        base_url="https://x/v1",
        model=model,
        generator_model=f"{provider_name}:{model}",
        effort="high",
        timeout=10,
        max_tokens=100,
        max_retries=max_retries,
    )


def _enrichment_json(wo_id="wo:foundation:0001"):
    return json.dumps(
        {
            "schema_id": "orgsmith/enrichment-deliverable@1",
            "work_order_id": wo_id,
            "personas": [{"person_id": "p:0001", "persona": "x" * 45}],
        }
    )


def _authoring_json(wo_id="wo:author:0001"):
    return json.dumps(
        {
            "schema_id": "orgsmith/authoring-deliverable@1",
            "work_order_id": wo_id,
            "docs": [
                {
                    "schema_id": "orgsmith/docir@1",
                    "doc_id": "d:0001",
                    "blocks": [
                        {"kind": "paragraph", "text": "Some prose."},
                        {"kind": "paragraph", "text": "More prose."},
                    ],
                }
            ],
        }
    )


def _make_wo(tmp_path, filename, wo_id):
    paths = org_paths("dev-mini", tmp_path)
    paths.workorders_dir.mkdir(parents=True, exist_ok=True)
    wo_path = paths.workorders_dir / filename
    wo_path.write_text(json.dumps({"id": wo_id}), "utf-8")
    return paths, wo_path


def test_stamps_generator_and_writes_reply(tmp_path, monkeypatch):
    paths, wo_path = _make_wo(tmp_path, "foundation-0001.json", "wo:foundation:0001")
    monkeypatch.setattr(forge_external, "call_provider", lambda *a, **k: _enrichment_json())
    seen = []
    monkeypatch.setattr(
        forge_external, "run_cli",
        lambda p, verb, *e: (seen.append(verb) or (0, "ok")),
    )
    author_and_ingest(paths, _resolved(), "foundation", wo_path, EnrichmentDeliverable)
    reply = paths.workorders_dir / "reply-wo-foundation-0001.json"
    obj = json.loads(reply.read_text())
    assert obj["generator"] == {"model": "openai:gpt-4o", "effort": "high"}
    EnrichmentDeliverable.model_validate_json(reply.read_text())  # real schema
    assert seen == ["foundation"]  # ingested via the foundation verb


def test_authoring_deliverable_validates_and_stamps(tmp_path, monkeypatch):
    paths, wo_path = _make_wo(tmp_path, "author-0001.json", "wo:author:0001")
    monkeypatch.setattr(forge_external, "call_provider", lambda *a, **k: _authoring_json())
    monkeypatch.setattr(forge_external, "run_cli", lambda *a: (0, "ok"))
    author_and_ingest(paths, _resolved(), "author", wo_path, AuthoringDeliverable)
    reply = paths.workorders_dir / "reply-wo-author-0001.json"
    AuthoringDeliverable.model_validate_json(reply.read_text())
    assert json.loads(reply.read_text())["generator"]["effort"] == "high"


def test_repair_loop_reprompts_with_rejection(tmp_path, monkeypatch):
    paths, wo_path = _make_wo(tmp_path, "foundation-0001.json", "wo:foundation:0001")
    prompts = []

    def fake_call(provider, *, system, user, model, timeout, max_tokens):
        prompts.append(user)
        return _enrichment_json()

    monkeypatch.setattr(forge_external, "call_provider", fake_call)
    results = iter([(1, "ingest rejected:\n  - missing personas for: p:0002"), (0, "ok")])
    monkeypatch.setattr(forge_external, "run_cli", lambda *a: next(results))
    author_and_ingest(paths, _resolved(), "foundation", wo_path, EnrichmentDeliverable)
    assert len(prompts) == 2
    assert "missing personas for: p:0002" in prompts[1]


def test_repair_loop_gives_up_loudly(tmp_path, monkeypatch):
    paths, wo_path = _make_wo(tmp_path, "foundation-0001.json", "wo:foundation:0001")
    monkeypatch.setattr(forge_external, "call_provider", lambda *a, **k: _enrichment_json())
    monkeypatch.setattr(forge_external, "run_cli", lambda *a: (1, "still nope"))
    with pytest.raises(DriverError):
        author_and_ingest(
            paths, _resolved(max_retries=1), "foundation", wo_path, EnrichmentDeliverable
        )


def test_none_from_provider_is_hard_stop(tmp_path, monkeypatch):
    paths, wo_path = _make_wo(tmp_path, "foundation-0001.json", "wo:foundation:0001")
    monkeypatch.setattr(forge_external, "call_provider", lambda *a, **k: None)
    monkeypatch.setattr(forge_external, "run_cli", lambda *a: (0, "ok"))
    with pytest.raises(DriverError):
        author_and_ingest(paths, _resolved(), "foundation", wo_path, EnrichmentDeliverable)


def test_local_schema_check_repairs_before_ingest(tmp_path, monkeypatch):
    paths, wo_path = _make_wo(tmp_path, "foundation-0001.json", "wo:foundation:0001")
    replies = iter(["not json at all", _enrichment_json()])
    monkeypatch.setattr(forge_external, "call_provider", lambda *a, **k: next(replies))
    ingests = []
    monkeypatch.setattr(forge_external, "run_cli", lambda *a: (ingests.append(a) or (0, "ok")))
    author_and_ingest(paths, _resolved(), "foundation", wo_path, EnrichmentDeliverable)
    assert len(ingests) == 1  # only the valid reply reached ingest


# --- adapters: fail-open + both shapes --------------------------------------


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _urlopen_returning(payload):
    def _open(req, timeout=None):
        return _FakeResp(payload)

    return _open


def test_openai_shape_success(monkeypatch):
    monkeypatch.setenv(PROVIDERS["openai"].key_env, "sk-test")
    monkeypatch.setattr(
        urllib.request, "urlopen",
        _urlopen_returning({"choices": [{"message": {"content": "hello"}}]}),
    )
    out = providers.call_provider(PROVIDERS["openai"], system="s", user="u", model="m")
    assert out == "hello"


def test_anthropic_shape_success(monkeypatch):
    monkeypatch.setenv(PROVIDERS["anthropic"].key_env, "sk-ant")
    monkeypatch.setattr(
        urllib.request, "urlopen",
        _urlopen_returning({"content": [{"type": "text", "text": "hi there"}]}),
    )
    out = providers.call_provider(PROVIDERS["anthropic"], system="s", user="u", model="m")
    assert out == "hi there"


def test_missing_key_fails_open():
    synthetic = Provider(
        name="synthetic", shape="openai", default_base_url="https://x/v1",
        key_env="ORGSMITH_TEST_KEY", default_model="m",
        base_url_env="ORGSMITH_TEST_BASE", model_env="ORGSMITH_TEST_MODEL",
    )
    assert providers.call_provider(synthetic, system="s", user="u", model="m") is None


def test_http_error_fails_open(monkeypatch):
    monkeypatch.setenv(PROVIDERS["openai"].key_env, "sk-test")

    def boom(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url, 500, "err", {}, io.BytesIO(b'{"error":{"message":"boom"}}')
        )

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert providers.call_provider(PROVIDERS["openai"], system="s", user="u", model="m") is None


def test_url_error_fails_open(monkeypatch):
    monkeypatch.setenv(PROVIDERS["openai"].key_env, "sk-test")

    def boom(req, timeout=None):
        raise urllib.error.URLError("no route to host")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert providers.call_provider(PROVIDERS["openai"], system="s", user="u", model="m") is None


def test_empty_response_fails_open(monkeypatch):
    monkeypatch.setenv(PROVIDERS["openai"].key_env, "sk-test")
    monkeypatch.setattr(urllib.request, "urlopen", _urlopen_returning({"choices": []}))
    assert providers.call_provider(PROVIDERS["openai"], system="s", user="u", model="m") is None


# --- --check preflight ------------------------------------------------------


def test_check_off_returns_zero(capsys):
    assert check(None) == 0
    assert "OFF" in capsys.readouterr().out


def test_check_selected_no_key_not_ready(monkeypatch):
    monkeypatch.setenv("ORGSMITH_AUTHOR_PROVIDER", "openai")
    monkeypatch.delenv(PROVIDERS["openai"].key_env, raising=False)
    assert check(None) == 1


def test_check_selected_ready(monkeypatch):
    monkeypatch.setenv("ORGSMITH_AUTHOR_PROVIDER", "openai")
    monkeypatch.setenv(PROVIDERS["openai"].key_env, "sk-test")
    assert check(None) == 0


def test_check_bogus_provider_errors(monkeypatch):
    monkeypatch.setenv("ORGSMITH_AUTHOR_PROVIDER", "bogus")
    assert check(None) == 2
