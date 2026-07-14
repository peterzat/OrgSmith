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
    load_manifest,
)
from ..paths import OrgPaths

Finding = tuple[str, str]  # (message, target)


@dataclass
class Context:
    paths: OrgPaths
    charter: object
    foundation: object
    finance: object
    engagements: object
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
            manifest=load_manifest(paths),
        )

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


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    description: str
    check: Callable[[Context], Iterator[Finding]]


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
    Rule("FILE-01", "ERROR", "every manifest doc opens in its native reader",
         file_01),
    Rule("MAN-01", "ERROR", "manifest and share tree match 1:1", man_01),
    Rule("PROV-01", "ERROR", "every rendered file carries the synthetic marker",
         prov_01),
]
