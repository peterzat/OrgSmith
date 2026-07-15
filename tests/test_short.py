"""Short tier: static and configuration checks. Runs in the pre-push hook."""

import os
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.short

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "scratch", ".cache"}


def repo_files():
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def test_product_name_constant():
    import orgsmith

    assert orgsmith.PRODUCT_NAME == "OrgSmith"


def test_pre_rename_working_name_absent():
    # The project was renamed before the first commit. The old working name
    # must not appear anywhere: not in code, docs, recipes, or generated
    # orgs (rendered files are searched as raw bytes, best-effort).
    needle = ("org" + "forge").encode("ascii")
    offenders = []
    for path in repo_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        if needle in path.read_bytes().lower():
            offenders.append(str(path.relative_to(REPO)))
    assert offenders == []


def test_requirements_are_pinned():
    for req_file in ("requirements.txt", "requirements-dev.txt"):
        for line in (REPO / req_file).read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or line.startswith("-r "):
                continue
            assert re.match(r"^[A-Za-z0-9._-]+==\S+$", line), (
                f"{req_file}: unpinned requirement {line!r}"
            )


def test_pyproject_version_matches_package():
    # orgsmith.__version__ is the source of truth; pyproject.toml must not
    # drift from it. Regex parse: tomllib is 3.11+, this box runs 3.10.
    import orgsmith

    text = (REPO / "pyproject.toml").read_text()
    match = re.search(r'^version = "([^"]+)"$', text, re.MULTILINE)
    assert match, "pyproject.toml has no version line"
    assert match.group(1) == orgsmith.__version__


def test_core_modules_import():
    import orgsmith.cli  # noqa: F401
    import orgsmith.paths  # noqa: F401
    import orgsmith.seeds  # noqa: F401


def test_scripts_are_executable():
    for rel in ("bin/test", "bin/setup-deps", "bin/install-hooks", "hooks/pre-push"):
        assert os.access(REPO / rel, os.X_OK), f"{rel} is not executable"
