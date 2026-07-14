"""Unit tier: the validator catches deliberate corruption."""

import shutil

import pytest

from orgsmith.assemble import run_assemble
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.validate import run_validate
from orgsmith.validate.rules import RULES

from conftest import build_pure_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def org(tmp_path_factory):
    paths = build_pure_stages(tmp_path_factory.mktemp("valid-org"))
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


@pytest.fixture()
def org_copy(org, tmp_path):
    shutil.copytree(org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=org.slug)


def test_rule_catalog_v0():
    assert len(RULES) >= 6
    families = {r.id.split("-")[0] for r in RULES}
    assert {"ORG", "DATE", "FIN", "FACT", "FILE", "MAN", "PROV"} <= families


def test_generated_org_validates_clean(org):
    assert run_validate(org) == 0


def test_deleted_rendered_file_fails(org_copy, capsys):
    manifest_doc = next(
        p for p in (org_copy.share_dir).rglob("*.docx")
    )
    manifest_doc.unlink()
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "FILE-01" in out and "MAN-01" in out


def test_changed_fact_value_fails_fact_echo(org_copy, capsys):
    ledger = org_copy.engagements_json
    text = ledger.read_text()
    # Bump the first engagement fee's surface form so no doc echoes it.
    import re

    match = re.search(r'"rendered": "\$([\d,]+)"', text)
    assert match
    corrupted = text.replace(match.group(0), '"rendered": "$999,999,999"', 1)
    ledger.write_text(corrupted)
    assert run_validate(org_copy) == 1
    assert "FACT-01" in capsys.readouterr().out


def test_stray_file_in_share_fails(org_copy, capsys):
    (org_copy.share_dir / "stray-note.txt").write_text("not planned")
    assert run_validate(org_copy) == 1
    assert "MAN-01" in capsys.readouterr().out


def test_broken_reporting_tree_fails(org_copy, capsys):
    foundation = org_copy.foundation_json
    text = foundation.read_text()
    corrupted = text.replace('"reports_to": null', '"reports_to": "p:ghost.person"', 1)
    assert corrupted != text
    foundation.write_text(corrupted)
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "ORG-01" in out or "ORG-02" in out


def test_only_filter_and_unknown_rule(org):
    assert run_validate(org, only=["ORG-01", "FIN-01"]) == 0
    with pytest.raises(SystemExit):
        run_validate(org, only=["NOPE-99"])
