"""The M9 genre registry: document supply is driven by the firm's activity,
the fixed-skeleton caps are gone, and the registry is the single declarative
source -- removing a row removes its documents, adding one (using an existing
driver, as pure data) adds them, with no other planner edit."""

from collections import Counter
from datetime import date

import pytest

from orgsmith.docplan import planner as planner_mod
from orgsmith.docplan.planner import build_manifest
from orgsmith.docplan.registry import REGISTRY, GenreRule
from orgsmith.fabric.engagements import build_engagements
from orgsmith.fabric.finance import build_finance
from orgsmith.foundation.scaffold import build_foundation
from orgsmith.schemas import (
    Charter,
    DocCulture,
    EngagementPlan,
    FinanceProfile,
    FormatMix,
    GraphTargets,
    RosterChurn,
)

pytestmark = pytest.mark.unit


def _charter(**over):
    """A synthetic charter, deliberately not a committed recipe."""
    base = dict(
        slug="synth",
        name="Synthetic Partners LLC",
        seed=4242,
        org_type="consulting",
        founded=2014,
        domain="synth.example",
        headcount={"Leadership": 1, "Consulting": 4},
        titles={
            "Leadership": ["Managing Partner"],
            "Consulting": ["Director", "Senior Associate", "Consultant", "Analyst"],
        },
        doc_culture=DocCulture(
            target_docs=11,
            date_range=(date(2016, 1, 1), date(2023, 12, 31)),
            format_mix=FormatMix(docx=7, pdf=2, xlsx=2),
        ),
        finance=FinanceProfile(base_revenue=1_000_000, growth_rate=0.1, expense_ratio=0.7),
        engagements=EngagementPlan(count=3),
        graph_targets=GraphTargets(external_orgs=3, external_people=3),
        # Rotation/churn off: supply, not staffing, is what these assert.
        roster_churn=RosterChurn(departures=0, promotions=0),
        narrative="A synthetic firm used only by tests.",
    )
    base.update(over)
    return Charter(**base)


def _build(charter):
    foundation = build_foundation(charter)
    finance = build_finance(charter, foundation)
    engagements = build_engagements(charter, foundation)
    manifest = build_manifest(charter, foundation, finance, engagements)
    return manifest, engagements.engagements, finance


def _expected_summaries(charter, finance):
    lo, hi = charter.doc_culture.date_range
    return sum(1 for y in finance.years if lo <= date(y.year + 1, 1, 15) <= hi)


def test_caps_are_gone_every_engagement_gets_its_recurring_docs():
    """The old skeleton gave kickoffs to the first two engagements and status
    reports to the first and last. Now every engagement gets both."""
    charter = _charter(engagements=EngagementPlan(count=3))
    manifest, engs, _ = _build(charter)
    for eng in engs:
        docs = [e for e in manifest if e.engagement == eng.id]
        genres = {e.genre for e in docs}
        assert sum(1 for e in docs if e.genre == "engagement_letter") == 1, eng.id
        assert "kickoff_memo" in genres, eng.id
        assert "status_report" in genres, eng.id
        assert "meeting_minutes" in genres, eng.id


def test_financial_summary_covers_every_in_range_fiscal_year():
    """The last-two-years cap is gone: a summary per in-range fiscal year."""
    charter = _charter()
    manifest, _, finance = _build(charter)
    got = sum(1 for e in manifest if e.genre == "financial_summary")
    assert got == _expected_summaries(charter, finance) >= 3


def test_more_engagements_yield_more_engagement_documents():
    small, _, _ = _build(_charter(engagements=EngagementPlan(count=2)))
    big, _, _ = _build(_charter(engagements=EngagementPlan(count=5)))
    small_eng = sum(1 for e in small if e.engagement is not None)
    big_eng = sum(1 for e in big if e.engagement is not None)
    assert big_eng > small_eng


def test_a_longer_span_yields_more_periodic_documents():
    short, _, _ = _build(_charter(doc_culture=DocCulture(
        target_docs=11, date_range=(date(2020, 1, 1), date(2022, 12, 31)),
        format_mix=FormatMix(docx=7, pdf=2, xlsx=2))))
    long, _, _ = _build(_charter(doc_culture=DocCulture(
        target_docs=11, date_range=(date(2015, 1, 1), date(2023, 12, 31)),
        format_mix=FormatMix(docx=7, pdf=2, xlsx=2))))
    periodic = ("financial_summary", "company_overview")
    n_short = sum(1 for e in short if e.genre in periodic)
    n_long = sum(1 for e in long if e.genre in periodic)
    assert n_long > n_short


def test_the_old_fixed_skeleton_identity_no_longer_holds():
    """`2E + 7` was the pre-M9 count. It must not be the count now."""
    charter = _charter(engagements=EngagementPlan(count=3))
    manifest, engs, _ = _build(charter)
    assert len(manifest) != 2 * len(engs) + 7


def test_per_hire_genre_lands_an_onboarding_record_in_a_new_folder():
    """A driver the fixed skeleton could not express: one onboarding record
    per person who joined after the window opened, in a People/ folder no
    prior genre used."""
    charter = _charter(roster_churn=RosterChurn(departures=1, promotions=0))
    manifest, _, _ = _build(charter)
    onb = [e for e in manifest if e.genre == "onboarding_record"]
    assert onb, "a backfill hire should get an onboarding record"
    for e in onb:
        assert e.path.startswith("People/")
        assert e.facts_refs == []
        assert len(e.participants) == 1  # the new hire, named
    assert "People" in {e.path.split("/")[0] for e in manifest}


def test_onboarding_count_matches_the_number_of_mid_range_joiners():
    """The driver is exact: one record per person who joined after the window
    opened, whichever way they joined (the scaffold's late joiner or a churn
    backfill)."""
    charter = _charter(roster_churn=RosterChurn(departures=1, promotions=0))
    manifest, _, _ = _build(charter)
    lo, _ = charter.doc_culture.date_range
    joiners = [p for p in build_foundation(charter).people if p.employment.start > lo]
    onb = [e for e in manifest if e.genre == "onboarding_record"]
    assert len(onb) == len(joiners) >= 1


def test_per_hire_at_minimum_roster_degrades_without_crashing():
    """At the smallest roster a recipe can host, per_hire still produces a
    coherent record for the lone mid-range joiner rather than crashing."""
    charter = _charter(
        headcount={"Leadership": 1, "Consulting": 1},
        titles={"Leadership": ["Managing Partner"], "Consulting": ["Analyst"]},
        engagements=EngagementPlan(count=1),
        graph_targets=GraphTargets(external_orgs=1, external_people=1),
        roster_churn=RosterChurn(departures=0, promotions=0),
    )
    manifest, _, _ = _build(charter)
    assert manifest, "minimum roster still yields a non-empty plan"
    for e in (x for x in manifest if x.genre == "onboarding_record"):
        assert e.path.startswith("People/")
        assert e.facts_refs == [] and len(e.participants) == 1


def test_registry_lengths_are_realistic_and_the_brief_sources_them():
    """M9: word targets live in the registry and were raised to real-world
    lengths. The authoring brief reads that one table, not a second copy."""
    from orgsmith.authoring.contexts import _TARGET_WORDS

    letter = next(r for r in REGISTRY if r.genre == "engagement_letter")
    assert 800 <= letter.target_words <= 1500
    assert _TARGET_WORDS["engagement_letter"] == letter.target_words
    # Every authored genre was raised off the old 130-350 band.
    authored = [r for r in REGISTRY if r.authoring == "batchable"]
    assert authored and all(r.target_words >= 250 for r in authored)


def test_registry_is_declarative_removing_a_row_removes_its_docs(monkeypatch):
    charter = _charter()
    full, _, _ = _build(charter)
    assert any(e.genre == "status_report" for e in full)
    trimmed = tuple(r for r in REGISTRY if r.genre != "status_report")
    monkeypatch.setattr(planner_mod, "REGISTRY", trimmed)
    without, _, _ = _build(charter)
    assert not any(e.genre == "status_report" for e in without)
    assert len(without) < len(full)


def test_registry_is_declarative_adding_a_row_adds_docs(monkeypatch):
    """A new row using an existing driver is pure data: no planner edit."""
    charter = _charter()
    full, _, _ = _build(charter)
    extra = GenreRule(
        genre="kickoff_memo",  # a valid Genre literal; its own filename/title
        driver="per_engagement",
        format="docx",
        folder="Engagements/{client}",
        fact_suffixes=("client",),
        start_offset_days=5,
        title_prefix="Planning Note",
        filename="{date:%Y.%m.%d} - Planning Note - {client}.docx",
    )
    monkeypatch.setattr(planner_mod, "REGISTRY", REGISTRY + (extra,))
    more, engs, _ = _build(charter)
    assert len(more) == len(full) + len(engs)
