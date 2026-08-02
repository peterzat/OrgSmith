"""Unit tier: the shared extractable-text reader (orgsmith/doctext.py).

The validator's text obligations, the eval emitter's rendered-truth scans,
and the retrieval baselines all read this one module, so "what text does
this file expose?" has a single answer. These tests pin that: the validator
still routes through it (parity), and importing it never drags in the
generation-only rendering stack.
"""

import subprocess
import sys

import pytest

from orgsmith.doctext import DocText, image_only
from orgsmith.paths import OrgPaths
from orgsmith.validate.rules import Context

from conftest import REPO

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def ctx():
    return Context.load(OrgPaths(root=REPO, slug="dev-mini"))


def test_context_delegates_to_the_shared_reader(ctx):
    """Parity: every Context text accessor returns exactly what a standalone
    DocText over the same org returns, for every format the org holds."""
    standalone = DocText(ctx.paths, ctx.engagements, ctx.foundation)
    for entry in ctx.manifest:
        assert ctx.doc_text(entry) == standalone.text(entry), entry.path
        if entry.format == "pdf":
            assert ctx.doc_pages(entry) == standalone.pages(entry), entry.path
            assert ctx.pdf_layout_text(entry) == standalone.layout_text(entry)


def test_context_shares_one_reader_instance(ctx):
    """The cache is paid once per org, not once per accessor."""
    assert ctx.doctext is ctx.doctext


def test_reader_extracts_text_for_every_committed_format(ctx):
    """A format the reader cannot read raises rather than returning "",
    so a silent empty extraction can never pass a text obligation. The
    workbook formats are the deliberate exception (checked cell-by-cell)."""
    seen = set()
    for entry in ctx.manifest:
        text = ctx.doc_text(entry)
        seen.add(entry.format)
        if entry.format not in ("xlsx", "xls"):
            assert text.strip(), f"no extractable text from {entry.path}"
    assert {"docx", "pdf", "xlsx"} <= seen


def test_image_only_reads_the_scan_flags():
    class Entry:
        def __init__(self, **params):
            self.render_params = params

    assert image_only(Entry(scan=1))
    assert not image_only(Entry(scan=1, ocr_layer=1))
    assert not image_only(Entry())


def test_importing_doctext_does_not_import_weasyprint():
    """A validate-only or score-only install must not need the Pango stack.
    Run in a fresh interpreter so an earlier test's import cannot mask it."""
    code = (
        "import sys, orgsmith.doctext; "
        "assert 'weasyprint' not in sys.modules, sorted(sys.modules)"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
