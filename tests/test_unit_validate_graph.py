"""Unit tier: MENT/GRAPH validator families and graceful skipping."""

import json
import shutil

import pytest

from orgsmith.acl import run_acl
from orgsmith.assemble import run_assemble
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.validate import run_validate

from conftest import REPO, base_recipe_text, build_knobbed_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def knobbed_org(tmp_path_factory):
    paths = build_knobbed_stages(tmp_path_factory.mktemp("knobbed"))
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    # ACL overlay (open posture: the recipe sets no acl_posture) so the
    # no-skip assertion below keeps meaning "every rule really ran".
    assert run_acl(paths) == 0
    return paths


@pytest.fixture()
def org_copy(knobbed_org, tmp_path):
    shutil.copytree(knobbed_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(knobbed_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=knobbed_org.slug)


def test_knobbed_org_validates_clean_with_all_rules(knobbed_org, capsys):
    assert run_validate(knobbed_org, as_json=True) == 0
    payload = json.loads(capsys.readouterr().out)
    for rule in ("MENT-01", "MENT-02", "GRAPH-01", "GRAPH-02",
                 "GRAPH-03", "GRAPH-04", "AFF-01", "AFF-02", "EML-01",
                 "EML-02", "EML-03", "DL-01", "SCAN-01", "SCAN-02"):
        assert rule in payload["rules_run"], rule
    # Every charter-gated rule must find its knob on here, with one
    # exception: legacy stays off because rendering it needs LibreOffice
    # and this org must build in CI.
    assert [s["rule"] for s in payload["skipped"]] == ["LEG-01"]


def test_pre_m2_org_skips_visibly(tmp_path, capsys):
    """The _needs_mentions grandfather outlives dev-mini's regeneration:
    a synthetic old-shape org (no mention knob, mention_map.json removed)
    still skips the mention rules visibly, never silently passing or
    failing."""
    dest = tmp_path / "recipes" / "dev-mini"
    dest.mkdir(parents=True)
    text = base_recipe_text()
    knob = "  min_mentions_per_person: 1\n"
    assert knob in text
    (dest / "ORG-CHARTER.md").write_text(text.replace(knob, ""))
    from conftest import build_pure_stages

    paths = build_pure_stages(tmp_path)
    paths.mention_map_json.unlink()
    rules = ["MENT-01", "MENT-02", "GRAPH-01", "GRAPH-02",
             "GRAPH-03", "GRAPH-04"]
    assert run_validate(paths, only=rules) == 0
    out = capsys.readouterr().out
    for rule in ("MENT-01", "MENT-02", "GRAPH-01", "GRAPH-02"):
        assert f"SKIP {rule}" in out, rule
    assert "SKIP GRAPH-03" not in out
    assert "SKIP GRAPH-04" not in out


def _edit_json(path, mutate):
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data, indent=2))


def test_tampered_surface_fails_ment_01(org_copy, capsys):
    def mutate(data):
        data["mentions"][0]["surface"] = "Nonexistent Q. Person"

    _edit_json(org_copy.mention_map_json, mutate)
    assert run_validate(org_copy) == 1
    assert "MENT-01" in capsys.readouterr().out


def test_unknown_entity_fails_ment_02(org_copy, capsys):
    def mutate(data):
        data["mentions"][0]["entity"] = "p:ghost.person"

    _edit_json(org_copy.mention_map_json, mutate)
    assert run_validate(org_copy) == 1
    assert "MENT-02" in capsys.readouterr().out


def test_erased_person_fails_coverage_and_orphan(org_copy, capsys):
    foundation = json.loads(org_copy.foundation_json.read_text())
    victim = foundation["people"][-1]["id"]

    def mutate(data):
        data["mentions"] = [
            m for m in data["mentions"] if m["entity"] != victim
        ]

    _edit_json(org_copy.mention_map_json, mutate)
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "GRAPH-01" in out
    assert "GRAPH-02" in out


def test_dangling_edge_fails_graph_03(org_copy, capsys):
    def mutate(data):
        data["edges"][0]["dst"] = "x:ghost-org"

    _edit_json(org_copy.graph_json, mutate)
    assert run_validate(org_copy) == 1
    assert "GRAPH-03" in capsys.readouterr().out


def test_missing_edge_fails_graph_04(org_copy, capsys):
    def mutate(data):
        idx = next(
            i for i, e in enumerate(data["edges"]) if e["kind"] == "reports_to"
        )
        del data["edges"][idx]

    _edit_json(org_copy.graph_json, mutate)
    assert run_validate(org_copy) == 1
    assert "GRAPH-04" in capsys.readouterr().out
