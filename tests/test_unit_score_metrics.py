"""Unit tier: ranked retrieval metrics and the extraction split (M17).

The critique's third finding: scoring was an exact-set unit test. Binary set
equality, no ranking, no partial credit, and extraction ANDed its two halves
so a right value cited to the wrong document was indistinguishable from a
wrong value.

Scored against hand-written evals directories, so the arithmetic is checked
against numbers worked out by hand rather than against whatever a fixture
happens to produce.
"""

import json
import math

import pytest

from orgsmith.evals.score import score_extraction, score_retrieval
from orgsmith.schemas import (
    ExtractionAnswers,
    ExtractionQuestion,
    RetrievalAnswers,
    RetrievalQuestion,
)

pytestmark = pytest.mark.unit


def _write(evals_dir, name, models):
    evals_dir.mkdir(parents=True, exist_ok=True)
    (evals_dir / name).write_text(
        "\n".join(json.dumps(m.model_dump(mode="json")) for m in models) + "\n"
    )


@pytest.fixture()
def evals_dir(tmp_path):
    _write(
        tmp_path,
        "retrieval.jsonl",
        [
            RetrievalQuestion(
                id="q:0001",
                question="Which documents state the fee?",
                expected_docs=["a.docx", "b.docx"],
                tags=["fact:money"],
            ),
            RetrievalQuestion(
                id="q:0002",
                question="Which documents mention Ada Reyes?",
                expected_docs=["c.docx"],
                acceptable_docs=["incidental.docx"],
                tags=["mention:person", "p:ada.reyes"],
            ),
        ],
    )
    return tmp_path


def _score(evals_dir, answers):
    return score_retrieval(
        evals_dir,
        RetrievalAnswers.model_validate({"suite": "retrieval", "answers": answers}),
    )


def test_ground_truth_scores_perfect_on_every_metric(evals_dir):
    result = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["a.docx", "b.docx"]},
            {"id": "q:0002", "docs": ["c.docx"]},
        ],
    )
    assert result.correct == result.total == 2
    assert result.macro == {
        "questions": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0,
    }
    assert result.ranked == {
        "recall@5": 1.0,
        "recall@10": 1.0,
        "mrr": 1.0,
        "ndcg@10": 1.0,
    }


def test_rank_position_moves_mrr_and_ndcg_but_not_the_strict_headline(
    evals_dir,
):
    """Two answers with identical sets and different orders: the strict
    headline cannot tell them apart, which is exactly why ranked metrics
    exist."""
    ordered = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["a.docx", "b.docx"]},
            {"id": "q:0002", "docs": ["c.docx"]},
        ],
    )
    buried = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["a.docx", "b.docx"]},
            {"id": "q:0002", "docs": ["junk1.docx", "junk2.docx", "c.docx"]},
        ],
    )
    assert buried.correct == 1 < ordered.correct
    assert buried.ranked["mrr"] == pytest.approx((1.0 + 1 / 3) / 2, abs=1e-4)
    # q:0002's single hit sits at rank 3 -> gain 1/log2(4) against an ideal
    # of 1/log2(2).
    assert buried.ranked["ndcg@10"] == pytest.approx(
        (1.0 + (1 / math.log2(4))) / 2, abs=1e-4
    )
    assert buried.ranked["recall@5"] == 1.0


def test_partial_recall_is_visible_where_the_headline_is_binary(evals_dir):
    result = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["a.docx"]},
            {"id": "q:0002", "docs": ["c.docx"]},
        ],
    )
    assert result.correct == 1, "the strict headline still fails a half answer"
    assert result.macro["recall"] == pytest.approx(0.75)  # (0.5 + 1.0) / 2
    assert result.macro["precision"] == 1.0
    assert result.ranked["recall@5"] == pytest.approx(0.75)


def test_an_acceptable_document_occupies_no_rank(evals_dir):
    """Returning an incidental document ahead of the answer must not push
    the answer down the ranking: acceptable documents are condensed out."""
    result = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["a.docx", "b.docx"]},
            {"id": "q:0002", "docs": ["incidental.docx", "c.docx"]},
        ],
    )
    assert result.correct == result.total == 2
    assert result.ranked["mrr"] == 1.0


def test_duplicate_entries_are_deduped_keeping_the_first(evals_dir):
    result = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["a.docx", "a.docx", "b.docx"]},
            {"id": "q:0002", "docs": ["c.docx"]},
        ],
    )
    assert result.correct == result.total == 2
    assert result.macro["precision"] == 1.0


def test_extraction_reports_value_and_attribution_separately(tmp_path):
    _write(
        tmp_path,
        "extraction.jsonl",
        [
            ExtractionQuestion(
                id="xq:0001",
                fact_id="f:E-2021-001.fee",
                question="What is the fee?",
                expected_value="$105,000",
                expected_docs=["letter.pdf"],
            ),
            ExtractionQuestion(
                id="xq:0002",
                fact_id="f:E-2021-001.start",
                question="When did it start?",
                expected_value="2021-03-01",
                expected_docs=["letter.pdf"],
            ),
        ],
    )
    result = score_extraction(
        tmp_path,
        ExtractionAnswers.model_validate(
            {
                "suite": "extraction",
                "answers": [
                    # right value, wrong document
                    {
                        "id": "xq:0001",
                        "value": "$105,000",
                        "docs": ["minutes.docx"],
                    },
                    # right document, wrong value
                    {
                        "id": "xq:0002",
                        "value": "2021-04-01",
                        "docs": ["letter.pdf"],
                    },
                ],
            }
        ),
    )
    assert result.correct == 0, "the conjunctive headline fails both"
    assert result.value_correct == 1 and result.value_accuracy == 0.5
    assert result.attribution_correct == 1
    assert result.attribution_accuracy == 0.5
