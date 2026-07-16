"""Org tier: every committed fixture re-derives from its recipe unchanged.

CLAUDE.md calls the committed fleet frozen: every fixture must keep
"regenerating byte-identical structure, without regeneration or hand
edits." Nothing enforced that. `test_unit_pure_stages.py`'s determinism
test proves the code agrees with *itself* run-to-run, on dev-mini only;
the rest of this tier validates committed artifacts against each other
and never re-runs the generator. So a change that moves every fixture
*consistently* was green in all three tiers, which is exactly what a
reordered `Faker` draw or a re-used `rng` stream does.

The fleet re-derives in ~60ms, so this runs over every fixture rather
than a representative one: a seed change that misses dev-mini and hits
one real recipe is the case worth catching.
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
def test_committed_foundation_regenerates(slug, regenerated):
    fresh = regenerated[slug].foundation_json.read_text()
    # Blanking personas is only sound while scaffold leaves them to the model.
    assert all(p["persona"] == "" for p in json.loads(fresh)["people"])
    committed = OrgPaths(root=REPO, slug=slug).foundation_json.read_text()
    assert _blank_personas(fresh) == _blank_personas(committed)


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", SLUGS or ["none"])
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


@pytest.mark.skipif(not SLUGS, reason="no committed orgs yet")
@pytest.mark.parametrize("slug", SLUGS or ["none"])
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
