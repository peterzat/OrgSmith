"""foundation --ingest: validate and merge persona enrichment.

Enrichment may fill persona prose and nothing else. The deliverable schema
carries only (person_id, persona) pairs and rejects unknown fields, so ids,
dates, and reporting lines are structurally out of reach; unknown or
missing person ids are rejected here.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from ..airlock import clear_outstanding, match_outstanding
from ..artifacts import load_foundation
from ..paths import OrgPaths
from ..schemas import EnrichmentDeliverable, write_model
from ..state import load_state, save_state


def run_ingest(paths: OrgPaths, deliverable_path: Path) -> int:
    state = load_state(paths)
    if not deliverable_path.exists():
        raise SystemExit(f"ingest: no such file {deliverable_path}")
    try:
        deliverable = EnrichmentDeliverable.model_validate_json(
            deliverable_path.read_text("utf-8")
        )
    except ValidationError as err:
        print(f"ingest: deliverable rejected (schema):\n{err}")
        return 1

    match_outstanding(paths, state, "foundation", deliverable.work_order_id)

    foundation = load_foundation(paths)
    roster_ids = [p.id for p in foundation.people]
    given = [e.person_id for e in deliverable.personas]

    problems = []
    if len(set(given)) != len(given):
        problems.append("duplicate person_id entries")
    unknown = sorted(set(given) - set(roster_ids))
    if unknown:
        problems.append(f"unknown person ids: {', '.join(unknown)}")
    missing = sorted(set(roster_ids) - set(given))
    if missing:
        problems.append(f"missing personas for: {', '.join(missing)}")
    if problems:
        print("ingest: deliverable rejected:")
        for p in problems:
            print(f"  - {p}")
        return 1

    by_id = {e.person_id: e.persona.strip() for e in deliverable.personas}
    for person in foundation.people:
        person.persona = by_id[person.id]
    write_model(paths.foundation_json, foundation)

    state.mark_done("foundation_enrich")
    clear_outstanding(state, "foundation")
    save_state(paths, state)
    print(f"ingest: merged {len(by_id)} personas into {paths.foundation_json}")
    return 0
