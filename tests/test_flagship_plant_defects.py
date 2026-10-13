"""Flagship tier: the planted-defect recall probe's tool (M17d).

Reads the committed `calderwood-partners` and writes only to tmp. Lives in
the flagship tier because calderwood does: copying it twice is the cost.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from orgsmith.paths import OrgPaths
from orgsmith.review.digest import org_digest

from conftest import REPO

pytestmark = [pytest.mark.org, pytest.mark.flagship]

SLUG = "calderwood-partners"


def _tool():
    spec = importlib.util.spec_from_file_location("plant_defects", REPO / "tools" / "plant_defects.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    tool = _tool()
    tmp = tmp_path_factory.mktemp("recall")
    before = org_digest(OrgPaths(root=REPO, slug=SLUG))
    answer = tool.build(SLUG, REPO, tmp / "out", tmp / "key.json", seed=7, small=50)
    return tool, tmp, answer, before


def test_the_committed_org_is_untouched(built):
    *_, before = built
    assert org_digest(OrgPaths(root=REPO, slug=SLUG)) == before


def test_every_plant_lands_once_in_both_copies(built):
    tool, tmp, answer, _ = built
    plants = answer["plants"]
    assert len(plants) == len(tool.PLANTS) and len({p["doc_id"] for p in plants}) == len(plants)
    for name in ("small", "large"):
        paths = OrgPaths(root=tmp / "out" / name, slug=SLUG)
        for plant in plants:
            text = (paths.docir_dir / f"{plant['doc_id'].replace(':', '')}.json").read_text()
            assert text.count(plant["sentence"]) == 1


def test_anachronisms_land_only_where_they_are_unambiguous(built):
    tool, _, answer, _ = built
    since = {t: s for _, _, t, s in tool.PLANTS}
    for plant in answer["plants"]:
        if plant["kind"] == "anachronism":
            year = int(plant["date"][:4])
            assert year <= since[plant["token"]] - tool.ANACHRONISM_MARGIN_YEARS


def test_both_reading_lists_carry_every_plant(built):
    _, tmp, answer, _ = built
    planted = {p["doc_id"] for p in answer["plants"]}
    sizes = {}
    for name in ("small", "large"):
        sample = json.loads((tmp / "out" / name / "companies" / f"{SLUG}-metadata" / "review" / "sample.json").read_text())
        ids = {d["doc_id"] for d in sample["docs"]}
        assert planted <= ids
        sizes[name] = len(ids)
    assert sizes["small"] == 50 and sizes["large"] > 3 * sizes["small"]


def test_no_prior_board_output_reaches_a_copy(built):
    _, tmp, _, _ = built
    meta = tmp / "out" / "small" / "companies" / f"{SLUG}-metadata"
    assert not (meta / "workorders").exists()
    assert sorted(p.name for p in (meta / "review").iterdir()) == ["sample.json"]


def test_placement_is_deterministic(built, tmp_path):
    tool, _, answer, _ = built
    again = tool.choose(OrgPaths(root=REPO, slug=SLUG), seed=7)
    assert again == answer["plants"]
