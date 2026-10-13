"""Unit tier: unanswerable questions (M17).

A question whose corpus holds no answer used to be dropped, which taught the
suite that everything asked is answerable. It is emitted with
`answerable: false` instead. Scored against a hand-written evals directory,
and emitted from a synthetic org, so nothing here depends on a fixture that a
regeneration could retire.
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


# --- emitted, not hand-written (re-hosted M17e) ----------------------------
#
# The org-tier check `test_unanswerable_questions_are_really_unanswerable`
# runs the emit-and-score path on every committed org that poses an
# unanswerable question. Until M17e exactly one did: hollowell-ip, whose
# Sharon Woods was named only in mundane mail. Its regeneration placed her in
# engagement documents, so the committed fleet now poses none and the org
# check skips everywhere. The path is re-hosted here on a synthetic org whose
# plan places one roster member nowhere, so it can never skip into a silent
# pass again.


@pytest.fixture(scope="module")
def unplaced(tmp_path_factory):
    from conftest import build_knobbed_stages, build_rendered
    from orgsmith.artifacts import load_foundation, load_mention_map
    from orgsmith.evals.emit import run_emit_evals
    from orgsmith.schemas import dump_json

    paths = build_rendered(
        build_knobbed_stages(tmp_path_factory.mktemp("unplaced-org"))
    )
    person = load_foundation(paths).people[-1]
    mention_map = load_mention_map(paths)
    mention_map.mentions = [
        r for r in mention_map.mentions if r.entity != person.id
    ]
    paths.mention_map_json.write_text(dump_json(mention_map))
    assert run_emit_evals(paths) == 0
    lines = (paths.evals_dir / "retrieval.jsonl").read_text().splitlines()
    return paths, person, [json.loads(line) for line in lines if line.strip()]


def test_a_person_the_plan_never_placed_is_asked_and_unanswerable(unplaced):
    _, person, questions = unplaced
    (question,) = [
        q for q in questions
        if q["tags"] == ["mention:person", person.id]
    ]
    assert question["answerable"] is False
    assert question["expected_docs"] == []


def test_emitted_abstention_scores_correct_and_invention_fails(unplaced):
    paths, _, questions = unplaced
    unanswerable = [q for q in questions if not q["answerable"]]
    assert unanswerable
    for question in unanswerable:
        assert question["expected_docs"] == [], question["id"]

    def answer(docs_for):
        return _score(
            paths.evals_dir,
            [{"id": q["id"], "docs": docs_for(q)} for q in questions],
        )

    abstained = answer(lambda q: q["expected_docs"])
    assert abstained.total and abstained.correct == abstained.total
    invented = answer(lambda q: q["expected_docs"] or ["TOC.md"])
    assert invented.correct == abstained.correct - len(unanswerable)
    ids = {q["id"] for q in unanswerable}
    assert all(f["abstention_expected"] for f in invented.failures if f["id"] in ids)
