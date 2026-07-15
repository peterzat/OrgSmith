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

from ..naming import strip_control
from ..schemas import (
    ExtractionAnswers,
    ExtractionQuestion,
    GraphAnswers,
    GraphExpected,
    RetrievalAnswers,
    RetrievalQuestion,
    VisibilityAnswers,
)


@dataclass
class RetrievalResult:
    total: int
    correct: int
    failures: list[dict] = field(default_factory=list)

    @property
    def score(self) -> float:
        return self.correct / self.total if self.total else 0.0


ExtractionResult = RetrievalResult  # same shape: total, correct, failures


@dataclass
class GraphResult:
    entity_precision: float
    entity_recall: float
    edge_precision: float
    edge_recall: float
    # per ambiguity class: {"expected": n, "matched": m, "recall": r};
    # empty when the org's ground truth carries no ambiguity tags
    classes: dict = field(default_factory=dict)


def load_questions(evals_dir: Path) -> list[RetrievalQuestion]:
    path = evals_dir / "retrieval.jsonl"
    if not path.exists():
        raise SystemExit(f"score: no retrieval suite at {path}")
    return [
        RetrievalQuestion.model_validate_json(line)
        for line in path.read_text("utf-8").splitlines()
        if line.strip()
    ]


def _score_docset(
    questions: list[RetrievalQuestion], answers
) -> RetrievalResult:
    """Exact doc-set matching, shared by the retrieval and visibility
    suites (identical answers contract)."""
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


def score_retrieval(evals_dir: Path, answers: RetrievalAnswers) -> RetrievalResult:
    return _score_docset(load_questions(evals_dir), answers)


def load_visibility_questions(evals_dir: Path) -> list[RetrievalQuestion]:
    path = evals_dir / "visibility.jsonl"
    if not path.exists():
        raise SystemExit(
            f"score: no visibility suite at {path} (orgs without an ACL "
            f"overlay do not emit one)"
        )
    return [
        RetrievalQuestion.model_validate_json(line)
        for line in path.read_text("utf-8").splitlines()
        if line.strip()
    ]


def score_visibility(
    evals_dir: Path, answers: VisibilityAnswers
) -> RetrievalResult:
    return _score_docset(load_visibility_questions(evals_dir), answers)


def load_extraction_questions(evals_dir: Path) -> list[ExtractionQuestion]:
    path = evals_dir / "extraction.jsonl"
    if not path.exists():
        raise SystemExit(f"score: no extraction suite at {path}")
    return [
        ExtractionQuestion.model_validate_json(line)
        for line in path.read_text("utf-8").splitlines()
        if line.strip()
    ]


def score_extraction(
    evals_dir: Path, answers: ExtractionAnswers
) -> ExtractionResult:
    questions = load_extraction_questions(evals_dir)
    given = {a.id: a for a in answers.answers}
    result = ExtractionResult(total=len(questions), correct=0)
    for q in questions:
        answer = given.get(q.id)
        got_docs = {d.strip() for d in answer.docs} if answer else set()
        value_ok = answer is not None and answer.value.strip() == q.expected_value
        docs_ok = answer is not None and got_docs == set(q.expected_docs)
        if value_ok and docs_ok:
            result.correct += 1
            continue
        result.failures.append(
            {
                "id": q.id,
                "tags": q.tags,
                "location": q.location,
                "answered": answer is not None,
                "value_ok": value_ok,
                "expected_value": q.expected_value,
                "got_value": answer.value if answer else None,
                "docs_missing": sorted(set(q.expected_docs) - got_docs),
                "docs_extra": sorted(got_docs - set(q.expected_docs)),
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

    class_ids: dict[str, set] = {}
    for entity in expected.entities:
        for tag in entity.tags:
            if tag.startswith("ambiguity:"):
                class_ids.setdefault(tag.split(":", 1)[1], set()).add(entity.id)
    classes = {
        name: {
            "expected": len(ids),
            "matched": len(ids & matched_ids),
            "recall": round(len(ids & matched_ids) / len(ids), 4),
        }
        for name, ids in sorted(class_ids.items())
    }

    return GraphResult(
        entity_precision=entity_precision,
        entity_recall=entity_recall,
        edge_precision=edge_precision,
        edge_recall=edge_recall,
        classes=classes,
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
        elif suite == "visibility":
            answers = VisibilityAnswers.model_validate_json(raw)
        elif suite == "graph":
            answers = GraphAnswers.model_validate_json(raw)
        elif suite == "extraction":
            answers = ExtractionAnswers.model_validate_json(raw)
        else:
            raise SystemExit(
                f"score: unknown suite {suite!r} "
                f"(retrieval|graph|extraction|visibility)"
            )
    except ValidationError as err:
        print(
            f"score: answers file does not match the {suite} contract "
            "(see evals/README.md):\n" + strip_control(str(err))
        )
        return 2

    if suite in ("retrieval", "visibility"):
        scorer = score_retrieval if suite == "retrieval" else score_visibility
        result = scorer(evals_dir, answers)
        if as_json:
            print(
                json.dumps(
                    {
                        "suite": suite,
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
                f"{suite}: {result.correct}/{result.total} "
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
                # Failure lines echo answer-file content; never let an
                # untrusted string drive the terminal.
                print(strip_control(
                    f"  {failure['id']} [{','.join(failure['tags'])}] "
                    + "; ".join(parts)
                ))
        return 0

    if suite == "extraction":
        result = score_extraction(evals_dir, answers)
        if as_json:
            print(
                json.dumps(
                    {
                        "suite": "extraction",
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
                f"extraction: {result.correct}/{result.total} "
                f"({result.score:.1%})"
            )
            for failure in result.failures:
                parts = []
                if not failure["answered"]:
                    parts.append("unanswered")
                elif not failure["value_ok"]:
                    parts.append(
                        f"value {failure['got_value']!r} != "
                        f"{failure['expected_value']!r}"
                    )
                if failure["docs_missing"]:
                    parts.append(
                        "docs missing: " + ", ".join(failure["docs_missing"])
                    )
                if failure["docs_extra"]:
                    parts.append(
                        "docs extra: " + ", ".join(failure["docs_extra"])
                    )
                print(strip_control(
                    f"  {failure['id']} [loc:{failure['location']}] "
                    + "; ".join(parts)
                ))
        return 0

    result = score_graph(evals_dir, answers)
    payload = {
        "suite": "graph",
        "entity_precision": round(result.entity_precision, 4),
        "entity_recall": round(result.entity_recall, 4),
        "edge_precision": round(result.edge_precision, 4),
        "edge_recall": round(result.edge_recall, 4),
    }
    if result.classes:
        payload["classes"] = result.classes
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "graph: entities P={entity_precision:.1%} R={entity_recall:.1%}; "
            "edges P={edge_precision:.1%} R={edge_recall:.1%}".format(**payload)
        )
        for name, stats in result.classes.items():
            print(
                f"  class {name}: R={stats['recall']:.1%} "
                f"({stats['matched']}/{stats['expected']})"
            )
    return 0
