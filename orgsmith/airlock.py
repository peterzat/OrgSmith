"""Work-order plumbing shared by every model touchpoint.

The airlock invariants live here:
- single-outstanding stages (foundation enrichment) keep at most ONE
  outstanding work order, and re-emitting without an intervening ingest
  returns the SAME work order (no duplicates, safe to re-run after a kill);
- the author stage is concurrent (M10 parallel authoring): several batches
  may be outstanding at once, each covering a disjoint set of documents, so
  the invariant there is that no two outstanding orders overlap (enforced by
  the caller choosing a batch disjoint from `state.covered_docs()`);
- work orders are self-contained JSON files under `-metadata/workorders/`
  and are kept after ingest as an audit trail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from .naming import contained_join, strip_control
from .paths import OrgPaths
from .schemas import WorkOrder, write_model
from .state import BatchRef, OrgState, save_state


def _next_serial(workorders_dir: Path, stage: str) -> int:
    """One past the highest serial on disk for `stage`.

    The max, not the count. Counting reuses a serial after any deletion and
    the reused name then overwrites the order that survived, silently, taking
    the audit trail and `state.author_batches` (keyed by work-order id) out of
    agreement with it. Gaps are fine; reuse is not. Names that do not parse are
    ignored rather than fatal, since the directory is an audit trail and may
    collect strays.
    """
    prefix = f"{stage}-"
    highest = 0
    for path in workorders_dir.glob(f"{prefix}*.json"):
        tail = path.name[len(prefix) : -len(".json")]
        # isascii() before isdigit(): "²".isdigit() is True and int("²")
        # raises, and "٣" parses as 3, so isdigit() alone both crashes on a
        # stray and silently accepts one. This must tolerate strays, not
        # interpret them.
        if tail.isascii() and tail.isdigit():
            highest = max(highest, int(tail))
    return highest + 1


def _claim_work_order_path(workorders_dir: Path, stage: str, serial: int) -> Path:
    """Create the file for a new order, or fail. Never returns a path that
    something else already holds.

    The claim is the creation: `O_CREAT | O_EXCL` via `touch(exist_ok=False)`,
    not an `exists()` check followed by a write. The check-then-write version
    of this function was a time-of-check/time-of-use hole -- two dispatchers
    could both see the serial free, both proceed, and one would silently
    destroy the other, which is the exact loss `_next_serial` exists to
    prevent. The kernel decides who wins here, so the loser fails loudly.

    `build()` runs before this is called, so a failed build leaves nothing
    behind. A crash between the claim and the write leaves an empty file,
    which costs one serial and is why gaps are blessed.
    """
    path = workorders_dir / f"{stage}-{serial:04d}.json"
    try:
        path.touch(exist_ok=False)
    except FileExistsError:
        raise SystemExit(
            f"{stage}: refusing to overwrite existing work order {path}; "
            f"serial {serial:04d} was computed as free but is not. Check for "
            f"a concurrent dispatcher or a hand-edited workorders directory."
        ) from None
    return path


def outstanding_work_order(paths: OrgPaths, state: OrgState, stage: str) -> Path | None:
    name = state.outstanding.get(stage)
    if name is None:
        return None
    try:
        path = contained_join(paths.workorders_dir, name)
    except ValueError as exc:
        raise SystemExit(
            f"state names an unsafe work order for stage {stage!r}: {exc}"
        ) from None
    if not path.exists():
        raise SystemExit(
            f"state says work order {name!r} is outstanding for stage "
            f"{stage!r} but {strip_control(str(path))} is missing; restore it "
            f"or clear the outstanding entry in {paths.state_json}"
        )
    return path


def emit_work_order(
    paths: OrgPaths,
    state: OrgState,
    stage: str,
    build: Callable[[str], WorkOrder],
) -> Path:
    """Return the outstanding work order for `stage`, creating it via
    `build(work_order_id)` only when none is pending."""
    existing = outstanding_work_order(paths, state, stage)
    if existing is not None:
        print(f"{stage}: outstanding work order (re-emitted): {existing}")
        return existing

    paths.workorders_dir.mkdir(parents=True, exist_ok=True)
    serial = _next_serial(paths.workorders_dir, stage)
    wo_id = f"wo:{stage}:{serial:04d}"
    order = build(wo_id)
    path = _claim_work_order_path(paths.workorders_dir, stage, serial)
    write_model(path, order)
    state.outstanding[stage] = path.name
    save_state(paths, state)
    print(f"{stage}: work order -> {path}")
    return path


def match_outstanding(
    paths: OrgPaths, state: OrgState, stage: str, work_order_id: str
) -> WorkOrder:
    """Load the outstanding work order and check the deliverable points at it."""
    path = outstanding_work_order(paths, state, stage)
    if path is None:
        raise SystemExit(
            f"ingest: no outstanding {stage} work order; emit one first"
        )
    order = WorkOrder.model_validate_json(path.read_text("utf-8"))
    if order.id != work_order_id:
        raise SystemExit(
            f"ingest: deliverable answers work order {work_order_id!r} but "
            f"{order.id!r} is outstanding ({path.name})"
        )
    return order


def clear_outstanding(state: OrgState, stage: str) -> None:
    state.outstanding.pop(stage, None)


# --- concurrent author stage (M10 parallel authoring) ----------------------
# The author stage does not use `outstanding`; it tracks a set of concurrent
# batches in `state.author_batches`. These three functions are its emit /
# match / clear, mirroring the single-outstanding trio above.


def emit_author_batch(
    paths: OrgPaths,
    state: OrgState,
    build: Callable[[str], WorkOrder],
    doc_ids: Iterable[str],
) -> Path:
    """Emit a NEW authoring work order covering `doc_ids` and record it in
    `state.author_batches`. Unlike `emit_work_order`, this always creates a
    fresh order: the caller has already chosen a batch disjoint from every
    outstanding one, so concurrent batches coexist without overlap.

    Serial numbering reads the work-order files on disk, so it stays
    deterministic as long as emission is sequential (the orchestrating skill
    calls this once per batch; only the model authoring runs concurrently).
    Two concurrent dispatchers would still race for a serial, and
    `_claim_work_order_path` is what decides that race in the kernel: both may
    compute the same number, only one creates the file, and the other exits
    rather than overwriting it.
    """
    paths.workorders_dir.mkdir(parents=True, exist_ok=True)
    serial = _next_serial(paths.workorders_dir, "author")
    wo_id = f"wo:author:{serial:04d}"
    order = build(wo_id)
    path = _claim_work_order_path(paths.workorders_dir, "author", serial)
    write_model(path, order)
    state.author_batches[wo_id] = BatchRef(
        workorder=path.name, doc_ids=list(doc_ids)
    )
    save_state(paths, state)
    print(f"author: work order -> {path}")
    return path


def match_author_batch(
    paths: OrgPaths, state: OrgState, work_order_id: str
) -> WorkOrder:
    """Load the outstanding author batch a deliverable answers, checking it is
    genuinely outstanding and its stored order points back at itself."""
    ref = state.author_batches.get(work_order_id)
    if ref is None:
        raise SystemExit(
            f"ingest: {work_order_id!r} is not an outstanding author batch; "
            f"emit one first or inspect {paths.state_json}"
        )
    try:
        path = contained_join(paths.workorders_dir, ref.workorder)
    except ValueError as exc:
        raise SystemExit(
            f"state names an unsafe author batch work order: {exc}"
        ) from None
    if not path.exists():
        raise SystemExit(
            f"state says author batch {ref.workorder!r} is outstanding but "
            f"{strip_control(str(path))} is missing; restore it or clear the "
            f"entry in {paths.state_json}"
        )
    order = WorkOrder.model_validate_json(path.read_text("utf-8"))
    if order.id != work_order_id:
        raise SystemExit(
            f"ingest: deliverable answers {work_order_id!r} but the stored "
            f"order is {order.id!r} ({ref.workorder!r})"
        )
    return order


def clear_author_batch(state: OrgState, work_order_id: str) -> None:
    state.author_batches.pop(work_order_id, None)
