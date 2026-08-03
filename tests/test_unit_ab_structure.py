"""M17c: the arm comparison reads every pair, not the printed reading list.

SPEC.md 2026-08-03 criterion four: the structural axis is compared over every
scored pair, "so a shift in the body of the distribution cannot hide behind
the truncated reading list. `STRUCTURAL_TOP_N` bounds what the report prints
and must not bound what the comparison reads."

That is a real hazard rather than a hypothetical one. `compute_pairs` defaults
to the top 50, and the outline work's whole mechanism is to spread documents
across a pool of 3-4 skeletons. If it works, the pairs that stop matching are
ordinary ones in the middle of the distribution; the handful of strongest
pairs may not move at all. A comparison that read only the head could see the
head unchanged and report no effect on a corpus where most of the body had
shifted.

Nothing here asserts a corpus number, and nothing here is a threshold.
"""

import pytest

from orgsmith.review import structure
from orgsmith.schemas import Block, DocIR

from tools.ab_compare import ALL_PAIRS, _dist

pytestmark = pytest.mark.unit


def _doc(doc_id: str, kinds: list[str]) -> DocIR:
    return DocIR(
        doc_id=doc_id,
        blocks=[Block(kind=k, text=f"{k} body text for {doc_id}") for k in kinds],
    )


def _corpus(n: int, genre: str = "status_report"):
    """`n` same-genre documents, so n*(n-1)/2 pairs. Shapes are varied so the
    scores are not all identical and a distribution exists to summarize."""
    shapes = [
        ["heading", "paragraph", "list", "paragraph"],
        ["paragraph", "table", "paragraph"],
        ["heading", "paragraph", "paragraph", "table", "paragraph"],
    ]
    authored, genre_of = {}, {}
    for i in range(1, n + 1):
        doc_id = f"d:{i:04d}"
        authored[doc_id] = _doc(doc_id, shapes[i % len(shapes)])
        genre_of[doc_id] = genre
    return authored, genre_of


def test_all_pairs_defeats_the_reading_list_cap():
    """The property criterion four turns on, stated as a comparison.

    Twenty documents give 190 pairs. The default returns the 50 a human
    reads; ALL_PAIRS must return all 190, and `considered` agrees with both.
    """
    authored, genre_of = _corpus(20)

    printed, considered = structure.compute_pairs(authored, genre_of)
    every, considered_again = structure.compute_pairs(
        authored, genre_of, top_n=ALL_PAIRS
    )

    assert considered == considered_again == 190
    assert len(printed) == structure.STRUCTURAL_TOP_N == 50
    assert len(every) == 190, (
        "the comparison must read every scored pair; truncating it would "
        "compare two reading lists and miss a shift in the body"
    )


def test_the_body_of_the_distribution_is_outside_the_printed_head():
    """Why the cap matters here specifically.

    The pairs the outline work is expected to move are ordinary ones, and on
    a corpus this size most of them fall outside the printed 50. If that were
    not true the cap would be harmless and this criterion would be pedantry.
    """
    authored, genre_of = _corpus(20)
    every, _ = structure.compute_pairs(authored, genre_of, top_n=ALL_PAIRS)
    printed = set(
        (p.doc_a, p.doc_b) for p in structure.compute_pairs(authored, genre_of)[0]
    )
    unread = [p for p in every if (p.doc_a, p.doc_b) not in printed]
    assert len(unread) == 140
    assert unread, "nothing outside the head means the cap could not hide anything"


def test_distribution_summary_reports_the_body_not_just_the_extremes():
    """`_dist` has to carry median and quartiles, not only mean and max.

    A mean moves for many reasons and a max is one pair. The quantiles are
    what make a claim about the body of the distribution legible.
    """
    d = _dist([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    assert d["n"] == 10
    assert d["p50"] == pytest.approx(0.45)
    assert d["p75"] == pytest.approx(0.7)
    assert d["p90"] == pytest.approx(0.9)
    assert d["max"] == pytest.approx(0.9)
    assert set(d) == {"n", "mean", "p50", "p75", "p90", "max"}


def test_empty_distribution_is_reported_not_crashed():
    """An arm with no authored prose yet must read as absent rather than as
    a zero score, which would look like a real measurement."""
    assert _dist([]) == {}
