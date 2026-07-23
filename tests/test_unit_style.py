"""Unit tier: M15 persona voice v2. A structured per-person style spec is
derived from charter + roster into ledger/style_specs.json (one twin,
derive_style_specs, shared by run_acl, STY-01, and brief building), and
knob-on briefs carry per-author guidance derived from it, auditable in
retained work orders. Default off: knob-off orgs derive an empty ledger,
write no artifact, and brief byte-identically."""

import json
import shutil

import pytest

from orgsmith.acl import run_acl
from orgsmith.artifacts import (
    load_charter,
    load_foundation,
    load_style_specs,
)
from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.foundation.style import derive_style_specs
from orgsmith.paths import OrgPaths
from orgsmith.validate.rules import Context, _needs_style, sty_01

from conftest import REPO, base_recipe_text, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


def _build_style_org(root, on=True, stages=True) -> OrgPaths:
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    text = base_recipe_text()
    anchor = "  format_mix: {docx: 15, pdf: 3, xlsx: 5}\n"
    assert anchor in text
    if on:
        text = text.replace(anchor, anchor + "  style_specs: true\n")
    (dest / "ORG-CHARTER.md").write_text(text)
    p = OrgPaths(root=root, slug="dev-mini")
    if stages:
        for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
            assert stage(p) == 0
    return p


@pytest.fixture(scope="module")
def style_org(tmp_path_factory):
    p = _build_style_org(tmp_path_factory.mktemp("style-org"))
    assert run_acl(p) == 0
    return p


def test_specs_cover_the_roster_deterministically(style_org):
    charter = load_charter(style_org)
    foundation = load_foundation(style_org)
    ledger = derive_style_specs(charter, foundation)
    assert [s.person for s in ledger.specs] == [
        p.id for p in foundation.people
    ]
    assert ledger == derive_style_specs(charter, foundation)  # deterministic
    # people differ: the spec is per-person, not a firm-wide constant
    shapes = {
        (s.voice_register, s.greeting, s.closing, tuple(s.habits))
        for s in ledger.specs
    }
    assert len(shapes) > 1
    for s in ledger.specs:
        assert len(s.habits) == 2 and len(s.banned_tics) == 2


def test_habits_are_never_self_contradictory(style_org):
    """A flat habit pool could hand one person both list-formatting habits
    (~6% of streams), and _style_guidance joins them verbatim into the brief:
    "You habitually: avoids lists entirely and writes in paragraphs; prefers
    numbered lists over bullet points." Drawing at most one habit per
    exclusion group is what rules that out, so assert the property over many
    per-person streams rather than over one roster."""
    from orgsmith.foundation.style import _HABIT_GROUPS

    charter = load_charter(style_org)
    foundation = load_foundation(style_org)
    seen = set()
    for i in range(500):
        charter.seed = 20260714 + i
        for s in derive_style_specs(charter, foundation).specs:
            assert len(set(s.habits)) == 2
            for group in _HABIT_GROUPS:
                assert len(set(s.habits) & set(group)) <= 1, (
                    f"{s.person} drew two habits from one exclusion group: "
                    f"{s.habits}"
                )
            seen.update(s.habits)
    # The grouping must not strand a habit: every one is still drawable.
    assert seen == {h for group in _HABIT_GROUPS for h in group}


def test_run_acl_writes_the_ledger_and_sty01_passes(style_org):
    on_disk = load_style_specs(style_org)
    assert on_disk is not None
    assert on_disk == derive_style_specs(
        load_charter(style_org), load_foundation(style_org)
    )
    ctx = Context.load(style_org)
    assert _needs_style(ctx) is None  # knob on: the rule runs
    assert list(sty_01(ctx)) == []


def test_knob_off_derives_empty_writes_nothing_and_skips_visibly(tmp_path):
    p = _build_style_org(tmp_path, on=False)
    assert run_acl(p) == 0
    assert not p.style_specs_json.exists()
    assert (
        derive_style_specs(load_charter(p), load_foundation(p)).specs == []
    )
    assert _needs_style(Context.load(p)) is not None  # visible skip


def test_sty01_fires_on_missing_and_on_tampered_ledger(style_org, tmp_path):
    root = tmp_path / "copy"
    shutil.copytree(style_org.root, root)
    q = OrgPaths(root=root, slug="dev-mini")

    data = json.loads(q.style_specs_json.read_text())
    data["specs"][0]["closing"] = "Warmly"  # a hand edit
    q.style_specs_json.write_text(json.dumps(data))
    findings = list(sty_01(Context.load(q)))
    assert any("does not recompute" in msg for msg, _ in findings)

    q.style_specs_json.unlink()
    findings = list(sty_01(Context.load(q)))
    assert any("missing" in msg for msg, _ in findings)


def test_knob_on_briefs_carry_the_spec_auditable_in_work_orders(style_org):
    """Criterion 10: guidance derived from the spec reaches every retained
    work order, per author; voice_diversify (v1) is untouched by it."""
    p = style_org
    run_enrichment(p)
    run_authoring(p)
    specs = {
        s.person: s
        for s in derive_style_specs(
            load_charter(p), load_foundation(p)
        ).specs
    }
    orders = sorted(p.workorders_dir.glob("author-*.json"))
    assert orders
    briefed = 0
    for wo_file in orders:
        wo = json.loads(wo_file.read_text())
        for doc in wo["docs"]:
            spec = specs[doc["authors"][0]["id"]]
            guidance = doc["guidance"]
            assert f"{spec.voice_register} register" in guidance
            for tic in spec.banned_tics:
                assert tic in guidance
            briefed += 1
    assert briefed


def test_knob_off_briefs_carry_no_style_text(tmp_path):
    p = _build_style_org(tmp_path, on=False)
    run_enrichment(p)
    run_authoring(p)
    orders = sorted(p.workorders_dir.glob("author-*.json"))
    assert orders
    for wo_file in orders:
        wo = json.loads(wo_file.read_text())
        for doc in wo["docs"]:
            assert "personal writing style" not in doc["guidance"]
