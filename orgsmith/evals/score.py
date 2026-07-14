"""score: grade an external system's answers against the golden suites.

Pure function of the evals directory and the answers file; needs neither
the rest of the org nor OrgSmith internals, so external-system authors can
be graded from a bare copy of `evals/`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from ..schemas import (
    GraphAnswers,
    GraphExpected,
    RetrievalAnswers,
    RetrievalQuestion,
)


@dataclass
class RetrievalResult:
    total: int
    correct: int
    failures: list[dict] = field(default_factory=list)

    @property
    def score(self) -> float:
        return self.correct / self.total if self.total else 0.0


@dataclass
class GraphResult:
    entity_precision: float
    entity_recall: float
    edge_precision: float
    edge_recall: float


def load_questions(evals_dir: Path) -> list[RetrievalQuestion]:
    path = evals_dir / "retrieval.jsonl"
    if not path.exists():
        raise SystemExit(f"score: no retrieval suite at {path}")
    return [
        RetrievalQuestion.model_validate_json(line)
        for line in path.read_text("utf-8").splitlines()
        if line.strip()
    ]


def score_retrieval(evals_dir: Path, answers: RetrievalAnswers) -> RetrievalResult:
    questions = load_questions(evals_dir)
    given = {a.id: a.docs for a in answers.answers}
    result = RetrievalResult(total=len(questions), correct=0)
    for q in questions:
        expected = set(q.expected_docs)
        got = {d.strip() for d in given.get(q.id, [])}
        if got == expected:
            result.correct += 1
            continue
        result.failures.append(
            {
                "id": q.id,
                "tags": q.tags,
                "missing": sorted(expected - got),
                "extra": sorted(got - expected),
                "answered": q.id in given,
            }
        )
    return result


def _alias_index(expected: GraphExpected) -> dict[str, str]:
    index: dict[str, str] = {}
    for entity in expected.entities:
        for name in [entity.canonical, *entity.aliases]:
            index[name.casefold()] = entity.id
    return index


def score_graph(evals_dir: Path, answers: GraphAnswers) -> GraphResult:
    path = evals_dir / "graph_expected.json"
    if not path.exists():
        raise SystemExit(f"score: no graph suite at {path}")
    expected = GraphExpected.model_validate_json(path.read_text("utf-8"))
    index = _alias_index(expected)

    matched_ids = set()
    matched_answers = 0
    for answer in answers.entities:
        eid = index.get(answer.name.casefold())
        if eid is not None:
            matched_answers += 1
            matched_ids.add(eid)
    entity_precision = (
        matched_answers / len(answers.entities) if answers.entities else 0.0
    )
    entity_recall = (
        len(matched_ids) / len(expected.entities) if expected.entities else 0.0
    )

    expected_edges = {(e.src, e.dst, e.kind) for e in expected.edges}
    resolved = []
    for edge in answers.edges:
        src = index.get(edge.src.casefold())
        dst = index.get(edge.dst.casefold())
        resolved.append((src, dst, edge.kind))
    hits = {t for t in resolved if t in expected_edges}
    edge_precision = len(hits) / len(resolved) if resolved else 0.0
    edge_recall = len(hits) / len(expected_edges) if expected_edges else 0.0

    return GraphResult(
        entity_precision=entity_precision,
        entity_recall=entity_recall,
        edge_precision=edge_precision,
        edge_recall=edge_recall,
    )


def run_score(
    evals_dir: Path, suite: str, answers_path: Path, as_json: bool = False
) -> int:
    if not answers_path.exists():
        raise SystemExit(f"score: no answers file at {answers_path}")
    raw = answers_path.read_text("utf-8")
    try:
        if suite == "retrieval":
            answers = RetrievalAnswers.model_validate_json(raw)
        elif suite == "graph":
            answers = GraphAnswers.model_validate_json(raw)
        else:
            raise SystemExit(f"score: unknown suite {suite!r} (retrieval|graph)")
    except ValidationError as err:
        print(
            f"score: answers file does not match the {suite} contract "
            f"(see evals/README.md):\n{err}"
        )
        return 2

    if suite == "retrieval":
        result = score_retrieval(evals_dir, answers)
        if as_json:
            print(
                json.dumps(
                    {
                        "suite": "retrieval",
                        "total": result.total,
                        "correct": result.correct,
                        "score": round(result.score, 4),
                        "failures": result.failures,
                    },
                    indent=2,
                )
            )
        else:
            print(
                f"retrieval: {result.correct}/{result.total} "
                f"({result.score:.1%})"
            )
            for failure in result.failures:
                parts = []
                if not failure["answered"]:
                    parts.append("unanswered")
                if failure["missing"]:
                    parts.append("missing: " + ", ".join(failure["missing"]))
                if failure["extra"]:
                    parts.append("extra: " + ", ".join(failure["extra"]))
                print(f"  {failure['id']} [{','.join(failure['tags'])}] "
                      + "; ".join(parts))
        return 0

    result = score_graph(evals_dir, answers)
    payload = {
        "suite": "graph",
        "entity_precision": round(result.entity_precision, 4),
        "entity_recall": round(result.entity_recall, 4),
        "edge_precision": round(result.edge_precision, 4),
        "edge_recall": round(result.edge_recall, 4),
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "graph: entities P={entity_precision:.1%} R={entity_recall:.1%}; "
            "edges P={edge_precision:.1%} R={edge_recall:.1%}".format(**payload)
        )
    return 0
