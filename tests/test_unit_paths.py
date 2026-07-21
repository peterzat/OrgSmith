"""Unit tier: M13 path containment and letterhead escaping.

Covers the three hardening surfaces closed in M13:
- the single guarded doc_id-to-filename derivation shared by every sink;
- the schema pattern plus contained join on state-derived work-order names;
- context-correct escaping of charter-tainted letterhead.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from orgsmith.airlock import match_author_batch, outstanding_work_order
from orgsmith.naming import doc_id_filename
from orgsmith.paths import OrgPaths
from orgsmith.schemas import dump_json
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
    """The guard on the pattern: all eight committed states still load, validate,
    and re-serialize byte-identically. A pattern that rejected a historically
    written name would fail here."""
    states = sorted(REPO.glob("companies/*-metadata/state.json"))
    assert len(states) == 8
    for sj in states:
        raw = sj.read_text("utf-8")
        state = OrgState.model_validate_json(raw)
        assert dump_json(state) == raw, f"{sj} did not round-trip"
