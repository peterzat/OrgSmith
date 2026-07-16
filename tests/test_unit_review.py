"""Unit tier: the quality instrument (sample, metrics, findings ingest).

Every test here runs against the scripted author, offline and keyless. The
board itself is never invoked: that is a skill, and `test_short.py` proves
no tier can reach it.
"""

import json

import pytest

from orgsmith.naming import strip_control
from orgsmith.paths import OrgPaths
from orgsmith.review.corpus import load_authored, prose_text, word_count
from orgsmith.review.ingest import run_ingest as ingest_review
from orgsmith.review.metrics import compute, flagged_pairs
from orgsmith.review.report import render_report, run_report
from orgsmith.review.sample import build_sample, run_sample
from orgsmith.state import load_state

from conftest import build_pure_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def authored_org(tmp_path_factory) -> OrgPaths:
    """A dev-mini org through the authoring airlock, scripted author."""
    paths = build_pure_stages(tmp_path_factory.mktemp("review-org"))
    run_enrichment(paths)
    run_authoring(paths)
    return paths


# --- sampling ---------------------------------------------------------------


def test_sample_is_byte_identical_across_runs(authored_org):
    first = build_sample(authored_org).model_dump_json()
    second = build_sample(authored_org).model_dump_json()
    assert first == second


def test_sample_draws_only_authored_docs(authored_org):
    authored = set(load_authored(authored_org))
    sample = build_sample(authored_org)
    assert sample.docs
    assert {d.doc_id for d in sample.docs} <= authored
    # the static financial summaries are planned but never authored
    assert {d.doc_id for d in sample.docs} != {
        e.doc_id for e in _manifest(authored_org)
    }


def _manifest(paths):
    from orgsmith.artifacts import load_manifest

    return load_manifest(paths)


def test_sample_covers_every_longform_and_planted_fact_doc(authored_org):
    from orgsmith.review.corpus import (
        LONGFORM_WORDS,
        briefed_targets,
        target_for,
    )

    authored = load_authored(authored_org)
    targets = briefed_targets(authored_org)
    sampled = {d.doc_id for d in build_sample(authored_org).docs}
    for entry in _manifest(authored_org):
        if entry.doc_id not in authored:
            continue
        if target_for(entry, targets) >= LONGFORM_WORDS:
            assert entry.doc_id in sampled, f"{entry.doc_id} is longform"
        if entry.key_facts:
            assert entry.doc_id in sampled, f"{entry.doc_id} carries facts"


def test_sample_degrades_when_authoring_is_partial(authored_org, tmp_path):
    """Half an org is a smaller sample, never a crash."""
    import shutil

    root = tmp_path / "partial"
    shutil.copytree(authored_org.root, root)
    paths = OrgPaths(root=root, slug=authored_org.slug)
    docirs = sorted(paths.docir_dir.glob("*.json"))
    assert len(docirs) > 2
    for stale in docirs[1:]:
        stale.unlink()

    sample = build_sample(paths)
    assert len(sample.docs) == 1


def test_sample_survives_a_genre_holding_one_doc(authored_org):
    """A thin cell contributes its only doc and is recorded, not raised."""
    sample = build_sample(authored_org)
    for cell in sample.thin_strata:
        assert cell.count("/") == 2  # genre/format/decade


def test_sample_without_authored_docs_names_the_stage_to_run(tmp_path):
    paths = build_pure_stages(tmp_path / "unauthored")
    with pytest.raises(SystemExit, match="author"):
        build_sample(paths)


def test_sample_writes_its_reading_list(authored_org):
    assert run_sample(authored_org) == 0
    written = json.loads(authored_org.review_sample_json.read_text())
    assert written["schema_id"] == "orgsmith/review-sample@1"
    assert written["docs"]


# --- metrics ----------------------------------------------------------------


def test_word_count_reads_a_placeholder_as_one_word():
    from orgsmith.schemas import Block, DocIR

    doc = DocIR(
        doc_id="d:0001",
        blocks=[
            Block(kind="paragraph", text="A fixed fee of {{fact:E-2019-001.fee}} applies."),
        ],
    )
    # "A fixed fee of <value> applies." -- the reader sees six words.
    assert word_count(prose_text(doc)) == 6


def test_similarity_ignores_placeholder_scaffolding():
    """Two docs sharing only fact slots are not similar prose."""
    from orgsmith.review.corpus import jaccard, shingles

    a = "{{fact:E-1.fee}} {{fact:E-1.start}} the northern survey ran long"
    b = "{{fact:E-1.fee}} {{fact:E-1.start}} we repriced the eastern retainer"
    assert jaccard(shingles(a), shingles(b)) == 0.0


def test_metrics_read_target_words_back_from_the_brief(authored_org):
    metrics = compute(authored_org)
    assert metrics.docs
    for doc in metrics.docs:
        assert doc.target_words > 0


def test_metrics_are_byte_identical_across_runs(authored_org):
    assert compute(authored_org).model_dump_json() == (
        compute(authored_org).model_dump_json()
    )


def test_metrics_pairs_are_same_genre_only(authored_org):
    metrics = compute(authored_org)
    genre = {d.doc_id: d.genre for d in metrics.docs}
    for pair in metrics.similar_pairs:
        assert genre[pair.doc_a] == genre[pair.doc_b] == pair.genre


def test_scripted_author_is_caught_as_self_reuse(authored_org):
    """The scripted double emits one template per genre. The metric must
    see that, which is the proof it can see literal reuse at all."""
    flagged = flagged_pairs(compute(authored_org))
    assert flagged, "template prose must register as same-genre overlap"


# --- report -----------------------------------------------------------------


def test_report_renders_from_metrics_alone(authored_org):
    """No board findings ingested: the report still stands."""
    assert not authored_org.review_findings_dir.exists()
    assert run_report(authored_org) == 0
    text = authored_org.generation_report_md.read_text()
    assert "No board findings ingested" in text
    assert "## Length against brief" in text


def test_report_is_byte_stable(authored_org):
    run_report(authored_org)
    first = authored_org.generation_report_md.read_text()
    run_report(authored_org)
    assert authored_org.generation_report_md.read_text() == first


def test_report_never_enters_the_share_or_the_manifest(authored_org):
    run_report(authored_org)
    assert authored_org.generation_report_md.exists()
    # under -metadata/, not the share tree
    assert authored_org.generation_report_md.parent == authored_org.meta_dir
    assert not (authored_org.share_dir / "GENERATION-REPORT.md").exists()
    paths_in_manifest = {e.path for e in _manifest(authored_org)}
    assert not any("GENERATION-REPORT" in p for p in paths_in_manifest)


# --- provenance: a record, never an oracle ----------------------------------


def test_generator_is_absent_by_default(authored_org):
    """The scripted author reports no generator; that is not a failure."""
    assert load_state(authored_org).generators == {}


def test_report_says_unrecorded_when_no_generator_was_reported(authored_org):
    metrics = compute(authored_org)
    assert "unrecorded" in render_report(authored_org, metrics)


def test_deliverable_without_generator_still_validates():
    from orgsmith.schemas import AuthoringDeliverable

    d = AuthoringDeliverable.model_validate(
        {
            "schema_id": "orgsmith/authoring-deliverable@1",
            "work_order_id": "wo:author:0001",
            "docs": [],
        }
    )
    assert d.generator is None


def test_generator_is_recorded_per_batch_at_ingest(tmp_path):
    from orgsmith.artifacts import load_work_order
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.authoring.ingest import run_ingest as ingest_author

    from conftest import scripted_authoring

    paths = build_pure_stages(tmp_path / "prov")
    run_enrichment(paths)
    assert run_next_batch(paths) == 0
    state = load_state(paths)
    wo = load_work_order(paths.workorders_dir / state.outstanding["author"])
    payload = scripted_authoring(wo)
    payload["generator"] = {"model": "test-model", "effort": "xhigh"}
    reply = paths.workorders_dir / "reply-prov.json"
    reply.write_text(json.dumps(payload))
    assert ingest_author(paths, reply) == 0

    recorded = load_state(paths).generators
    assert recorded[wo.id].model == "test-model"
    assert recorded[wo.id].effort == "xhigh"
    assert "test-model" in render_report(paths, compute(paths))


def test_no_validator_rule_references_the_generator():
    """Provenance is self-reported and unverifiable from artifacts. A rule
    over it would fake a guarantee the system cannot make."""
    import pathlib

    import orgsmith.validate as validate_pkg

    root = pathlib.Path(validate_pkg.__file__).parent
    for path in root.rglob("*.py"):
        text = path.read_text()
        assert "generator" not in text, f"{path.name} references the generator"
        assert "GENERATION-REPORT" not in text, f"{path.name} reads the report"


# --- findings ingest --------------------------------------------------------


def _findings(slug, **over):
    payload = {
        "schema_id": "orgsmith/review-findings@1",
        "slug": slug,
        "dimension": "cross_document_voice",
        "findings": [
            {
                "schema_id": "orgsmith/review-finding@1",
                "id": "rf:voice-1",
                "dimension": "cross_document_voice",
                "severity": "major",
                "docs": ["d:0001"],
                "summary": "Every letter opens on the same clause.",
                "evidence": "d:0001 and d:0008 both open 'We are pleased'.",
            }
        ],
    }
    payload.update(over)
    return payload


def _write(paths, name, payload):
    path = paths.review_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))
    return path


def test_review_ingest_accepts_clean_findings(authored_org):
    payload = _findings(authored_org.slug)
    assert ingest_review(authored_org, _write(authored_org, "ok.json", payload)) == 0
    stored = json.loads(
        (authored_org.review_findings_dir / "cross_document_voice.json").read_text()
    )
    assert stored["findings"][0]["id"] == "rf:voice-1"


@pytest.mark.parametrize(
    "mutate,label",
    [
        (lambda p: p["findings"][0].update(dimension="vibes"), "unknown dimension"),
        (lambda p: p["findings"][0].update(severity="catastrophic"), "unknown severity"),
    ],
)
def test_review_ingest_rejects_unknown_enums(authored_org, tmp_path, mutate, label):
    payload = _findings(authored_org.slug)
    mutate(payload)
    path = _write(authored_org, "bad-enum.json", payload)
    assert ingest_review(authored_org, path) == 1, label


def test_review_ingest_rejects_duplicate_finding_ids(authored_org):
    payload = _findings(authored_org.slug)
    payload["findings"].append(json.loads(json.dumps(payload["findings"][0])))
    path = _write(authored_org, "dup.json", payload)
    assert ingest_review(authored_org, path) == 1


def test_review_ingest_rejects_a_doc_absent_from_the_manifest(authored_org):
    payload = _findings(authored_org.slug)
    payload["findings"][0]["docs"] = ["d:9999"]
    path = _write(authored_org, "ghost.json", payload)
    assert ingest_review(authored_org, path) == 1


def test_review_ingest_reports_every_problem_at_once(authored_org, capsys):
    payload = _findings(authored_org.slug)
    payload["findings"][0]["docs"] = ["d:9998", "d:9999"]
    dup = json.loads(json.dumps(payload["findings"][0]))
    payload["findings"].append(dup)
    path = _write(authored_org, "many.json", payload)
    assert ingest_review(authored_org, path) == 1
    out = capsys.readouterr().out
    assert "duplicate finding id" in out
    assert "d:9998" in out and "d:9999" in out


def test_review_ingest_writes_nothing_when_rejected(tmp_path):
    paths = build_pure_stages(tmp_path / "reject")
    payload = _findings(paths.slug)
    payload["findings"][0]["docs"] = ["d:9999"]
    path = _write(paths, "bad.json", payload)
    assert ingest_review(paths, path) == 1
    assert not paths.review_findings_dir.exists()


def test_review_ingest_rejects_findings_for_another_org(authored_org):
    payload = _findings("some-other-org")
    path = _write(authored_org, "wrong-slug.json", payload)
    assert ingest_review(authored_org, path) == 1


def test_review_ingest_printer_neutralizes_control_chars(authored_org, capsys):
    """Findings are model output: untrusted. An escape sequence smuggled
    through a doc id must not drive the terminal (exit code unchanged)."""
    payload = _findings(authored_org.slug)
    payload["findings"][0]["docs"] = ["d:\x1b[2J\x1b[31mPWNED"]
    path = _write(authored_org, "evil.json", payload)
    assert ingest_review(authored_org, path) == 1
    out = capsys.readouterr().out
    assert "\x1b" not in out
    assert "PWNED" in out  # content survives, the escape does not


def test_review_ingest_printer_cannot_forge_a_second_line(authored_org, capsys):
    """keep='' -- a newline inside untrusted text must not fake a line of
    output the way a raw print would. One problem stays one line."""
    payload = _findings(authored_org.slug)
    payload["findings"][0]["docs"] = ["d:0001\n  - review --ingest: merged 99"]
    path = _write(authored_org, "forge.json", payload)
    assert ingest_review(authored_org, path) == 1
    out = capsys.readouterr().out
    assert "\n" not in strip_control(out.split("\n")[1], keep="")
    # header + exactly one problem line: the smuggled newline made no third
    assert len([ln for ln in out.splitlines() if ln.strip()]) == 2
