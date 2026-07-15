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

from conftest import REPO

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
@pytest.mark.parametrize("slug", SLUGS or ["none"])
def test_committed_org_validates_clean(slug):
    paths = OrgPaths(root=REPO, slug=slug)
    assert run_validate(paths) == 0


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", SLUGS or ["none"])
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
@pytest.mark.parametrize("slug", SLUGS or ["none"])
def test_committed_org_is_complete(slug):
    paths = OrgPaths(root=REPO, slug=slug)
    status = collect_status(paths)
    for stage in ("charter", "foundation", "fabric", "docplan",
                  "author", "render", "assemble"):
        assert status["stages"][stage] == "done", stage
    assert status["outstanding"] == {}
    assert paths.toc_md.exists()
