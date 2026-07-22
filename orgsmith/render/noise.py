"""Derive noise documents from authored sources, with no model pass (M12).

An exact duplicate is a byte copy of the source's rendered file (handled in the
render runner). A draft is a near-duplicate: the source's blocks with a DRAFT
banner prepended and the final block dropped, so it shares most of the source's
prose (an agent cannot collapse it on a hash) and introduces no new fact --
every placeholder it carries was already the source's, owned by the answer key.
"""

from __future__ import annotations

from ..schemas import Block, DocIR
from ..seeds import rng

_EMPTY_DIR_NAMES = (
    "Old",
    "Archive",
    "New folder",
    "Old Versions",
    "Backup",
    "scratch",
)

# Git cannot represent an empty directory, so a committed org would lose the
# junk directories on the first clone and NOISE-01 would then report them
# missing on the very fixture that planted them. Each planned empty directory
# therefore carries one zero-byte placeholder: transport, not content. It is
# the only file the emptiness check and MAN-01 tolerate there, and both derive
# the allowance from expected_empty_dirs, so the exception cannot widen to a
# directory the charter never planned.
EMPTY_DIR_PLACEHOLDER = ".gitkeep"


def expected_empty_dirs(charter, manifest) -> list[str]:
    """M15: the empty directories the charter plans, recomputed. The single
    twin shared by render (which creates them) and NOISE-01 (which checks
    them), so the two cannot drift. Candidates are junk names under the
    share root or any planned folder, excluding anything that would collide
    with a manifest path or folder; draws come only from the NEW
    docplan.noise.dirs stream, so a knob-off charter draws zero values.
    Fails actionably when the tree cannot host the asked count (docplan
    calls this at plan time)."""
    noise = charter.doc_culture.noise
    n = noise.empty_dirs if noise is not None else 0
    if n == 0:
        return []
    folders = sorted(
        {e.path.rsplit("/", 1)[0] for e in manifest if "/" in e.path}
    )
    taken = {e.path.lower() for e in manifest} | {f.lower() for f in folders}
    combos = []
    for parent in ["", *folders]:
        for name in _EMPTY_DIR_NAMES:
            path = f"{parent}/{name}" if parent else name
            if path.lower() not in taken:
                combos.append(path)
    if n > len(combos):
        raise SystemExit(
            f"docplan: noise wants {n} empty director(ies) but only "
            f"{len(combos)} junk-name slots exist under the planned tree; "
            f"lower empty_dirs"
        )
    picks = rng(charter.seed, "docplan.noise.dirs").sample(
        range(len(combos)), n
    )
    return sorted(combos[i] for i in picks)

_DRAFT_BANNER = (
    "DRAFT -- superseded by the final version; not for distribution"
)

_VERSION_BANNER = (
    "WORKING DRAFT v{pos} -- superseded; retained for reference"
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


_TEMPLATE_SECTIONS = {
    "engagement_letter": (
        "Background",
        "Scope of Engagement",
        "Fees and Expenses",
        "Terms and Termination",
        "Signatures",
    ),
    "kickoff_memo": (
        "Objectives",
        "Workstreams",
        "Team and Responsibilities",
        "First Thirty Days",
    ),
    "meeting_minutes": ("Attendees", "Agenda", "Decisions", "Action Items"),
    "status_report": (
        "Summary",
        "Progress This Period",
        "Risks and Issues",
        "Next Steps",
    ),
    "onboarding_record": (
        "Position and Start Date",
        "Reporting Line",
        "Systems Access",
        "First Assignments",
    ),
}


def stale_template_docir(doc_id: str, genre: str, title: str) -> DocIR:
    """M15: a dead template. Genre-shaped (the genre's own section headings)
    with every field a bracketed dummy, zero planted facts, zero mentions.
    Deterministic and RNG-free; no model pass ever touches it."""
    blocks = [
        Block(kind="heading", text=title, level=1),
        Block(kind="paragraph", text="Date: [DATE]    Author: [AUTHOR NAME]"),
    ]
    for section in _TEMPLATE_SECTIONS[genre]:
        blocks.append(Block(kind="heading", text=section, level=2))
        blocks.append(
            Block(
                kind="paragraph",
                text=f"[{section.upper()} -- replace with the matter's own "
                f"text before use.]",
            )
        )
    return DocIR(doc_id=doc_id, blocks=blocks)


def derive_version_docir(
    source: DocIR, doc_id: str, pos: int, length: int
) -> DocIR:
    """Member `pos` (1-based, pos < length) of a version chain whose final
    member is the source document. Earlier members keep fewer trailing blocks
    and every member carries a banner naming its own version, so no two chain
    members (nor the final) can share bytes even when the block prefix
    collapses on a short source. Deterministic and RNG-free."""
    blocks = list(source.blocks)
    keep = max(1, len(blocks) - (length - pos))
    banner = Block(
        kind="heading", text=_VERSION_BANNER.format(pos=pos), level=1
    )
    return DocIR(doc_id=doc_id, blocks=[banner, *blocks[:keep]])
