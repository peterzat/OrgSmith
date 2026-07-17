"""Unit tier: the airlock contract (work orders, ingest, rejections)."""

import json

import pytest

from orgsmith.airlock import _fresh_work_order_path, _next_serial
from orgsmith.artifacts import load_foundation, load_manifest, load_work_order
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.authoring.ingest import docir_path
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


def _author_batches(paths):
    """The outstanding author work orders, keyed by work_order_id."""
    state = load_state(paths)
    return {
        wo_id: load_work_order(paths.workorders_dir / ref.workorder)
        for wo_id, ref in state.author_batches.items()
    }


def _one_author_batch(paths):
    """The single outstanding author work order (tests driving one batch)."""
    batches = _author_batches(paths)
    assert len(batches) == 1
    return next(iter(batches.values()))


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


def test_enrichment_printer_neutralizes_control_chars(org, capsys):
    """The rejection printer echoes deliverable-controlled person ids: an
    escape sequence must not drive the terminal and a smuggled newline must
    not forge a line of output (exit code unchanged)."""
    run_emit_context(org)
    wo = _outstanding_wo(org, "foundation")
    tampered = scripted_enrichment(wo)
    tampered["personas"][0]["person_id"] = (
        "p:x\x1b[2J\x1b[31mPWNED\n  - ingest: merged 99 personas"
    )
    path = _write(org, "evil.json", tampered)
    capsys.readouterr()  # drop the emit-context banner
    assert ingest_enrichment(org, path) == 1
    out = capsys.readouterr().out
    assert "\x1b" not in out
    assert "PWNED" in out  # content survives, the escape does not
    # header + "unknown person ids" + "missing personas for": the smuggled
    # newline made no fourth line
    assert len([ln for ln in out.splitlines() if ln.strip()]) == 3


def test_authoring_requires_enrichment(org):
    with pytest.raises(SystemExit):
        run_next_batch(org)


def test_authoring_flow_and_rejections(org, capsys):
    run_enrichment(org)
    assert run_next_batch(org) == 0
    wo = _one_author_batch(org)
    assert 0 < len(wo.docs) <= 6
    groups = {b.doc_id.split(":")[0] for b in wo.docs}
    assert groups == {"d"}
    # facts are briefed as ids + hints, never values: no ledger surface
    # form may appear anywhere in the serialized work order
    from orgsmith.artifacts import load_engagements
    from orgsmith.state import load_state as _ls

    ref = next(iter(_ls(org).author_batches.values()))
    wo_text = (org.workorders_dir / ref.workorder).read_text()
    for fact in load_engagements(org).fact_index().values():
        if fact.kind in ("money", "date"):
            assert fact.rendered not in wo_text, fact.id

    good = scripted_authoring(wo)

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
    assert not state.author_batches
    for brief in wo.docs:
        assert state.doc(brief.doc_id).authored_hash
        assert (org.docir_dir / f"{brief.doc_id.replace(':', '')}.json").exists()


def test_traversal_doc_id_is_rejected_at_the_schema_and_at_the_sink(org):
    """SECURITY.md 2026-07-16 [NOTE]: `docir_path` derives a write target from
    the model-controlled `DocIR.doc_id`, which carried no pattern. Nothing was
    exploitable, but the safety was non-local: it held only because
    run_ingest's `unknown` membership check happens to run before the write
    loop. Both layers now guard themselves, so a refactor of that ordering
    cannot reopen a traversal."""
    run_enrichment(org)
    assert run_next_batch(org) == 0
    wo = _one_author_batch(org)
    good = scripted_authoring(wo)

    hostile_ids = ["../../evil", "d:0001/../../evil", "/etc/passwd", "..\\..\\evil"]

    # Rejected at parse by DocIR.doc_id's pattern -- before match_author_batch
    # and before the `unknown` check that used to be the only thing between a
    # hostile id and the write loop.
    for hostile in hostile_ids:
        tampered = json.loads(json.dumps(good))
        tampered["docs"][0]["doc_id"] = hostile
        assert ingest_author(org, _write(org, "trav.json", tampered)) == 1

    # And the sink guards itself, independent of the schema.
    for hostile in hostile_ids:
        with pytest.raises(ValueError, match="unsafe doc_id"):
            docir_path(org, hostile)

    # A legitimate id still resolves, and inside docir_dir.
    assert docir_path(org, "d:0001").parent == org.docir_dir

    assert not org.docir_dir.exists()  # nothing written by any rejected attempt
    assert ingest_author(org, _write(org, "ok.json", good)) == 0


def test_work_order_serial_never_reuses_a_deleted_number(org):
    """A deleted order must not hand its serial to the next emit.

    Work orders are kept after ingest as an audit trail, so the directory
    normally only grows and a count-based serial looks safe. Nothing enforces
    that. Counting meant one deletion made the next emit compute a serial that
    was already taken, write over the order that survived, and replace its
    entry in `state.author_batches` (keyed by work-order id) -- losing the
    surviving batch's doc_ids with no error. The max is stable under gaps.
    """
    run_enrichment(org)
    assert run_next_batch(org) == 0
    assert run_next_batch(org) == 0
    assert sorted(p.name for p in org.workorders_dir.glob("author-*.json")) == [
        "author-0001.json",
        "author-0002.json",
    ]

    survivor = org.workorders_dir / "author-0002.json"
    survivor_bytes = survivor.read_bytes()
    survivor_docs = load_state(org).author_batches["wo:author:0002"].doc_ids
    (org.workorders_dir / "author-0001.json").unlink()

    assert run_next_batch(org) == 0

    assert survivor.read_bytes() == survivor_bytes, "surviving order was overwritten"
    assert (org.workorders_dir / "author-0003.json").exists()

    batches = load_state(org).author_batches
    assert set(batches) == {"wo:author:0001", "wo:author:0002", "wo:author:0003"}
    assert batches["wo:author:0002"].doc_ids == survivor_docs
    # Still disjoint: a reused serial would have merged two batches' claims.
    claimed = [d for ref in batches.values() for d in ref.doc_ids]
    assert len(claimed) == len(set(claimed))


def test_fresh_work_order_path_refuses_to_clobber(org):
    """The belt to `_next_serial`'s braces: if a serial is ever computed as
    free and is not, the run fails instead of destroying an order."""
    org.workorders_dir.mkdir(parents=True, exist_ok=True)
    (org.workorders_dir / "author-0001.json").write_text("{}")
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        _fresh_work_order_path(org.workorders_dir, "author", 1)


def test_next_serial_reads_the_max_not_the_count(org):
    org.workorders_dir.mkdir(parents=True, exist_ok=True)
    assert _next_serial(org.workorders_dir, "author") == 1
    for name in ("author-0001.json", "author-0007.json"):
        (org.workorders_dir / name).write_text("{}")
    assert _next_serial(org.workorders_dir, "author") == 8
    # Other stages and unparseable strays do not perturb the count.
    (org.workorders_dir / "foundation-0003.json").write_text("{}")
    (org.workorders_dir / "author-draft.json").write_text("{}")
    assert _next_serial(org.workorders_dir, "author") == 8
    assert _next_serial(org.workorders_dir, "foundation") == 4


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
    assert not load_state(org).author_batches
