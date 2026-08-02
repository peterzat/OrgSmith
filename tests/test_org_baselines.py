"""Org tier: the keyless retrieval baselines (M17).

Baselines are reference points, never targets. Nothing here asserts a
threshold a generator change could be tuned against; what is asserted is
that the numbers are reproducible, that the floor is genuinely a floor
(neither retriever reaches ground truth), and that the two retrievers really
are different instruments.
"""

import pytest

from orgsmith.baselines import (
    RETRIEVERS,
    answer,
    bm25,
    derive_baseline,
    filename_only,
    render_fleet,
    tokenize,
)
from orgsmith.paths import OrgPaths
from orgsmith.schemas import BaselineSummary

from conftest import REPO, flagship_params

pytestmark = pytest.mark.org


def _committed_slugs():
    root = REPO / "companies"
    if not root.is_dir():
        return []
    return sorted(
        p.name
        for p in root.iterdir()
        if p.is_dir()
        and not p.name.endswith("-metadata")
        and (root / f"{p.name}-metadata" / "baselines").is_dir()
    )


SLUGS = _committed_slugs()


def _summary(slug) -> BaselineSummary:
    paths = OrgPaths(root=REPO, slug=slug)
    return BaselineSummary.model_validate_json(
        (paths.baselines_dir / "summary.json").read_text()
    )


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_committed_summary_recomputes_byte_identically(slug):
    """Recompute-and-compare, the ACL-03 pattern: a committed baseline is
    stale evidence the moment the suites move under it. Recomputed in
    memory against the committed org, so the check costs one text
    extraction pass rather than a copy of the whole share."""
    paths = OrgPaths(root=REPO, slug=slug)
    committed = BaselineSummary.model_validate_json(
        (paths.baselines_dir / "summary.json").read_text()
    )
    assert derive_baseline(paths) == committed, (
        f"{slug}: baselines/summary.json is stale; run "
        f"`python -m orgsmith baseline {slug}`"
    )


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_no_baseline_reaches_ground_truth(slug):
    """The floor is a floor. If a dumb lexical retriever matched the answer
    key, the suite would be measuring the filenames rather than the corpus."""
    for score in _summary(slug).scores:
        assert score.strict < 1.0, score
        assert score.ndcg_at_10 < 1.0, score


def test_the_two_retrievers_are_different_instruments():
    """Reading the document body has to buy something somewhere in the
    fleet, or the body-reading baseline measures nothing the filename does
    not. Asserted fleet-wide, not per org: on the scan-heavy orgs a
    synthetic OCR layer degrades exactly the text BM25 reads, so filename
    matching legitimately wins there. That is a result, not a bug."""
    leads = [
        slug
        for slug in SLUGS
        if any(
            s.ndcg_at_10
            > next(
                o.ndcg_at_10
                for o in _summary(slug).scores
                if o.retriever == "filename-only" and o.split == s.split
            )
            for s in _summary(slug).scores
            if s.retriever == "bm25"
        )
    ]
    assert leads, "bm25 never beats filename matching anywhere in the fleet"


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_every_split_and_retriever_is_covered(slug):
    summary = _summary(slug)
    assert {(s.retriever, s.split) for s in summary.scores} == {
        (r, split)
        for r in RETRIEVERS
        for split in ("core", "distractors", "noise", "full")
    }
    assert summary.config["k1"] == 1.5 and summary.config["b"] == 0.75


def test_fleet_table_is_fresh_and_covers_every_org():
    committed = (REPO / "docs" / "BASELINES.md").read_text()
    assert committed == render_fleet(REPO), (
        "docs/BASELINES.md is stale; run `python -m orgsmith baseline --fleet`"
    )
    for slug in SLUGS:
        assert f"## {slug}" in committed


def test_the_tokenizer_is_ascii_and_deterministic():
    """Deliberately ASCII-only, so a unicode-table change between Python
    versions cannot move a committed number."""
    assert tokenize("Fee: $105,000 (FY2021)") == ["fee", "105", "000", "fy2021"]
    assert tokenize("Café") == ["caf"]


def test_ranking_ties_break_by_ascending_path():
    corpus = {"b.docx": "fee fee", "a.docx": "fee fee", "c.docx": "nothing"}
    assert bm25("fee", corpus)[:2] == ["a.docx", "b.docx"]
    names = {"b - fee.docx": "", "a - fee.docx": ""}
    assert filename_only("fee", names) == ["a - fee.docx", "b - fee.docx"]


def test_a_baseline_answer_is_an_ordinary_answers_file():
    """No privileged path: the baseline hands the scorer the same contract
    any external system would."""

    from orgsmith.baselines import bm25_index

    class Q:
        id = "q:0001"
        question = "Which documents state the fee?"

    result = answer(bm25_index, [Q()], {"a.docx": "the fee is stated here"})
    assert result.suite == "retrieval"
    assert result.answers[0].id == "q:0001"
    assert result.answers[0].docs == ["a.docx"]
