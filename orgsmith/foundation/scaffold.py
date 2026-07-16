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

from ..namescreen import screen_foundation
from ..paths import OrgPaths
from ..schemas import (
    Affiliation,
    Charter,
    EmploymentSpan,
    ExternalOrg,
    ExternalPerson,
    Foundation,
    Person,
    TimelineEvent,
    TitleSpan,
    write_model,
)
from ..seeds import derive_seed, rng
from ..state import load_state, require_stages, save_state, sha256_file
from ..artifacts import load_charter

# Reserved fictional phone block (555-0100..0199) keeps numbers undialable.
_AREA_CODES = ["212", "312", "415", "617", "206", "303"]
_EXT_TITLES = ["Chief Operating Officer", "VP Finance", "Director of Operations",
               "General Manager", "Chief Financial Officer"]

# A departure needs a plausible tenure behind it; a seat that turns over in
# the same quarter it was filled reads as a data error, not a resignation.
_MIN_TENURE_DAYS = 180

# Nickname pool for the nickname_aliases knob. Keys double as replacement
# first names when a seeded roster has no nicknamable member.
_NICKNAMES = {
    "Michael": "Mike", "Robert": "Bob", "William": "Bill", "James": "Jim",
    "Jennifer": "Jen", "Elizabeth": "Liz", "Katherine": "Kate",
    "Christopher": "Chris", "Joseph": "Joe", "Daniel": "Dan", "Thomas": "Tom",
    "Richard": "Rick", "Matthew": "Matt", "Anthony": "Tony", "Steven": "Steve",
    "Andrew": "Drew", "Rebecca": "Becca", "Nicholas": "Nick",
    "Samantha": "Sam", "Benjamin": "Ben", "Timothy": "Tim", "Gregory": "Greg",
    "Jessica": "Jess", "Stephanie": "Steph",
}


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


# --- knob-gated ambiguity post-passes --------------------------------------
# Each pass draws from its OWN seed stream and is a no-op when its knob is 0,
# so recipes written before the knobs regenerate byte-identically.


def _rename_person(
    person: Person,
    people: list[Person],
    charter: Charter,
    new_first: str | None = None,
    new_last: str | None = None,
) -> None:
    first, last = person.name.split(" ", 1)
    first = new_first or first
    last = new_last or last
    new_id = _person_id(first, last)
    if any(p.id == new_id for p in people if p is not person):
        raise ValueError(f"rename collision on {new_id}")
    old_id = person.id
    person.id = new_id
    person.name = f"{first} {last}"
    person.email = f"{_slugify(first)}.{_slugify(last)}@{charter.domain}".replace(
        "-", ""
    )
    for other in people:
        if other.reports_to == old_id:
            other.reports_to = new_id


def _successor_seat(incumbent: Person, first: str, last: str, charter: Charter) -> Person:
    """A new hire into the seat `incumbent` is vacating: same title, dept,
    and manager. The seat is what `headcount` counts; the person is not."""
    email = f"{_slugify(first)}.{_slugify(last)}@{charter.domain}".replace("-", "")
    return Person(
        id=_person_id(first, last),
        name=f"{first} {last}",
        title=incumbent.title,
        dept=incumbent.dept,
        reports_to=incumbent.reports_to,
        # Filled by the caller, which owns the handover gap.
        employment=EmploymentSpan(start=incumbent.employment.start),
        email=email,
        phone=incumbent.phone,
    )


def _apply_roster_churn(
    charter: Charter, people: list[Person], fake: Faker, rand
) -> None:
    """Hires, promotions, and departures across the charter's date range.

    Eligible-to-depart means "manages nobody". `reports_to` is a scalar with
    no time dimension, so a departing manager's reports would dangle or need
    to be re-pointed at a successor who did not exist when they were hired.
    That is a real limit and it is why a lead never leaves here; the
    CEO-equivalent is covered by the same rule and never departs.
    """
    churn = charter.roster_churn
    if not churn.departures and not churn.promotions:
        return
    range_start, range_end = charter.doc_culture.date_range
    span = (range_end - range_start).days

    def leave_window(p: Person) -> tuple[date, date]:
        """The dates `p` could plausibly depart on. Bounded to the first half
        of the range so BOTH holders of the seat are meaningfully documented:
        push a departure later and the successor joins with too little range
        left to appear in any document, which surfaces as
        min_mentions_per_person failing over at docplan rather than as
        anything churn can see from here. Also requires a token tenure, so
        nobody arrives and leaves in the same quarter."""
        lo = max(
            range_start + timedelta(days=int(span * 0.25)),
            p.employment.start + timedelta(days=_MIN_TENURE_DAYS),
        )
        return lo, range_start + timedelta(days=int(span * 0.5))

    managers = {p.reports_to for p in people if p.reports_to}
    # Sorted for determinism: `people` order is already stable, but an id sort
    # keeps the choice independent of how _build_people happens to emit seats.
    eligible = sorted(
        (
            p
            for p in people
            if p.id not in managers
            and p.reports_to is not None
            # Eligibility must mean "a departure really fits", not "probably".
            # _build_people plants one late joiner at 25-45% of the span,
            # which collides with the window above; skipping such a person
            # after sampling would silently drop a requested departure.
            and leave_window(p)[0] < leave_window(p)[1]
        ),
        key=lambda p: p.id,
    )

    hires: list[Person] = []
    used = {p.id for p in people}
    want_dep = min(churn.departures, len(eligible))
    if want_dep < churn.departures:
        print(
            f"foundation: roster hosts {want_dep} of "
            f"{churn.departures} requested departures "
            f"({len(eligible)} seats can host one); planting {want_dep}"
        )
    for incumbent in rand.sample(eligible, want_dep) if want_dep else []:
        lo, hi = leave_window(incumbent)
        leave = lo + timedelta(days=rand.randint(0, (hi - lo).days))
        incumbent.employment = EmploymentSpan(
            start=incumbent.employment.start, end=leave
        )
        while True:
            first, last = fake.first_name(), fake.last_name()
            if (
                _person_id(first, last) not in used
                and _slugify(first)
                and _slugify(last)
            ):
                break
        used.add(_person_id(first, last))
        successor = _successor_seat(incumbent, first, last, charter)
        # The seat sits empty for a handover gap, then refills. Bounded to
        # 60% of the range, not just `leave + gap`: at the shortest range
        # fabric allows (149 days) a 45-day gap alone would strand the
        # successor at 80% of the span with no documents left to name them.
        latest = range_start + timedelta(days=int(span * 0.6))
        joined = min(leave + timedelta(days=rand.randint(14, 45)), latest)
        successor.employment = EmploymentSpan(
            start=max(joined, leave + timedelta(days=1))
        )
        successor.phone = (
            f"+1 ({rand.choice(_AREA_CODES)}) 555-01{rand.randint(0, 99):02d}"
        )
        hires.append(successor)
    people.extend(hires)

    # Promotions: one rung up the dept's title list. Nobody who departed and
    # nobody hired as a backfill (no tenure yet) is eligible, and the roster
    # must actually have a rung above the person to move into.
    promotable = []
    for p in sorted(people, key=lambda p: p.id):
        if p.reports_to is None or p.employment.end is not None or p in hires:
            continue
        titles = charter.titles.get(p.dept, [])
        if p.title in titles and titles.index(p.title) > 0:
            promotable.append((p, titles[titles.index(p.title) - 1]))
    want_promo = min(churn.promotions, len(promotable))
    if want_promo < churn.promotions:
        print(
            f"foundation: roster hosts {want_promo} of "
            f"{churn.promotions} requested promotions "
            f"({len(promotable)} people have a rung above them); "
            f"planting {want_promo}"
        )
    for person, new_title in (
        rand.sample(promotable, want_promo) if want_promo else []
    ):
        earliest = max(person.employment.start, range_start)
        promoted = earliest + timedelta(
            days=rand.randint(int(span * 0.3), int(span * 0.6))
        )
        if promoted >= range_end:
            continue
        old_title = person.title
        person.title_history = [
            TitleSpan(
                title=old_title,
                start=person.employment.start,
                end=promoted - timedelta(days=1),
            ),
            TitleSpan(title=new_title, start=promoted),
        ]
        # Person.title is the LATEST title; title_at() resolves the rest.
        person.title = new_title


def _apply_surname_collisions(charter: Charter, people: list[Person], rand) -> None:
    for _ in range(charter.graph_targets.surname_collisions):
        staff = [p for p in people if p.reports_to is not None]
        candidates = [
            (a, b)
            for a in staff
            for b in staff
            if a is not b
            and a.name.split(" ", 1)[1] != b.name.split(" ", 1)[1]
            and a.name.split(" ", 1)[0] != b.name.split(" ", 1)[0]
        ]
        if not candidates:
            raise SystemExit(
                "foundation: roster too small for the surname_collisions knob"
            )
        keeper, renamed = rand.choice(sorted(
            candidates, key=lambda ab: (ab[0].id, ab[1].id)
        ))
        _rename_person(
            renamed, people, charter, new_last=keeper.name.split(" ", 1)[1]
        )


def _apply_nickname_aliases(charter: Charter, people: list[Person], rand) -> None:
    want = charter.graph_targets.nickname_aliases
    if not want:
        return
    staff = [p for p in people if p.reports_to is not None]
    eligible = [p for p in staff if p.name.split(" ", 1)[0] in _NICKNAMES]
    pool = iter([p for p in staff if p not in eligible])
    while len(eligible) < want:
        person = next(pool, None)
        if person is None:
            raise SystemExit(
                "foundation: roster too small for the nickname_aliases knob"
            )
        new_first = rand.choice(sorted(_NICKNAMES))
        try:
            _rename_person(person, people, charter, new_first=new_first)
        except ValueError:
            continue  # id taken; try the next roster member
        eligible.append(person)
    for person in eligible[:want]:
        nickname = _NICKNAMES[person.name.split(" ", 1)[0]]
        if nickname not in person.aliases:
            person.aliases.append(nickname)


def _apply_multi_affiliations(
    charter: Charter, externals: tuple, rand
) -> None:
    want = charter.graph_targets.multi_affiliations
    if not want:
        return
    orgs, people = externals
    if len(orgs) < 2:
        raise SystemExit(
            "foundation: multi_affiliations knob needs at least 2 external orgs"
        )
    if want > len(people):
        raise SystemExit(
            "foundation: multi_affiliations knob exceeds external_people"
        )
    range_start, range_end = charter.doc_culture.date_range
    span = (range_end - range_start).days
    for person in people[:want]:
        prior = rand.choice(
            sorted((o for o in orgs if o.id != person.org), key=lambda o: o.id)
        )
        boundary = range_start + timedelta(
            days=rand.randint(int(span * 0.3), int(span * 0.6))
        )
        person.affiliations = [
            Affiliation(org=prior.id, start=None, end=boundary),
            Affiliation(org=person.org, start=boundary + timedelta(days=1)),
        ]


def build_foundation(charter: Charter) -> Foundation:
    fake = Faker("en_US")
    fake.seed_instance(charter.seed)
    rand = rng(charter.seed, "foundation.scaffold")

    people = _build_people(charter, fake, rand)

    # Churn draws names from its OWN seeded Faker, not the shared instance.
    # `fake` is consumed in order by _build_people then _build_externals, so a
    # draw taken from it here would couple backfill names to the external
    # roster's size: change external_people and every hire's name moves. Its
    # own instance keeps the two independent, which is the same reason every
    # pass below takes its own rng stream.
    churn_fake = Faker("en_US")
    churn_fake.seed_instance(derive_seed(charter.seed, "foundation.churn"))
    _apply_roster_churn(
        charter, people, churn_fake, rng(charter.seed, "foundation.churn")
    )

    orgs, ext_people = _build_externals(charter, fake, rand)

    _apply_surname_collisions(
        charter, people, rng(charter.seed, "foundation.collisions")
    )
    _apply_nickname_aliases(
        charter, people, rng(charter.seed, "foundation.nicknames")
    )
    _apply_multi_affiliations(
        charter, (orgs, ext_people), rng(charter.seed, "foundation.affiliations")
    )

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
    # The screen fires here, before any model tokens are spent on the org.
    problems = screen_foundation(foundation)
    if problems:
        for msg, _ in problems:
            print(f"foundation: {msg}")
        raise SystemExit(
            "foundation: name screen failed; rename in the recipe or bump "
            "the seed"
        )
    write_model(paths.foundation_json, foundation)

    state.mark_done("foundation", inputs_hash=sha256_file(paths.charter_json))
    save_state(paths, state)
    print(
        f"foundation: {len(foundation.people)} people, "
        f"{len(foundation.external_orgs)} external orgs -> {paths.foundation_json}"
    )
    return 0
