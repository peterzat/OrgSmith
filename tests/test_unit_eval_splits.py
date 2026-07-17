"""Unit tier: nested eval splits (M12, external-validity-program). emit-evals
derives core/distractors/noise/full corpora into splits.json; ground truth
scores 100% on every split by construction. Splits are derived, never stored."""

import json

import pytest

from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.evals.emit import run_emit_evals
from orgsmith.evals.score import run_score
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render

from conftest import REPO, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def evals_org(tmp_path_factory):
    """A dev-mini org with noise on, taken through emit-evals once."""
    root = tmp_path_factory.mktemp("splits-org")
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True)
    text = (REPO / "recipes" / "dev-mini" / "ORG-CHARTER.md").read_text()
    anchor = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    text = text.replace(anchor, anchor + "  noise:\n    duplicates: 2\n    drafts: 3\n")
    dest.joinpath("ORG-CHARTER.md").write_text(text)
    p = OrgPaths(root=root, slug="dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(p) == 0
    run_enrichment(p)
    run_authoring(p)
    assert run_render(p) == 0
    assert run_emit_evals(p) == 0
    return p


def _splits(p) -> dict:
    return json.loads((p.evals_dir / "splits.json").read_text())["splits"]


def test_splits_are_nested_and_distinct(evals_org):
    s = _splits(evals_org)
    core = set(s["core"])
    distractors = set(s["distractors"])
    noise = set(s["noise"])
    full = set(s["full"])
    assert core <= distractors <= full
    assert core <= noise <= full
    # noise always grows core: derived docs are never answers. (dev-mini is
    # small enough that every authored doc answers some question, so it may
    # have no distractors; a larger org does.)
    assert core < noise
    # noise and distractors differ: noise carries derived docs, distractors
    # carries only authored ones.
    assert noise != distractors
    assert full == distractors | noise


def test_noise_split_holds_the_derived_docs_and_core_does_not(evals_org):
    from orgsmith.artifacts import load_manifest

    derived = {
        e.path for e in load_manifest(evals_org) if e.authoring == "derived"
    }
    assert derived
    s = _splits(evals_org)
    assert derived <= set(s["noise"])
    assert derived <= set(s["full"])
    assert not (derived & set(s["core"]))
    assert not (derived & set(s["distractors"]))


def _ground_truth_answers(evals_org, tmp_path):
    """Perfect retrieval answers straight from the suite's expected sets."""
    lines = (evals_org.evals_dir / "retrieval.jsonl").read_text().splitlines()
    answers = [
        {"id": json.loads(ln)["id"], "docs": json.loads(ln)["expected_docs"]}
        for ln in lines
        if ln.strip()
    ]
    path = tmp_path / "gt.json"
    path.write_text(json.dumps({"suite": "retrieval", "answers": answers}))
    return path


@pytest.mark.parametrize("split", ["core", "distractors", "noise", "full"])
def test_ground_truth_scores_100_on_every_split(evals_org, tmp_path, split, capsys):
    gt = _ground_truth_answers(evals_org, tmp_path)
    assert run_score(
        evals_org.evals_dir, "retrieval", gt, as_json=True, split=split
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["score"] == 1.0
    assert payload["total"] > 0


def test_unknown_split_and_graph_split_are_rejected(evals_org, tmp_path):
    gt = _ground_truth_answers(evals_org, tmp_path)
    with pytest.raises(SystemExit, match="unknown split"):
        run_score(evals_org.evals_dir, "retrieval", gt, split="bogus")
    # graph has no document corpus
    graph_ans = tmp_path / "g.json"
    graph_ans.write_text(json.dumps({"suite": "graph", "entities": [], "edges": []}))
    with pytest.raises(SystemExit, match="does not apply to the graph"):
        run_score(evals_org.evals_dir, "graph", graph_ans, split="full")
