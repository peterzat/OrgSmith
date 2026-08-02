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
    # M17: set-level macro precision/recall/F1 and the rank-aware metrics,
    # both computed over the condensed answer list. Empty for the visibility
    # suite, which is graded as a raw exact set and has no meaningful rank
    # (the question is "which documents may this person read?", not "which
    # are most relevant?").
    macro: dict = field(default_factory=dict)
    ranked: dict = field(default_factory=dict)

    @property
    def score(self) -> float:
        return self.correct / self.total if self.total else 0.0


@dataclass
class ExtractionResult:
    total: int
    correct: int
    failures: list[dict] = field(default_factory=list)
    # M17: the two halves of the conjunctive headline, reported separately.
    # "Found the right value but cited the wrong document" and "cited the
    # right document but read the wrong value" are different failures and a
    # single AND-ed number hides which one you have.
    value_correct: int = 0
    attribution_correct: int = 0

    @property
    def score(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def value_accuracy(self) -> float:
        return self.value_correct / self.total if self.total else 0.0

    @property
    def attribution_accuracy(self) -> float:
        return self.attribution_correct / self.total if self.total else 0.0


def _rank_metrics(required: set[str], condensed: list[str]) -> dict:
    """Rank-aware credit for one question, over the condensed answer list.

    Binary gains (a document either answers the question or does not), and
    no tie handling: the rank is the order the system wrote its answer in,
    which is total by construction."""
    import math

    ranks = [i for i, doc in enumerate(condensed) if doc in required]
    dcg = sum(1.0 / math.log2(i + 2) for i in ranks if i < 10)
    ideal = sum(
        1.0 / math.log2(i + 2) for i in range(min(10, len(required)))
    )
    return {
        "recall@5": len([i for i in ranks if i < 5]) / len(required),
        "recall@10": len([i for i in ranks if i < 10]) / len(required),
        "rr": 1.0 / (ranks[0] + 1) if ranks else 0.0,
        "ndcg@10": (dcg / ideal) if ideal else 0.0,
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


@dataclass
class GraphResult:
    entity_precision: float
    entity_recall: float
    edge_precision: float
    edge_recall: float
    # per ambiguity class: {"expected": n, "matched": m, "recall": r};
    # empty when the org's ground truth carries no ambiguity tags
    classes: dict = field(default_factory=dict)
    # M17: per edge kind {"expected": n, "matched": m, "recall": r}, so
    # "who worked on what" (participant edges) is visible separately from
    # the org chart.
    edge_kinds: dict = field(default_factory=dict)
    # M17: of the correctly-identified edges whose ground truth carries
    # dates, the share whose answer got both dates right. None when the
    # answer file supplies no dates at all, so a dateless answer reads as
    # "did not attempt" rather than "scored zero".
    dated_edge_credit: float | None = None
    dated_edges_eligible: int = 0
    dated_edges_credited: int = 0


def load_questions(evals_dir: Path) -> list[RetrievalQuestion]:
    path = evals_dir / "retrieval.jsonl"
    if not path.exists():
        raise SystemExit(f"score: no retrieval suite at {path}")
    return [
        RetrievalQuestion.model_validate_json(line)
        for line in path.read_text("utf-8").splitlines()
        if line.strip()
    ]


def load_split_corpus(evals_dir: Path, split: str) -> set[str]:
    """The document set of one corpus split (M12), from splits.json. A split
    restricts which documents a system searched; grading a split ignores
    questions whose answers are not in that corpus, so ground-truth answers
    score 100% on every split by construction."""
    path = evals_dir / "splits.json"
    if not path.exists():
        raise SystemExit(
            f"score: no splits at {path} (run emit-evals to derive them)"
        )
    splits = json.loads(path.read_text("utf-8")).get("splits", {})
    if split not in splits:
        raise SystemExit(
            f"score: unknown split {split!r}; choose from {sorted(splits)}"
        )
    return set(splits[split])


def load_canonical_map(evals_dir: Path) -> dict[str, str]:
    """{member path: canonical path} from clusters.json (M17).

    A document that carries byte-identical evidence to another (a derived
    exact duplicate, a misfiled copy, a transmittal email attaching it)
    answers every question its canonical answers, so scoring maps both the
    expected and the returned sets through this table before comparing.

    Returns an empty map when the org emitted no clusters.json, which makes
    canonicalization the identity function: a pre-M17 `evals/` directory
    scores byte-identically through this scorer."""
    path = evals_dir / "clusters.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text("utf-8"))
    return {
        member["path"]: cluster["canonical"]
        for cluster in data.get("clusters", [])
        for member in cluster.get("members", [])
    }


def _canonicalize(docs, canonical: dict[str, str]) -> set[str]:
    return {canonical.get(d, d) for d in docs}


def _score_docset(
    questions: list[RetrievalQuestion],
    answers,
    corpus: set[str] | None = None,
    canonical: dict[str, str] | None = None,
    ranked: bool = False,
) -> RetrievalResult:
    """Exact doc-set matching, shared by the retrieval and visibility
    suites (identical answers contract). When `corpus` is given (a split), a
    question whose expected answers are not all in the split is not gradable
    there and is skipped, so ground truth scores 100% on every split.

    `ranked` adds the set-level macro metrics and the rank-aware ones,
    computed over questions with a non-empty required set. An unanswerable
    question is excluded from those aggregates (recall, MRR, and nDCG are
    all undefined against an empty required set) but is still graded by the
    strict headline, where abstaining is the correct answer. Visibility
    passes `ranked=False`: it is a raw exact set with no notion of rank.

    M17: both sides are canonicalized through the equivalence clusters
    first, so returning a byte-identical copy of an expected document (or
    both the copy and the original) is correct rather than an error. Then
    the question's acceptable documents are dropped from the answer: their
    rendered text carries the same evidence, so returning one is never
    penalized, and they are never required, so missing one costs nothing.

    Order matters. Canonicalization runs first because a cluster member
    stands in for its original; acceptable documents are dropped second and
    are never cluster members, so the two relaxations cannot interfere."""
    canonical = canonical or {}
    given = {a.id: a.docs for a in answers.answers}
    gradable = [
        q
        for q in questions
        if corpus is None or set(q.expected_docs) <= corpus
    ]
    result = RetrievalResult(total=len(gradable), correct=0)
    precisions: list[float] = []
    recalls: list[float] = []
    f1s: list[float] = []
    per_question: list[dict] = []
    for q in gradable:
        expected = _canonicalize(q.expected_docs, canonical)
        acceptable = set(q.acceptable_docs) - expected
        raw = [d.strip() for d in given.get(q.id, [])]
        # The condensed list: canonicalized, acceptable documents removed so
        # they occupy no rank and earn no penalty, deduped keeping the first
        # occurrence so the system's own ordering survives.
        condensed: list[str] = []
        for doc in raw:
            doc = canonical.get(doc, doc)
            if doc not in acceptable and doc not in condensed:
                condensed.append(doc)
        got = set(condensed)

        if ranked and expected:
            hits = len(expected & got)
            precision = hits / len(condensed) if condensed else 0.0
            recall = hits / len(expected)
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(
                2 * precision * recall / (precision + recall)
                if precision + recall
                else 0.0
            )
            per_question.append(_rank_metrics(expected, condensed))

        if got == expected:
            result.correct += 1
            continue
        result.failures.append(
            {
                "id": q.id,
                "tags": q.tags,
                # An unanswerable question is failed only by inventing an
                # answer, so say that rather than listing "extra" documents
                # against an empty expected set.
                "abstention_expected": not q.answerable,
                "missing": sorted(expected - got),
                # Report what the system actually returned, not its
                # canonical form, so a failure line names a real path.
                # Acceptable documents never appear here: they were dropped.
                "extra": sorted(
                    d
                    for d in raw
                    if canonical.get(d, d) not in expected
                    and canonical.get(d, d) not in acceptable
                ),
                "answered": q.id in given,
            }
        )

    if ranked and per_question:
        result.macro = {
            "questions": len(per_question),
            "precision": round(_mean(precisions), 4),
            "recall": round(_mean(recalls), 4),
            "f1": round(_mean(f1s), 4),
        }
        result.ranked = {
            "recall@5": round(_mean([m["recall@5"] for m in per_question]), 4),
            "recall@10": round(
                _mean([m["recall@10"] for m in per_question]), 4
            ),
            "mrr": round(_mean([m["rr"] for m in per_question]), 4),
            "ndcg@10": round(_mean([m["ndcg@10"] for m in per_question]), 4),
        }
    return result


def score_retrieval(
    evals_dir: Path, answers: RetrievalAnswers, corpus: set[str] | None = None
) -> RetrievalResult:
    return _score_docset(
        load_questions(evals_dir),
        answers,
        corpus,
        load_canonical_map(evals_dir),
        ranked=True,
    )


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
    evals_dir: Path, answers: VisibilityAnswers, corpus: set[str] | None = None
) -> RetrievalResult:
    return _score_docset(load_visibility_questions(evals_dir), answers, corpus)


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
    evals_dir: Path, answers: ExtractionAnswers, corpus: set[str] | None = None
) -> ExtractionResult:
    questions = load_extraction_questions(evals_dir)
    canonical = load_canonical_map(evals_dir)
    given = {a.id: a for a in answers.answers}
    gradable = [
        q
        for q in questions
        if corpus is None or set(q.expected_docs) <= corpus
    ]
    result = ExtractionResult(total=len(gradable), correct=0)
    for q in gradable:
        answer = given.get(q.id)
        raw_docs = [d.strip() for d in answer.docs] if answer else []
        expected_docs = _canonicalize(q.expected_docs, canonical)
        got_docs = _canonicalize(raw_docs, canonical)
        value_ok = answer is not None and answer.value.strip() == q.expected_value
        docs_ok = answer is not None and got_docs == expected_docs
        result.value_correct += int(value_ok)
        result.attribution_correct += int(docs_ok)
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
                "docs_missing": sorted(expected_docs - got_docs),
                "docs_extra": sorted(
                    d for d in raw_docs if canonical.get(d, d) not in expected_docs
                ),
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
    expected_dates = {
        (e.src, e.dst, e.kind): (e.start, e.end) for e in expected.edges
    }
    resolved = []
    for edge in answers.edges:
        src = index.get(edge.src.casefold())
        dst = index.get(edge.dst.casefold())
        resolved.append(((src, dst, edge.kind), edge))
    hits = {t for t, _ in resolved if t in expected_edges}
    edge_precision = len(hits) / len(resolved) if resolved else 0.0
    edge_recall = len(hits) / len(expected_edges) if expected_edges else 0.0

    edge_kinds: dict = {}
    for key in expected_edges:
        stats = edge_kinds.setdefault(key[2], {"expected": 0, "matched": 0})
        stats["expected"] += 1
        stats["matched"] += int(key in hits)
    edge_kinds = {
        kind: {**stats, "recall": round(stats["matched"] / stats["expected"], 4)}
        for kind, stats in sorted(edge_kinds.items())
    }

    # Dated-edge credit: of the correct edges whose ground truth carries
    # dates, how many did the answer date correctly? Attempted only when the
    # answer file supplies at least one date, so a dateless answer scores
    # identical edge precision and recall and reports no credit at all.
    attempted = any(e.start or e.end for _, e in resolved)
    eligible = credited = 0
    for key, edge in resolved:
        if key not in expected_edges:
            continue
        want = expected_dates.get(key)
        if want is None or (want[0] is None and want[1] is None):
            continue
        eligible += 1
        credited += int((edge.start, edge.end) == want)
    dated_credit = (
        (credited / eligible if eligible else 0.0) if attempted else None
    )

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
        edge_kinds=edge_kinds,
        dated_edge_credit=dated_credit,
        dated_edges_eligible=eligible if attempted else 0,
        dated_edges_credited=credited if attempted else 0,
    )


def run_score(
    evals_dir: Path,
    suite: str,
    answers_path: Path,
    as_json: bool = False,
    split: str | None = None,
) -> int:
    if not answers_path.exists():
        raise SystemExit(f"score: no answers file at {answers_path}")
    corpus = None
    if split is not None:
        if suite == "graph":
            raise SystemExit(
                "score: --split does not apply to the graph suite "
                "(it grades entities and edges, not a document corpus)"
            )
        corpus = load_split_corpus(evals_dir, split)
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
        result = scorer(evals_dir, answers, corpus)
        if as_json:
            payload = {
                "suite": suite,
                "total": result.total,
                "correct": result.correct,
                "score": round(result.score, 4),
            }
            if result.macro:
                payload["macro"] = result.macro
            if result.ranked:
                payload["ranked"] = result.ranked
            payload["failures"] = result.failures
            print(json.dumps(payload, indent=2))
        else:
            print(
                f"{suite}: {result.correct}/{result.total} "
                f"({result.score:.1%})"
            )
            if result.macro:
                print(
                    "  macro P={precision:.1%} R={recall:.1%} "
                    "F1={f1:.1%} (over {questions} answerable "
                    "questions)".format(**result.macro)
                )
            if result.ranked:
                print(
                    "  ranked R@5={recall@5:.1%} R@10={recall@10:.1%} "
                    "MRR={mrr:.3f} nDCG@10={ndcg@10:.3f}".format(
                        **result.ranked
                    )
                )
            for failure in result.failures:
                parts = []
                if failure.get("abstention_expected"):
                    parts.append("expected abstention")
                elif not failure["answered"]:
                    parts.append("unanswered")
                if failure["missing"]:
                    parts.append("missing: " + ", ".join(failure["missing"]))
                if failure["extra"]:
                    parts.append("extra: " + ", ".join(failure["extra"]))
                # Failure lines echo answer-file content; never let an
                # untrusted string drive the terminal. One failure is one
                # line: keep="" so an embedded newline cannot forge a
                # second line of output.
                print(strip_control(
                    f"  {failure['id']} [{','.join(failure['tags'])}] "
                    + "; ".join(parts),
                    keep="",
                ))
        return 0

    if suite == "extraction":
        result = score_extraction(evals_dir, answers, corpus)
        if as_json:
            print(
                json.dumps(
                    {
                        "suite": "extraction",
                        "total": result.total,
                        "correct": result.correct,
                        "score": round(result.score, 4),
                        "value_accuracy": round(result.value_accuracy, 4),
                        "attribution_accuracy": round(
                            result.attribution_accuracy, 4
                        ),
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
            print(
                f"  value {result.value_correct}/{result.total} "
                f"({result.value_accuracy:.1%}); attribution "
                f"{result.attribution_correct}/{result.total} "
                f"({result.attribution_accuracy:.1%})"
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
                    + "; ".join(parts),
                    keep="",
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
    if result.edge_kinds:
        payload["edge_kinds"] = result.edge_kinds
    if result.dated_edge_credit is not None:
        payload["dated_edge_credit"] = round(result.dated_edge_credit, 4)
        payload["dated_edges_eligible"] = result.dated_edges_eligible
        payload["dated_edges_credited"] = result.dated_edges_credited
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "graph: entities P={entity_precision:.1%} R={entity_recall:.1%}; "
            "edges P={edge_precision:.1%} R={edge_recall:.1%}".format(**payload)
        )
        for kind, stats in result.edge_kinds.items():
            print(
                f"  edges {kind}: R={stats['recall']:.1%} "
                f"({stats['matched']}/{stats['expected']})"
            )
        if result.dated_edge_credit is not None:
            print(
                f"  dated edges: {result.dated_edges_credited}/"
                f"{result.dated_edges_eligible} "
                f"({result.dated_edge_credit:.1%})"
            )
        for name, stats in result.classes.items():
            # Class names come from ambiguity tags in a third-party
            # graph_expected.json (`--evals-dir` is a supported input);
            # never let them drive the terminal.
            print(strip_control(
                f"  class {name}: R={stats['recall']:.1%} "
                f"({stats['matched']}/{stats['expected']})",
                keep="",
            ))
    return 0
