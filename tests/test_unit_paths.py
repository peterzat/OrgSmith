"""Unit tier: M13 path containment and letterhead escaping.

Covers the three hardening surfaces closed in M13:
- the single guarded doc_id-to-filename derivation shared by every sink;
- the schema pattern plus contained join on state-derived work-order names;
- context-correct escaping of charter-tainted letterhead.
"""

from pathlib import Path

import pytest

from orgsmith.naming import doc_id_filename

pytestmark = pytest.mark.unit


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
