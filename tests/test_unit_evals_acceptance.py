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
