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
