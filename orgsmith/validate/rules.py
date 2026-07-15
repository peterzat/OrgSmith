"""The v0 rule catalog: ORG, DATE, FIN, FACT, FILE, MAN, PROV families."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterator

from ..artifacts import (
    load_acl,
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
    acl: object  # None for orgs generated before the ACL overlay
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
            acl=load_acl(paths),
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
        elif entry.format == "pptx":
            text = _pptx_text(path)
        elif entry.format == "eml":
            body = _eml_message(path).get_body(preferencelist=("plain",))
            text = body.get_content() if body is not None else ""
        elif entry.format == "xlsx":
            # Workbooks are checked cell-by-cell (FIN-02), not as prose;
            # FACT-01 skips them explicitly.
            text = ""
        else:
            raise SystemExit(
                f"validate: no text extractor for format {entry.format!r} "
                f"({entry.path})"
            )
        text = re.sub(r"\s+", " ", text)
        self._text_cache[entry.doc_id] = text
        return text

    def doc_pages(self, entry) -> list[str]:
        """Per-page extractable text (pdf only), whitespace-normalized.
        Page addressing is what makes signature-page scoping checkable."""
        key = ("pages", entry.doc_id)
        if key in self._text_cache:
            return self._text_cache[key]
        from pypdf import PdfReader

        path = self.paths.share_dir / entry.path
        pages = [
            re.sub(r"\s+", " ", page.extract_text() or "")
            for page in PdfReader(str(path)).pages
        ]
        self._text_cache[key] = pages
        return pages


def _pptx_text(path) -> str:
    """Every text run a pptx exposes: shape frames plus table cells."""
    from pptx import Presentation

    chunks: list[str] = []
    for slide in Presentation(str(path)).slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                chunks.extend(p.text for p in shape.text_frame.paragraphs)
            if shape.has_table:
                for row in shape.table.rows:
                    chunks.extend(c.text for c in row.cells)
    return "\n".join(chunks)


def _eml_message(path):
    from email import policy
    from email.parser import BytesParser

    with open(path, "rb") as fh:
        return BytesParser(policy=policy.default).parse(fh)


def _always(_ctx: Context) -> str | None:
    return None


def _needs_eml(ctx: Context) -> str | None:
    if ctx.charter.doc_culture.format_mix.eml == 0:
        return "format_mix.eml is 0 for this recipe"
    return None


def _needs_mentions(ctx: Context) -> str | None:
    if ctx.mention_map is None:
        return "org predates mention ground truth (no mention_map.json)"
    return None


def _needs_acl(ctx: Context) -> str | None:
    # Only an open posture may legitimately lack the ledger (every pre-ACL
    # org is posture open). A non-open org with no acl.json is corruption:
    # the rules run and yield the missing-ledger finding instead of skipping.
    if ctx.acl is None and ctx.charter.acl_posture == "open":
        return "org predates the ACL overlay (no ledger/acl.json)"
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
            elif e.format == "pptx":
                from pptx import Presentation

                if len(Presentation(str(path)).slides) < 1:
                    yield ("pptx has no slides", e.path)
            elif e.format == "eml":
                msg = _eml_message(path)
                for header in ("From", "To", "Date", "Subject", "Message-ID"):
                    if msg[header] is None:
                        yield (f"eml missing {header} header", e.path)
                msg.get_content()  # undecodable body -> reader failure below
            else:
                # Every supported format must have a reader branch above; a
                # format this rule does not know is a finding, not a pass.
                yield (f"no native reader known for format {e.format!r}", e.path)
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
    # PERMISSIONS.md is a sanctioned extra only while the ACL ledger that
    # renders it exists; a stray copy on a ledgerless org is unmanifested.
    extras = _SHARE_EXTRAS | (
        {"PERMISSIONS.md"} if ctx.acl is not None else set()
    )
    for extra in sorted(on_disk - planned - extras):
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


# --- LOC (hard-case location policies) --------------------------------------


def _hard_case_hosts(ctx: Context):
    """(entry, key_fact, fact) for every non-body key fact whose fact id
    resolves in the ledger; dangling ids are LOC-03's finding."""
    facts = ctx.engagements.fact_index()
    for e in ctx.manifest:
        for kf in e.key_facts:
            if kf.location != "body" and kf.fact_id in facts:
                yield e, kf, facts[kf.fact_id]


def loc_01(ctx: Context):
    for entry, kf, fact in _hard_case_hosts(ctx):
        if kf.location != "signature_page":
            continue
        if entry.format != "pdf":
            yield (
                f"signature_page fact {fact.id} planted in non-pdf doc",
                entry.path,
            )
            continue
        if not (ctx.paths.share_dir / entry.path).exists():
            continue  # FILE-01/MAN-01 report the absence
        pages = ctx.doc_pages(entry)
        hits = [i for i, text in enumerate(pages) if fact.rendered in text]
        last = len(pages) - 1
        if last not in hits:
            yield (
                f"fact {fact.id} surface {fact.rendered!r} missing from the "
                f"signature page",
                entry.path,
            )
        early = [i + 1 for i in hits if i != last]
        if early:
            yield (
                f"signature-page-only fact {fact.id} leaked into "
                f"page(s) {early}",
                entry.path,
            )


def loc_02(ctx: Context):
    from pathlib import PurePosixPath

    for entry, kf, fact in _hard_case_hosts(ctx):
        if kf.location != "filename":
            continue
        name = PurePosixPath(entry.path).name
        if fact.rendered not in name:
            yield (
                f"filename-only fact {fact.id} surface {fact.rendered!r} "
                f"missing from filename {name!r}",
                entry.path,
            )
        if not (ctx.paths.share_dir / entry.path).exists():
            continue
        if fact.rendered in ctx.doc_text(entry):
            yield (
                f"filename-only fact {fact.id} appears in extractable text",
                entry.path,
            )


def loc_03(ctx: Context):
    facts = ctx.engagements.fact_index()
    hosted: dict[str, int] = {}
    for e in ctx.manifest:
        for kf in e.key_facts:
            fact = facts.get(kf.fact_id)
            if fact is None:
                yield (f"key_fact {kf.fact_id} not in engagement ledger", e.path)
                continue
            if kf.location != fact.location_policy:
                yield (
                    f"key_fact {kf.fact_id} location {kf.location} != ledger "
                    f"policy {fact.location_policy}",
                    e.path,
                )
            if kf.location != "body":
                hosted[kf.fact_id] = hosted.get(kf.fact_id, 0) + 1
    for fid, fact in facts.items():
        if fact.location_policy != "body" and hosted.get(fid, 0) != 1:
            yield (
                f"hard-case fact {fid} ({fact.location_policy}) hosted by "
                f"{hosted.get(fid, 0)} docs, expected exactly 1",
                "docplan/manifest.jsonl",
            )


# --- ACL (read-access overlay) ----------------------------------------------


def _acl_missing(ctx: Context) -> Finding:
    """Any posture other than open requires acl.json; deleting the ledger
    must fail the org, not resurrect the pre-ACL grandfather skip."""
    return (
        f"ledger/acl.json missing but charter posture is "
        f"{ctx.charter.acl_posture!r}",
        "ledger/acl.json",
    )


def acl_01(ctx: Context):
    if ctx.acl is None:
        yield _acl_missing(ctx)
        return
    roster = {p.id for p in ctx.foundation.people}
    for grant in ctx.acl.grants:
        if grant.person not in roster:
            yield (
                f"ACL principal {grant.person} not on the roster",
                "ledger/acl.json",
            )
    for pid in sorted(roster - {g.person for g in ctx.acl.grants}):
        yield (f"roster member {pid} has no ACL grant", "ledger/acl.json")


def acl_02(ctx: Context):
    if ctx.acl is None:
        yield _acl_missing(ctx)
        return
    planned = {e.path for e in ctx.manifest}
    readable: set[str] = set()
    for grant in ctx.acl.grants:
        for doc in grant.docs:
            if doc not in planned:
                yield (
                    f"grant for {grant.person} references unknown doc {doc!r}",
                    "ledger/acl.json",
                )
            readable.add(doc)
    for doc in sorted(planned - readable):
        yield (f"document readable by no one: {doc}", "ledger/acl.json")


def acl_03(ctx: Context):
    if ctx.acl is None:
        yield _acl_missing(ctx)
        return
    from ..acl import derive_acl, render_permissions

    expected = derive_acl(
        ctx.charter, ctx.foundation, ctx.engagements, ctx.manifest
    )
    if expected != ctx.acl:
        yield (
            f"acl.json does not match recomputation from posture "
            f"{ctx.charter.acl_posture!r}",
            "ledger/acl.json",
        )
    if not ctx.paths.permissions_md.exists():
        yield ("PERMISSIONS.md missing from the share", "PERMISSIONS.md")
        return
    # Render from the recomputed ledger (trusted, roster-derived), never
    # from ctx.acl: a tampered grant naming an unknown principal would
    # KeyError inside render_permissions and crash the whole run.
    rendered = render_permissions(ctx.charter, ctx.foundation, expected)
    if ctx.paths.permissions_md.read_text("utf-8") != rendered:
        yield (
            "PERMISSIONS.md does not match the posture's expected rendering",
            "PERMISSIONS.md",
        )


# --- EML ------------------------------------------------------------------


def eml_01(ctx: Context):
    """Transport headers recompute exactly from the ledgers, via the same
    helper the renderer used. Runs only when the charter asks for mail, so
    a knob that is on with no .eml documents is tamper evidence."""
    from ..render import people_index
    from ..render.eml import expected_headers

    entries = [e for e in ctx.manifest if e.format == "eml"]
    if not entries:
        yield (
            "format_mix.eml > 0 but the manifest plans no eml documents",
            "docplan/manifest.jsonl",
        )
        return
    people = people_index(ctx.foundation)
    for e in entries:
        path = ctx.paths.share_dir / e.path
        if not path.exists():
            continue  # FILE-01/MAN-01 report the absence
        msg = _eml_message(path)
        expected = expected_headers(
            e, people, ctx.charter.slug, ctx.charter.domain
        )
        for name, want in expected.items():
            got = re.sub(r"\s+", " ", str(msg[name] or "")).strip()
            if got != re.sub(r"\s+", " ", want).strip():
                yield (
                    f"header {name} does not recompute from the ledger: "
                    f"{got!r} != {want!r}",
                    e.path,
                )


# --- PROV -----------------------------------------------------------------


def prov_01(ctx: Context):
    from ..render.provenance import eml_has_marker, opc_has_marker, pdf_has_marker

    checkers = {"docx": opc_has_marker, "pdf": pdf_has_marker,
                "xlsx": opc_has_marker, "pptx": opc_has_marker,
                "eml": eml_has_marker}
    for e in ctx.manifest:
        path = ctx.paths.share_dir / e.path
        if not path.exists():
            continue
        checker = checkers.get(e.format)
        if checker is None:
            # A format without a marker checker can never silently pass.
            yield (f"no provenance checker known for format {e.format!r}", e.path)
        elif not checker(path):
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
    Rule("LOC-01", "ERROR", "signature-page facts on the signature page only",
         loc_01),
    Rule("LOC-02", "ERROR", "filename facts in the filename only", loc_02),
    Rule("LOC-03", "ERROR", "manifest key-fact locations mirror the ledger",
         loc_03),
    Rule("ACL-01", "ERROR", "ACL principals mirror the roster", acl_01,
         available=_needs_acl),
    Rule("ACL-02", "ERROR", "every document is readable by someone", acl_02,
         available=_needs_acl),
    Rule("ACL-03", "ERROR", "grants and PERMISSIONS.md match the posture",
         acl_03, available=_needs_acl),
    Rule("EML-01", "ERROR", "eml transport headers recompute from the ledger",
         eml_01, available=_needs_eml),
    Rule("FILE-01", "ERROR", "every manifest doc opens in its native reader",
         file_01),
    Rule("MAN-01", "ERROR", "manifest and share tree match 1:1", man_01),
    Rule("PROV-01", "ERROR", "every rendered file carries the synthetic marker",
         prov_01),
]
