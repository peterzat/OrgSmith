"""Typed load/save for every inter-stage artifact.

Stages exchange data only through these helpers, so schema validation
happens at every boundary in both directions.
"""

from __future__ import annotations

import json

from .naming import check_relpath
from .paths import OrgPaths
from .schemas import (
    Charter,
    EngagementsLedger,
    FinanceLedger,
    Foundation,
    GraphLedger,
    ManifestEntry,
    WorkOrder,
)


def _read(path) -> str:
    if not path.exists():
        raise SystemExit(f"missing artifact: {path} (run the producing stage first)")
    return path.read_text("utf-8")


def load_charter(paths: OrgPaths) -> Charter:
    return Charter.model_validate_json(_read(paths.charter_json))


def load_foundation(paths: OrgPaths) -> Foundation:
    return Foundation.model_validate_json(_read(paths.foundation_json))


def load_finance(paths: OrgPaths) -> FinanceLedger:
    return FinanceLedger.model_validate_json(_read(paths.finance_json))


def load_engagements(paths: OrgPaths) -> EngagementsLedger:
    return EngagementsLedger.model_validate_json(_read(paths.engagements_json))


def load_graph(paths: OrgPaths) -> GraphLedger:
    return GraphLedger.model_validate_json(_read(paths.graph_json))


def load_mention_map(paths: OrgPaths):
    """MentionMap, or None for orgs generated before mention ground truth
    existed (the committed v1 dev-mini). Callers must handle None."""
    from .schemas import MentionMap

    if not paths.mention_map_json.exists():
        return None
    return MentionMap.model_validate_json(paths.mention_map_json.read_text("utf-8"))


def load_manifest(paths: OrgPaths) -> list[ManifestEntry]:
    entries = []
    for line in _read(paths.manifest_jsonl).splitlines():
        if line.strip():
            entry = ManifestEntry.model_validate_json(line)
            # Re-validate at every load so consumers that join entry.path to
            # the filesystem (render, validate) reject tampered manifests.
            problems = check_relpath(entry.path)
            if problems:
                raise SystemExit(f"manifest: unsafe path: {problems}")
            entries.append(entry)
    return entries


def save_manifest(paths: OrgPaths, entries: list[ManifestEntry]) -> None:
    paths.docplan_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(e.model_dump(mode="json"), ensure_ascii=False) for e in entries
    ]
    paths.manifest_jsonl.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_work_order(path) -> WorkOrder:
    return WorkOrder.model_validate_json(_read(path))
