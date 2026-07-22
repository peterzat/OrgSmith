"""Unit tier: legacy .doc/.xls/.ppt end to end.

Planning and the soffice-absence failure run everywhere; conversion,
marker, container, and workbook tie-out tests need LibreOffice and skip
without it (CI has none by design: validation itself stays pure Python,
proven here by validating with PATH masked).
"""

import json
import shutil

import pytest

from orgsmith.artifacts import load_manifest
from orgsmith.assemble import run_assemble
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.render.provenance import MARKER_NAME, legacy_has_marker
from orgsmith.schemas import BASE_FORMAT
from orgsmith.validate import run_validate

from conftest import (
    REPO,
    build_culture_stages,
    run_authoring,
    run_enrichment,
    write_culture_recipe,
)

pytestmark = pytest.mark.unit

needs_soffice = pytest.mark.skipif(
    not shutil.which("soffice"), reason="LibreOffice not installed"
)

# 13 office docs (8 docx + 2 xlsx + 2 pptx + 1 deck short...): with the
# default dev-mini mix plus one deck, office = 8 docx + 2 xlsx + 1 pptx.
DECK_MIX = (
    "  format_mix: {docx: 8, pdf: 3, xlsx: 2, pptx: 1}\n"
)


def _write_recipe(root, culture_lines, mix=DECK_MIX, target=14):
    """dev-mini with a deck in the mix and format knobs set."""
    paths = write_culture_recipe(root, culture_lines)
    text = (paths.recipe_dir / "ORG-CHARTER.md").read_text()
    text = text.replace(
        "  format_mix: {docx: 15, pdf: 3, xlsx: 5}\n", mix
    ).replace("target_docs: 23", f"target_docs: {target}")
    (paths.recipe_dir / "ORG-CHARTER.md").write_text(text)
    return paths


# Every new format capability in one org: modern mail, decks, scans of
# both kinds, and (at ratio 1.0) every office doc a pre-2007 binary.
ALL_FORMATS_MIX = "  format_mix: {docx: 8, pdf: 3, xlsx: 2, pptx: 2, eml: 2}\n"
ALL_FORMATS_LINES = (
    "  legacy_ratio: 1.0\n  scanned_ratio: 0.67\n  ocr_layer_rate: 0.5\n"
)


def _build_stages(root, culture_lines="  legacy_ratio: 0.5\n", **kw):
    from orgsmith.charter import run_charter
    from orgsmith.docplan import run_docplan
    from orgsmith.fabric import run_fabric
    from orgsmith.foundation import run_scaffold

    paths = _write_recipe(root, culture_lines, **kw)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


def _legacy(paths):
    return [e for e in load_manifest(paths) if e.format in BASE_FORMAT]


def test_legacy_assignment_oldest_office_docs(tmp_path):
    paths = _build_stages(tmp_path)
    manifest = load_manifest(paths)
    office = sorted(
        (
            e
            for e in manifest
            if e.format in BASE_FORMAT or e.format in ("docx", "xlsx", "pptx")
        ),
        key=lambda e: (e.date, e.path),
    )
    # ratio 0.5 -> the oldest round(0.5 * n) office docs are legacy (dates
    # compare on the swapped path only within same-day ties, which stay
    # office). n is driver-derived now, so compute the split rather than pin
    # it to the old skeleton's count.
    legacy = [e for e in office if e.format in BASE_FORMAT]
    expected = round(0.5 * len(office))
    assert len(legacy) == expected
    assert legacy == office[:expected]
    for e in legacy:
        assert e.path.endswith("." + e.format)
        assert not (paths.share_dir / e.path).suffix.endswith("x")


def test_legacy_assignment_is_deterministic(tmp_path):
    a = _build_stages(tmp_path / "a")
    b = _build_stages(tmp_path / "b")
    assert a.manifest_jsonl.read_bytes() == b.manifest_jsonl.read_bytes()


def test_render_without_soffice_fails_actionably(tmp_path, monkeypatch):
    paths = _build_stages(tmp_path)
    run_enrichment(paths)
    run_authoring(paths)
    monkeypatch.setenv("PATH", str(tmp_path / "empty-bin"))
    with pytest.raises(SystemExit, match="doctor"):
        run_render(paths)


@pytest.fixture(scope="module")
def legacy_org(tmp_path_factory):
    if not shutil.which("soffice"):
        pytest.skip("LibreOffice not installed")
    # ratio 1.0 converts every office doc, covering all three binaries
    # (the financial summaries publish late, so partial ratios never
    # reach them in this recipe); mail and scans ride along so the
    # masked-PATH test validates an org holding every new format at once.
    paths = _build_stages(
        tmp_path_factory.mktemp("legacy-org"),
        ALL_FORMATS_LINES,
        mix=ALL_FORMATS_MIX,
        target=17,
    )
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


@pytest.fixture()
def org_copy(legacy_org, tmp_path):
    shutil.copytree(legacy_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(legacy_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=legacy_org.slug)


@needs_soffice
def test_legacy_org_validates_clean_without_soffice_on_path(
    legacy_org, monkeypatch
):
    # CI-safety: an org holding every new format (mail, decks-as-.ppt,
    # both scan kinds, all three binaries) validates pure Python.
    manifest = load_manifest(legacy_org)
    assert {"doc", "xls", "ppt", "eml", "pdf"} <= {e.format for e in manifest}
    layers = {
        bool(e.render_params.get("ocr_layer"))
        for e in manifest
        if e.render_params.get("scan") == 1
    }
    assert layers == {True, False}
    monkeypatch.setenv("PATH", "/nonexistent")
    assert run_validate(legacy_org) == 0


@needs_soffice
def test_converted_binaries_are_marked_ole_containers(legacy_org):
    import olefile

    from orgsmith.render.legacy import LEGACY_STREAMS

    legacy = _legacy(legacy_org)
    assert {e.format for e in legacy} == {"doc", "xls", "ppt"}
    for e in legacy:
        path = legacy_org.share_dir / e.path
        assert olefile.isOleFile(str(path)), e.path
        with olefile.OleFileIO(str(path)) as ole:
            assert ole.exists(LEGACY_STREAMS[e.format]), e.path
        assert legacy_has_marker(path), e.path


@needs_soffice
def test_xls_summary_ties_to_finance_ledger(legacy_org):
    import xlrd

    from orgsmith.artifacts import load_finance

    finance = load_finance(legacy_org)
    xls = [e for e in _legacy(legacy_org) if e.format == "xls"]
    assert xls, "no financial summary went legacy"
    for e in xls:
        fy = next(
            y for y in finance.years if y.year == int(e.render_params["year"])
        )
        sheet = xlrd.open_workbook(
            str(legacy_org.share_dir / e.path)
        ).sheet_by_name("Summary")
        assert sheet.cell_value(3, 5) == fy.revenue
        assert [sheet.cell_value(3, c) for c in range(1, 5)] == fy.quarters


@needs_soffice
def test_wrong_container_stream_fails_leg01(org_copy, capsys):
    legacy = _legacy(org_copy)
    doc = next(e for e in legacy if e.format == "doc")
    ppt = next(e for e in legacy if e.format == "ppt")
    shutil.copyfile(
        org_copy.share_dir / doc.path, org_copy.share_dir / ppt.path
    )
    assert run_validate(org_copy, only=["LEG-01"]) == 1
    assert "PowerPoint Document" in capsys.readouterr().out


@needs_soffice
def test_defaced_marker_fails_prov01(org_copy, capsys):
    entry = _legacy(org_copy)[0]
    target = org_copy.share_dir / entry.path
    token = f"{MARKER_NAME}:true".encode("utf-16-le")
    fake = f"{MARKER_NAME}:fake".encode("utf-16-le")
    data = target.read_bytes()
    if token not in data:
        token = f"{MARKER_NAME}:true".encode("ascii")
        fake = f"{MARKER_NAME}:fake".encode("ascii")
    assert token in data, "marker token not found in the binary"
    target.write_bytes(data.replace(token, fake))
    assert run_validate(org_copy, only=["PROV-01"]) == 1
    assert "synthetic-provenance marker missing" in capsys.readouterr().out


@needs_soffice
def test_stripped_legacy_format_fails_recomputation(org_copy, capsys):
    entry = next(e for e in _legacy(org_copy) if e.format == "doc")
    lines = org_copy.manifest_jsonl.read_text("utf-8").splitlines()
    out = []
    for line in lines:
        data = json.loads(line)
        if data["doc_id"] == entry.doc_id:
            data["format"] = "docx"
            data["path"] = data["path"][: -len("doc")] + "docx"
        out.append(json.dumps(data, ensure_ascii=False))
    org_copy.manifest_jsonl.write_text("\n".join(out) + "\n", "utf-8")
    assert run_validate(org_copy, only=["LEG-01"]) == 1
    assert "does not recompute" in capsys.readouterr().out


def test_corrupt_ole_binary_is_a_finding_not_a_traceback(tmp_path, capsys):
    """A file with a valid OLE magic but a garbage body makes olefile raise
    on open; LEG-01 must report a finding, not crash. Pure-python read path
    (no soffice), corrupting a COPY of the committed retro fixture.

    Hosted by cindergrove-advisors until M11b retired it; brackenridge-civil
    is the fleet's replacement legacy org and a stronger host, at
    legacy_ratio 1.0 against cindergrove's partial mix.
    """
    slug = "brackenridge-civil"
    (tmp_path / "recipes").mkdir()
    shutil.copytree(REPO / "recipes" / slug, tmp_path / "recipes" / slug)
    (tmp_path / "companies").mkdir()
    for d in (slug, f"{slug}-metadata"):
        shutil.copytree(REPO / "companies" / d, tmp_path / "companies" / d)
    paths = OrgPaths(root=tmp_path, slug=slug)
    entry = _legacy(paths)[0]
    (paths.share_dir / entry.path).write_bytes(
        b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 64
    )
    assert run_validate(paths, only=["LEG-01"]) == 1
    assert "does not open as an OLE container" in capsys.readouterr().out


def test_leg01_skips_visibly_when_knob_off(capsys):
    committed = OrgPaths(root=REPO, slug="dev-mini")
    assert run_validate(committed, only=["LEG-01"]) == 0
    out = capsys.readouterr().out
    assert "SKIP LEG-01" in out and "legacy_ratio is 0" in out


def test_unknown_format_is_a_finding_never_a_crash(tmp_path):
    """FILE-01 and PROV-01 must treat a format they do not know as a
    finding. DocFormat rejects unknown values at load time, so this guards
    the rules' own dispatch against a future format landing without
    branches."""
    from types import SimpleNamespace

    from orgsmith.validate.rules import file_01, prov_01

    share = tmp_path / "companies" / "x"
    share.mkdir(parents=True)
    (share / "mystery.wpd").write_bytes(b"not a known format")
    fake = SimpleNamespace(
        format="wpd", path="mystery.wpd", doc_id="d:0001", render_params={}
    )
    ctx = SimpleNamespace(
        manifest=[fake], paths=OrgPaths(root=tmp_path, slug="x")
    )
    findings = list(file_01(ctx))
    assert findings and "no native reader" in findings[0][0]
    findings = list(prov_01(ctx))
    assert findings and "no provenance checker" in findings[0][0]
