#!/usr/bin/env python3
"""Plant known defects into scratch copies of an org, to measure board recall
(M17d).

`board-yield-at-scale` in BACKLOG.md found findings per sampled document
falling 15x from the smallest boarded org to the largest, at the same
coverage band, and two readings fit: the large org is cleaner, or six
reviewers handed 168 documents read less closely than six handed 51. Nothing
distinguished them, because nobody knew what a board SHOULD find. This builds
the oracle: the same fixed set of defects, planted identically, read once
from a short reading list and once from the full one. If recall falls with
the list, the instrument degrades with reading load.

It never touches the source org. It writes two roots, each a copy of the org
with the same plants, differing only in `review/sample.json`, plus an answer
key outside both roots so no reviewer can find it. Deterministic and
offline:

    python tools/plant_defects.py calderwood-partners \\
        --out scratch/recall --key <scratchpad>/recall-key.json
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orgsmith.artifacts import load_manifest  # noqa: E402
from orgsmith.naming import doc_id_filename  # noqa: E402
from orgsmith.paths import OrgPaths  # noqa: E402
from orgsmith.review.corpus import load_authored, prose_text, word_count  # noqa: E402
from orgsmith.schemas import ReviewSample, SampledDoc, write_model  # noqa: E402

# Each plant: (kind, sentence, the token a finding must quote or name to be
# credited, the first year the reference is not an anachronism). Sentences
# carry no digits and no names, so they cannot collide with a ledger value or
# a planned mention; only documents dated well before `since` receive an
# anachronism. The tokens are fixed here, before any reviewer runs.
ANACHRONISMS = [
    ("anachronism", "I will post the revised workplan in our Slack channel once the client signs off.", "Slack", 2014),
    ("anachronism", "We agreed to hold the follow-up over Zoom rather than travel, which suits everyone now.", "Zoom", 2020),
    ("anachronism", "The team will keep the action log in the shared Microsoft Teams space.", "Teams", 2017),
    ("anachronism", "The interviews will be recorded and transcribed automatically by the meeting assistant.", "transcribed automatically", 2021),
    ("anachronism", "I have asked the analysts to draft the first pass with ChatGPT before we edit it.", "ChatGPT", 2023),
    ("anachronism", "Everyone dialed in from home, as has become the norm since the pandemic.", "pandemic", 2020),
    ("anachronism", "I will record a short Loom walkthrough of the model for the client's finance team.", "Loom", 2016),
    ("anachronism", "Open items will live on the Notion board the client set up for us.", "Notion", 2018),
]
ASSISTANT_VOICE = [
    ("assistant_voice", "I hope this helps, and do let me know if you would like me to expand on any section.", "hope this helps", None),
    ("assistant_voice", "Certainly. Here is a concise summary of the key points discussed.", "Certainly", None),
    ("assistant_voice", "Great question! The short answer is that the timeline still holds.", "Great question", None),
    ("assistant_voice", "In summary, this document has outlined the key considerations for the engagement.", "this document has outlined", None),
]
PLANTS = ANACHRONISMS + ASSISTANT_VOICE

# An anachronism lands only in a document at least this many years before
# the reference became possible, so no reviewer could reasonably call it a
# borderline early adopter.
ANACHRONISM_MARGIN_YEARS = 4


def _insert(doc: dict, sentence: str) -> None:
    """Append the sentence to the second paragraph (the first if there is
    only one), so it reads as part of the author's own prose rather than as a
    block of its own."""
    paragraphs = [b for b in doc["blocks"] if b["kind"] == "paragraph" and b.get("text", "").strip()]
    if not paragraphs:
        raise SystemExit(f"{doc['doc_id']}: no paragraph to plant into")
    target = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]
    target["text"] = target["text"].rstrip() + " " + sentence


def choose(paths: OrgPaths, seed: int) -> list[dict]:
    """Deterministic plant placement: one document per plant, distinct
    documents, spread across genres, anachronisms only where they are
    unambiguous."""
    rand = random.Random(seed)
    authored = load_authored(paths)
    manifest = {e.doc_id: e for e in load_manifest(paths)}
    eligible = sorted(
        d for d, doc in authored.items()
        if any(b.kind == "paragraph" and b.text.strip() for b in doc.blocks)
    )
    used: set[str] = set()
    used_genres: dict[str, int] = {}
    placed = []
    for kind, sentence, token, since in PLANTS:
        pool = [
            d for d in eligible
            if d not in used
            and (since is None or manifest[d].date.year <= since - ANACHRONISM_MARGIN_YEARS)
        ]
        if not pool:
            raise SystemExit(
                f"no unplanted document is dated early enough for the {token!r} "
                f"anachronism (needs {since - ANACHRONISM_MARGIN_YEARS} or earlier)"
            )
        # Prefer the genre used least so far, so plants spread across genres.
        least = min(used_genres.get(manifest[d].genre, 0) for d in pool)
        pool = [d for d in pool if used_genres.get(manifest[d].genre, 0) == least]
        doc_id = rand.choice(pool)
        used.add(doc_id)
        used_genres[manifest[doc_id].genre] = used_genres.get(manifest[doc_id].genre, 0) + 1
        placed.append({
            "doc_id": doc_id, "kind": kind, "sentence": sentence, "token": token,
            "genre": manifest[doc_id].genre, "date": manifest[doc_id].date.isoformat(),
        })
    return placed


def _copy_org(src: Path, dst: Path, slug: str) -> None:
    if dst.exists():
        raise SystemExit(f"{dst} already exists; choose a fresh --out")
    shutil.copytree(src / "recipes" / slug, dst / "recipes" / slug)
    shutil.copytree(src / "companies" / slug, dst / "companies" / slug)
    shutil.copytree(
        src / "companies" / f"{slug}-metadata",
        dst / "companies" / f"{slug}-metadata",
        # The board's own prior output must not reach a reviewer, and the
        # work orders carry generator stamps nobody needs for this read.
        ignore=lambda d, names: [n for n in names if n in ("review", "workorders")],
    )


def _sample(paths: OrgPaths, doc_ids: list[str]) -> ReviewSample:
    manifest = {e.doc_id: e for e in load_manifest(paths)}
    authored = load_authored(paths)
    return ReviewSample(
        slug=paths.slug,
        docs=[
            SampledDoc(
                doc_id=d, path=manifest[d].path, genre=manifest[d].genre,
                format=manifest[d].format, date=manifest[d].date,
                stratum="reading list",
                words=word_count(prose_text(authored[d])),
            )
            for d in sorted(doc_ids)
        ],
        thin_strata=[],
    )


def build(slug: str, source_root: Path, out: Path, key: Path, seed: int, small: int) -> dict:
    src = OrgPaths(root=source_root, slug=slug)
    # The source is only ever read; every write lands under `out`, and a copy
    # refuses to land on an existing path. Pointing `out` at the source root
    # itself is the one way to aim a write at the committed org.
    if out.resolve() == source_root.resolve():
        raise SystemExit("--out must be a scratch directory, never the source root")
    placed = choose(src, seed)
    planted_ids = [p["doc_id"] for p in placed]
    others = sorted(set(load_authored(src)) - set(planted_ids))
    if small < len(planted_ids):
        raise SystemExit(f"--small must hold all {len(planted_ids)} planted documents")
    small_ids = planted_ids + random.Random(seed + 1).sample(others, small - len(planted_ids))
    lists = {"small": small_ids, "large": planted_ids + others}

    for name, ids in lists.items():
        root = out / name
        _copy_org(source_root, root, slug)
        paths = OrgPaths(root=root, slug=slug)
        for plant in placed:
            path = paths.docir_dir / doc_id_filename(plant["doc_id"], ".json")
            doc = json.loads(path.read_text("utf-8"))
            _insert(doc, plant["sentence"])
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", "utf-8")
        paths.review_dir.mkdir(parents=True, exist_ok=True)
        write_model(paths.review_sample_json, _sample(paths, ids))

    answer = {"slug": slug, "seed": seed, "plants": placed,
              "lists": {k: len(v) for k, v in lists.items()}}
    key.parent.mkdir(parents=True, exist_ok=True)
    key.write_text(json.dumps(answer, indent=2) + "\n", "utf-8")
    return answer


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--source-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, required=True, help="scratch directory for the two copies")
    ap.add_argument("--key", type=Path, required=True, help="answer key path, outside --out")
    ap.add_argument("--seed", type=int, default=20261013)
    ap.add_argument("--small", type=int, default=50, help="documents on the short reading list")
    args = ap.parse_args(argv)
    if args.out.resolve() in args.key.resolve().parents:
        raise SystemExit("--key must live outside --out, where no reviewer reads")
    answer = build(args.slug, args.source_root, args.out, args.key, args.seed, args.small)
    print(f"planted {len(answer['plants'])} defects; lists {answer['lists']}; key -> {args.key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
