"""Unit tier: a firm overview names only finished engagements (M17e,
`doc_culture.overview_cites_finished_work`).

Overviews cited every engagement begun by their date, so a marketing
document named a live, confidential mandate a month in. Found by four
reviewers on the two M17d boards (`overview-names-live-mandates`).
"""

from __future__ import annotations

import pytest

from orgsmith.artifacts import load_engagements, load_manifest

from conftest import build_culture_stages, build_pure_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit

_FORMAT = "  format_mix: {docx: 15, pdf: 3, xlsx: 5}\n"
_ON = "  overview_cites_finished_work: true\n"


def _overviews(paths):
    return [e for e in load_manifest(paths) if e.genre == "company_overview"]


@pytest.fixture(scope="module")
def on(tmp_path_factory):
    return build_culture_stages(tmp_path_factory.mktemp("on"), _FORMAT + _ON)


@pytest.fixture(scope="module")
def off(tmp_path_factory):
    return build_pure_stages(tmp_path_factory.mktemp("off"))


def test_an_overview_names_exactly_the_engagements_finished_before_it(on):
    engs = load_engagements(on).engagements
    overviews = _overviews(on)
    assert overviews
    for entry in overviews:
        want = {f"f:{e.id}.client" for e in engs if e.end < entry.date}
        assert set(entry.facts_refs) == want, entry.path


def test_an_overview_before_any_engagement_ends_names_no_client(on):
    engs = load_engagements(on).engagements
    first_end = min(e.end for e in engs)
    early = [e for e in _overviews(on) if e.date <= first_end]
    assert early, "the fixture has no overview dated before the first engagement ends"
    assert all(e.facts_refs == [] for e in early)


def test_off_overviews_still_cite_engagements_begun(off):
    engs = load_engagements(off).engagements
    for entry in _overviews(off):
        want = {f"f:{e.id}.client" for e in engs if e.start <= entry.date}
        assert set(entry.facts_refs) == want


def test_the_brief_agrees_with_the_plan_and_ingests(on):
    """Plan and brief share one function; the scripted author writes every
    briefed placeholder, so a disagreement would be an ingest rejection."""
    from orgsmith.artifacts import load_work_order
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.state import load_state

    run_enrichment(on)
    assert run_next_batch(on) == 0
    briefs = [
        b
        for ref in load_state(on).author_batches.values()
        for b in load_work_order(on.workorders_dir / ref.workorder).docs
        if b.genre == "company_overview"
    ]
    for b in briefs:
        if b.facts:
            assert "confidential" in b.firm_digest
            assert "has completed" in b.firm_digest
        else:
            assert "no completed client engagements" in b.firm_digest
    assert run_authoring(on) >= 0
    assert all(load_state(on).doc(e.doc_id).authored_hash for e in _overviews(on))
