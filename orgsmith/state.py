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
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from .paths import OrgPaths
from .schemas import SCHEMA_IDS, Generator, StrictModel, write_model

# A work-order filename as stored in state: one safe path component living
# directly under workorders/. The pattern rejects path separators, "..",
# absolute paths, and control characters at load (M13; SECURITY.md 2026-07-17c),
# so a tampered state.json cannot steer a file read outside workorders_dir, and
# a control character cannot ride a name into a terminal message. The airlock
# also guards the join at the sink (naming.contained_join), so the containment
# holds even if this pattern is bypassed. Admits every name the generator
# writes: "<stage>-NNNN.json" (e.g. "foundation-0001.json", "author-0003.json").
WorkOrderName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]+\.json$")]

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


class BatchRef(StrictModel):
    """One outstanding authoring work order (M10 parallel authoring).

    The author stage dispatches concurrent batches; each is tracked here by
    its work_order_id until its deliverable is ingested. `workorder` is the
    file under workorders/; `doc_ids` are the batchable docs it covers, kept
    so `--next-batch` can exclude in-flight docs without loading every order.
    """

    workorder: WorkOrderName
    doc_ids: list[str] = Field(default_factory=list)


class DocState(StrictModel):
    authored_hash: str | None = None
    rendered_hash: str | None = None
    # Content basis the last render consumed (authored hash, or ledger hash
    # for static docs); rendering skips docs whose basis is unchanged.
    rendered_from: str | None = None
    rev: int = 0


class OrgState(StrictModel):
    schema_id: Literal["orgsmith/state@1"] = SCHEMA_IDS["state"]
    slug: str
    stages: dict[str, StageState] = {}
    docs: dict[str, DocState] = {}
    # stage -> workorders/<file>; at most one outstanding per stage. Governs
    # the single-outstanding stages (foundation enrichment). The author stage
    # is concurrent and lives in `author_batches` instead.
    outstanding: dict[str, WorkOrderName] = {}
    # Author stage supports concurrent outstanding batches (M10 parallel
    # authoring): work_order_id -> BatchRef. Empty by default so every
    # committed state.json still loads under the unchanged orgsmith/state@1 id.
    author_batches: dict[str, BatchRef] = Field(default_factory=dict)
    probes: dict[str, str] = {}
    fallbacks: list[str] = Field(default_factory=list)
    # work_order_id -> the model/effort that answered it. Self-reported by
    # the dispatching skill: a record for `report` to surface, never an
    # oracle for a validator to trust. Absent by default, which is why
    # every org authored before it existed still loads.
    generators: dict[str, Generator] = Field(default_factory=dict)

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

    def covered_docs(self) -> set[str]:
        """doc_ids currently claimed by an outstanding author batch, so a new
        batch is chosen disjoint from every in-flight one."""
        return {d for ref in self.author_batches.values() for d in ref.doc_ids}


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


# Depth per locked directory, so a stage that calls another stage in the same
# process re-enters instead of deadlocking on its own lock: flock locks belong
# to an open file description, and a second open of the same directory in one
# process would wait on the first.
_HELD: dict[str, int] = {}


@contextmanager
def state_lock(paths: OrgPaths):
    """Exclusive advisory lock over one org's `state.json` read-modify-write.

    Every stage loads state, works, and saves it whole, so two processes
    overlapping would each save over the other's update. M10 made that safe
    by convention: `/forge` runs every `--ingest` itself, one at a time, and
    tells its workers never to ingest. That is a rule in a prompt. This makes
    it a property of the CLI (M17d): a second writer on the same org waits.

    The lock is a `flock` on the org's metadata directory itself, so it leaves
    no lock file in a committed tree. Before the first stage has created that
    directory there is no state to race on, and nothing is locked. Advisory
    and POSIX-only; on a platform without `fcntl` it is a no-op, which is the
    behavior before this existed.
    """
    try:
        import fcntl
    except ImportError:  # pragma: no cover - non-POSIX
        yield
        return
    target = paths.meta_dir
    if not target.is_dir():
        yield
        return
    key = str(target.resolve())
    if _HELD.get(key):
        _HELD[key] += 1
        try:
            yield
        finally:
            _HELD[key] -= 1
        return
    fd = os.open(target, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        _HELD[key] = 1
        try:
            yield
        finally:
            _HELD[key] = 0
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def require_stages(state: OrgState, *names: str) -> None:
    """Fail loudly when an upstream stage has not completed."""
    missing = [n for n in names if not state.stage_done(n)]
    if missing:
        raise SystemExit(
            f"upstream stage(s) not done: {', '.join(missing)}. "
            f"Run them first (see `python -m orgsmith status {state.slug}`)."
        )
