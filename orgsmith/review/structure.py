"""Structural similarity: what two documents CONTAIN, not what they say.

The same-genre 4-gram metric in `metrics.py` is structurally blind to the
defect it exists to surface. Two kickoff memos can be the same memo
re-skinned -- same sections in the same order, same moves in the same
positions -- and share almost no literal 4-gram, because a fresh-context
author paraphrases everything. On the M17 exemplar the median same-genre
Jaccard is 0.0031: the lexical axis is pinned against its floor and has no
dynamic range left to spend.

Two axes here, both computed from committed DocIR with no model:

- **shape** -- a per-block token sequence (`H<level>`, `P<bucket>`,
  `L<bucket>`, `T<rows>x<cols>`, `SIG`) compared with
  `difflib.SequenceMatcher`. Pure structure: rewriting every word changes
  nothing, which is exactly the blindness the lexical axis has.
- **openers** -- the same comparison over the first content word of each
  prose unit, with a small frozen stoplist. Positional lexis, which is what
  "the same moves in the same order" looks like once a whole-document
  4-gram set has drowned it in body prose.

MEASURE, NEVER GATE. Neither number is a verdict and neither may become a
validator rule or a test threshold. Two status reports SHOULD share a shape;
a firm that files them any other way is the unrealistic one. The scores rank
a reading list for the board, and `docs/REVIEW-CALIBRATION.md` records what
the axis caught and missed against the board's own findings. Reported
BESIDE the lexical score rather than replacing it: on the exemplar each axis
ranks pairs the other misses.
"""

from __future__ import annotations

import itertools
import re
from difflib import SequenceMatcher

from ..schemas import DocIR, StructurePair

_PLACEHOLDER = re.compile(r"\{\{fact:[^}]*\}\}")
_TOKEN = re.compile(r"[a-z0-9]+")

# How many pairs the artifact keeps. Every same-genre pair is SCORED; only
# the strongest are stored, because shape ratios are dense where Jaccard is
# sparse (`metrics.py` drops the zeros and keeps a small set for free). An
# uncapped set is O(docs^2) within each genre, which is a few hundred rows
# on today's fleet and six figures on a flagship. `CorpusMetrics.
# structural_pairs_considered` records the full count so the cap is a
# visible truncation rather than a silent one.
STRUCTURAL_TOP_N = 50

# Paragraph word counts and list item counts land in coarse buckets. Exact
# counts would make every pair distinct and the axis would measure length
# noise; these separate "one-liner" from "paragraph" from "essay", which is
# the structural fact worth comparing.
_PARAGRAPH_BUCKETS = (25, 60, 120)
_LIST_BUCKETS = (2, 5, 9)

# Skipped when looking for a unit's opening CONTENT word. Deliberately small
# and frozen: determiners, common prepositions, conjunctions, copulas and
# personal pronouns, so that "We recommend", "The team recommends" and "Our
# recommendation is" all open on the move rather than on the framing. Not
# tuned against any corpus -- a stoplist fitted to the fixtures would be a
# threshold in disguise.
_STOPWORDS = frozenset(
    """
    a an the this that these those
    i we you he she it they us our your his her its their my
    of in on at to for from by with as into over under
    and or but so nor yet
    is are was were be been being am
    there here
    """.split()
)

# Emitted for a unit with no content word at all (a heading that is a bare
# placeholder, an empty list item). Keeps positions aligned so the opener
# sequences stay comparable block for block.
_NO_OPENER = "-"


def _bucket(n: int, edges: tuple[int, ...]) -> int:
    for i, edge in enumerate(edges):
        if n <= edge:
            return i
    return len(edges)


def _words(text: str) -> list[str]:
    return _TOKEN.findall(_PLACEHOLDER.sub(" ", text).lower())


def shape_tokens(doc: DocIR) -> list[str]:
    """One token per block, describing what the block IS.

    Carries no authored word, by construction: a paraphrase that keeps the
    document's skeleton scores identically here, which is the point.
    """
    out: list[str] = []
    for b in doc.blocks:
        if b.kind == "heading":
            out.append(f"H{b.level}")
        elif b.kind == "paragraph":
            out.append(f"P{_bucket(len(_words(b.text)), _PARAGRAPH_BUCKETS)}")
        elif b.kind == "list":
            out.append(f"L{_bucket(len(b.items), _LIST_BUCKETS)}")
        elif b.kind == "table":
            cols = len(b.header) or (len(b.rows[0]) if b.rows else 0)
            out.append(f"T{len(b.rows)}x{cols}")
        elif b.kind == "sigblock":
            out.append("SIG")
    return out


def opener_tokens(doc: DocIR) -> list[str]:
    """The first content word of each prose unit, in document order.

    Units are headings, paragraphs and list items. Tables and sigblocks
    contribute nothing: their cells are label fragments and resolved ids,
    not authorial moves.
    """
    out: list[str] = []
    for b in doc.blocks:
        if b.kind in ("heading", "paragraph"):
            units = [b.text]
        elif b.kind == "list":
            units = list(b.items)
        else:
            continue
        for unit in units:
            content = [w for w in _words(unit) if w not in _STOPWORDS]
            out.append(content[0] if content else _NO_OPENER)
    return out


def ratio(a: list[str], b: list[str]) -> float:
    """Ordered-sequence similarity. Two empty sequences are 0.0, not 1.0:
    a document with no blocks is missing data, not a perfect match."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def pair_scores(doc_a: DocIR, doc_b: DocIR) -> tuple[float, float]:
    return (
        ratio(shape_tokens(doc_a), shape_tokens(doc_b)),
        ratio(opener_tokens(doc_a), opener_tokens(doc_b)),
    )


def rank_key(pair: StructurePair) -> tuple:
    """Strongest first, doc ids breaking ties so the order is total and the
    artifact is byte-stable."""
    return (-(pair.shape + pair.openers) / 2, pair.doc_a, pair.doc_b)


def compute_pairs(
    authored: dict[str, DocIR],
    genre_of: dict[str, str],
    top_n: int = STRUCTURAL_TOP_N,
) -> tuple[list[StructurePair], int]:
    """Score every same-genre pair; return the strongest `top_n` and how many
    were scored.

    Pure in its inputs so a test can hand it a constructed corpus. Callers
    decide which documents are eligible: `metrics.compute` passes authored
    `batchable` documents only, because a derived duplicate is a byte copy of
    its source and would score 1.0 against it for reasons that have nothing
    to do with the author.
    """
    pairs: list[StructurePair] = []
    for a, b in itertools.combinations(sorted(authored), 2):
        if genre_of.get(a) != genre_of.get(b):
            continue
        shape, openers = pair_scores(authored[a], authored[b])
        pairs.append(
            StructurePair(
                doc_a=a,
                doc_b=b,
                genre=genre_of[a],
                shape=round(shape, 4),
                openers=round(openers, 4),
            )
        )
    considered = len(pairs)
    pairs.sort(key=rank_key)
    return pairs[:top_n], considered
