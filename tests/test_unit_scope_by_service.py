"""Unit tier: scope vocabulary follows the service line (SCOPE-A, M17d).

M17c planted one buy-side M&A profile on all eight of quillon-harbor's
engagements, so a Fairness Opinion carried a four-stage acquisition funnel and
a sell-side mandate counted "acquisition targets". `scope_by_service` gives a
service its own profile, or none at all.
"""

from __future__ import annotations

import json
import shutil

import pytest

from orgsmith.artifacts import load_charter, load_engagements, load_manifest
from orgsmith.charter import parse_charter_md
from orgsmith.fabric.engagements import engagement_service, scope_profile_for
from orgsmith.paths import OrgPaths
from orgsmith.validate import run_validate

from conftest import SCOPE_ANCHOR, SCOPE_LINES, base_recipe_text, build_pure_stages

pytestmark = pytest.mark.unit

SERVICES = "  services: [Buy-Side Search, Fairness Opinion, Capital Raise]\n"
BY_SERVICE = (
    "  scope_by_service:\n"
    "    Fairness Opinion: null\n"
    "    Capital Raise:\n"
    "      unit: investors\n"
    "      unit_range: [6, 12]\n"
    "      comparator: precedent raises\n"
    "      comparator_range: [10, 20]\n"
    "      pipeline: [investors approached, investors in diligence]\n"
    "      pipeline_top_range: [30, 50]\n"
    "      pipeline_retention: [0.3, 0.5]\n"
)


def _recipe(root, extra=BY_SERVICE):
    text = base_recipe_text()
    assert SCOPE_ANCHOR in text
    text = text.replace(SCOPE_ANCHOR, SCOPE_ANCHOR + SERVICES + SCOPE_LINES + extra)
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "ORG-CHARTER.md").write_text(text)


@pytest.fixture(scope="module")
def org(tmp_path_factory):
    root = tmp_path_factory.mktemp("by_service")
    _recipe(root)
    return build_pure_stages(root)


def _by_service(paths):
    charter = load_charter(paths)
    return {
        engagement_service(charter, e): e for e in load_engagements(paths).engagements
    }


def test_each_service_gets_its_own_vocabulary(org):
    engs = _by_service(org)
    assert set(engs) == {"Buy-Side Search", "Fairness Opinion", "Capital Raise"}
    counts = {
        service: {f.id.split(".", 1)[1]: f.rendered for f in e.facts if f.kind == "count"}
        for service, e in engs.items()
    }
    assert counts["Buy-Side Search"]["scope"].endswith(" positions")
    assert counts["Capital Raise"]["scope"].endswith(" investors")
    assert counts["Capital Raise"]["comparators"].endswith(" precedent raises")
    assert any(k.startswith("pipeline-investors-") for k in counts["Capital Raise"])
    # null: a fairness opinion has no deal funnel and gets no scope facts.
    assert counts["Fairness Opinion"] == {}


def test_no_document_cites_a_scope_fact_its_engagement_lacks(org):
    engs = {e.id: e for e in load_engagements(org).engagements}
    facts = {f.id for e in engs.values() for f in e.facts}
    fairness = next(e for s, e in _by_service(org).items() if s == "Fairness Opinion")
    for entry in load_manifest(org):
        assert set(entry.facts_refs) <= facts
        if entry.engagement == fairness.id:
            assert not any(r.endswith((".scope", ".comparators")) or ".pipeline-" in r
                           for r in entry.facts_refs)


def test_scope_01_recomputes_the_per_service_planting(org, capsys):
    capsys.readouterr()
    run_validate(org, as_json=True)
    report = json.loads(capsys.readouterr().out)
    assert "SCOPE-01" in report["rules_run"]
    assert not [f for f in report["findings"] if f["rule"] == "SCOPE-01"]


def test_scope_01_catches_a_funnel_planted_on_a_no_scope_service(org, tmp_path, capsys):
    shutil.copytree(org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(org.root / "companies", tmp_path / "companies")
    paths = OrgPaths(root=tmp_path, slug=org.slug)
    ledger = json.loads(paths.engagements_json.read_text())
    charter = load_charter(paths)
    for eng in ledger["engagements"]:
        if eng["title"].startswith("Fairness Opinion for "):
            eng["facts"].append(
                {"id": f"f:{eng['id']}.scope", "kind": "count", "value": 9,
                 "rendered": "9 positions", "location_policy": "body"}
            )
    paths.engagements_json.write_text(json.dumps(ledger, indent=2))
    capsys.readouterr()
    run_validate(paths, as_json=True)
    report = json.loads(capsys.readouterr().out)
    findings = [f for f in report["findings"] if f["rule"] == "SCOPE-01"]
    assert findings and "does not plant" in findings[0]["message"]
    assert charter.engagements.scope_by_service["Fairness Opinion"] is None


def test_the_brief_names_the_service_specific_noun(org):
    from conftest import run_enrichment
    from orgsmith.artifacts import load_work_order
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.state import load_state

    run_enrichment(org)
    prev = -1
    while True:
        assert run_next_batch(org) == 0
        n = len(load_state(org).author_batches)
        if n == prev:
            break
        prev = n
    capital = next(e for s, e in _by_service(org).items() if s == "Capital Raise")
    hints = [
        f.hint
        for ref in load_state(org).author_batches.values()
        for b in load_work_order(org.workorders_dir / ref.workorder).docs
        for f in b.facts
        if f.id == f"f:{capital.id}.scope"
    ]
    assert hints and all(h.startswith("count of investors;") for h in hints)


def test_an_unknown_service_key_is_rejected_at_parse(tmp_path):
    _recipe(tmp_path, BY_SERVICE.replace("Fairness Opinion: null", "Valuation: null"))
    text = (tmp_path / "recipes" / "dev-mini" / "ORG-CHARTER.md").read_text()
    with pytest.raises(Exception, match="not in engagements.services"):
        parse_charter_md(text, "dev-mini")


def test_without_scope_by_service_the_profile_is_the_recipe_wide_one(tmp_path):
    _recipe(tmp_path, extra="")
    paths = build_pure_stages(tmp_path)
    charter = load_charter(paths)
    for eng in load_engagements(paths).engagements:
        assert scope_profile_for(charter, eng) == charter.engagements.scope
