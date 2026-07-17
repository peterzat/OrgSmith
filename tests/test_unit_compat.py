"""Unit tier: schema evolution stays additive.

Old-shape artifacts (from before the M2 graph knobs, manifest mentions,
external-person affiliations, and the later knob families) must keep
loading, with new fields filling as inert defaults. dev-mini was the
committed old-shape oracle until its spec-sanctioned M6 regeneration;
synthetic artifacts now pin the contract instead.

M11b completed that migration. Three tests here read committed pre-M3/M4/M5
fixtures (torchlake, quillbrook, bramblewood) to assert the same defaults;
the v2.0 fleet reset retired those six fixtures, so those tests lost their
subject. They were not repointed at the new fleet, which would have been
vacuous: every surviving org was generated under the current schema and sets
these fields explicitly, so asserting "the default is open" against a
charter that literally says `acl_posture: open` proves nothing about
defaults. The synthetic OLD_CHARTER and OLD_MANIFEST_LINE below already
assert every contract those tests covered, and they are strictly better at
it -- they describe an artifact that genuinely omits the fields, and they
cannot rot when a fixture is regenerated. This is the same move dev-mini's
M6 regeneration made, one fleet later.
"""

import pytest

from orgsmith.schemas import Charter, ExternalPerson, ManifestEntry

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


def test_pre_m3_key_fact_defaults_to_body_location():
    """A key_fact written before `location` existed reads as body.

    Held by a committed pre-M3 fixture until M11b retired it. Stated
    synthetically instead: the point is an entry that OMITS the field, which
    no current fixture does -- every org the fleet now ships writes
    `location` explicitly, so a fixture-based version of this test would
    assert the serializer's output rather than the schema's default.
    """
    entry = ManifestEntry.model_validate(
        {
            **OLD_MANIFEST_LINE,
            # a v2 key_fact: fact_id only, before location policies existed
            "key_facts": [{"fact_id": "f:E-2020-001.fee"}],
        }
    )
    assert [k.location for k in entry.key_facts] == ["body"]


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
