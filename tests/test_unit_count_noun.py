"""Unit tier: a count placeholder must not be followed by its own noun
(REND-01, M17d).

A scope count renders with its noun ("15 acquisition targets"), and M17c's
treatment arm shipped eleven placements where the author wrote the noun again,
so the rendered corpus read "15 acquisition targets targets". The cases below
are those eleven, verbatim, plus the correct placements beside them.
"""

from __future__ import annotations

import pytest

from orgsmith.authoring.ingest import check_doubled_count_noun
from orgsmith.schemas import Block, DocIR, Fact

pytestmark = pytest.mark.unit

FACTS = {
    f.id: f
    for f in (
        Fact(id="f:E-1.scope", kind="count", value=15, rendered="15 acquisition targets"),
        Fact(id="f:E-1.comparators", kind="count", value=40, rendered="40 comparable transactions"),
        Fact(id="f:E-1.pipeline-targets-screened", kind="count", value=64, rendered="64 targets screened"),
        Fact(id="f:E-1.pipeline-ndas-executed", kind="count", value=24, rendered="24 NDAs executed"),
        Fact(id="f:E-1.client", kind="text", value="Morse PLC", rendered="Morse PLC"),
    )
}
SCOPE, COMP, SCREENED, NDAS = (
    "{{fact:f:E-1.scope}}",
    "{{fact:f:E-1.comparators}}",
    "{{fact:f:E-1.pipeline-targets-screened}}",
    "{{fact:f:E-1.pipeline-ndas-executed}}",
)


def _doc(text: str) -> DocIR:
    return DocIR(
        doc_id="d:0001",
        blocks=[Block(kind="heading", text="Status"), Block(kind="paragraph", text=text)],
    )


# The eleven REND-01 placements from M17c's treatment arm (docs/M17C-RUN-LOG.md),
# each reduced to the placeholder and the words the author wrote after it.
M17C_OCCURRENCES = [
    f"we assembled {COMP} comparable transactions, so that your board",  # d0012
    f"scoped that program at {SCOPE} candidate targets, which we will build",  # d0020
    f"an acquisition program scoped at {SCOPE} targets, which is research",  # d0021
    f"The program remains scoped at {SCOPE} acquisition targets, unchanged",  # d0022
    f"against {COMP} comparable transactions close enough in size",  # d0022
    f"remains scoped at {SCOPE} targets, which is the number",  # d0024
    f"against {COMP} transactions close enough in size and structure",  # d0024
    f"the {SCOPE} acquisition targets the engagement letter named",  # d0038
    f"priced against {COMP} comparable transactions in the sector",  # d0038
    f"the evidence is {COMP} comparable transactions, which is enough",  # d0045
    f"the funnel stood at {SCREENED} candidates screened, and the",  # d0046
]

# Correct placements from the same arm: the placeholder followed by
# punctuation, a clause word, or prose that does not repeat its noun.
CORRECT = [
    f"the universe of {SCOPE}, together with the screening criteria",
    f"{SCREENED} against the criteria Laura Gonzalez confirmed",
    f"{SCREENED}, then the contact wave",
    f"{SCREENED} and {NDAS} to date",
    f"{NDAS} of those approached",
    f"{SCOPE} for {{{{fact:f:E-1.client}}}}, each to be found",
    f"{SCOPE}? And who at the Company hears what",
    f"{COMP}. The multiples cluster",
    f"{SCREENED} to date, each one scored",
    f"{SCREENED} were approached in the first wave",
    f"{SCOPE}\nacquisition targets",  # a line break ends the clause
]


@pytest.mark.parametrize("text", M17C_OCCURRENCES)
def test_every_m17c_occurrence_is_rejected(text):
    problems = check_doubled_count_noun(_doc(text), FACTS)
    assert len(problems) == 1, problems
    assert "repeats its noun" in problems[0]


@pytest.mark.parametrize("text", CORRECT)
def test_correct_placements_pass(text):
    assert check_doubled_count_noun(_doc(text), FACTS) == []


def test_only_count_facts_are_checked():
    # A text fact followed by a word of its own surface is not this check's
    # business: "Morse PLC PLC" would be a different defect, and no committed
    # ledger carries count facts, so the check is inert on the frozen fleet.
    doc = _doc("prepared for {{fact:f:E-1.client}} Morse, as agreed")
    assert check_doubled_count_noun(doc, FACTS) == []


def test_the_problem_names_the_fact_and_the_words():
    (problem,) = check_doubled_count_noun(_doc(f"scoped at {SCOPE} targets."), FACTS)
    assert "f:E-1.scope" in problem and "'15 acquisition targets'" in problem
    assert "'targets'" in problem


def test_list_items_and_table_cells_are_checked():
    doc = DocIR(
        doc_id="d:0001",
        blocks=[
            Block(kind="heading", text="Pipeline"),
            Block(kind="list", items=[f"{NDAS} NDAs signed"]),
            Block(kind="table", header=["stage", "count"], rows=[["screen", f"{SCREENED} targets"]]),
        ],
    )
    assert len(check_doubled_count_noun(doc, FACTS)) == 2


def test_ingest_rejects_a_doubled_noun_end_to_end(tmp_path, capsys):
    """Wired into `author --ingest`, not just callable: a scope-on org's
    scripted deliverable ingests clean, and the same deliverable with the
    noun written after one count placeholder is rejected whole."""
    import json

    from orgsmith.artifacts import load_engagements, load_work_order
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.authoring.ingest import run_ingest
    from orgsmith.state import load_state

    from conftest import build_knobbed_stages, committed_outlines, run_enrichment, scripted_authoring

    paths = build_knobbed_stages(tmp_path)
    run_enrichment(paths)
    facts = load_engagements(paths).fact_index()
    for _ in range(40):
        assert run_next_batch(paths) == 0
        batches = load_state(paths).author_batches
        if not batches:
            pytest.skip("no batch left to inspect")  # pragma: no cover
        wo_id, ref = next(reversed(batches.items()))
        wo = load_work_order(paths.workorders_dir / ref.workorder)
        reply = scripted_authoring(wo, committed_outlines(paths))
        target = next(
            (
                (doc, block, f.id)
                for doc in reply["docs"]
                for block in doc["blocks"]
                for f in facts.values()
                if f.kind == "count" and f"{{{{fact:{f.id}}}}}" in block.get("text", "")
            ),
            None,
        )
        if target is not None:
            break
        path = paths.workorders_dir / f"reply-{wo_id.replace(':', '-')}.json"
        path.write_text(json.dumps(reply))
        assert run_ingest(paths, path) == 0
    else:  # pragma: no cover
        raise AssertionError("no scope-on batch carried a count placeholder")

    doc, block, fid = target
    noun_word = facts[fid].rendered.split()[-1]
    placeholder = f"{{{{fact:{fid}}}}}"
    block["text"] = block["text"].replace(placeholder, f"{placeholder} {noun_word}", 1)
    path = paths.workorders_dir / f"reply-{wo_id.replace(':', '-')}.json"
    path.write_text(json.dumps(reply))
    capsys.readouterr()
    assert run_ingest(paths, path) == 1
    out = capsys.readouterr().out
    assert "repeats its noun" in out and fid in out


def _all_briefs(paths):
    from orgsmith.artifacts import load_work_order
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.state import load_state

    prev = -1
    while True:
        assert run_next_batch(paths) == 0
        n = len(load_state(paths).author_batches)
        if n == prev:
            break
        prev = n
    return [
        brief
        for ref in load_state(paths).author_batches.values()
        for brief in load_work_order(paths.workorders_dir / ref.workorder).docs
    ]


def test_a_scope_on_brief_says_the_count_renders_its_noun(tmp_path):
    from conftest import build_knobbed_stages, run_enrichment

    paths = build_knobbed_stages(tmp_path)
    run_enrichment(paths)
    briefs = _all_briefs(paths)
    hints = [f.hint for b in briefs for f in b.facts if f.hint.startswith("count of")]
    assert hints, "the knobbed org briefs no count fact"
    assert all("do not write the noun again" in h for h in hints)
    # The nesting constraint rides exactly the briefs carrying both kinds.
    for b in briefs:
        ids = [f.id for f in b.facts if f.hint.startswith("count of")]
        both = any(".pipeline-" in i for i in ids) and any(".pipeline-" not in i for i in ids)
        assert ("separate measures of this engagement" in b.guidance) == both
    assert any("separate measures of this engagement" in b.guidance for b in briefs)


def test_a_scope_off_brief_carries_neither_sentence(tmp_path):
    from conftest import build_pure_stages, run_enrichment

    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)
    for b in _all_briefs(paths):
        assert "separate measures of this engagement" not in b.guidance
        assert not any("renders as the number" in f.hint for f in b.facts)
