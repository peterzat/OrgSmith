"""Unit tier: alias-agreement discipline (M17).

The exemplar's published headline residual, four of six board reviewers
independently: the ledger registers the nickname `Jim` to one James while a
different James's model-authored persona claims it, so the firm overview
calls the wrong man Jim and the corpus contradicts itself. No fact check can
see that, because both documents faithfully report a source that disagrees
with itself.

`graph_targets.alias_agreement` makes it impossible by construction. Off by
default, so the frozen fleet is untouched.
"""

import shutil

import pytest

from orgsmith.artifacts import load_charter, load_foundation
from orgsmith.authoring.ingest import (
    alias_owners,
    check_alias_agreement,
    check_persona_aliases,
)
from orgsmith.paths import OrgPaths
from orgsmith.validate import collect
from orgsmith.validate.rules import RULES, Context

from conftest import REPO, base_recipe_text, build_pure_stages

pytestmark = pytest.mark.unit

MENT_03 = [r for r in RULES if r.id == "MENT-03"]


def _charter_with_knob(root, on: bool) -> OrgPaths:
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    text = base_recipe_text()
    anchor = "  external_people: 3\n"
    assert anchor in text
    knobs = "  nickname_aliases: 1\n"
    if on:
        knobs += "  alias_agreement: true\n"
    (dest / "ORG-CHARTER.md").write_text(text.replace(anchor, anchor + knobs))
    return build_pure_stages(root)


def test_the_knob_defaults_off():
    assert not load_charter(
        OrgPaths(root=REPO, slug="dev-mini")
    ).graph_targets.alias_agreement


def test_the_knob_is_inert_on_the_frozen_fleet():
    """Additive evolution: with the knob unset, every committed org's rule
    set is unchanged and MENT-03 skips visibly rather than running."""
    for slug in sorted(
        p.name
        for p in (REPO / "companies").iterdir()
        if p.is_dir() and not p.name.endswith("-metadata")
    ):
        ctx = Context.load(OrgPaths(root=REPO, slug=slug))
        _, skipped = collect(ctx, MENT_03)
        assert skipped == [
            {
                "rule": "MENT-03",
                "reason": "graph_targets.alias_agreement is off for this recipe",
            }
        ], slug


def test_forced_on_ment_03_flags_the_exemplars_jim_collision(tmp_path):
    """The critique's probe, on today's northgate: turn the knob on against
    the committed exemplar and the rule finds the overview that calls the
    wrong James 'Jim'.

    Scoped to the pre-regeneration exemplar deliberately. Once northgate is
    regenerated with the knob on, this collision cannot exist, and the
    durable proofs are the synthetic ones below."""
    shutil.copytree(
        REPO / "companies" / "northgate-staffing",
        tmp_path / "companies" / "northgate-staffing",
    )
    shutil.copytree(
        REPO / "companies" / "northgate-staffing-metadata",
        tmp_path / "companies" / "northgate-staffing-metadata",
    )
    paths = OrgPaths(root=tmp_path, slug="northgate-staffing")
    ctx = Context.load(paths)
    ctx.charter.graph_targets.alias_agreement = True

    findings, skipped = collect(ctx, MENT_03)
    assert not skipped
    assert [f["target"] for f in findings] == [
        "Firm/Firm Overview 2015 v3.docx"
    ], findings
    assert "'Jim'" in findings[0]["message"]
    assert "p:james.grant" in findings[0]["message"]


def test_a_clean_org_passes_with_the_knob_on(tmp_path):
    paths = _charter_with_knob(tmp_path, on=True)
    assert paths.charter_json.exists()
    assert load_charter(paths).graph_targets.alias_agreement


def test_ingest_rejects_an_unplanned_alias_in_authored_text(tmp_path):
    from orgsmith.artifacts import load_manifest

    paths = _charter_with_knob(tmp_path, on=True)
    foundation = load_foundation(paths)
    alias, owner = next(iter(alias_owners(foundation).items()))
    entry = next(
        e
        for e in load_manifest(paths)
        if not any(m.surface == alias for m in e.mentions)
    )
    problems = check_alias_agreement(
        entry, foundation, f"The team agreed, and {alias} signed off."
    )
    assert problems and alias in problems[0] and owner in problems[0]


def test_a_planned_alias_in_its_own_document_passes(tmp_path):
    paths = _charter_with_knob(tmp_path, on=True)
    from orgsmith.artifacts import load_manifest

    foundation = load_foundation(paths)
    aliases = set(alias_owners(foundation))
    entry = next(
        (
            e
            for e in load_manifest(paths)
            if any(m.surface in aliases for m in e.mentions)
        ),
        None,
    )
    if entry is None:
        pytest.skip("this org plans no alias mention")
    alias = next(m.surface for m in entry.mentions if m.surface in aliases)
    assert not check_alias_agreement(
        entry, foundation, f"{alias} chaired the session."
    )


def test_an_alias_inside_a_longer_planned_name_is_not_a_finding(tmp_path):
    """The false positive the mask exists to prevent: a registered `Jim`
    standing inside another person's planned `Jim Halpert`."""
    paths = _charter_with_knob(tmp_path, on=True)
    foundation = load_foundation(paths)
    alias = next(iter(alias_owners(foundation)))

    class Entry:
        mentions = [
            type(
                "M",
                (),
                {"surface": f"{alias} Halpert", "kind": "person"},
            )()
        ]

    assert not check_alias_agreement(
        Entry(), foundation, f"{alias} Halpert chaired the session."
    )


def test_persona_gate_rejects_a_stolen_nickname(tmp_path):
    """The root cause: enrichment writing another person's registered alias
    into a persona, which then propagates into every document."""
    paths = _charter_with_knob(tmp_path, on=True)
    foundation = load_foundation(paths)
    alias, owner = next(iter(alias_owners(foundation).items()))
    thief = next(p.id for p in foundation.people if p.id != owner)

    assert not check_persona_aliases(
        foundation, {owner: f"Everyone calls them {alias}."}
    ), "the registered owner may claim their own alias"

    problems = check_persona_aliases(
        foundation, {thief: f"Around here he is simply {alias}."}
    )
    assert problems and alias in problems[0] and owner in problems[0]
