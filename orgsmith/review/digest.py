"""review --digest: prove the board left the org as it found it (M17d).

The board is read-only by instruction: `/forge-review` and every
`forge-reviewer` are told never to edit a ledger, a manifest, a DocIR file, a
rendered document, `state.json`, or a recipe. An instruction is advice. This
is the check: the chair records a digest of everything the board may read
before dispatching anyone and verifies it after, so a reviewer that "fixed" a
sentence it was reviewing is caught rather than trusted.

The digest covers the recipe, the rendered share, and the whole `-metadata/`
tree, and excludes exactly what the board is allowed to write: `review/`
(the sample, metrics, reply files, and merged findings) and
`GENERATION-REPORT.md` (which `report` rewrites after the merge). Each file
contributes its path relative to the repo root and its own sha256, in sorted
order, so the result is independent of filesystem iteration order.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from ..paths import OrgPaths


def _allowed_writes(paths: OrgPaths) -> tuple[Path, Path]:
    return paths.review_dir.resolve(), paths.generation_report_md.resolve()


def digested_files(paths: OrgPaths) -> list[Path]:
    """Every file the digest covers, sorted by repo-relative path."""
    review_dir, report = _allowed_writes(paths)
    files: list[Path] = []
    for top in (paths.recipe_dir, paths.share_dir, paths.meta_dir):
        if not top.is_dir():
            continue
        for path in top.rglob("*"):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved == report or review_dir in resolved.parents:
                continue
            files.append(path)
    root = paths.root.resolve()
    return sorted(files, key=lambda p: p.resolve().relative_to(root).as_posix())


def org_digest(paths: OrgPaths) -> str:
    root = paths.root.resolve()
    outer = hashlib.sha256()
    for path in digested_files(paths):
        rel = path.resolve().relative_to(root).as_posix()
        inner = hashlib.sha256(path.read_bytes()).hexdigest()
        outer.update(f"{rel}\0{inner}\n".encode("utf-8"))
    return outer.hexdigest()


def run_digest(paths: OrgPaths, verify: str | None = None) -> int:
    digest = org_digest(paths)
    if verify is None:
        print(digest)
        return 0
    if digest == verify.strip():
        print(f"review: org unchanged ({len(digested_files(paths))} files, {digest[:16]})")
        return 0
    print(
        f"review: THE ORG CHANGED during the board (was {verify.strip()[:16]}, "
        f"now {digest[:16]}). The board is read-only: find what moved "
        f"(`git status` for a committed org) and restore it before trusting "
        f"any finding."
    )
    return 1
