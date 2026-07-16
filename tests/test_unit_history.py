"""Unit tier: the fabric's time dimension (M8).

Title history and its date resolver. Churn, rotation, and behavioral
finance join this module as they land.
"""

from datetime import date

import pytest
from pydantic import ValidationError

from orgsmith.artifacts import load_foundation
from orgsmith.authoring.contexts import _brief_person
from orgsmith.foundation.scaffold import build_foundation
from orgsmith.schemas import (
    Charter,
    DocCulture,
    EmploymentSpan,
    EngagementPlan,
    FinanceProfile,
    FormatMix,
    GraphTargets,
    Person,
    RosterChurn,
    TitleSpan,
)

from conftest import build_pure_stages

pytestmark = pytest.mark.unit


def _person(title: str = "Senior Associate", history=None) -> Person:
    return Person(
        id="p:rey.strong",
        name="Rey Strong",
        title=title,
        dept="Advisory",
        reports_to="p:boss",
        employment=EmploymentSpan(start=date(2019, 3, 1)),
        email="rey@example.com",
        phone="555-0100",
        title_history=history or [],
    )


def test_empty_history_resolves_to_title_for_every_date():
    """Most of a roster is never promoted and carries no history. The scalar
    stays the answer, which is what lets a hand-built Person and a synthetic
    charter work without inventing spans."""
    p = _person()
    assert p.title_history == []
    for when in (date(1990, 1, 1), date(2019, 3, 1), date(2050, 12, 31)):
        assert p.title_at(when) == "Senior Associate"


def test_promotion_resolves_the_title_held_on_the_date():
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2021, 6, 30)),
            TitleSpan(
                title="Senior Associate", start=date(2021, 7, 1), end=date(2024, 1, 31)
            ),
            TitleSpan(title="Director", start=date(2024, 2, 1)),
        ],
    )
    assert p.title_at(date(2020, 5, 1)) == "Analyst"
    assert p.title_at(date(2022, 9, 15)) == "Senior Associate"
    assert p.title_at(date(2025, 1, 1)) == "Director"
    # Person.title is the latest, and the last span mirrors it.
    assert p.title == p.title_history[-1].title == p.title_at(date(2025, 6, 1))


def test_span_boundaries_are_inclusive_on_both_ends():
    """Off-by-one here would brief the wrong title on exactly the day a
    promotion lands, which is the case a reviewer checks first."""
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2021, 6, 30)),
            TitleSpan(title="Director", start=date(2021, 7, 1)),
        ],
    )
    assert p.title_at(date(2019, 3, 1)) == "Analyst"
    assert p.title_at(date(2021, 6, 30)) == "Analyst"
    assert p.title_at(date(2021, 7, 1)) == "Director"


def test_date_outside_every_span_falls_back_to_title():
    """Mirrors employer_at: a resolver that raised on a gap or a pre-hire date
    would push a case the ledger cannot produce onto every caller."""
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2021, 6, 30)),
            # Deliberate gap: 2021-07-01 .. 2021-07-31 is covered by no span.
            TitleSpan(title="Director", start=date(2021, 8, 1)),
        ],
    )
    assert p.title_at(date(2015, 1, 1)) == "Director"  # before the first span
    assert p.title_at(date(2021, 7, 15)) == "Director"  # inside the gap


def test_first_matching_span_wins_when_spans_overlap():
    """Overlap is malformed and the ledger should never emit it, but the
    resolver must still be a function rather than order-dependent luck."""
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2022, 1, 1)),
            TitleSpan(title="Director", start=date(2021, 1, 1)),
        ],
    )
    assert p.title_at(date(2021, 6, 1)) == "Analyst"


def test_title_span_rejects_end_at_or_before_start():
    with pytest.raises(ValidationError, match="title span end must follow start"):
        TitleSpan(title="Analyst", start=date(2021, 1, 1), end=date(2021, 1, 1))
    with pytest.raises(ValidationError, match="title span end must follow start"):
        TitleSpan(title="Analyst", start=date(2021, 6, 1), end=date(2021, 1, 1))


def test_brief_resolves_the_title_held_on_the_document_date(tmp_path):
    """The criterion: an earlier document briefs the earlier title. Built on
    a real derived org and a promotion planted into it, so this exercises the
    path run_next_batch actually takes rather than a hand-made Person."""
    paths = build_pure_stages(tmp_path)
    foundation = load_foundation(paths)
    p = next(x for x in foundation.people if x.reports_to is not None)
    promoted_on = date(2022, 1, 1)
    p.title = "Principal"
    p.title_history = [
        TitleSpan(
            title="Associate", start=p.employment.start, end=date(2021, 12, 31)
        ),
        TitleSpan(title="Principal", start=promoted_on),
    ]

    before = _brief_person(foundation, p.id, date(2020, 6, 1))
    after = _brief_person(foundation, p.id, date(2023, 6, 1))
    assert before.title == "Associate"
    assert after.title == "Principal"
    # Everything else about the person is era-invariant.
    assert before.name == after.name and before.dept == after.dept


def test_brief_title_scoping_does_not_depend_on_the_affiliations_knob(tmp_path):
    """affiliations_in_docs is a hard-case planting knob for external
    employers. Only fernhollow sets it, so gating title resolution on it
    would leave the anachronism in place for every other recipe -- which is
    what `brief_at` did before M8."""
    paths = build_pure_stages(tmp_path)
    foundation = load_foundation(paths)
    p = next(x for x in foundation.people if x.reports_to is not None)
    p.title = "Principal"
    p.title_history = [
        TitleSpan(title="Associate", start=p.employment.start, end=date(2021, 12, 31)),
        TitleSpan(title="Principal", start=date(2022, 1, 1)),
    ]
    for historical_employer in (False, True):
        brief = _brief_person(foundation, p.id, date(2020, 6, 1), historical_employer)
        assert brief.title == "Associate"


# --- roster churn ----------------------------------------------------------


def _charter(**over):
    """A synthetic charter. Deliberately not dev-mini: these assert the knob's
    contract at boundaries no committed recipe sits on."""
    base = dict(
        slug="synth",
        name="Synthetic Partners LLC",
        seed=4242,
        org_type="consulting",
        founded=2015,
        domain="synth.example",
        headcount={"Leadership": 1, "Consulting": 3},
        titles={"Leadership": ["Managing Partner"],
                "Consulting": ["Director", "Senior Associate", "Analyst"]},
        doc_culture=DocCulture(
            target_docs=11,
            date_range=(date(2016, 1, 1), date(2023, 12, 31)),
            format_mix=FormatMix(docx=7, pdf=2, xlsx=2),
        ),
        finance=FinanceProfile(base_revenue=1000000, growth_rate=0.1,
                               expense_ratio=0.7),
        engagements=EngagementPlan(count=2),
        graph_targets=GraphTargets(external_orgs=2, external_people=2),
        narrative="A synthetic firm used only by tests.",
    )
    base.update(over)
    return Charter(**base)


def test_churn_is_on_by_default_and_moves_the_roster():
    """rf:orgreal-1: nobody is ever hired, promoted, or leaves. The default
    charter -- no churn block written at all -- must not reproduce it."""
    f = build_foundation(_charter())
    assert f.slug == "synth"
    departed = [p for p in f.people if p.employment.end is not None]
    promoted = [p for p in f.people if p.title_history]
    assert len(departed) == 1, "default recipe must contain a departure"
    assert len(promoted) == 1, "default recipe must contain a promotion"
    # headcount declares 4 concurrent seats; churn makes people-ever exceed it.
    assert len(f.people) == 5
    assert sum(p.employment.end is None for p in f.people) == 4


def test_churn_zero_freezes_the_roster():
    f = build_foundation(_charter(roster_churn=RosterChurn(departures=0,
                                                           promotions=0)))
    assert all(p.employment.end is None for p in f.people)
    assert all(not p.title_history for p in f.people)
    assert len(f.people) == 4


def test_a_departing_seat_is_backfilled_by_a_successor():
    f = build_foundation(_charter())
    gone = next(p for p in f.people if p.employment.end is not None)
    successor = next(
        p
        for p in f.people
        if p.id != gone.id
        and p.dept == gone.dept
        and p.reports_to == gone.reports_to
        and p.employment.start > gone.employment.end
    )
    assert successor.title == gone.title, "the seat keeps its title"
    assert successor.employment.start > gone.employment.end, "no overlap"
    assert successor.name != gone.name and successor.email != gone.email


def test_the_ceo_equivalent_never_departs():
    f = build_foundation(_charter())
    ceo = next(p for p in f.people if p.reports_to is None)
    assert ceo.employment.end is None


def test_nobody_who_manages_anyone_departs():
    """reports_to is a scalar with no time dimension, so a departing manager
    would leave its reports pointing at someone who is gone. Eligibility is
    'manages nobody', which is what keeps the tree intact."""
    f = build_foundation(_charter())
    managers = {p.reports_to for p in f.people if p.reports_to}
    for p in f.people:
        if p.id in managers:
            assert p.employment.end is None, f"{p.id} manages someone and left"


def test_the_org_chart_stays_one_acyclic_tree_with_no_orphan():
    f = build_foundation(_charter())
    ids = {p.id for p in f.people}
    roots = [p for p in f.people if p.reports_to is None]
    assert len(roots) == 1, "exactly one CEO-equivalent"
    for p in f.people:
        assert p.reports_to is None or p.reports_to in ids, "dangling reports_to"
    for p in f.people:  # walk to the root; a cycle never terminates
        seen, cur, hops = {p.id}, p, 0
        while cur.reports_to is not None:
            assert cur.reports_to not in seen, f"cycle through {cur.id}"
            seen.add(cur.reports_to)
            cur = f.person(cur.reports_to)
            hops += 1
            assert hops <= len(f.people), "unterminated walk"


def test_a_promotion_moves_one_rung_up_the_dept_title_list():
    charter = _charter()
    f = build_foundation(charter)
    p = next(x for x in f.people if x.title_history)
    titles = charter.titles[p.dept]
    old, new = p.title_history[0].title, p.title_history[-1].title
    assert titles.index(new) == titles.index(old) - 1, "exactly one rung"
    assert p.title == new, "Person.title is the latest"
    assert p.title_at(p.title_history[0].start) == old
    assert p.employment.end is None, "a departed person is not promoted"


def test_the_minimum_roster_degrades_rather_than_crashing(capsys):
    """Criterion 2, and the case the freeze lift creates: with churn ON by
    default, a roster too small to host it must not crash a legitimate
    recipe. headcount total 2 is the schema minimum, and its one non-CEO seat
    has no rung above it, so departures fit and promotions cannot."""
    f = build_foundation(
        _charter(
            headcount={"Leadership": 1, "Ops": 1},
            titles={"Leadership": ["Managing Partner"]},
        )
    )
    out = capsys.readouterr().out
    assert "0 of 1 requested promotions" in out, "degradation must be reported"
    assert not any(p.title_history for p in f.people)
    # The departure still fits: the lone Ops seat manages nobody.
    assert sum(p.employment.end is not None for p in f.people) == 1
    assert len(f.people) == 3


def test_asking_for_more_churn_than_the_roster_holds_degrades_visibly(capsys):
    f = build_foundation(
        _charter(roster_churn=RosterChurn(departures=99, promotions=99))
    )
    out = capsys.readouterr().out
    assert "of 99 requested departures" in out
    assert "of 99 requested promotions" in out
    # Everyone eligible left; nobody who manages anyone did.
    managers = {p.reports_to for p in f.people if p.reports_to}
    assert all(p.employment.end is None for p in f.people if p.id in managers)


def test_churn_draws_from_its_own_stream_and_leaves_the_base_roster_alone():
    """The seeds discipline the freeze lift must not relax: churn must not
    reach into the shared Faker, or a change to external_people would move
    every backfill hire's name."""
    a = build_foundation(_charter())
    b = build_foundation(_charter(graph_targets=GraphTargets(
        external_orgs=3, external_people=5)))
    hires_a = [p.name for p in a.people if p.employment.start > date(2016, 1, 1)
               and p.employment.end is None and p.reports_to is not None]
    hires_b = [p.name for p in b.people if p.employment.start > date(2016, 1, 1)
               and p.employment.end is None and p.reports_to is not None]
    assert hires_a and hires_a == hires_b, (
        "backfill names moved when only the external roster changed"
    )


def test_churn_is_deterministic_under_the_seed():
    a, b = build_foundation(_charter()), build_foundation(_charter())
    assert a.model_dump(mode="json") == b.model_dump(mode="json")
    c = build_foundation(_charter(seed=99))
    assert c.model_dump(mode="json") != a.model_dump(mode="json")


def test_title_history_is_additive_on_the_existing_schema_id():
    """The six fixtures that stay committed until M11 carry no title_history.
    They must keep loading, and they must resolve every date to the scalar."""
    p = Person.model_validate(
        {
            "id": "p:old.hand",
            "name": "Old Hand",
            "title": "Managing Partner",
            "dept": "Leadership",
            "employment": {"start": "2018-01-01"},
            "email": "old@example.com",
            "phone": "555-0101",
        }
    )
    assert p.title_history == []
    assert p.title_at(date(2020, 1, 1)) == "Managing Partner"
