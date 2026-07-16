"""review --ingest: validate and merge one reviewer's findings.

The same contract as `author --ingest`, for the same reason: the board is a
model pass, so its deliverable is untrusted input. Every problem across the
file is reported at once and nothing is written unless the file is clean.

Findings are a record for a human to read. They gate nothing, and no
validator rule may reference them.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from ..artifacts import load_manifest
from ..naming import strip_control
from ..paths import OrgPaths
from ..schemas import ReviewFindings, dump_json


def findings_path(paths: OrgPaths, dimension: str) -> Path:
    return paths.review_findings_dir / f"{dimension}.json"


def _warn_unreadable(path: Path, err: Exception) -> None:
    """A findings file that will not load is evidence, not a skip.

    Dropping it silently would under-report the board a user just paid for
    and would disable cross-dimension duplicate-id detection without a
    word. Name the file so the count is never quietly wrong.
    """
    print(
        f"review: WARNING: {strip_control(path.name, keep='')} did not load "
        f"({type(err).__name__}); its findings are absent from the report and "
        f"cannot be checked for duplicate ids."
    )


def load_findings(paths: OrgPaths) -> list:
    """Every finding ingested so far, across dimensions, in a stable order."""
    out = []
    if not paths.review_findings_dir.exists():
        return out
    for path in sorted(paths.review_findings_dir.glob("*.json")):
        try:
            batch = ReviewFindings.model_validate_json(path.read_text("utf-8"))
        except (OSError, ValidationError) as err:
            _warn_unreadable(path, err)
            continue
        out.extend(batch.findings)
    return out


def _other_dimension_ids(paths: OrgPaths, dimension: str) -> dict[str, str]:
    """Finding id -> dimension, for findings already stored under a
    different dimension. Re-ingesting one dimension replaces its own file,
    so its ids never collide with themselves."""
    seen: dict[str, str] = {}
    if not paths.review_findings_dir.exists():
        return seen
    for path in sorted(paths.review_findings_dir.glob("*.json")):
        if path.name == f"{dimension}.json":
            continue
        try:
            batch = ReviewFindings.model_validate_json(path.read_text("utf-8"))
        except (OSError, ValidationError) as err:
            _warn_unreadable(path, err)
            continue
        for finding in batch.findings:
            seen.setdefault(finding.id, batch.dimension)
    return seen


def run_ingest(paths: OrgPaths, deliverable_path: Path) -> int:
    if not deliverable_path.exists():
        raise SystemExit(f"review --ingest: no such file {deliverable_path}")
    try:
        batch = ReviewFindings.model_validate_json(
            deliverable_path.read_text("utf-8")
        )
    except ValidationError as err:
        # Unknown dimensions and severities land here: both are Literals, so
        # pydantic reports every bad value in the file in one pass.
        print("review --ingest: findings rejected (schema):")
        print(strip_control(str(err)))
        return 1

    problems: list[str] = []
    if batch.slug != paths.slug:
        problems.append(
            f"findings are for slug {batch.slug!r}, not {paths.slug!r}"
        )

    known_docs = {e.doc_id for e in load_manifest(paths)}
    seen_ids: set[str] = set()
    elsewhere = _other_dimension_ids(paths, batch.dimension)
    for finding in batch.findings:
        if finding.id in seen_ids:
            problems.append(f"duplicate finding id {finding.id}")
        seen_ids.add(finding.id)
        if finding.id in elsewhere:
            problems.append(
                f"finding id {finding.id} already ingested under dimension "
                f"{elsewhere[finding.id]}"
            )
        for doc_id in finding.docs:
            if doc_id not in known_docs:
                problems.append(
                    f"{finding.id}: doc {doc_id} is not in the manifest"
                )

    if problems:
        print("review --ingest: findings rejected:")
        for p in problems:
            # Problem strings embed deliverable-controlled text (finding
            # ids, doc ids). One problem is one line: keep="" so an embedded
            # newline cannot forge a second line of output, and no escape
            # sequence can rewrite what was already printed.
            print(f"  - {strip_control(p, keep='')}")
        return 1

    paths.review_findings_dir.mkdir(parents=True, exist_ok=True)
    target = findings_path(paths, batch.dimension)
    target.write_text(dump_json(batch), encoding="utf-8")
    print(
        f"review --ingest: merged {len(batch.findings)} findings "
        f"({batch.dimension}) -> {target}"
    )
    return 0
