"""author --next-batch: the next authoring work order.

Batches are short docs grouped by engagement so one ledger slice serves
the whole batch. The work order is self-contained: briefs carry personas,
engagement summaries, and fact ids with hints, but never fact values; the
model must place `{{fact:...}}` placeholders it cannot resolve itself.
"""

from __future__ import annotations

from datetime import date

from ..airlock import emit_work_order
from ..artifacts import load_charter, load_engagements, load_foundation, load_manifest
from ..fabric.engagements import employer_at
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
    "briefing_deck": (
        "Client briefing deck. Structure strictly as slides: each slide is "
        "one heading block (level 1, the slide title) followed by one list "
        "block of 3-5 tight bullets (or one short paragraph). Open with a "
        "title slide for the engagement, close with a next-steps slide. "
        "4-6 slides total. No sigblock."
    ),
    "engagement_email": (
        "Plain-text status email within the engagement thread: a greeting "
        "line naming the recipients, 2-3 short paragraphs of progress and "
        "asks, a sign-off line with the sender's name. The subject lives in "
        "the message header, not the body. No sigblock."
    ),
}

_TARGET_WORDS = {
    "engagement_letter": 350,
    "kickoff_memo": 240,
    "meeting_minutes": 220,
    "status_report": 300,
    "company_overview": 320,
    "briefing_deck": 180,
    "engagement_email": 130,
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
  {{fact:<id>}} at least once in that doc's text, where <id> is the
  briefed id verbatim including its `f:` prefix (e.g.
  {{fact:f:E-2019-001.start}}). You do not know fact values; never write
  a number, date, or name in place of a placeholder.
- Use only placeholders for fact ids briefed on that document.
- Do not invent people, organizations, addresses, amounts, or dates.
  People and their titles come from the briefs; the org narrative sets
  tone only.
- Every entry in a doc's `mentions` list must appear VERBATIM (the exact
  `surface` string) somewhere in that doc's text. Sigblock signers count
  as mentions of themselves. Short surfaces are nicknames: work them into
  prose naturally ("...as {{nickname}} noted..."), alongside, not instead
  of, the person's full name.
- Write plain, era-appropriate business prose in the org's voice.
"""


def _brief_summary(eng) -> str:
    """Engagement context WITHOUT ledger values. The ledger summary carries
    the exact fee and dates; briefs must never leak what a placeholder will
    resolve to."""
    months = max(1, round((eng.end - eng.start).days / 30))
    return (
        f"{eng.title}, running about {months} months. Commercial terms and "
        f"dates are briefed as fact placeholders only."
    )


def _brief_person(
    foundation: Foundation, pid: str, at: date | None = None
) -> PersonBrief:
    """`at` resolves an external person's employer (the brief's dept
    line) as of that date, so era-appropriate briefs match what render
    puts in the sigblock; None keeps the current employer."""
    if pid.startswith("p:"):
        p = foundation.person(pid)
        return PersonBrief(
            id=p.id, name=p.name, title=p.title, dept=p.dept, persona=p.persona
        )
    xp = next(x for x in foundation.external_people if x.id == pid)
    org_id = employer_at(xp, at) if at is not None else xp.org
    org = next(o for o in foundation.external_orgs if o.id == org_id)
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

    aff_docs = charter.graph_targets.affiliations_in_docs

    def brief_at(entry) -> date | None:
        return entry.date if aff_docs else None

    def build(wo_id: str) -> WorkOrder:
        briefs = []
        for entry in batch:
            eng = engagements.get(entry.engagement) if entry.engagement else None
            # Non-body facts are never briefed: the model must not place
            # their placeholders (render owns signature-page injection, the
            # filename owns filename dates) and must not learn they exist.
            locations = {k.fact_id: k.location for k in entry.key_facts}
            body_refs = [
                ref
                for ref in entry.facts_refs
                if locations.get(ref, "body") == "body"
            ]
            guidance = _GENRE_GUIDANCE[entry.genre]
            if any(loc == "signature_page" for loc in locations.values()):
                guidance += (
                    " Commercial fee terms are executed on the signature "
                    "page by counsel; do not state, estimate, or reference "
                    "the fee amount anywhere in the text."
                )
            if any(loc == "filename" for loc in locations.values()):
                guidance += (
                    " Do not state the meeting date anywhere in the text, "
                    "in any format, and do not include a sigblock; this "
                    "record is dated by its filename only."
                )
            briefs.append(
                DocBrief(
                    doc_id=entry.doc_id,
                    title=entry.title,
                    genre=entry.genre,
                    date=entry.date,
                    authors=[
                        _brief_person(foundation, a, brief_at(entry))
                        for a in entry.authors
                    ],
                    participants=[
                        _brief_person(foundation, p, brief_at(entry))
                        for p in entry.participants
                    ],
                    engagement_summary=_brief_summary(eng) if eng else "",
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
                        for ref in body_refs
                    ],
                    mentions=list(entry.mentions),
                    target_words=_TARGET_WORDS[entry.genre],
                    guidance=guidance,
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
