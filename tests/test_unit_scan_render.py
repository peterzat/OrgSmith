"""Unit tier: the scan transform in render.

Scanned pdfs become raster pages; the true text is archived; OCR-layer
docs expose every protected surface verbatim plus at least one synthetic
corruption; image-only docs expose nothing; degradation is seeded and
reproducible; provenance survives the rebuild.
"""

import re

import pytest

from orgsmith.artifacts import load_engagements, load_manifest
from orgsmith.assemble import run_assemble
from orgsmith.render import run_render
from orgsmith.render.provenance import pdf_has_marker
from orgsmith.render.scan import corrupt_pages, scan_pages_path
from orgsmith.schemas import ScanPages
from orgsmith.seeds import rng
from orgsmith.state import load_state, save_state

from conftest import build_culture_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit

# 3 pdfs: 2 scans (oldest first), 1 of them with the OCR layer.
SCAN_LINES = "  scanned_ratio: 0.67\n  ocr_layer_rate: 0.5\n"


@pytest.fixture(scope="module")
def scan_org(tmp_path_factory):
    paths = build_culture_stages(tmp_path_factory.mktemp("scanrender"), SCAN_LINES)
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


def _split(paths):
    scans = [
        e for e in load_manifest(paths) if e.render_params.get("scan") == 1
    ]
    ocr = [e for e in scans if e.render_params.get("ocr_layer") == 1]
    image_only = [e for e in scans if e.render_params.get("ocr_layer") is None]
    return scans, ocr, image_only


def _pdf_text(path) -> str:
    from pypdf import PdfReader

    return "\n".join(
        page.extract_text() or "" for page in PdfReader(str(path)).pages
    )


def test_scan_split_as_planned(scan_org):
    scans, ocr, image_only = _split(scan_org)
    assert len(scans) == 2 and len(ocr) == 1 and len(image_only) == 1


def test_scanned_pages_are_raster_images(scan_org):
    import pikepdf

    scans, _, _ = _split(scan_org)
    for entry in scans:
        with pikepdf.open(scan_org.share_dir / entry.path) as pdf:
            assert len(pdf.pages) >= 1
            for page in pdf.pages:
                xobjects = page.get("/Resources", {}).get("/XObject", {})
                images = [
                    x for x in xobjects.values()
                    if x.get("/Subtype") == pikepdf.Name.Image
                ]
                assert images, f"{entry.path}: page carries no raster image"


def test_true_text_archived_exactly_for_scans(scan_org):
    scans, _, _ = _split(scan_org)
    archived = sorted(p.name for p in scan_org.scans_dir.glob("*.pages.json"))
    expected = sorted(
        scan_pages_path(scan_org, e.doc_id).name for e in scans
    )
    assert archived == expected
    for entry in scans:
        pages = ScanPages.model_validate_json(
            scan_pages_path(scan_org, entry.doc_id).read_text("utf-8")
        )
        assert pages.doc_id == entry.doc_id
        assert any(p.strip() for p in pages.pages), "archive is empty"


def test_ocr_layer_protects_surfaces_and_corrupts_prose(scan_org):
    facts = load_engagements(scan_org).fact_index()
    _, ocr, _ = _split(scan_org)
    for entry in ocr:
        text = re.sub(r"\s+", " ", _pdf_text(scan_org.share_dir / entry.path))
        for ref in entry.facts_refs:
            assert facts[ref].rendered in text, f"{entry.path}: {ref}"
        for mention in entry.mentions:
            assert mention.surface in text, f"{entry.path}: {mention.surface}"
        archived = ScanPages.model_validate_json(
            scan_pages_path(scan_org, entry.doc_id).read_text("utf-8")
        )
        true_text = re.sub(r"\s+", " ", "\n".join(archived.pages))
        assert text != true_text, "no corruption applied"


def test_image_only_doc_exposes_no_text(scan_org):
    _, _, image_only = _split(scan_org)
    for entry in image_only:
        assert _pdf_text(scan_org.share_dir / entry.path).strip() == ""


def test_provenance_survives_rebuild(scan_org):
    scans, _, _ = _split(scan_org)
    for entry in scans:
        assert pdf_has_marker(scan_org.share_dir / entry.path), entry.path


def test_degradation_is_seeded_and_reproducible(scan_org):
    scans, _, _ = _split(scan_org)
    entry = scans[0]
    target = scan_org.share_dir / entry.path
    before = target.read_bytes()
    state = load_state(scan_org)
    state.docs[entry.doc_id].rendered_from = None
    save_state(scan_org, state)
    target.unlink()
    assert run_render(scan_org) == 0
    assert target.read_bytes() == before


def test_corrupt_pages_forces_one_corruption_and_respects_spans():
    pages = ["Only Marlon Oliver worked. l"]
    surfaces = ["Marlon Oliver"]
    # A rand that never fires: every corruption must come from the force.
    class NeverFires:
        def random(self):
            return 1.0

    out, applied = corrupt_pages(pages, surfaces, NeverFires())
    assert applied == 1
    assert "Marlon Oliver" in out[0]
    assert out[0] != pages[0]

    # A rand that always fires must still keep protected spans verbatim.
    out2, applied2 = corrupt_pages(pages, surfaces, rng(1, "test"))
    assert "Marlon Oliver" in out2[0]
