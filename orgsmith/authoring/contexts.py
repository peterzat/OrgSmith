"""author --next-batch: the next authoring work order.

Batches are short docs grouped by engagement so one ledger slice serves
the whole batch. The work order is self-contained: briefs carry personas,
engagement summaries, and fact ids with hints, but never fact values; the
model must place `{{fact:...}}` placeholders it cannot resolve itself.
"""

from __future__ import annotations

from datetime import date

from ..airlock import emit_author_batch
from ..artifacts import load_charter, load_engagements, load_foundation, load_manifest
from ..docplan.registry import REGISTRY
from ..fabric.engagements import employer_at
from ..paths import OrgPaths
from ..seeds import rng
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
        "Formal engagement letter on firm letterhead confirming the "
        "engagement. Do NOT repeat the firm's name as a heading or title "
        "line: the letterhead already carries it. Open with the client's "
        "inside address and a salutation, then cover scope and approach, "
        "the team, and the fee and start date, followed by the standard "
        "terms a real engagement letter carries -- each as its own short "
        "headed paragraph: fees and payment, term and termination, "
        "confidentiality, limitation of liability, and governing law. Close "
        "with a signature request and end with a sigblock block signed by "
        "the letter's author and the client contact."
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
    "onboarding_record": (
        "Internal onboarding record welcoming a new hire to the firm: a "
        "short welcome, the person's role and where they sit in the "
        "practice, and first-period logistics and expectations. Name the "
        "new employee. 2-4 short paragraphs, no sigblock."
    ),
    "internal_email": (
        "A short, mundane internal email about firm logistics: scheduling, "
        "office admin, coverage, supplies -- NOT about any client "
        "engagement. One or two brief paragraphs. Name the colleagues "
        "involved. No client facts, no figures, no sigblock. The subject "
        "lives in the message header, not the body."
    ),
}

# The genre registry owns per-genre word targets (raised to real-world
# lengths at M9). Kept as a name here because review/corpus.py imports it as
# its fallback target table; both sides now read one source.
_TARGET_WORDS = {
    rule.genre: rule.target_words for rule in REGISTRY if rule.target_words
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
- If a doc carries `engagement_position`, honor it: it states where the
  document sits in its engagement's timeline. Do not describe progress or a
  phase inconsistent with it, and do not state the engagement's start or
  end date (those are fact placeholders, not yours to write).
- If a doc carries `firm_digest`, it is the ONLY firm history you may treat
  as established as of this document's date. Reference clients only through
  the placeholders it names; claim no engagement it does not list; present
  nothing later than this document as already true.
- If a doc carries `reporting_line`, the person reports to exactly who it
  names and to no one else. Do not name any other person or title as their
  supervisor; a reporting relationship is owned by the ledger, not invented.
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


def _engagement_position(eng, when: date) -> str:
    """Where `when` sits inside the engagement, in Python. rf:narr-2's exact
    failure (a deck 51 days into a 204-day program calling itself 'past its
    midpoint') stops being expressible because the author is told the position
    instead of inferring it from a start date it must not see.

    States elapsed days and a phase, never the start or end date: those are
    facts, and the airlock holds only if the brief carries structure, not
    values. A document dated before the letter's lead-in or after the close
    is clamped to the engagement's own window."""
    total = max(1, (eng.end - eng.start).days)
    elapsed = (when - eng.start).days
    pct = max(0, min(100, round(100 * elapsed / total)))
    if elapsed <= 0:
        phase = "at or before kickoff"
    elif elapsed >= total:
        phase = "at or after the close"
    elif pct < 40:
        phase = "in the early phase"
    elif pct <= 60:
        phase = "around the midpoint"
    else:
        phase = "in the later phase"
    return (
        f"This document is dated about {pct}% of the way through the "
        f"engagement ({phase}); it runs roughly {round(total / 30)} months "
        f"end to end. Do not describe progress inconsistent with that "
        f"position, and do not state the engagement's start or end date."
    )


def _firm_digest(all_engagements, when: date, book_is_sample: bool = False) -> str:
    """What the firm can truthfully say about itself AS OF `when`: how many
    engagements have begun, over how many years, and their clients BY FACT ID
    (never by value -- a client name is `f:E-....client` and would leak). This
    replaces handing the timeless recipe narrative to a dated overview
    (rf:narr-1), which invented a relationship because it had nothing true and
    a whole-arc brief.

    An overview dated early in the firm's life gets a short digest, which is
    the point: it cannot claim client work that has not happened yet.

    When `book_is_sample` (M12, engagement-ledger-reads-as-whole-book), the
    digest tells the author these engagements are a representative SAMPLE of a
    larger book, not the complete client list, so the overview stops claiming
    "the whole business" while the financial summary posts 20-60x the fee
    total. Default off keeps every existing brief byte-identical."""
    started = sorted(
        (e for e in all_engagements if e.start <= when), key=lambda e: e.start
    )
    if not started:
        return (
            "As of this document's date the firm has no completed client "
            "engagements to cite; describe the practice and its intent, and "
            "claim no specific client work."
        )
    years = sorted({e.start.year for e in started})
    span = f"{years[0]}" if len(years) == 1 else f"{years[0]}-{years[-1]}"
    client_refs = ", ".join(f"{{{{fact:f:{e.id}.client}}}}" for e in started)
    if book_is_sample:
        return (
            f"As of this document's date, the engagements you may cite are a "
            f"representative SAMPLE of the firm's client work across {span}, "
            f"not its complete book of business. Reference clients ONLY "
            f"through these placeholders, never by inventing a name: "
            f"{client_refs}. Present them as illustrative examples. Make NO "
            f"claim about the firm's total number of clients or engagements, "
            f"do not call this the whole business or a complete list, and do "
            f"not imply the firm's revenue is limited to these engagements. "
            f"Present nothing that post-dates this document as established."
        )
    return (
        f"As of this document's date the firm has begun {len(started)} "
        f"client engagement(s) across {span}. Reference clients ONLY through "
        f"these placeholders, never by inventing a name: {client_refs}. "
        f"Present nothing that post-dates this document as established, and "
        f"claim no engagement not listed here."
    )


_VOICE_REGISTERS = (
    "Write in a terse, factual register: short declarative sentences, few "
    "adjectives, no rhetorical flourishes.",
    "Write in a warm, narrative register: connective prose and some "
    "first-person-plural framing, without slogans.",
    "Write in a formal, precise register: careful qualifications and a "
    "measured tone, sparing with metaphor.",
    "Write in a plainspoken, direct register: concrete nouns and verbs, no "
    "epigrams or aphorisms.",
    "Write in a structured, enumerative register: name things in order with "
    "minimal figurative language.",
)

_VOICE_BANNED = (
    " Vary your openings, section names, and closings from what a template "
    "would produce. Do not open with 'Two asks. First... Second...'; do not "
    "structure the document as 'Workstreams' then 'Next Steps' then a closing "
    "aphorism; and avoid the 'rather X now than Y later' antithesis and "
    "formulaic epigrams."
)


def _author_voice(seed: int, person_id: str) -> str:
    """A per-author voice register drawn from a NEW seed stream keyed on the
    person (M12, cross-document-voice). Deterministic, so a re-authored brief
    reproduces; drawn only under the voice_diversify knob, so knob-off briefs
    are byte-identical."""
    return rng(seed, "author.voice", person_id).choice(_VOICE_REGISTERS)


_REGISTER_PROSE = {
    "crisp": "short declarative sentences, few adjectives, no flourishes",
    "warm": "connective prose, first-person-plural framing, no slogans",
    "formal": "careful qualifications and a measured, precise tone",
    "plainspoken": "concrete nouns and verbs, no epigrams",
    "structured": "ordered, enumerative prose with minimal figuration",
}


def _style_guidance(spec, genre: str) -> str:
    """M15 (persona voice v2): per-author brief guidance derived from the
    style-spec ledger. Auditable in retained work orders. Style owns the
    salutation prose and prose habits; the ledger owns signature facts, so
    every mail form ends before the auto-appended signature block."""
    text = (
        f" Your personal writing style, held consistently: a "
        f"{spec.voice_register} register "
        f"({_REGISTER_PROSE[spec.voice_register]}) in {spec.sentence_length} "
        f"sentences. You habitually: {'; '.join(spec.habits)}."
        f" Never use {'; '.join(spec.banned_tics)}."
    )
    if genre in ("engagement_email", "internal_email"):
        text += (
            f' Open with your salutation form "{spec.greeting}" (fill in the '
            f'recipient\'s first name) and sign off with "{spec.closing}" -- '
            f"the signature block itself is appended automatically from the "
            f"ledger; never type one."
        )
    return text


def _mail_audience(foundation: Foundation, entry) -> str:
    """M15 (mail-audience-internal-vs-external): name who the message is
    delivered To, so a client-delivered reply cannot be authored as an
    internal staff note. Mirrors expected_headers' partition exactly:
    external participants land in To, internal colleagues in Cc; a
    DL-addressed or all-internal message is internal traffic."""
    if entry.render_params.get("dl"):
        return (
            " Delivery: addressed to an internal distribution list; every "
            "reader is a colleague, so an internal register is right."
        )
    author = entry.authors[0]
    recipients = [p for p in entry.participants if p != author]
    to = [p for p in recipients if p.startswith("xp:")]
    if to:
        names = ", ".join(
            next(x.name for x in foundation.external_people if x.id == pid)
            for pid in to
        )
        return (
            f" Delivery: this message is sent To {names} at the client; "
            f"internal colleagues see it on Cc only. Address the client "
            f"directly, in a client-facing register -- it is not an internal "
            f"note, and nothing in it may read as a staff-to-staff aside "
            f"about the client."
        )
    return (
        " Delivery: internal only -- every recipient is a colleague, so an "
        "internal register is right."
    )


def _reporting_line(foundation: Foundation, subject_id: str, when: date) -> str:
    """The new hire's reporting line as of `when`, from foundation's
    `reports_to` edge (M12, rf:graph-1). A reporting line is a relationship the
    ledger owns; briefing it stops the author guessing a wrong supervisor, and
    ingest rejects prose that names a different internal manager. Empty for the
    CEO-equivalent (no manager) so the airlock stays silent where there is
    nothing to state. Names and titles are briefed directly, exactly as
    PersonBrief already briefs author and participant titles -- they are not
    fact placeholders, and never have been."""
    subject = foundation.person(subject_id)
    if subject.reports_to is None:
        return ""
    manager = foundation.person(subject.reports_to)
    return (
        f"Reports to {manager.name}, {manager.title_at(when)}. State the "
        f"reporting line only as briefed: name no other person or title as "
        f"this hire's supervisor."
    )


def _brief_person(
    foundation: Foundation,
    pid: str,
    at: date,
    historical_employer: bool = False,
) -> PersonBrief:
    """The brief for one person as of `at`, the document's date.

    An internal person's title is ALWAYS resolved as of `at`. That is not a
    knob: briefing a 2024 title into a 2020 letter is an anachronism, and
    nothing should be able to switch it on.

    An external person's employer resolves as of `at` only when
    `historical_employer` is set, which is the `affiliations_in_docs` knob.
    That knob plants the employer boundary as a labeled hard case (both
    sides surfaced in sigblocks and briefs); with it off, a recipe that
    populated affiliation history still briefs everyone under their current
    employer, which is torchlake-engineering's shape. Keeping the two
    resolutions independent is the point: title correctness is not
    something a hard-case knob gets a vote on.
    """
    if pid.startswith("p:"):
        p = foundation.person(pid)
        return PersonBrief(
            id=p.id,
            name=p.name,
            title=p.title_at(at),
            dept=p.dept,
            persona=p.persona,
        )
    xp = next(x for x in foundation.external_people if x.id == pid)
    org_id = employer_at(xp, at) if historical_employer else xp.org
    org = next(o for o in foundation.external_orgs if o.id == org_id)
    return PersonBrief(id=xp.id, name=xp.name, title=xp.title, dept=org.name)


def pick_batch(
    manifest: list[ManifestEntry], state, exclude: frozenset[str] = frozenset()
) -> list[ManifestEntry]:
    """Unauthored, unclaimed batchable docs from the first pending engagement
    group. `exclude` holds doc_ids already covered by an outstanding order, so
    concurrent batches never overlap and draining the manifest partitions it
    exactly once, in manifest order."""
    pending = [
        e
        for e in manifest
        if e.authoring == "batchable"
        and state.doc(e.doc_id).authored_hash is None
        and e.doc_id not in exclude
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

    batch = pick_batch(manifest, state, exclude=frozenset(state.covered_docs()))
    if not batch:
        if state.author_batches:
            # Every remaining batchable doc is already claimed by an
            # outstanding order; nothing fresh to emit until one ingests.
            # Not an error: the orchestrator is mid-window and should ingest
            # or re-dispatch the outstanding batches (see `status --json`).
            print(
                f"author: {len(state.author_batches)} batch(es) outstanding, "
                f"awaiting ingest"
            )
            return 0
        state.mark_done("author")
        save_state(paths, state)
        print("author: all batchable docs authored")
        return 0

    # The document's date always reaches the brief; this knob decides only
    # whether an external person's employer is resolved historically.
    aff_docs = charter.graph_targets.affiliations_in_docs

    # M15: per-author style specs from the one derive_style_specs twin (the
    # same recompute STY-01 checks the published ledger against). Empty when
    # the knob is off, so knob-off briefs stay byte-identical.
    style_specs = {}
    if charter.doc_culture.style_specs:
        from ..foundation.style import derive_style_specs

        style_specs = {
            s.person: s for s in derive_style_specs(charter, foundation).specs
        }

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
            if entry.genre == "engagement_email" and "thread_pos" in (
                entry.render_params
            ):
                # M14 thread-position guidance: a reply answers the message
                # before it rather than restating the engagement.
                if int(entry.render_params["thread_pos"]) > 0:
                    guidance += (
                        " This is a reply partway through an ongoing thread: "
                        "answer the previous message directly, do not "
                        "reintroduce the engagement or the participants, and "
                        "keep it to a few tight lines. A quoted history and "
                        "your signature are appended automatically -- write "
                        "only your new reply."
                    )
                else:
                    guidance += (
                        " This opens the thread: set the topic up clearly for "
                        "the replies that follow. Your signature is appended "
                        "automatically; do not type one."
                    )
            if entry.format == "eml" and "send_minute" in entry.render_params:
                # M15: every mail-block email names its delivery audience.
                guidance += _mail_audience(foundation, entry)
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
            if charter.doc_culture.voice_diversify and entry.authors:
                guidance += (
                    " " + _author_voice(charter.seed, entry.authors[0])
                    + _VOICE_BANNED
                )
            if style_specs and entry.authors:
                guidance += _style_guidance(
                    style_specs[entry.authors[0]], entry.genre
                )
            briefs.append(
                DocBrief(
                    doc_id=entry.doc_id,
                    title=entry.title,
                    genre=entry.genre,
                    date=entry.date,
                    authors=[
                        _brief_person(foundation, a, entry.date, aff_docs)
                        for a in entry.authors
                    ],
                    participants=[
                        _brief_person(foundation, p, entry.date, aff_docs)
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
                    engagement_position=(
                        _engagement_position(eng, entry.date) if eng else ""
                    ),
                    firm_digest=(
                        _firm_digest(
                            engagements.values(),
                            entry.date,
                            charter.engagements.book_is_sample,
                        )
                        if entry.genre == "company_overview"
                        else ""
                    ),
                    reporting_line=(
                        _reporting_line(
                            foundation, entry.participants[0], entry.date
                        )
                        if entry.genre == "onboarding_record"
                        and entry.participants
                        else ""
                    ),
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

    emit_author_batch(paths, state, build, [e.doc_id for e in batch])
    return 0
