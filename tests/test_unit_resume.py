"""Unit tier: killing a session mid-authoring loses nothing.

The CLI is stateless between invocations; resume truth lives in state.json
and the artifact files. These tests simulate the kill points a real
session hits: after a work order is emitted but before its deliverable is
ingested, and between batches with a partial render in between.
"""

import json

import pytest

from orgsmith.artifacts import load_manifest, load_work_order
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.authoring.ingest import run_ingest as ingest_author
from orgsmith.render import run_render
from orgsmith.assemble import run_assemble
from orgsmith.state import load_state
from orgsmith.status import collect_status
from orgsmith.validate import run_validate

from conftest import (
    build_pure_stages,
    run_authoring,
    run_enrichment,
    scripted_authoring,
)

pytestmark = pytest.mark.unit


def _ingest_outstanding(paths):
    """Author and ingest the single outstanding author batch."""
    state = load_state(paths)
    (_wo_id, ref), = state.author_batches.items()
    wo = load_work_order(paths.workorders_dir / ref.workorder)
    reply = paths.workorders_dir / f"reply-{wo.id.replace(':', '-')}.json"
    reply.write_text(json.dumps(scripted_authoring(wo)))
    assert ingest_author(paths, reply) == 0
    return wo


def test_rerunning_charter_on_an_unchanged_recipe_writes_nothing(tmp_path):
    """`/forge` runs `charter` unconditionally, so the advertised resume must
    not rewrite a committed fixture's charter.json (BACKLOG:
    charter-redump-drift). The recipe is the stage's only input: unchanged
    recipe, nothing to re-derive. But a recipe that DOES move must still
    propagate, which is why the guard keys on the recipe hash rather than on
    the file merely existing."""
    from orgsmith.charter import run_charter

    paths = build_pure_stages(tmp_path)
    first = paths.charter_json.read_bytes()
    mtime = paths.charter_json.stat().st_mtime_ns

    assert run_charter(paths) == 0
    assert paths.charter_json.read_bytes() == first
    assert paths.charter_json.stat().st_mtime_ns == mtime, "charter.json rewritten"

    # An edited recipe still propagates.
    text = paths.charter_md.read_text("utf-8")
    paths.charter_md.write_text(text.replace("base_revenue: 850000", "base_revenue: 860000"))
    assert run_charter(paths) == 0
    assert json.loads(paths.charter_json.read_text())["finance"]["base_revenue"] == 860000


def test_resume_mid_authoring_no_dup_no_loss(tmp_path):
    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)

    # Session 1: one batch authored, a second work order emitted, then the
    # session dies before the deliverable lands.
    assert run_next_batch(paths) == 0
    first_wo = _ingest_outstanding(paths)
    assert run_render(paths) == 0  # browsable early
    assert run_next_batch(paths) == 0
    (orphan_id, orphan_ref), = load_state(paths).author_batches.items()
    orphan_docs = set(orphan_ref.doc_ids)
    assert orphan_docs  # the orphan batch claims real docs

    # Session 2: fresh process, file-derived state only. The orphan stays
    # outstanding across the kill; a fresh next-batch never re-covers its
    # docs (it emits a disjoint batch, or nothing if the orphan holds the
    # tail), so the orphan is not lost and no doc is claimed twice.
    assert run_next_batch(paths) == 0
    state = load_state(paths)
    assert orphan_id in state.author_batches
    for wo_id, ref in state.author_batches.items():
        if wo_id != orphan_id:
            assert not (set(ref.doc_ids) & orphan_docs)
    run_authoring(paths)  # re-dispatches the orphan and completes the org
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0

    # No doc was authored twice across work orders...
    orders = [
        load_work_order(p) for p in sorted(paths.workorders_dir.glob("author-*.json"))
    ]
    briefed = [b.doc_id for wo in orders for b in wo.docs]
    assert len(briefed) == len(set(briefed)), "a doc appeared in two work orders"
    assert set(b.doc_id for b in first_wo.docs) <= set(briefed)

    # ...every batchable doc has exactly one DocIR and one rendered file...
    manifest = load_manifest(paths)
    batchable = [e for e in manifest if e.authoring == "batchable"]
    docirs = list(paths.docir_dir.glob("d*.json"))
    assert len(docirs) == len(batchable)
    state = load_state(paths)
    for entry in manifest:
        assert (paths.share_dir / entry.path).exists()
        doc = state.doc(entry.doc_id)
        assert doc.rendered_hash and doc.rendered_from

    # ...stages report done and the org validates clean.
    status = collect_status(paths)
    assert status["stages"]["author"] == "done"
    assert status["stages"]["render"] == "done"
    assert status["outstanding"] == {}
    assert status["author_batches"] == {}
    assert run_validate(paths) == 0


def test_resume_with_several_batches_outstanding(tmp_path):
    """M10 authors K wide, so a killed session strands up to K orphans.

    `test_resume_mid_authoring_no_dup_no_loss` only ever holds ONE orphan at
    its kill point. This holds three, which is the documented real shape:
    /forge fills a K=4 window, and a session that dies mid-window strands
    every batch in it.

    Both tests fail if `covered_docs()` stops unioning across outstanding
    orders (verified by injecting exactly that fault), so this is not
    coverage the suite lacked outright. What it adds is where and how it
    fails. Under the fault the single-orphan test survives to the end of a
    full authoring-and-render pass and then reports `a doc appeared in two
    work orders` (20 vs 17) -- true, but it names neither the invariant nor
    the orders involved, and it only gets there because `run_authoring`
    happens to open a second batch. This test fails at the moment the window
    is opened, before any authoring, and names which order re-covered which.

    The kill is modeled the way the airlock defines it: work orders emitted
    and never ingested. `load_state` re-reads state.json from disk, so every
    assertion below is against file-derived truth exactly as a fresh process
    would see it (CLAUDE.md: resume state is never conversation memory).
    """
    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)

    # Session 1: fill a 3-wide window and die before ingesting any of it.
    for _ in range(3):
        assert run_next_batch(paths) == 0
    orphans = {
        wo_id: set(ref.doc_ids)
        for wo_id, ref in load_state(paths).author_batches.items()
    }
    assert len(orphans) == 3, "the window did not open three batches"
    for doc_ids in orphans.values():
        assert doc_ids

    # The orphans were disjoint when emitted; that is the M10 invariant.
    claimed = [d for ids in orphans.values() for d in ids]
    assert len(claimed) == len(set(claimed)), "two outstanding orders overlap"

    # Session 2: a fresh process sees only the files. A new batch must be
    # disjoint from every orphan, not just the last one.
    assert run_next_batch(paths) == 0
    state = load_state(paths)
    for wo_id, doc_ids in orphans.items():
        assert wo_id in state.author_batches, f"orphan {wo_id} was dropped"
        assert set(state.author_batches[wo_id].doc_ids) == doc_ids
    fresh = {
        wo_id: set(ref.doc_ids)
        for wo_id, ref in state.author_batches.items()
        if wo_id not in orphans
    }
    for wo_id, doc_ids in fresh.items():
        for orphan_id, orphan_docs in orphans.items():
            overlap = doc_ids & orphan_docs
            assert not overlap, f"{wo_id} re-covers {orphan_id}: {overlap}"

    # Draining the window completes the org with no duplicate and no loss.
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0

    orders = [
        load_work_order(p) for p in sorted(paths.workorders_dir.glob("author-*.json"))
    ]
    briefed = [b.doc_id for wo in orders for b in wo.docs]
    assert len(briefed) == len(set(briefed)), "a doc appeared in two work orders"
    for orphan_docs in orphans.values():
        assert orphan_docs <= set(briefed), "an orphan's docs were never authored"

    manifest = load_manifest(paths)
    batchable = [e for e in manifest if e.authoring == "batchable"]
    assert len(list(paths.docir_dir.glob("d*.json"))) == len(batchable)
    state = load_state(paths)
    for entry in manifest:
        assert (paths.share_dir / entry.path).exists()
        doc = state.doc(entry.doc_id)
        assert doc.rendered_hash and doc.rendered_from

    status = collect_status(paths)
    assert status["stages"]["author"] == "done"
    assert status["outstanding"] == {}
    assert status["author_batches"] == {}
    assert run_validate(paths) == 0


def test_partial_render_survives_resume(tmp_path):
    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)
    assert run_next_batch(paths) == 0
    _ingest_outstanding(paths)
    assert run_render(paths) == 0

    rendered_early = {
        p: p.stat().st_mtime_ns
        for p in paths.share_dir.rglob("*")
        if p.is_file()
    }
    assert rendered_early

    run_authoring(paths)
    assert run_render(paths) == 0
    # Early files were not re-rendered on resume.
    for path, mtime in rendered_early.items():
        assert path.stat().st_mtime_ns == mtime, path
