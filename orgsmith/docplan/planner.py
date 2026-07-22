"""docplan: the immutable document manifest.

Pure. Decides every document's identity before any prose exists: path with
a realistic filename, genre, format, date, authors (employed on that
date), engagement link, and which ledger facts MUST appear in the text
(facts_refs). The manifest is append-only ground truth; soft fixes bump
`rev`, they never rewrite identity fields.

Supply is driven by the genre registry (`registry.py`): the planner walks
its rows, and a row's driver and cadence decide how many documents each
genre spawns from the firm's engagements, fiscal years, and hires. There is
no fixed skeleton and no per-genre count wired into this file.
"""

from __future__ import annotations

from datetime import date, timedelta

from ..artifacts import (
    load_charter,
    load_engagements,
    load_finance,
    load_foundation,
    save_manifest,
)
from ..fabric.engagements import (
    LETTER_LEAD_DAYS,
    calendar_holidays,
    minutes_date,
    to_business_day,
)
from ..naming import check_relpath, sanitize_component
from ..paths import OrgPaths
from ..seeds import rng
from .registry import REGISTRY, GenreRule
from ..schemas import (
    BASE_FORMAT,
    Charter,
    Engagement,
    EngagementsLedger,
    FinanceLedger,
    Foundation,
    KeyFact,
    ManifestEntry,
    MentionMap,
    MentionRecord,
    Person,
    PlannedMention,
    write_model,
)
from ..state import load_state, require_stages, save_state, sha256_file


def _employed_at(person: Person, when: date) -> bool:
    emp = person.employment
    return emp.start <= when and (emp.end is None or emp.end >= when)


# Genres the coverage top-up may add a participant to. All four name internal
# staff as a matter of course, so a planted mention reads as the document
# doing its job rather than as a plant.
#
# Deliberately excluded: engagement_letter (a countersigned contract; its
# signatories are the CEO and the client, not the team), briefing_deck and
# engagement_email (the eml renderer derives To/Cc headers from
# `participants`, so a plant there would move headers EML-01 checks).
#
# Minutes and kickoffs alone were enough while every person was employed for
# the whole date range. Roster churn narrows employment windows, so a
# late-joining backfill can find no minutes dated after their start and the
# knob fails for a corpus that has perfectly good documents to name them in.
_TOP_UP_GENRES = (
    "meeting_minutes",
    "kickoff_memo",
    "status_report",
    "company_overview",
)

_LEGACY_FOR = {base: legacy for legacy, base in BASE_FORMAT.items()}


def legacy_selection(culture, office: list[tuple[date, str]]) -> set[str]:
    """Which office docs become pre-2007 binaries: the oldest
    round(legacy_ratio * n) by (date, path). Pure and RNG-free, shared by
    the planner and the LEG-01 recomputation. office holds (date, path)
    with the MODERN extension; membership is by that path."""
    if culture.legacy_ratio == 0:
        return set()
    ordered = sorted(office, key=lambda t: (t[0], t[1]))
    return {path for _, path in ordered[: round(culture.legacy_ratio * len(ordered))]}


def scan_selection(
    seed: int, culture, pdfs: list[tuple[date, str, bool]]
) -> dict[str, bool]:
    """Which pdfs become scans, and which of those keep an OCR layer:
    {path: has_ocr_layer}. Pure function of the charter knobs and the pdf
    identities, shared by the planner and the SCAN-01 recomputation so the
    two can never drift. pdfs holds (date, path, hosts_signature_fact);
    the scanned set is the oldest round(scanned_ratio * n) by (date,
    path); layers draw from the docplan.ocr stream (knobs off consume
    nothing); a signature_page host is never image-only."""
    if culture.scanned_ratio == 0:
        return {}
    ordered = sorted(pdfs, key=lambda t: (t[0], t[1]))
    scans = ordered[: round(culture.scanned_ratio * len(ordered))]
    if not scans:
        return {}
    layered = round(culture.ocr_layer_rate * len(scans))
    with_layer = set(
        rng(seed, "docplan.ocr").sample(range(len(scans)), layered)
    )
    return {
        path: (i in with_layer or hosts_sig)
        for i, (_, path, hosts_sig) in enumerate(scans)
    }


def _clamp(d: date, lo: date, hi: date) -> date:
    return max(lo, min(d, hi))


class _Planner:
    def __init__(
        self,
        charter: Charter,
        foundation: Foundation,
        finance: FinanceLedger,
        engagements: EngagementsLedger,
    ):
        self.charter = charter
        self.foundation = foundation
        self.finance = finance
        self.engagements = engagements
        self.range_start, self.range_end = charter.doc_culture.date_range
        self.calendar = calendar_holidays(charter)
        self.ceo = next(p for p in foundation.people if p.reports_to is None)
        self.ops_lead = self._ops_lead()
        self.planned: list[dict] = []
        self.facts = engagements.fact_index()
        self.policy = {fid: f.location_policy for fid, f in self.facts.items()}

    def _ops_lead(self) -> Person:
        depts = list(self.charter.headcount)
        last_dept = depts[-1]
        for p in self.foundation.people:
            if p.dept == last_dept and p.id != self.ceo.id:
                return p
        return self.ceo

    def _client_name(self, eng: Engagement) -> str:
        for org in self.foundation.external_orgs:
            if org.id == eng.client:
                return org.name
        raise KeyError(eng.client)

    def _team(self, eng: Engagement) -> list[Person]:
        return [self.foundation.person(pid) for pid in eng.internal_participants]

    def _author_for(self, eng: Engagement, when: date, junior: bool) -> Person:
        team = [p for p in self._team(eng) if _employed_at(p, when)]
        if not team:
            return self.ceo
        return team[-1] if junior else team[0]

    def _clamp_range(self, d: date) -> date:
        return _clamp(d, self.range_start, self.range_end)

    def _add(self, **kw) -> None:
        problems = check_relpath(kw["path"])
        if problems:
            raise SystemExit(f"docplan: unsafe path: {problems}")
        kw["date"] = _clamp(kw["date"], self.range_start, self.range_end)
        if not _employed_at(self.foundation.person(kw["authors"][0]), kw["date"]):
            raise SystemExit(
                f"docplan: author {kw['authors'][0]} not employed on {kw['date']}"
            )
        self.planned.append(kw)

    # --- registry-driven supply -----------------------------------------

    def plan_from_registry(self) -> None:
        """Build the manifest by walking the registry, dispatching each row
        to its driver. Supply is whatever the drivers yield; there is no
        target count and no fixed skeleton."""
        for rule in REGISTRY:
            if rule.genre == "engagement_email":
                self._emit_email(rule)
            elif rule.genre == "internal_email":
                self._emit_mundane(rule)
            elif rule.driver == "per_engagement":
                self._emit_engagement(rule)
            elif rule.driver == "per_fiscal_year":
                self._emit_fiscal_year(rule)
            elif rule.driver == "firm_periodic":
                self._emit_firm_periodic(rule)
            elif rule.driver == "per_hire":
                self._emit_hire(rule)
            else:
                raise SystemExit(
                    f"docplan: registry row {rule.genre!r} names driver "
                    f"{rule.driver!r}, which has no planner handler"
                )

    def _author_id(self, rule: GenreRule, eng, when: date) -> str:
        if rule.author_role == "ceo" or eng is None:
            return self.ceo.id
        return self._author_for(eng, when, junior=rule.author_role == "junior").id

    def _participant_ids(self, rule: GenreRule, eng) -> list[str]:
        if rule.participants == "ceo":
            return [self.ceo.id]
        if rule.participants == "none" or eng is None:
            return []
        ids = list(eng.internal_participants)
        if rule.participants == "team_external":
            ids = ids + list(eng.external_participants)
        return ids

    @staticmethod
    def _dedupe(dates: list[date]) -> list[date]:
        """Clamping can collapse two cadence instances onto one range-edge
        date; keep one so the path-uniqueness check does not fail on a
        legitimate short engagement."""
        seen: set[date] = set()
        out: list[date] = []
        for d in dates:
            if d not in seen:
                seen.add(d)
                out.append(d)
        return out

    def _engagement_dates(self, rule: GenreRule, eng) -> list[date]:
        """The dates one per-engagement genre lands inside this engagement,
        interpreting the row's cadence fields."""
        start, end = eng.start, eng.end
        duration = max(1, (end - start).days)
        if rule.lead_days:
            return [_clamp(
                start - timedelta(days=rule.lead_days), self.range_start, start
            )]
        anchor_off = int(rule.anchor_frac * duration)
        if rule.period_days:
            # The hosting genre's first instance shares the exact minutes_date
            # the fabric planted the filename fact on; recurrence follows.
            if rule.hosts_filename:
                first = minutes_date(
                    start, end, self.range_start, self.range_end, self.calendar
                )
            else:
                first = self._clamp_range(start + timedelta(days=anchor_off))
            dates = [first]
            k = 1
            while True:
                d = start + timedelta(days=anchor_off + k * rule.period_days)
                if d >= end:
                    break
                dates.append(self._clamp_range(d))
                k += 1
            return self._dedupe(self._shift_attendance(rule, dates))
        return [self._clamp_range(
            start + timedelta(days=anchor_off + rule.start_offset_days)
        )]

    def _shift_attendance(self, rule: GenreRule, dates: list[date]) -> list[date]:
        """Shift an attendance-asserting genre's dates onto business days when
        the recipe declares a calendar (M12). Idempotent on the minutes' first
        instance, which minutes_date already shifted at the source so fabric's
        filename fact matches. A no-op for other genres and for a recipe with
        no calendar, so committed fixtures stay byte-identical."""
        if not rule.asserts_attendance or self.calendar is None:
            return dates
        return [
            to_business_day(d, self.calendar, self.range_start, self.range_end)
            for d in dates
        ]

    def _facts_for(
        self, rule: GenreRule, eng, is_first: bool
    ) -> tuple[list[str], list[KeyFact], dict]:
        """(facts_refs, extra_key_facts, render_params) for one instance.

        A fact is briefed on the genre that hosts it: the letter carries its
        signature-page fee (rendered onto the sig page, never briefed as
        body); the first minutes carries the filename-only date. Any other
        genre drops a non-body fact rather than leak the value into text."""
        refs: list[str] = []
        render_params: dict = {}
        for suf in rule.fact_suffixes:
            ref = f"f:{eng.id}.{suf}"
            pol = self.policy.get(ref, "body")
            if pol == "body":
                refs.append(ref)
            elif pol == "signature_page" and rule.hosts_signature:
                refs.append(ref)
                render_params["sig_fact"] = ref
        extra: list[KeyFact] = []
        if rule.hosts_filename and is_first:
            md_ref = f"f:{eng.id}.minutes-date"
            if self.policy.get(md_ref) == "filename":
                # Filename-only: never a facts_ref, because FACT-01 demands
                # body presence for those.
                extra = [KeyFact(fact_id=md_ref, location="filename")]
        return refs, extra, render_params

    def _emit_engagement(self, rule: GenreRule) -> None:
        engs = self.engagements.engagements
        if rule.optional_count:
            want = getattr(self.charter.doc_culture.format_mix, rule.optional_count)
            if want == 0:
                return
            if want > len(engs):
                raise SystemExit(
                    f"docplan: format_mix.{rule.optional_count} wants {want} "
                    f"{rule.genre}(s) but only {len(engs)} engagement(s) "
                    f"exist; lower the mix or raise engagements.count"
                )
            engs = engs[:want]
        for eng in engs:
            client = sanitize_component(self._client_name(eng))
            folder = rule.folder.format(client=client)
            service = eng.title.split(" for ")[0]
            dates = self._engagement_dates(rule, eng)
            for i, when in enumerate(dates):
                refs, extra, render_params = self._facts_for(rule, eng, i == 0)
                name = rule.filename.format(
                    date=when, client=client, service=service, n=i + 1
                )
                self._add(
                    path=f"{folder}/{name}",
                    title=f"{rule.title_prefix}: {eng.title}",
                    genre=rule.genre,
                    format=rule.format,
                    date=when,
                    authors=[self._author_id(rule, eng, when)],
                    participants=self._participant_ids(rule, eng),
                    engagement=eng.id,
                    facts_refs=refs,
                    extra_key_facts=extra,
                    render_params=render_params,
                    authoring=rule.authoring,
                )

    def _emit_email(self, rule: GenreRule) -> None:
        """Engagement mail. Knob-off (no doc_culture.mail): the pre-M14 flat
        path. Knob-on (M14): real threads with minute-granularity timing,
        varied depth, and reply structure the renderer turns into In-Reply-To /
        References / quoted history."""
        want = getattr(self.charter.doc_culture.format_mix, rule.optional_count)
        if want == 0:
            return
        if self.charter.doc_culture.mail is None:
            self._emit_email_flat(rule, want)
        else:
            self._emit_email_threaded(rule, want, self.charter.doc_culture.mail)

    def _emit_email_flat(self, rule: GenreRule, want: int) -> None:
        """The pre-M14 path: format_mix.eml messages assigned round-robin over
        engagements (wrapping is fine; a thread carries many mails). A thread
        opens about four weeks into its engagement and its replies land a day
        or two apart, so it reads as a thread rather than as monthly memos
        (the old 45-day spacing; email-thread-spacing). The per-reply gap
        draws from its OWN seed stream so the cadence never perturbs another
        pass's randomness."""
        engs = self.engagements.engagements
        erand = rng(self.charter.seed, "docplan.email.cadence")
        rounds: dict[str, int] = {}
        last: dict[str, date] = {}
        for i in range(want):
            eng = engs[i % len(engs)]
            k = rounds.get(eng.id, 0)
            rounds[eng.id] = k + 1
            client = sanitize_component(self._client_name(eng))
            service = eng.title.split(" for ")[0]
            if k == 0:
                ed = self._clamp_range(eng.start + timedelta(days=28))
            else:
                ed = self._clamp_range(
                    last[eng.id] + timedelta(days=erand.randint(1, 3))
                )
            # A live thread reads as sent on a workday (M12). The cadence RNG
            # draws BEFORE the shift, so the shift never perturbs the stream;
            # a no-op when no calendar is declared.
            ed = to_business_day(
                ed, self.calendar, self.range_start, self.range_end
            )
            last[eng.id] = ed
            refs, _, _ = self._facts_for(rule, eng, False)
            name = rule.filename.format(
                date=ed, client=client, service=service, n=k + 1
            )
            self._add(
                path=f"Engagements/{client}/{name}",
                title=f"RE: {eng.title}",
                genre=rule.genre,
                format=rule.format,
                date=ed,
                authors=[self._author_id(rule, eng, ed)],
                participants=self._participant_ids(rule, eng),
                engagement=eng.id,
                facts_refs=refs,
                authoring=rule.authoring,
            )

    def _thread_depths(self, want: int, n: int, max_depth: int) -> list[int]:
        """Per-engagement thread depths summing to `want`, each in
        [1, max_depth], varied rather than uniform round-robin: engagements
        draw a priority weight from the docplan.email.threads stream and fill
        to the cap in that order, so some threads run long and others stay
        short. When want <= n only the first `want` engagements host a
        (single-message) thread."""
        if want <= n:
            return [1] * want + [0] * (n - want)
        trand = rng(self.charter.seed, "docplan.email.threads")
        depths = [1] * n
        remaining = want - n
        order = sorted(
            range(n), key=lambda i: (trand.random(), i), reverse=True
        )
        for i in order:
            take = min(max_depth - depths[i], remaining)
            depths[i] += take
            remaining -= take
            if remaining == 0:
                break
        return depths

    def _next_send(
        self, cur_date: date, cur_min: int, day_lo: int, day_hi: int, hrand
    ) -> tuple[date, int]:
        """The next strictly-later (date, minute) in a thread. Same-day replies
        occur (a later minute the same day); otherwise the reply lands one or a
        few business days on. Always strictly increasing, and bounded: at the
        range-end wall it stays same-day with a later minute."""
        gap = hrand.choice((0, 0, 1, 1, 2, 3))
        if gap == 0 and cur_min + 1 < day_hi:
            return cur_date, hrand.randint(cur_min + 1, day_hi - 1)
        g = max(1, gap)
        for _ in range(21):
            cand = to_business_day(
                self._clamp_range(cur_date + timedelta(days=g)),
                self.calendar, self.range_start, self.range_end,
            )
            if cand > cur_date:
                return cand, hrand.randint(day_lo, day_hi - 1)
            g += 1
        # Range-end wall: the date cannot advance, so keep the strictly-
        # increasing invariant with a later minute (past business-hours end if
        # need be), bounded to a valid minute-of-day (0..1439).
        return cur_date, min(cur_min + 1, 1439)

    def _thread_author(self, eng: Engagement, when: date, pos: int) -> str:
        """A thread alternates its internal sender (senior, then junior) so it
        reads as a back-and-forth and the signature block changes down the
        chain. A one-person team keeps a single sender; an empty team (nobody
        employed on the date) falls back to the CEO-equivalent."""
        team = [p for p in self._team(eng) if _employed_at(p, when)]
        if not team:
            return self.ceo.id
        return (team[0] if pos % 2 == 0 else team[-1]).id

    def _emit_email_threaded(
        self, rule: GenreRule, want: int, mail
    ) -> None:
        """M14 engagement threads. Depth varies per engagement; each thread
        opens ~28 days in and its replies land at strictly increasing
        minute-granularity times inside the declared business hours, with
        same-day replies occurring. thread_pos and send_minute ride in
        render_params; the renderer and EML-01 turn them into the Date,
        In-Reply-To, References, RE: subject, and quoted history. Draws come
        only from the new email streams, so a knob-off recipe draws nothing."""
        engs = self.engagements.engagements
        n = len(engs)
        if want > n * mail.max_thread_depth:
            raise SystemExit(
                f"docplan: format_mix.eml wants {want} mail(s) but {n} "
                f"engagement(s) x max_thread_depth {mail.max_thread_depth} "
                f"host at most {n * mail.max_thread_depth}; lower eml, raise "
                f"engagements.count, or raise max_thread_depth"
            )
        depths = self._thread_depths(want, n, mail.max_thread_depth)
        lo, hi = mail.business_hours
        day_lo, day_hi = lo * 60, hi * 60
        opener_hi = day_lo + (day_hi - day_lo) // 2  # openers land before noon
        hrand = rng(self.charter.seed, "docplan.email.hours")
        attached = 0
        for eng, depth in zip(engs, depths):
            if depth == 0:
                continue
            client = sanitize_component(self._client_name(eng))
            service = eng.title.split(" for ")[0]
            cur_date = to_business_day(
                self._clamp_range(eng.start + timedelta(days=28)),
                self.calendar, self.range_start, self.range_end,
            )
            cur_min = hrand.randint(day_lo, opener_hi)
            ancestor_refs: list[str] = []
            for pos in range(depth):
                if pos > 0:
                    cur_date, cur_min = self._next_send(
                        cur_date, cur_min, day_lo, day_hi, hrand
                    )
                refs, _, _ = self._facts_for(rule, eng, False)
                # A reply's quoted tail carries its predecessor's resolved
                # body, so the reply's manifest entry owns those fact surfaces
                # too: evals attribute a quoted fact to the reply as well.
                ancestor_refs = list(dict.fromkeys(ancestor_refs + refs))
                name = rule.filename.format(
                    date=cur_date, client=client, service=service, n=pos + 1
                )
                render_params = {"thread_pos": pos, "send_minute": cur_min}
                # M14 transmittal: the opener of the first `attachments`
                # threads carries the engagement's kickoff memo as a MIME
                # attachment. The kickoff is planned before mail (registry
                # order), so its path is already known here.
                if pos == 0 and attached < mail.attachments:
                    kickoff = self._attach_source(eng)
                    if kickoff is not None:
                        render_params["attach_path"] = kickoff
                        attached += 1
                self._add(
                    path=f"Engagements/{client}/{name}",
                    title=eng.title,
                    genre=rule.genre,
                    format=rule.format,
                    date=cur_date,
                    authors=[self._thread_author(eng, cur_date, pos)],
                    participants=self._participant_ids(rule, eng),
                    engagement=eng.id,
                    facts_refs=list(ancestor_refs),
                    render_params=render_params,
                    authoring=rule.authoring,
                )
        if attached < mail.attachments:
            raise SystemExit(
                f"docplan: mail.attachments wants {mail.attachments} "
                f"transmittal(s) but only {attached} thread(s) have a kickoff "
                f"memo to attach; lower attachments or add engagements"
            )

    def _attach_source(self, eng: Engagement) -> str | None:
        """The share path of the kickoff memo a transmittal opener attaches: a
        modern docx with body facts, planted before mail in registry order.
        None when the engagement has no kickoff."""
        for d in self.planned:
            if d.get("engagement") == eng.id and d["genre"] == "kickoff_memo":
                return d["path"]
        return None

    _MUNDANE_SUBJECTS = (
        "Office logistics",
        "Scheduling next week",
        "Building access",
        "IT maintenance window",
        "Timesheet reminder",
        "Holiday coverage",
        "Team lunch",
        "Parking update",
        "All-hands prep",
        "Supplies order",
    )

    def _emit_mundane(self, rule: GenreRule) -> None:
        """Mundane internal mail (M14): non-engagement scheduling / logistics /
        admin, spread across the range, authored short, carrying colleague
        mentions but no engagement facts, drawn only from docplan.email.mundane
        so a knob-off recipe plans none. Standalone messages (no thread), so
        they are distractor traffic, not thread answers."""
        mail = self.charter.doc_culture.mail
        if mail is None or mail.mundane_emails == 0:
            return
        count = mail.mundane_emails
        from ..acl import derive_distribution_lists

        dls = derive_distribution_lists(self.charter, self.foundation).lists
        mrand = rng(self.charter.seed, "docplan.email.mundane")
        lo, hi = mail.business_hours
        day_lo, day_hi = lo * 60, hi * 60
        span = max(1, (self.range_end - self.range_start).days)
        for i in range(count):
            frac = (i + 0.5) / count
            when = to_business_day(
                self._clamp_range(
                    self.range_start + timedelta(days=int(frac * span))
                ),
                self.calendar, self.range_start, self.range_end,
            )
            employed = [
                p for p in self.foundation.people if _employed_at(p, when)
            ]
            if len(employed) < 2:
                continue  # too few staff on that date to address a note
            author = employed[mrand.randrange(len(employed))]
            others = [p for p in employed if p.id != author.id]
            k = min(len(others), mrand.choice((1, 1, 2)))
            recips = mrand.sample(others, k)
            subject = self._MUNDANE_SUBJECTS[i % len(self._MUNDANE_SUBJECTS)]
            minute = mrand.randint(day_lo, day_hi - 1)
            name = rule.filename.format(
                date=when, subject=sanitize_component(subject)
            )
            render_params = {"send_minute": minute}
            # M14: address every third mundane note to a distribution list; the
            # To header becomes the list, the named colleagues stay as body
            # mentions. Visibility expands the list to its members (DL-01).
            if dls and i % 3 == 0:
                render_params["dl"] = dls[i % len(dls)].address
            self._add(
                path=f"{rule.folder}/{name}",
                title=subject,
                genre=rule.genre,
                format=rule.format,
                date=when,
                authors=[author.id],
                participants=[p.id for p in recips],
                engagement=None,
                facts_refs=[],
                render_params=render_params,
                authoring=rule.authoring,
            )

    def _emit_fiscal_year(self, rule: GenreRule) -> None:
        """One financial summary per fiscal year whose January publish date
        falls inside the charter range. The last-two-years cap is gone; the
        lower bound keeps a firm founded before its document window from
        back-publishing summaries that would clamp onto the range-start date."""
        fy_years = [
            fy.year
            for fy in self.finance.years
            if self.range_start <= date(fy.year + 1, 1, 15) <= self.range_end
        ]
        for year in fy_years:
            pub = date(year + 1, 1, 15)
            author = (
                self.ops_lead if _employed_at(self.ops_lead, pub) else self.ceo
            )
            self._add(
                path=f"{rule.folder}/{rule.filename.format(year=year)}",
                title=f"FY{year} Financial Summary",
                genre=rule.genre,
                format=rule.format,
                date=pub,
                authors=[author.id],
                participants=[],
                engagement=None,
                facts_refs=[],
                authoring=rule.authoring,
                render_params={"year": year},
            )

    def _emit_firm_periodic(self, rule: GenreRule) -> None:
        """Firm overviews across the range, one every period_years, anchored
        just after the first engagement so the earliest one has a client to
        cite. Each names exactly the clients whose engagement has begun by its
        date (by fact id); the brief's date-scoped digest keeps it from
        claiming anything later than itself."""
        engs = self.engagements.engagements
        if not engs:
            return
        anchor = engs[0].start + timedelta(days=30)
        step_days = max(1, rule.period_years) * 365
        dates: list[date] = []
        offset = 0
        while anchor + timedelta(days=step_days * offset) <= self.range_end:
            dates.append(self._clamp_range(anchor + timedelta(days=step_days * offset)))
            offset += 1
        for when in self._dedupe(dates):
            as_of = [e for e in engs if e.start <= when]
            self._add(
                path=f"{rule.folder}/{rule.filename.format(date=when)}",
                title="Firm Overview",
                genre=rule.genre,
                format=rule.format,
                date=when,
                authors=[self.ceo.id],
                participants=[self.ceo.id],
                engagement=None,
                facts_refs=[f"f:{e.id}.client" for e in as_of],
                authoring=rule.authoring,
            )

    def _emit_hire(self, rule: GenreRule) -> None:
        """One onboarding record per person who joined AFTER the document
        window opened -- a roster-churn backfill. A firm with no such hire
        produces none, which is the degradation, not an error. The record
        names the new hire (a mention) and carries no ledger facts."""
        offset = rule.hire_offset_days or 7
        for person in self.foundation.people:
            if person.employment.start <= self.range_start:
                continue  # a founder / pre-window employee, not a hire
            when = self._clamp_range(
                person.employment.start + timedelta(days=offset)
            )
            name = rule.filename.format(
                date=when, person=sanitize_component(person.name)
            )
            self._add(
                path=f"{rule.folder}/{name}",
                title=f"{rule.title_prefix}: {person.name}",
                genre=rule.genre,
                format=rule.format,
                date=when,
                authors=[self._author_id(rule, None, when)],
                participants=[person.id],
                engagement=None,
                facts_refs=[],
                authoring=rule.authoring,
            )

    # --- mention planning -------------------------------------------------

    def _entity_surface(self, entity_id: str) -> PlannedMention:
        if entity_id.startswith("p:"):
            return PlannedMention(
                entity=entity_id,
                surface=self.foundation.person(entity_id).name,
            )
        if entity_id.startswith("xp:"):
            xp = next(
                x for x in self.foundation.external_people if x.id == entity_id
            )
            return PlannedMention(entity=entity_id, surface=xp.name)
        org = next(o for o in self.foundation.external_orgs if o.id == entity_id)
        return PlannedMention(entity=entity_id, surface=org.name, kind="org")

    def _doc_mention_add(self, doc: dict, mention: PlannedMention) -> bool:
        key = (mention.entity, mention.surface)
        existing = {(m.entity, m.surface) for m in doc["mentions"]}
        if key in existing:
            return False
        doc["mentions"].append(mention)
        return True

    def _mentioned_docs(self, entity_id: str) -> list[dict]:
        return [
            d
            for d in self.planned
            if any(m.entity == entity_id for m in d["mentions"])
        ]

    def plan_mentions(self) -> None:
        """Natural mentions from doc identity, then coverage top-up, then
        nickname plants. Static docs carry no mentions (no model pass)."""
        eng_by_id = {e.id: e for e in self.engagements.engagements}
        for doc in self.planned:
            doc["mentions"] = []
            if doc.get("authoring") == "static":
                continue
            for pid in doc["authors"] + doc["participants"]:
                self._doc_mention_add(doc, self._entity_surface(pid))
            if doc["engagement"]:
                eng = eng_by_id[doc["engagement"]]
                self._doc_mention_add(doc, self._entity_surface(eng.client))

        minimum = self.charter.graph_targets.min_mentions_per_person
        if minimum:
            for person in self.foundation.people:
                have = len(self._mentioned_docs(person.id))
                candidates = [
                    d
                    for d in self.planned
                    if d.get("authoring") != "static"
                    and d["genre"] in _TOP_UP_GENRES
                    and _employed_at(person, d["date"])
                    and not any(m.entity == person.id for m in d["mentions"])
                ]
                candidates.sort(key=lambda d: (d["date"], d["path"]))
                while have < minimum and candidates:
                    doc = candidates.pop(0)
                    doc["participants"] = doc["participants"] + [person.id]
                    self._doc_mention_add(doc, self._entity_surface(person.id))
                    have += 1
                if have < minimum:
                    raise SystemExit(
                        f"docplan: cannot reach min_mentions_per_person="
                        f"{minimum} for {person.id}; add docs or lower the knob"
                    )

        for person in self.foundation.people:
            for alias in person.aliases:
                hosts = self._mentioned_docs(person.id)
                hosts.sort(
                    key=lambda d: (d["genre"] != "meeting_minutes", d["date"])
                )
                if not hosts:
                    raise SystemExit(
                        f"docplan: no doc mentions {person.id}; cannot plant "
                        f"nickname alias {alias!r}"
                    )
                self._doc_mention_add(
                    hosts[0],
                    PlannedMention(entity=person.id, surface=alias),
                )

    def plan_scans(self) -> None:
        """Flag scans per scan_selection. Paths stay .pdf: the filename is
        immutable eval/ACL ground truth."""
        selection = scan_selection(
            self.charter.seed,
            self.charter.doc_culture,
            [
                (
                    d["date"],
                    d["path"],
                    any(
                        self.policy.get(ref) == "signature_page"
                        for ref in d.get("facts_refs", [])
                    ),
                )
                for d in self.planned
                if d["format"] == "pdf"
            ],
        )
        for doc in self.planned:
            layer = selection.get(doc["path"])
            if layer is None:
                continue
            params = dict(doc.get("render_params", {}))
            params["scan"] = 1
            if layer:
                params["ocr_layer"] = 1
            doc["render_params"] = params

    def plan_legacy(self) -> None:
        """The oldest office docs become .doc/.xls/.ppt per legacy_ratio;
        paths swap extension, everything else about the doc's identity
        stays. RNG-free, so knobs-off recipes regenerate byte-identically."""
        legacy = legacy_selection(
            self.charter.doc_culture,
            [
                (d["date"], d["path"])
                for d in self.planned
                if d["format"] in _LEGACY_FOR
            ],
        )
        for doc in self.planned:
            if doc["path"] not in legacy:
                continue
            fmt = _LEGACY_FOR[doc["format"]]
            doc["path"] = doc["path"][: -len(doc["format"])] + fmt
            doc["format"] = fmt

    def build(self) -> list[ManifestEntry]:
        self.plan_from_registry()
        self.plan_mentions()
        self.plan_scans()
        self.plan_legacy()

        self.planned.sort(key=lambda d: (d["date"], d["path"]))
        entries = []
        seen_paths: set[str] = set()
        for i, doc in enumerate(self.planned, start=1):
            key = doc["path"].lower()
            if key in seen_paths:
                raise SystemExit(f"docplan: duplicate path {doc['path']!r}")
            seen_paths.add(key)
            doc["key_facts"] = [
                KeyFact(fact_id=ref, location=self.policy.get(ref, "body"))
                for ref in doc.get("facts_refs", [])
            ] + doc.pop("extra_key_facts", [])
            entries.append(ManifestEntry(doc_id=f"d:{i:04d}", **doc))
        self._check_hard_cases(entries)
        return self._plan_noise(entries)

    @staticmethod
    def _noise_path(
        src_path: str, kind: str, suffix: str = "", pos: int = 0
    ) -> str:
        dot = src_path.rfind(".")
        stem, ext = src_path[:dot], src_path[dot:]
        if kind == "exact_duplicate":
            tag = " (copy)"
        elif kind == "version":
            tag = f" v{pos}"
        else:
            tag = " - DRAFT"
        extra = f" {suffix}" if suffix else ""
        return f"{stem}{tag}{extra}{ext}"

    def _plan_noise(self, entries: list[ManifestEntry]) -> list[ManifestEntry]:
        """Append derived noise documents (M12): exact duplicates and draft
        near-duplicates of eligible authored sources, from a NEW seed stream so
        a knob-off recipe plans the same manifest byte-for-byte. Eligible
        sources are batchable prose in a modern format with no scan, legacy, or
        non-body fact, so a copy renders cleanly and cannot break a location
        rule. Fails actionably when the corpus has too few sources."""
        noise = self.charter.doc_culture.noise
        if noise is None:
            return entries
        eligible = [
            e
            for e in entries
            if e.authoring == "batchable"
            and e.format in ("docx", "pdf", "pptx", "eml")
            and not e.render_params.get("scan")
            and "sig_fact" not in e.render_params
            and all(kf.location == "body" for kf in e.key_facts)
        ]
        total = noise.duplicates + noise.drafts
        if total > len(eligible):
            raise SystemExit(
                f"docplan: noise wants {total} derived doc(s) but only "
                f"{len(eligible)} eligible source(s) exist; lower "
                f"duplicates/drafts or grow the corpus"
            )
        picks = rng(self.charter.seed, "docplan.noise").sample(
            range(len(eligible)), total
        )
        plan = [("exact_duplicate", noise.duplicates), ("draft", noise.drafts)]
        seen = {e.path.lower() for e in entries}
        derived: list[ManifestEntry] = []
        next_id = len(entries) + 1
        cursor = 0
        for kind, count in plan:
            for _ in range(count):
                src = eligible[picks[cursor]]
                cursor += 1
                path = self._noise_path(src.path, kind)
                if path.lower() in seen:
                    path = self._noise_path(src.path, kind, suffix=str(next_id))
                seen.add(path.lower())
                label = "copy" if kind == "exact_duplicate" else "draft"
                derived.append(
                    ManifestEntry(
                        doc_id=f"d:{next_id:04d}",
                        path=path,
                        title=f"{src.title} ({label})",
                        genre=src.genre,
                        format=src.format,
                        date=src.date,
                        authors=list(src.authors),
                        participants=[],
                        engagement=src.engagement,
                        authoring="derived",
                        render_params={
                            "noise_of": src.doc_id,
                            "noise_kind": kind,
                        },
                    )
                )
                next_id += 1
        next_id = self._plan_chains(entries, eligible, seen, derived, next_id)
        next_id = self._plan_misfiles(entries, eligible, seen, derived, next_id)
        return entries + derived

    def _plan_misfiles(
        self,
        entries: list[ManifestEntry],
        eligible: list[ManifestEntry],
        seen: set[str],
        derived: list[ManifestEntry],
        next_id: int,
    ) -> int:
        """M15: misfiled copies. An exact copy of an authored source filed in
        a folder other than its source's, engagement folders included. The
        manifest owns the location and everything downstream follows it (ACL
        grants and the visibility suite derive from the manifest), so a
        misfile readable by the wrong team is ground truth, never a validator
        failure. Draws only from the NEW docplan.noise.misfile stream and
        appends after chains, keeping earlier kinds byte-stable.

        The `engagement` label stays the source's: it describes what the
        document IS (engagement A's letter), while `path` says where it SITS.
        Access follows the path: acl.derive_acl grants a misfile its
        destination folder's reader set, as a real share's folder ACL
        would."""
        noise = self.charter.doc_culture.noise
        if noise is None or noise.misfiled == 0:
            return next_id
        mrng = rng(self.charter.seed, "docplan.noise.misfile")
        folders = sorted({e.path.rsplit("/", 1)[0] for e in entries if "/" in e.path})
        if noise.misfiled > len(eligible):
            raise SystemExit(
                f"docplan: noise wants {noise.misfiled} misfiled cop(ies) but "
                f"only {len(eligible)} eligible source(s) exist; lower "
                f"misfiled or grow the corpus"
            )
        picks = mrng.sample(range(len(eligible)), noise.misfiled)
        for pi in picks:
            src = eligible[pi]
            src_dir = src.path.rsplit("/", 1)[0] if "/" in src.path else ""
            foreign = [f for f in folders if f != src_dir]
            if not foreign:
                raise SystemExit(
                    "docplan: noise.misfiled needs a second directory to "
                    "misfile into, and the share plans only one"
                )
            dest = foreign[mrng.randrange(len(foreign))]
            base = src.path.rsplit("/", 1)[-1]
            path = f"{dest}/{base}"
            if path.lower() in seen:
                dot = path.rfind(".")
                path = f"{path[:dot]} ({next_id}){path[dot:]}"
            seen.add(path.lower())
            derived.append(
                ManifestEntry(
                    doc_id=f"d:{next_id:04d}",
                    path=path,
                    title=f"{src.title} (misfiled)",
                    genre=src.genre,
                    format=src.format,
                    date=src.date,
                    authors=list(src.authors),
                    participants=[],
                    engagement=src.engagement,
                    authoring="derived",
                    render_params={
                        "noise_of": src.doc_id,
                        "noise_kind": "misfile",
                    },
                )
            )
            next_id += 1
        return next_id

    def _plan_chains(
        self,
        entries: list[ManifestEntry],
        eligible: list[ManifestEntry],
        seen: set[str],
        derived: list[ManifestEntry],
        next_id: int,
    ) -> int:
        """M15: version chains with divergence. Each chain's final member is
        an authored source; the planner plants length-1 earlier versions with
        deterministic earlier dates inside the recipe's range, every draw from
        the NEW docplan.noise.chains stream so the M12 duplicates/drafts picks
        are untouched. Renderers give each member a distinct version banner,
        so no two members are byte-identical and hash dedupe cannot collapse
        the chain. Appended after the M12 kinds so existing doc_ids and paths
        stay byte-stable."""
        noise = self.charter.doc_culture.noise
        if noise is None or noise.version_chains == 0:
            return next_id
        crng = rng(self.charter.seed, "docplan.noise.chains")
        start = self.charter.doc_culture.date_range[0]
        # A versioned email is not a thing; chains need date room for the
        # earlier members (max length 5 -> up to 4 earlier dates).
        chainable = [
            e
            for e in eligible
            if e.format != "eml" and (e.date - start).days >= 4
        ]
        if noise.version_chains > len(chainable):
            raise SystemExit(
                f"docplan: noise wants {noise.version_chains} version "
                f"chain(s) but only {len(chainable)} chainable source(s) "
                f"exist (non-eml, dated 4+ days into the range); lower "
                f"version_chains or grow the corpus"
            )
        picks = crng.sample(range(len(chainable)), noise.version_chains)
        for pi in picks:
            src = chainable[pi]
            length = crng.randint(3, 5)  # members including the final
            span = (src.date - start).days
            spacing = max(1, min(crng.randint(2, 7), span // (length - 1)))
            for pos in range(1, length):
                path = self._noise_path(src.path, "version", pos=pos)
                if path.lower() in seen:
                    path = self._noise_path(
                        src.path, "version", suffix=str(next_id), pos=pos
                    )
                seen.add(path.lower())
                derived.append(
                    ManifestEntry(
                        doc_id=f"d:{next_id:04d}",
                        path=path,
                        title=f"{src.title} (v{pos})",
                        genre=src.genre,
                        format=src.format,
                        date=src.date - timedelta(days=(length - pos) * spacing),
                        authors=list(src.authors),
                        participants=[],
                        engagement=src.engagement,
                        authoring="derived",
                        render_params={
                            "noise_of": src.doc_id,
                            "noise_kind": "version",
                            "noise_pos": pos,
                            "noise_len": length,
                        },
                    )
                )
                next_id += 1
        return next_id

    def _check_hard_cases(self, entries: list[ManifestEntry]) -> None:
        """The knob contract gate: placement demand meets document supply
        here, so over-demanding recipes fail at this stage, actionably,
        rather than silently under-planting."""
        planted = {
            fid: pol for fid, pol in self.policy.items() if pol != "body"
        }
        want = {
            "signature_page": self.charter.hard_cases.signature_page_facts,
            "filename": self.charter.hard_cases.filename_dates,
        }
        for pol, wanted in want.items():
            have = sum(1 for p in planted.values() if p == pol)
            if have < wanted:
                raise SystemExit(
                    f"docplan: hard_cases wants {wanted} {pol} fact(s) but "
                    f"only {have} eligible engagement fact(s) exist; lower "
                    f"the knob or raise engagements.count"
                )
        hosts: dict[str, list[ManifestEntry]] = {f: [] for f in planted}
        for entry in entries:
            for kf in entry.key_facts:
                if kf.location != "body":
                    hosts.setdefault(kf.fact_id, []).append(entry)
        for fid, pol in planted.items():
            docs = hosts[fid]
            if len(docs) != 1:
                raise SystemExit(
                    f"docplan: hard-case fact {fid} ({pol}) must be planted "
                    f"in exactly one document, found {len(docs)}"
                )
            if pol == "signature_page" and docs[0].format != "pdf":
                raise SystemExit(
                    f"docplan: signature_page fact {fid} landed in "
                    f"{docs[0].path!r}, which is not page-addressable (pdf)"
                )


def build_manifest(
    charter: Charter,
    foundation: Foundation,
    finance: FinanceLedger,
    engagements: EngagementsLedger,
) -> list[ManifestEntry]:
    return _Planner(charter, foundation, finance, engagements).build()


def run_docplan(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "charter", "foundation", "fabric")
    if paths.manifest_jsonl.exists():
        # Immutable after first write: authored DocIR and rendered files key
        # off doc ids; replanning would orphan them.
        print(f"docplan: {paths.manifest_jsonl} exists, nothing to do")
        return 0

    charter = load_charter(paths)
    entries = build_manifest(
        charter,
        load_foundation(paths),
        load_finance(paths),
        load_engagements(paths),
    )
    save_manifest(paths, entries)

    mention_map = MentionMap(
        slug=charter.slug,
        mentions=[
            MentionRecord(
                doc_id=e.doc_id, entity=m.entity, surface=m.surface, kind=m.kind
            )
            for e in entries
            for m in e.mentions
        ],
    )
    write_model(paths.mention_map_json, mention_map)

    state.mark_done("docplan", inputs_hash=sha256_file(paths.engagements_json))
    save_state(paths, state)
    print(
        f"docplan: {len(entries)} docs, {len(mention_map.mentions)} planned "
        f"mentions -> {paths.manifest_jsonl}"
    )
    return 0
