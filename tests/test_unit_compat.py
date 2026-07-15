"""Unit tier: schema evolution stays additive.

Old-shape artifacts (from before the M2 graph knobs, manifest mentions,
external-person affiliations, and the later knob families) must keep
loading, with new fields filling as inert defaults. dev-mini was the
committed old-shape oracle until its spec-sanctioned M6 regeneration;
synthetic artifacts now pin the contract instead.
"""

import pytest

from orgsmith.artifacts import load_charter, load_manifest
from orgsmith.paths import OrgPaths
from orgsmith.schemas import Charter, ExternalPerson, ManifestEntry

from conftest import REPO

pytestmark = pytest.mark.unit


OLD_MANIFEST_LINE = {
    # a v1 manifest entry: written before mentions, key_facts, authoring,
    # render_params, and rev existed
    "schema_id": "orgsmith/manifest-entry@1",
    "doc_id": "d:0001",
    "path": "Firm/Firm Overview 2020 v1.docx",
    "title": "Firm Overview",
    "genre": "company_overview",
    "format": "docx",
    "date": "2020-06-01",
    "authors": ["p:jane.doe"],
}

OLD_CHARTER = {
    # a v1 charter: written before the ambiguity knobs, services,
    # hard_cases, acl_posture, format transforms, and affiliations_in_docs
    "schema_id": "orgsmith/charter@1",
    "slug": "old-shape",
    "name": "Old Shape Advisors LLC",
    "seed": 1,
    "org_type": "consulting",
    "founded": 2018,
    "domain": "oldshapeadvisors.example",
    "headcount": {"Leadership": 1, "Consulting": 2},
    "doc_culture": {
        "target_docs": 2,
        "date_range": ["2019-01-01", "2020-01-01"],
        "format_mix": {"docx": 1, "pdf": 1},
    },
    "finance": {
        "base_revenue": 100000,
        "growth_rate": 0.1,
        "expense_ratio": 0.7,
    },
    "engagements": {"count": 1},
    "graph_targets": {"external_orgs": 1, "external_people": 1},
    "narrative": "An old-shape charter from before every knob family.",
}


def test_old_manifest_line_loads_with_defaults():
    entry = ManifestEntry.model_validate(OLD_MANIFEST_LINE)
    assert entry.schema_id == "orgsmith/manifest-entry@1"
    assert entry.mentions == []
    assert entry.key_facts == []
    assert entry.authoring == "batchable"
    assert entry.render_params == {}
    assert entry.rev == 0


def test_old_charter_loads_with_knob_defaults():
    charter = Charter.model_validate(OLD_CHARTER)
    gt = charter.graph_targets
    assert gt.min_mentions_per_person == 0
    assert gt.surname_collisions == 0
    assert gt.nickname_aliases == 0
    assert gt.multi_affiliations == 0
    assert gt.affiliations_in_docs is False
    assert charter.engagements.services == []
    assert charter.hard_cases.signature_page_facts == 0
    assert charter.hard_cases.filename_dates == 0
    assert charter.acl_posture == "open"
    culture = charter.doc_culture
    assert culture.format_mix.pptx == 0 and culture.format_mix.eml == 0
    assert culture.scanned_ratio == 0.0 and culture.legacy_ratio == 0.0


def test_old_external_person_loads_with_empty_affiliations():
    xp = ExternalPerson.model_validate(
        {
            "id": "xp:old.contact",
            "name": "Old Contact",
            "org": "x:client",
            "title": "COO",
            "email": "old.contact@client.example",
        }
    )
    assert xp.affiliations == []


TORCHLAKE = OrgPaths(root=REPO, slug="torchlake-engineering")


def test_m2_manifest_loads_with_body_location_defaults():
    """The committed pre-M3 fixture must keep loading; facts are all body."""
    entries = load_manifest(TORCHLAKE)
    assert entries, "committed torchlake manifest missing"
    for entry in entries:
        assert all(k.location == "body" for k in entry.key_facts)


def test_committed_charters_load_with_open_acl_posture():
    """The pre-M4 fixtures predate acl_posture; the default must be open
    and none of them may grow an ACL ledger without regeneration.
    (dev-mini left this list at its M6 regeneration: it now carries the
    derived overlay for its open posture.)"""
    for slug in ("torchlake-engineering", "quillbrook-appraisal"):
        paths = OrgPaths(root=REPO, slug=slug)
        assert load_charter(paths).acl_posture == "open"
        assert not paths.acl_json.exists()


def test_committed_charters_load_with_format_knob_defaults():
    """The pre-M5 fixtures predate the format knobs; defaults must be off
    and format_mix totals must still satisfy target_docs."""
    for slug in (
        "torchlake-engineering",
        "quillbrook-appraisal",
        "bramblewood-legal",
    ):
        charter = load_charter(OrgPaths(root=REPO, slug=slug))
        culture = charter.doc_culture
        assert culture.format_mix.pptx == 0, slug
        assert culture.format_mix.eml == 0, slug
        assert culture.scanned_ratio == 0.0, slug
        assert culture.legacy_ratio == 0.0, slug
        assert culture.ocr_layer_rate == 0.0, slug
        assert culture.format_mix.total == culture.target_docs, slug


def test_ocr_layer_rate_requires_scanned_ratio():
    from pydantic import ValidationError

    from orgsmith.schemas import DocCulture, FormatMix

    with pytest.raises(ValidationError, match="scanned_ratio"):
        DocCulture(
            target_docs=2,
            date_range=("2020-01-01", "2021-01-01"),
            format_mix=FormatMix(docx=1, pdf=1),
            ocr_layer_rate=0.5,
        )


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
