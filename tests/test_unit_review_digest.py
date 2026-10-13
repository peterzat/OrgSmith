"""Unit tier: the board's read-only rule is checked, not just asked for (M17d).

`review --digest` covers everything the board may read and excludes exactly
what it may write, so the board's chair can record it before dispatch and
verify it after.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from orgsmith.paths import org_paths
from orgsmith.review.digest import org_digest

pytestmark = pytest.mark.unit

REPO = Path(__file__).resolve().parent.parent
SLUG = "dev-mini"


@pytest.fixture()
def org(tmp_path):
    for rel in (f"recipes/{SLUG}", f"companies/{SLUG}", f"companies/{SLUG}-metadata"):
        shutil.copytree(REPO / rel, tmp_path / rel)
    return org_paths(SLUG, tmp_path)


def _first(directory: Path, pattern: str) -> Path:
    return sorted(p for p in directory.rglob(pattern) if p.is_file())[0]


def test_digest_is_stable(org):
    assert org_digest(org) == org_digest(org)


@pytest.mark.parametrize(
    "target",
    [
        lambda p: _first(p.docir_dir, "*.json"),
        lambda p: p.engagements_json,
        lambda p: p.manifest_jsonl,
        lambda p: p.state_json,
        lambda p: _first(p.share_dir, "*.docx"),
        lambda p: p.charter_md,
    ],
    ids=["docir", "ledger", "manifest", "state", "rendered", "recipe"],
)
def test_digest_moves_when_a_readable_file_changes(org, target):
    before = org_digest(org)
    path = target(org)
    path.write_bytes(path.read_bytes() + b" ")
    assert org_digest(org) != before


def test_digest_ignores_what_the_board_may_write(org):
    before = org_digest(org)
    org.review_dir.mkdir(parents=True, exist_ok=True)
    (org.review_dir / "reply-cross_document_voice.json").write_text("{}")
    org.generation_report_md.write_text("rewritten by report\n")
    assert org_digest(org) == before


def test_digest_moves_when_a_file_is_added(org):
    before = org_digest(org)
    (org.docir_dir / "stray.json").write_text("{}")
    assert org_digest(org) != before


def test_verify_digest_fails_loudly_on_a_change(org):
    def run(*extra):
        return subprocess.run(
            [sys.executable, "-m", "orgsmith", "review", SLUG, *extra,
             "--root", str(org.root)],
            cwd=REPO, capture_output=True, text=True,
        )

    digest = run("--digest").stdout.strip()
    assert run("--verify-digest", digest).returncode == 0
    org.engagements_json.write_text(org.engagements_json.read_text() + "\n")
    changed = run("--verify-digest", digest)
    assert changed.returncode == 1 and "CHANGED" in changed.stdout
