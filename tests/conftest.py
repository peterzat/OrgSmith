import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from orgsmith.charter import run_charter  # noqa: E402
from orgsmith.docplan import run_docplan  # noqa: E402
from orgsmith.fabric import run_fabric  # noqa: E402
from orgsmith.foundation import run_scaffold  # noqa: E402
from orgsmith.paths import OrgPaths


def build_pure_stages(root: Path, slug: str = "dev-mini") -> OrgPaths:
    """Copy the tracer recipe into `root` and run every pure stage up to
    docplan. No model pass, no network."""
    (root / "recipes").mkdir(parents=True, exist_ok=True)
    dest = root / "recipes" / slug
    if not dest.exists():
        shutil.copytree(REPO / "recipes" / slug, dest)
    paths = OrgPaths(root=root, slug=slug)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


@pytest.fixture(scope="module")
def pure_org(tmp_path_factory) -> OrgPaths:
    """One dev-mini org built through docplan, shared read-only per module."""
    return build_pure_stages(tmp_path_factory.mktemp("pure-org"))
