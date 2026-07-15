"""Unit tier: deterministic scan planning in docplan.

Oldest pdfs get the scan flag per scanned_ratio, OCR layers land per
ocr_layer_rate from the docplan.ocr seed stream, paths stay .pdf, and a
signature_page host is never image-only.
"""

import pytest

from orgsmith.artifacts import load_manifest

from conftest import build_culture_stages

pytestmark = pytest.mark.unit

SCAN_LINES = "  scanned_ratio: 0.67\n  ocr_layer_rate: 0.5\n"


@pytest.fixture(scope="module")
def scan_org(tmp_path_factory):
    return build_culture_stages(tmp_path_factory.mktemp("scan-org"), SCAN_LINES)


def _pdfs(paths):
    return sorted(
        (e for e in load_manifest(paths) if e.format == "pdf"),
        key=lambda e: (e.date, e.path),
    )


def test_oldest_pdfs_flagged_with_layers(scan_org):
    pdfs = _pdfs(scan_org)
    assert len(pdfs) == 3
    scans = [e for e in pdfs if e.render_params.get("scan") == 1]
    # round(0.67 * 3) = 2 scans, the two oldest; round(0.5 * 2) = 1 layer.
    assert scans == pdfs[:2]
    assert all(e.path.endswith(".pdf") for e in scans)
    layered = [e for e in scans if e.render_params.get("ocr_layer") == 1]
    assert len(layered) == 1
    assert pdfs[2].render_params.get("scan") is None
    assert pdfs[2].render_params.get("ocr_layer") is None


def test_scan_planning_twice_is_identical(scan_org, tmp_path):
    again = build_culture_stages(tmp_path, SCAN_LINES)
    assert (
        again.manifest_jsonl.read_bytes() == scan_org.manifest_jsonl.read_bytes()
    )


def test_signature_page_host_is_never_image_only(tmp_path):
    # Every pdf scanned, zero OCR layers drawn: the letter hosting the
    # signature-page fee must still be forced onto the OCR path.
    paths = build_culture_stages(
        tmp_path,
        "  scanned_ratio: 1.0\n",
        extra_blocks="\nhard_cases:\n  signature_page_facts: 1\n",
    )
    manifest = load_manifest(paths)
    sig_hosts = [
        e
        for e in manifest
        if any(k.location == "signature_page" for k in e.key_facts)
    ]
    assert sig_hosts, "hard-case recipe planted no signature_page host"
    for host in sig_hosts:
        assert host.render_params.get("scan") == 1
        assert host.render_params.get("ocr_layer") == 1
    # Non-host scans drew no layer (ocr_layer_rate defaults 0).
    others = [
        e
        for e in manifest
        if e.format == "pdf" and e not in sig_hosts
    ]
    assert others and all(
        e.render_params.get("ocr_layer") is None for e in others
    )


def test_knobs_off_manifest_carries_no_scan_params(pure_org):
    for entry in load_manifest(pure_org):
        assert "scan" not in entry.render_params
        assert "ocr_layer" not in entry.render_params
