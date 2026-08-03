"""M17c: the two analyses the evidence standard calls discriminating.

`docs/M17C-EVIDENCE-STANDARD.md` fixes three comparisons before either arm is
authored and is explicit that the headline structural one is the weakest,
because dealing skeletons and enforcing what they forbid makes a shape drop
close to mechanically guaranteed. The two that actually discriminate are
covered here:

1. treatment pairs whose documents share an outline id, against control pairs;
2. the lexical axis across arms, which no outline directly controls.

These are tested before any prose exists on purpose. Pre-registration is only
worth what it fixes in advance, and an analysis implemented after the numbers
arrive can be shaped by them.
"""

import pytest

from orgsmith.review.corpus import jaccard, shingles
from orgsmith.schemas import StructurePair

from tools.ab_compare import _dist, split_by_outline

pytestmark = pytest.mark.unit


def _pair(a: str, b: str, shape: float = 0.5, openers: float = 0.5) -> StructurePair:
    return StructurePair(
        doc_a=a, doc_b=b, genre="status_report", shape=shape, openers=openers
    )


def test_split_by_outline_separates_same_from_different_skeletons():
    outlines = {
        "d:0001": "sr-exception",
        "d:0002": "sr-exception",
        "d:0003": "sr-narrative",
    }
    pairs = [_pair("d:0001", "d:0002"), _pair("d:0001", "d:0003")]

    same, different, unknown = split_by_outline(pairs, outlines)

    assert [p.doc_b for p in same] == ["d:0002"]
    assert [p.doc_b for p in different] == ["d:0003"]
    assert unknown == []


def test_a_pair_with_an_unassigned_document_is_neither_same_nor_different():
    """Not every authored document gets a skeleton: `assign_outlines` returns
    None for a genre with no pool. Bucketing those as 'different' would
    silently pad the comparison group with pairs the treatment never acted on.
    """
    outlines = {"d:0001": "sr-exception"}
    pairs = [_pair("d:0001", "d:0099")]

    same, different, unknown = split_by_outline(pairs, outlines)

    assert same == [] and different == []
    assert [p.doc_b for p in unknown] == ["d:0099"]


def test_a_control_arm_splits_into_nothing_but_unknown():
    """The control carries no outline ids at all, which is what makes this a
    treatment-arm analysis. It must not silently report an empty 'same
    skeleton' group as a measured zero."""
    pairs = [_pair("d:0001", "d:0002")]

    same, different, unknown = split_by_outline(pairs, {})

    assert same == [] and different == []
    assert len(unknown) == 1
    assert _dist([]) == {}, "an empty group must read as absent, not as 0.0"


def test_lexical_zeros_are_kept_so_the_arms_stay_comparable():
    """The one place this deliberately diverges from `metrics.compute`.

    That function drops pairs scoring 0 because it is building a reading
    list. Keeping them matters here: if one arm has more non-overlapping
    pairs than the other, dropping zeros changes the two arms' pair counts
    for a reason unrelated to the treatment, and the means stop being
    comparable. This asserts the arithmetic that makes the difference.
    """
    disjoint = jaccard(
        shingles("alpha beta gamma delta epsilon"),
        shingles("one two three four five"),
    )
    assert disjoint == 0.0

    kept = _dist([0.0, 0.0, 0.4])
    dropped = _dist([0.4])
    assert kept["n"] == 3 and dropped["n"] == 1
    assert kept["mean"] == pytest.approx(0.4 / 3)
    assert dropped["mean"] == pytest.approx(0.4)
    assert kept["mean"] != dropped["mean"], (
        "dropping zeros moves the mean; across two arms with different zero "
        "counts that difference is an artifact of the filter, not the knob"
    )


def test_identical_text_scores_one_and_anchors_the_axis():
    text = "the quarterly review covered scope schedule and budget in that order"
    assert jaccard(shingles(text), shingles(text)) == pytest.approx(1.0)
