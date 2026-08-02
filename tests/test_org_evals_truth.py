"""Org tier: the answer key tells the truth about the rendered corpus (M17).

Fleet-wide properties, not named probes: the three orgs the M17 carve-out
regenerates would take any doc-id-anchored assertion with them. What is
anchored here is the rule (every byte-identical derived copy of a required
document is accepted; every cluster member really is byte-identical; the
visibility suite no longer decides the split curve), which survives a
regeneration.
"""

import json

import pytest

from orgsmith.artifacts import load_manifest
from orgsmith.evals.score import load_canonical_map, score_retrieval
from orgsmith.paths import OrgPaths
from orgsmith.schemas import RetrievalAnswers
from orgsmith.state import sha256_file

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


def _questions(paths):
    return [
        json.loads(line)
        for line in (paths.evals_dir / "retrieval.jsonl").read_text().splitlines()
        if line.strip()
    ]


def _clusters(paths) -> dict:
    return json.loads((paths.evals_dir / "clusters.json").read_text())


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_every_cluster_member_really_carries_the_same_bytes(slug):
    """Membership is verified, never labeled. A `byte_copy` hashes equal to
    its canonical; an `attachment` carries it as a byte-identical MIME part.
    Recomputed here from the committed share, so a hand-edited clusters.json
    cannot claim an equivalence the files do not support."""
    from orgsmith.render.eml import eml_attachment_bytes

    paths = OrgPaths(root=REPO, slug=slug)
    for cluster in _clusters(paths)["clusters"]:
        source = paths.share_dir / cluster["canonical"]
        assert source.is_file(), cluster["canonical"]
        for member in cluster["members"]:
            path = paths.share_dir / member["path"]
            assert path.is_file(), member["path"]
            if member["basis"] == "byte_copy":
                assert sha256_file(path) == sha256_file(source), member["path"]
            else:
                assert eml_attachment_bytes(path) == source.read_bytes(), (
                    member["path"]
                )


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_near_duplicates_are_never_cluster_members(slug):
    """Drafts, version-chain members, and stale templates resemble their
    source without matching it. Discriminating them is a capability under
    test, so they may never be scored as equivalent."""
    paths = OrgPaths(root=REPO, slug=slug)
    near = {
        e.path
        for e in load_manifest(paths)
        if e.noise_kind in ("draft", "version", "stale_template")
    }
    members = {
        m["path"] for c in _clusters(paths)["clusters"] for m in c["members"]
    }
    assert not (near & members)


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_a_byte_identical_copy_of_a_required_doc_is_accepted(slug):
    """The critique's central complaint, as a fleet-wide property: wherever
    a required document has a byte-identical copy in the share, returning
    the copy instead scores exactly as returning the original."""
    paths = OrgPaths(root=REPO, slug=slug)
    canonical = load_canonical_map(paths.evals_dir)
    substitute: dict[str, str] = {}
    for member, source in canonical.items():
        substitute.setdefault(source, member)

    questions = _questions(paths)
    truth = [
        {"id": q["id"], "docs": list(q["expected_docs"])} for q in questions
    ]
    swapped = [
        {"id": a["id"], "docs": [substitute.get(d, d) for d in a["docs"]]}
        for a in truth
    ]
    if swapped == truth:
        pytest.skip(f"{slug} has no clustered document in any required set")

    result = score_retrieval(
        paths.evals_dir,
        RetrievalAnswers.model_validate(
            {"suite": "retrieval", "answers": swapped}
        ),
    )
    assert result.total and result.correct == result.total, result.failures


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_splits_are_a_retrieval_device_not_a_visibility_one(slug):
    """`core` is derived from the retrieval and extraction suites only. It
    used to union the visibility gold, and because ACL-02 guarantees every
    document is readable by someone, that made `core` the entire authored
    corpus on every org in the fleet: the advertised four-point degradation
    curve was a two-point one everywhere."""
    paths = OrgPaths(root=REPO, slug=slug)
    splits = json.loads((paths.evals_dir / "splits.json").read_text())["splits"]
    core = set(splits["core"])

    answers: set[str] = set()
    for name in ("retrieval.jsonl", "extraction.jsonl"):
        for line in (paths.evals_dir / name).read_text().splitlines():
            if line.strip():
                answers.update(json.loads(line)["expected_docs"])
    derived = {
        e.path for e in load_manifest(paths) if e.authoring == "derived"
    }
    assert core == answers - derived


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_mundane_traffic_produces_a_real_distractor_gap(slug):
    """Splits only degrade if `distractors` is bigger than `core`. Before
    M17 it never was on any org, because visibility gold was unioned into
    core and ACL-02 makes every document readable by someone. An org whose
    recipe declares mundane internal mail plants documents that answer
    nothing, so its gap must now be positive.

    Keyed off the charter rather than a doc count, so it follows a recipe
    through a regeneration instead of pinning today's numbers."""
    from orgsmith.artifacts import load_charter

    paths = OrgPaths(root=REPO, slug=slug)
    mail = load_charter(paths).doc_culture.mail
    if mail is None or mail.mundane_emails == 0:
        pytest.skip(f"{slug} plans no mundane internal mail")
    splits = json.loads((paths.evals_dir / "splits.json").read_text())["splits"]
    assert len(splits["distractors"]) > len(splits["core"]), (
        f"{slug}: distractors == core, so the degradation curve is flat"
    )


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_transmittals_are_equivalents_rather_than_gold(slug):
    """A transmittal email carrying a document byte-identically is a cluster
    member, not a member of the required set. It enters gold only for facts
    it states in its own body."""
    paths = OrgPaths(root=REPO, slug=slug)
    manifest = load_manifest(paths)
    transmittals = [
        e
        for e in manifest
        if e.render_params.get("attach_path") and e.authoring != "derived"
    ]
    if not transmittals:
        pytest.skip(f"{slug} plans no transmittal mail")

    members = {
        m["path"]
        for c in _clusters(paths)["clusters"]
        for m in c["members"]
        if m["basis"] == "attachment"
    }
    assert {t.path for t in transmittals} <= members

    for entry in transmittals:
        own = set(entry.facts_refs) | {k.fact_id for k in entry.key_facts}
        for line in (paths.evals_dir / "extraction.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            question = json.loads(line)
            if entry.path in question["expected_docs"]:
                assert question["fact_id"] in own, question["id"]
