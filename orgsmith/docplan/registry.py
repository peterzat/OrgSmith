"""The genre registry: the single declarative source of document supply.

Before M9 the planner spawned each genre from a hand-written method with a
hard-coded count (kickoffs for the first two engagements, status reports for
the first and last, financial summaries for the last two years), so document
supply was a fixed `2E + 7` skeleton no recipe number could move. The registry
replaces that: each genre is one row naming a DRIVER (what spawns it) and a
CADENCE (how many per driver window), and the planner builds the manifest by
walking these rows. Document count then falls out of the firm's real activity
-- its engagements, fiscal years, and hires -- which is the whole point.

Drivers:
  per_engagement   one driver window per engagement; cadence dates instances
                   inside [start, end] (or leading the start, for the letter).
  per_fiscal_year  one instance per fiscal year whose summary publishes inside
                   the charter range.
  firm_periodic    the firm on a period: one instance every `period_years`
                   across the range, first anchored after the first engagement.
  per_hire         one instance per person hired after the range began (a
                   roster-churn backfill), dated near their start. A class the
                   fixed skeleton could not express: it is keyed off the
                   roster's time dimension, which did not exist before M8.

Adding or removing a row changes the plan with no other planner edit (a genre
using an existing driver needs only its row); this is asserted in the tests.
Length is a per-genre property and lands here in a later increment.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..seeds import rng


@dataclass(frozen=True)
class GenreRule:
    """One genre's supply declaration.

    genre/format/authoring mirror the manifest fields. `folder` is a share
    path template; `{client}` is filled per engagement, other folders are
    literal. `fact_suffixes` names the engagement facts the genre references
    (e.g. "fee" -> f:<eid>.fee); the planner keeps only body-policy facts
    unless a host flag says otherwise. Cadence fields are interpreted by the
    driver; unused ones stay at their zero default.
    """

    genre: str
    driver: str
    format: str
    folder: str
    fact_suffixes: tuple[str, ...] = ()
    # M17b: which engagement SCOPE quantities this genre cites, from the
    # vocabulary {"scope", "comparators", "pipeline"}. Inert unless the
    # recipe declares engagements.scope: the planner drops a ref whose fact
    # the ledger never planted, so a knob-off org plans the same manifest
    # byte for byte. "pipeline" is position-gated -- a document cites only
    # the funnel stages its own date says are complete.
    scope_refs: tuple[str, ...] = ()
    authoring: str = "batchable"
    # The brief's word target for this genre, and the single source of truth
    # for it (authoring/contexts.py and review/corpus.py both read it here).
    # Raised to real-world lengths at M9: an engagement letter runs 800-1500
    # because it has clauses, and every authored genre was raised with it. 0
    # for static genres, which are never briefed.
    target_words: int = 0
    # Who signs the document and who it names. author_role: "ceo" (the
    # CEO-equivalent), "lead" (the engagement's senior on that date), or
    # "junior" (its most-junior member). participants: "team_external"
    # (internal team + client contacts), "team" (internal only), "ceo", or
    # "none". Both resolve against the roster AS OF the document's date, so
    # churn never staffs a departed person.
    author_role: str = "lead"
    participants: str = "team_external"
    # Realism surface. `title_prefix` builds the manifest title as
    # "<prefix>: <engagement title>" for engagement genres. `filename` is a
    # str.format template over {date}, {client}, {service}, {n} (instance
    # number), {year}; unused fields are ignored, and the extension is the
    # modern one (legacy conversion swaps it after quota accounting).
    title_prefix: str = ""
    filename: str = ""
    # A genre that hosts a non-body engagement fact: the engagement letter
    # carries a signature-page fee, the first minutes carries a filename-only
    # date. Every other genre drops a non-body fact rather than leaking it.
    hosts_signature: bool = False
    hosts_filename: bool = False
    # per_engagement cadence. Exactly one shapes the dates:
    lead_days: int = 0          # single instance dated this far BEFORE start
    start_offset_days: int = 0  # single instance dated start + this
    anchor_frac: float = 0.0    # first recurring instance at this fraction
    period_days: int = 0        # recurring: one per period_days after the anchor
    # firm_periodic cadence:
    period_years: int = 0
    # per_hire cadence:
    hire_offset_days: int = 0
    # Optional genres whose instance count is the recipe's format_mix bucket
    # of this name (pptx/eml); "" means always-on. Kept because a firm may
    # legitimately produce no decks and no mail, and the least-invasive way
    # to say so on an existing recipe is its format_mix, now that the bucket
    # no longer has to sum to target_docs.
    optional_count: str = ""
    # M12: this genre asserts a meeting or working session HAPPENED on its
    # date (minutes, a status email within a live thread), so the business-day
    # calendar shifts it off weekends and declared holidays. Off for genres
    # whose date is a filing or publication (letters, reports, overviews),
    # which legitimately carry any date. Default inert.
    asserts_attendance: bool = False


# The registry. Order is presentation order only; the planner sorts the final
# manifest by (date, path). Genres, formats, and folders match the pre-M9
# skeleton so a regenerated org stays recognizable; what changed is that the
# caps are gone and the counts now follow the drivers.
REGISTRY: tuple[GenreRule, ...] = (
    GenreRule(
        genre="engagement_letter",
        driver="per_engagement",
        format="pdf",
        folder="Engagements/{client}",
        fact_suffixes=("fee", "start", "client"),
        # The letter leads the start, so no funnel stage is complete yet:
        # it states what the engagement is FOR and nothing about progress.
        scope_refs=("scope",),
        hosts_signature=True,
        author_role="ceo",  # a countersigned contract, signed by the principal
        lead_days=10,  # LETTER_LEAD_DAYS; the letter leads the engagement
        title_prefix="Engagement Letter",
        filename="{date:%Y.%m.%d} - Engagement Letter - {client} - EXECUTED.pdf",
        target_words=1100,  # a real engagement letter has clauses (800-1500)
    ),
    GenreRule(
        genre="kickoff_memo",
        driver="per_engagement",
        format="docx",
        folder="Engagements/{client}",
        fact_suffixes=("start", "client"),
        scope_refs=("scope",),
        start_offset_days=3,  # a kickoff for EVERY engagement now (cap removed)
        title_prefix="Kickoff Memo",
        filename="{date:%Y.%m.%d} - Kickoff Memo - {service}.docx",
        target_words=650,
    ),
    GenreRule(
        genre="meeting_minutes",
        driver="per_engagement",
        format="docx",
        folder="Engagements/{client}",
        fact_suffixes=("client",),
        # Minutes report progress against the funnel, not the commercials.
        scope_refs=("pipeline",),
        hosts_filename=True,
        author_role="junior",  # the most-junior member takes the minutes
        anchor_frac=0.4,  # first working session; shares minutes_date()
        period_days=90,   # a session roughly every quarter of the engagement
        title_prefix="Meeting Minutes",
        filename="Meeting Minutes {date:%Y-%m-%d} - {client}.docx",
        target_words=600,
        asserts_attendance=True,  # minutes claim a session happened on the date
    ),
    GenreRule(
        genre="status_report",
        driver="per_engagement",
        format="docx",
        folder="Engagements/{client}",
        fact_suffixes=("fee", "client"),
        # The genre the divergence blocker landed on: a status report
        # states the whole picture, so it cites every quantity its date
        # permits and every one of them is a ledger object.
        scope_refs=("scope", "comparators", "pipeline"),
        participants="team",  # a client-facing report names the internal team
        anchor_frac=0.5,  # status reports for EVERY engagement now (cap removed)
        period_days=120,
        title_prefix="Status Report",
        filename="{date:%Y.%m.%d} - Status Report - {client} v2 FINAL.docx",
        target_words=850,
    ),
    GenreRule(
        genre="briefing_deck",
        driver="per_engagement",
        format="pptx",
        folder="Engagements/{client}",
        fact_suffixes=("start", "client"),
        scope_refs=("scope", "comparators"),
        anchor_frac=0.25,  # dated a quarter of the way in
        optional_count="pptx",
        title_prefix="Briefing Deck",
        filename="{date:%Y.%m.%d} - Briefing Deck - {client}.pptx",
        target_words=400,  # a deck is bulleted; raised but still terse
    ),
    GenreRule(
        genre="engagement_email",
        driver="per_engagement",
        format="eml",
        folder="Engagements/{client}",
        fact_suffixes=("client",),
        optional_count="eml",
        title_prefix="RE",
        filename="{date:%Y.%m.%d} - Email {n} - {service} - {client}.eml",
        target_words=250,  # a real status email, raised from 130
        asserts_attendance=True,  # a live thread reads as sent on a workday
    ),
    GenreRule(
        genre="onboarding_record",
        driver="per_hire",
        format="docx",
        folder="People",  # a folder the fixed skeleton never had
        author_role="ceo",  # the principal signs a small firm's hires in
        # A record per person who joined AFTER the document window opened (a
        # roster-churn backfill). A firm with no such hire produces none of
        # these, which is the degradation, not an error. hire_offset_days
        # dates it a week into the new hire's tenure.
        hire_offset_days=7,
        target_words=450,
        title_prefix="Onboarding",
        filename="{date:%Y.%m.%d} - Onboarding - {person}.docx",
    ),
    GenreRule(
        genre="company_overview",
        driver="firm_periodic",
        format="docx",
        folder="Firm",
        author_role="ceo",
        participants="ceo",
        period_years=3,  # a fresh overview every few years (was one, mid-range)
        filename="Firm Overview {date:%Y} v3.docx",
        target_words=750,
    ),
    GenreRule(
        genre="financial_summary",
        driver="per_fiscal_year",
        format="xlsx",
        folder="Finance",
        authoring="static",
        participants="none",
        filename="FY{year} Financial Summary.xlsx",
    ),
    GenreRule(
        # M14 mailbox ecology: mundane internal mail (scheduling, logistics,
        # admin). Count is doc_culture.mail.mundane_emails, spread across the
        # range; the planner special-cases this genre (like engagement_email)
        # rather than a driver window. Off entirely when mail is off, so
        # committed recipes plan none of it.
        genre="internal_email",
        driver="mail_culture",
        format="eml",
        folder="Firm/Mail",
        target_words=110,  # a short note
        participants="none",  # the planner picks internal recipients
        title_prefix="",
        filename="{date:%Y.%m.%d} - {subject}.eml",
    ),
)


# --------------------------------------------------------------------------
# Per-document section skeletons (M17b, part B)
# --------------------------------------------------------------------------
#
# M17's board: "per-person voice genuinely works now; what recurs is the
# per-genre outline." Two kickoff memos by two authors two years apart came
# back as the same memo re-skinned -- same five numbered owners in the same
# order, same open-questions pair -- because every fresh-context author is
# asked for the same document. The fix is not a better prompt (M16 already
# proved a banned-construction list only stops literal strings); it is to
# stop asking every kickoff memo to contain the same things.
#
# `forbids` is what actually does the work. "The same five numbered owners
# in the same order" cannot recur in a variant that may not contain a list.
# A directive is a suggestion an author can drift from; a forbidden block
# kind is checked at ingest.


@dataclass(frozen=True)
class Section:
    """One thing a document must contain.

    `form` is the DocIR block kind the section is expected to arrive as, and
    is what ingest counts: a `list` section means the deliverable must carry
    at least that many list blocks. `directive` is the brief text -- what
    this section is FOR, not what to call it. Variants that differ only in
    section naming would leave the underlying document identical, which is
    the defect, so directives name different content.
    """

    form: str  # heading | paragraph | list | table | sigblock
    directive: str


@dataclass(frozen=True)
class Outline:
    id: str
    sections: tuple[Section, ...]
    # Block kinds this variant may NOT contain. Never forbid a form another
    # mechanism requires of the genre: minutes must be able to list
    # attendees (MENT-01 reads those names) and an engagement letter must be
    # able to carry its sigblock (LOC-01 puts the fee on the signature page).
    forbids: tuple[str, ...] = ()


def _s(form: str, directive: str) -> Section:
    return Section(form=form, directive=directive)


# Three to four variants per longform authored genre. The two mail genres
# are deliberately absent: a 110-250 word note has one shape, and imposing
# four sections on it produces worse prose than the repetition it would
# prevent. `assign_outlines` leaves any genre with no pool unassigned, so
# adding one later is a pool entry and nothing else.
OUTLINES: dict[str, tuple[Outline, ...]] = {
    "kickoff_memo": (
        Outline(
            id="km-risk-first",
            sections=(
                _s("paragraph", "open on the single risk that will decide "
                   "this engagement, before any objective is stated"),
                _s("paragraph", "what the team will do differently because "
                   "of that risk"),
                _s("paragraph", "the objectives, framed as consequences of "
                   "the approach above"),
                _s("paragraph", "what the team needs from the client, in "
                   "prose, with no enumeration"),
            ),
            forbids=("list", "table"),
        ),
        Outline(
            id="km-owner-table",
            sections=(
                _s("table", "workstreams and their owners, as the FIRST "
                   "block of the document"),
                _s("paragraph", "why the work is split this way"),
                _s("paragraph", "the sequencing constraint between the "
                   "workstreams"),
            ),
            forbids=("list",),
        ),
        Outline(
            id="km-question-led",
            sections=(
                _s("heading", "a title naming the decision at stake"),
                _s("paragraph", "the questions this engagement exists to "
                   "answer, stated as questions"),
                _s("list", "how each question gets answered, one item per "
                   "question, in the same order"),
                _s("paragraph", "what is explicitly out of scope"),
            ),
            forbids=("table",),
        ),
        Outline(
            id="km-narrative",
            sections=(
                _s("paragraph", "the client's situation as the team "
                   "understands it today"),
                _s("paragraph", "the approach, as a continuous argument "
                   "rather than a set of workstreams"),
                _s("paragraph", "the first two weeks, concretely"),
            ),
            forbids=("list", "table"),
        ),
    ),
    "status_report": (
        Outline(
            id="sr-exception",
            sections=(
                _s("paragraph", "what is off track and what is being done "
                   "about it -- lead with the exception, not the summary"),
                _s("table", "the quantities this period, one row per "
                   "measure"),
                _s("paragraph", "what the client must decide before the "
                   "next report"),
            ),
            forbids=("list",),
        ),
        Outline(
            id="sr-narrative",
            sections=(
                _s("paragraph", "the period in one continuous account, "
                   "start to finish"),
                _s("paragraph", "the quantities, stated inside the prose "
                   "rather than tabulated"),
                _s("paragraph", "the outlook, with its assumptions named"),
            ),
            forbids=("list", "table"),
        ),
        Outline(
            id="sr-risk-register",
            sections=(
                _s("heading", "a title naming the period"),
                _s("paragraph", "progress against the plan"),
                _s("list", "the open risks, each with its owner and its "
                   "trigger"),
                _s("paragraph", "what changed in the risk picture since "
                   "the last report"),
            ),
            forbids=("table",),
        ),
        Outline(
            id="sr-decision-log",
            sections=(
                _s("paragraph", "the decisions this period asked the client "
                   "for, and which are still open"),
                _s("list", "the work completed, one item each"),
                _s("list", "the work in flight, one item each"),
                _s("paragraph", "what the next period depends on"),
            ),
            forbids=("table",),
        ),
    ),
    "engagement_letter": (
        Outline(
            id="el-terms-first",
            sections=(
                _s("paragraph", "the client's inside address and salutation"),
                _s("paragraph", "the commercial terms, stated before the "
                   "description of the work"),
                _s("paragraph", "scope and approach"),
                _s("paragraph", "the standard clauses, each as its own "
                   "short headed paragraph"),
                _s("sigblock", "signed by the author and the client contact"),
            ),
            forbids=("list", "table"),
        ),
        Outline(
            id="el-scope-schedule",
            sections=(
                _s("paragraph", "the client's inside address and salutation"),
                _s("paragraph", "scope, in prose"),
                _s("table", "the schedule of deliverables and their timing"),
                _s("paragraph", "the standard clauses, each as its own "
                   "short headed paragraph"),
                _s("sigblock", "signed by the author and the client contact"),
            ),
            forbids=("list",),
        ),
        Outline(
            id="el-enumerated-scope",
            sections=(
                _s("paragraph", "the client's inside address and salutation"),
                _s("list", "the scope, one item per deliverable"),
                _s("paragraph", "the team and how it is staffed"),
                _s("paragraph", "the standard clauses, each as its own "
                   "short headed paragraph"),
                _s("sigblock", "signed by the author and the client contact"),
            ),
            forbids=("table",),
        ),
    ),
    "meeting_minutes": (
        # No variant forbids `list`: MENT-01 reads the attendee names, and a
        # firm that minutes a session without listing who was there is the
        # unrealistic one.
        Outline(
            id="mm-decisions-first",
            sections=(
                _s("list", "attendees, full names"),
                _s("paragraph", "the decisions taken, before any discussion "
                   "is recounted"),
                _s("paragraph", "the discussion that produced them"),
                _s("list", "actions with owners"),
            ),
            forbids=("table",),
        ),
        Outline(
            id="mm-action-table",
            sections=(
                _s("list", "attendees, full names"),
                _s("paragraph", "discussion summary"),
                _s("table", "actions, owners and due dates"),
            ),
        ),
        Outline(
            id="mm-chronological",
            sections=(
                _s("list", "attendees, full names"),
                _s("paragraph", "the session in the order it happened, "
                   "including what was raised and dropped"),
                _s("paragraph", "what was left unresolved and who carries it"),
            ),
            forbids=("table",),
        ),
        Outline(
            id="mm-by-topic",
            sections=(
                _s("list", "attendees, full names"),
                _s("paragraph", "the first topic and where it landed"),
                _s("paragraph", "the second topic and where it landed"),
                _s("paragraph", "who carries what out of the session, in "
                   "prose rather than as an action list"),
            ),
            forbids=("table",),
        ),
    ),
    "briefing_deck": (
        Outline(
            id="bd-bulleted",
            sections=(
                _s("heading", "title slide naming the engagement"),
                _s("list", "the situation, 3-5 bullets"),
                _s("heading", "a slide title for the findings"),
                _s("list", "the findings, 3-5 bullets"),
                _s("heading", "next steps"),
                _s("list", "next steps, 3-5 bullets"),
            ),
            forbids=("table",),
        ),
        Outline(
            id="bd-data-led",
            sections=(
                _s("heading", "title slide naming the engagement"),
                _s("table", "the quantities, as the deck's second block"),
                _s("heading", "a slide title for what the numbers mean"),
                _s("paragraph", "the reading of those numbers, in prose"),
                _s("heading", "next steps"),
                _s("list", "next steps, 3-5 bullets"),
            ),
        ),
        Outline(
            id="bd-question-slides",
            sections=(
                _s("heading", "a title slide posing the question"),
                _s("paragraph", "why the question matters now"),
                _s("heading", "a slide title giving the answer"),
                _s("list", "the evidence, 3-5 bullets"),
                _s("heading", "what we need to proceed"),
                _s("paragraph", "the ask, in prose"),
            ),
            forbids=("table",),
        ),
    ),
    "onboarding_record": (
        Outline(
            id="or-welcome",
            sections=(
                _s("paragraph", "welcome, naming the new employee"),
                _s("paragraph", "their role and where it sits in the "
                   "practice"),
                _s("paragraph", "first-period expectations, in prose"),
            ),
            forbids=("list", "table"),
        ),
        Outline(
            id="or-checklist",
            sections=(
                _s("paragraph", "welcome, naming the new employee"),
                _s("list", "first-week logistics, one item each"),
                _s("paragraph", "who to go to for what"),
            ),
            forbids=("table",),
        ),
        Outline(
            id="or-role-table",
            sections=(
                _s("paragraph", "welcome, naming the new employee"),
                _s("table", "responsibilities and who they are shared with"),
                _s("paragraph", "how the first review will work"),
            ),
            forbids=("list",),
        ),
    ),
    "company_overview": (
        Outline(
            id="co-service-lines",
            sections=(
                _s("paragraph", "what the firm does, in one paragraph"),
                _s("list", "the service lines"),
                _s("paragraph", "representative client work"),
            ),
            forbids=("table",),
        ),
        Outline(
            id="co-history",
            sections=(
                _s("paragraph", "how the firm came to do what it does"),
                _s("paragraph", "what that history means for how it works "
                   "now"),
                _s("paragraph", "representative client work"),
            ),
            forbids=("list", "table"),
        ),
        Outline(
            id="co-capability-table",
            sections=(
                _s("paragraph", "what the firm does, in one paragraph"),
                _s("table", "capabilities and the sectors they serve"),
                _s("paragraph", "representative client work"),
            ),
            forbids=("list",),
        ),
    ),
}


def outline_by_id(genre: str, outline_id: str) -> Outline | None:
    for outline in OUTLINES.get(genre, ()):
        if outline.id == outline_id:
            return outline
    return None


def assign_outlines(charter, rows) -> list[str | None]:
    """Deal each authored document a section skeleton.

    `rows` is [(genre, authoring, engagement)] in manifest order; the return
    is aligned to it, carrying an outline id or None. Pure and module-level
    so OUT-01 recomputes it with the same code that planned it.

    A CONSTRAINED DRAW over a cycle, which is three properties at once. Write
    k for the pool size.

    1. THE CYCLE, and it is absolute: a per-genre `cycle` set records what
       this pass through the pool has used and empties once full, so **no
       variant repeats within any k consecutive documents of a genre.** That
       is what makes corpus variety a structural guarantee rather than luck:
       the first min(k, n) documents of a genre are all different.
    2. ADJACENCY, also absolute for k >= 2, and what OUT-01 enforces as a
       rule. It survives the cycle boundary because the previous pick is
       excluded even on the pass where the cycle resets.
    3. WITHIN-ENGAGEMENT uniqueness, preferred but not absolute. Concurrent
       engagements interleave in the global genre order, so an engagement's
       documents are not contiguous, and the cycle can leave only variants
       this engagement has already taken. When the two conflict the cycle
       wins, because corpus variety is the property a reader notices and a
       within-engagement repeat two years apart is not.

    Priority when candidates run out: drop within-engagement first, then the
    cycle, then adjacency. The last two are unreachable for k >= 2 -- with
    the cycle emptied when full the previous pick is always inside it, so
    excluding both leaves at least one variant -- which is why the first two
    properties are absolute and this order is provable rather than hopeful.
    "Impossible by construction" is still an overclaim: a genre with more
    than k documents reuses variants, in cycles, by design.

    Exactly one draw per assigned document, from a per-genre stream, so the
    deal is deterministic across runs and independent of every other genre.
    """
    if not charter.doc_culture.outline_variety:
        return [None] * len(rows)
    rands: dict = {}
    last: dict = {}
    cycles: dict = {}
    used: dict = {}
    out: list[str | None] = []
    for genre, authoring, engagement in rows:
        pool = OUTLINES.get(genre)
        if authoring != "batchable" or not pool:
            out.append(None)
            continue
        rand = rands.get(genre)
        if rand is None:
            rand = rands[genre] = rng(charter.seed, "docplan.outline", genre)
        ids = [o.id for o in pool]
        cycle = cycles.setdefault(genre, set())
        if len(cycle) >= len(ids):
            cycle.clear()
        seen = used.setdefault((genre, engagement), set())
        blocked = last.get(genre)
        candidates = [
            i for i in ids if i != blocked and i not in cycle and i not in seen
        ]
        if not candidates:  # the cycle and this engagement disagree
            candidates = [i for i in ids if i != blocked and i not in cycle]
        if not candidates:  # unreachable for k >= 2; kept as a floor
            candidates = [i for i in ids if i != blocked] or ids
        pick = rand.choice(candidates)
        out.append(pick)
        last[genre] = pick
        cycle.add(pick)
        seen.add(pick)
    return out
