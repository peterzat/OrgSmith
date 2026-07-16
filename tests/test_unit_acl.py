"""Unit tier: the ACL overlay (derivation, PERMISSIONS.md, determinism)
and the ACL validator family (skips, corruption in every direction)."""

import shutil

import pytest

from orgsmith.acl import run_acl
from orgsmith.artifacts import (
    load_acl,
    load_charter,
    load_engagements,
    load_foundation,
    load_manifest,
)
from orgsmith.paths import OrgPaths
from orgsmith.schemas import write_model
from orgsmith.validate import run_validate

from conftest import build_acl_stages, build_pure_stages

pytestmark = pytest.mark.unit

ACL_RULES = ["ACL-01", "ACL-02", "ACL-03"]


@pytest.fixture(scope="module")
def dept_org(tmp_path_factory):
    return build_acl_stages(tmp_path_factory.mktemp("acl-dept"))


def test_absent_acl_loads_as_none(pure_org):
    assert load_acl(pure_org) is None


def test_open_posture_grants_everything_to_current_staff(tmp_path):
    paths = build_pure_stages(tmp_path)
    assert run_acl(paths) == 0
    acl = load_acl(paths)
    assert acl.posture == "open"
    all_paths = sorted(e.path for e in load_manifest(paths))
    people = load_foundation(paths).people
    assert [g.person for g in acl.grants] == [p.id for p in people]

    current = {p.id for p in people if p.employment.end is None}
    departed = {p.id for p in people if p.employment.end is not None}
    assert current and departed, "dev-mini's churn should plant both"
    by_person = {g.person: g.docs for g in acl.grants}
    assert all(by_person[pid] == all_paths for pid in current)
    # `open` is everyone currently employed, not everyone who ever was.
    assert all(by_person[pid] == [] for pid in departed)


def test_departed_person_keeps_no_read_access(tmp_path):
    """BACKLOG acl-blind-to-departure, resolved 2026-07-16 (M11a). The open
    posture used to hand a departed employee every document in the share,
    including ones created after they left, because grants were built over
    the roster with no reference to `employment.end`. The org modelled the
    departure as a first-class dated fact and the ACL overlay ignored it.

    Only newly visible since M8: before roster churn every person spanned the
    whole range, so an employment-blind ACL was indistinguishable from a
    correct one.
    """
    paths = build_pure_stages(tmp_path)
    assert run_acl(paths) == 0
    foundation = load_foundation(paths)
    manifest = load_manifest(paths)
    departed = [p for p in foundation.people if p.employment.end is not None]
    assert departed, "dev-mini's roster churn should retire a seat"

    acl = load_acl(paths)
    by_person = {g.person: g.docs for g in acl.grants}
    for person in departed:
        assert by_person[person.id] == [], person.name
        # The documents that motivated the finding: created after they left.
        assert [e for e in manifest if e.date > person.employment.end], (
            f"{person.name} left before the corpus ends, so post-departure "
            f"documents must exist for this test to prove anything"
        )

    # Still principals, so ACL-01 holds and the visibility suite asks the
    # question ("may they read anything?") instead of omitting the person.
    assert {g.person for g in acl.grants} == {p.id for p in foundation.people}


def test_departmental_posture_restricts(dept_org):
    acl = load_acl(dept_org)
    assert acl.posture == "departmental"
    foundation = load_foundation(dept_org)
    manifest = load_manifest(dept_org)
    engagements = load_engagements(dept_org).engagements
    ceo = next(p for p in foundation.people if p.reports_to is None)
    by_person = {g.person: set(g.docs) for g in acl.grants}
    # Employment scoping applies on top of every posture, so each expected
    # reader set below is intersected with current staff. The CEO-equivalent
    # is always current: churn only retires seats that manage nobody.
    current = {p.id for p in foundation.people if p.employment.end is None}
    assert ceo.id in current

    # The CEO-equivalent reads everything.
    assert by_person[ceo.id] == {e.path for e in manifest}

    # Engagement docs: exactly the team plus the CEO, less anyone departed.
    for entry in manifest:
        if entry.engagement is None:
            continue
        eng = next(e for e in engagements if e.id == entry.engagement)
        team = (set(eng.internal_participants) | {ceo.id}) & current
        readers = {p for p, docs in by_person.items() if entry.path in docs}
        assert readers == team, entry.path

    # Financial summaries: exactly the CEO plus the workbook author.
    for entry in manifest:
        if entry.genre != "financial_summary":
            continue
        readers = {p for p, docs in by_person.items() if entry.path in docs}
        assert readers == ({ceo.id} | set(entry.authors)) & current, entry.path

    # Firm-level non-finance docs: everyone currently employed.
    for entry in manifest:
        if entry.engagement is None and entry.genre != "financial_summary":
            readers = {p for p, docs in by_person.items() if entry.path in docs}
            assert readers == current, entry.path

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


# --- validator family --------------------------------------------------------


@pytest.fixture()
def acl_copy(dept_org, tmp_path):
    shutil.copytree(dept_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(dept_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=dept_org.slug)


def test_acl_rules_pass_on_derived_org(dept_org):
    assert run_validate(dept_org, only=ACL_RULES) == 0


def test_acl_rules_skip_visibly_without_ledger(pure_org, capsys):
    assert run_validate(pure_org, only=ACL_RULES) == 0
    out = capsys.readouterr().out
    for rule in ACL_RULES:
        assert f"SKIP {rule}" in out
    assert "predates the ACL overlay" in out


def test_unknown_principal_fails_acl01(acl_copy, capsys):
    acl = load_acl(acl_copy)
    acl.grants[0].person = "p:ghost.reader"
    write_model(acl_copy.acl_json, acl)
    assert run_validate(acl_copy, only=["ACL-01"]) == 1
    out = capsys.readouterr().out
    assert "ACL-01" in out and "p:ghost.reader" in out


def test_unreadable_document_fails_acl02(acl_copy, capsys):
    acl = load_acl(acl_copy)
    victim = acl.grants[0].docs[0]
    for grant in acl.grants:
        grant.docs = [d for d in grant.docs if d != victim]
    write_model(acl_copy.acl_json, acl)
    assert run_validate(acl_copy, only=["ACL-02"]) == 1
    assert "readable by no one" in capsys.readouterr().out


def test_tampered_grant_fails_acl03(acl_copy, capsys):
    acl = load_acl(acl_copy)
    # Grant someone a doc the posture denies them: a restricted person
    # gains the whole share.
    everything = sorted({d for g in acl.grants for d in g.docs})
    restricted = next(g for g in acl.grants if g.docs != everything)
    restricted.docs = everything
    write_model(acl_copy.acl_json, acl)
    assert run_validate(acl_copy, only=["ACL-03"]) == 1
    assert "does not match recomputation" in capsys.readouterr().out


def test_tampered_permissions_md_fails_acl03(acl_copy, capsys):
    text = acl_copy.permissions_md.read_text()
    acl_copy.permissions_md.write_text(
        text.replace("posture: departmental", "posture: open")
    )
    assert run_validate(acl_copy, only=["ACL-03"]) == 1
    assert "PERMISSIONS.md" in capsys.readouterr().out


def test_missing_permissions_md_fails_acl03(acl_copy, capsys):
    acl_copy.permissions_md.unlink()
    assert run_validate(acl_copy, only=["ACL-03"]) == 1
    assert "missing from the share" in capsys.readouterr().out


def test_deleted_ledger_fails_departmental_org(acl_copy, capsys):
    """Regression: deleting ledger/acl.json from a departmental org must
    fail every ACL rule with a missing-ledger finding (and MAN-01 must stop
    whitelisting the orphaned PERMISSIONS.md), not resurrect the pre-ACL
    grandfather skip."""
    acl_copy.acl_json.unlink()
    assert run_validate(acl_copy, only=ACL_RULES + ["MAN-01"]) == 1
    out = capsys.readouterr().out
    assert "SKIP" not in out
    assert out.count("ledger/acl.json missing") == len(ACL_RULES)
    assert "'departmental'" in out
    assert "MAN-01 [PERMISSIONS.md] file in share but not in manifest" in out


def test_stray_permissions_md_fails_man01_on_pre_acl_org(tmp_path, capsys):
    """A forged PERMISSIONS.md on an org with no ACL ledger is an
    unmanifested file; MAN-01 whitelists it only alongside acl.json."""
    paths = build_pure_stages(tmp_path)
    paths.share_dir.mkdir(parents=True, exist_ok=True)
    paths.permissions_md.write_text("# forged permissions\n")
    assert run_validate(paths, only=["MAN-01"]) == 1
    out = capsys.readouterr().out
    assert "MAN-01 [PERMISSIONS.md] file in share but not in manifest" in out


def test_ghost_principal_full_run_reports_findings(acl_copy, capsys):
    """Regression: a grant naming an unknown principal must surface as
    findings from the full rule set, not crash acl_03 with a KeyError
    inside render_permissions."""
    acl = load_acl(acl_copy)
    acl.grants[0].person = "p:ghost.reader"
    write_model(acl_copy.acl_json, acl)
    assert run_validate(acl_copy) == 1  # full rule set, no only= filter
    out = capsys.readouterr().out
    assert "p:ghost.reader" in out
    assert "does not match recomputation" in out
    # PERMISSIONS.md was rendered from the pristine ledger, which matches
    # the recomputed one; the drift check must compare against that, so
    # the tampered acl.json alone must not flag PERMISSIONS.md.
    assert "PERMISSIONS.md does not match" not in out
