"""Numbers an author wrote that no ledger value accounts for (M17d).

M17c's AIRLOCK-01: the airlock stops a model transcribing a value the ledger
owns, and does not stop it inventing one. Two identical control runs authored
0 and 18 such numbers across the same 59 documents, one worker building a
whole funnel ("238 universe / 61 screened") that no ledger owns. A number
like that is not wrong, it is unverifiable: a consumer building an
extraction eval finds it in the document and nothing in the answer key to
score it against.

This counts them, per document and in total, for GENERATION-REPORT.md. It is
a measurement and never gates: no threshold it produces enters a test tier or
a validator rule.

The counting rule is the one `tools/probe_numbers.py` pre-registered for the
M17d Opus 5.5 probe (and a test pins the two in agreement): placeholders are
removed, a number is a run of digits with optional thousands separators, only
values of 10 or more count, four-digit 1900-2099 values are years, and each
document contributes its distinct values. On top of that, a value equal to
one of the document's OWN briefed facts is not counted, since the answer key
scores that document on it. A value that merely coincides with some other
engagement's fact is still counted: nothing about this document makes it
checkable.
"""

from __future__ import annotations

import re

from ..paths import OrgPaths

_PLACEHOLDER = re.compile(r"\{\{fact:[^}]*\}\}")
_NUMBER = re.compile(r"(?<![\w])\d{1,3}(?:,\d{3})+(?![\d])|(?<![\w,])\d+(?![\d])")

# How many documents the report lists by name.
LISTED_DOCS = 10


def numbers_in(text: str) -> set[int]:
    """Distinct counted values in one document's prose."""
    text = _PLACEHOLDER.sub(" ", text)
    found: set[int] = set()
    for match in _NUMBER.finditer(text):
        value = int(match.group().replace(",", ""))
        if value < 10:
            continue
        if 1900 <= value <= 2099 and len(match.group()) == 4:
            continue
        found.add(value)
    return found


def owned_by_doc(paths: OrgPaths) -> dict[str, set[int]]:
    """{doc id: the integer values of the facts the plan briefs that doc}."""
    from ..artifacts import load_engagements, load_manifest

    facts = load_engagements(paths).fact_index()
    owned: dict[str, set[int]] = {}
    for entry in load_manifest(paths):
        owned[entry.doc_id] = {
            facts[ref].value
            for ref in entry.facts_refs
            if ref in facts and isinstance(facts[ref].value, int)
        }
    return owned


def unowned_by_doc(paths: OrgPaths) -> dict[str, set[int]]:
    from .corpus import load_authored, prose_text

    owned = owned_by_doc(paths)
    return {
        doc_id: numbers_in(prose_text(doc)) - owned.get(doc_id, set())
        for doc_id, doc in sorted(load_authored(paths).items())
    }


def unowned_lines(paths: OrgPaths) -> list[str]:
    per_doc = unowned_by_doc(paths)
    if not per_doc:
        return ["No authored documents to measure."]
    total = sum(len(v) for v in per_doc.values())
    hits = sorted(
        ((d, v) for d, v in per_doc.items() if v), key=lambda dv: (-len(dv[1]), dv[0])
    )
    lines = [
        f"{total} number(s) in authored prose that no ledger value accounts for, "
        f"across {len(hits)} of {len(per_doc)} documents (distinct values per "
        f"document; values under 10 and years not counted). The airlock keeps "
        f"the model from transcribing a value the ledger owns; it does not keep "
        f"it from inventing one, and an invented number is one the answer key "
        f"cannot score. A measurement, never a gate.",
    ]
    if hits:
        lines += ["", "| doc | count | values |", "| --- | ---: | --- |"]
        for doc_id, values in hits[:LISTED_DOCS]:
            shown = ", ".join(str(v) for v in sorted(values))
            lines.append(f"| {doc_id} | {len(values)} | {shown} |")
        if len(hits) > LISTED_DOCS:
            lines.append("")
            lines.append(f"{len(hits) - LISTED_DOCS} more document(s) not listed.")
    return lines
