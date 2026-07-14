"""foundation --scaffold: deterministic roster, externals, and timeline.

Pure. Everything structural is fixed here under the recipe seed: ids,
names, the reporting tree, employment spans, emails, phones, external orgs
and people, and skeleton timeline events. Model enrichment later fills
persona prose only; it can never move a date or a reporting line.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta

from faker import Faker

from ..paths import OrgPaths
from ..schemas import (
    Charter,
    EmploymentSpan,
    ExternalOrg,
    ExternalPerson,
    Foundation,
    Person,
    TimelineEvent,
    write_model,
)
from ..seeds import rng
from ..state import load_state, require_stages, save_state, sha256_file
from ..artifacts import load_charter

# Reserved fictional phone block (555-0100..0199) keeps numbers undialable.
_AREA_CODES = ["212", "312", "415", "617", "206", "303"]
_EXT_TITLES = ["Chief Operating Officer", "VP Finance", "Director of Operations",
               "General Manager", "Chief Financial Officer"]


def _ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def _slugify(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", _ascii(text).lower()).strip("-")
    return re.sub(r"-+", "-", out)


def _person_id(first: str, last: str) -> str:
    return f"p:{_slugify(first)}.{_slugify(last)}"


def _mid_month(year: int, month: int) -> date:
    return date(year, month, 15)


def _build_people(charter: Charter, fake: Faker, rand) -> list[Person]:
    people: list[Person] = []
    used_ids: set[str] = set()
    depts = list(charter.headcount.items())
    ceo_id: str | None = None
    dept_lead: dict[str, str] = {}
    range_start, range_end = charter.doc_culture.date_range

    total = sum(n for _, n in depts)
    built = 0
    for dept_idx, (dept, count) in enumerate(depts):
        titles = charter.titles.get(dept, [])
        for i in range(count):
            # Unique, ascii-safe name (regenerate on id collision).
            while True:
                first, last = fake.first_name(), fake.last_name()
                pid = _person_id(first, last)
                if pid not in used_ids and _slugify(first) and _slugify(last):
                    break
            used_ids.add(pid)

            if i < len(titles):
                title = titles[i]
            else:
                title = f"Director, {dept}" if i == 0 else f"{dept} Associate"

            is_ceo = dept_idx == 0 and i == 0
            if is_ceo:
                reports_to = None
            elif i == 0:
                reports_to = ceo_id
            else:
                reports_to = dept_lead[dept]

            built += 1
            is_last_hire = built == total and not is_ceo
            if is_ceo or i == 0:
                start = _mid_month(charter.founded, 2 + dept_idx)
            elif is_last_hire:
                # One late joiner mid-range keeps employment-vs-doc-date
                # checks meaningful.
                span_days = (range_end - range_start).days
                start = range_start + timedelta(days=rand.randint(
                    int(span_days * 0.25), int(span_days * 0.45)))
            else:
                start = _mid_month(
                    charter.founded, rand.randint(3, 11)
                ) + timedelta(days=rand.randint(0, 400))
                start = min(start, range_start + timedelta(days=60))

            area = rand.choice(_AREA_CODES)
            phone = f"+1 ({area}) 555-01{rand.randint(0, 99):02d}"
            email = f"{_slugify(first)}.{_slugify(last)}@{charter.domain}"
            email = email.replace("-", "")

            person = Person(
                id=pid,
                name=f"{first} {last}",
                title=title,
                dept=dept,
                reports_to=reports_to,
                employment=EmploymentSpan(start=start),
                email=email,
                phone=phone,
            )
            people.append(person)
            if is_ceo:
                ceo_id = pid
            if i == 0:
                dept_lead[dept] = pid
    return people


def _build_externals(
    charter: Charter, fake: Faker, rand
) -> tuple[list[ExternalOrg], list[ExternalPerson]]:
    orgs: list[ExternalOrg] = []
    used: set[str] = set()
    while len(orgs) < charter.graph_targets.external_orgs:
        name = fake.company()
        oid = f"x:{_slugify(name)}"
        if oid in used or not _slugify(name):
            continue
        used.add(oid)
        orgs.append(ExternalOrg(id=oid, name=name, org_type="client"))

    people: list[ExternalPerson] = []
    used_p: set[str] = set()
    for i in range(charter.graph_targets.external_people):
        org = orgs[i % len(orgs)]
        while True:
            first, last = fake.first_name(), fake.last_name()
            pid = f"xp:{_slugify(first)}.{_slugify(last)}"
            if pid not in used_p and _slugify(first) and _slugify(last):
                break
        used_p.add(pid)
        domain = f"{_slugify(org.name).replace('-', '')}.com"
        people.append(
            ExternalPerson(
                id=pid,
                name=f"{first} {last}",
                org=org.id,
                title=rand.choice(_EXT_TITLES),
                email=f"{_slugify(first)}.{_slugify(last)}@{domain}".replace("-", ""),
            )
        )
    return orgs, people


def build_foundation(charter: Charter) -> Foundation:
    fake = Faker("en_US")
    fake.seed_instance(charter.seed)
    rand = rng(charter.seed, "foundation.scaffold")

    people = _build_people(charter, fake, rand)
    orgs, ext_people = _build_externals(charter, fake, rand)

    timeline = [
        TimelineEvent(
            date=_mid_month(charter.founded, 1),
            summary=f"{charter.name} founded.",
            ground_truth_tags=["founding"],
        ),
        TimelineEvent(
            date=_mid_month(charter.founded + 1, rand.randint(3, 10)),
            summary="Firm moved into its current office.",
            ground_truth_tags=["facilities"],
        ),
    ]
    return Foundation(
        slug=charter.slug,
        people=people,
        external_orgs=orgs,
        external_people=ext_people,
        timeline=timeline,
    )


def run_scaffold(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "charter")
    if paths.foundation_json.exists():
        # Immutable once written: a re-scaffold would wipe merged enrichment
        # prose and could reshuffle ids under a changed recipe.
        print(f"foundation: {paths.foundation_json} exists, nothing to do")
        return 0

    charter = load_charter(paths)
    foundation = build_foundation(charter)
    write_model(paths.foundation_json, foundation)

    state.mark_done("foundation", inputs_hash=sha256_file(paths.charter_json))
    save_state(paths, state)
    print(
        f"foundation: {len(foundation.people)} people, "
        f"{len(foundation.external_orgs)} external orgs -> {paths.foundation_json}"
    )
    return 0
