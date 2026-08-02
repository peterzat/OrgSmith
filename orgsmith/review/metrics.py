"""Deterministic corpus metrics. No model, no network, no opinion.

Two measurements, both proxies for things the validator cannot see (a third,
structural similarity, lives in `structure.py` and is wired in below):

- **Length against the brief.** `target_words` is what the author was asked
  for; the word count is what arrived. Until now nothing read the target
  back, so a corpus could drift arbitrarily far from its own brief in
  silence.
- **Same-genre n-gram overlap.** Two documents of one genre sharing long
  literal runs is the generator reusing itself.

Neither is a verdict. A high-overlap pair may be perfectly realistic --
firms do reuse engagement-letter templates -- and a short document may be
right for its genre. The metric measures, the board judges, the human
decides. Nothing here may become a validator rule: the thresholds are
unknown and the frozen fixtures would fail them.
"""

from __future__ import annotations

import itertools

from ..artifacts import load_manifest
from ..paths import OrgPaths
from ..schemas import (
    CorpusMetrics,
    DocMetric,
    SimilarPair,
    StructurePair,
    write_model,
)
from . import structure
from .corpus import (
    briefed_targets,
    jaccard,
    load_authored,
    prose_text,
    require_authored,
    shingles,
    target_for,
    word_count,
)

# Flag thresholds. Chosen to surface the known positives in the committed
# fleet without burying them in noise, and deliberately generous: this is a
# reading list for a human, not a gate. Tune freely -- nothing depends on
# these values being stable across versions.
SHORT_RATIO = 0.75  # words / target below this is "short of brief"
LONG_RATIO = 1.5  # and above this is "over brief"
SIMILAR_JACCARD = 0.15  # same-genre 4-gram overlap worth a second look


def compute(paths: OrgPaths) -> CorpusMetrics:
    authored = load_authored(paths)
    require_authored(paths, authored)
    targets = briefed_targets(paths)
    entries = [e for e in load_manifest(paths) if e.doc_id in authored]

    docs = [
        DocMetric(
            doc_id=e.doc_id,
            genre=e.genre,
            words=word_count(prose_text(authored[e.doc_id])),
            target_words=target_for(e, targets),
        )
        for e in entries
    ]

    grams = {
        e.doc_id: shingles(prose_text(authored[e.doc_id])) for e in entries
    }
    genre_of = {e.doc_id: e.genre for e in entries}
    pairs = []
    for a, b in itertools.combinations(sorted(grams), 2):
        if genre_of[a] != genre_of[b]:
            continue
        score = jaccard(grams[a], grams[b])
        if score <= 0:
            continue
        pairs.append(
            SimilarPair(doc_a=a, doc_b=b, genre=genre_of[a], jaccard=round(score, 4))
        )
    # Strongest overlap first; doc ids break ties so the order is total and
    # the file is byte-stable.
    pairs.sort(key=lambda p: (-p.jaccard, p.doc_a, p.doc_b))

    # M17b's structural axis, over authored `batchable` documents only. A
    # derived document is a byte copy (or a stale-template variant) of its
    # source, so it would score ~1.0 on shape against it and crowd the list
    # with the noise stages rather than the author.
    authored_batchable = {
        e.doc_id: authored[e.doc_id] for e in entries if e.authoring == "batchable"
    }
    structural, considered = structure.compute_pairs(
        authored_batchable,
        {e.doc_id: e.genre for e in entries},
    )
    return CorpusMetrics(
        slug=paths.slug,
        docs=docs,
        similar_pairs=pairs,
        structural_pairs=structural,
        structural_pairs_considered=considered,
    )


def flagged_pairs(metrics: CorpusMetrics) -> list[SimilarPair]:
    return [p for p in metrics.similar_pairs if p.jaccard >= SIMILAR_JACCARD]


# How many structural rows the report prints. A row count, not a threshold:
# the axis has no validated cut point (docs/REVIEW-CALIBRATION.md), so the
# report shows a fixed-length reading list instead of pretending one exists.
STRUCTURAL_ROWS = 10


def top_structural_pairs(
    metrics: CorpusMetrics, limit: int = STRUCTURAL_ROWS
) -> list[StructurePair]:
    return metrics.structural_pairs[:limit]


def jaccard_of(metrics: CorpusMetrics, doc_a: str, doc_b: str) -> float:
    """The lexical score for a pair, or 0.0 when the pair shares no 4-gram
    (`similar_pairs` drops the zeros)."""
    for p in metrics.similar_pairs:
        if p.doc_a == doc_a and p.doc_b == doc_b:
            return p.jaccard
    return 0.0


class AuthorRange:
    """One author's proxy row (M15). Plain object, not a contract: these
    numbers live only in the rendered report, never in a schema'd artifact,
    so the thresholds and shape stay free to tune."""

    def __init__(self, author, docs, within, cross, early_late):
        self.author = author
        self.docs = docs
        self.within = within  # (min, mean, max) or None with < 2 docs
        self.cross = cross  # mean vs every other author's docs, or None
        self.early_late = early_late  # first-half vs second-half shingles


def author_ranges(paths: OrgPaths) -> list[AuthorRange]:
    """M15: deterministic per-author similarity proxies, no model. For each
    author: the range of pairwise 4-gram Jaccard among their own docs
    (within), the mean against every other author's docs (cross), and the
    overlap of their first-half shingles with their second half, in date
    order (early/late, a consistency-over-time proxy).

    A PROXY, measure-never-gate: same-genre similarity is structurally blind
    to template collapse (docs/REVIEW-CALIBRATION.md), thresholds are
    unvalidated, and nothing here enters any test tier as a bar. The M12a
    confound stands: this is measurement machinery plus data points, never
    an effect size."""
    authored = load_authored(paths)
    entries = [
        e
        for e in load_manifest(paths)
        if e.doc_id in authored and e.authoring == "batchable"
    ]
    grams = {
        e.doc_id: shingles(prose_text(authored[e.doc_id])) for e in entries
    }
    by_author: dict[str, list] = {}
    for e in entries:
        by_author.setdefault(e.authors[0], []).append(e)

    def mean(xs):
        return sum(xs) / len(xs)

    rows = []
    for author in sorted(by_author):
        docs = sorted(by_author[author], key=lambda e: (e.date, e.doc_id))
        within_scores = [
            jaccard(grams[a.doc_id], grams[b.doc_id])
            for a, b in itertools.combinations(docs, 2)
        ]
        within = (
            (min(within_scores), mean(within_scores), max(within_scores))
            if within_scores
            else None
        )
        others = [e for e in entries if e.authors[0] != author]
        cross_scores = [
            jaccard(grams[a.doc_id], grams[b.doc_id])
            for a in docs
            for b in others
        ]
        cross = mean(cross_scores) if cross_scores else None
        early, late = docs[: len(docs) // 2], docs[len(docs) // 2:]
        early_late = None
        if early and late:
            eg = set().union(*(grams[e.doc_id] for e in early))
            lg = set().union(*(grams[e.doc_id] for e in late))
            early_late = jaccard(eg, lg)
        rows.append(AuthorRange(author, len(docs), within, cross, early_late))
    return rows


def flagged_lengths(metrics: CorpusMetrics) -> list[DocMetric]:
    return [
        d
        for d in metrics.docs
        if d.ratio < SHORT_RATIO or d.ratio > LONG_RATIO
    ]


def run_metrics(paths: OrgPaths) -> CorpusMetrics:
    metrics = compute(paths)
    write_model(paths.corpus_metrics_json, metrics)
    return metrics
