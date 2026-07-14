"""Fact placeholder resolution: the model cannot mistranscribe a number.

Renderers accept only fully resolved DocIR. Resolution fails loudly on an
unknown fact id or any placeholder that survives substitution.
"""

from __future__ import annotations

import re

from ..schemas import Block, DocIR, Fact

_PLACEHOLDER = re.compile(r"\{\{fact:([^}]*)\}\}")


class FactResolutionError(Exception):
    pass


def resolve_text(text: str, facts: dict[str, Fact], where: str) -> str:
    def _sub(match: re.Match) -> str:
        fid = match.group(1)
        if fid not in facts:
            raise FactResolutionError(f"{where}: unknown fact id {fid!r}")
        return facts[fid].rendered

    resolved = _PLACEHOLDER.sub(_sub, text)
    if "{{fact:" in resolved:
        raise FactResolutionError(f"{where}: unresolved placeholder in {text!r}")
    return resolved


def resolve_docir(doc: DocIR, facts: dict[str, Fact]) -> DocIR:
    blocks = []
    for i, b in enumerate(doc.blocks):
        where = f"{doc.doc_id} block {i}"
        blocks.append(
            Block(
                kind=b.kind,
                text=resolve_text(b.text, facts, where),
                level=b.level,
                items=[resolve_text(x, facts, where) for x in b.items],
                header=[resolve_text(x, facts, where) for x in b.header],
                rows=[[resolve_text(x, facts, where) for x in row] for row in b.rows],
                signers=list(b.signers),
            )
        )
    return DocIR(doc_id=doc.doc_id, blocks=blocks)
