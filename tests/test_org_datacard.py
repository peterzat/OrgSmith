"""Org tier: per-org data cards (M17).

The card is a derived artifact whose whole value is that it is recomputed
rather than written, so the only interesting assertions are that it is
fresh, that it is idempotent, and that it carries the unflattering parts.
"""

import pytest

from orgsmith.datacard import render_data_card
from orgsmith.paths import OrgPaths

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
        and (root / f"{p.name}-metadata" / "DATA-CARD.md").exists()
    )


SLUGS = _committed_slugs()


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_committed_card_is_fresh_and_idempotent(slug):
    paths = OrgPaths(root=REPO, slug=slug)
    first = render_data_card(paths)
    assert first == paths.data_card_md.read_text(), (
        f"{slug}: DATA-CARD.md is stale; run "
        f"`python -m orgsmith data-card {slug}`"
    )
    assert render_data_card(paths) == first


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_card_states_the_split_gap_and_the_non_claims(slug):
    """The two sections that stop the card being marketing: the distractor
    gap (which is zero on several orgs and says so) and the non-claims."""
    card = (REPO / "companies" / f"{slug}-metadata" / "DATA-CARD.md").read_text()
    assert "**Distractor gap = " in card
    assert "## Non-claims" in card
    assert "specimen, not a sample" in card
    assert "does not establish scoring well on a real" in card
    assert "## Feature matrix" in card
    assert "Relevance-label policy version" in card


@pytest.mark.parametrize("slug", flagship_params(SLUGS) or ["none"])
def test_card_publishes_the_residuals_it_has(slug):
    """Board findings and recorded fact-value disagreements appear on the
    card, or the card says plainly that there are none. What must never
    happen is a card that has residuals and does not show them."""
    import json

    paths = OrgPaths(root=REPO, slug=slug)
    card = paths.data_card_md.read_text()
    assert "## Known residuals" in card

    findings_dir = paths.meta_dir / "review" / "findings"
    if findings_dir.is_dir():
        for path in findings_dir.glob("*.json"):
            for finding in json.loads(path.read_text())["findings"]:
                assert finding["id"] in card, finding["id"]

    diagnostics = paths.evals_dir / "diagnostics.json"
    if diagnostics.exists():
        data = json.loads(diagnostics.read_text())
        for sighting in data["unplanned_alias_sightings"]:
            assert sighting["path"] in card
        for collision in data["value_collisions"]:
            assert collision["fact_id"] in card


def test_the_checksum_manifest_excludes_the_self_referential_card():
    """DATA-CARD.md quotes the manifest's own row for its org. Hashing it
    would make emitting the card change the digest that the card quotes."""
    import subprocess

    from tools.checksums import _org_files

    tracked = subprocess.run(
        ["git", "ls-files", "companies/northgate-staffing-metadata"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO,
    ).stdout
    assert "DATA-CARD.md" in tracked, "the card is not committed"
    assert not any(
        f.endswith("DATA-CARD.md") for f in _org_files("northgate-staffing")
    )
