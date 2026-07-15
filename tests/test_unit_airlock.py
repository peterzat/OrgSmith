"""Unit tier: the airlock contract (work orders, ingest, rejections)."""

import json

import pytest

from orgsmith.artifacts import load_foundation, load_manifest, load_work_order
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.authoring.ingest import run_ingest as ingest_author
from orgsmith.foundation.contexts import run_emit_context
from orgsmith.foundation.ingest import run_ingest as ingest_enrichment
from orgsmith.state import load_state

from conftest import (
    build_pure_stages,
    run_authoring,
    run_enrichment,
    scripted_authoring,
    scripted_enrichment,
)

pytestmark = pytest.mark.unit


@pytest.fixture()
def org(tmp_path):
    return build_pure_stages(tmp_path)


def _outstanding_wo(paths, stage):
    state = load_state(paths)
    return load_work_order(paths.workorders_dir / state.outstanding[stage])


def _write(paths, name, payload) -> str:
    p = paths.workorders_dir / name
    p.write_text(json.dumps(payload))
    return p


def test_emit_context_is_idempotent(org):
    assert run_emit_context(org) == 0
    first = load_state(org).outstanding["foundation"]
    assert run_emit_context(org) == 0
    assert load_state(org).outstanding["foundation"] == first
    assert len(list(org.workorders_dir.glob("foundation-*.json"))) == 1


def test_work_order_is_self_contained(org):
    run_emit_context(org)
    wo = _outstanding_wo(org, "foundation")
    assert wo.narrative and wo.instructions and wo.people
    assert wo.deliverable_schema == "orgsmith/enrichment-deliverable@1"
    assert all(p.name and p.title for p in wo.people)


def test_enrichment_rejections(org):
    run_emit_context(org)
    wo = _outstanding_wo(org, "foundation")
    good = scripted_enrichment(wo)

    # schema-invalid: personas trying to alter protected fields
    tampered = json.loads(json.dumps(good))
    tampered["personas"][0]["reports_to"] = "p:someone.else"
    assert ingest_enrichment(org, _write(org, "t1.json", tampered)) == 1

    tampered = json.loads(json.dumps(good))
    tampered["personas"][0]["person_id"] = "p:not.a.person"
    assert ingest_enrichment(org, _write(org, "t2.json", tampered)) == 1

    tampered = json.loads(json.dumps(good))
    del tampered["personas"][0]
    assert ingest_enrichment(org, _write(org, "t3.json", tampered)) == 1

    tampered = json.loads(json.dumps(good))
    tampered["work_order_id"] = "wo:foundation:9999"
    with pytest.raises(SystemExit):
        ingest_enrichment(org, _write(org, "t4.json", tampered))

    # nothing merged by the failed attempts
    assert all(p.persona == "" for p in load_foundation(org).people)

    assert ingest_enrichment(org, _write(org, "ok.json", good)) == 0
    foundation = load_foundation(org)
    assert all(len(p.persona) >= 40 for p in foundation.people)
    state = load_state(org)
    assert state.stage_done("foundation_enrich")
    assert "foundation" not in state.outstanding


def test_authoring_requires_enrichment(org):
    with pytest.raises(SystemExit):
        run_next_batch(org)


def test_authoring_flow_and_rejections(org, capsys):
    run_enrichment(org)
    assert run_next_batch(org) == 0
    wo = _outstanding_wo(org, "author")
    assert 0 < len(wo.docs) <= 6
    groups = {b.doc_id.split(":")[0] for b in wo.docs}
    assert groups == {"d"}
    # facts are briefed as ids + hints, never values: no ledger surface
    # form may appear anywhere in the serialized work order
    from orgsmith.artifacts import load_engagements
    from orgsmith.state import load_state as _ls

    wo_text = (
        org.workorders_dir / _ls(org).outstanding["author"]
    ).read_text()
    for fact in load_engagements(org).fact_index().values():
        if fact.kind in ("money", "date"):
            assert fact.rendered not in wo_text, fact.id

    good = scripted_authoring(wo)

    # re-emit without ingest returns the same order
    assert run_next_batch(org) == 0
    assert _outstanding_wo(org, "author").id == wo.id

    briefed_with_facts = next(b for b in wo.docs if b.facts)

    # missing required placeholder
    tampered = json.loads(json.dumps(good))
    for doc in tampered["docs"]:
        if doc["doc_id"] == briefed_with_facts.doc_id:
            for block in doc["blocks"]:
                block["text"] = (
                    block.get("text", "").replace("{{fact:", "((fact:")
                )
    assert ingest_author(org, _write(org, "a1.json", tampered)) == 1

    # unbriefed fact id
    tampered = json.loads(json.dumps(good))
    tampered["docs"][0]["blocks"][1]["text"] += " {{fact:E-2099-001.fee}}"
    assert ingest_author(org, _write(org, "a2.json", tampered)) == 1

    # unknown doc id
    tampered = json.loads(json.dumps(good))
    tampered["docs"][0]["doc_id"] = "d:9999"
    assert ingest_author(org, _write(org, "a3.json", tampered)) == 1

    # deliverable-controlled text must never drive the terminal: an escape
    # sequence smuggled through a fact id is neutralized in the rejection
    # printout (exit code unchanged)
    tampered = json.loads(json.dumps(good))
    tampered["docs"][0]["blocks"][1]["text"] += " {{fact:\x1b[2Jevil}}"
    assert ingest_author(org, _write(org, "a4.json", tampered)) == 1
    probe_out = capsys.readouterr().out
    assert "\x1b" not in probe_out
    assert "[2Jevil" in probe_out  # content survives, the escape does not

    # nothing merged
    assert not org.docir_dir.exists()

    assert ingest_author(org, _write(org, "ok.json", good)) == 0
    state = load_state(org)
    assert "author" not in state.outstanding
    for brief in wo.docs:
        assert state.doc(brief.doc_id).authored_hash
        assert (org.docir_dir / f"{brief.doc_id.replace(':', '')}.json").exists()


def test_authoring_converges_over_all_batches(org):
    run_enrichment(org)
    batches = run_authoring(org)
    assert batches >= 2  # dev-mini has multiple engagement groups
    state = load_state(org)
    assert state.stage_done("author")
    manifest = load_manifest(org)
    batchable = [e for e in manifest if e.authoring == "batchable"]
    assert all(state.doc(e.doc_id).authored_hash for e in batchable)
    static = [e for e in manifest if e.authoring == "static"]
    assert all(state.doc(e.doc_id).authored_hash is None for e in static)
    # next-batch after completion stays a no-op
    assert run_next_batch(org) == 0
    assert "author" not in load_state(org).outstanding
