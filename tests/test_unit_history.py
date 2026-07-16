"""Unit tier: the fabric's time dimension (M8).

Title history and its date resolver. Churn, rotation, and behavioral
finance join this module as they land.
"""

from collections import Counter
from datetime import date

import pytest
from pydantic import ValidationError

from orgsmith.artifacts import load_foundation
from orgsmith.authoring.contexts import _brief_person
from orgsmith.fabric.engagements import _employed_at, build_engagements
from orgsmith.fabric.finance import _avg_headcount, build_finance
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


# --- behavioral finance ----------------------------------------------------


def _finance(**over):
    charter = _charter(**over)
    return charter, build_finance(charter, build_foundation(charter))


def _rates(a, b):
    return {c: b.expenses[c] / a.expenses[c] - 1 for c in a.expenses}


def test_no_two_expense_categories_grow_at_the_same_rate():
    """rf:finance-1: 'every expense line is a frozen percentage of revenue in
    all eight years, which no real P&L does'. Under the old model every rate
    in a year was identical by construction."""
    charter, f = _finance()
    checked = 0
    for a, b in zip(f.years, f.years[1:]):
        if a.year == charter.founded:
            continue  # the founding year is a partial ramp, not a comparison
        rates = [round(r, 6) for r in _rates(a, b).values()]
        assert len(set(rates)) == len(rates), f"FY{b.year} rates tie: {rates}"
        checked += 1
    assert checked >= 5


def test_the_lease_is_step_fixed_across_a_multi_year_span():
    """rf:finance-2: 'rent is a lease cost and cannot compound 11% a year
    because fees went up'."""
    charter, f = _finance()
    full = [y for y in f.years if y.year > charter.founded]
    rent = [y.expenses["Office & Facilities"] for y in full]
    runs, run = [], 1
    for a, b in zip(rent, rent[1:]):
        run = run + 1 if a == b else 1
        runs.append(run)
    assert max(runs) >= 3, f"rent never holds still: {rent}"
    assert len(set(rent)) > 1, "rent must step on renewal, not be constant"
    # Revenue rises every full year; rent must not follow it.
    assert [y.revenue for y in full] == sorted(y.revenue for y in full)


def test_compensation_does_not_track_revenue():
    """The specific shape rf:finance-1 indicts. In a year where headcount did
    not move and revenue sprinted 50%, compensation must move at raises.

    Years are selected by asking `_avg_headcount` rather than assumed flat:
    `_build_people` starts its last hire 25-45% into the range, so the early
    years of any org are still filling up and compensation rightly jumps
    there. Asserting over them would fail for the opposite of the reason this
    test exists.
    """
    charter, f = _finance(
        finance=FinanceProfile(
            base_revenue=1000000, growth_rate=0.5, expense_ratio=0.7
        ),
        roster_churn=RosterChurn(departures=0, promotions=0),
    )
    foundation = build_foundation(
        _charter(
            finance=FinanceProfile(
                base_revenue=1000000, growth_rate=0.5, expense_ratio=0.7
            ),
            roster_churn=RosterChurn(departures=0, promotions=0),
        )
    )
    checked = 0
    for a, b in zip(f.years, f.years[1:]):
        if _avg_headcount(foundation, a.year) != _avg_headcount(foundation, b.year):
            continue
        rev = b.revenue / a.revenue - 1
        comp = b.expenses["Compensation"] / a.expenses["Compensation"] - 1
        assert rev > 0.3, "the test needs revenue to actually be sprinting"
        assert comp < 0.1, f"FY{b.year} compensation chased revenue: {comp:+.3f}"
        checked += 1
    assert checked >= 2, "no flat-headcount year to compare; test is vacuous"


def test_compensation_falls_when_a_seat_empties():
    """The positive half: headcount is what drives it. Identical charters but
    for one departure; the revenue and expense RNG streams are untouched by
    churn, so compensation is the only reason the number can move."""
    _, churned = _finance(roster_churn=RosterChurn(departures=1, promotions=0))
    _, frozen = _finance(roster_churn=RosterChurn(departures=0, promotions=0))
    assert [y.revenue for y in churned.years] == [y.revenue for y in frozen.years]
    comp_c = {y.year: y.expenses["Compensation"] for y in churned.years}
    comp_f = {y.year: y.expenses["Compensation"] for y in frozen.years}
    assert any(comp_c[y] < comp_f[y] for y in comp_f), (
        "a seat sat empty and compensation did not notice"
    )
    assert all(comp_c[y] <= comp_f[y] for y in comp_f), "churn only removes here"


def test_the_first_full_year_is_calibrated_to_expense_ratio():
    """expense_ratio's remaining job: it sizes the P&L once and then stops
    applying. If it did not land here it would mean nothing at all."""
    for ratio in (0.55, 0.71, 0.85):
        charter, f = _finance(
            finance=FinanceProfile(
                base_revenue=1000000, growth_rate=0.1, expense_ratio=ratio
            )
        )
        first_full = next(y for y in f.years if y.year == charter.founded + 1)
        realized = sum(first_full.expenses.values()) / first_full.revenue
        assert abs(realized - ratio) < 0.02, f"{realized:.3f} vs {ratio}"


def test_tie_outs_still_hold_and_a_loss_is_recorded_not_raised():
    """A firm whose costs outrun its fees is a fact about the firm, not a
    generator error. Under the old model this was unreachable: expenses were
    revenue * a ratio that the schema pins below 1.0, so net income was
    positive by construction."""
    charter, f = _finance(
        finance=FinanceProfile(
            base_revenue=4000000, growth_rate=-0.45, expense_ratio=0.95
        )
    )
    assert all(c.ok for c in f.checks), [c for c in f.checks if not c.ok]
    for y in f.years:
        assert sum(y.quarters) == y.revenue
    losses = [y for y in f.years if sum(y.expenses.values()) > y.revenue]
    assert losses, "the shrinking firm never posted a loss"
    for y in losses:
        rec = next(c for c in f.checks if c.name == f"FY{y.year}.net-income")
        assert rec.ok, "a loss is not a failed check"
        assert f"net=-" in rec.detail, rec.detail


def test_expenses_draw_from_their_own_stream():
    """Tuning the expense model must not move the revenue series. Same seed,
    different expense_ratio: revenue is identical."""
    _, a = _finance(
        finance=FinanceProfile(
            base_revenue=1000000, growth_rate=0.1, expense_ratio=0.5
        )
    )
    _, b = _finance(
        finance=FinanceProfile(
            base_revenue=1000000, growth_rate=0.1, expense_ratio=0.9
        )
    )
    assert [y.revenue for y in a.years] == [y.revenue for y in b.years]
    assert [y.quarters for y in a.years] == [y.quarters for y in b.years]


# --- date-scoped briefs: engagement position and firm digest ---------------


def test_engagement_position_is_stated_not_the_dates():
    """rf:narr-2: a deck 51 days into a 204-day program called itself 'past
    its midpoint'. The brief now states the position in Python, and never the
    start or end date -- those stay fact placeholders (the airlock)."""
    from datetime import timedelta

    from orgsmith.authoring.contexts import _engagement_position

    class E:
        start = date(2020, 1, 1)
        end = start + timedelta(days=204)

    e = E()
    early = _engagement_position(e, e.start + timedelta(days=51))
    assert "25%" in early and "early phase" in early
    late = _engagement_position(e, e.start + timedelta(days=180))
    assert "later phase" in late
    # The exact rf:narr-2 failure is no longer expressible: 51/204 is not
    # "past the midpoint".
    assert "midpoint" not in early
    # No literal engagement date leaks into the brief.
    for text in (early, late):
        assert "2020" not in text and "01-01" not in text


def test_engagement_position_clamps_out_of_window_dates():
    from datetime import timedelta

    from orgsmith.authoring.contexts import _engagement_position

    class E:
        start = date(2020, 1, 1)
        end = start + timedelta(days=100)

    e = E()
    # A letter dated before kickoff (lead-in) and a doc after close both stay
    # inside 0..100% rather than reading -30% or 130%.
    assert "0%" in _engagement_position(e, e.start - timedelta(days=30))
    assert "100%" in _engagement_position(e, e.end + timedelta(days=30))


def test_firm_digest_names_clients_by_fact_id_and_scopes_to_the_date():
    """rf:narr-1: an overview invented a relationship because it was handed the
    whole-arc narrative and one client fact. The digest carries only what has
    begun as of the date, clients as placeholders, never by value."""
    from datetime import timedelta

    from orgsmith.authoring.contexts import _firm_digest

    class E:
        def __init__(self, eid, start):
            self.id = eid
            self.start = start

    engs = [
        E("E-2019-001", date(2019, 6, 1)),
        E("E-2021-001", date(2021, 6, 1)),
        E("E-2023-001", date(2023, 6, 1)),
    ]
    # Dated mid-2021: the first two have begun, the third has not.
    digest = _firm_digest(engs, date(2021, 12, 31))
    assert "2 client engagement" in digest
    assert "{{fact:f:E-2019-001.client}}" in digest
    assert "{{fact:f:E-2021-001.client}}" in digest
    assert "E-2023-001" not in digest, "cited an engagement that had not begun"


def test_firm_digest_before_any_engagement_claims_no_client_work():
    from orgsmith.authoring.contexts import _firm_digest

    class E:
        id = "E-2022-001"
        start = date(2022, 1, 1)

    digest = _firm_digest([E()], date(2020, 1, 1))
    assert "no completed client engagements" in digest or "no " in digest.lower()
    assert "{{fact" not in digest, "claimed a client before any engagement began"


def test_overview_briefs_only_the_clients_that_exist_as_of_its_date(tmp_path):
    """End to end: the planted facts_refs match the digest, so FACT-01 is
    satisfiable -- the overview is briefed exactly the clients it may cite,
    and more than the single one it used to carry."""
    paths = build_pure_stages(tmp_path)
    from orgsmith.artifacts import load_manifest

    man = load_manifest(paths)
    overview = next(e for e in man if e.genre == "company_overview")
    # dev-mini's engagements that begin before the mid-range overview.
    assert len(overview.facts_refs) >= 2, "overview should cite more than one client"
    assert all(ref.endswith(".client") for ref in overview.facts_refs)


# --- staffing rotation -----------------------------------------------------


def _big_delivery_charter(consultants=6, engagements=6, **over):
    base = dict(
        founded=2014,
        headcount={"Leadership": 1, "Consulting": consultants},
        titles={
            "Leadership": ["Managing Partner"],
            "Consulting": [f"Consultant {i}" for i in range(consultants)],
        },
        engagements=EngagementPlan(count=engagements),
        # A decade so the engagements spread across distinct years.
        doc_culture=DocCulture(
            target_docs=11,
            date_range=(date(2014, 1, 1), date(2023, 12, 31)),
            format_mix=FormatMix(docx=7, pdf=2, xlsx=2),
        ),
        # No churn: rotation is the variable under test, and a departure
        # narrowing the pool mid-history is a different knob's noise here.
        roster_churn=RosterChurn(departures=0, promotions=0),
    )
    base.update(over)
    return _charter(**base)


def _engagements(charter):
    return build_engagements(charter, build_foundation(charter))


def test_no_two_engagements_share_an_identical_team_when_the_roster_allows():
    """rf:graph-1: 'every engagement across five years is staffed by exactly
    the same three people'. With a roster large enough to afford it, the teams
    must differ."""
    eng = _engagements(_big_delivery_charter())
    teams = [frozenset(e.internal_participants) for e in eng.engagements]
    assert len(set(teams)) == len(teams), f"identical teams: {teams}"


def test_no_consultant_appears_on_every_engagement():
    eng = _engagements(_big_delivery_charter())
    n = len(eng.engagements)
    counts = Counter(p for e in eng.engagements for p in e.internal_participants)
    assert not [p for p, k in counts.items() if k == n], (
        "someone is on every engagement"
    )


def test_the_lead_rotates_rather_than_being_the_dept_lead_every_time():
    """Today lead = available[0] is the same person for the firm's life."""
    eng = _engagements(_big_delivery_charter())
    leads = [e.internal_participants[0] for e in eng.engagements]
    assert len(set(leads)) >= 3, f"lead barely rotates: {leads}"
    # Load is spread, not piled on one person.
    assert max(Counter(leads).values()) <= 2


def test_rotation_draws_from_its_own_stream_and_leaves_dates_and_fees_alone():
    """Adding rotation must not move engagement dates, fees, clients, or
    years -- those come from the fabric.engagements stream, staffing from
    fabric.engagements.staffing."""
    charter = _charter()  # 3 consultants, 2 engagements
    a = build_engagements(charter, build_foundation(charter))
    b = build_engagements(charter, build_foundation(charter))
    for x, y in zip(a.engagements, b.engagements):
        assert (x.start, x.end, x.fee, x.client) == (y.start, y.end, y.fee, y.client)
    # Deterministic staffing too.
    assert [e.internal_participants for e in a.engagements] == [
        e.internal_participants for e in b.engagements
    ]


def test_rotation_degrades_on_a_roster_too_small_to_vary():
    """One consultant cannot produce distinct teams. It must return that
    person, not crash trying to sample a fresh set."""
    charter = _big_delivery_charter(consultants=1, engagements=3)
    eng = _engagements(charter)
    teams = [frozenset(e.internal_participants) for e in eng.engagements]
    assert all(len(t) == 1 for t in teams), teams
    assert len(set(teams)) == 1, "the lone consultant leads every engagement"


def test_a_lead_is_employed_for_the_whole_engagement_under_churn():
    """The bug roster churn exposes: the lead was checked only at start, so a
    person who departs mid-program could lead it. Every internal participant
    must be employed across the full window now."""
    charter = _big_delivery_charter(
        consultants=5, engagements=6,
        roster_churn=RosterChurn(departures=2, promotions=1),
    )
    foundation = build_foundation(charter)
    eng = build_engagements(charter, foundation)
    by_id = {p.id: p for p in foundation.people}
    for e in eng.engagements:
        for pid in e.internal_participants:
            p = by_id[pid]
            assert _employed_at(p, e.start) and _employed_at(p, e.end), (
                f"{pid} staffed on {e.id} but not employed across it"
            )


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
