"""Derive noise documents from authored sources, with no model pass (M12).

An exact duplicate is a byte copy of the source's rendered file (handled in the
render runner). A draft is a near-duplicate: the source's blocks with a DRAFT
banner prepended and the final block dropped, so it shares most of the source's
prose (an agent cannot collapse it on a hash) and introduces no new fact --
every placeholder it carries was already the source's, owned by the answer key.
"""

from __future__ import annotations

from ..schemas import Block, DocIR

_DRAFT_BANNER = (
    "DRAFT -- superseded by the final version; not for distribution"
)


def derive_draft_docir(source: DocIR, doc_id: str) -> DocIR:
    """A draft near-duplicate of `source`: a DRAFT banner heading, then the
    source blocks with the last one dropped (an unfinished earlier version).
    Deterministic and RNG-free, so re-deriving yields identical bytes."""
    blocks = list(source.blocks)
    if len(blocks) > 2:
        blocks = blocks[:-1]
    banner = Block(kind="heading", text=_DRAFT_BANNER, level=1)
    return DocIR(doc_id=doc_id, blocks=[banner, *blocks])
