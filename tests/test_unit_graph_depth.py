"""Unit tier: knob-gated roster ambiguity (collisions, nicknames,
multi-affiliation) and the stability guarantee for unchanged recipes."""

import pytest

from orgsmith.charter import parse_charter_md
from orgsmith.fabric.engagements import build_engagements
from orgsmith.fabric.graph import build_graph
from orgsmith.foundation.scaffold import _NICKNAMES, build_foundation
from orgsmith.schemas import dump_json

from conftest import REPO


pytestmark = pytest.mark.unit


def _dev_mini_charter(**graph_target_updates):
    text = (REPO / "recipes/dev-mini/ORG-CHARTER.md").read_text()
    charter = parse_charter_md(text, "dev-mini")
    if graph_target_updates:
        gt = charter.graph_targets.model_copy(update=graph_target_updates)
        charter = charter.model_copy(update={"graph_targets": gt})
    return charter


def test_default_knobs_leave_v1_roster_identical():
    # The committed dev-mini foundation must be reproducible from its
    # unchanged recipe: same ids, names, tree, emails, spans.
    from orgsmith.artifacts import load_foundation
    from orgsmith.paths import OrgPaths

    committed = load_foundation(OrgPaths(root=REPO, slug="dev-mini"))
    rebuilt = build_foundation(_dev_mini_charter())
    assert [
        (p.id, p.name, p.title, p.reports_to, p.email, p.employment.start)
        for p in rebuilt.people
    ] == [
        (p.id, p.name, p.title, p.reports_to, p.email, p.employment.start)
        for p in committed.people
    ]
    assert [o.id for o in rebuilt.external_orgs] == [
        o.id for o in committed.external_orgs
    ]


def test_knobs_are_deterministic():
    knobs = dict(surname_collisions=1, nickname_aliases=1, multi_affiliations=1)
    a = build_foundation(_dev_mini_charter(**knobs))
    b = build_foundation(_dev_mini_charter(**knobs))
    assert dump_json(a) == dump_json(b)


def test_surname_collision_pair():
    foundation = build_foundation(_dev_mini_charter(surname_collisions=1))
    last_names = [p.name.rsplit(" ", 1)[1] for p in foundation.people]
    collided = [n for n in last_names if last_names.count(n) >= 2]
    assert collided, "no surname collision planted"
    ids = [p.id for p in foundation.people]
    assert len(set(ids)) == len(ids)
    # reporting tree still resolves after renames
    for p in foundation.people:
        if p.reports_to is not None:
            foundation.person(p.reports_to)


def test_nickname_alias_planted():
    foundation = build_foundation(_dev_mini_charter(nickname_aliases=1))
    aliased = [p for p in foundation.people if p.aliases]
    assert len(aliased) >= 1
    person = aliased[0]
    first = person.name.split(" ", 1)[0]
    assert person.aliases[0] == _NICKNAMES[first]


def test_multi_affiliation_history_and_edges():
    charter = _dev_mini_charter(multi_affiliations=1)
    foundation = build_foundation(charter)
    moved = [xp for xp in foundation.external_people if xp.affiliations]
    assert len(moved) == 1
    person = moved[0]
    assert len(person.affiliations) == 2
    prior, current = person.affiliations
    assert prior.org != current.org
    assert prior.end is not None and current.start is not None
    assert prior.end < current.start
    assert current.org == person.org

    engagements = build_engagements(charter, foundation)
    graph = build_graph(charter, foundation, engagements)
    works_at = [
        e for e in graph.edges if e.kind == "works_at" and e.src == person.id
    ]
    assert len(works_at) == 2
    assert {e.dst for e in works_at} == {prior.org, current.org}


def test_engagement_services_knob():
    charter = _dev_mini_charter()
    eng_plan = charter.engagements.model_copy(
        update={"services": ["Alpha Study", "Beta Assessment"]}
    )
    charter = charter.model_copy(update={"engagements": eng_plan})
    foundation = build_foundation(charter)
    engagements = build_engagements(charter, foundation)
    services = {e.title.split(" for ")[0] for e in engagements.engagements}
    assert services <= {"Alpha Study", "Beta Assessment"}
