"""Org tier: rendered-truth acceptance and the diagnostics record (M17).

The critique's second finding: mention gold was planned-only, so a system
returning a document that visibly names the person was scored wrong. These
are fleet-wide properties of the committed corpus, keyed off scans rather
than doc ids, so the M17 regenerations cannot silently retire them.
"""

import json

import pytest

from orgsmith.artifacts import load_manifest
from orgsmith.doctext import DocText
from orgsmith.evals.emit import LABEL_POLICY_VERSION
from orgsmith.evals.score import score_retrieval
from orgsmith.paths import OrgPaths
from orgsmith.schemas import RetrievalAnswers, surface_in_text

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


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_every_acceptable_document_really_carries_the_surface(slug):
    """An acceptable document is not a courtesy. Its rendered text has to
    contain the questioned surface as a standalone token run, recomputed
    here from the committed share."""
    from orgsmith.artifacts import load_engagements, load_foundation

    paths = OrgPaths(root=REPO, slug=slug)
    manifest = load_manifest(paths)
    by_path = {e.path: e for e in manifest}
    reader = DocText(paths, load_engagements(paths), load_foundation(paths))

    checked = 0
    for question in _questions(paths):
        if not question["acceptable_docs"]:
            continue
        surface = _surface_of(question)
        for path in question["acceptable_docs"]:
            text = reader.text(by_path[path])
            assert surface_in_text(surface, text), (
                f"{slug} {question['id']}: {path} does not contain {surface!r}"
            )
            checked += 1
    if not checked:
        pytest.skip(f"{slug} has no acceptable documents")


def _surface_of(question: dict) -> str:
    """The surface a mention or alias question scans for, read back off the
    question text the same way a consumer would."""
    if "“" in question["question"]:
        return question["question"].split("“")[1].rstrip("”?")
    prefix = "Which documents mention "
    assert question["question"].startswith(prefix), question["question"]
    return question["question"][len(prefix) :].rstrip("?")


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_acceptable_documents_are_never_required_or_derived(slug):
    """Acceptance relaxes scoring; it must never quietly extend gold, and
    it must never launder a near-duplicate into an answer."""
    paths = OrgPaths(root=REPO, slug=slug)
    derived = {
        e.path for e in load_manifest(paths) if e.authoring == "derived"
    }
    for question in _questions(paths):
        acceptable = set(question["acceptable_docs"])
        assert not (acceptable & set(question["expected_docs"])), question["id"]
        assert not (acceptable & derived), question["id"]


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_returning_the_full_rendered_truth_scores_correct(slug):
    """The Fuentes probe as a property: answer every question with its
    required set plus everything the scan found, and score 100%."""
    paths = OrgPaths(root=REPO, slug=slug)
    questions = _questions(paths)
    if not any(q["acceptable_docs"] for q in questions):
        pytest.skip(f"{slug} has no acceptable documents")
    result = score_retrieval(
        paths.evals_dir,
        RetrievalAnswers.model_validate(
            {
                "suite": "retrieval",
                "answers": [
                    {
                        "id": q["id"],
                        "docs": q["expected_docs"] + q["acceptable_docs"],
                    }
                    for q in questions
                ],
            }
        ),
    )
    assert result.total and result.correct == result.total, result.failures


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_missing_an_acceptable_document_is_not_a_miss(slug):
    """Recall is measured against the required set alone, so ground truth
    scores 100% whether or not it names the incidental documents."""
    paths = OrgPaths(root=REPO, slug=slug)
    result = score_retrieval(
        paths.evals_dir,
        RetrievalAnswers.model_validate(
            {
                "suite": "retrieval",
                "answers": [
                    {"id": q["id"], "docs": q["expected_docs"]}
                    for q in _questions(paths)
                ],
            }
        ),
    )
    assert result.total and result.correct == result.total, result.failures


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_scan_hits_are_required_acceptable_or_a_recorded_diagnostic(slug):
    """The completeness property: for every questioned mention surface,
    every authored document whose rendered text carries it is accounted for.
    Nothing the scan can see is silently absent from the answer key."""
    from orgsmith.artifacts import load_engagements, load_foundation

    paths = OrgPaths(root=REPO, slug=slug)
    manifest = [
        e for e in load_manifest(paths) if e.authoring != "derived"
    ]
    reader = DocText(paths, load_engagements(paths), load_foundation(paths))
    clusters = json.loads((paths.evals_dir / "clusters.json").read_text())
    members = {
        m["path"] for c in clusters["clusters"] for m in c["members"]
    }
    texts = {
        e.path: reader.text(e)
        for e in manifest
        if (paths.share_dir / e.path).is_file() and e.path not in members
    }

    for question in _questions(paths):
        if not any(t.startswith("mention:person") for t in question["tags"]):
            continue  # alias scans mask planned surfaces; covered by emit
        surface = _surface_of(question)
        accounted = set(question["expected_docs"]) | set(
            question["acceptable_docs"]
        )
        hits = {p for p, t in texts.items() if surface_in_text(surface, t)}
        assert hits <= accounted, (
            f"{slug} {question['id']}: {sorted(hits - accounted)} carry "
            f"{surface!r} but are neither required nor acceptable"
        )


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_diagnostics_are_emitted_and_stamped(slug):
    paths = OrgPaths(root=REPO, slug=slug)
    data = json.loads((paths.evals_dir / "diagnostics.json").read_text())
    assert data["policy_version"] == LABEL_POLICY_VERSION
    clusters = json.loads((paths.evals_dir / "clusters.json").read_text())
    assert clusters["policy_version"] == LABEL_POLICY_VERSION
    readme = (paths.evals_dir / "README.md").read_text()
    assert f"policy version {LABEL_POLICY_VERSION}" in readme


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_recorded_value_collisions_are_real_and_never_gold(slug):
    """A collision names documents that really hold the surface and are
    really not answers. Recorded, never promoted."""
    from orgsmith.artifacts import load_engagements, load_foundation

    paths = OrgPaths(root=REPO, slug=slug)
    data = json.loads((paths.evals_dir / "diagnostics.json").read_text())
    if not data["value_collisions"]:
        pytest.skip(f"{slug} records no value collisions")

    by_path = {e.path: e for e in load_manifest(paths)}
    reader = DocText(paths, load_engagements(paths), load_foundation(paths))
    extraction = {
        json.loads(line)["id"]: json.loads(line)
        for line in (paths.evals_dir / "extraction.jsonl").read_text().splitlines()
        if line.strip()
    }
    for collision in data["value_collisions"]:
        question = extraction[collision["question"]]
        for path in collision["paths"]:
            assert surface_in_text(
                collision["value"], reader.text(by_path[path])
            ), path
            assert path not in question["expected_docs"], path
