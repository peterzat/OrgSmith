"""Unit tier: the rendered-truth scan's semantics (M17).

Fixture-independent proofs of the two rules that decide what a scan sees:
word-boundary matching, and masking other entities' planned surfaces before
an alias scan so a short nickname is not stolen from a longer planned name.
"""

import pytest

from orgsmith.evals.emit import _mask
from orgsmith.schemas import surface_in_text

pytestmark = pytest.mark.unit


def test_mask_removes_only_standalone_surfaces():
    text = "Jim Halpert met James Grant. Halperton is a place."
    masked = _mask(text, {"Jim Halpert"})
    assert "Jim" not in masked
    assert "James Grant" in masked
    assert "Halperton" in masked, "masking must not cut inside a longer word"


def test_mask_prefers_the_longest_surface():
    """A short surface that is a prefix of a long one must not shred the
    long one first: masking runs longest-first."""
    masked = _mask("Ann Marie Cole spoke.", {"Ann", "Ann Marie Cole"})
    assert "Cole" not in masked


def test_alias_inside_a_planned_name_is_not_an_unplanned_sighting():
    """The false positive the mask exists to prevent: `Jim` registered to
    one person, standing inside another person's planned `Jim Halpert`."""
    text = "Jim Halpert chaired the review."
    assert surface_in_text("Jim", text), "unmasked, the naive scan hits"
    assert not surface_in_text("Jim", _mask(text, {"Jim Halpert"}))


def test_alias_standing_alone_survives_masking():
    """And the true positive it must not suppress: the same token used on
    its own, which is exactly the exemplar's published `Jim` residual."""
    text = "James Weiss, whom everyone here calls Jim, keeps the office."
    masked = _mask(text, {"James Weiss"})
    assert surface_in_text("Jim", masked)


def test_surface_matching_is_word_bounded():
    assert surface_in_text("Jen", "Jen filed it")
    assert surface_in_text("Jen", "we asked Jen, then left")
    assert surface_in_text("Jen", "Jen's report")
    assert not surface_in_text("Jen", "Jennifer filed it")


def test_a_synthetic_value_collision_is_recorded_and_never_promoted():
    """The recording path, proven on a collision built by hand rather than
    on whichever ones a committed fixture happens to hold.

    Two engagements priced identically is the case that matters: the second
    engagement's paperwork carries the first's expected surface, so an
    extractor that returns it has found the right string in the wrong place.
    Diagnostics records it; gold never gains it."""
    from orgsmith.evals.emit import build_diagnostics
    from orgsmith.schemas import EvalClusters, ExtractionQuestion

    class Entry:
        def __init__(self, path, engagement):
            self.path = path
            self.doc_id = path
            self.engagement = engagement
            self.authoring = "batchable"
            self.noise_of = None
            self.noise_kind = None

    class Paths:
        slug = "synthetic"

    class Foundation:
        people = []
        external_people = []

    manifest = [
        Entry("Engagements/A/letter.pdf", "E-2021-001"),
        Entry("Engagements/A/status.docx", "E-2021-001"),
        Entry("Engagements/B/letter.pdf", "E-2022-001"),
    ]
    question = ExtractionQuestion(
        id="xq:0001",
        fact_id="f:E-2021-001.fee",
        question="What is the fee?",
        expected_value="$105,000",
        expected_docs=["Engagements/A/letter.pdf"],
    )
    texts = {
        # the planted host
        "Engagements/A/letter.pdf": "The fixed fee is $105,000 for the work.",
        # the same engagement restating its own value: ordinary repetition
        "Engagements/A/status.docx": "Against the $105,000 fee, we have billed half.",
        # another engagement that happens to be priced the same: a collision
        "Engagements/B/letter.pdf": "Our fee for this engagement is $105,000.",
    }

    diagnostics = build_diagnostics(
        Paths(),
        manifest,
        Foundation(),
        None,
        [],
        [question],
        EvalClusters(slug="synthetic", policy_version="1.0", clusters=[]),
        texts,
    )
    (collision,) = diagnostics.value_collisions
    assert collision.question == "xq:0001"
    assert collision.fact_id == "f:E-2021-001.fee"
    assert collision.value == "$105,000"
    assert collision.paths == ["Engagements/B/letter.pdf"], (
        "the fact's own engagement restating its own value is repetition, "
        "not a collision"
    )
    # And the recording never widens gold.
    assert question.expected_docs == ["Engagements/A/letter.pdf"]


def test_a_derived_near_duplicate_hit_is_lineage_explained_not_flagged():
    """A draft holds its source's fee because it was copied from it. That is
    lineage, not a new disagreement, so it is counted rather than listed."""
    from orgsmith.evals.emit import build_diagnostics
    from orgsmith.schemas import EvalClusters, ExtractionQuestion

    class Entry:
        def __init__(self, path, engagement, authoring="batchable", of=None):
            self.path = path
            self.doc_id = path
            self.engagement = engagement
            self.authoring = authoring
            self.noise_of = of
            self.noise_kind = "draft" if of else None

    class Paths:
        slug = "synthetic"

    class Foundation:
        people = []
        external_people = []

    manifest = [
        Entry("Engagements/A/letter.pdf", "E-2021-001"),
        Entry(
            "Engagements/A/letter DRAFT.pdf",
            None,
            authoring="derived",
            of="Engagements/A/letter.pdf",
        ),
    ]
    question = ExtractionQuestion(
        id="xq:0001",
        fact_id="f:E-2021-001.fee",
        question="What is the fee?",
        expected_value="$105,000",
        expected_docs=["Engagements/A/letter.pdf"],
    )
    texts = {
        "Engagements/A/letter.pdf": "The fixed fee is $105,000.",
        "Engagements/A/letter DRAFT.pdf": "The fixed fee is $105,000.",
    }
    diagnostics = build_diagnostics(
        Paths(),
        manifest,
        Foundation(),
        None,
        [],
        [question],
        EvalClusters(slug="synthetic", policy_version="1.0", clusters=[]),
        texts,
    )
    assert diagnostics.value_collisions == []
    assert diagnostics.lineage_explained_value_hits == 1
