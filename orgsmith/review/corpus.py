"""Read the authored corpus back out of DocIR.

Shared by `review --sample` and `report`. Everything here is a pure
function of committed files: DocIR for the prose, the manifest for what
each document is, and the retained work orders for what the brief actually
asked of the author.

Placeholders get two different treatments on purpose:

- word count substitutes one token per placeholder, because a fee renders
  as "$120,000" and the reader sees one word there;
- similarity strips them, because `{{fact:E-2019-001.fee}}` is pipeline
  scaffolding the model did not write. Leaving them in would score every
  pair of engagement letters as similar for having the same fact slots,
  which measures the docplan, not the prose.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..artifacts import load_manifest
from ..authoring.contexts import _TARGET_WORDS as _GENRE_TARGETS
from ..paths import OrgPaths
from ..schemas import DocIR, ManifestEntry

_PLACEHOLDER = re.compile(r"\{\{fact:[^}]*\}\}")
_TOKEN = re.compile(r"[a-z0-9]+")

# `_GENRE_TARGETS` is a fallback only: the briefed value is read back from
# the retained work order whenever one covers the doc. It is imported
# rather than copied so the metric can never drift from what `contexts.py`
# actually briefs.

# A document is longform when its brief asked for at least this many words.
# Longform docs are where voice and structure are visible, so the board
# reads all of them rather than a sample.
LONGFORM_WORDS = 300


def docir_path(paths: OrgPaths, doc_id: str) -> Path:
    return paths.docir_dir / f"{doc_id.replace(':', '')}.json"


def prose_text(doc: DocIR) -> str:
    """Every string the author wrote, in block order.

    Sigblock signers are deliberately excluded: they are `p:`/`xp:` ids the
    renderer resolves to names, not prose.
    """
    chunks: list[str] = []
    for b in doc.blocks:
        if b.kind == "sigblock":
            continue
        chunks.append(b.text)
        chunks.extend(b.items)
        chunks.extend(b.header)
        for row in b.rows:
            chunks.extend(row)
    return "\n".join(c for c in chunks if c)


def word_count(text: str) -> int:
    """Words as a reader of the rendered document would count them."""
    return len(_PLACEHOLDER.sub("0", text).split())


def shingles(text: str, n: int = 4) -> set[tuple[str, ...]]:
    """Case-folded n-gram set over authored prose, placeholders removed."""
    toks = _TOKEN.findall(_PLACEHOLDER.sub(" ", text).lower())
    return {tuple(toks[i : i + n]) for i in range(len(toks) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_authored(paths: OrgPaths) -> dict[str, DocIR]:
    """Every document that has been through the authoring airlock.

    Unauthored docs are simply absent: a half-authored org yields a smaller
    corpus, never an error.
    """
    out: dict[str, DocIR] = {}
    if not paths.docir_dir.exists():
        return out
    for entry in load_manifest(paths):
        path = docir_path(paths, entry.doc_id)
        if path.exists():
            out[entry.doc_id] = DocIR.model_validate_json(path.read_text("utf-8"))
    return out


def briefed_targets(paths: OrgPaths) -> dict[str, int]:
    """doc_id -> the `target_words` its authoring brief actually carried.

    Read back from the retained work orders rather than recomputed, so the
    metric compares against what this org's author was told, not against
    whatever the genre table says today.
    """
    targets: dict[str, int] = {}
    if not paths.workorders_dir.exists():
        return targets
    for wo in sorted(paths.workorders_dir.glob("author-*.json")):
        try:
            data = json.loads(wo.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for brief in data.get("docs", []):
            doc_id, target = brief.get("doc_id"), brief.get("target_words")
            if isinstance(doc_id, str) and isinstance(target, int):
                targets[doc_id] = target
    return targets


def target_for(entry: ManifestEntry, targets: dict[str, int]) -> int:
    return targets.get(entry.doc_id, _GENRE_TARGETS.get(entry.genre, 250))


def require_authored(paths: OrgPaths, authored: dict[str, DocIR]) -> None:
    if not authored:
        raise SystemExit(
            f"no authored documents in {paths.slug}: the quality instrument "
            f"reads DocIR, which the author stage writes. Run "
            f"`python -m orgsmith author {paths.slug} --next-batch` and "
            f"dispatch the batches (see /forge), then retry."
        )
