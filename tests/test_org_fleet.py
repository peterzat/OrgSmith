"""Org tier: full validation over the committed fleet in companies/.

Skips when no orgs are committed yet (fresh clones mid-milestone). Every
committed org must validate clean forever; these are the product's
fixtures.
"""

import json

import pytest

from orgsmith.paths import OrgPaths
from orgsmith.status import collect_status
from orgsmith.validate import run_validate

from conftest import REPO, flagship_params

pytestmark = pytest.mark.org


def _committed_slugs():
    companies = REPO / "companies"
    if not companies.exists():
        return []
    return sorted(
        p.name[: -len("-metadata")]
        for p in companies.iterdir()
        if p.is_dir() and p.name.endswith("-metadata")
    )


SLUGS = _committed_slugs()


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_committed_org_validates_clean(slug):
    paths = OrgPaths(root=REPO, slug=slug)
    assert run_validate(paths) == 0


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_committed_org_extraction_ground_truth_scores_100(slug):
    from orgsmith.evals.score import score_extraction
    from orgsmith.schemas import ExtractionAnswers

    paths = OrgPaths(root=REPO, slug=slug)
    suite = paths.evals_dir / "extraction.jsonl"
    if not suite.exists():
        pytest.skip("org has no committed evals")
    questions = [
        json.loads(line) for line in suite.read_text().splitlines() if line.strip()
    ]
    result = score_extraction(
        paths.evals_dir,
        ExtractionAnswers.model_validate(
            {
                "suite": "extraction",
                "answers": [
                    {
                        "id": q["id"],
                        "value": q["expected_value"],
                        "docs": q["expected_docs"],
                    }
                    for q in questions
                ],
            }
        ),
    )
    assert result.total and result.correct == result.total


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_committed_org_is_complete(slug):
    paths = OrgPaths(root=REPO, slug=slug)
    status = collect_status(paths)
    for stage in ("charter", "foundation", "fabric", "docplan",
                  "author", "render", "assemble"):
        assert status["stages"][stage] == "done", stage
    assert status["outstanding"] == {}
    assert paths.toc_md.exists()


def test_affiliation_host_exercises_affiliation_surfaces(capsys):
    """The fleet's affiliation host: AFF and NAME rules run unskipped, the
    graph carries dated works_at edges for the boundary person plus the
    multi-affiliation ambiguity tag, and the corpus is modern-format only
    (CI stays LibreOffice-free).

    Hosted by fernhollow from M6 until M11b retired it; saltmarsh is the
    replacement. The `if not exists: skip` guard fernhollow carried is gone
    rather than repointed. It was there to let the test land before the
    fixture did, but once fernhollow retired it turned into a silent pass:
    the org tier reported "fernhollow-partners not committed yet" and moved
    on, which is grandfathering by absence -- the exact thing CLAUDE.md
    forbids. A missing host is now a failure, because saltmarsh's recipe has
    the knob ON and a knob that is on with its artifact missing is tamper
    evidence, never a skip.
    """
    from orgsmith.artifacts import (
        load_charter,
        load_foundation,
        load_graph,
        load_manifest,
    )
    from orgsmith.evals.emit import build_graph_expected

    paths = OrgPaths(root=REPO, slug="saltmarsh-environmental")
    assert load_charter(paths).graph_targets.affiliations_in_docs is True, (
        "the affiliation host must ship the knob on, or this test is vacuous"
    )

    assert run_validate(
        paths, as_json=True, only=["AFF-01", "AFF-02", "NAME-01"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["rules_run"] == ["NAME-01", "AFF-01", "AFF-02"]
    assert payload["skipped"] == []

    foundation = load_foundation(paths)
    xp = next(p for p in foundation.external_people if p.affiliations)
    graph = load_graph(paths)
    works_at = [
        e for e in graph.edges if e.kind == "works_at" and e.src == xp.id
    ]
    assert len(works_at) == 2
    assert any(e.end is not None for e in works_at)
    assert any(e.start is not None and e.end is None for e in works_at)

    expected = build_graph_expected(load_charter(paths), foundation, graph)
    entity = next(e for e in expected.entities if e.id == xp.id)
    assert "ambiguity:multi-affiliation" in entity.tags

    formats = {e.format for e in load_manifest(paths)}
    assert formats <= {"docx", "pdf", "xlsx", "pptx", "eml"}
