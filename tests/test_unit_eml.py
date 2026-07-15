"""Unit tier: engagement mail (.eml) end to end.

Round-robin planning, deterministic headers tied to the ledger, byte-
identical re-render, the marker header, and EML-01 corruption both ways.
"""

import shutil
from email import policy
from email.parser import BytesParser

import pytest

from orgsmith.artifacts import load_engagements, load_manifest
from orgsmith.assemble import run_assemble
from orgsmith.paths import OrgPaths
from orgsmith.render import people_index, run_render
from orgsmith.render.eml import MARKER_HEADER, expected_headers
from orgsmith.render.provenance import eml_has_marker
from orgsmith.validate import run_validate

from conftest import REPO, build_mix_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit

# 4 mails over 3 engagements: the round-robin wraps one engagement.
EML_MIX = {"docx": 8, "pdf": 3, "xlsx": 2, "eml": 4}


@pytest.fixture(scope="module")
def eml_org(tmp_path_factory):
    paths = build_mix_stages(tmp_path_factory.mktemp("eml-org"), EML_MIX)
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


@pytest.fixture()
def eml_org_copy(eml_org, tmp_path):
    shutil.copytree(eml_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(eml_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=eml_org.slug)


def _mails(paths):
    return [e for e in load_manifest(paths) if e.format == "eml"]


def _parse(path):
    with open(path, "rb") as fh:
        return BytesParser(policy=policy.default).parse(fh)


def test_mails_planned_round_robin(eml_org):
    mails = _mails(eml_org)
    assert len(mails) == EML_MIX["eml"]
    by_eng = {}
    for m in mails:
        assert m.genre == "engagement_email"
        assert m.path.endswith(".eml")
        by_eng[m.engagement] = by_eng.get(m.engagement, 0) + 1
    assert len(by_eng) == 3  # every engagement got mail
    assert max(by_eng.values()) == 2  # the wrap landed a second thread mail


def test_rendered_mail_headers_recompute_and_marker(eml_org):
    from orgsmith.artifacts import load_charter, load_foundation

    charter = load_charter(eml_org)
    people = people_index(load_foundation(eml_org))
    for entry in _mails(eml_org):
        path = eml_org.share_dir / entry.path
        msg = _parse(path)
        for name, want in expected_headers(
            entry, people, charter.slug, charter.domain
        ).items():
            assert str(msg[name]) == want, f"{entry.path}: {name}"
        assert eml_has_marker(path)


def test_mail_body_carries_facts_and_mentions(eml_org):
    facts = load_engagements(eml_org).fact_index()
    for entry in _mails(eml_org):
        msg = _parse(eml_org.share_dir / entry.path)
        body = msg.get_body(preferencelist=("plain",)).get_content()
        for ref in entry.facts_refs:
            assert facts[ref].rendered in body, f"{entry.path}: {ref}"
        for mention in entry.mentions:
            assert mention.surface in body, f"{entry.path}: {mention.surface}"


def test_mail_renders_byte_identically(eml_org):
    from orgsmith.artifacts import load_charter, load_foundation
    from orgsmith.authoring.ingest import docir_path
    from orgsmith.render.eml import render_eml
    from orgsmith.render.resolve import resolve_docir
    from orgsmith.schemas import DocIR

    charter = load_charter(eml_org)
    people = people_index(load_foundation(eml_org))
    facts = load_engagements(eml_org).fact_index()
    entry = _mails(eml_org)[0]
    docir = DocIR.model_validate_json(
        docir_path(eml_org, entry.doc_id).read_text("utf-8")
    )
    resolved = resolve_docir(docir, facts)
    first = render_eml(resolved, entry, people, charter.slug, charter.domain)
    second = render_eml(resolved, entry, people, charter.slug, charter.domain)
    assert first == second
    assert first == (eml_org.share_dir / entry.path).read_bytes()


def test_eml_org_validates_clean(eml_org):
    assert run_validate(eml_org) == 0


def test_tampered_header_fails_eml01(eml_org_copy, capsys):
    entry = _mails(eml_org_copy)[0]
    target = eml_org_copy.share_dir / entry.path
    text = target.read_bytes().decode("utf-8")
    assert "Date: " in text
    tampered = text.replace("Date: ", "Date: Mon, 1 Jan 1990 00:00:00 +0000\nX-Was-Date: ", 1)
    target.write_bytes(tampered.encode("utf-8"))
    assert run_validate(eml_org_copy, only=["EML-01"]) == 1
    assert "does not recompute" in capsys.readouterr().out


def test_stripped_marker_header_fails_prov(eml_org_copy, capsys):
    entry = _mails(eml_org_copy)[0]
    target = eml_org_copy.share_dir / entry.path
    lines = target.read_bytes().decode("utf-8").splitlines(keepends=True)
    kept = [ln for ln in lines if not ln.startswith(MARKER_HEADER)]
    assert len(kept) < len(lines)
    target.write_bytes("".join(kept).encode("utf-8"))
    assert run_validate(eml_org_copy, only=["PROV-01"]) == 1
    assert "synthetic-provenance marker missing" in capsys.readouterr().out


def test_eml01_fires_when_knob_on_but_manifest_stripped(eml_org_copy, capsys):
    lines = eml_org_copy.manifest_jsonl.read_text("utf-8").splitlines()
    kept = [ln for ln in lines if '"format": "eml"' not in ln]
    assert len(kept) < len(lines)
    eml_org_copy.manifest_jsonl.write_text("\n".join(kept) + "\n", "utf-8")
    assert run_validate(eml_org_copy, only=["EML-01"]) == 1
    assert "plans no eml documents" in capsys.readouterr().out


def test_eml01_skips_visibly_when_knob_off(capsys):
    committed = OrgPaths(root=REPO, slug="dev-mini")
    assert run_validate(committed, only=["EML-01"]) == 0
    out = capsys.readouterr().out
    assert "SKIP EML-01" in out and "format_mix.eml is 0" in out
