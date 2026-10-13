"""Unit tier: numbers no ledger owns are measured, never gated (AIRLOCK-01,
M17d)."""

from __future__ import annotations

import importlib.util
import json

import pytest

from orgsmith.artifacts import load_engagements, load_manifest
from orgsmith.review.numbers import numbers_in, unowned_by_doc
from orgsmith.review.report import run_report

from conftest import REPO, build_pure_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit

SAMPLES = [
    "238 universe / 61 screened (24 first tier, 37 second)",
    "In 2019 we saw 1,250 bids and 3 offers; phase 2 of 12.",
    "{{fact:f:E-2019-001.scope}} and 40 more",
    "rev 2.5, 2099, 1899, 10, 09, 007",
    "a 95th percentile and 48-hour turnaround",
    "E-2019-001 and v12 and 12b",
]


def _tool():
    spec = importlib.util.spec_from_file_location(
        "probe_numbers", REPO / "tools" / "probe_numbers.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("text", SAMPLES)
def test_the_package_counts_exactly_what_the_preregistered_tool_counts(text):
    assert numbers_in(text) == _tool().numbers_in(text)


def test_the_counting_rule():
    assert numbers_in(SAMPLES[0]) == {238, 61, 24, 37}
    assert numbers_in(SAMPLES[1]) == {1250, 12}  # 2019 is a year; 3 and 2 are small
    assert numbers_in(SAMPLES[2]) == {40}  # the placeholder supplies its own value


@pytest.fixture(scope="module")
def authored(tmp_path_factory):
    paths = build_pure_stages(tmp_path_factory.mktemp("numbers"))
    run_enrichment(paths)
    run_authoring(paths)
    return paths


def test_a_documents_own_fact_value_is_owned_and_a_coincidence_is_not(authored):
    paths = authored
    engagements = load_engagements(paths).engagements
    entry = next(
        e for e in load_manifest(paths)
        if e.engagement and any(r.endswith(".fee") for r in e.facts_refs)
    )
    own = next(x for x in engagements if x.id == entry.engagement)
    other = next(x for x in engagements if x.id != entry.engagement and x.fee != own.fee)
    path = paths.docir_dir / f"{entry.doc_id.replace(':', '')}.json"
    doc = json.loads(path.read_text())
    doc["blocks"].append({
        "kind": "paragraph",
        "text": f"We screened 238 companies; the fee is {own.fee:,}, and {other.fee:,} elsewhere.",
    })
    path.write_text(json.dumps(doc))
    found = unowned_by_doc(paths)[entry.doc_id]
    assert 238 in found
    assert own.fee not in found, "a value the document's own briefed fact owns is not counted"
    assert other.fee in found, "a coincidence with another engagement's fact is still unverifiable"


def test_the_report_carries_the_section(authored):
    assert run_report(authored) == 0
    text = authored.generation_report_md.read_text()
    assert "### Numbers no ledger owns" in text
    assert "never a gate" in text
