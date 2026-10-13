#!/usr/bin/env python3
"""Count the numbers an author wrote that no placeholder supplied (M17d).

M17c's AIRLOCK-01 found the airlock stops a model transcribing a ledger value
but not inventing one: two identical control runs authored 0 and 18 such
numbers across their shared documents. This is the instrument the M17d Opus
5.5 probe pre-registered for that axis, kept deliberately simple so that what
it counts is obvious from reading it:

- the text is `prose_text` with every `{{fact:...}}` placeholder removed, so
  a value the ledger supplies is never counted;
- a number is a run of digits, with thousands separators allowed;
- only values of 10 or more count (small counts are ordinary prose: "two of
  the three", "phase 2");
- four-digit values from 1900 to 2099 are years and are not counted;
- each document contributes its DISTINCT values, so a number repeated in one
  document counts once.

It measures and never gates. Deterministic, offline, model-free:

    python tools/probe_numbers.py quillon-harbor --root scratch/arms/alpha
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orgsmith.paths import OrgPaths  # noqa: E402
from orgsmith.review.corpus import load_authored, prose_text  # noqa: E402

_PLACEHOLDER = re.compile(r"\{\{fact:[^}]*\}\}")
_NUMBER = re.compile(r"(?<![\w])\d{1,3}(?:,\d{3})+(?![\d])|(?<![\w,])\d+(?![\d])")


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


def per_doc(paths: OrgPaths) -> dict[str, set[int]]:
    return {
        doc_id: numbers_in(prose_text(doc))
        for doc_id, doc in sorted(load_authored(paths).items())
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--docs", help="comma-separated doc ids to restrict to")
    args = ap.parse_args(argv)

    counts = per_doc(OrgPaths(root=args.root, slug=args.slug))
    if args.docs:
        wanted = set(args.docs.split(","))
        counts = {k: v for k, v in counts.items() if k in wanted}
    total = sum(len(v) for v in counts.values())
    with_any = sum(1 for v in counts.values() if v)
    print(f"{args.root}: {total} unowned numbers across {with_any} of {len(counts)} docs")
    for doc_id, values in counts.items():
        if values:
            shown = ", ".join(str(v) for v in sorted(values))
            print(f"  {doc_id}: {len(values)} ({shown})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
