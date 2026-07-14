"""Unit tier: golden eval emission and scoring (the oracle self-check)."""

import json
import shutil

import pytest

from orgsmith.artifacts import (
    load_charter,
    load_engagements,
    load_foundation,
    load_graph,
    load_manifest,
    load_mention_map,
)
from orgsmith.evals.emit import build_graph_expected, build_retrieval, run_emit_evals
from orgsmith.evals.score import run_score, score_graph, score_retrieval
from orgsmith.paths import OrgPaths
from orgsmith.schemas import GraphAnswers, GraphExpected, RetrievalAnswers

from conftest import REPO, build_knobbed_stages

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def org(tmp_path_factory):
    paths = build_knobbed_stages(tmp_path_factory.mktemp("evals-org"))
    assert run_emit_evals(paths) == 0
    return paths


def _questions(paths):
    lines = (paths.evals_dir / "retrieval.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _ground_truth_answers(paths) -> dict:
    return {
        "suite": "retrieval",
        "answers": [
            {"id": q["id"], "docs": q["expected_docs"]}
            for q in _questions(paths)
        ],
    }


def test_emission_is_deterministic(org):
    first = {
        name: (org.evals_dir / name).read_bytes()
        for name in ("retrieval.jsonl", "graph_expected.json", "README.md")
    }
    assert run_emit_evals(org) == 0
    for name, content in first.items():
        assert (org.evals_dir / name).read_bytes() == content, name


def test_question_floor_and_contract(org):
    questions = _questions(org)
    assert len(questions) >= 12
    ids = [q["id"] for q in questions]
    assert len(set(ids)) == len(ids)
    manifest_paths = {e.path for e in load_manifest(org)}
    for q in questions:
        assert q["expected_docs"], q["id"]
        assert set(q["expected_docs"]) <= manifest_paths
    # the knobbed org has alias questions
    assert any("mention:alias" in q["tags"] for q in questions)


def test_committed_dev_mini_reaches_question_floor():
    paths = OrgPaths(root=REPO, slug="dev-mini")
    questions = build_retrieval(
        load_charter(paths),
        load_foundation(paths),
        load_engagements(paths),
        load_manifest(paths),
        load_mention_map(paths),  # None: predates mention ground truth
    )
    assert len(questions) >= 12


def test_ground_truth_answers_score_100(org):
    result = score_retrieval(
        org.evals_dir,
        RetrievalAnswers.model_validate(_ground_truth_answers(org)),
    )
    assert result.total >= 12
    assert result.correct == result.total
    assert result.failures == []


def test_wrong_answers_attributed(org):
    payload = _ground_truth_answers(org)
    payload["answers"][0]["docs"] = []  # everything missing
    payload["answers"][1]["docs"].append("Firm/Not A Real Doc.docx")
    result = score_retrieval(
        org.evals_dir, RetrievalAnswers.model_validate(payload)
    )
    assert result.correct == result.total - 2
    by_id = {f["id"]: f for f in result.failures}
    q0, q1 = payload["answers"][0]["id"], payload["answers"][1]["id"]
    assert by_id[q0]["missing"]
    assert by_id[q1]["extra"] == ["Firm/Not A Real Doc.docx"]


def test_graph_alias_credit(org):
    expected = GraphExpected.model_validate_json(
        (org.evals_dir / "graph_expected.json").read_text()
    )
    aliased = next(e for e in expected.entities if e.aliases)
    entities = []
    for entity in expected.entities:
        name = entity.aliases[0] if entity is aliased else entity.canonical
        entities.append({"name": name, "kind": entity.kind})
    by_id = {e.id: e for e in expected.entities}
    edges = [
        {
            "src": by_id[e.src].canonical,
            "dst": by_id[e.dst].canonical,
            "kind": e.kind,
        }
        for e in expected.edges
        if e.src in by_id and e.dst in by_id
    ]
    # every expected edge is entity-to-entity, so alias-credited answers
    # can reach perfect scores
    assert all(e.kind != "participant" for e in expected.edges)
    result = score_graph(
        org.evals_dir,
        GraphAnswers.model_validate(
            {"suite": "graph", "entities": entities, "edges": edges}
        ),
    )
    assert result.entity_precision == 1.0
    assert result.entity_recall == 1.0
    assert result.edge_precision == 1.0
    assert result.edge_recall == 1.0


def test_score_from_bare_evals_dir(org, tmp_path):
    bare = tmp_path / "just-evals"
    shutil.copytree(org.evals_dir, bare)
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(_ground_truth_answers(org)))
    assert run_score(bare, "retrieval", answers) == 0


def test_malformed_answers_rejected(org, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"suite": "retrieval", "answers": [{"id": 42}]}')
    assert run_score(org.evals_dir, "retrieval", bad) == 2
    missing = tmp_path / "nope.json"
    with pytest.raises(SystemExit):
        run_score(org.evals_dir, "retrieval", missing)
