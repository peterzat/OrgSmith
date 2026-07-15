"""Unit tier: evals ride along with the M5 formats.

Extraction questions carry difficulty tags derived from their host docs;
suites emit and score over format-heavy orgs; all four committed pre-M5
fixtures re-emit their evals byte-identically.
"""

import json
import shutil

import pytest

from orgsmith.acl import run_acl
from orgsmith.evals import run_emit_evals
from orgsmith.evals.score import (
    score_extraction,
    score_retrieval,
    score_visibility,
)
from orgsmith.paths import OrgPaths
from orgsmith.schemas import (
    ExtractionAnswers,
    RetrievalAnswers,
    VisibilityAnswers,
)

from conftest import REPO, build_culture_stages

pytestmark = pytest.mark.unit

FORMAT_LINES = (
    "  scanned_ratio: 0.67\n"
    "  ocr_layer_rate: 0.5\n"
    "  legacy_ratio: 0.5\n"
)


@pytest.fixture(scope="module")
def format_org(tmp_path_factory):
    paths = build_culture_stages(
        tmp_path_factory.mktemp("evals-fmt"), FORMAT_LINES
    )
    assert run_acl(paths) == 0
    assert run_emit_evals(paths) == 0
    return paths


def _jsonl(paths, name):
    lines = (paths.evals_dir / name).read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def test_extraction_questions_carry_difficulty_tags(format_org):
    from orgsmith.artifacts import load_manifest
    from orgsmith.schemas import BASE_FORMAT

    questions = _jsonl(format_org, "extraction.jsonl")
    by_path = {e.path: e for e in load_manifest(format_org)}
    seen = set()
    for q in questions:
        hosts = [by_path[p] for p in q["expected_docs"]]
        want = set()
        if any(
            h.render_params.get("ocr_layer") == 1
            for h in hosts
            if h.render_params.get("scan") == 1
        ):
            want.add("scan:ocr")
        if any(
            not h.render_params.get("ocr_layer")
            for h in hosts
            if h.render_params.get("scan") == 1
        ):
            want.add("scan:image-only")
        if any(h.format in BASE_FORMAT for h in hosts):
            want.add("format:legacy")
        got = {
            t for t in q["tags"]
            if t in ("scan:ocr", "scan:image-only", "format:legacy")
        }
        assert got == want, q["id"]
        seen |= got
    # The recipe puts all three properties in play.
    assert seen == {"scan:ocr", "scan:image-only", "format:legacy"}


def test_readme_documents_tags_only_when_present(format_org):
    readme = (format_org.evals_dir / "README.md").read_text()
    assert "Difficulty tags" in readme
    committed = (
        REPO / "companies" / "dev-mini-metadata" / "evals" / "README.md"
    ).read_text()
    assert "Difficulty tags" not in committed


def test_ground_truth_scores_100_over_format_org(format_org):
    retrieval = _jsonl(format_org, "retrieval.jsonl")
    result = score_retrieval(
        format_org.evals_dir,
        RetrievalAnswers.model_validate(
            {
                "suite": "retrieval",
                "answers": [
                    {"id": q["id"], "docs": q["expected_docs"]}
                    for q in retrieval
                ],
            }
        ),
    )
    assert result.total and result.correct == result.total

    extraction = _jsonl(format_org, "extraction.jsonl")
    result = score_extraction(
        format_org.evals_dir,
        ExtractionAnswers.model_validate(
            {
                "suite": "extraction",
                "answers": [
                    {
                        "id": q["id"],
                        "value": q["expected_value"],
                        "docs": q["expected_docs"],
                    }
                    for q in extraction
                ],
            }
        ),
    )
    assert result.total and result.correct == result.total

    visibility = _jsonl(format_org, "visibility.jsonl")
    result = score_visibility(
        format_org.evals_dir,
        VisibilityAnswers.model_validate(
            {
                "suite": "visibility",
                "answers": [
                    {"id": q["id"], "docs": q["expected_docs"]}
                    for q in visibility
                ],
            }
        ),
    )
    assert result.total and result.correct == result.total


@pytest.mark.parametrize(
    "slug",
    [
        "dev-mini",
        "torchlake-engineering",
        "quillbrook-appraisal",
        "bramblewood-legal",
    ],
)
def test_committed_fixture_evals_reemit_byte_identically(slug, tmp_path):
    src = REPO / "companies" / f"{slug}-metadata"
    dst = tmp_path / "companies" / f"{slug}-metadata"
    shutil.copytree(src, dst)
    paths = OrgPaths(root=tmp_path, slug=slug)
    assert run_emit_evals(paths) == 0
    committed = sorted(p.name for p in (src / "evals").iterdir())
    emitted = sorted(p.name for p in paths.evals_dir.iterdir())
    assert emitted == committed
    for name in committed:
        assert (paths.evals_dir / name).read_bytes() == (
            src / "evals" / name
        ).read_bytes(), f"{slug}: {name}"
