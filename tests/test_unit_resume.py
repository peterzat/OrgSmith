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
