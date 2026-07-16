"""Short tier: static and configuration checks. Runs in the pre-push hook."""

import ast
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


# --- the board never runs in a test tier ------------------------------------
# The review board is a skill, and skills are the only place a model pass
# may happen. bin/test must never reach one: an LLM grading an LLM inside a
# test tier would make the suite non-deterministic, keyed, and online, and
# would quietly turn a critic's opinion into a gate. These checks are
# static, so they hold without running the board to find out.

# Import roots that could reach a model or a socket. `urllib.parse` is not
# here on purpose: assemble.py quotes TOC links with it and never opens a
# connection, so the ban is on `urllib.request` specifically.
_OFFLINE_BANNED = {
    "socket",
    "ssl",
    "http",
    "requests",
    "httpx",
    "urllib3",
    "aiohttp",
    "anthropic",
    "openai",
    "subprocess",
}


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module)
    return roots


def test_review_package_cannot_reach_a_model_or_the_network():
    """The instrument reads committed files and nothing else."""
    review = REPO / "orgsmith" / "review"
    modules = sorted(review.rglob("*.py"))
    assert modules, "review package missing"
    for path in modules:
        for name in _imported_roots(path):
            root = name.split(".")[0]
            offender = name if name in _OFFLINE_BANNED else root
            assert offender not in _OFFLINE_BANNED, (
                f"{path.relative_to(REPO)} imports {name!r}: the review "
                f"package must stay offline and model-free"
            )


def test_no_test_tier_invokes_the_review_board():
    """No test may dispatch the board skill or fabricate a model pass."""
    board_markers = ("forge-review", "forge_review")
    for path in sorted((REPO / "tests").rglob("*.py")):
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in board_markers:
            assert marker not in text, (
                f"{path.name} references the board skill {marker!r}; the "
                f"board is a skill and no tier may invoke it"
            )


def test_review_and_report_verbs_are_pure_python():
    """The CLI's quality verbs resolve to offline code paths.

    `review --ingest` is model-FACING (it validates a board deliverable)
    but never model-CALLING: it reads a file the skill already wrote.
    """
    from orgsmith.review import run_report, run_review_ingest, run_sample

    for fn in (run_report, run_review_ingest, run_sample):
        module = Path(fn.__module__.replace(".", "/") + ".py")
        assert (REPO / module).exists()
        for name in _imported_roots(REPO / module):
            assert name.split(".")[0] not in _OFFLINE_BANNED


def test_no_tier_reads_a_model_api_key():
    """Keyless by design: nothing in the package or the suite may look for
    a provider credential."""
    key_names = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "CLAUDE_API_KEY")
    for base in ("orgsmith", "tests"):
        for path in sorted((REPO / base).rglob("*.py")):
            if path.resolve() == Path(__file__).resolve():
                continue
            text = path.read_text(encoding="utf-8")
            for key in key_names:
                assert key not in text, f"{path.name} reads {key}"
