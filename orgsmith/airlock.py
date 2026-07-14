"""Work-order plumbing shared by every model touchpoint.

The airlock invariants live here:
- at most ONE outstanding work order per stage;
- re-emitting without an intervening ingest returns the SAME work order
  (no duplicates, safe to re-run after a killed session);
- work orders are self-contained JSON files under `-metadata/workorders/`
  and are kept after ingest as an audit trail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from .paths import OrgPaths
from .schemas import WorkOrder, write_model
from .state import OrgState, save_state


def outstanding_work_order(paths: OrgPaths, state: OrgState, stage: str) -> Path | None:
    name = state.outstanding.get(stage)
    if name is None:
        return None
    path = paths.workorders_dir / name
    if not path.exists():
        raise SystemExit(
            f"state says work order {name!r} is outstanding for stage "
            f"{stage!r} but {path} is missing; restore it or clear the "
            f"outstanding entry in {paths.state_json}"
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
    serial = len(list(paths.workorders_dir.glob(f"{stage}-*.json"))) + 1
    wo_id = f"wo:{stage}:{serial:04d}"
    order = build(wo_id)
    path = paths.workorders_dir / f"{stage}-{serial:04d}.json"
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
