"""Engagements: the deal/matter spine that owns the planted facts.

Each engagement carries its facts with exact surface forms (`rendered`).
Documents reference facts by id; renderers substitute the surface form; the
fact-echo validator finds it verbatim in the rendered text.
"""

from __future__ import annotations

from datetime import date, timedelta

from ..schemas import (
    Affiliation,
    Charter,
    Engagement,
    EngagementsLedger,
    Fact,
    Foundation,
)
from ..seeds import rng

_SERVICES = ["Operational Review", "Pricing Study", "Integration Support"]

# The engagement letter is dated this many days before the engagement
# start (clamped to the charter range). Shared with docplan's letter
# dating and the AFF validators' covering-window recomputation: all three
# must agree on how far a document can lead its engagement.
LETTER_LEAD_DAYS = 10


def render_money(value: int) -> str:
    return f"${value:,}"


def render_date(value: date) -> str:
    return f"{value:%B} {value.day}, {value.year}"


def minutes_date(start: date, end: date, range_start: date, range_end: date) -> date:
    """The engagement's working-session date, 40% through its duration.

    Single source of truth shared by fabric (which plants filename-only
    minutes-date facts) and docplan (which dates the minutes doc): both
    sides must land on the same day or the planted fact would not match
    the filename docplan builds."""
    duration = (end - start).days
    when = start + timedelta(days=int(duration * 0.4))
    return max(range_start, min(when, range_end))


def _employed_at(person, when: date) -> bool:
    emp = person.employment
    return emp.start <= when and (emp.end is None or emp.end >= when)


# --- affiliation-aware participant selection (M6+) -------------------------
# Pure helpers shared with the AFF validators, which recompute the plan
# from charter plus foundation as tamper evidence.


def xp_affiliations(xp) -> list[Affiliation]:
    """Explicit history, or the implicit open-ended current-org
    affiliation for single-employer people."""
    if xp.affiliations:
        return list(xp.affiliations)
    return [Affiliation(org=xp.org)]


def affiliation_covering(xp, org_id: str, lo: date, hi: date) -> bool:
    """Whether xp holds an affiliation to org_id covering [lo, hi]."""
    for aff in xp_affiliations(xp):
        if aff.org != org_id:
            continue
        if (aff.start is None or aff.start <= lo) and (
            aff.end is None or aff.end >= hi
        ):
            return True
    return False


def padded_window(start: date, end: date, range_start: date) -> tuple[date, date]:
    """The affiliation-coverage window of an engagement's documents: the
    letter leads the start by LETTER_LEAD_DAYS, clamped to the charter
    range exactly as docplan dates it."""
    return max(range_start, start - timedelta(days=LETTER_LEAD_DAYS)), end


def affiliation_plan(
    foundation: Foundation,
    windows: list[tuple[str, date, date]],
    range_start: date,
) -> dict[str, tuple[str, list[str]]]:
    """Deterministic, RNG-free client and external-participant assignment
    for the affiliations_in_docs knob.

    `windows` is [(engagement_id, start, end)] in build order (which is
    also round-robin client order). Returns
    {engagement_id: (client_org_id, [xp_ids])}.

    Every multi-affiliation external person, in foundation order, is
    designated onto one engagement per affiliation side: the first
    undesignated engagement whose padded window that side's affiliation
    covers has its client reassigned to the side's org and the person
    attached. Round-robin alone cannot guarantee this: index 0 pairs the
    current org with the earliest engagement while the affiliation
    boundary lands mid-range. Undesignated engagements keep their
    round-robin client and take the first external person (foundation
    order, current-org contacts first) holding a covering affiliation.

    RNG-freeness is load-bearing: AFF-01 recomputes this plan as tamper
    evidence. Tie-breaking randomness, if ever wanted, must come from a
    new seeds.py stream. A reassignment can leave an external org with no
    engagement; that is harmless (client_of edges derive from the ledger).
    """
    multi = [
        xp for xp in foundation.external_people if len(xp.affiliations) >= 2
    ]
    designated: dict[str, tuple[str, str]] = {}

    for xp in multi:
        sides: list[str] = []
        for aff in xp_affiliations(xp):
            if aff.org not in sides:
                sides.append(aff.org)
        for side_org in sides:
            picked = None
            for eid, start, end in windows:
                if eid in designated:
                    continue
                lo, hi = padded_window(start, end, range_start)
                if affiliation_covering(xp, side_org, lo, hi):
                    picked = eid
                    break
            if picked is None:
                raise SystemExit(
                    f"fabric: affiliations_in_docs cannot place {xp.id} on "
                    f"an engagement under {side_org}: no undesignated "
                    "engagement window falls inside that affiliation. Widen "
                    "doc_culture.date_range, raise engagements.count, or "
                    "change the seed."
                )
            designated[picked] = (side_org, xp.id)

    orgs = foundation.external_orgs
    plan: dict[str, tuple[str, list[str]]] = {}
    for idx, (eid, start, end) in enumerate(windows):
        if eid in designated:
            org_id, xp_id = designated[eid]
            plan[eid] = (org_id, [xp_id])
            continue
        org_id = orgs[idx % len(orgs)].id
        lo, hi = padded_window(start, end, range_start)
        eligible = [
            xp
            for xp in foundation.external_people
            if affiliation_covering(xp, org_id, lo, hi)
        ]
        eligible.sort(key=lambda xp: xp.org != org_id)  # stable sort
        plan[eid] = (org_id, [eligible[0].id] if eligible else [])
    return plan


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

    # Affiliation-aware docs (M6+): a deterministic, RNG-free post-pass.
    # Knob off = zero fields touched and zero RNG consumed, so committed
    # orgs regenerate byte-identically; knob on = clients and external
    # participants are exactly affiliation_plan's output, which AFF-01
    # recomputes from charter plus foundation.
    if charter.graph_targets.affiliations_in_docs:
        windows = [(e.id, e.start, e.end) for e in engagements]
        plan = affiliation_plan(foundation, windows, range_start)
        org_by_id = {o.id: o for o in foundation.external_orgs}
        services = charter.engagements.services or _SERVICES
        for idx, eng in enumerate(engagements):
            client_id, xp_ids = plan[eng.id]
            eng.external_participants = xp_ids
            if client_id == eng.client:
                continue
            client = org_by_id[client_id]
            service = services[idx % len(services)]
            eng.client = client.id
            eng.title = f"{service} for {client.name}"
            eng.summary = (
                f"{service} engagement for {client.name}, running "
                f"{eng.start:%B %Y} through {eng.end:%B %Y} at a fixed fee "
                f"of {render_money(eng.fee)}."
            )
            fact = next(f for f in eng.facts if f.id == f"f:{eng.id}.client")
            fact.value = client.name
            fact.rendered = client.name

    # Hard-case planting: assign non-body location policies from the recipe
    # knobs. Selection is deterministic (build order) and consumes no RNG,
    # so knobs-off recipes regenerate byte-identically. Capped at the
    # eligible count here; docplan owns the actionable over-demand failure,
    # where placement demand meets document supply.
    hard = charter.hard_cases
    for eng in engagements[: min(hard.signature_page_facts, len(engagements))]:
        fee = next(f for f in eng.facts if f.id == f"f:{eng.id}.fee")
        fee.location_policy = "signature_page"
    for eng in engagements[: min(hard.filename_dates, len(engagements))]:
        md = minutes_date(eng.start, eng.end, range_start, range_end)
        eng.facts.append(
            Fact(
                id=f"f:{eng.id}.minutes-date",
                kind="date",
                value=md.isoformat(),
                rendered=f"{md:%Y-%m-%d}",
                location_policy="filename",
            )
        )

    ledger = EngagementsLedger(slug=charter.slug, engagements=engagements)
    ledger.fact_index()  # raises on duplicate fact ids
    return ledger
