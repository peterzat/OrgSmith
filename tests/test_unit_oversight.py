"""Unit tier: a senior oversees every engagement one can cover (M17d,
`engagements.oversight_titles`).

M17c's board found no partner in any quillon-harbor engagement document after
2015 and none able to read a later mandate, while one promised to "be at every
session". Staffing drew teams uniformly from the delivery department with no
notion of seniority; this is the post-pass that fixes it without moving that
draw.
"""

from __future__ import annotations

import json
import shutil

import pytest

from orgsmith.artifacts import load_charter, load_engagements, load_foundation, load_manifest
from orgsmith.charter import parse_charter_md
from orgsmith.fabric.engagements import oversight_candidates
from orgsmith.paths import OrgPaths
from orgsmith.validate import run_validate

from conftest import SCOPE_ANCHOR, base_recipe_text, build_pure_stages

pytestmark = pytest.mark.unit

TITLES = "  oversight_titles: [Principal Consultant]\n"


def _build(root, lines=TITLES):
    text = base_recipe_text()
    assert SCOPE_ANCHOR in text
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "ORG-CHARTER.md").write_text(text.replace(SCOPE_ANCHOR, SCOPE_ANCHOR + lines))
    return build_pure_stages(root)


@pytest.fixture(scope="module")
def plain(tmp_path_factory):
    return build_pure_stages(tmp_path_factory.mktemp("plain"))


@pytest.fixture(scope="module")
def overseen(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("overseen"))


def test_every_coverable_engagement_carries_a_senior(overseen):
    charter, foundation = load_charter(overseen), load_foundation(overseen)
    for eng in load_engagements(overseen).engagements:
        eligible = {p.id for p in oversight_candidates(charter, foundation, eng)}
        assert eligible, "the fixture should leave every engagement coverable"
        assert eligible & set(eng.internal_participants), eng.id


def test_the_lead_and_the_drawn_team_do_not_move(plain, overseen):
    """A post-pass appends; it never replaces the lead or reorders the team,
    so the staffing draw and the documents the lead owns are unchanged."""
    before = {e.id: e.internal_participants for e in load_engagements(plain).engagements}
    for eng in load_engagements(overseen).engagements:
        assert eng.internal_participants[: len(before[eng.id])] == before[eng.id]
        assert len(eng.internal_participants) - len(before[eng.id]) in (0, 1)


def test_the_senior_reaches_the_engagements_documents(overseen):
    charter, foundation = load_charter(overseen), load_foundation(overseen)
    engs = {e.id: e for e in load_engagements(overseen).engagements}
    seniors = {p.id for e in engs.values() for p in oversight_candidates(charter, foundation, e)}
    reached = {
        p
        for entry in load_manifest(overseen)
        if entry.engagement
        for p in entry.participants
        if p in seniors
    }
    assert reached, "no engagement document plans its senior as a participant"


def test_knob_off_changes_no_team(plain, tmp_path):
    again = build_pure_stages(tmp_path)
    assert [e.model_dump() for e in load_engagements(again).engagements] == [
        e.model_dump() for e in load_engagements(plain).engagements
    ]


def _ovr(paths, capsys):
    capsys.readouterr()
    run_validate(paths, as_json=True)
    return json.loads(capsys.readouterr().out)


def test_ovr_01_passes_and_catches_a_stripped_senior(overseen, tmp_path, capsys):
    report = _ovr(overseen, capsys)
    assert "OVR-01" in report["rules_run"]
    assert not [f for f in report["findings"] if f["rule"] == "OVR-01"]

    shutil.copytree(overseen.root / "recipes", tmp_path / "recipes")
    shutil.copytree(overseen.root / "companies", tmp_path / "companies")
    paths = OrgPaths(root=tmp_path, slug=overseen.slug)
    charter, foundation = load_charter(paths), load_foundation(paths)
    ledger = json.loads(paths.engagements_json.read_text())
    first = load_engagements(paths).engagements[0]
    seniors = {p.id for p in oversight_candidates(charter, foundation, first)}
    ledger["engagements"][0]["internal_participants"] = [
        p for p in ledger["engagements"][0]["internal_participants"] if p not in seniors
    ]
    paths.engagements_json.write_text(json.dumps(ledger, indent=2))
    findings = [f for f in _ovr(paths, capsys)["findings"] if f["rule"] == "OVR-01"]
    assert findings and findings[0]["target"] == first.id


def test_ovr_01_skips_visibly_when_the_knob_is_off(plain, capsys):
    report = _ovr(plain, capsys)
    assert "OVR-01" not in report["rules_run"]
    (skip,) = [s for s in report["skipped"] if s["rule"] == "OVR-01"]
    assert "oversight_titles" in skip["reason"]


def test_an_oversight_title_no_one_can_hold_is_rejected_at_parse():
    """A typo would leave the knob on, nobody eligible, and OVR-01 passing
    vacuously; it has to fail at the charter stage instead."""
    text = base_recipe_text().replace(
        SCOPE_ANCHOR, SCOPE_ANCHOR + "  oversight_titles: [Managing Partners]\n"
    )
    with pytest.raises(Exception, match="no staff member can hold: Managing Partners"):
        parse_charter_md(text, "dev-mini")
