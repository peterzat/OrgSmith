"""Unit tier: SCAN validator family and the archive redirect.

A scanned org validates clean end to end (including a signature-page
fact riding an OCR scan); every corruption direction fires: stripped
flags, missing raster, layer-presence mismatches both ways, missing or
stray or gutted archives; rules skip visibly only when the charter's
scan knobs are off.
"""

import json
import shutil

import pytest

from orgsmith.artifacts import load_engagements, load_manifest
from orgsmith.assemble import run_assemble
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.render.scan import scan_pages_path
from orgsmith.validate import run_validate

from conftest import REPO, build_culture_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit

SCAN_LINES = "  scanned_ratio: 0.67\n  ocr_layer_rate: 0.5\n"


@pytest.fixture(scope="module")
def scan_org(tmp_path_factory):
    paths = build_culture_stages(tmp_path_factory.mktemp("scanval"), SCAN_LINES)
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


@pytest.fixture()
def org_copy(scan_org, tmp_path):
    shutil.copytree(scan_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(scan_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=scan_org.slug)


def _split(paths):
    scans = [e for e in load_manifest(paths) if e.render_params.get("scan") == 1]
    ocr = [e for e in scans if e.render_params.get("ocr_layer") == 1]
    image_only = [e for e in scans if e.render_params.get("ocr_layer") is None]
    plain = [
        e
        for e in load_manifest(paths)
        if e.format == "pdf" and e.render_params.get("scan") is None
    ]
    return ocr, image_only, plain


def test_scanned_org_validates_clean(scan_org):
    assert run_validate(scan_org) == 0


def test_sig_page_fact_on_ocr_scan_validates_clean(tmp_path):
    paths = build_culture_stages(
        tmp_path,
        "  scanned_ratio: 1.0\n",
        extra_blocks="\nhard_cases:\n  signature_page_facts: 1\n",
    )
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    assert run_validate(paths) == 0


def test_corrupt_scanned_pdf_is_a_finding_not_a_traceback(org_copy, capsys):
    _, image_only, _ = _split(org_copy)
    entry = image_only[0]
    (org_copy.share_dir / entry.path).write_bytes(b"%PDF-1.4 garbage no eof")
    assert run_validate(org_copy, only=["SCAN-02"]) == 1
    assert "does not open" in capsys.readouterr().out


def test_stripped_scan_flag_fails_recomputation(org_copy, capsys):
    _, image_only, _ = _split(org_copy)
    doc_id = image_only[0].doc_id
    lines = org_copy.manifest_jsonl.read_text("utf-8").splitlines()
    out = []
    for line in lines:
        entry = json.loads(line)
        if entry["doc_id"] == doc_id:
            entry["render_params"] = {}
        out.append(json.dumps(entry, ensure_ascii=False))
    org_copy.manifest_jsonl.write_text("\n".join(out) + "\n", "utf-8")
    assert run_validate(org_copy, only=["SCAN-01"]) == 1
    assert "do not recompute" in capsys.readouterr().out


def test_unrasterized_scan_fails(org_copy, capsys):
    ocr, _, plain = _split(org_copy)
    shutil.copyfile(
        org_copy.share_dir / plain[0].path, org_copy.share_dir / ocr[0].path
    )
    assert run_validate(org_copy, only=["SCAN-01"]) == 1
    assert "no raster image" in capsys.readouterr().out


def test_layer_presence_mismatch_fails_both_ways(org_copy, capsys):
    ocr, image_only, _ = _split(org_copy)
    ocr_path = org_copy.share_dir / ocr[0].path
    image_path = org_copy.share_dir / image_only[0].path
    ocr_bytes, image_bytes = ocr_path.read_bytes(), image_path.read_bytes()
    ocr_path.write_bytes(image_bytes)  # planned layer, none present
    image_path.write_bytes(ocr_bytes)  # planned image-only, layer present
    assert run_validate(org_copy, only=["SCAN-01"]) == 1
    out = capsys.readouterr().out
    assert "exposes no extractable text" in out
    assert "image-only scan exposes extractable text" in out


def test_missing_archive_fails_scan02_and_obligations(org_copy, capsys):
    _, image_only, _ = _split(org_copy)
    scan_pages_path(org_copy, image_only[0].doc_id).unlink()
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "no archived page text" in out
    # The image-only doc's obligations fail loudly through the redirect.
    assert "FACT-01" in out or "MENT-01" in out


def test_stray_archive_fails(org_copy, capsys):
    stray = org_copy.scans_dir / "d9999.pages.json"
    stray.write_text(
        json.dumps(
            {
                "schema_id": "orgsmith/scan-pages@1",
                "doc_id": "d:9999",
                "pages": ["never planned"],
            }
        ),
        "utf-8",
    )
    assert run_validate(org_copy, only=["SCAN-02"]) == 1
    assert "never scanned" in capsys.readouterr().out


def test_gutted_archive_fails_image_only_fact_echo(org_copy, capsys):
    facts = load_engagements(org_copy).fact_index()
    _, image_only, _ = _split(org_copy)
    entry = image_only[0]
    assert entry.facts_refs, "image-only doc plants no facts"
    archive = scan_pages_path(org_copy, entry.doc_id)
    data = json.loads(archive.read_text("utf-8"))
    surface = facts[entry.facts_refs[0]].rendered
    data["pages"] = [p.replace(surface, "REDACTED") for p in data["pages"]]
    archive.write_text(json.dumps(data, ensure_ascii=False), "utf-8")
    assert run_validate(org_copy, only=["FACT-01"]) == 1
    assert "not found in extractable text" in capsys.readouterr().out


def test_scan_rules_skip_visibly_when_knobs_off(capsys):
    committed = OrgPaths(root=REPO, slug="dev-mini")
    assert run_validate(committed, only=["SCAN-01", "SCAN-02"]) == 0
    out = capsys.readouterr().out
    assert "SKIP SCAN-01" in out and "SKIP SCAN-02" in out
    assert "scanned_ratio is 0" in out
