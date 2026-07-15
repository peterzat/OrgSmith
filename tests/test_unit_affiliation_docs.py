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
from orgsmith.schemas import Affiliation, GraphTargets, dump_json

from conftest import REPO

pytestmark = pytest.mark.unit


def _charter(slug, **graph_target_updates):
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    charter = parse_charter_md(text, slug)
    if graph_target_updates:
        gt = charter.graph_targets.model_copy(update=graph_target_updates)
        charter = charter.model_copy(update={"graph_targets": gt})
    return charter


AFF_KNOBS = dict(multi_affiliations=1, affiliations_in_docs=True)


def _aff_org(slug="dev-mini"):
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
    # torchlake's frozen seed genuinely cannot host both sides of its
    # multi-affiliation boundary; the failure must be actionable, at
    # fabric, before any model pass.
    charter = _charter("torchlake-engineering", affiliations_in_docs=True)
    foundation = build_foundation(charter)
    with pytest.raises(SystemExit, match="Widen doc_culture.date_range"):
        build_engagements(charter, foundation)


def test_plan_direct_failure_on_empty_windows():
    charter, foundation, _ = _aff_org()
    range_start = charter.doc_culture.date_range[0]
    with pytest.raises(SystemExit, match="affiliations_in_docs"):
        affiliation_plan(foundation, [], range_start)


@pytest.mark.parametrize("slug", ["dev-mini", "torchlake-engineering"])
def test_knob_off_reproduces_committed_engagements_ledger(slug):
    # The planting pass must not run, touch fields, or consume RNG when
    # the knob is off: the committed ledgers are the oracles. torchlake
    # is the load-bearing case: it is frozen with multi_affiliations: 1,
    # and a covering-affiliation pass would rewrite it.
    charter = _charter(slug)
    assert charter.graph_targets.affiliations_in_docs is False
    rebuilt = build_engagements(charter, build_foundation(charter))
    committed = (
        REPO / "companies" / f"{slug}-metadata" / "ledger" / "engagements.json"
    ).read_text("utf-8")
    assert dump_json(rebuilt) == committed


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
    from orgsmith.authoring.contexts import _brief_person

    _, foundation, _ = _aff_org()
    xp, prior, current, org_names = _boundary_people(foundation)
    assert _brief_person(foundation, xp.id, prior.end).dept == org_names[prior.org]
    assert (
        _brief_person(foundation, xp.id, current.start).dept
        == org_names[current.org]
    )
    assert _brief_person(foundation, xp.id).dept == org_names[current.org]


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

    root = tmp_path_factory.mktemp("affrender")
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True)
    text = (REPO / "recipes" / "dev-mini" / "ORG-CHARTER.md").read_text()
    anchor = "  external_people: 3\n"
    assert anchor in text
    (dest / "ORG-CHARTER.md").write_text(
        text.replace(anchor, anchor + AFF_LINES)
    )
    paths = OrgPaths(root=root, slug="dev-mini")
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
