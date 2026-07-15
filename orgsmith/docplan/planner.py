"""docplan: the immutable document manifest.

Pure. Decides every document's identity before any prose exists: path with
a realistic filename, genre, format, date, authors (employed on that
date), engagement link, and which ledger facts MUST appear in the text
(facts_refs). The manifest is append-only ground truth; soft fixes bump
`rev`, they never rewrite identity fields.
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
from ..fabric.engagements import minutes_date
from ..naming import check_relpath, sanitize_component
from ..paths import OrgPaths
from ..seeds import rng
from ..schemas import (
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

    # --- genre planners -------------------------------------------------

    def plan_engagement_docs(self) -> None:
        engs = self.engagements.engagements
        for idx, eng in enumerate(engs):
            client = sanitize_component(self._client_name(eng))
            folder = f"Engagements/{client}"
            service = eng.title.split(" for ")[0]
            duration = (eng.end - eng.start).days

            letter_date = _clamp(
                eng.start - timedelta(days=10), self.range_start, eng.start
            )
            fee_ref = f"f:{eng.id}.fee"
            letter_params = {}
            if self.policy.get(fee_ref) == "signature_page":
                # Render injects the fee into the signature page; the model
                # is never briefed for it (see authoring.contexts).
                letter_params = {"sig_fact": fee_ref}
            self._add(
                path=f"{folder}/{letter_date:%Y.%m.%d} - Engagement Letter - "
                f"{client} - EXECUTED.pdf",
                title=f"Engagement Letter: {eng.title}",
                genre="engagement_letter",
                format="pdf",
                date=letter_date,
                authors=[self.ceo.id],
                participants=eng.internal_participants + eng.external_participants,
                engagement=eng.id,
                facts_refs=[fee_ref, f"f:{eng.id}.start", f"f:{eng.id}.client"],
                render_params=letter_params,
            )

            if idx < 2:  # kickoff memos for the first two engagements
                kd = self._clamp_range(eng.start + timedelta(days=3))
                self._add(
                    path=f"{folder}/{kd:%Y.%m.%d} - Kickoff Memo - {service}.docx",
                    title=f"Kickoff Memo: {eng.title}",
                    genre="kickoff_memo",
                    format="docx",
                    date=kd,
                    authors=[self._author_for(eng, kd, junior=False).id],
                    participants=eng.internal_participants
                    + eng.external_participants,
                    engagement=eng.id,
                    facts_refs=[f"f:{eng.id}.start", f"f:{eng.id}.client"],
                )

            md = minutes_date(eng.start, eng.end, self.range_start, self.range_end)
            md_ref = f"f:{eng.id}.minutes-date"
            extra_key_facts = []
            if self.policy.get(md_ref) == "filename":
                # The filename (built below from the same shared helper the
                # fabric fact used) is the only place this date may appear;
                # it never enters facts_refs because FACT-01 demands body
                # presence for those.
                extra_key_facts = [KeyFact(fact_id=md_ref, location="filename")]
            self._add(
                path=f"{folder}/Meeting Minutes {md:%Y-%m-%d} - {client}.docx",
                title=f"Meeting Minutes: {eng.title}",
                genre="meeting_minutes",
                format="docx",
                date=md,
                authors=[self._author_for(eng, md, junior=True).id],
                participants=eng.internal_participants + eng.external_participants,
                engagement=eng.id,
                facts_refs=[f"f:{eng.id}.client"],
                extra_key_facts=extra_key_facts,
            )

            if idx in (0, len(engs) - 1):  # status reports: first and last
                sd = self._clamp_range(
                    eng.start + timedelta(days=int(duration * 0.75))
                )
                # A signature-page-only fee may surface nowhere but the
                # letter's signature page, so it leaves other docs' refs.
                report_refs = [
                    ref
                    for ref in (fee_ref, f"f:{eng.id}.client")
                    if self.policy.get(ref, "body") == "body"
                ]
                self._add(
                    path=f"{folder}/{sd:%Y.%m.%d} - Status Report - {client} "
                    f"v2 FINAL.docx",
                    title=f"Status Report: {eng.title}",
                    genre="status_report",
                    format="docx",
                    date=sd,
                    authors=[self._author_for(eng, sd, junior=False).id],
                    participants=eng.internal_participants,
                    engagement=eng.id,
                    facts_refs=report_refs,
                )

    def plan_deck_docs(self) -> None:
        """Briefing decks: one per engagement, first engagements first, when
        the recipe's format_mix asks for pptx documents."""
        want = self.charter.doc_culture.format_mix.pptx
        if want == 0:
            return
        engs = self.engagements.engagements
        if want > len(engs):
            raise SystemExit(
                f"docplan: format_mix.pptx wants {want} deck(s) but only "
                f"{len(engs)} engagement(s) exist; lower the mix or raise "
                f"engagements.count"
            )
        for eng in engs[:want]:
            client = sanitize_component(self._client_name(eng))
            dd = self._clamp_range(
                eng.start + timedelta(days=int((eng.end - eng.start).days * 0.25))
            )
            deck_refs = [
                ref
                for ref in (f"f:{eng.id}.start", f"f:{eng.id}.client")
                if self.policy.get(ref, "body") == "body"
            ]
            self._add(
                path=f"Engagements/{client}/{dd:%Y.%m.%d} - Briefing Deck - "
                f"{client}.pptx",
                title=f"Briefing Deck: {eng.title}",
                genre="briefing_deck",
                format="pptx",
                date=dd,
                authors=[self._author_for(eng, dd, junior=False).id],
                participants=eng.internal_participants
                + eng.external_participants,
                engagement=eng.id,
                facts_refs=deck_refs,
            )

    def plan_email_docs(self) -> None:
        """Engagement mail: format_mix.eml messages assigned round-robin
        over engagements (wrapping is fine; a thread carries many mails),
        dated deterministically inside each engagement's window."""
        want = self.charter.doc_culture.format_mix.eml
        if want == 0:
            return
        engs = self.engagements.engagements
        rounds: dict[str, int] = {}
        for i in range(want):
            eng = engs[i % len(engs)]
            k = rounds.get(eng.id, 0)
            rounds[eng.id] = k + 1
            client = sanitize_component(self._client_name(eng))
            service = eng.title.split(" for ")[0]
            ed = self._clamp_range(eng.start + timedelta(days=30 + 45 * k))
            refs = [
                ref
                for ref in (f"f:{eng.id}.client",)
                if self.policy.get(ref, "body") == "body"
            ]
            self._add(
                path=f"Engagements/{client}/{ed:%Y.%m.%d} - Email {k + 1} - "
                f"{service} - {client}.eml",
                title=f"RE: {eng.title}",
                genre="engagement_email",
                format="eml",
                date=ed,
                authors=[self._author_for(eng, ed, junior=False).id],
                participants=eng.internal_participants
                + eng.external_participants,
                engagement=eng.id,
                facts_refs=refs,
            )

    def plan_firm_docs(self) -> None:
        first_eng = self.engagements.engagements[0]
        mid = self.range_start + (self.range_end - self.range_start) / 2
        mid = self._clamp_range(max(mid, first_eng.start + timedelta(days=30)))
        self._add(
            path=f"Firm/Firm Overview {mid:%Y} v3.docx",
            title="Firm Overview",
            genre="company_overview",
            format="docx",
            date=mid,
            authors=[self.ceo.id],
            participants=[self.ceo.id],
            engagement=None,
            facts_refs=[f"f:{first_eng.id}.client"],
        )

        fy_years = [
            fy.year
            for fy in self.finance.years
            if date(fy.year + 1, 1, 15) <= self.range_end
        ][-2:]
        for year in fy_years:
            pub = date(year + 1, 1, 15)
            author = (
                self.ops_lead if _employed_at(self.ops_lead, pub) else self.ceo
            )
            self._add(
                path=f"Finance/FY{year} Financial Summary.xlsx",
                title=f"FY{year} Financial Summary",
                genre="financial_summary",
                format="xlsx",
                date=pub,
                authors=[author.id],
                participants=[],
                engagement=None,
                facts_refs=[],
                authoring="static",
                render_params={"year": year},
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
                    and d["genre"] in ("meeting_minutes", "kickoff_memo")
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
        """Scan selection: the oldest pdfs by (date, path) get flagged, per
        scanned_ratio; ocr_layer_rate of those keep a synthetic OCR text
        layer, drawn from a NEW seed stream so knobs-off recipes never
        consume it and regenerate byte-identically. Paths stay .pdf: the
        filename is immutable eval/ACL ground truth. A doc hosting a
        signature_page fact is never image-only, or its per-page location
        obligation would be unverifiable from extractable text."""
        culture = self.charter.doc_culture
        if culture.scanned_ratio == 0:
            return
        pdfs = sorted(
            (d for d in self.planned if d["format"] == "pdf"),
            key=lambda d: (d["date"], d["path"]),
        )
        scans = pdfs[: round(culture.scanned_ratio * len(pdfs))]
        if not scans:
            return
        layered = round(culture.ocr_layer_rate * len(scans))
        with_layer = set(
            rng(self.charter.seed, "docplan.ocr").sample(
                range(len(scans)), layered
            )
        )
        for i, doc in enumerate(scans):
            params = dict(doc.get("render_params", {}))
            params["scan"] = 1
            hosts_sig = any(
                self.policy.get(ref) == "signature_page"
                for ref in doc.get("facts_refs", [])
            )
            if i in with_layer or hosts_sig:
                params["ocr_layer"] = 1
            doc["render_params"] = params

    def build(self) -> list[ManifestEntry]:
        self.plan_engagement_docs()
        self.plan_deck_docs()
        self.plan_email_docs()
        self.plan_firm_docs()
        self.plan_mentions()
        self.plan_scans()

        mix = self.charter.doc_culture.format_mix
        want = {
            fmt: getattr(mix, fmt) for fmt in ("docx", "pdf", "xlsx", "pptx", "eml")
        }
        counts = dict.fromkeys(want, 0)
        for doc in self.planned:
            counts[doc["format"]] += 1
        if counts != want:
            raise SystemExit(
                f"docplan: format mix {counts} does not match charter {want}"
            )

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
