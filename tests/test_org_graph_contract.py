"""Org tier: participation and edge dates enter the scored graph (M17).

Participant edges used to be stripped at emit because they point at
engagement ids an answer file had no way to name, so "who worked on what"
was ground truth that nothing could score. Engagements are entities now.

Fleet-wide properties rather than named probes, so the M17 regenerations
cannot retire them.
"""

import pytest

from orgsmith.artifacts import load_graph
from orgsmith.evals.score import score_graph
from orgsmith.paths import OrgPaths
from orgsmith.schemas import GraphAnswers, GraphExpected

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
        and (root / f"{p.name}-metadata" / "evals").is_dir()
    )


SLUGS = _committed_slugs()


def _expected(paths) -> GraphExpected:
    return GraphExpected.model_validate_json(
        (paths.evals_dir / "graph_expected.json").read_text()
    )


def _answers(expected: GraphExpected, dated: bool) -> GraphAnswers:
    name = {e.id: e.canonical for e in expected.entities}
    return GraphAnswers.model_validate(
        {
            "suite": "graph",
            "entities": [
                {"name": e.canonical, "kind": e.kind} for e in expected.entities
            ],
            "edges": [
                {
                    "src": name[e.src],
                    "dst": name[e.dst],
                    "kind": e.kind,
                    **(
                        {
                            "start": e.start.isoformat() if e.start else None,
                            "end": e.end.isoformat() if e.end else None,
                        }
                        if dated
                        else {}
                    ),
                }
                for e in expected.edges
            ],
        }
    )


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_every_ledger_edge_is_scorable(slug):
    """No edge kind is silently dropped from the contract: the emitted
    graph carries every edge the ledger holds, and every endpoint resolves
    to a named entity."""
    paths = OrgPaths(root=REPO, slug=slug)
    expected = _expected(paths)
    ledger = load_graph(paths)
    assert len(expected.edges) == len(ledger.edges)
    known = {e.id for e in expected.entities}
    for edge in expected.edges:
        assert edge.src in known and edge.dst in known, edge


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_participant_edges_score_end_to_end_by_naming_engagements(slug):
    paths = OrgPaths(root=REPO, slug=slug)
    expected = _expected(paths)
    participants = [e for e in expected.edges if e.kind == "participant"]
    if not participants:
        pytest.skip(f"{slug} plans no participant edges")

    result = score_graph(paths.evals_dir, _answers(expected, dated=False))
    assert result.edge_precision == 1.0 and result.edge_recall == 1.0
    assert result.edge_kinds["participant"] == {
        "expected": len(participants),
        "matched": len(participants),
        "recall": 1.0,
    }


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_engagement_canonical_names_are_unique(slug):
    """A duplicate title is disambiguated by client, so name resolution
    cannot silently collapse two engagements into one."""
    paths = OrgPaths(root=REPO, slug=slug)
    engagements = [e for e in _expected(paths).entities if e.kind == "engagement"]
    if not engagements:
        pytest.skip(f"{slug} has no engagements")
    names = [e.canonical.casefold() for e in engagements]
    assert len(set(names)) == len(names), "two engagements share a name"


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_a_dateless_answer_scores_identical_edge_precision_and_recall(slug):
    """Back-compat: dates are optional and never move the headline."""
    paths = OrgPaths(root=REPO, slug=slug)
    expected = _expected(paths)
    if not expected.edges:
        pytest.skip(f"{slug} has no edges")

    bare = score_graph(paths.evals_dir, _answers(expected, dated=False))
    dated = score_graph(paths.evals_dir, _answers(expected, dated=True))
    assert bare.edge_precision == dated.edge_precision
    assert bare.edge_recall == dated.edge_recall
    assert bare.dated_edge_credit is None, "not attempting is not a zero"
    assert dated.dated_edge_credit == 1.0
    assert dated.dated_edges_credited == dated.dated_edges_eligible > 0


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_wrong_dates_lose_credit_without_losing_the_edge(slug):
    from datetime import timedelta

    paths = OrgPaths(root=REPO, slug=slug)
    expected = _expected(paths)
    dated = [e for e in expected.edges if e.start or e.end]
    if not dated:
        pytest.skip(f"{slug} has no dated edges")

    name = {e.id: e.canonical for e in expected.entities}
    answers = GraphAnswers.model_validate(
        {
            "suite": "graph",
            "entities": [
                {"name": e.canonical, "kind": e.kind} for e in expected.entities
            ],
            "edges": [
                {
                    "src": name[e.src],
                    "dst": name[e.dst],
                    "kind": e.kind,
                    "start": (e.start + timedelta(days=1)).isoformat()
                    if e.start
                    else None,
                    "end": e.end.isoformat() if e.end else None,
                }
                for e in expected.edges
            ],
        }
    )
    result = score_graph(paths.evals_dir, answers)
    assert result.edge_precision == 1.0 and result.edge_recall == 1.0
    assert result.dated_edge_credit < 1.0
