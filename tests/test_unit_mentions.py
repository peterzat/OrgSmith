"""Unit tier: mention planning and the authoring mention contract."""

import json

import pytest

from orgsmith.artifacts import (
    load_charter,
    load_foundation,
    load_manifest,
    load_mention_map,
    load_work_order,
)
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.authoring.ingest import run_ingest as ingest_author
from orgsmith.charter import parse_charter_md
from orgsmith.docplan.planner import build_manifest
from orgsmith.fabric.engagements import build_engagements
from orgsmith.fabric.finance import build_finance
from orgsmith.foundation.scaffold import build_foundation
from orgsmith.state import load_state

from conftest import REPO, build_pure_stages, run_enrichment, scripted_authoring

pytestmark = pytest.mark.unit


def _knobbed_manifest(**graph_target_updates):
    text = (REPO / "recipes/dev-mini/ORG-CHARTER.md").read_text()
    charter = parse_charter_md(text, "dev-mini")
    gt = charter.graph_targets.model_copy(update=graph_target_updates)
    charter = charter.model_copy(update={"graph_targets": gt})
    foundation = build_foundation(charter)
    engagements = build_engagements(charter, foundation)
    finance = build_finance(charter, foundation)
    return charter, foundation, build_manifest(
        charter, foundation, finance, engagements
    )


def test_natural_mentions_and_mention_map(tmp_path):
    paths = build_pure_stages(tmp_path)
    manifest = load_manifest(paths)
    foundation = load_foundation(paths)
    charter = load_charter(paths)
    names = {p.id: p.name for p in foundation.people}

    for entry in manifest:
        if entry.authoring == "static":
            assert entry.mentions == []
            continue
        mentioned = {m.entity for m in entry.mentions}
        for pid in entry.authors + entry.participants:
            assert pid in mentioned, f"{entry.doc_id} misses {pid}"
        for m in entry.mentions:
            if m.entity in names:
                assert m.surface == names[m.entity]
        if entry.engagement:
            assert any(m.kind == "org" for m in entry.mentions)
        assert [k.fact_id for k in entry.key_facts] == entry.facts_refs
        assert all(k.location == "body" for k in entry.key_facts)

    mention_map = load_mention_map(paths)
    assert mention_map is not None and mention_map.slug == charter.slug
    flat = {
        (r.doc_id, r.entity, r.surface, r.kind) for r in mention_map.mentions
    }
    expected = {
        (e.doc_id, m.entity, m.surface, m.kind)
        for e in manifest
        for m in e.mentions
    }
    assert flat == expected


def test_coverage_top_up_meets_minimum():
    _, foundation, manifest = _knobbed_manifest(min_mentions_per_person=3)
    for person in foundation.people:
        docs = [
            e
            for e in manifest
            if any(m.entity == person.id for m in e.mentions)
        ]
        assert len(docs) >= 3, person.id
        for e in docs:
            if person.id in e.participants:
                assert person.employment.start <= e.date


def test_nickname_plant_lands_in_a_doc():
    _, foundation, manifest = _knobbed_manifest(
        nickname_aliases=1, min_mentions_per_person=2
    )
    aliased = next(p for p in foundation.people if p.aliases)
    planted = [
        e
        for e in manifest
        for m in e.mentions
        if m.entity == aliased.id and m.surface == aliased.aliases[0]
    ]
    assert len(planted) == 1


def test_ingest_rejects_missing_mention(tmp_path):
    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)
    assert run_next_batch(paths) == 0
    state = load_state(paths)
    wo = load_work_order(paths.workorders_dir / state.outstanding["author"])
    assert any(b.mentions for b in wo.docs), "briefs carry no mentions"

    good = scripted_authoring(wo)
    tampered = json.loads(json.dumps(good))
    # Strip the mention line from a doc without a sigblock (kickoff memo).
    victim = next(
        b for b in wo.docs if b.genre == "kickoff_memo" and b.mentions
    )
    for doc in tampered["docs"]:
        if doc["doc_id"] == victim.doc_id:
            for block in doc["blocks"]:
                if "Present:" in block.get("text", ""):
                    block["text"] = block["text"].split("Present:")[0]
    reply = paths.workorders_dir / "tampered-mentions.json"
    reply.write_text(json.dumps(tampered))
    assert ingest_author(paths, reply) == 1

    ok = paths.workorders_dir / "ok-mentions.json"
    ok.write_text(json.dumps(good))
    assert ingest_author(paths, ok) == 0
