"""foundation --emit-context: the persona-enrichment work order."""

from __future__ import annotations

from ..airlock import emit_work_order
from ..artifacts import load_charter, load_foundation
from ..paths import OrgPaths
from ..schemas import SCHEMA_IDS, PersonBrief, WorkOrder
from ..state import load_state, require_stages

_INSTRUCTIONS = """\
Write a persona for EVERY person listed in `people`, as JSON matching the
deliverable schema:

  {"schema_id": "%(schema)s",
   "work_order_id": "%(wo)s",
   "personas": [{"person_id": "p:...", "persona": "..."}, ...]}

Persona = 2-4 sentences of working style, background, and voice that later
document authoring can lean on (at least 40 characters). Ground it in the
org narrative and the person's title. Do NOT invent or restate structured
facts: no dates, numbers, employers, addresses, or new people. Do not
change or echo any other field; ids must match the roster exactly, one
entry per person, no extras.
"""


def run_emit_context(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "foundation")
    if state.stage_done("foundation_enrich"):
        print("foundation: enrichment already merged, nothing to emit")
        return 0
    charter = load_charter(paths)
    foundation = load_foundation(paths)

    def build(wo_id: str) -> WorkOrder:
        return WorkOrder(
            id=wo_id,
            stage="foundation",
            slug=charter.slug,
            org_name=charter.name,
            org_type=charter.org_type,
            narrative=charter.narrative,
            instructions=_INSTRUCTIONS
            % {"schema": SCHEMA_IDS["enrichment_deliverable"], "wo": wo_id},
            people=[
                PersonBrief(
                    id=p.id, name=p.name, title=p.title, dept=p.dept, persona=""
                )
                for p in foundation.people
            ],
            deliverable_schema=SCHEMA_IDS["enrichment_deliverable"],
        )

    emit_work_order(paths, state, "foundation", build)
    return 0
