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
    "acl": "orgsmith/acl@1",
    "manifest_entry": "orgsmith/manifest-entry@1",
    "mention_map": "orgsmith/mention-map@1",
    "graph_expected": "orgsmith/graph-expected@1",
    "work_order": "orgsmith/work-order@1",
    "enrichment_deliverable": "orgsmith/enrichment-deliverable@1",
    "authoring_deliverable": "orgsmith/authoring-deliverable@1",
    "docir": "orgsmith/docir@1",
    "state": "orgsmith/state@1",
    "scan_pages": "orgsmith/scan-pages@1",
    "review_sample": "orgsmith/review-sample@1",
    "review_finding": "orgsmith/review-finding@1",
    "review_findings": "orgsmith/review-findings@1",
    "corpus_metrics": "orgsmith/corpus-metrics@1",
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
    # M5+: decks and mail. Additive with zero defaults so pre-M5 recipes
    # and committed charters keep loading and summing unchanged.
    pptx: int = 0
    eml: int = 0

    @property
    def total(self) -> int:
        return self.docx + self.pdf + self.xlsx + self.pptx + self.eml


class DocCulture(StrictModel):
    target_docs: int = Field(gt=0)
    date_range: tuple[date, date]
    format_mix: FormatMix
    # M5+ transforms, all default off. scanned_ratio: fraction of pdf docs
    # rendered as degraded raster scans; ocr_layer_rate: fraction of those
    # scans carrying a synthetic OCR text layer (the rest are image-only);
    # legacy_ratio: fraction of office docs converted to .doc/.xls/.ppt.
    scanned_ratio: float = Field(ge=0.0, le=1.0, default=0.0)
    legacy_ratio: float = Field(ge=0.0, le=1.0, default=0.0)
    ocr_layer_rate: float = Field(ge=0.0, le=1.0, default=0.0)

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
        if self.ocr_layer_rate > 0 and self.scanned_ratio == 0:
            raise ValueError(
                "ocr_layer_rate requires scanned_ratio > 0; an OCR layer "
                "only exists on scanned documents"
            )
        return self


class FinanceProfile(StrictModel):
    base_revenue: int = Field(gt=0, description="first full fiscal year, USD")
    growth_rate: float = Field(ge=-0.5, le=2.0)
    # CALIBRATION ONLY, and this changed meaning in M8. It used to define
    # every year: expense_total = revenue * expense_ratio, with the
    # categories split out of it by fixed weights, which is why every line
    # moved in lockstep with fees forever (rf:finance-1, rf:finance-2).
    #
    # Now the categories are computed from what actually drives them and the
    # total is their sum, so the causality is inverted and this ratio sizes
    # the P&L exactly once: in the first FULL fiscal year. Afterwards the
    # realized ratio drifts on its own, and a firm whose costs outrun its
    # fees can post a loss. Read it as "how expensive this firm is out of the
    # gate", not as an invariant it is held to. See fabric/finance.py.
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
    # M6+: multi-affiliation external people appear in rendered documents
    # under both employers, era-appropriate per doc date. Default inert on
    # the existing schema id.
    affiliations_in_docs: bool = False

    @model_validator(mode="after")
    def _check(self) -> "GraphTargets":
        if self.affiliations_in_docs and self.multi_affiliations < 1:
            raise ValueError(
                "affiliations_in_docs requires multi_affiliations >= 1; "
                "without a multi-affiliation person there is no employer "
                "boundary to surface in documents"
            )
        return self


class HardCases(StrictModel):
    """Hard-to-find fact planting (M3+). Defaults keep the knobs off so
    recipes and committed orgs from before them regenerate byte-identically.

    signature_page_facts: engagement fees that appear ONLY on the signature
    page of their engagement letter (pdf), injected at render time.
    filename_dates: meeting dates that appear ONLY in the minutes filename;
    the document text carries no date in any form."""

    signature_page_facts: int = Field(ge=0, default=0)
    filename_dates: int = Field(ge=0, default=0)


class RosterChurn(StrictModel):
    """The roster's time dimension (M8). ON by default: a firm where nobody
    is ever hired, promoted, or leaves is the shape the review board
    indicted (`rf:orgreal-1`), so a frozen roster is now the opt-out rather
    than the default. Set both to 0 for the pre-M8 shape.

    Counts, not rates, matching the surname_collisions / nickname_aliases /
    multi_affiliations idiom: a recipe asks for a shape and the generator
    plants exactly it. A count also makes the fixture a specimen rather than
    a sample, which is the house position -- an org must CONTAIN the case,
    not contain it on average.

    Both degrade rather than crash when the roster cannot host them, because
    unlike the knobs above these default ON and every recipe in the repo is
    5-6 people. The degradation is reported at scaffold time and visible in
    the ledger.

    departures: seats whose incumbent leaves mid-range and is backfilled by
    a new hire into the same seat. Only seats that manage nobody are
    eligible, so the reporting tree cannot dangle: `reports_to` is a scalar
    with no time dimension, so a departing manager has nowhere to hand its
    reports to.
    promotions: people who move up one rung of their department's `titles`
    list mid-range. Recorded in `Person.title_history`.
    """

    departures: int = Field(ge=0, default=1)
    promotions: int = Field(ge=0, default=1)


class Charter(StrictModel):
    schema_id: Literal["orgsmith/charter@1"] = SCHEMA_IDS["charter"]
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str
    seed: int
    org_type: str
    founded: int = Field(ge=1800, le=2100)
    domain: str
    # CONCURRENT SEATS, not people-ever. Under roster churn a seat may be
    # held by successive people across the date range, so a 5-seat firm with
    # one departure has six people in its foundation and five at any instant.
    headcount: dict[str, int]
    # Per-dept title lists assigned in order; missing entries fall back to
    # generic titles. The first person of the first dept is the
    # CEO-equivalent and reports to no one.
    titles: dict[str, list[str]] = {}
    doc_culture: DocCulture
    finance: FinanceProfile
    engagements: EngagementPlan
    graph_targets: GraphTargets
    hard_cases: HardCases = HardCases()
    roster_churn: RosterChurn = RosterChurn()
    # Access-control posture (M4+). `open` derives an ACL where every
    # internal person reads every document; `departmental` restricts
    # engagement folders to their teams and finance to its owners.
    acl_posture: Literal["open", "departmental"] = "open"
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


class TitleSpan(StrictModel):
    """One title held over a window. Mirrors Affiliation: entries run oldest
    first, the last entry's title equals Person.title, and end=None means the
    title is still held."""

    title: str
    start: date
    end: date | None = None

    @model_validator(mode="after")
    def _check(self) -> "TitleSpan":
        if self.end is not None and self.end <= self.start:
            raise ValueError("title span end must follow start")
        return self


class Person(StrictModel):
    id: str = Field(pattern=r"^p:[a-z0-9.\-]+$")
    name: str
    aliases: list[str] = []
    title: str  # the LATEST title held; title_at() resolves it by date
    dept: str
    reports_to: str | None = None  # None = the CEO-equivalent
    employment: EmploymentSpan
    email: str
    phone: str
    persona: str = ""  # model-authored prose; ONLY field enrichment may fill
    # Empty for anyone never promoted, which is most of a roster; `title` is
    # then the answer for every date. Populated only where a title moved.
    title_history: list[TitleSpan] = []

    def title_at(self, when: date) -> str:
        """The title held on `when`. Falls back to `title` for dates outside
        every span and for an empty history, mirroring employer_at: a resolver
        that raised on a boundary date would make every caller handle a case
        the ledger cannot produce."""
        for span in self.title_history:
            if span.start <= when and (span.end is None or span.end >= when):
                return span.title
        return self.title


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


class AclGrant(StrictModel):
    person: str  # p: id
    docs: list[str]  # share-relative paths this person may read, sorted


class AclLedger(StrictModel):
    """Read-access ground truth: one grant per internal person, roster
    order. Derived (never authored) from the charter's posture plus the
    manifest and engagement teams; external people carry no grants."""

    schema_id: Literal["orgsmith/acl@1"] = SCHEMA_IDS["acl"]
    slug: str
    posture: Literal["open", "departmental"]
    grants: list[AclGrant]


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
    "briefing_deck",  # pptx
    "engagement_email",  # eml
]

DocFormat = Literal[
    "docx", "pdf", "xlsx", "pptx", "eml", "doc", "xls", "ppt"
]

# Legacy binaries occupy their modern format's format_mix bucket; docplan
# swaps format and extension only after quota accounting, and validators
# recover the bucket through this map.
BASE_FORMAT = {"doc": "docx", "xls": "xlsx", "ppt": "pptx"}


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


class ScanPages(StrictModel):
    """True per-page text of a scanned document, archived at render time
    before rasterization. This is the text-obligation oracle for image-only
    scans, whose rendered pages expose nothing extractable."""

    schema_id: Literal["orgsmith/scan-pages@1"] = SCHEMA_IDS["scan_pages"]
    doc_id: str
    pages: list[str]


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


class Generator(StrictModel):
    """Which model, at which effort, authored one batch.

    A RECORD, not an oracle. Self-reported by the skill that dispatched the
    pass and not recomputable from artifacts, so no validator rule may ever
    reference it: a rule would fake a guarantee the system cannot make.
    Optional and inert by default, which is what keeps deliverables written
    before it existed loading unchanged against the same schema ids.
    """

    model: str = Field(min_length=1)
    effort: str = Field(min_length=1)


class PersonaEnrichment(StrictModel):
    person_id: str
    persona: str = Field(min_length=40)


class EnrichmentDeliverable(StrictModel):
    schema_id: Literal["orgsmith/enrichment-deliverable@1"] = SCHEMA_IDS[
        "enrichment_deliverable"
    ]
    work_order_id: str
    personas: list[PersonaEnrichment]
    generator: Generator | None = None


class AuthoringDeliverable(StrictModel):
    schema_id: Literal["orgsmith/authoring-deliverable@1"] = SCHEMA_IDS[
        "authoring_deliverable"
    ]
    work_order_id: str
    docs: list[DocIR]
    generator: Generator | None = None


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
    # Planted-ambiguity classes ("ambiguity:<class>"), derived from the
    # ledgers at emit time so pre-existing orgs gain them on re-emission
    # without touching frozen artifacts.
    tags: list[str] = []


class GraphExpected(StrictModel):
    schema_id: Literal["orgsmith/graph-expected@1"] = SCHEMA_IDS["graph_expected"]
    slug: str
    entities: list[GraphEntityExpected]
    edges: list[GraphEdge]


class ExtractionQuestion(StrictModel):
    """One planted fact to extract: the exact surface form and where it
    lives. `location` is the difficulty class: body text, the pdf's
    signature page, or only the filename."""

    id: str  # xq:0001
    fact_id: str
    question: str
    expected_value: str  # exact rendered surface
    expected_docs: list[str]  # share-relative paths, sorted
    location: LocationPolicy = "body"
    tags: list[str] = []


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


class VisibilityAnswers(StrictModel):
    """Same doc-set contract as retrieval: per question (one per internal
    person), the exact set of share paths that person may read."""

    suite: Literal["visibility"]
    answers: list[RetrievalAnswerItem]


class ExtractionAnswerItem(StrictModel):
    id: str
    value: str
    docs: list[str]  # where the value was found; must match expected_docs


class ExtractionAnswers(StrictModel):
    suite: Literal["extraction"]
    answers: list[ExtractionAnswerItem]


# --------------------------------------------------------------------------
# the quality instrument: sample, metrics, and the review board's findings
#
# Everything below observes authored prose and reports. None of it gates:
# no validator rule may reference a review finding or a metric, because
# thresholds are unknown and prose quality is not recomputable from ground
# truth the way a planted fact is. The metric measures, the board judges,
# the human decides.
# --------------------------------------------------------------------------


class SampledDoc(StrictModel):
    doc_id: str
    path: str  # share-relative
    genre: Genre
    format: DocFormat
    date: date
    stratum: str  # why this doc is in the sample
    words: int


class ReviewSample(StrictModel):
    """A deterministic stratified reading list for the board.

    Drawn from the `review.sample` seed stream so two runs over an unchanged
    org select the same docs in the same order.
    """

    schema_id: Literal["orgsmith/review-sample@1"] = SCHEMA_IDS["review_sample"]
    slug: str
    docs: list[SampledDoc]
    # Strata the org could not fill (e.g. a genre holding one doc). Recorded
    # rather than raised: a thin corpus is a smaller sample, not an error.
    thin_strata: list[str] = []


ReviewDimension = Literal[
    "org_realism",
    "finance_realism",
    "narrative_consistency",
    "document_plausibility",
    "graph_acl_naturalness",
    # The dimension no fresh-context author can self-check: nothing in the
    # pipeline holds two authored documents at once, so only a reader with
    # the whole sample in view can see the same voice twice.
    "cross_document_voice",
]

ReviewSeverity = Literal["blocker", "major", "minor", "note"]


class ReviewFinding(StrictModel):
    schema_id: Literal["orgsmith/review-finding@1"] = SCHEMA_IDS["review_finding"]
    id: str = Field(pattern=r"^rf:[a-z0-9][a-z0-9._-]*$")
    dimension: ReviewDimension
    severity: ReviewSeverity
    # Docs the finding is about. Empty is legal: a corpus-level finding
    # ("every letter opens the same way") belongs to no single document.
    docs: list[str] = []
    summary: str = Field(min_length=1)
    evidence: str = ""


class ReviewFindings(StrictModel):
    """The board's deliverable: one reviewer's findings for one org.

    Same shape of contract as an authoring deliverable -- validated and
    merged all-or-nothing by `review --ingest`, never trusted as written.
    """

    schema_id: Literal["orgsmith/review-findings@1"] = SCHEMA_IDS["review_findings"]
    slug: str
    dimension: ReviewDimension
    findings: list[ReviewFinding] = []
    generator: Generator | None = None


class DocMetric(StrictModel):
    doc_id: str
    genre: Genre
    words: int
    target_words: int

    @property
    def ratio(self) -> float:
        return self.words / self.target_words if self.target_words else 0.0


class SimilarPair(StrictModel):
    """Two same-genre docs and their n-gram overlap.

    High overlap is a measurement, not a verdict: real firms genuinely reuse
    engagement-letter templates. The board judges whether it reads as reuse
    or as the generator running out of ideas.
    """

    doc_a: str
    doc_b: str
    genre: Genre
    jaccard: float


class CorpusMetrics(StrictModel):
    schema_id: Literal["orgsmith/corpus-metrics@1"] = SCHEMA_IDS["corpus_metrics"]
    slug: str
    docs: list[DocMetric]
    similar_pairs: list[SimilarPair] = []
