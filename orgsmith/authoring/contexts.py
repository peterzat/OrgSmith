"""author --next-batch: the next authoring work order.

Batches are short docs grouped by engagement so one ledger slice serves
the whole batch. The work order is self-contained: briefs carry personas,
engagement summaries, and fact ids with hints, but never fact values; the
model must place `{{fact:...}}` placeholders it cannot resolve itself.
"""

from __future__ import annotations

from ..airlock import emit_work_order
from ..artifacts import load_charter, load_engagements, load_foundation, load_manifest
from ..paths import OrgPaths
from ..schemas import (
    SCHEMA_IDS,
    DocBrief,
    FactBrief,
    Foundation,
    ManifestEntry,
    PersonBrief,
    WorkOrder,
)
from ..state import load_state, require_stages, save_state

BATCH_SIZE = 6

_GENRE_GUIDANCE = {
    "engagement_letter": (
        "Formal letter on firm letterhead confirming the engagement: "
        "scope, approach, team, fee and start date, closing. End with a "
        "sigblock block signed by the letter's author and the client "
        "contact. 3-6 paragraphs."
    ),
    "kickoff_memo": (
        "Internal memo to the engagement team. Open with a short paragraph "
        "on objectives, then a list of workstreams, then next steps."
    ),
    "meeting_minutes": (
        "Minutes of a working session: a list block naming every attendee "
        "(full names), discussion summary paragraphs, and a table or list "
        "of action items with owners."
    ),
    "status_report": (
        "Progress report for the client executive: status summary, "
        "accomplishments this period, upcoming work, risks. Reference the "
        "engagement budget where the fee fact is briefed."
    ),
    "company_overview": (
        "One-page firm overview: what the firm does, service lines, "
        "representative client work. Written in the firm's own voice."
    ),
}

_TARGET_WORDS = {
    "engagement_letter": 350,
    "kickoff_memo": 240,
    "meeting_minutes": 220,
    "status_report": 300,
    "company_overview": 320,
}

_INSTRUCTIONS = """\
Author every document briefed in `docs`, as JSON matching the deliverable
schema:

  {"schema_id": "%(schema)s",
   "work_order_id": "%(wo)s",
   "docs": [{"schema_id": "orgsmith/docir@1", "doc_id": "d:....",
             "blocks": [...]}, ...]}

Block kinds: heading (text, level), paragraph (text), list (items),
table (header, rows), sigblock (signers = person ids from the brief).

Hard rules:
- One DocIR per brief; doc_ids must match the work order exactly.
- Every fact id briefed for a doc MUST appear as a literal placeholder
  {{fact:<id>}} at least once in that doc's text. You do not know fact
  values; never write a number, date, or name in place of a placeholder.
- Use only placeholders for fact ids briefed on that document.
- Do not invent people, organizations, addresses, amounts, or dates.
  People and their titles come from the briefs; the org narrative sets
  tone only.
- Write plain, era-appropriate business prose in the org's voice.
"""


def _brief_person(foundation: Foundation, pid: str) -> PersonBrief:
    if pid.startswith("p:"):
        p = foundation.person(pid)
        return PersonBrief(
            id=p.id, name=p.name, title=p.title, dept=p.dept, persona=p.persona
        )
    xp = next(x for x in foundation.external_people if x.id == pid)
    org = next(o for o in foundation.external_orgs if o.id == xp.org)
    return PersonBrief(id=xp.id, name=xp.name, title=xp.title, dept=org.name)


def pick_batch(manifest: list[ManifestEntry], state) -> list[ManifestEntry]:
    """Unauthored batchable docs from the first pending engagement group."""
    pending = [
        e
        for e in manifest
        if e.authoring == "batchable" and state.doc(e.doc_id).authored_hash is None
    ]
    if not pending:
        return []
    group_key = pending[0].engagement or "firm"
    batch = [e for e in pending if (e.engagement or "firm") == group_key]
    return batch[:BATCH_SIZE]


def run_next_batch(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "docplan", "foundation_enrich")

    charter = load_charter(paths)
    foundation = load_foundation(paths)
    engagements = {e.id: e for e in load_engagements(paths).engagements}
    facts = {
        f.id: f for e in engagements.values() for f in e.facts
    }
    manifest = load_manifest(paths)

    batch = pick_batch(manifest, state)
    if not batch:
        if "author" in state.outstanding:
            raise SystemExit(
                "author: outstanding work order covers no pending docs; "
                f"state is inconsistent, inspect {paths.state_json}"
            )
        state.mark_done("author")
        save_state(paths, state)
        print("author: all batchable docs authored")
        return 0

    def build(wo_id: str) -> WorkOrder:
        briefs = []
        for entry in batch:
            eng = engagements.get(entry.engagement) if entry.engagement else None
            briefs.append(
                DocBrief(
                    doc_id=entry.doc_id,
                    title=entry.title,
                    genre=entry.genre,
                    date=entry.date,
                    authors=[_brief_person(foundation, a) for a in entry.authors],
                    participants=[
                        _brief_person(foundation, p) for p in entry.participants
                    ],
                    engagement_summary=eng.summary if eng else "",
                    facts=[
                        FactBrief(
                            id=ref,
                            hint={
                                "money": "amount of money; place where the "
                                "figure belongs",
                                "date": "calendar date; place where the date "
                                "belongs",
                                "text": "proper name; place where the name "
                                "belongs",
                            }[facts[ref].kind],
                        )
                        for ref in entry.facts_refs
                    ],
                    target_words=_TARGET_WORDS[entry.genre],
                    guidance=_GENRE_GUIDANCE[entry.genre],
                )
            )
        return WorkOrder(
            id=wo_id,
            stage="author",
            slug=charter.slug,
            org_name=charter.name,
            org_type=charter.org_type,
            narrative=charter.narrative,
            instructions=_INSTRUCTIONS
            % {"schema": SCHEMA_IDS["authoring_deliverable"], "wo": wo_id},
            docs=briefs,
            deliverable_schema=SCHEMA_IDS["authoring_deliverable"],
        )

    emit_work_order(paths, state, "author", build)
    return 0
