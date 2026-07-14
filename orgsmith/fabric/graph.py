"""Canonical people/org graph derived from foundation + engagements.

M1 keeps this minimal (entities plus reports_to/works_at/client_of/
participant edges); graph targets and mention maps deepen in M2/M3.
"""

from __future__ import annotations

from ..schemas import (
    Charter,
    EngagementsLedger,
    Foundation,
    GraphEdge,
    GraphLedger,
)


def build_graph(
    charter: Charter, foundation: Foundation, engagements: EngagementsLedger
) -> GraphLedger:
    self_org = f"x:{charter.slug}"
    entities = (
        [self_org]
        + [p.id for p in foundation.people]
        + [o.id for o in foundation.external_orgs]
        + [p.id for p in foundation.external_people]
    )

    edges: list[GraphEdge] = []
    for p in foundation.people:
        if p.reports_to:
            edges.append(GraphEdge(src=p.id, dst=p.reports_to, kind="reports_to"))
        edges.append(
            GraphEdge(
                src=p.id, dst=self_org, kind="works_at", start=p.employment.start
            )
        )
    for xp in foundation.external_people:
        edges.append(GraphEdge(src=xp.id, dst=xp.org, kind="works_at"))
    for eng in engagements.engagements:
        edges.append(
            GraphEdge(src=eng.client, dst=self_org, kind="client_of", start=eng.start)
        )
        for pid in eng.internal_participants + eng.external_participants:
            edges.append(
                GraphEdge(
                    src=pid, dst=eng.id, kind="participant",
                    start=eng.start, end=eng.end,
                )
            )
    return GraphLedger(slug=charter.slug, entities=entities, edges=edges)
