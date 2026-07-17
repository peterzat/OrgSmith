"""Unit tier: the affiliations_in_docs knob and the RNG-free fabric
planting pass (charter dependency, determinism, both-sides designation,
covering participants, actionable failure, knob-off byte-identity)."""

import json

import pytest
from pydantic import ValidationError

from orgsmith.charter import parse_charter_md
from orgsmith.fabric.engagements import (
    LETTER_LEAD_DAYS,
    affiliation_covering,
    affiliation_plan,
    build_engagements,
    padded_window,
    xp_affiliations,
)
from orgsmith.foundation.scaffold import build_foundation
from orgsmith.paths import OrgPaths
from orgsmith.schemas import Affiliation, GraphTargets, RosterChurn, dump_json

from conftest import REPO

pytestmark = pytest.mark.unit


def _charter(slug, **graph_target_updates):
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    charter = parse_charter_md(text, slug)
    if graph_target_updates:
        gt = charter.graph_targets.model_copy(update=graph_target_updates)
        charter = charter.model_copy(update={"graph_targets": gt})
    # Every test in this file is about the affiliations_in_docs knob. Churn is
    # on by default in M8, and a departure that narrows the delivery pool
    # mid-history changes which engagements a multi-affiliation person can be
    # placed on -- real behavior, but a different knob's, and it turns these
    # into flaky seed-dependent placements. Pin it off so they test one thing.
    return charter.model_copy(
        update={"roster_churn": RosterChurn(departures=0, promotions=0)}
    )


AFF_KNOBS = dict(multi_affiliations=1, affiliations_in_docs=True)


def _aff_org(slug="saltmarsh-environmental"):
    # saltmarsh is the fixture that actually ships affiliations_in_docs, so
    # it is the honest host. These tests used to bolt the knob onto dev-mini,
    # which worked until M8's staffing rotation shifted engagement dates and
    # dev-mini's seed could no longer place its multi-affiliation person on
    # both sides. fernhollow hosted this from M8 until M11b retired it;
    # saltmarsh is its replacement, sized for exactly this and placing
    # cleanly (verdant-health is the fleet's other honest host).
    charter = _charter(slug, **AFF_KNOBS)
    foundation = build_foundation(charter)
    return charter, foundation, build_engagements(charter, foundation)


def test_knob_requires_multi_affiliations():
    with pytest.raises(ValidationError, match="multi_affiliations"):
        GraphTargets(external_orgs=2, external_people=2, affiliations_in_docs=True)
    gt = GraphTargets(
        external_orgs=2,
        external_people=2,
        multi_affiliations=1,
        affiliations_in_docs=True,
    )
    assert gt.affiliations_in_docs


def test_knob_defaults_off_on_existing_schema_id():
    charter = _charter("dev-mini")
    assert charter.schema_id == "orgsmith/charter@1"
    assert charter.graph_targets.affiliations_in_docs is False


def test_xp_affiliations_implicit_and_explicit():
    _, foundation, _ = _aff_org()
    for xp in foundation.external_people:
        affs = xp_affiliations(xp)
        if xp.affiliations:
            assert affs == xp.affiliations
        else:
            assert affs == [Affiliation(org=xp.org)]
            assert affs[0].start is None and affs[0].end is None


def test_planting_is_deterministic():
    _, _, a = _aff_org()
    _, _, b = _aff_org()
    assert dump_json(a) == dump_json(b)


def test_multi_affiliation_person_designated_on_both_sides():
    charter, foundation, ledger = _aff_org()
    xp = next(p for p in foundation.external_people if p.affiliations)
    prior, current = xp.affiliations
    by_side = {prior.org: [], current.org: []}
    for eng in ledger.engagements:
        if xp.id in eng.external_participants and eng.client in by_side:
            by_side[eng.client].append(eng.id)
    assert by_side[prior.org], "no engagement under the prior employer"
    assert by_side[current.org], "no engagement under the current employer"


def test_participants_hold_covering_affiliations():
    charter, foundation, ledger = _aff_org()
    range_start = charter.doc_culture.date_range[0]
    people = {xp.id: xp for xp in foundation.external_people}
    for eng in ledger.engagements:
        lo, hi = padded_window(eng.start, eng.end, range_start)
        for xp_id in eng.external_participants:
            assert affiliation_covering(people[xp_id], eng.client, lo, hi), (
                f"{xp_id} has no affiliation to {eng.client} covering "
                f"{lo}..{hi} ({eng.id})"
            )


def test_reassignment_rebuilds_client_dependent_fields():
    charter, foundation, ledger = _aff_org()
    org_names = {o.id: o.name for o in foundation.external_orgs}
    for eng in ledger.engagements:
        client_name = org_names[eng.client]
        assert eng.title.endswith(f"for {client_name}")
        assert f"for {client_name}, running" in eng.summary
        fact = next(f for f in eng.facts if f.id == f"f:{eng.id}.client")
        assert fact.value == client_name and fact.rendered == client_name


def test_impossible_placement_fails_actionably():
    # dev-mini's seed genuinely cannot host both sides of a multi-affiliation
    # boundary; the failure must be actionable, at fabric, before any model
    # pass. torchlake hosted this until M11b retired it. dev-mini is the
    # honest replacement rather than a contrivance: _aff_org's comment above
    # records that M8's staffing rotation is what cost dev-mini this
    # placement, so the recipe that failed the knob is now the one pinning
    # the failure. Verified to raise on the message below, not merely to
    # raise: dev-mini reports "cannot place xp:stephanie.campos on an
    # engagement under x:johnson-and-sons".
    charter = _charter("dev-mini", **AFF_KNOBS)
    foundation = build_foundation(charter)
    with pytest.raises(SystemExit, match="Widen doc_culture.date_range"):
        build_engagements(charter, foundation)


def test_plan_direct_failure_on_empty_windows():
    charter, foundation, _ = _aff_org()
    range_start = charter.doc_culture.date_range[0]
    with pytest.raises(SystemExit, match="affiliations_in_docs"):
        affiliation_plan(foundation, [], range_start)


def test_knob_off_leaves_clients_on_their_simple_assignment():
    """The affiliations_in_docs OFF path must not run the covering-affiliation
    reassignment: clients stay on the plain `idx % external_orgs` mapping and
    no external person is placed on two different clients.

    This was a byte-pin against torchlake's committed engagements.json until
    M8. Rotation is unconditional and staffing lives in that ledger, so the
    committed bytes are no longer reproducible and the pin could not survive
    -- the same reason test_org_regen.py narrowed to dev-mini. The property
    the pin actually protected is behavioral and is asserted directly here,
    churn pinned off so only the affiliations pass is under test.

    Hosted by torchlake's real recipe (multi_affiliations: 1, knob off) until
    M11b retired it. No surviving recipe has that combination -- the fleet's
    two multi_affiliations hosts, saltmarsh and verdant, both ship the knob
    ON -- so the knob is forced off here instead of found off. That is a
    weaker setup and worth naming: it tests the off path of a recipe that
    ships on, rather than a recipe someone actually wrote that way. The
    property under test is unchanged, and multi_affiliations: 1 still comes
    from the real recipe, so there is still a multi-affiliation person the
    off path could wrongly reassign."""
    charter = _charter("saltmarsh-environmental", affiliations_in_docs=False)
    assert charter.graph_targets.affiliations_in_docs is False
    assert charter.graph_targets.multi_affiliations == 1, (
        "the host recipe must still plant a multi-affiliation person, or the "
        "knob-off assertion below is vacuous"
    )
    foundation = build_foundation(charter)
    ledger = build_engagements(charter, foundation)

    orgs = foundation.external_orgs
    for idx, eng in enumerate(ledger.engagements):
        assert eng.client == orgs[idx % len(orgs)].id, (
            "knob-off clients must follow the plain idx-mod assignment; "
            "a reassignment ran"
        )
    # No external person spans two clients when the pass is off.
    seen: dict[str, str] = {}
    for eng in ledger.engagements:
        for xp in eng.external_participants:
            assert seen.setdefault(xp, eng.client) == eng.client, (
                f"{xp} placed on two clients with the knob off"
            )


def _boundary_people(foundation):
    xp = next(p for p in foundation.external_people if p.affiliations)
    prior, current = xp.affiliations
    org_names = {o.id: o.name for o in foundation.external_orgs}
    return xp, prior, current, org_names


def test_people_index_resolves_employer_per_date():
    from orgsmith.render import people_index

    _, foundation, _ = _aff_org()
    xp, prior, current, org_names = _boundary_people(foundation)
    before = people_index(foundation, at=prior.end)
    after = people_index(foundation, at=current.start)
    assert before[xp.id]["title"] == f"{xp.title}, {org_names[prior.org]}"
    assert after[xp.id]["title"] == f"{xp.title}, {org_names[current.org]}"
    # without a date the current employer stands (single-era orgs)
    plain = people_index(foundation)
    assert plain[xp.id]["title"] == f"{xp.title}, {org_names[current.org]}"
    # name and email are single ledger-owned fields: era-invariant
    assert before[xp.id]["name"] == after[xp.id]["name"]
    assert before[xp.id]["email"] == after[xp.id]["email"]


def test_brief_person_resolves_employer_per_date():
    """With affiliations_in_docs on (historical_employer=True), the brief's
    dept line follows the doc date across the employer boundary."""
    from orgsmith.authoring.contexts import _brief_person

    _, foundation, _ = _aff_org()
    xp, prior, current, org_names = _boundary_people(foundation)
    assert (
        _brief_person(foundation, xp.id, prior.end, True).dept
        == org_names[prior.org]
    )
    assert (
        _brief_person(foundation, xp.id, current.start, True).dept
        == org_names[current.org]
    )


def test_brief_person_keeps_current_employer_when_the_knob_is_off():
    """The knob's off state, which torchlake-engineering ships: affiliation
    history exists in the graph, but documents brief the current employer.
    M8 date-scopes titles unconditionally and must not drag this with it."""
    from orgsmith.authoring.contexts import _brief_person

    _, foundation, _ = _aff_org()
    xp, prior, current, org_names = _boundary_people(foundation)
    for when in (prior.end, current.start):
        assert (
            _brief_person(foundation, xp.id, when, False).dept
            == org_names[current.org]
        )


AFF_LINES = "  multi_affiliations: 1\n  affiliations_in_docs: true\n"


@pytest.fixture(scope="module")
def aff_render_org(tmp_path_factory):
    """dev-mini with the affiliation knobs on, authored (scripted) and
    rendered."""
    from orgsmith.assemble import run_assemble
    from orgsmith.charter import run_charter
    from orgsmith.docplan import run_docplan
    from orgsmith.fabric import run_fabric
    from orgsmith.foundation import run_scaffold
    from orgsmith.render import run_render

    from conftest import run_authoring, run_enrichment

    # saltmarsh ships the affiliation knobs; dev-mini used to have them
    # bolted on, but M8's staffing rotation shifted its dates past a working
    # placement (see _aff_org). fernhollow hosted this until M11b retired it.
    # Churn is pinned off in the recipe text so this render test exercises
    # only the affiliations path.
    slug = "saltmarsh-environmental"
    root = tmp_path_factory.mktemp("affrender")
    dest = root / "recipes" / slug
    dest.mkdir(parents=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    anchor = "  affiliations_in_docs: true\n"
    assert anchor in text
    text = text.replace(
        anchor, anchor + "\nroster_churn:\n  departures: 0\n  promotions: 0\n"
    )
    (dest / "ORG-CHARTER.md").write_text(text)
    paths = OrgPaths(root=root, slug=slug)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


def test_rendered_letters_show_era_correct_employer(aff_render_org):
    import re

    from pypdf import PdfReader

    from orgsmith.artifacts import (
        load_engagements,
        load_foundation,
        load_manifest,
    )

    foundation = load_foundation(aff_render_org)
    ledger = load_engagements(aff_render_org)
    manifest = load_manifest(aff_render_org)
    xp, prior, current, org_names = _boundary_people(foundation)
    sides = {prior.org: current.org, current.org: prior.org}
    for side_org, other_org in sides.items():
        eng = next(
            e
            for e in ledger.engagements
            if e.client == side_org and xp.id in e.external_participants
        )
        letter = next(
            m
            for m in manifest
            if m.genre == "engagement_letter" and m.engagement == eng.id
        )
        raw = "\n".join(
            page.extract_text() or ""
            for page in PdfReader(
                str(aff_render_org.share_dir / letter.path)
            ).pages
        )
        text = re.sub(r"\s+", " ", raw)
        # the sigblock title line is the era surface: the xp signs under
        # the employer matching the letter's date
        assert f"{xp.title}, {org_names[side_org]}" in text
        assert f"{xp.title}, {org_names[other_org]}" not in text


def test_work_order_briefs_show_era_correct_employer(aff_render_org):
    import json

    from orgsmith.artifacts import (
        load_engagements,
        load_foundation,
        load_manifest,
    )

    foundation = load_foundation(aff_render_org)
    ledger = load_engagements(aff_render_org)
    manifest = load_manifest(aff_render_org)
    xp, prior, current, org_names = _boundary_people(foundation)
    # authoring already converged; inspect the archived work orders
    orders = sorted(aff_render_org.workorders_dir.glob("author-*.json"))
    assert orders
    briefs = {}  # doc_id -> dept briefed for the boundary xp
    for path in orders:
        data = json.loads(path.read_text("utf-8"))
        for doc in data.get("docs", []):
            for person in doc["authors"] + doc["participants"]:
                if person["id"] == xp.id:
                    briefs[doc["doc_id"]] = person["dept"]
    entries = {m.doc_id: m for m in manifest}
    boundary = prior.end
    checked = 0
    for doc_id, dept in briefs.items():
        doc_date = entries[doc_id].date
        expected = prior.org if doc_date <= boundary else current.org
        assert dept == org_names[expected], (doc_id, doc_date)
        checked += 1
    assert checked >= 2


# --- AFF validator rules ---------------------------------------------------


@pytest.fixture()
def aff_org_copy(aff_render_org, tmp_path):
    import shutil

    shutil.copytree(aff_render_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(aff_render_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=aff_render_org.slug)


def _edit_json(path, mutate):
    data = json.loads(path.read_text("utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2), "utf-8")


def test_aff_rules_pass_and_never_skip_with_knob_on(aff_render_org, capsys):
    from orgsmith.validate import run_validate

    assert run_validate(aff_render_org, only=["AFF-01", "AFF-02"]) == 0
    assert "SKIP" not in capsys.readouterr().out


def test_aff_rules_skip_visibly_with_knob_off(capsys):
    from orgsmith.validate import run_validate

    committed = OrgPaths(root=REPO, slug="dev-mini")
    assert run_validate(committed, only=["AFF-01", "AFF-02"]) == 0
    out = capsys.readouterr().out
    assert "SKIP AFF-01" in out and "SKIP AFF-02" in out
    assert "affiliations_in_docs knob is off" in out


def _designated(paths):
    """(xp, prior, current, engagements ledger path, engagement) for the
    boundary person's prior-side engagement."""
    from orgsmith.artifacts import load_engagements, load_foundation

    foundation = load_foundation(paths)
    ledger = load_engagements(paths)
    xp, prior, current, org_names = _boundary_people(foundation)
    eng = next(
        e
        for e in ledger.engagements
        if e.client == prior.org and xp.id in e.external_participants
    )
    return xp, prior, current, eng


def test_aff01_fails_tampered_participant(aff_org_copy, capsys):
    from orgsmith.validate import run_validate

    xp, _, _, eng = _designated(aff_org_copy)

    def mutate(data):
        for e in data["engagements"]:
            if e["id"] == eng.id:
                e["external_participants"] = []

    _edit_json(
        aff_org_copy.engagements_json, mutate
    )
    assert run_validate(aff_org_copy, only=["AFF-01"]) == 1
    assert "do not recompute" in capsys.readouterr().out


def test_aff01_fails_undone_reassignment(aff_org_copy, capsys):
    from orgsmith.artifacts import load_foundation
    from orgsmith.validate import run_validate

    xp, prior, current, eng = _designated(aff_org_copy)
    foundation = load_foundation(aff_org_copy)
    other = next(
        o.id for o in foundation.external_orgs if o.id != eng.client
    )

    def mutate(data):
        for e in data["engagements"]:
            if e["id"] == eng.id:
                e["client"] = other

    _edit_json(
        aff_org_copy.engagements_json, mutate
    )
    assert run_validate(aff_org_copy, only=["AFF-01"]) == 1
    assert "client does not recompute" in capsys.readouterr().out


def test_aff01_fails_shifted_affiliation_window(aff_org_copy, capsys):
    from orgsmith.validate import run_validate

    xp, _, _, _ = _designated(aff_org_copy)

    def mutate(data):
        for person in data["external_people"]:
            if person["id"] == xp.id:
                person["affiliations"][0]["end"] = "2099-01-01"
                person["affiliations"][1]["start"] = "2099-01-02"

    _edit_json(aff_org_copy.foundation_json, mutate)
    assert run_validate(aff_org_copy, only=["AFF-01"]) == 1
    assert "recompute" in capsys.readouterr().out


def test_aff02_fails_person_missing_from_one_side(aff_org_copy, capsys):
    from orgsmith.validate import run_validate

    xp, prior, _, eng = _designated(aff_org_copy)

    def mutate(data):
        for e in data["engagements"]:
            if e["id"] == eng.id:
                e["external_participants"] = []

    _edit_json(
        aff_org_copy.engagements_json, mutate
    )
    assert run_validate(aff_org_copy, only=["AFF-02"]) == 1
    out = capsys.readouterr().out
    assert f"{xp.id} never participates" in out and prior.org in out


def test_aff02_fails_stripped_affiliations(aff_org_copy, capsys):
    from orgsmith.validate import run_validate

    xp, _, _, _ = _designated(aff_org_copy)

    def mutate(data):
        for person in data["external_people"]:
            person["affiliations"] = []

    _edit_json(aff_org_copy.foundation_json, mutate)
    assert run_validate(aff_org_copy, only=["AFF-02"]) == 1
    assert "affiliation history stripped" in capsys.readouterr().out


def test_letter_lead_days_shared_with_docplan(pure_org):
    # docplan dates the engagement letter start - LETTER_LEAD_DAYS
    # (clamped); the covering window must agree or a letter could be
    # signed by someone the ledger says works elsewhere on that date.
    from orgsmith.artifacts import load_engagements, load_manifest

    engagements = {e.id: e for e in load_engagements(pure_org).engagements}
    range_start = _charter("dev-mini").doc_culture.date_range[0]
    letters = [
        e for e in load_manifest(pure_org) if e.genre == "engagement_letter"
    ]
    assert letters
    for entry in letters:
        eng = engagements[entry.engagement]
        lo, _ = padded_window(eng.start, eng.end, range_start)
        assert entry.date == lo
