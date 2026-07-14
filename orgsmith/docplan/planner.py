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
from ..naming import check_relpath, sanitize_component
from ..paths import OrgPaths
from ..schemas import (
    Charter,
    Engagement,
    EngagementsLedger,
    FinanceLedger,
    Foundation,
    ManifestEntry,
    Person,
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

    def _add(self, **kw) -> None:
        problems = check_relpath(kw["path"])
        if problems:
            raise SystemExit(f"docplan: unsafe path: {problems}")
        if not _employed_at(self.foundation.person(kw["authors"][0]), kw["date"]):
            raise SystemExit(
                f"docplan: author {kw['authors'][0]} not employed on {kw['date']}"
            )
        kw["date"] = _clamp(kw["date"], self.range_start, self.range_end)
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
                facts_refs=[f"f:{eng.id}.fee", f"f:{eng.id}.start",
                            f"f:{eng.id}.client"],
            )

            if idx < 2:  # kickoff memos for the first two engagements
                kd = eng.start + timedelta(days=3)
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

            md = eng.start + timedelta(days=int(duration * 0.4))
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
            )

            if idx in (0, len(engs) - 1):  # status reports: first and last
                sd = eng.start + timedelta(days=int(duration * 0.75))
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
                    facts_refs=[f"f:{eng.id}.fee", f"f:{eng.id}.client"],
                )

    def plan_firm_docs(self) -> None:
        first_eng = self.engagements.engagements[0]
        mid = self.range_start + (self.range_end - self.range_start) / 2
        mid = max(mid, first_eng.start + timedelta(days=30))
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

    def build(self) -> list[ManifestEntry]:
        self.plan_engagement_docs()
        self.plan_firm_docs()

        mix = self.charter.doc_culture.format_mix
        counts = {"docx": 0, "pdf": 0, "xlsx": 0}
        for doc in self.planned:
            counts[doc["format"]] += 1
        want = {"docx": mix.docx, "pdf": mix.pdf, "xlsx": mix.xlsx}
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
            entries.append(ManifestEntry(doc_id=f"d:{i:04d}", **doc))
        return entries


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

    entries = build_manifest(
        load_charter(paths),
        load_foundation(paths),
        load_finance(paths),
        load_engagements(paths),
    )
    save_manifest(paths, entries)

    state.mark_done("docplan", inputs_hash=sha256_file(paths.engagements_json))
    save_state(paths, state)
    print(f"docplan: {len(entries)} docs -> {paths.manifest_jsonl}")
    return 0
