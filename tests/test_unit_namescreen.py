"""Unit tier: the real-firm name screen.

Normalization and matching semantics, generation gates (charter and
scaffold fail before any model pass), the NAME-01 rule in both
directions, committed-fleet cleanliness, and source-list hygiene.
"""

import json
import shutil

import pytest

from orgsmith.charter import run_charter
from orgsmith.foundation import run_scaffold
from orgsmith.namescreen import (
    FirmIndex,
    default_index,
    domain_key,
    load_firms,
    normalize,
    screen_charter,
    screen_foundation,
)
from orgsmith.artifacts import load_charter, load_foundation
from orgsmith.paths import OrgPaths
from orgsmith.validate import run_validate

from conftest import REPO, build_pure_stages

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "name,expected",
    [
        ("McKinsey & Company", ("mckinsey",)),
        ("Ernst & Young LLP", ("ernst", "young")),
        ("The Vanguard Group", ("vanguard", "group")),
        ("Foley Group", ("foley", "group")),
        ("Société Générale", ("societe", "generale")),
        ("K&L Gates", ("k", "l", "gates")),
        ("Greenhill & Co.", ("greenhill",)),
        ("Slaughter and May", ("slaughter", "may")),
        ("Cravath, Swaine & Moore", ("cravath", "swaine", "moore")),
        ("Company Inc", ()),
    ],
)
def test_normalization_table(name, expected):
    assert normalize(name) == expected


@pytest.mark.parametrize(
    "domain,expected",
    [
        ("mckinsey.com", "mckinsey"),
        ("Goldman-Sachs.COM", "goldmansachs"),
        ("someone@mckinsey.com", "mckinsey"),
        ("pinebrookadvisory.com", "pinebrookadvisory"),
    ],
)
def test_domain_key(domain, expected):
    assert domain_key(domain) == expected


def test_org_matching_exact_and_contiguous_run():
    idx = default_index()
    assert idx.match_org("McKinsey Group LLC") == "McKinsey & Company"
    assert idx.match_org("Morgan Stanley Advisors") == "Morgan Stanley"
    # a firm's tokens must appear contiguously, not merely be present
    assert idx.match_org("Stanley Morgan Advisors") is None
    # committed-fixture shapes must stay clean
    assert idx.match_org("Foley Group") is None
    assert idx.match_org("Perkins Group") is None
    assert idx.match_org("Franklin PLC") is None
    assert idx.match_org("Johnson PLC") is None


def test_person_matching_is_exact_only():
    idx = default_index()
    # the Morgan-Stanley-the-person class flags
    assert idx.match_person("Morgan Stanley") == "Morgan Stanley"
    # a person merely sharing a token with a firm does not
    assert idx.match_person("Sarah Morgan") is None
    assert idx.match_person("David Jones") is None


def test_domain_matching():
    idx = default_index()
    assert idx.match_domain("mckinsey.io") == "McKinsey & Company"
    assert idx.match_domain("pinebrookadvisory.com") is None


def test_committed_fleet_screens_clean():
    metadata_dirs = sorted(REPO.glob("companies/*-metadata"))
    assert len(metadata_dirs) >= 6
    for d in metadata_dirs:
        paths = OrgPaths(root=REPO, slug=d.name[: -len("-metadata")])
        problems = screen_charter(load_charter(paths)) + screen_foundation(
            load_foundation(paths)
        )
        assert problems == [], f"{paths.slug}: {problems}"


def test_source_list_hygiene():
    firms = load_firms()
    assert 150 <= len(firms) <= 300
    normalized = [normalize(f) for f in firms]
    assert () not in normalized, "an entry normalizes to nothing"
    assert len(set(normalized)) == len(normalized), "duplicate entries"


def test_custom_index_is_isolated():
    idx = FirmIndex(["Acme & Co"])
    assert idx.match_org("Acme Widgets LLC") == "Acme & Co"
    assert idx.match_org("McKinsey Group") is None


def test_charter_gate_blocks_colliding_name(tmp_path, capsys):
    dest = tmp_path / "recipes" / "dev-mini"
    dest.mkdir(parents=True)
    text = (REPO / "recipes" / "dev-mini" / "ORG-CHARTER.md").read_text()
    assert "Pinebrook Advisory Group LLC" in text
    text = text.replace(
        "Pinebrook Advisory Group LLC", "Morgan Stanley Advisory Group LLC"
    )
    (dest / "ORG-CHARTER.md").write_text(text)
    paths = OrgPaths(root=tmp_path, slug="dev-mini")
    with pytest.raises(SystemExit, match="name screen failed"):
        run_charter(paths)
    assert "collides with real firm 'Morgan Stanley'" in capsys.readouterr().out
    assert not paths.charter_json.exists(), "gate must fire before writing"


def test_scaffold_gate_blocks_colliding_foundation(tmp_path, capsys, monkeypatch):
    # Generated names are seed-dependent, so force a hit through the same
    # entry point run_scaffold consults; the wiring under test is that the
    # gate fires before foundation.json is written.
    dest = tmp_path / "recipes" / "dev-mini"
    dest.mkdir(parents=True)
    shutil.copytree(
        REPO / "recipes" / "dev-mini", dest, dirs_exist_ok=True
    )
    paths = OrgPaths(root=tmp_path, slug="dev-mini")
    assert run_charter(paths) == 0

    import orgsmith.foundation.scaffold as scaffold

    monkeypatch.setattr(
        scaffold,
        "screen_foundation",
        lambda _f: [("person p:x name 'Morgan Stanley' collides with real "
                     "firm 'Morgan Stanley'", "foundation.json")],
    )
    with pytest.raises(SystemExit, match="bump the seed"):
        run_scaffold(paths)
    assert not paths.foundation_json.exists(), "gate must fire before writing"


def test_name01_clean_and_never_skipped(pure_org, capsys):
    assert run_validate(pure_org, only=["NAME-01"]) == 0
    assert "SKIP" not in capsys.readouterr().out


def _corrupt_foundation(pure_org, tmp_path, mutate):
    shutil.copytree(pure_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(pure_org.root / "companies", tmp_path / "companies")
    paths = OrgPaths(root=tmp_path, slug=pure_org.slug)
    data = json.loads(paths.foundation_json.read_text("utf-8"))
    mutate(data)
    paths.foundation_json.write_text(json.dumps(data), "utf-8")
    return paths


def test_name01_fails_colliding_person(pure_org, tmp_path, capsys):
    def mutate(data):
        data["people"][0]["name"] = "Morgan Stanley"

    paths = _corrupt_foundation(pure_org, tmp_path, mutate)
    assert run_validate(paths, only=["NAME-01"]) == 1
    assert "collides with real firm" in capsys.readouterr().out


def test_name01_fails_colliding_external_org(pure_org, tmp_path, capsys):
    def mutate(data):
        data["external_orgs"][0]["name"] = "McKinsey Group LLC"

    paths = _corrupt_foundation(pure_org, tmp_path, mutate)
    assert run_validate(paths, only=["NAME-01"]) == 1
    assert "collides with real firm" in capsys.readouterr().out
