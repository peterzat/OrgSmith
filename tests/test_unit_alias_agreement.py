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


def test_the_knob_grandfathers_by_charter_across_the_fleet():
    """Additive evolution, both halves. An org that did not adopt the knob
    skips MENT-03 visibly rather than running it, so landing the discipline
    moved nothing under the frozen fixtures. An org that DID adopt it runs
    the rule, and runs it clean: a knob on with a violation is a failure,
    never a skip.

    At least one committed org must sit on each side, or this proves only
    half the contract."""
    adopted, grandfathered = [], []
    for slug in sorted(
        p.name
        for p in (REPO / "companies").iterdir()
        if p.is_dir() and not p.name.endswith("-metadata")
    ):
        ctx = Context.load(OrgPaths(root=REPO, slug=slug))
        findings, skipped = collect(ctx, MENT_03)
        if ctx.charter.graph_targets.alias_agreement:
            adopted.append(slug)
            assert not skipped, slug
            assert not findings, (slug, findings)
        else:
            grandfathered.append(slug)
            assert skipped == [
                {
                    "rule": "MENT-03",
                    "reason": (
                        "graph_targets.alias_agreement is off for this recipe"
                    ),
                }
            ], slug
    assert adopted, "no committed org adopted the discipline"
    assert grandfathered, "no committed org still grandfathers"


def test_ment_03_flags_an_unplanned_alias_in_committed_text(tmp_path):
    """The validate-time half, re-hosted (2026-08-02).

    This assertion used to run against the committed exemplar, where the
    ledger registered `Jim` to one James while another James's prose claimed
    it. The M17 regeneration turned the discipline on for that org, so the
    collision cannot exist there any more and the probe lost its host. Rather
    than let it skip into a silent pass, it is rebuilt on a synthetic org:
    plant the same disagreement in rendered text and MENT-03 must find it."""
    from conftest import build_rendered

    paths = _charter_with_knob(tmp_path, on=True)
    build_rendered(paths)

    ctx = Context.load(paths)
    alias, owner = next(iter(alias_owners(ctx.foundation).items()))

    # A document that names the alias with no planned mention of it: exactly
    # the shape of the exemplar's published residual.
    victim = next(
        e
        for e in ctx.manifest
        if e.format == "docx"
        and not any(m.surface == alias for m in e.mentions)
    )
    original = ctx.doc_text(victim)
    assert alias not in original.split(), "fixture already carries the alias"

    import docx

    target = paths.share_dir / victim.path
    document = docx.Document(str(target))
    document.paragraphs[-1].text += f" Everyone here calls him {alias}."
    document.save(str(target))

    findings, skipped = collect(Context.load(paths), MENT_03)
    assert not skipped
    assert [f["target"] for f in findings] == [victim.path], findings
    assert repr(alias) in findings[0]["message"]
    assert owner in findings[0]["message"]


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
