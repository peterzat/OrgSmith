"""M9 letter-rendering fixes: the PDF renderer honors intra-paragraph
newlines the way the docx renderer does (pdf-newline-flattening), and drops
a leading heading that only repeats the letterhead firm name
(letterhead-duplicated-in-letters)."""

import pytest

from orgsmith.render.pdf import (
    _blocks_to_html,
    _duplicates_letterhead,
    _para_html,
)
from orgsmith.schemas import Block, DocIR

pytestmark = pytest.mark.unit


def test_para_html_converts_newlines_to_line_breaks():
    """A multi-line inside address renders on separate lines, not smeared."""
    out = _para_html("Attn: Jane Roe\n123 Main Street\nSpringfield")
    assert out == "Attn: Jane Roe<br>123 Main Street<br>Springfield"


def test_para_html_still_escapes_html():
    assert _para_html("a < b & c\nnext") == "a &lt; b &amp; c<br>next"


def test_duplicates_letterhead_matches_with_or_without_legal_suffix():
    firm = "Pinebrook Advisory Group LLC"
    assert _duplicates_letterhead("Pinebrook Advisory Group LLC", firm)
    assert _duplicates_letterhead("Pinebrook Advisory Group", firm)
    assert _duplicates_letterhead("PINEBROOK ADVISORY GROUP, LLC", firm)
    # An ordinary heading is not the firm name and stays.
    assert not _duplicates_letterhead("Engagement Letter", firm)
    assert not _duplicates_letterhead("Scope of Services", firm)


def _people():
    return {"p:a": {"name": "A Author", "title": "Partner", "email": "a@x"}}


def test_blocks_to_html_drops_a_leading_firm_name_heading():
    firm = "Pinebrook Advisory Group LLC"
    docir = DocIR(doc_id="d:0001", blocks=[
        Block(kind="heading", text="Pinebrook Advisory Group LLC", level=1),
        Block(kind="paragraph", text="Dear Ms. Roe,"),
    ])
    html_body = _blocks_to_html(docir, _people(), "January 1, 2021", firm_name=firm)
    assert "Pinebrook Advisory Group" not in html_body
    assert "Dear Ms. Roe," in html_body


def test_blocks_to_html_keeps_a_non_firm_leading_heading():
    firm = "Pinebrook Advisory Group LLC"
    docir = DocIR(doc_id="d:0001", blocks=[
        Block(kind="heading", text="Engagement Letter", level=1),
        Block(kind="paragraph", text="Body."),
    ])
    html_body = _blocks_to_html(docir, _people(), "January 1, 2021", firm_name=firm)
    assert "<h1>Engagement Letter</h1>" in html_body


def test_blocks_to_html_only_drops_the_heading_when_it_is_first():
    """A firm-name heading deeper in the body (unusual) is left alone; only a
    leading duplicate of the letterhead is suppressed."""
    firm = "Pinebrook Advisory Group LLC"
    docir = DocIR(doc_id="d:0001", blocks=[
        Block(kind="paragraph", text="Dear Ms. Roe,"),
        Block(kind="heading", text="Pinebrook Advisory Group LLC", level=2),
    ])
    html_body = _blocks_to_html(docir, _people(), "January 1, 2021", firm_name=firm)
    assert "Pinebrook Advisory Group LLC" in html_body
