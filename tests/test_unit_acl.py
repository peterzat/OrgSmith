"""Unit tier: the ACL overlay (derivation, PERMISSIONS.md, determinism)."""

import pytest

from orgsmith.acl import run_acl
from orgsmith.artifacts import (
    load_acl,
    load_charter,
    load_engagements,
    load_foundation,
    load_manifest,
)

from conftest import build_acl_stages, build_pure_stages

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def dept_org(tmp_path_factory):
    return build_acl_stages(tmp_path_factory.mktemp("acl-dept"))


def test_absent_acl_loads_as_none(pure_org):
    assert load_acl(pure_org) is None


def test_open_posture_grants_everything(tmp_path):
    paths = build_pure_stages(tmp_path)
    assert run_acl(paths) == 0
    acl = load_acl(paths)
    assert acl.posture == "open"
    all_paths = sorted(e.path for e in load_manifest(paths))
    people = load_foundation(paths).people
    assert [g.person for g in acl.grants] == [p.id for p in people]
    assert all(g.docs == all_paths for g in acl.grants)


def test_departmental_posture_restricts(dept_org):
    acl = load_acl(dept_org)
    assert acl.posture == "departmental"
    foundation = load_foundation(dept_org)
    manifest = load_manifest(dept_org)
    engagements = load_engagements(dept_org).engagements
    ceo = next(p for p in foundation.people if p.reports_to is None)
    by_person = {g.person: set(g.docs) for g in acl.grants}

    # The CEO-equivalent reads everything.
    assert by_person[ceo.id] == {e.path for e in manifest}

    # Engagement docs: exactly the team plus the CEO.
    for entry in manifest:
        if entry.engagement is None:
            continue
        eng = next(e for e in engagements if e.id == entry.engagement)
        team = set(eng.internal_participants) | {ceo.id}
        readers = {p for p, docs in by_person.items() if entry.path in docs}
        assert readers == team, entry.path

    # Financial summaries: exactly the CEO plus the workbook author.
    for entry in manifest:
        if entry.genre != "financial_summary":
            continue
        readers = {p for p, docs in by_person.items() if entry.path in docs}
        assert readers == {ceo.id} | set(entry.authors), entry.path

    # Firm-level non-finance docs: everyone.
    for entry in manifest:
        if entry.engagement is None and entry.genre != "financial_summary":
            readers = {p for p, docs in by_person.items() if entry.path in docs}
            assert readers == set(by_person), entry.path

    # The posture actually restricts: someone is denied something.
    assert any(
        set(g.docs) != {e.path for e in manifest} for g in acl.grants
    )


def test_every_doc_readable_by_someone(dept_org):
    acl = load_acl(dept_org)
    readable = {doc for g in acl.grants for doc in g.docs}
    assert readable == {e.path for e in load_manifest(dept_org)}


def test_rederivation_is_byte_identical(dept_org):
    acl_before = dept_org.acl_json.read_bytes()
    perms_before = dept_org.permissions_md.read_bytes()
    assert run_acl(dept_org) == 0
    assert dept_org.acl_json.read_bytes() == acl_before
    assert dept_org.permissions_md.read_bytes() == perms_before


def test_permissions_md_lists_every_person(dept_org):
    text = dept_org.permissions_md.read_text()
    charter = load_charter(dept_org)
    assert charter.name in text
    assert "posture: departmental" in text
    for person in load_foundation(dept_org).people:
        assert f"## {person.name} ({person.title})" in text
