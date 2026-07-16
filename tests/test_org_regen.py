"""Org tier: committed fixtures re-derive from their recipes unchanged.

The property this exists to hold: `test_unit_pure_stages.py`'s determinism
test proves the code agrees with *itself* run-to-run, so a change that
moves every fixture *consistently* is green there and everywhere else in
the suite. That is exactly what a reordered `Faker` draw or a re-used
`rng` stream does. Only a diff against previously committed bytes catches
it, which is why `+ 1` on every expense line in `fabric/finance.py` passed
the entire suite before this module existed.

**The byte-pin is scoped to `dev-mini` until the fleet resets in M11.**
M8 lifts the freeze on `companies/`: churn moves `foundation.json`,
behavioral finance moves `finance.json`, and rotation moves the manifest,
so no pin against the other six fixtures' committed bytes can pass, and
they retire in M11 rather than being regenerated twice. Scoping the pin to
one recipe keeps the fault-injection property alive and gives it up on
six; that is the priced cost of the lift, recorded in SPEC.md, and it is
an argument for M11 landing promptly. The six stay committed and keep
validating clean (`test_org_fleet.py`) -- their artifacts are internally
consistent, and validation never re-runs the generator.

What survives the unpin fleet-wide, because it costs ~60ms and still
catches a real class of break: every recipe must keep *deriving* through
all four pure stages. A generator that crashes on cindergrove's 1998
recipe is caught here even though its bytes are no longer pinned.
"""

import json
import shutil

import pytest

from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.fabric import run_fabric
from orgsmith.foundation import run_scaffold
from orgsmith.paths import OrgPaths

from conftest import REPO

pytestmark = pytest.mark.org

# acl.json is derived rather than a pure-stage output (CLAUDE.md lists it
# with evals/ and PERMISSIONS.md as re-emittable), and test_unit_acl.py
# already diffs its re-derivation.
DERIVED_LEDGERS = {"acl.json"}


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

# The fixtures whose committed bytes are pinned. Scoped to the tracer for
# M8..M10 (see the module docstring); M11 restores it to the whole fleet by
# setting this back to SLUGS once the new fleet is generated. Kept as a
# derived list rather than a literal so an absent dev-mini degrades to an
# empty pin and a visible skip, not a KeyError.
PINNED = [s for s in SLUGS if s == "dev-mini"]


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory):
    """The whole fleet re-derived from recipes/ into tmp_path, once.

    Module-scoped because it is the tier's only expensive fixture and every
    test here reads it read-only. Each slug is copied from a pristine
    recipe, and the pure stages only ever write under their own slug.
    """
    root = tmp_path_factory.mktemp("regen")
    (root / "recipes").mkdir()
    fleet = {}
    for slug in SLUGS:
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


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", SLUGS or ["none"])
def test_every_committed_recipe_still_derives(slug, regenerated):
    """Fleet-wide, and the coverage that survives the scoped pin: all four
    pure stages run to completion on every recipe and write what the next
    stage reads. Cheap (~60ms for the fleet) and catches a generator that
    crashes on one era or knob cluster, which the pin no longer would."""
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


@pytest.mark.skipif(not PINNED, reason="no byte-pinned fixture")
@pytest.mark.parametrize("slug", PINNED or ["none"])
def test_committed_foundation_regenerates(slug, regenerated):
    fresh = regenerated[slug].foundation_json.read_text()
    # Blanking personas is only sound while scaffold leaves them to the model.
    assert all(p["persona"] == "" for p in json.loads(fresh)["people"])
    committed = OrgPaths(root=REPO, slug=slug).foundation_json.read_text()
    assert _blank_personas(fresh) == _blank_personas(committed)


@pytest.mark.skipif(not PINNED, reason="no byte-pinned fixture")
@pytest.mark.parametrize("slug", PINNED or ["none"])
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
@pytest.mark.parametrize("slug", PINNED or ["none"])
def test_committed_manifest_regenerates_byte_identical(slug, regenerated):
    committed = OrgPaths(root=REPO, slug=slug)
    assert (
        regenerated[slug].manifest_jsonl.read_bytes()
        == committed.manifest_jsonl.read_bytes()
    )


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", SLUGS or ["none"])
def test_committed_charter_redump_stays_additive(slug, regenerated):
    """`run_charter` rewrites charter.json unconditionally, so re-deriving a
    frozen fixture gains whatever fields the schema grew since it was
    generated (BACKLOG: charter-redump-drift). That is tolerable only while
    the drift stays additive: a re-dump may add a field that was already
    implicitly its default, but must never drop a key or move a value.

    Asserted this way the test is neutral on how charter-redump-drift is
    resolved. Guarding the write the way scaffold.py does leaves no diff at
    all, which passes; accepting the re-dump also passes. It does not
    ratify today's 23 gained keys by counting them, and it does not block
    M8 from adding more.

    Inertness of a gained field is enforced by the sibling tests, not here:
    a new charter field whose default were load-bearing would move the
    ledgers or the manifest.
    """
    fresh = json.loads(regenerated[slug].charter_json.read_text())
    committed = json.loads(OrgPaths(root=REPO, slug=slug).charter_json.read_text())
    _, lost, changed = _leaf_diffs(fresh, committed)
    assert lost == [], f"re-dump dropped committed charter keys: {lost}"
    assert changed == [], f"re-dump moved committed charter values: {changed}"
