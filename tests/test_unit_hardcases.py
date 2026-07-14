"""Unit tier: hard-case planting (non-body location policies).

Covers the planting engine (fabric policy assignment, docplan placement and
its over-demand gate). End-to-end enforcement (ingest, render, validator)
is covered in test_unit_validate_loc.py.
"""

from pathlib import PurePosixPath

import pytest

from orgsmith.artifacts import load_engagements, load_manifest
from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.fabric import run_fabric
from orgsmith.foundation import run_scaffold

from conftest import build_hardcase_stages, write_hardcase_recipe

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def hard_org(tmp_path_factory):
    return build_hardcase_stages(tmp_path_factory.mktemp("hard-org"))


def test_knobs_off_plants_only_body_facts(pure_org):
    facts = load_engagements(pure_org).fact_index()
    assert all(f.location_policy == "body" for f in facts.values())
    assert not any(f.id.endswith(".minutes-date") for f in facts.values())
    for entry in load_manifest(pure_org):
        assert all(k.location == "body" for k in entry.key_facts)


def test_signature_page_fee_planted_in_letter_only(hard_org):
    facts = load_engagements(hard_org).fact_index()
    sig_facts = [f for f in facts.values() if f.location_policy == "signature_page"]
    assert len(sig_facts) == 1
    fee = sig_facts[0]
    assert fee.id.endswith(".fee")

    manifest = load_manifest(hard_org)
    hosts = [
        e
        for e in manifest
        if any(k.fact_id == fee.id and k.location == "signature_page"
               for k in e.key_facts)
    ]
    assert len(hosts) == 1
    letter = hosts[0]
    assert letter.genre == "engagement_letter"
    assert letter.format == "pdf"
    assert letter.render_params.get("sig_fact") == fee.id
    # The fee may not be referenced by any other document.
    others = [e for e in manifest if e.doc_id != letter.doc_id]
    assert all(fee.id not in e.facts_refs for e in others)


def test_filename_date_fact_matches_minutes_filename(hard_org):
    facts = load_engagements(hard_org).fact_index()
    fn_facts = [f for f in facts.values() if f.location_policy == "filename"]
    assert len(fn_facts) == 1
    md = fn_facts[0]
    assert md.id.endswith(".minutes-date")
    assert md.kind == "date"

    manifest = load_manifest(hard_org)
    hosts = [
        e
        for e in manifest
        if any(k.fact_id == md.id and k.location == "filename"
               for k in e.key_facts)
    ]
    assert len(hosts) == 1
    minutes = hosts[0]
    assert minutes.genre == "meeting_minutes"
    assert md.rendered in PurePosixPath(minutes.path).name
    # Never in facts_refs anywhere: FACT-01 would demand body presence.
    assert all(md.id not in e.facts_refs for e in manifest)


def test_over_demand_fails_at_docplan_with_actionable_message(tmp_path):
    paths = write_hardcase_recipe(tmp_path, sig=99, fn=0)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    with pytest.raises(SystemExit, match="lower the knob"):
        run_docplan(paths)
