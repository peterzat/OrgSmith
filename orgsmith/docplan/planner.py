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
from ..fabric.engagements import LETTER_LEAD_DAYS, minutes_date
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
                first = minutes_date(start, end, self.range_start, self.range_end)
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
            return self._dedupe(dates)
        return [self._clamp_range(
            start + timedelta(days=anchor_off + rule.start_offset_days)
        )]

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
        """Engagement mail: format_mix.eml messages assigned round-robin over
        engagements (wrapping is fine; a thread carries many mails). A thread
        opens about four weeks into its engagement and its replies land a day
        or two apart, so it reads as a thread rather than as monthly memos
        (the old 45-day spacing; email-thread-spacing). The per-reply gap
        draws from its OWN seed stream so the cadence never perturbs another
        pass's randomness."""
        want = getattr(self.charter.doc_culture.format_mix, rule.optional_count)
        if want == 0:
            return
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
        return entries

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
