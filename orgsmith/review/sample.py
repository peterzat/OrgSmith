"""review --sample: a deterministic stratified reading list for the board.

The board reads a sample, not a corpus: reviewers have finite context and
the fleet is meant to grow. What the sample must never do is vary between
two runs over the same org, or a finding could not be reproduced.

Coverage rules, in priority order:

1. every longform document (the brief asked for LONGFORM_WORDS or more) --
   voice and structure are only visible at length;
2. every document carrying a planted fact -- these are the docs the rest of
   the system makes promises about;
3. one document from each remaining genre x format x decade cell, so decks,
   mail, legacy binaries and scans all reach a reviewer's eye.

Randomness enters at exactly one point: choosing which document represents
an over-full cell. It is drawn from the `review.sample` stream, which is
new, so every existing stream keeps producing exactly what it produced
before.
"""

from __future__ import annotations

from ..artifacts import load_charter, load_manifest
from ..paths import OrgPaths
from ..schemas import ReviewSample, SampledDoc, write_model
from ..seeds import rng
from .corpus import (
    LONGFORM_WORDS,
    briefed_targets,
    load_authored,
    prose_text,
    require_authored,
    target_for,
    word_count,
)

SEED_STREAM = "review.sample"


def _decade(year: int) -> str:
    return f"{year // 10 * 10}s"


def build_sample(paths: OrgPaths) -> ReviewSample:
    charter = load_charter(paths)
    authored = load_authored(paths)
    require_authored(paths, authored)

    targets = briefed_targets(paths)
    entries = [e for e in load_manifest(paths) if e.doc_id in authored]

    strata: dict[str, str] = {}  # doc_id -> why it is in the sample
    for entry in entries:
        if target_for(entry, targets) >= LONGFORM_WORDS:
            strata[entry.doc_id] = "longform"
    for entry in entries:
        if entry.key_facts and entry.doc_id not in strata:
            strata[entry.doc_id] = "planted-facts"

    # Remaining docs compete cell by cell. A cell with one doc contributes
    # that doc; a cell already covered above contributes nothing more.
    cells: dict[str, list[str]] = {}
    for entry in entries:
        if entry.doc_id in strata:
            continue
        cell = f"{entry.genre}/{entry.format}/{_decade(entry.date.year)}"
        cells.setdefault(cell, []).append(entry.doc_id)

    thin: list[str] = []
    stream = rng(charter.seed, SEED_STREAM)
    for cell in sorted(cells):
        candidates = sorted(cells[cell])
        if len(candidates) == 1:
            thin.append(cell)
        # Draw per cell in sorted cell order so the stream is consumed in a
        # fixed sequence regardless of manifest ordering.
        pick = candidates[stream.randrange(len(candidates))]
        strata[pick] = f"stratum {cell}"

    by_id = {e.doc_id: e for e in entries}
    docs = [
        SampledDoc(
            doc_id=doc_id,
            path=by_id[doc_id].path,
            genre=by_id[doc_id].genre,
            format=by_id[doc_id].format,
            date=by_id[doc_id].date,
            stratum=stratum,
            words=word_count(prose_text(authored[doc_id])),
        )
        for doc_id, stratum in sorted(strata.items())
    ]
    return ReviewSample(slug=paths.slug, docs=docs, thin_strata=sorted(thin))


def run_sample(paths: OrgPaths, as_json: bool = False) -> int:
    sample = build_sample(paths)
    write_model(paths.review_sample_json, sample)
    if as_json:
        print(paths.review_sample_json.read_text("utf-8"), end="")
        return 0
    print(f"review: sample -> {paths.review_sample_json}")
    print(f"  {len(sample.docs)} of {len(load_authored(paths))} authored docs")
    counts: dict[str, int] = {}
    for doc in sample.docs:
        key = doc.stratum.split("/")[0]
        counts[key] = counts.get(key, 0) + 1
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
    if sample.thin_strata:
        print(f"  thin strata (one doc each): {', '.join(sample.thin_strata)}")
    return 0
