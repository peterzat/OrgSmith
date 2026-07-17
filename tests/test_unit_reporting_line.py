"""Unit tier: prose may not contradict a reporting line the ledger owns (M12,
rf:graph-1). northgate shipped onboarding records telling a hire she reports to
the Managing Director when foundation reports her to the Principal. A reporting
line is a relationship the ledger owns, so the onboarding brief states the true
one and ingest rejects a deliverable that names a different internal manager."""

import json

import pytest

from orgsmith.artifacts import load_foundation, load_manifest, load_work_order
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.authoring.ingest import _check_reporting_line
from orgsmith.authoring.ingest import run_ingest as ingest_author
from orgsmith.state import load_state

from conftest import build_pure_stages, run_enrichment, scripted_authoring

pytestmark = pytest.mark.unit


@pytest.fixture()
def org(tmp_path):
    return build_pure_stages(tmp_path)


def _onboarding_entry(paths):
    entry = next(
        e for e in load_manifest(paths) if e.genre == "onboarding_record"
    )
    return entry, load_foundation(paths)


def test_lint_rejects_only_a_contradicting_internal_manager(org):
    """dev-mini's one onboarding record: Cynthia Ball reports to Robert Miller
    (Principal Consultant), one rung below the Managing Partner. The lint fires
    on a wrong internal title or name and stays silent on correct, absent, or
    outward-facing reporting prose -- precision over recall."""
    entry, foundation = _onboarding_entry(org)

    # correct: names the true manager by name and title
    assert not _check_reporting_line(
        entry, foundation, "She reports to Robert Miller, the Principal Consultant."
    )
    # correct: true title alone
    assert not _check_reporting_line(
        entry, foundation, "Cynthia reports to the Principal Consultant."
    )
    # silent: no reporting line at all
    assert not _check_reporting_line(
        entry, foundation, "She joins the analytics practice this quarter."
    )
    # outward-facing: reporting to a client is not a supervisor claim
    assert not _check_reporting_line(
        entry, foundation, "The team reports to the client every other week."
    )
    # contradiction: wrong internal title (the rf:graph-1 shape exactly)
    assert _check_reporting_line(
        entry, foundation, "She reports to the Managing Partner."
    )
    # contradiction: wrong internal person by name
    assert _check_reporting_line(
        entry, foundation, "Cynthia reports directly to Daniel Jones."
    )


def test_naming_the_true_manager_passes_even_beside_a_wrong_title(org):
    """True-first ordering: prose that names the real manager passes even when
    a wrong management title also appears in the same clause, so a contrastive
    'reports to X, not Y' does not misfire."""
    entry, foundation = _onboarding_entry(org)
    assert not _check_reporting_line(
        entry,
        foundation,
        "She reports to the Principal Consultant, not the Managing Partner.",
    )


def test_containment_is_word_bounded(org):
    """The containment helper matches whole tokens, not substrings, so a short
    alias cannot match inside a longer word."""
    from orgsmith.authoring.ingest import _contains_token

    assert _contains_token("Principal", "the Principal Consultant")
    assert not _contains_token("Principal", "Principality of Monaco")


def test_briefed_reporting_line_states_the_true_manager(org):
    """The onboarding work order carries the true reporting line, so the author
    is told who the hire reports to rather than guessing (which is how the
    wrong supervisor got written in the first place)."""
    run_enrichment(org)
    entry, foundation = _onboarding_entry(org)
    manager = foundation.person(foundation.person(entry.participants[0]).reports_to)

    # drive batches until the one carrying the onboarding record is outstanding
    brief = None
    for _ in range(20):
        assert run_next_batch(org) == 0
        state = load_state(org)
        if not state.author_batches:
            break
        for ref in state.author_batches.values():
            wo = load_work_order(org.workorders_dir / ref.workorder)
            found = next(
                (b for b in wo.docs if b.doc_id == entry.doc_id), None
            )
            if found is not None:
                brief = found
                wo_hit = wo
            ingest_author(org, _write(org, f"{ref.workorder}.d.json",
                                      scripted_authoring(wo)))
        if brief is not None:
            break
    assert brief is not None
    assert manager.name in brief.reporting_line
    assert manager.title_at(entry.date) in brief.reporting_line
    assert "reporting_line" in wo_hit.instructions


def _write(paths, name, payload):
    p = paths.workorders_dir / name
    p.write_text(json.dumps(payload))
    return p


def test_contradiction_is_rejected_at_ingest(org):
    """End to end: a deliverable whose onboarding prose names the wrong internal
    manager is rejected by run_ingest, and the same batch with correct scripted
    prose merges clean."""
    run_enrichment(org)
    entry, _ = _onboarding_entry(org)

    for _ in range(20):
        assert run_next_batch(org) == 0
        state = load_state(org)
        if not state.author_batches:
            break
        ref = next(iter(state.author_batches.values()))
        wo = load_work_order(org.workorders_dir / ref.workorder)
        good = scripted_authoring(wo)
        if any(d["doc_id"] == entry.doc_id for d in good["docs"]):
            tampered = json.loads(json.dumps(good))
            for doc in tampered["docs"]:
                if doc["doc_id"] == entry.doc_id:
                    doc["blocks"].append({
                        "kind": "paragraph",
                        "text": "She reports to the Managing Partner.",
                    })
            assert ingest_author(org, _write(org, "bad.json", tampered)) == 1
            assert ingest_author(org, _write(org, "good.json", good)) == 0
            return
        assert ingest_author(org, _write(org, f"{ref.workorder}.json", good)) == 0
    pytest.fail("never reached the onboarding batch")
