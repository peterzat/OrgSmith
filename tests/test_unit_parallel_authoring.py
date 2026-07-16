"""Unit tier: the concurrent-batch author airlock (M10 parallel authoring).

The author stage carries several outstanding work orders at once, each over
a disjoint set of documents, so /forge can dispatch a window of workers in
parallel. These tests pin the properties that make that safe offline: the
emitted batches partition the batchable manifest exactly once and
deterministically, each ingests independently and in any order, and a
work-order id that is not outstanding is rejected without a partial write.
"""

import json

import pytest

from orgsmith.artifacts import load_manifest, load_work_order
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.authoring.ingest import run_ingest as ingest_author
from orgsmith.state import load_state
from orgsmith.status import collect_status

from conftest import (
    build_pure_stages,
    ingest_author_batch,
    run_authoring,
    run_enrichment,
    scripted_authoring,
    sole_author_wo,
)

pytestmark = pytest.mark.unit


def _batchable_ids(paths):
    return [e.doc_id for e in load_manifest(paths) if e.authoring == "batchable"]


def _emit_all_batches(paths):
    """Drain next-batch without ingesting, so every batchable doc ends up
    claimed by exactly one outstanding order. Returns author_batches."""
    prev = -1
    while True:
        assert run_next_batch(paths) == 0
        n = len(load_state(paths).author_batches)
        if n == prev:
            break
        prev = n
    return load_state(paths).author_batches


def _batch_doc_ids(paths):
    """Doc ids per outstanding batch, in emission order (from state)."""
    return [list(ref.doc_ids) for ref in load_state(paths).author_batches.values()]


@pytest.fixture()
def enriched(tmp_path):
    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)
    return paths


def test_two_next_batches_are_disjoint(enriched):
    paths = enriched
    assert run_next_batch(paths) == 0
    assert run_next_batch(paths) == 0
    batches = load_state(paths).author_batches
    assert len(batches) == 2, "two batches should be outstanding at once"
    first, second = (ref.doc_ids for ref in batches.values())
    assert first and second
    assert not (set(first) & set(second)), "concurrent batches overlap"
    # each stored order briefs exactly the docs its BatchRef claims
    for wo_id, ref in batches.items():
        wo = load_work_order(paths.workorders_dir / ref.workorder)
        assert [b.doc_id for b in wo.docs] == list(ref.doc_ids)
        assert wo.id == wo_id


def test_drain_partitions_the_manifest_exactly_once(enriched):
    paths = enriched
    _emit_all_batches(paths)
    per_batch = _batch_doc_ids(paths)
    covered = [d for batch in per_batch for d in batch]
    batchable = _batchable_ids(paths)
    # complete: every batchable doc is claimed
    assert set(covered) == set(batchable)
    # disjoint: no doc claimed twice
    assert len(covered) == len(set(covered)) == len(batchable)
    # each batch is drawn from a single engagement group, so one ledger slice
    # serves the whole batch (the grouping that keeps briefs self-contained)
    manifest = {e.doc_id: e for e in load_manifest(paths)}
    for batch in per_batch:
        groups = {(manifest[d].engagement or "firm") for d in batch}
        assert len(groups) == 1


def test_partition_is_a_pure_function_of_the_manifest(tmp_path):
    # Same recipe, two independent builds: identical batch groupings.
    a = build_pure_stages(tmp_path / "a")
    run_enrichment(a)
    b = build_pure_stages(tmp_path / "b")
    run_enrichment(b)
    _emit_all_batches(a)
    _emit_all_batches(b)
    assert _batch_doc_ids(a) == _batch_doc_ids(b)


def test_next_batch_waits_when_all_docs_are_in_flight(enriched):
    paths = enriched
    batches = _emit_all_batches(paths)
    count = len(batches)
    assert count >= 2
    # Nothing left uncovered, but batches are outstanding: not an error, not
    # done, and no new order is emitted.
    assert run_next_batch(paths) == 0
    state = load_state(paths)
    assert len(state.author_batches) == count
    assert not state.stage_done("author")


def test_ingest_clears_only_its_own_batch_in_any_order(enriched):
    paths = enriched
    _emit_all_batches(paths)
    order = list(load_state(paths).author_batches)  # emission order
    assert len(order) >= 2

    # Ingest in reverse. The stage is done only after the last one lands.
    for i, wo_id in enumerate(reversed(order)):
        claimed = list(load_state(paths).author_batches[wo_id].doc_ids)
        ingest_author_batch(paths, wo_id)
        state = load_state(paths)
        assert wo_id not in state.author_batches, "ingested batch not cleared"
        # only this batch's docs became authored in this step
        for doc_id in claimed:
            assert state.doc(doc_id).authored_hash
        last = i == len(order) - 1
        assert state.stage_done("author") is last

    # No doc authored twice, none skipped.
    docirs = sorted(p.name for p in paths.docir_dir.glob("d*.json"))
    assert len(docirs) == len(set(docirs)) == len(_batchable_ids(paths))


def test_ingest_rejects_a_work_order_that_is_not_outstanding(enriched):
    paths = enriched
    assert run_next_batch(paths) == 0
    wo = sole_author_wo(paths)
    outstanding_before = dict(load_state(paths).author_batches)

    forged = scripted_authoring(wo)
    forged["work_order_id"] = "wo:author:9999"  # never emitted
    reply = paths.workorders_dir / "forged.json"
    reply.write_text(json.dumps(forged))
    with pytest.raises(SystemExit):
        ingest_author(paths, reply)

    # The real batch is untouched and nothing was written.
    assert load_state(paths).author_batches == outstanding_before
    assert not paths.docir_dir.exists()


def test_status_surfaces_and_clears_outstanding_batches(enriched):
    paths = enriched
    assert run_next_batch(paths) == 0
    assert run_next_batch(paths) == 0
    state = load_state(paths)
    surfaced = collect_status(paths)["author_batches"]
    assert set(surfaced) == set(state.author_batches)
    assert len(surfaced) == 2
    for wo_id, info in surfaced.items():
        ref = state.author_batches[wo_id]
        assert info["docs"] == len(ref.doc_ids)
        assert info["workorder"].endswith(ref.workorder)

    # run_authoring ingests the two outstanding batches plus any remaining.
    run_authoring(paths)
    assert collect_status(paths)["author_batches"] == {}
    assert load_state(paths).stage_done("author")
