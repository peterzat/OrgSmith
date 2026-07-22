"""Unit tier: M13 path containment and letterhead escaping.

Covers the three hardening surfaces closed in M13:
- the single guarded doc_id-to-filename derivation shared by every sink;
- the schema pattern plus contained join on state-derived work-order names;
- context-correct escaping of charter-tainted letterhead.
"""

import html
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from orgsmith.airlock import match_author_batch, outstanding_work_order
from orgsmith.naming import doc_id_filename
from orgsmith.paths import OrgPaths
from orgsmith.render.pdf import _css_string
from orgsmith.schemas import Charter, dump_json
from orgsmith.state import BatchRef, OrgState

from conftest import REPO

pytestmark = pytest.mark.unit

_HOSTILE_WO_NAMES = ["/etc/passwd", "../evil.json", "..\\evil.json", "wo\x1b.json", ".."]
_LEGIT_WO_NAMES = ["foundation-0001.json", "author-0003.json"]


# --- one guarded doc_id -> filename helper (criterion 4) --------------------

_HOSTILE_DOC_IDS = ["../../evil", "d:0001/../../evil", "/etc/passwd", "..\\..\\evil"]


@pytest.mark.parametrize("hostile", _HOSTILE_DOC_IDS)
@pytest.mark.parametrize("suffix", [".json", ".pages.json"])
def test_doc_id_filename_rejects_traversal(hostile, suffix):
    with pytest.raises(ValueError, match="unsafe doc_id"):
        doc_id_filename(hostile, suffix)


def test_doc_id_filename_strips_colon_and_appends_suffix():
    assert doc_id_filename("d:0001", ".json") == "d0001.json"
    assert doc_id_filename("d:0001", ".pages.json") == "d0001.pages.json"


def test_all_doc_id_sinks_route_through_the_one_guarded_helper():
    """review/corpus, render/scan, and authoring/ingest must all derive their
    doc_id filename from the shared guard, so a hostile id is rejected the same
    way at every sink rather than escaping the one that forgot to check."""
    from orgsmith.authoring.ingest import docir_path as ingest_docir_path
    from orgsmith.paths import OrgPaths
    from orgsmith.render.scan import scan_pages_path
    from orgsmith.review.corpus import docir_path as review_docir_path

    paths = OrgPaths(root=Path("/tmp/orgsmith-doesnotexist"), slug="x")
    for sink in (ingest_docir_path, review_docir_path, scan_pages_path):
        for hostile in _HOSTILE_DOC_IDS:
            with pytest.raises(ValueError, match="unsafe doc_id"):
                sink(paths, hostile)
    # A legitimate id resolves inside the expected directory at every sink.
    assert ingest_docir_path(paths, "d:0001").parent == paths.docir_dir
    assert review_docir_path(paths, "d:0001").parent == paths.docir_dir
    assert scan_pages_path(paths, "d:0001").parent == paths.scans_dir


# --- state-derived work-order names: schema pattern + sink guard (crit 1,2,5) --


@pytest.mark.parametrize("hostile", _HOSTILE_WO_NAMES)
def test_hostile_work_order_name_rejected_at_the_schema(hostile):
    """A tampered state.json whose outstanding value or a batch ref carries a
    separator, '..', an absolute path, or a control character is rejected at
    load, before any sink sees it."""
    with pytest.raises(ValidationError):
        OrgState(slug="x", outstanding={"foundation": hostile})
    with pytest.raises(ValidationError):
        BatchRef(workorder=hostile)


@pytest.mark.parametrize("legit", _LEGIT_WO_NAMES)
def test_generator_written_names_are_admitted(legit):
    """The pattern admits every name the generator writes, so mid-generation
    states validate."""
    st = OrgState(slug="x", outstanding={"foundation": legit})
    assert st.outstanding["foundation"] == legit
    assert BatchRef(workorder=legit).workorder == legit


@pytest.mark.parametrize("hostile", _HOSTILE_WO_NAMES)
def test_sink_contains_a_value_that_bypassed_the_schema(tmp_path, hostile):
    """Defense in depth: if a hostile name reaches the sink anyway (validation
    bypassed via model_construct, or a future pattern relaxation), the airlock
    refuses it rather than resolving a read outside workorders_dir, and the
    control character never reaches the terminal message raw."""
    paths = OrgPaths(root=tmp_path, slug="x")

    single = OrgState.model_construct(slug="x", outstanding={"foundation": hostile})
    with pytest.raises(SystemExit) as exc:
        outstanding_work_order(paths, single, "foundation")
    assert "\x1b" not in str(exc.value)  # ESC repr'd, not passed through

    ref = BatchRef.model_construct(workorder=hostile, doc_ids=[])
    batch = OrgState.model_construct(slug="x", author_batches={"wo:author:0001": ref})
    with pytest.raises(SystemExit) as exc:
        match_author_batch(paths, batch, "wo:author:0001")
    assert "\x1b" not in str(exc.value)


def test_committed_states_load_and_round_trip_under_the_new_pattern():
    """The guard on the pattern: every committed state still loads, validates,
    and re-serializes byte-identically. A pattern that rejected a historically
    written name would fail here. (Nine as of M14: the fleet, calderwood, and
    the ashcombe-advisory email pilot.)"""
    states = sorted(REPO.glob("companies/*-metadata/state.json"))
    assert len(states) == 9
    for sj in states:
        raw = sj.read_text("utf-8")
        state = OrgState.model_validate_json(raw)
        assert dump_json(state) == raw, f"{sj} did not round-trip"


# --- letterhead context escaping (criterion 3) -----------------------------


def test_css_string_escapes_delimiters_and_controls():
    # Backslash and the string delimiter are escaped.
    assert _css_string('Acme "Co" \\ Ltd') == 'Acme \\"Co\\" \\\\ Ltd'
    # A control character (ESC, 0x1b) becomes a hex escape with a terminator.
    assert _css_string("a\x1bb") == "a\\1b b"
    # Angle brackets and ampersand are legal inside a CSS string; left as-is
    # (they are escaped in the separate HTML letterhead context instead).
    assert _css_string("A <b> & C") == "A <b> & C"


def test_letterhead_escape_is_identity_on_every_committed_charter():
    """Every committed charter is plain ASCII, so both escapes are the
    identity: adding them changes no committed letterhead output. (Nine as of
    M14: the fleet, calderwood, and the ashcombe-advisory email pilot.)"""
    charters = sorted(REPO.glob("companies/*-metadata/charter.json"))
    assert len(charters) == 9
    for cj in charters:
        charter = Charter.model_validate_json(cj.read_text("utf-8"))
        for line in (charter.name, f"www.{charter.domain}"):
            assert _css_string(line) == line, cj
            assert html.escape(line) == line, cj


def test_hostile_charter_name_renders_a_well_formed_pdf_with_the_literal_name(tmp_path):
    """A charter name carrying '<', '>', '&', and '\"' renders a well-formed PDF
    showing the literal name: the angle brackets survive as text rather than
    being parsed as an HTML tag, and the quote does not break the CSS string."""
    from pypdf import PdfReader

    from orgsmith.render.pdf import render_pdf
    from orgsmith.render.styles import StylePack
    from orgsmith.schemas import Block, DocIR, ManifestEntry

    hostile = 'Zephyr <script> & "Quotes" Ltd'
    style = StylePack(
        font_family="Georgia",
        font_generic="serif",
        accent_hex="1F3A5F",
        letterhead_lines=(hostile, "www.example.com"),
    )
    docir = DocIR(doc_id="d:0001", blocks=[Block(kind="paragraph", text="Body.")])
    entry = ManifestEntry(
        doc_id="d:0001",
        path="Firm/Doc.pdf",
        title="Doc",
        genre="engagement_letter",
        format="pdf",
        date=date(2021, 1, 4),
        authors=["p:a"],
    )
    target = tmp_path / "out.pdf"
    render_pdf(docir, entry, style, "A Author", {}, target)

    assert target.read_bytes().startswith(b"%PDF")
    text = "".join(page.extract_text() for page in PdfReader(str(target)).pages)
    assert "Zephyr" in text and "script" in text
    for ch in "<>&":
        assert ch in text, f"{ch!r} missing from extracted text {text!r}"
