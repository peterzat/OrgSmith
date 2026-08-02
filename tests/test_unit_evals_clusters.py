"""Unit tier: byte-copy equivalence clusters (M17).

The external critique of 2026-07-28 found the answer key punishing a system
for returning a document that literally contains the answer: a derived
exact duplicate is byte-identical to its source, and returning it scored as
an error. Clusters fix that without relaxing near-duplicate discrimination,
which stays a capability under test.

These tests run against a synthetic noise org, so they keep proving the
rule after any committed fixture is regenerated.
"""

import json
import shutil

import pytest

from orgsmith.artifacts import load_manifest
from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.evals.emit import build_clusters, run_emit_evals
from orgsmith.evals.score import load_canonical_map, score_retrieval
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.schemas import RetrievalAnswers

from conftest import base_recipe_text, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def noise_org(tmp_path_factory):
    """dev-mini with duplicates and drafts, rendered and emitted."""
    root = tmp_path_factory.mktemp("cluster-org")
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True)
    text = base_recipe_text()
    anchor = "  format_mix: {docx: 15, pdf: 3, xlsx: 5}\n"
    text = text.replace(
        anchor, anchor + "  noise:\n    duplicates: 2\n    drafts: 3\n"
    )
    dest.joinpath("ORG-CHARTER.md").write_text(text)
    p = OrgPaths(root=root, slug="dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(p) == 0
    run_enrichment(p)
    run_authoring(p)
    assert run_render(p) == 0
    assert run_emit_evals(p) == 0
    return p


def _questions(paths):
    return [
        json.loads(line)
        for line in (paths.evals_dir / "retrieval.jsonl").read_text().splitlines()
        if line.strip()
    ]


def _score(paths, answers) -> tuple[int, int]:
    result = score_retrieval(
        paths.evals_dir,
        RetrievalAnswers.model_validate({"suite": "retrieval", "answers": answers}),
    )
    return result.correct, result.total


def _ground_truth(paths):
    return [
        {"id": q["id"], "docs": list(q["expected_docs"])}
        for q in _questions(paths)
    ]


def test_exact_duplicates_are_members_and_drafts_are_not(noise_org):
    clusters = json.loads((noise_org.evals_dir / "clusters.json").read_text())
    kinds = {
        m["noise_kind"]
        for c in clusters["clusters"]
        for m in c["members"]
        if m["basis"] == "byte_copy"
    }
    assert "exact_duplicate" in kinds, "no duplicate became a cluster member"
    assert "draft" not in kinds and "version" not in kinds, (
        "a near-duplicate must never be acceptable: telling a draft from "
        "its final is a capability under test"
    )
    by_path = {e.path: e for e in load_manifest(noise_org)}
    drafts = {
        e.path for e in by_path.values() if e.noise_kind in ("draft", "version")
    }
    assert drafts
    members = {
        m["path"] for c in clusters["clusters"] for m in c["members"]
    }
    assert not (drafts & members)


def test_returning_a_duplicate_in_place_of_its_source_is_correct(noise_org):
    """The critique's Coleman probe, on an org that cannot be regenerated
    out from under it: swap every expected document for its byte-identical
    copy where one exists, and the score is unchanged."""
    canonical = load_canonical_map(noise_org.evals_dir)
    assert canonical, "org emitted no clusters"
    reverse: dict[str, str] = {}
    for member, source in canonical.items():
        reverse.setdefault(source, member)

    swapped = [
        {"id": a["id"], "docs": [reverse.get(d, d) for d in a["docs"]]}
        for a in _ground_truth(noise_org)
    ]
    assert swapped != _ground_truth(noise_org), "no answer held a clustered doc"
    correct, total = _score(noise_org, swapped)
    assert total and correct == total


def test_returning_a_duplicate_beside_its_source_is_correct(noise_org):
    canonical = load_canonical_map(noise_org.evals_dir)
    reverse: dict[str, str] = {}
    for member, source in canonical.items():
        reverse.setdefault(source, member)
    def widen(docs):
        out = []
        for doc in docs:
            out.append(doc)
            if doc in reverse:
                out.append(reverse[doc])
        return out

    both = [
        {"id": a["id"], "docs": widen(a["docs"])}
        for a in _ground_truth(noise_org)
    ]
    assert any(len(a["docs"]) > 1 for a in both)
    correct, total = _score(noise_org, both)
    assert total and correct == total


def test_a_draft_is_still_an_error(noise_org):
    """Near-duplicate discrimination survives: substituting a draft for its
    final fails, exactly as it did before clusters existed."""
    by_id = {e.doc_id: e for e in load_manifest(noise_org)}
    drafts = [e for e in by_id.values() if e.noise_kind == "draft"]
    assert drafts
    swap = {
        by_id[d.noise_of].path: d.path for d in drafts if d.noise_of in by_id
    }
    answers = [
        {"id": a["id"], "docs": [swap.get(d, d) for d in a["docs"]]}
        for a in _ground_truth(noise_org)
    ]
    touched = [a for a in answers if a not in _ground_truth(noise_org)]
    assert touched, "no question expected a draft's source"
    correct, total = _score(noise_org, answers)
    assert correct < total


def test_membership_is_decided_by_the_hash_not_the_label(noise_org, tmp_path):
    """A doc labeled `exact_duplicate` whose rendered bytes differ from its
    source is not a member. The label picks candidates; the hash decides."""
    shutil.copytree(noise_org.root / "companies", tmp_path / "companies")
    paths = OrgPaths(root=tmp_path, slug=noise_org.slug)
    manifest = load_manifest(paths)
    dupe = next(e for e in manifest if e.noise_kind == "exact_duplicate")
    before = build_clusters(paths, manifest)
    assert any(
        m.path == dupe.path for c in before.clusters for m in c.members
    )

    target = paths.share_dir / dupe.path
    target.write_bytes(target.read_bytes() + b"\n")
    after = build_clusters(paths, manifest)
    assert not any(
        m.path == dupe.path for c in after.clusters for m in c.members
    )


def test_a_bare_evals_dir_without_clusters_scores_identically(
    noise_org, tmp_path
):
    """Back-compat: a v2.1.1-shape evals directory (no clusters.json) scores
    exactly as it did, because canonicalization falls back to identity."""
    bare = tmp_path / "evals"
    bare.mkdir()
    for name in ("retrieval.jsonl", "extraction.jsonl"):
        shutil.copy(noise_org.evals_dir / name, bare / name)
    assert load_canonical_map(bare) == {}

    answers = RetrievalAnswers.model_validate(
        {"suite": "retrieval", "answers": _ground_truth(noise_org)}
    )
    with_clusters = score_retrieval(noise_org.evals_dir, answers)
    without = score_retrieval(bare, answers)
    assert (without.correct, without.total) == (
        with_clusters.correct,
        with_clusters.total,
    )
