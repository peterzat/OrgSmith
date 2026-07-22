"""Unit tier: the cross-document voice instrument and its brief mitigation
(M12, cross-document-voice). The instrument measures pre-registered patterns as
a RANGE, not a single count; the mitigation is a default-off brief nudge. Both
are unmeasurable to one number and neither gates."""

import pytest

from orgsmith.artifacts import load_work_order
from orgsmith.authoring.contexts import _author_voice, run_next_batch
from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.paths import OrgPaths
from orgsmith.review.voice import VOICE_PATTERNS, measure_voice
from orgsmith.schemas import Block, DocIR
from orgsmith.state import load_state

from conftest import REPO, base_recipe_text, run_enrichment

pytestmark = pytest.mark.unit


def _doc(doc_id, *texts):
    return DocIR(
        doc_id=doc_id,
        blocks=[Block(kind="paragraph", text=t) for t in texts],
    )


def test_measure_voice_prints_patterns_and_counts_a_range():
    """Every pattern is reported with the exact regex it counted, and the same
    antithesis sentence lands under several readings, so strict counts are at
    or below the plain 'rather than' count -- the range the finding is about."""
    docs = {
        "d:0001": _doc(
            "d:0001",
            "I would rather act now than wait until later.",
            "Two asks. First, review. Second, approve.",
        ),
        "d:0002": _doc(
            "d:0002",
            "We would rather invest early than delay.",
            "Workstreams for the quarter. Next Steps follow.",
        ),
        "d:0003": _doc("d:0003", "She prefers tea rather than coffee."),
    }
    tics, total = measure_voice(docs)
    assert total == 3
    assert len(tics) == len(VOICE_PATTERNS)
    for t in tics:
        assert t.pattern  # the regex is printed, per the finding's own lesson
    counts = {t.name: t.occurrences for t in tics}
    # The finding's whole thesis: the antithesis readings DISAGREE, so no
    # single number is the count. Plain "rather than" only matches the one
    # adjacent occurrence; the loose reading catches the two spaced ones.
    assert counts["antithesis-plain-rather-than"] == 1
    assert counts["antithesis-loose-rather-word-than"] == 2
    assert counts["antithesis-strict-now-than-later"] == 1
    antithesis = {
        v for k, v in counts.items() if k.startswith("antithesis")
    }
    assert len(antithesis) > 1, "the readings must disagree; that is the point"
    # structural tics are unambiguous and reproducible
    assert counts["two-asks-opener"] == 1
    assert counts["workstreams-heading"] == 1
    assert counts["next-steps-heading"] == 1


def test_measure_voice_is_deterministic():
    docs = {"d:0001": _doc("d:0001", "rather now than later")}
    assert [t.occurrences for t in measure_voice(docs)[0]] == [
        t.occurrences for t in measure_voice(docs)[0]
    ]


def test_author_voice_is_deterministic_and_varies_by_person():
    a1 = _author_voice(1234, "p:alice")
    a2 = _author_voice(1234, "p:alice")
    b = _author_voice(1234, "p:bob")
    assert a1 == a2  # same seed + person -> same register
    # different people can (and across a roster do) draw different registers
    assert isinstance(b, str) and b


def _build(root, voice_on: bool) -> OrgPaths:
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    text = base_recipe_text()
    if voice_on:
        anchor = "  format_mix: {docx: 15, pdf: 3, xlsx: 5}\n"
        text = text.replace(anchor, anchor + "  voice_diversify: true\n")
    dest.joinpath("ORG-CHARTER.md").write_text(text)
    p = OrgPaths(root=root, slug="dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(p) == 0
    run_enrichment(p)
    assert run_next_batch(p) == 0
    return p


def _first_guidance(p) -> str:
    ref = next(iter(load_state(p).author_batches.values()))
    wo = load_work_order(p.workorders_dir / ref.workorder)
    return " ".join(b.guidance for b in wo.docs)


def test_mitigation_adds_a_register_and_bans_constructions_when_on(tmp_path):
    guidance = _first_guidance(_build(tmp_path, voice_on=True))
    assert "Two asks" in guidance  # names the banned construction
    assert "register" in guidance  # a per-author voice register was injected


def test_mitigation_is_absent_when_off(tmp_path):
    guidance = _first_guidance(_build(tmp_path, voice_on=False))
    assert "Two asks" not in guidance
    assert "register" not in guidance
