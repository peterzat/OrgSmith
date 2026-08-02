"""Unit tier: unanswerable questions (M17).

A question whose corpus holds no answer used to be dropped, which taught the
suite that everything asked is answerable. It is emitted with
`answerable: false` instead. Scored against a hand-written evals directory,
so nothing here depends on a fixture that a regeneration could retire.
"""

import json

import pytest

from orgsmith.evals.score import score_retrieval
from orgsmith.schemas import RetrievalAnswers, RetrievalQuestion

pytestmark = pytest.mark.unit


@pytest.fixture()
def evals_dir(tmp_path):
    questions = [
        RetrievalQuestion(
            id="q:0001",
            question="Which documents mention Ada Reyes?",
            expected_docs=["Firm/Overview.docx"],
            tags=["mention:person", "p:ada.reyes"],
        ),
        RetrievalQuestion(
            id="q:0002",
            question="Which documents mention Sharon Woods?",
            expected_docs=[],
            acceptable_docs=["Firm/Internal Email 1.eml"],
            answerable=False,
            tags=["mention:person", "p:sharon.woods"],
        ),
    ]
    (tmp_path / "retrieval.jsonl").write_text(
        "\n".join(json.dumps(q.model_dump(mode="json")) for q in questions)
        + "\n"
    )
    return tmp_path


def _score(evals_dir, answers):
    return score_retrieval(
        evals_dir,
        RetrievalAnswers.model_validate({"suite": "retrieval", "answers": answers}),
    )


def test_omitting_the_question_entirely_is_correct(evals_dir):
    result = _score(evals_dir, [{"id": "q:0001", "docs": ["Firm/Overview.docx"]}])
    assert (result.correct, result.total) == (2, 2)


def test_an_explicit_empty_answer_is_correct(evals_dir):
    result = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["Firm/Overview.docx"]},
            {"id": "q:0002", "docs": []},
        ],
    )
    assert (result.correct, result.total) == (2, 2)


def test_returning_only_acceptable_documents_is_correct(evals_dir):
    result = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["Firm/Overview.docx"]},
            {"id": "q:0002", "docs": ["Firm/Internal Email 1.eml"]},
        ],
    )
    assert (result.correct, result.total) == (2, 2)


def test_an_invented_answer_fails_with_expected_abstention(evals_dir):
    result = _score(
        evals_dir,
        [
            {"id": "q:0001", "docs": ["Firm/Overview.docx"]},
            {"id": "q:0002", "docs": ["Firm/Overview.docx"]},
        ],
    )
    assert (result.correct, result.total) == (1, 2)
    (failure,) = result.failures
    assert failure["id"] == "q:0002"
    assert failure["abstention_expected"] is True
    assert failure["extra"] == ["Firm/Overview.docx"]


def test_an_answerable_question_is_not_marked_for_abstention(evals_dir):
    result = _score(evals_dir, [{"id": "q:0001", "docs": ["wrong.docx"]}])
    failure = next(f for f in result.failures if f["id"] == "q:0001")
    assert failure["abstention_expected"] is False


def test_the_printed_failure_says_expected_abstention(evals_dir, capsys, tmp_path):
    from orgsmith.evals.score import run_score

    answers = tmp_path / "answers.json"
    answers.write_text(
        json.dumps(
            {
                "suite": "retrieval",
                "answers": [{"id": "q:0002", "docs": ["Firm/Overview.docx"]}],
            }
        )
    )
    assert run_score(evals_dir, "retrieval", answers) == 0
    out = capsys.readouterr().out
    assert "expected abstention" in out
