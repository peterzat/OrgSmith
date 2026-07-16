"""Deterministic corpus metrics. No model, no network, no opinion.

Two measurements, both proxies for things the 29-rule validator cannot see:

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
from ..schemas import CorpusMetrics, DocMetric, SimilarPair, write_model
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
    return CorpusMetrics(slug=paths.slug, docs=docs, similar_pairs=pairs)


def flagged_pairs(metrics: CorpusMetrics) -> list[SimilarPair]:
    return [p for p in metrics.similar_pairs if p.jaccard >= SIMILAR_JACCARD]


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
