"""Unit tier: the structural similarity axis (M17b, part C).

The claim under test is narrow and it is the whole reason the axis exists:
the lexical metric cannot see a document that was re-skinned rather than
rewritten. So the two shaped fixtures here are constructed rather than
sampled -- a paraphrase twin (identical skeleton, disjoint vocabulary) and
its inverse (same words, different shape) -- and each is asserted to score
high on one axis and near the floor on the other.

Nothing here asserts a corpus number. `docs/REVIEW-CALIBRATION.md` records
what the axis measured against the frozen exemplar as a dated measurement;
turning any of those numbers into an assert would make a proxy a gate, which
TESTING.md forbids and which is exactly how the lexical metric came to be
trusted further than it earns.
"""

import pytest

from orgsmith.review import structure
from orgsmith.schemas import Block, DocIR

pytestmark = pytest.mark.unit


def _doc(doc_id: str, blocks: list[dict]) -> DocIR:
    return DocIR(doc_id=doc_id, blocks=[Block(**b) for b in blocks])


# A four-block memo: title, opening paragraph, a list of owners, a closing
# paragraph. Both twins below are this skeleton.
def _memo(doc_id: str, words: list[str], openers: list[str]) -> DocIR:
    body = " ".join(words)
    return _doc(
        doc_id,
        [
            {"kind": "heading", "text": f"{openers[0]} {body}", "level": 1},
            {"kind": "paragraph", "text": f"{openers[1]} {body} {body} {body}"},
            {
                "kind": "list",
                "items": [f"{openers[2]} {body}", f"{openers[3]} {body}"],
            },
            {"kind": "paragraph", "text": f"{openers[4]} {body} {body} {body}"},
        ],
    )


LATINATE = "engagement scope deliverable milestone stakeholder governance".split()
SAXON = "work reach output step owner oversight".split()

# The five opening moves, all content words. Deliberately not stopwords: the
# openers axis is POSITIONAL LEXIS, not structure, so it is supposed to
# degrade when the words change. The twins below keep their moves and swap
# their bodies, which is the case the axis exists to catch.
MOVES = ["Kickoff", "Purpose", "First", "Second", "Finally"]


def test_paraphrase_twin_scores_high_on_shape_and_near_zero_lexically():
    """The defect the axis exists for: same document, every word replaced.

    Jaccard is computed here rather than imported as a fixture number so the
    contrast is proven on this pair rather than asserted about another one.
    """
    from orgsmith.review.corpus import jaccard, prose_text, shingles

    a = _memo("d:0001", LATINATE, MOVES)
    b = _memo("d:0002", SAXON, MOVES)

    shape, openers = structure.pair_scores(a, b)
    lexical = jaccard(shingles(prose_text(a)), shingles(prose_text(b)))

    assert shape == 1.0, "identical skeletons must score 1.0 on shape"
    assert openers == 1.0, "identical opening moves must score 1.0 on openers"
    assert lexical < 0.05, (
        f"the twins share {lexical:.4f} 4-gram Jaccard; the fixture is "
        f"supposed to have disjoint vocabulary"
    )


def test_same_words_different_shape_inverts():
    """The inverse control. One document's words, poured into a different
    skeleton: the lexical axis sees a match and the structural axis does
    not."""
    from orgsmith.review.corpus import jaccard, prose_text, shingles

    words = " ".join(LATINATE * 6)
    prose = _doc(
        "d:0003",
        [
            {"kind": "heading", "text": "Kickoff", "level": 1},
            {"kind": "paragraph", "text": words},
            {"kind": "paragraph", "text": words},
        ],
    )
    tabular = _doc(
        "d:0004",
        [
            {"kind": "table", "header": ["a", "b"], "rows": [[words, words]]},
            {"kind": "sigblock", "signers": ["p:one"]},
        ],
    )

    shape, _openers = structure.pair_scores(prose, tabular)
    lexical = jaccard(shingles(prose_text(prose)), shingles(prose_text(tabular)))

    assert shape == 0.0, "no block kind is shared; shape must find nothing"
    assert lexical > 0.5, (
        f"the pair shares only {lexical:.4f} 4-gram Jaccard; the fixture is "
        f"supposed to reuse the same words"
    )


def test_shape_tokens_carry_no_authored_word():
    """The property that makes the axis paraphrase-proof, asserted directly
    rather than inferred from a score: no token is a word from the prose."""
    doc = _doc(
        "d:0005",
        [
            {"kind": "heading", "text": " ".join(LATINATE), "level": 2},
            {"kind": "paragraph", "text": " ".join(LATINATE * 3)},  # 18 words
            {"kind": "paragraph", "text": " ".join(LATINATE * 12)},  # 72 words
            {"kind": "list", "items": [" ".join(LATINATE)] * 4},
            {"kind": "table", "header": ["a", "b"], "rows": [["x", "y"]] * 3},
            {"kind": "sigblock", "signers": ["p:one"]},
        ],
    )
    assert structure.shape_tokens(doc) == ["H2", "P0", "P2", "L1", "T3x2", "SIG"]
    lowered = " ".join(structure.shape_tokens(doc)).lower()
    for word in LATINATE:
        assert word not in lowered


def test_openers_skip_the_stoplist_to_reach_the_move():
    """"We recommend", "The team recommends" and "Our recommendation" all
    open on the move, which is what makes recurring moves visible."""
    doc = _doc(
        "d:0006",
        [
            {"kind": "paragraph", "text": "We recommend proceeding."},
            {"kind": "paragraph", "text": "The team recommends proceeding."},
            {"kind": "paragraph", "text": "Our recommendation is to proceed."},
        ],
    )
    assert structure.opener_tokens(doc) == [
        "recommend",
        "team",
        "recommendation",
    ]


def test_a_unit_with_no_content_word_keeps_its_position():
    """A placeholder-only or stopword-only unit still emits a token, so the
    two opener sequences stay aligned unit for unit."""
    doc = _doc(
        "d:0007",
        [
            {"kind": "paragraph", "text": "{{fact:E-1.fee}}"},
            {"kind": "paragraph", "text": "The engagement closed."},
        ],
    )
    assert structure.opener_tokens(doc) == [structure._NO_OPENER, "engagement"]


def test_placeholders_never_become_openers():
    """A fact placeholder is pipeline scaffolding the author did not write.
    Two documents opening on the same placeholder are the docplan agreeing
    with itself, not two authors making the same move."""
    doc = _doc(
        "d:0008",
        [{"kind": "paragraph", "text": "{{fact:E-1.fee}} covers the scope."}],
    )
    assert structure.opener_tokens(doc) == ["covers"]


def test_empty_document_scores_zero_not_one():
    """`SequenceMatcher` calls two empty sequences a perfect match. A
    document with no blocks is missing data, and scoring it 1.0 would put
    every unauthored pair at the top of the board's reading list."""
    empty_a, empty_b = _doc("d:0009", []), _doc("d:0010", [])
    assert structure.pair_scores(empty_a, empty_b) == (0.0, 0.0)


def test_compute_pairs_is_same_genre_only_and_totally_ordered():
    a = _memo("d:0001", LATINATE, MOVES)
    b = _memo("d:0002", SAXON, MOVES)
    c = _doc("d:0003", [{"kind": "heading", "text": "Other", "level": 2}])
    authored = {"d:0001": a, "d:0002": b, "d:0003": c}
    genre_of = {
        "d:0001": "kickoff_memo",
        "d:0002": "kickoff_memo",
        "d:0003": "status_report",
    }

    pairs, considered = structure.compute_pairs(authored, genre_of)
    assert considered == 1
    assert [(p.doc_a, p.doc_b) for p in pairs] == [("d:0001", "d:0002")]
    assert pairs[0].genre == "kickoff_memo"


def test_compute_pairs_truncates_visibly():
    """The cap is a reading list, not a census: what is dropped is counted."""
    authored, genre_of = {}, {}
    for i in range(1, 8):
        doc_id = f"d:{i:04d}"
        authored[doc_id] = _memo(
            doc_id, LATINATE, MOVES
        )
        genre_of[doc_id] = "kickoff_memo"

    pairs, considered = structure.compute_pairs(authored, genre_of, top_n=3)
    assert considered == 21  # 7 choose 2, every pair scored
    assert len(pairs) == 3


def test_pair_order_is_deterministic_across_runs():
    """Byte stability of the artifact reduces to a total order on the pair
    list. Ties are broken by doc id, so no two runs can disagree."""
    authored, genre_of = {}, {}
    for i in range(1, 6):
        doc_id = f"d:{i:04d}"
        authored[doc_id] = _memo(
            doc_id,
            LATINATE if i % 2 else SAXON,
            MOVES,
        )
        genre_of[doc_id] = "kickoff_memo"

    first, _ = structure.compute_pairs(authored, genre_of)
    second, _ = structure.compute_pairs(dict(reversed(authored.items())), genre_of)
    assert [p.model_dump() for p in first] == [p.model_dump() for p in second]
