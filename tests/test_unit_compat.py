"""Unit tier: schema evolution stays additive.

The committed v1 dev-mini org predates the M2 fields (graph knobs, manifest
mentions/key_facts, external-person affiliations). Its artifacts must keep
loading unchanged; new fields must fill with inert defaults.
"""

import pytest

from orgsmith.artifacts import load_charter, load_foundation, load_manifest
from orgsmith.paths import OrgPaths

from conftest import REPO

pytestmark = pytest.mark.unit

DEV_MINI = OrgPaths(root=REPO, slug="dev-mini")


def test_v1_manifest_lines_load_with_defaults():
    entries = load_manifest(DEV_MINI)
    assert entries, "committed dev-mini manifest missing"
    for entry in entries:
        assert entry.schema_id == "orgsmith/manifest-entry@1"
        assert entry.mentions == []
        assert entry.key_facts == []


def test_v1_charter_loads_with_knob_defaults():
    charter = load_charter(DEV_MINI)
    gt = charter.graph_targets
    assert gt.min_mentions_per_person == 0
    assert gt.surname_collisions == 0
    assert gt.nickname_aliases == 0
    assert gt.multi_affiliations == 0
    assert charter.engagements.services == []


def test_v1_foundation_loads_with_empty_affiliations():
    foundation = load_foundation(DEV_MINI)
    assert all(xp.affiliations == [] for xp in foundation.external_people)


TORCHLAKE = OrgPaths(root=REPO, slug="torchlake-engineering")


def test_m2_manifest_loads_with_body_location_defaults():
    """Both pre-M3 fixtures must keep loading; their facts are all body."""
    for paths in (DEV_MINI, TORCHLAKE):
        entries = load_manifest(paths)
        assert entries, f"committed {paths.slug} manifest missing"
        for entry in entries:
            assert all(k.location == "body" for k in entry.key_facts)


def test_location_policies_round_trip():
    from orgsmith.schemas import Fact, KeyFact

    for policy in ("body", "signature_page", "filename"):
        fact = Fact(
            id="f:E-2020-001.fee",
            kind="money",
            value=10000,
            rendered="$10,000",
            location_policy=policy,
        )
        assert Fact.model_validate(fact.model_dump()).location_policy == policy
        kf = KeyFact(fact_id="f:E-2020-001.fee", location=policy)
        assert KeyFact.model_validate(kf.model_dump()).location == policy
