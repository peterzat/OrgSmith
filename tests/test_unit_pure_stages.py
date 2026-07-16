"""Unit tier: pure stages (charter, foundation scaffold, fabric, docplan)."""

import json
import os
from datetime import date
from pathlib import Path

import pytest

from orgsmith.artifacts import (
    load_charter,
    load_engagements,
    load_finance,
    load_foundation,
    load_manifest,
)
from orgsmith.charter import parse_charter_md
from orgsmith.foundation import run_scaffold
from orgsmith.docplan import run_docplan
from orgsmith.naming import check_relpath
from orgsmith.paths import OrgPaths
from orgsmith.schemas import ManifestEntry

from conftest import REPO, build_pure_stages

pytestmark = pytest.mark.unit


def _tree_bytes(root: Path) -> dict[str, bytes]:
    out = {}
    for dirpath, _, filenames in os.walk(root / "companies"):
        for name in filenames:
            p = Path(dirpath) / name
            out[str(p.relative_to(root))] = p.read_bytes()
    return out


def test_pure_stages_are_deterministic(tmp_path):
    a = build_pure_stages(tmp_path / "a")
    b = build_pure_stages(tmp_path / "b")
    assert _tree_bytes(a.root) == _tree_bytes(b.root)


def test_rerun_is_noop_and_preserves_enrichment(tmp_path):
    paths = build_pure_stages(tmp_path)
    # Simulate merged enrichment prose, then re-run the producing stages.
    foundation = paths.foundation_json.read_text()
    edited = foundation.replace('"persona": ""', '"persona": "hand-merged"', 1)
    assert edited != foundation
    paths.foundation_json.write_text(edited)
    manifest_before = paths.manifest_jsonl.read_bytes()

    assert run_scaffold(paths) == 0
    assert run_docplan(paths) == 0
    assert paths.foundation_json.read_text() == edited
    assert paths.manifest_jsonl.read_bytes() == manifest_before


def test_charter_accepts_advisory_format_mix_total():
    """M9: target_docs and the docx/pdf/xlsx buckets are advisory. A recipe
    whose format_mix no longer sums to target_docs still parses, because the
    genre registry -- not this number -- decides how many documents exist."""
    text = (REPO / "recipes/dev-mini/ORG-CHARTER.md").read_text()
    loosened = text.replace("target_docs: 13", "target_docs: 12")
    charter = parse_charter_md(loosened, "dev-mini")
    assert charter.doc_culture.target_docs == 12
    assert charter.doc_culture.format_mix.total != charter.doc_culture.target_docs


def test_charter_rejects_missing_narrative():
    text = (REPO / "recipes/dev-mini/ORG-CHARTER.md").read_text()
    start = text.index("```yaml")
    end = text.index("```", start + 3) + 3
    yaml_only = "# Title\n\n" + text[start:end]
    with pytest.raises(SystemExit):
        parse_charter_md(yaml_only, "dev-mini")


def test_finance_tie_outs(pure_org):
    finance = load_finance(pure_org)
    assert finance.years, "no fiscal years"
    for fy in finance.years:
        assert sum(fy.quarters) == fy.revenue
        assert sum(fy.expenses.values()) > 0
    assert all(c.ok for c in finance.checks)


def test_roster_is_a_single_acyclic_tree(pure_org):
    foundation = load_foundation(pure_org)
    charter = load_charter(pure_org)
    roots = [p for p in foundation.people if p.reports_to is None]
    assert len(roots) == 1
    ids = {p.id for p in foundation.people}
    assert len(ids) == len(foundation.people)
    for p in foundation.people:
        assert p.email.endswith("@" + charter.domain)
        seen = set()
        cur = p
        while cur.reports_to is not None:
            assert cur.id not in seen, "cycle in reports_to"
            seen.add(cur.id)
            cur = foundation.person(cur.reports_to)
        assert cur.id == roots[0].id


def test_manifest_contract(pure_org):
    charter = load_charter(pure_org)
    foundation = load_foundation(pure_org)
    manifest = load_manifest(pure_org)
    facts = load_engagements(pure_org).fact_index()

    # Supply is driver-derived (test_supply_is_driver_derived owns the count);
    # here every entry must be well-formed ground truth.
    assert manifest, "empty manifest"
    seen_ids, seen_paths = set(), set()
    lo, hi = charter.doc_culture.date_range
    for entry in manifest:
        assert entry.doc_id not in seen_ids
        seen_ids.add(entry.doc_id)
        assert entry.path.lower() not in seen_paths
        seen_paths.add(entry.path.lower())
        assert check_relpath(entry.path) == []
        assert lo <= entry.date <= hi
        for author in entry.authors:
            emp = foundation.person(author).employment
            assert emp.start <= entry.date
        for ref in entry.facts_refs:
            assert ref in facts
        if entry.format == "xlsx":
            assert entry.authoring == "static"
    # Every planted fact appears in at least one document.
    referenced = {r for e in manifest for r in e.facts_refs}
    assert referenced == set(facts)


@pytest.mark.parametrize("bad_path", ["../outside-share.docx", "/etc/passwd"])
def test_load_manifest_rejects_tampered_path(tmp_path, bad_path):
    entry = ManifestEntry(
        doc_id="d:0001",
        path=bad_path,
        title="Tampered",
        genre="kickoff_memo",
        format="docx",
        date=date(2021, 1, 4),
        authors=["p:someone"],
    )
    paths = OrgPaths(root=tmp_path, slug="tampered")
    paths.docplan_dir.mkdir(parents=True)
    paths.manifest_jsonl.write_text(
        json.dumps(entry.model_dump(mode="json")) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="unsafe path"):
        load_manifest(paths)


def test_manifest_dates_cover_engagement_lifecycle(pure_org):
    engagements = load_engagements(pure_org).engagements
    manifest = load_manifest(pure_org)
    for eng in engagements:
        dates = [e.date for e in manifest if e.engagement == eng.id]
        assert dates, f"no docs for {eng.id}"
        assert min(dates) <= eng.start
        assert max(dates) >= eng.start + (eng.end - eng.start) * 0.3
