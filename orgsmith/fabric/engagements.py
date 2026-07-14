"""Engagements: the deal/matter spine that owns the planted facts.

Each engagement carries its facts with exact surface forms (`rendered`).
Documents reference facts by id; renderers substitute the surface form; the
fact-echo validator finds it verbatim in the rendered text.
"""

from __future__ import annotations

from datetime import date, timedelta

from ..schemas import Charter, Engagement, EngagementsLedger, Fact, Foundation
from ..seeds import rng

_SERVICES = ["Operational Review", "Pricing Study", "Integration Support"]


def render_money(value: int) -> str:
    return f"${value:,}"


def render_date(value: date) -> str:
    return f"{value:%B} {value.day}, {value.year}"


def _employed_at(person, when: date) -> bool:
    emp = person.employment
    return emp.start <= when and (emp.end is None or emp.end >= when)


def build_engagements(charter: Charter, foundation: Foundation) -> EngagementsLedger:
    rand = rng(charter.seed, "fabric.engagements")
    range_start, range_end = charter.doc_culture.date_range

    ceo = next(p for p in foundation.people if p.reports_to is None)
    # Engagement staff come from the largest department outside the CEO's
    # (the delivery org: Consulting here, Engineering elsewhere).
    staff_dept = max(
        (d for d in charter.headcount if d != ceo.dept),
        key=lambda d: charter.headcount[d],
    )
    consultants = [p for p in foundation.people if p.dept == staff_dept]

    # Spread engagements over distinct years where possible, leaving margin
    # for pre-engagement letters and post-start documents.
    years = list(range(range_start.year, range_end.year + 1))
    chosen_years = sorted(
        rand.sample(years, min(charter.engagements.count, len(years)))
    )
    while len(chosen_years) < charter.engagements.count:
        chosen_years.append(rand.choice(years))
    chosen_years.sort()

    # Bound the seeded start to the usable window so the end clamp below can
    # never invert the engagement: 45d lead-in + 90d minimum duration + 14d
    # end margin must fit inside the charter date range.
    start_floor = range_start + timedelta(days=45)
    start_cap = range_end - timedelta(days=90 + 14)
    if start_cap < start_floor:
        raise SystemExit(
            f"fabric: doc_culture.date_range {range_start}..{range_end} is too "
            "short for engagements; it must span at least 149 days"
        )

    engagements: list[Engagement] = []
    serial_by_year: dict[int, int] = {}
    for idx in range(charter.engagements.count):
        year = chosen_years[idx]
        start = date(year, rand.randint(2, 8), rand.randint(1, 28))
        start = min(max(start, start_floor), start_cap)
        end = start + timedelta(days=rand.randint(90, 270))
        end = min(end, range_end - timedelta(days=14))

        serial_by_year[year] = serial_by_year.get(year, 0) + 1
        eid = f"E-{year}-{serial_by_year[year]:03d}"

        client = foundation.external_orgs[idx % len(foundation.external_orgs)]
        client_people = [p for p in foundation.external_people if p.org == client.id]
        externals = [client_people[0].id] if client_people else []

        available = [p for p in consultants if _employed_at(p, start)]
        if not available:
            available = [ceo]
        lead = available[0]
        others = [p for p in available[1:] if _employed_at(p, end)]
        team = [lead] + rand.sample(others, min(len(others), rand.randint(1, 2)))

        services = charter.engagements.services or _SERVICES
        service = services[idx % len(services)]
        fee = rand.randint(60, 240) * 500
        facts = [
            Fact(
                id=f"f:{eid}.fee",
                kind="money",
                value=fee,
                rendered=render_money(fee),
            ),
            Fact(
                id=f"f:{eid}.start",
                kind="date",
                value=start.isoformat(),
                rendered=render_date(start),
            ),
            Fact(
                id=f"f:{eid}.client",
                kind="text",
                value=client.name,
                rendered=client.name,
            ),
        ]
        engagements.append(
            Engagement(
                id=eid,
                title=f"{service} for {client.name}",
                client=client.id,
                start=start,
                end=end,
                fee=fee,
                internal_participants=[p.id for p in team],
                external_participants=externals,
                summary=(
                    f"{service} engagement for {client.name}, running "
                    f"{start:%B %Y} through {end:%B %Y} at a fixed fee of "
                    f"{render_money(fee)}."
                ),
                facts=facts,
            )
        )

    ledger = EngagementsLedger(slug=charter.slug, engagements=engagements)
    ledger.fact_index()  # raises on duplicate fact ids
    return ledger
