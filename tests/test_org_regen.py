"""Org tier: committed fixtures re-derive from their recipes unchanged.

The property this exists to hold: `test_unit_pure_stages.py`'s determinism
test proves the code agrees with *itself* run-to-run, so a change that
moves every fixture *consistently* is green there and everywhere else in
the suite. That is exactly what a reordered `Faker` draw or a re-used
`rng` stream does. Only a diff against previously committed bytes catches
it, which is why `+ 1` on every expense line in `fabric/finance.py` passed
the entire suite before this module existed.

**The byte-pin covers the whole committed fleet again (M11b).** It was
scoped to `dev-mini` for M8..M10 and to `{dev-mini, meridian-actuarial}` at
M11a, because M8 lifted the freeze on `companies/`: churn moved
`foundation.json`, behavioral finance moved `finance.json`, and rotation
moved the manifest, so no pin against the six pre-v2.0 fixtures' committed
bytes could pass. That was the priced cost of the lift, recorded in SPEC.md
as temporary and as an argument for M11 landing promptly. M11b retired those
six, generated their replacements on the v2.0 stack, and set `PINNED` back
to `SLUGS` -- see the comment there for why it is `SLUGS` itself rather than
a literal.

Independent of the pin, and worth keeping because it costs ~60ms and catches
a different class of break: every recipe must keep *deriving* through all
four pure stages. A generator that crashes on brackenridge's 1999 recipe is
caught by that test even for a recipe with no committed org.
"""

import json
import shutil

import pytest

from orgsmith.artifacts import load_charter, load_finance
from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.fabric import run_fabric
from orgsmith.foundation import run_scaffold
from orgsmith.paths import OrgPaths

from conftest import REPO, flagship_params

pytestmark = pytest.mark.org

# acl.json is derived rather than a pure-stage output (CLAUDE.md lists it
# with evals/ and PERMISSIONS.md as re-emittable), and test_unit_acl.py
# already diffs its re-derivation. distribution_lists.json (M14) and
# style_specs.json (M15) are written by the same `acl` stage and are derived
# for the same reason. Excluding them is not a hole: each has a validator
# rule that recomputes it against the producer's own twin function on every
# validate (DL-01, STY-01), which covers every committed org rather than
# only the pin fixture.
DERIVED_LEDGERS = {
    "acl.json",
    "distribution_lists.json",
    "style_specs.json",
}


def _committed_slugs():
    companies = REPO / "companies"
    if not companies.exists():
        return []
    return sorted(
        p.name[: -len("-metadata")]
        for p in companies.iterdir()
        if p.is_dir() and p.name.endswith("-metadata")
    )


COMMITTED = _committed_slugs()
SLUGS = [s for s in COMMITTED if (REPO / "recipes" / s).is_dir()]

# Every recipe in the repo, committed org or not. A recipe whose org has not
# been generated yet is exactly the one worth checking: the org costs hours of
# model authoring and the recipe costs ~60ms, so finding a broken one here is
# the whole point of checking at all.
RECIPES = sorted(p.name for p in (REPO / "recipes").iterdir() if p.is_dir())

# Recipes exempt from the coherence check below, and why each is exempt.
#
# EMPTY as of M15, and it should stay that way. M11b shrank this to
# {"dev-mini"} when the six pre-v2.0 recipes were retired; M15 spent the
# carve-out's one-time dev-mini regeneration and retuned the recipe
# (growth_rate 0.12 -> 0.07, expense_ratio 0.78 -> 0.80, roster_churn.hires
# 0 -> 1), so the tracer's terminal net margin fell from 43.1% to 22.7% and
# it now passes the check unexempted. Closes BACKLOG
# dev-mini-margin-incoherent.
#
# The bar for adding a name back: a recipe whose incoherence is the thing it
# exists to demonstrate. "Regenerating it is expensive" is not that bar -- it
# is what kept dev-mini here for four milestones, and the exemption outlived
# every reason given for it.
_COHERENCE_EXEMPT: set = set()
FLEET = [s for s in RECIPES if s not in _COHERENCE_EXEMPT]


def test_coherence_exempt_names_only_live_recipes():
    """The exempt set cannot go stale (M11a review NOTE, closed M11b).

    Nothing asserted that _COHERENCE_EXEMPT was a subset of RECIPES, so a
    deleted recipe left a dead entry behind and the set could not fail when
    it rotted. The concrete trap the review named: the fleet turn deletes the
    six legacy recipes, the set keeps six dead entries, and if a future fleet
    recipe ever reuses one of those slugs it is silently exempted from the
    coherence check with no signal. This is the same reason
    test_every_committed_fixture_has_a_recipe exists, and the same rule
    CLAUDE.md states -- grandfather by charter, not by absence.
    """
    stale = _COHERENCE_EXEMPT - set(RECIPES)
    assert not stale, (
        f"_COHERENCE_EXEMPT names recipes that no longer exist: {sorted(stale)}. "
        "Prune them in the same commit that deletes the recipe, or a future "
        "recipe reusing the slug is silently exempted from the coherence check."
    )

# No professional-services firm posts this. Set well clear of both sides of
# the measurement rather than tuned to it: the new fleet lands at 20.0-26.2%
# and the same recipes with the growth knob off land at 42.4-51.4%, so this
# separates coherent from incoherent by ~14pp in either direction.
_NET_MARGIN_CEILING = 0.40

# The fixtures whose committed bytes are pinned.
#
# M11b closes the v2.0 window and restores this to the whole committed fleet,
# as the M8 comment said it would. It is SLUGS itself now, not a filtered
# subset: every committed org was generated under the v2.0 stack, so there is
# no pre-v2.0 drift left to grandfather and no reason for any org to sit
# outside the pin. The narrowing to {dev-mini, meridian-actuarial} that M8
# through M11a needed is over.
#
# Deliberately SLUGS rather than a literal set: a literal is what let
# _COHERENCE_EXEMPT rot above, and it would let a newly generated org be
# quietly left unpinned. Every committed fixture with a recipe is pinned, and
# test_every_committed_fixture_has_a_recipe makes that the whole fleet.
PINNED = SLUGS


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory):
    """Every recipe re-derived from recipes/ into tmp_path, once.

    Module-scoped because it is the tier's only expensive fixture and every
    test here reads it read-only. Each slug is copied from a pristine
    recipe, and the pure stages only ever write under their own slug.

    Keyed over RECIPES rather than SLUGS so the not-yet-generated fleet
    recipes are covered too; the pin tests below index into it by committed
    slug, which is a subset.
    """
    root = tmp_path_factory.mktemp("regen")
    (root / "recipes").mkdir()
    fleet = {}
    for slug in RECIPES:
        shutil.copytree(REPO / "recipes" / slug, root / "recipes" / slug)
        paths = OrgPaths(root=root, slug=slug)
        assert run_charter(paths) == 0
        assert run_scaffold(paths) == 0
        assert run_fabric(paths) == 0
        assert run_docplan(paths) == 0
        fleet[slug] = paths
    return fleet


def _blank_personas(text):
    """Personas are model-authored and merged in after scaffold; the pure
    stages cannot produce them (airlock). Everything else must match."""
    data = json.loads(text)
    for person in data["people"]:
        person["persona"] = ""
    return data


def _leaf_diffs(new, old, path=""):
    """(gained, lost, changed) key paths between two parsed charters."""
    gained, lost, changed = [], [], []
    if isinstance(new, dict) and isinstance(old, dict):
        gained += [f"{path}.{k}".lstrip(".") for k in set(new) - set(old)]
        lost += [f"{path}.{k}".lstrip(".") for k in set(old) - set(new)]
        for k in set(new) & set(old):
            sub = _leaf_diffs(new[k], old[k], f"{path}.{k}".lstrip("."))
            gained += sub[0]
            lost += sub[1]
            changed += sub[2]
    elif new != old:
        changed.append(path or ".")
    return sorted(gained), sorted(lost), sorted(changed)


@pytest.mark.skipif(not COMMITTED, reason="no committed orgs yet")
def test_every_committed_fixture_has_a_recipe():
    """The parametrized fleet below is built from fixtures that still have a
    recipe. Without this, deleting one would shrink the fleet under test
    silently instead of failing."""
    assert SLUGS == COMMITTED


@pytest.mark.skipif(not RECIPES, reason="no recipes")
@pytest.mark.parametrize("slug", flagship_params(RECIPES) or ["none"])
def test_every_recipe_derives(slug, regenerated):
    """Fleet-wide, and the coverage that survives the scoped pin: all four
    pure stages run to completion on every recipe and write what the next
    stage reads. Cheap (~60ms each) and catches a generator that crashes on
    one era or knob cluster, which the pin no longer would.

    Widened from COMMITTED ∩ recipes to every recipe (M11a). A recipe with no
    committed org was previously untested until its org existed, which is
    backwards: the org is hours of model authoring and the recipe is 60ms to
    check. This is where a recipe asking for an impossible knob combination
    fails -- affiliations_in_docs without the engagements to host both sides,
    an OCR layer with no scans, a date_range starting before founding, a name
    colliding with the real-firm screen -- rather than partway through a fleet
    generation.
    """
    paths = regenerated[slug]
    for artifact in (
        paths.charter_json,
        paths.foundation_json,
        paths.finance_json,
        paths.engagements_json,
        paths.manifest_jsonl,
    ):
        assert artifact.exists(), artifact.name
        assert artifact.stat().st_size > 0, artifact.name


@pytest.mark.skipif(not FLEET, reason="no fleet recipes yet")
@pytest.mark.parametrize("slug", flagship_params(FLEET) or ["none"])
def test_fleet_recipe_growth_headcount_and_span_describe_one_firm(slug, regenerated):
    """BACKLOG recipe-growth-outruns-headcount, resolved 2026-07-16 (M11a).

    Behavioral finance (M8) made every recipe's incoherence visible: when
    expense_total was revenue * expense_ratio the realized ratio was the
    recipe's ratio by definition, forever. Now compensation tracks the roster,
    so a firm that compounds fees with a seat count that never moves posts a
    margin that climbs to something no professional-services firm posts. The
    model is right and the recipes were wrong.

    This is a check on the RECIPE's internal coherence, computed from its own
    finance ledger -- not a quality proxy, and TESTING.md's "never a metric
    threshold as a bar" is not in tension with it. That rule governs `report`
    numbers and board findings, which are proxies for prose quality with no
    validated threshold and a Goodhart problem. A net margin is ground-truth
    arithmetic over the ledger, closer to a tie-out than to an n-gram score,
    and nothing downstream optimizes against it.

    The founding year is excluded: it is a deliberate partial ramp (0.45x),
    so its margin is an artifact of the calendar rather than of the recipe.
    """
    paths = regenerated[slug]
    charter = load_charter(paths)
    finance = load_finance(paths)
    rows = [
        (y.year, y.revenue, sum(y.expenses.values()))
        for y in finance.years
        if y.year != charter.founded
    ]
    assert rows, f"{slug}: no full fiscal year to judge"
    margins = [(rev - exp) / rev for _, rev, exp in rows]
    trail = ", ".join(f"FY{y}:{m*100:.1f}%" for (y, _, _), m in zip(rows, margins))
    assert margins[-1] < _NET_MARGIN_CEILING, (
        f"{slug} posts a {margins[-1]*100:.1f}% net margin in its last year "
        f"(growth_rate={charter.finance.growth_rate}, "
        f"seats={sum(charter.headcount.values())}, "
        f"hires={charter.roster_churn.hires}). A recipe's growth, headcount, "
        f"and span have to describe one firm: raise roster_churn.hires so the "
        f"roster keeps up with the fees, or lower growth_rate. Trail: {trail}"
    )


@pytest.mark.skipif(not PINNED, reason="no byte-pinned fixture")
@pytest.mark.parametrize("slug", flagship_params(PINNED) or ["none"])
def test_committed_foundation_regenerates(slug, regenerated):
    fresh = regenerated[slug].foundation_json.read_text()
    # Blanking personas is only sound while scaffold leaves them to the model.
    assert all(p["persona"] == "" for p in json.loads(fresh)["people"])
    committed = OrgPaths(root=REPO, slug=slug).foundation_json.read_text()
    assert _blank_personas(fresh) == _blank_personas(committed)


@pytest.mark.skipif(not PINNED, reason="no byte-pinned fixture")
@pytest.mark.parametrize("slug", flagship_params(PINNED) or ["none"])
def test_committed_ledgers_regenerate_byte_identical(slug, regenerated):
    committed = OrgPaths(root=REPO, slug=slug)
    names = sorted(
        p.name
        for p in committed.ledger_dir.glob("*.json")
        if p.name not in DERIVED_LEDGERS
    )
    assert names, "fixture committed no pure-stage ledgers"
    for name in names:
        assert (regenerated[slug].ledger_dir / name).read_bytes() == (
            committed.ledger_dir / name
        ).read_bytes(), name


@pytest.mark.skipif(not PINNED, reason="no byte-pinned fixture")
@pytest.mark.parametrize("slug", flagship_params(PINNED) or ["none"])
def test_committed_manifest_regenerates_byte_identical(slug, regenerated):
    committed = OrgPaths(root=REPO, slug=slug)
    assert (
        regenerated[slug].manifest_jsonl.read_bytes()
        == committed.manifest_jsonl.read_bytes()
    )


@pytest.mark.skipif(not PINNED, reason="no byte-pinned fixture")
@pytest.mark.parametrize("slug", flagship_params(PINNED) or ["none"])
def test_committed_charter_regenerates_byte_identical(slug, regenerated):
    """charter-redump-drift, resolved (2026-07-16, M11a): charter.json is
    frozen beside the ledgers for any fixture generated under the current
    schema, and `run_charter` now guards its write on the recipe hash so a
    `/forge` resume cannot dirty one.

    Scoped to PINNED rather than SLUGS because the drift was never a code
    defect: the six pre-v2.0 fixtures' committed charters were written by an
    older schema, so a fresh derive legitimately gains fields they never
    carried. They keep only the additive guarantee below until the fleet turn
    retires them. Measured 2026-07-16: dev-mini byte-identical, the other six
    drift (fernhollow included, which was still clean at M8 -- exactly the
    widening the backlog entry predicted).
    """
    assert (
        regenerated[slug].charter_json.read_bytes()
        == OrgPaths(root=REPO, slug=slug).charter_json.read_bytes()
    )


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_committed_charter_redump_stays_additive(slug, regenerated):
    """The weaker guarantee that still covers the not-yet-retired fixtures
    whose charters predate the current schema (BACKLOG: charter-redump-drift).
    A re-dump may add a field that was already implicitly its default, but
    must never drop a key or move a value.

    Kept alongside the byte pin above rather than replaced by it: this is the
    only thing standing under the six legacy fixtures until the fleet turn,
    and it deliberately does not count today's gained keys, which would ratify
    the drift instead of bounding it.

    Inertness of a gained field is enforced by the sibling tests, not here:
    a new charter field whose default were load-bearing would move the
    ledgers or the manifest.
    """
    fresh = json.loads(regenerated[slug].charter_json.read_text())
    committed = json.loads(OrgPaths(root=REPO, slug=slug).charter_json.read_text())
    _, lost, changed = _leaf_diffs(fresh, committed)
    assert lost == [], f"re-dump dropped committed charter keys: {lost}"
    assert changed == [], f"re-dump moved committed charter values: {changed}"
