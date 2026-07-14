"""Checkpoint/resume state for one org.

state.json is committed with the org and is the single source of resume
truth: per-stage completion, per-doc content hashes, at most one
outstanding work order per stage, and capability-probe results. It is a
pure record of file-derived facts; it deliberately contains no timestamps
so that regeneration with the same inputs is byte-stable.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from .paths import OrgPaths
from .schemas import SCHEMA_IDS, StrictModel, write_model

STAGES = [
    "charter",
    "foundation",
    "foundation_enrich",
    "fabric",
    "docplan",
    "author",
    "render",
    "assemble",
]


class StageState(StrictModel):
    status: Literal["pending", "done"] = "pending"
    inputs_hash: str | None = None


class DocState(StrictModel):
    authored_hash: str | None = None
    rendered_hash: str | None = None
    rev: int = 0


class OrgState(StrictModel):
    schema_id: Literal["orgsmith/state@1"] = SCHEMA_IDS["state"]
    slug: str
    stages: dict[str, StageState] = {}
    docs: dict[str, DocState] = {}
    # stage -> workorders/<file>; at most one outstanding per stage
    outstanding: dict[str, str] = {}
    probes: dict[str, str] = {}
    fallbacks: list[str] = Field(default_factory=list)

    def stage(self, name: str) -> StageState:
        if name not in STAGES:
            raise KeyError(f"unknown stage {name!r}")
        return self.stages.get(name, StageState())

    def stage_done(self, name: str) -> bool:
        return self.stage(name).status == "done"

    def mark_done(self, name: str, inputs_hash: str | None = None) -> None:
        if name not in STAGES:
            raise KeyError(f"unknown stage {name!r}")
        self.stages[name] = StageState(status="done", inputs_hash=inputs_hash)

    def doc(self, doc_id: str) -> DocState:
        return self.docs.setdefault(doc_id, DocState())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_state(paths: OrgPaths) -> OrgState:
    if paths.state_json.exists():
        return OrgState.model_validate_json(paths.state_json.read_text("utf-8"))
    return OrgState(slug=paths.slug)


def save_state(paths: OrgPaths, state: OrgState) -> None:
    write_model(paths.state_json, state)


def require_stages(state: OrgState, *names: str) -> None:
    """Fail loudly when an upstream stage has not completed."""
    missing = [n for n in names if not state.stage_done(n)]
    if missing:
        raise SystemExit(
            f"upstream stage(s) not done: {', '.join(missing)}. "
            f"Run them first (see `python -m orgsmith status {state.slug}`)."
        )
