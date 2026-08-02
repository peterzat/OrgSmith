"""Unit tier: EVAL-01, the tamper check on the answer key (M17).

`evals/` was the one derived artifact nothing checked. A hand-edited
question, a deleted suite, or a smuggled extra file all validated clean.
"""

import shutil

import pytest

from orgsmith.acl import run_acl
from orgsmith.evals.emit import run_emit_evals
from orgsmith.paths import OrgPaths
from orgsmith.validate import collect
from orgsmith.validate.rules import RULES, Context

from conftest import build_knobbed_stages, build_rendered

pytestmark = pytest.mark.unit

EVAL_01 = [r for r in RULES if r.id == "EVAL-01"]


@pytest.fixture(scope="module")
def org(tmp_path_factory):
    paths = build_rendered(
        build_knobbed_stages(tmp_path_factory.mktemp("eval01-org"))
    )
    assert run_acl(paths) == 0
    assert run_emit_evals(paths) == 0
    return paths


@pytest.fixture()
def org_copy(org, tmp_path):
    shutil.copytree(org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=org.slug)


def _findings(paths):
    findings, skipped = collect(Context.load(paths), EVAL_01)
    return findings, skipped


def test_freshly_emitted_evals_pass(org):
    findings, skipped = _findings(org)
    assert not skipped, skipped
    assert not findings, findings


def test_one_mutated_byte_is_a_finding(org_copy):
    target = org_copy.evals_dir / "retrieval.jsonl"
    text = target.read_text()
    target.write_text(text.replace("Which documents", "which documents", 1))
    findings, _ = _findings(org_copy)
    assert [f["target"] for f in findings] == ["evals/retrieval.jsonl"]
    assert "does not re-derive" in findings[0]["message"]


def test_a_hand_added_expected_doc_is_a_finding(org_copy):
    """The failure the rule exists for: gold quietly widened by hand."""
    import json

    target = org_copy.evals_dir / "retrieval.jsonl"
    lines = [line for line in target.read_text().splitlines() if line.strip()]
    first = json.loads(lines[0])
    first["expected_docs"] = sorted(first["expected_docs"] + ["TOC.md"])
    lines[0] = json.dumps(first, ensure_ascii=False)
    target.write_text("\n".join(lines) + "\n")
    findings, _ = _findings(org_copy)
    assert any(f["target"] == "evals/retrieval.jsonl" for f in findings)


def test_a_deleted_suite_file_is_a_finding(org_copy):
    (org_copy.evals_dir / "clusters.json").unlink()
    findings, _ = _findings(org_copy)
    assert [f["target"] for f in findings] == ["evals/clusters.json"]
    assert "missing" in findings[0]["message"]


def test_an_extra_file_is_a_finding(org_copy):
    (org_copy.evals_dir / "extra.jsonl").write_text("{}\n")
    findings, _ = _findings(org_copy)
    assert [f["target"] for f in findings] == ["evals/extra.jsonl"]
    assert "unexpected" in findings[0]["message"]


def test_an_org_that_never_emitted_evals_skips_visibly(org_copy):
    shutil.rmtree(org_copy.evals_dir)
    findings, skipped = _findings(org_copy)
    assert not findings
    assert skipped == [
        {"rule": "EVAL-01", "reason": "evals/ was never emitted for this org"}
    ]
