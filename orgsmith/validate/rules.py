"""The v0 rule catalog: ORG, DATE, FIN, FACT, FILE, MAN, PROV families."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterator

from ..artifacts import (
    load_charter,
    load_engagements,
    load_finance,
    load_foundation,
    load_graph,
    load_manifest,
    load_mention_map,
)
from ..paths import OrgPaths
from ..schemas import surface_in_text

Finding = tuple[str, str]  # (message, target)


@dataclass
class Context:
    paths: OrgPaths
    charter: object
    foundation: object
    finance: object
    engagements: object
    graph: object
    mention_map: object  # None for orgs generated before mention ground truth
    manifest: list
    _text_cache: dict = field(default_factory=dict)

    @classmethod
    def load(cls, paths: OrgPaths) -> "Context":
        return cls(
            paths=paths,
            charter=load_charter(paths),
            foundation=load_foundation(paths),
            finance=load_finance(paths),
            engagements=load_engagements(paths),
            graph=load_graph(paths),
            mention_map=load_mention_map(paths),
            manifest=load_manifest(paths),
        )

    def entry(self, doc_id: str):
        for e in self.manifest:
            if e.doc_id == doc_id:
                return e
        return None

    def doc_text(self, entry) -> str:
        """Extractable text of a rendered doc, whitespace-normalized."""
        if entry.doc_id in self._text_cache:
            return self._text_cache[entry.doc_id]
        path = self.paths.share_dir / entry.path
        if entry.format == "docx":
            import docx

            d = docx.Document(str(path))
            chunks = [p.text for p in d.paragraphs]
            for t in d.tables:
                for row in t.rows:
                    chunks.extend(c.text for c in row.cells)
            text = "\n".join(chunks)
        elif entry.format == "pdf":
            from pypdf import PdfReader

            text = "\n".join(
                page.extract_text() or "" for page in PdfReader(str(path)).pages
            )
        else:
            text = ""
        text = re.sub(r"\s+", " ", text)
        self._text_cache[entry.doc_id] = text
        return text


def _always(_ctx: Context) -> str | None:
    return None


def _needs_mentions(ctx: Context) -> str | None:
    if ctx.mention_map is None:
        return "org predates mention ground truth (no mention_map.json)"
    return None


def _needs_mention_knob(ctx: Context) -> str | None:
    absent = _needs_mentions(ctx)
    if absent:
        return absent
    if ctx.charter.graph_targets.min_mentions_per_person < 1:
        return "min_mentions_per_person knob is 0 for this recipe"
    return None


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    description: str
    check: Callable[[Context], Iterator[Finding]]
    # Returns a skip reason when the rule cannot run for this org (e.g. it
    # predates an artifact); None means run. Skips are surfaced visibly.
    available: Callable[[Context], str | None] = _always


def _employed_at(person, when) -> bool:
    emp = person.employment
    return emp.start <= when and (emp.end is None or emp.end >= when)


# --- ORG ------------------------------------------------------------------


def org_01(ctx: Context):
    roots = [p for p in ctx.foundation.people if p.reports_to is None]
    if len(roots) != 1:
        yield (
            f"expected exactly one CEO-equivalent, found {len(roots)}: "
            f"{[p.id for p in roots]}",
            "foundation.json",
        )


def org_02(ctx: Context):
    ids = {p.id for p in ctx.foundation.people}
    for p in ctx.foundation.people:
        seen = set()
        cur = p
        while cur.reports_to is not None:
            if cur.reports_to not in ids:
                yield (f"{cur.id} reports to unknown {cur.reports_to}",
                       "foundation.json")
                break
            if cur.id in seen:
                yield (f"reports_to cycle involving {cur.id}", "foundation.json")
                break
            seen.add(cur.id)
            cur = ctx.foundation.person(cur.reports_to)


# --- DATE -----------------------------------------------------------------


def date_01(ctx: Context):
    lo, hi = ctx.charter.doc_culture.date_range
    for e in ctx.manifest:
        if not (lo <= e.date <= hi):
            yield (f"doc date {e.date} outside charter range {lo}..{hi}", e.path)


def date_02(ctx: Context):
    for e in ctx.manifest:
        for author in e.authors:
            person = ctx.foundation.person(author)
            if not _employed_at(person, e.date):
                yield (
                    f"author {author} not employed on {e.date} "
                    f"(start {person.employment.start})",
                    e.path,
                )


# --- FIN ------------------------------------------------------------------


def fin_01(ctx: Context):
    for check in ctx.finance.checks:
        if not check.ok:
            yield (f"ledger check failed: {check.name} ({check.detail})",
                   "ledger/finance.json")
    for fy in ctx.finance.years:
        if sum(fy.quarters) != fy.revenue:
            yield (
                f"FY{fy.year} quarters sum {sum(fy.quarters)} != revenue "
                f"{fy.revenue}",
                "ledger/finance.json",
            )


def fin_02(ctx: Context):
    from openpyxl import load_workbook

    for e in ctx.manifest:
        if e.format != "xlsx":
            continue
        path = ctx.paths.share_dir / e.path
        if not path.exists():
            continue  # FILE-01 reports the absence
        year = int(e.render_params["year"])
        fy = next((y for y in ctx.finance.years if y.year == year), None)
        if fy is None:
            yield (f"workbook year {year} not in finance ledger", e.path)
            continue
        cached = load_workbook(path, data_only=True)["Summary"]
        if cached["F4"].value != fy.revenue:
            yield (
                f"cached revenue total {cached['F4'].value} != ledger "
                f"{fy.revenue}",
                e.path,
            )
        quarters = [cached[f"{c}4"].value for c in "BCDE"]
        if quarters != fy.quarters:
            yield (f"cached quarters {quarters} != ledger {fy.quarters}", e.path)


# --- FACT (fact echo) ------------------------------------------------------


def fact_01(ctx: Context):
    facts = ctx.engagements.fact_index()
    for e in ctx.manifest:
        if not e.facts_refs or e.format == "xlsx":
            continue
        if not (ctx.paths.share_dir / e.path).exists():
            continue
        text = ctx.doc_text(e)
        for ref in e.facts_refs:
            if ref not in facts:
                yield (f"facts_ref {ref} not in engagement ledger", e.path)
            elif facts[ref].rendered not in text:
                yield (
                    f"fact {ref} surface form {facts[ref].rendered!r} not "
                    f"found in extractable text",
                    e.path,
                )


# --- FILE -----------------------------------------------------------------


def file_01(ctx: Context):
    for e in ctx.manifest:
        path = ctx.paths.share_dir / e.path
        if not path.exists():
            yield ("manifest doc missing from share", e.path)
            continue
        try:
            if e.format == "docx":
                import docx

                docx.Document(str(path))
            elif e.format == "pdf":
                from pypdf import PdfReader

                if len(PdfReader(str(path)).pages) < 1:
                    yield ("pdf has no pages", e.path)
            elif e.format == "xlsx":
                from openpyxl import load_workbook

                load_workbook(path, data_only=True)
        except Exception as err:  # noqa: BLE001 - any reader failure is the finding
            yield (f"file does not open in native reader: {err}", e.path)


# --- MAN ------------------------------------------------------------------

_SHARE_EXTRAS = {"TOC.md"}


def man_01(ctx: Context):
    if not ctx.paths.share_dir.exists():
        yield ("share directory missing", str(ctx.paths.share_dir))
        return
    on_disk = {
        str(p.relative_to(ctx.paths.share_dir))
        for p in ctx.paths.share_dir.rglob("*")
        if p.is_file()
    }
    planned = {e.path for e in ctx.manifest}
    for extra in sorted(on_disk - planned - _SHARE_EXTRAS):
        yield ("file in share but not in manifest", extra)
    for missing in sorted(planned - on_disk):
        yield ("manifest doc missing from share", missing)


# --- MENT (mention echo) ----------------------------------------------------


def ment_01(ctx: Context):
    for record in ctx.mention_map.mentions:
        entry = ctx.entry(record.doc_id)
        if entry is None:
            yield (f"mention references unknown doc {record.doc_id}",
                   "ledger/mention_map.json")
            continue
        if not (ctx.paths.share_dir / entry.path).exists():
            continue  # FILE-01/MAN-01 report the absence
        if not surface_in_text(record.surface, ctx.doc_text(entry)):
            yield (
                f"planned mention surface {record.surface!r} "
                f"({record.entity}) not found in extractable text",
                entry.path,
            )


def ment_02(ctx: Context):
    entities = set(ctx.graph.entities)
    for record in ctx.mention_map.mentions:
        if record.entity not in entities:
            yield (
                f"mention entity {record.entity} not in the graph ledger",
                "ledger/mention_map.json",
            )


# --- GRAPH ------------------------------------------------------------------


def graph_01(ctx: Context):
    minimum = ctx.charter.graph_targets.min_mentions_per_person
    for person in ctx.foundation.people:
        docs = {
            r.doc_id for r in ctx.mention_map.mentions if r.entity == person.id
        }
        if len(docs) < minimum:
            yield (
                f"{person.id} planned in {len(docs)} docs, recipe requires "
                f">= {minimum}",
                "ledger/mention_map.json",
            )


def graph_02(ctx: Context):
    mentioned = {r.entity for r in ctx.mention_map.mentions}
    for person in ctx.foundation.people:
        if person.id not in mentioned:
            yield (f"roster member {person.id} has zero planned mentions",
                   "ledger/mention_map.json")


def graph_03(ctx: Context):
    valid = set(ctx.graph.entities) | {
        e.id for e in ctx.engagements.engagements
    }
    for edge in ctx.graph.edges:
        for endpoint in (edge.src, edge.dst):
            if endpoint not in valid:
                yield (
                    f"edge {edge.src} -{edge.kind}-> {edge.dst} has unknown "
                    f"endpoint {endpoint}",
                    "ledger/graph.json",
                )


def graph_04(ctx: Context):
    by_kind: dict[str, int] = {}
    for edge in ctx.graph.edges:
        by_kind[edge.kind] = by_kind.get(edge.kind, 0) + 1

    people = ctx.foundation.people
    externals = ctx.foundation.external_people
    expected = {
        "reports_to": len(people) - 1,
        "works_at": len(people)
        + sum(len(xp.affiliations) or 1 for xp in externals),
        "client_of": len({e.client for e in ctx.engagements.engagements}),
        "participant": sum(
            len(e.internal_participants) + len(e.external_participants)
            for e in ctx.engagements.engagements
        ),
    }
    for kind, want in expected.items():
        got = by_kind.get(kind, 0)
        if got != want:
            yield (
                f"{kind} edge count {got} != {want} derived from ledgers",
                "ledger/graph.json",
            )


# --- PROV -----------------------------------------------------------------


def prov_01(ctx: Context):
    from ..render.provenance import docx_has_marker, pdf_has_marker, xlsx_has_marker

    checkers = {"docx": docx_has_marker, "pdf": pdf_has_marker,
                "xlsx": xlsx_has_marker}
    for e in ctx.manifest:
        path = ctx.paths.share_dir / e.path
        if not path.exists():
            continue
        if not checkers[e.format](path):
            yield ("synthetic-provenance marker missing", e.path)


RULES = [
    Rule("ORG-01", "ERROR", "exactly one CEO-equivalent", org_01),
    Rule("ORG-02", "ERROR", "reports_to is a single acyclic tree", org_02),
    Rule("DATE-01", "ERROR", "doc dates inside charter range", date_01),
    Rule("DATE-02", "ERROR", "authors employed at doc date", date_02),
    Rule("FIN-01", "ERROR", "finance ledger ties out", fin_01),
    Rule("FIN-02", "ERROR", "workbooks tie to the finance ledger", fin_02),
    Rule("FACT-01", "ERROR", "planted facts appear verbatim in doc text", fact_01),
    Rule("MENT-01", "ERROR", "planned mention surfaces appear in doc text",
         ment_01, available=_needs_mentions),
    Rule("MENT-02", "ERROR", "mentions resolve to graph entities", ment_02,
         available=_needs_mentions),
    Rule("GRAPH-01", "ERROR", "per-person mention coverage meets the recipe",
         graph_01, available=_needs_mention_knob),
    Rule("GRAPH-02", "ERROR", "no orphan roster member", graph_02,
         available=_needs_mention_knob),
    Rule("GRAPH-03", "ERROR", "graph edges have known endpoints", graph_03),
    Rule("GRAPH-04", "ERROR", "per-type edge counts match the ledgers",
         graph_04),
    Rule("FILE-01", "ERROR", "every manifest doc opens in its native reader",
         file_01),
    Rule("MAN-01", "ERROR", "manifest and share tree match 1:1", man_01),
    Rule("PROV-01", "ERROR", "every rendered file carries the synthetic marker",
         prov_01),
]
