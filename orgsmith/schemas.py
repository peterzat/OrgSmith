"""All inter-stage contracts. The keystone file.

Every artifact that crosses a stage boundary (or the airlock) is one of
these pydantic models, tagged with a schema id of the form
``orgsmith/<kind>@<version>``. Bump the version when a change is not
backward-compatible; ingest rejects deliverables with the wrong id.

Conventions for ids:
  p:first.last      internal person          x:slug        external org
  xp:first.last     external person          d:0007        document
  E-2021-003        engagement (doubles as in-world numbering)
  f:E-2021-003.fee  fact (owned by exactly one ledger record)
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_IDS = {
    "charter": "orgsmith/charter@1",
    "foundation": "orgsmith/foundation@1",
    "finance": "orgsmith/finance@1",
    "engagements": "orgsmith/engagements@1",
    "graph": "orgsmith/graph@1",
    "manifest_entry": "orgsmith/manifest-entry@1",
    "mention_map": "orgsmith/mention-map@1",
    "graph_expected": "orgsmith/graph-expected@1",
    "work_order": "orgsmith/work-order@1",
    "enrichment_deliverable": "orgsmith/enrichment-deliverable@1",
    "authoring_deliverable": "orgsmith/authoring-deliverable@1",
    "docir": "orgsmith/docir@1",
    "state": "orgsmith/state@1",
}


class StrictModel(BaseModel):
    """Base for every contract: unknown fields are rejected, not ignored."""

    model_config = ConfigDict(extra="forbid")


def dump_json(model: BaseModel) -> str:
    """Canonical serialization: pydantic field order and dict insertion
    order, both deterministic. Never sort keys: recipe dicts like
    `headcount` are order-significant (first dept holds the CEO)."""
    data = model.model_dump(mode="json")
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def write_model(path: Path, model: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(model), encoding="utf-8")


# --------------------------------------------------------------------------
# charter
# --------------------------------------------------------------------------


class FormatMix(StrictModel):
    docx: int = 0
    pdf: int = 0
    xlsx: int = 0

    @property
    def total(self) -> int:
        return self.docx + self.pdf + self.xlsx


class DocCulture(StrictModel):
    target_docs: int = Field(gt=0)
    date_range: tuple[date, date]
    format_mix: FormatMix

    @model_validator(mode="after")
    def _check(self) -> "DocCulture":
        start, end = self.date_range
        if start >= end:
            raise ValueError("date_range start must precede end")
        if self.format_mix.total != self.target_docs:
            raise ValueError(
                f"format_mix sums to {self.format_mix.total}, "
                f"target_docs is {self.target_docs}"
            )
        return self


class FinanceProfile(StrictModel):
    base_revenue: int = Field(gt=0, description="first full fiscal year, USD")
    growth_rate: float = Field(ge=-0.5, le=2.0)
    expense_ratio: float = Field(gt=0.0, lt=1.0)


class EngagementPlan(StrictModel):
    count: int = Field(gt=0)
    # Service-line names used for engagement titles; empty = fabric's
    # generic defaults. Additive: recipes written before this field exist
    # unchanged.
    services: list[str] = []


class GraphTargets(StrictModel):
    external_orgs: int = Field(ge=1)
    external_people: int = Field(ge=1)
    # Ambiguity knobs (M2+). All default OFF so recipes and committed orgs
    # from before these knobs regenerate byte-identically.
    min_mentions_per_person: int = Field(ge=0, default=0)
    surname_collisions: int = Field(ge=0, default=0)
    nickname_aliases: int = Field(ge=0, default=0)
    multi_affiliations: int = Field(ge=0, default=0)


class Charter(StrictModel):
    schema_id: Literal["orgsmith/charter@1"] = SCHEMA_IDS["charter"]
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str
    seed: int
    org_type: str
    founded: int = Field(ge=1800, le=2100)
    domain: str
    headcount: dict[str, int]
    # Per-dept title lists assigned in order; missing entries fall back to
    # generic titles. The first person of the first dept is the
    # CEO-equivalent and reports to no one.
    titles: dict[str, list[str]] = {}
    doc_culture: DocCulture
    finance: FinanceProfile
    engagements: EngagementPlan
    graph_targets: GraphTargets
    narrative: str

    @model_validator(mode="after")
    def _check(self) -> "Charter":
        if sum(self.headcount.values()) < 2:
            raise ValueError("headcount must total at least 2")
        if any(n <= 0 for n in self.headcount.values()):
            raise ValueError("headcount entries must be positive")
        if self.doc_culture.date_range[0].year < self.founded:
            raise ValueError("date_range must not start before founding year")
        return self


# --------------------------------------------------------------------------
# foundation
# --------------------------------------------------------------------------


class EmploymentSpan(StrictModel):
    start: date
    end: date | None = None  # None = still employed

    @model_validator(mode="after")
    def _check(self) -> "EmploymentSpan":
        if self.end is not None and self.end <= self.start:
            raise ValueError("employment end must follow start")
        return self


class Person(StrictModel):
    id: str = Field(pattern=r"^p:[a-z0-9.\-]+$")
    name: str
    aliases: list[str] = []
    title: str
    dept: str
    reports_to: str | None = None  # None = the CEO-equivalent
    employment: EmploymentSpan
    email: str
    phone: str
    persona: str = ""  # model-authored prose; ONLY field enrichment may fill


class ExternalOrg(StrictModel):
    id: str = Field(pattern=r"^x:[a-z0-9.\-]+$")
    name: str
    org_type: str


class Affiliation(StrictModel):
    org: str  # x: id
    start: date | None = None
    end: date | None = None  # None = current


class ExternalPerson(StrictModel):
    id: str = Field(pattern=r"^xp:[a-z0-9.\-]+$")
    name: str
    org: str  # x: id of the CURRENT employer
    title: str
    email: str
    # Full affiliation history when the multi-affiliation knob is on; the
    # last entry mirrors `org`. Empty for single-employer people.
    affiliations: list[Affiliation] = []


class TimelineEvent(StrictModel):
    date: date
    summary: str
    ground_truth_tags: list[str] = []


class Foundation(StrictModel):
    schema_id: Literal["orgsmith/foundation@1"] = SCHEMA_IDS["foundation"]
    slug: str
    people: list[Person]
    external_orgs: list[ExternalOrg]
    external_people: list[ExternalPerson]
    timeline: list[TimelineEvent]

    def person(self, pid: str) -> Person:
        for p in self.people:
            if p.id == pid:
                return p
        raise KeyError(pid)


# --------------------------------------------------------------------------
# ledgers: finance, engagements (fact spine), graph
# --------------------------------------------------------------------------


class FiscalYear(StrictModel):
    year: int
    revenue: int  # USD; == sum(quarters)
    quarters: list[int]  # Q1..Q4
    expenses: dict[str, int]  # category -> USD

    @model_validator(mode="after")
    def _check(self) -> "FiscalYear":
        if len(self.quarters) != 4:
            raise ValueError("need exactly 4 quarters")
        return self


class LedgerCheck(StrictModel):
    name: str
    ok: bool
    detail: str


class FinanceLedger(StrictModel):
    schema_id: Literal["orgsmith/finance@1"] = SCHEMA_IDS["finance"]
    slug: str
    years: list[FiscalYear]
    checks: list[LedgerCheck]


# Where a planted fact is allowed to surface. `body` is the ordinary case;
# the hard-case policies constrain the fact to exactly one location and
# validators enforce absence everywhere else. `signature_page` applies only
# to page-addressable formats (pdf); `filename` only to filename-safe
# surfaces (date facts).
LocationPolicy = Literal["body", "signature_page", "filename"]


class Fact(StrictModel):
    """One planted, render-ready fact. `rendered` is the exact surface form
    substituted for ``{{fact:<id>}}``; validators look for it verbatim in
    document text."""

    id: str = Field(pattern=r"^f:[A-Za-z0-9.\-]+$")
    kind: Literal["money", "date", "text"]
    value: Union[int, str]
    rendered: str
    location_policy: LocationPolicy = "body"


class Engagement(StrictModel):
    id: str = Field(pattern=r"^E-\d{4}-\d{3}$")
    title: str
    client: str  # x: id
    start: date
    end: date
    fee: int  # USD
    internal_participants: list[str]  # p: ids
    external_participants: list[str]  # xp: ids
    summary: str
    facts: list[Fact]

    @model_validator(mode="after")
    def _check(self) -> "Engagement":
        if self.end <= self.start:
            raise ValueError("engagement end must follow start")
        return self


class EngagementsLedger(StrictModel):
    schema_id: Literal["orgsmith/engagements@1"] = SCHEMA_IDS["engagements"]
    slug: str
    engagements: list[Engagement]

    def fact_index(self) -> dict[str, Fact]:
        index: dict[str, Fact] = {}
        for eng in self.engagements:
            for fact in eng.facts:
                if fact.id in index:
                    raise ValueError(f"duplicate fact id {fact.id}")
                index[fact.id] = fact
        return index


class GraphEdge(StrictModel):
    src: str
    dst: str
    kind: Literal["reports_to", "works_at", "client_of", "participant"]
    start: date | None = None
    end: date | None = None


class GraphLedger(StrictModel):
    schema_id: Literal["orgsmith/graph@1"] = SCHEMA_IDS["graph"]
    slug: str
    entities: list[str]
    edges: list[GraphEdge]


# --------------------------------------------------------------------------
# docplan
# --------------------------------------------------------------------------

Genre = Literal[
    "engagement_letter",  # pdf
    "kickoff_memo",  # docx
    "meeting_minutes",  # docx
    "status_report",  # docx
    "company_overview",  # docx
    "financial_summary",  # xlsx, static (no model pass)
]

DocFormat = Literal["docx", "pdf", "xlsx"]


class PlannedMention(StrictModel):
    """One entity the doc must name, with the exact surface form the
    mention-echo validator looks for in extractable text."""

    entity: str  # p:/xp:/x: id
    surface: str
    kind: Literal["person", "org"] = "person"


class KeyFact(StrictModel):
    """A planted fact with its placement policy. Mirrors the owning ledger
    Fact's `location_policy` so manifest consumers need not join against the
    ledger to know where a fact is allowed to appear."""

    fact_id: str
    location: LocationPolicy = "body"


class ManifestEntry(StrictModel):
    schema_id: Literal["orgsmith/manifest-entry@1"] = SCHEMA_IDS["manifest_entry"]
    doc_id: str = Field(pattern=r"^d:\d{4}$")
    path: str  # share-relative, realistic filename
    title: str
    genre: Genre
    format: DocFormat
    date: date
    authors: list[str]  # p: ids
    participants: list[str] = []  # p:/xp: ids mentioned or attending
    engagement: str | None = None  # E- id
    facts_refs: list[str] = []  # f: ids that MUST appear in the doc
    # Additive since M2 (defaults keep pre-M2 manifests readable):
    mentions: list[PlannedMention] = []
    key_facts: list[KeyFact] = []
    authoring: Literal["batchable", "static"] = "batchable"
    render_params: dict[str, Union[int, str]] = {}
    rev: int = 0


class MentionRecord(StrictModel):
    doc_id: str
    entity: str
    surface: str
    kind: Literal["person", "org"] = "person"


class MentionMap(StrictModel):
    """Flat ground-truth view of every planned mention, for external
    consumers who should not need to parse the manifest."""

    schema_id: Literal["orgsmith/mention-map@1"] = SCHEMA_IDS["mention_map"]
    slug: str
    mentions: list[MentionRecord]


def surface_in_text(surface: str, text: str) -> bool:
    """Whether a mention surface occurs in text as a standalone token run.

    Substring containment would let a short alias ("Jen") match inside a
    longer word ("Jennifer"); non-word lookarounds require the surface to
    stand on its own. Shared by authoring ingest and the MENT-01 validator
    so both sides of the mention contract use identical semantics."""
    return re.search(rf"(?<!\w){re.escape(surface)}(?!\w)", text) is not None


# --------------------------------------------------------------------------
# DocIR: the model's deliverable unit for one document
# --------------------------------------------------------------------------


class Block(StrictModel):
    kind: Literal["heading", "paragraph", "list", "table", "sigblock"]
    # heading/paragraph: text. list: items. table: header+rows. sigblock:
    # signer p:/xp: ids; render pulls name/title and the ledger date.
    text: str = ""
    level: int = 1  # headings only
    items: list[str] = []
    header: list[str] = []
    rows: list[list[str]] = []
    signers: list[str] = []


class DocIR(StrictModel):
    schema_id: Literal["orgsmith/docir@1"] = SCHEMA_IDS["docir"]
    doc_id: str
    blocks: list[Block]


# --------------------------------------------------------------------------
# airlock: work orders and deliverables
# --------------------------------------------------------------------------


class PersonBrief(StrictModel):
    id: str
    name: str
    title: str
    dept: str
    persona: str = ""


class FactBrief(StrictModel):
    id: str
    hint: str  # human description, e.g. "engagement fee"
    # The rendered value is deliberately withheld: the model must place the
    # placeholder, never the number.


class DocBrief(StrictModel):
    doc_id: str
    title: str
    genre: Genre
    date: date
    authors: list[PersonBrief]
    participants: list[PersonBrief]
    engagement_summary: str = ""
    facts: list[FactBrief] = []
    # Names the document must contain verbatim (surface forms); enforced at
    # ingest and re-checked against rendered text by the validator.
    mentions: list[PlannedMention] = []
    target_words: int = 250
    guidance: str = ""


class WorkOrder(StrictModel):
    schema_id: Literal["orgsmith/work-order@1"] = SCHEMA_IDS["work_order"]
    id: str  # e.g. wo:author:0001
    stage: Literal["foundation", "author"]
    slug: str
    org_name: str
    org_type: str
    narrative: str
    instructions: str
    docs: list[DocBrief] = []  # author stage
    people: list[PersonBrief] = []  # foundation enrichment stage
    deliverable_schema: str  # name of the expected deliverable schema id


class PersonaEnrichment(StrictModel):
    person_id: str
    persona: str = Field(min_length=40)


class EnrichmentDeliverable(StrictModel):
    schema_id: Literal["orgsmith/enrichment-deliverable@1"] = SCHEMA_IDS[
        "enrichment_deliverable"
    ]
    work_order_id: str
    personas: list[PersonaEnrichment]


class AuthoringDeliverable(StrictModel):
    schema_id: Literal["orgsmith/authoring-deliverable@1"] = SCHEMA_IDS[
        "authoring_deliverable"
    ]
    work_order_id: str
    docs: list[DocIR]


# --------------------------------------------------------------------------
# golden evals: emitted ground truth and the external answers contract
# --------------------------------------------------------------------------


class RetrievalQuestion(StrictModel):
    id: str  # q:0001
    question: str
    expected_docs: list[str]  # share-relative paths, sorted
    tags: list[str] = []


class GraphEntityExpected(StrictModel):
    id: str
    canonical: str
    aliases: list[str] = []  # any of these earn full credit for the entity
    kind: Literal["person", "org"]


class GraphExpected(StrictModel):
    schema_id: Literal["orgsmith/graph-expected@1"] = SCHEMA_IDS["graph_expected"]
    slug: str
    entities: list[GraphEntityExpected]
    edges: list[GraphEdge]


class RetrievalAnswerItem(StrictModel):
    id: str
    docs: list[str]


class RetrievalAnswers(StrictModel):
    suite: Literal["retrieval"]
    answers: list[RetrievalAnswerItem]


class GraphAnswerEntity(StrictModel):
    name: str
    kind: Literal["person", "org"]


class GraphAnswerEdge(StrictModel):
    src: str  # entity name (canonical or alias)
    dst: str
    kind: str


class GraphAnswers(StrictModel):
    suite: Literal["graph"]
    entities: list[GraphAnswerEntity]
    edges: list[GraphAnswerEdge] = []
