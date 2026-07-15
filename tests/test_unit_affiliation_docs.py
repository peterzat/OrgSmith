"""Unit tier: the affiliations_in_docs knob and the RNG-free fabric
planting pass (charter dependency, determinism, both-sides designation,
covering participants, actionable failure, knob-off byte-identity)."""

import json

import pytest
from pydantic import ValidationError

from orgsmith.charter import parse_charter_md
from orgsmith.fabric.engagements import (
    LETTER_LEAD_DAYS,
    affiliation_covering,
    affiliation_plan,
    build_engagements,
    padded_window,
    xp_affiliations,
)
from orgsmith.foundation.scaffold import build_foundation
from orgsmith.paths import OrgPaths
from orgsmith.schemas import Affiliation, GraphTargets, dump_json

from conftest import REPO

pytestmark = pytest.mark.unit


def _charter(slug, **graph_target_updates):
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    charter = parse_charter_md(text, slug)
    if graph_target_updates:
        gt = charter.graph_targets.model_copy(update=graph_target_updates)
        charter = charter.model_copy(update={"graph_targets": gt})
    return charter


AFF_KNOBS = dict(multi_affiliations=1, affiliations_in_docs=True)


def _aff_org(slug="dev-mini"):
    charter = _charter(slug, **AFF_KNOBS)
    foundation = build_foundation(charter)
    return charter, foundation, build_engagements(charter, foundation)


def test_knob_requires_multi_affiliations():
    with pytest.raises(ValidationError, match="multi_affiliations"):
        GraphTargets(external_orgs=2, external_people=2, affiliations_in_docs=True)
    gt = GraphTargets(
        external_orgs=2,
        external_people=2,
        multi_affiliations=1,
        affiliations_in_docs=True,
    )
    assert gt.affiliations_in_docs


def test_knob_defaults_off_on_existing_schema_id():
    charter = _charter("dev-mini")
    assert charter.schema_id == "orgsmith/charter@1"
    assert charter.graph_targets.affiliations_in_docs is False


def test_xp_affiliations_implicit_and_explicit():
    _, foundation, _ = _aff_org()
    for xp in foundation.external_people:
        affs = xp_affiliations(xp)
        if xp.affiliations:
            assert affs == xp.affiliations
        else:
            assert affs == [Affiliation(org=xp.org)]
            assert affs[0].start is None and affs[0].end is None


def test_planting_is_deterministic():
    _, _, a = _aff_org()
    _, _, b = _aff_org()
    assert dump_json(a) == dump_json(b)


def test_multi_affiliation_person_designated_on_both_sides():
    charter, foundation, ledger = _aff_org()
    xp = next(p for p in foundation.external_people if p.affiliations)
    prior, current = xp.affiliations
    by_side = {prior.org: [], current.org: []}
    for eng in ledger.engagements:
        if xp.id in eng.external_participants and eng.client in by_side:
            by_side[eng.client].append(eng.id)
    assert by_side[prior.org], "no engagement under the prior employer"
    assert by_side[current.org], "no engagement under the current employer"


def test_participants_hold_covering_affiliations():
    charter, foundation, ledger = _aff_org()
    range_start = charter.doc_culture.date_range[0]
    people = {xp.id: xp for xp in foundation.external_people}
    for eng in ledger.engagements:
        lo, hi = padded_window(eng.start, eng.end, range_start)
        for xp_id in eng.external_participants:
            assert affiliation_covering(people[xp_id], eng.client, lo, hi), (
                f"{xp_id} has no affiliation to {eng.client} covering "
                f"{lo}..{hi} ({eng.id})"
            )


def test_reassignment_rebuilds_client_dependent_fields():
    charter, foundation, ledger = _aff_org()
    org_names = {o.id: o.name for o in foundation.external_orgs}
    for eng in ledger.engagements:
        client_name = org_names[eng.client]
        assert eng.title.endswith(f"for {client_name}")
        assert f"for {client_name}, running" in eng.summary
        fact = next(f for f in eng.facts if f.id == f"f:{eng.id}.client")
        assert fact.value == client_name and fact.rendered == client_name


def test_impossible_placement_fails_actionably():
    # torchlake's frozen seed genuinely cannot host both sides of its
    # multi-affiliation boundary; the failure must be actionable, at
    # fabric, before any model pass.
    charter = _charter("torchlake-engineering", affiliations_in_docs=True)
    foundation = build_foundation(charter)
    with pytest.raises(SystemExit, match="Widen doc_culture.date_range"):
        build_engagements(charter, foundation)


def test_plan_direct_failure_on_empty_windows():
    charter, foundation, _ = _aff_org()
    range_start = charter.doc_culture.date_range[0]
    with pytest.raises(SystemExit, match="affiliations_in_docs"):
        affiliation_plan(foundation, [], range_start)


@pytest.mark.parametrize("slug", ["dev-mini", "torchlake-engineering"])
def test_knob_off_reproduces_committed_engagements_ledger(slug):
    # The planting pass must not run, touch fields, or consume RNG when
    # the knob is off: the committed ledgers are the oracles. torchlake
    # is the load-bearing case: it is frozen with multi_affiliations: 1,
    # and a covering-affiliation pass would rewrite it.
    charter = _charter(slug)
    assert charter.graph_targets.affiliations_in_docs is False
    rebuilt = build_engagements(charter, build_foundation(charter))
    committed = (
        REPO / "companies" / f"{slug}-metadata" / "ledger" / "engagements.json"
    ).read_text("utf-8")
    assert dump_json(rebuilt) == committed


def test_letter_lead_days_shared_with_docplan(pure_org):
    # docplan dates the engagement letter start - LETTER_LEAD_DAYS
    # (clamped); the covering window must agree or a letter could be
    # signed by someone the ledger says works elsewhere on that date.
    from orgsmith.artifacts import load_engagements, load_manifest

    engagements = {e.id: e for e in load_engagements(pure_org).engagements}
    range_start = _charter("dev-mini").doc_culture.date_range[0]
    letters = [
        e for e in load_manifest(pure_org) if e.genre == "engagement_letter"
    ]
    assert letters
    for entry in letters:
        eng = engagements[entry.engagement]
        lo, _ = padded_window(eng.start, eng.end, range_start)
        assert entry.date == lo
