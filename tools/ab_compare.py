#!/usr/bin/env python3
"""M17c: is the two-arm comparison actually controlled?

SPEC.md 2026-08-03 criterion three: across arms the share tree and the
manifest's doc ids, genres, dates and authors are identical, `foundation.json`
and the finance and people ledgers are byte-identical, and "every remaining
difference is enumerated and attributed to a named knob rather than
hand-waved".

This is that enumeration, as a check rather than a report. Every difference
between the two arms' deterministic artifacts must map to an entry in
`ATTRIBUTION`; anything else exits non-zero. The point is the failure case: a
future knob, a reordered draw, or a stray edit that moves something the arms
were supposed to share would otherwise show up as a structural-axis
difference and be read as the outline work doing something.

Scoped to the deterministic stages on purpose. After authoring, `docir/` and
the rendered share differ between arms by design -- that difference is the
prose, and measuring it is `--structure`'s job, not this one's.

Deterministic, offline, model-free. Run from the repo root:

    python tools/ab_compare.py --control scratch/arms/alpha \\
                               --treatment scratch/arms/beta quillon-harbor
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orgsmith.artifacts import load_manifest  # noqa: E402
from orgsmith.paths import OrgPaths  # noqa: E402
from orgsmith.review import structure  # noqa: E402
from orgsmith.review.corpus import load_authored  # noqa: E402

# Every same-genre pair, not the reading list. `compute_pairs` defaults to
# STRUCTURAL_TOP_N = 50 because that is how many rows a human will read in
# GENERATION-REPORT.md; comparing two arms on their top 50 would compare two
# truncations and miss exactly the case that matters, where the outline work
# moves the BODY of the distribution and leaves its head alone. Nothing here
# may become a threshold: SPEC.md's "nothing that is not an oracle may gate"
# applies to this file too.
ALL_PAIRS = 10**9

# Every artifact or manifest field the arms are allowed to differ in, and the
# knob that accounts for it. A difference outside this map is a confound.
ATTRIBUTION: dict[str, str] = {
    "ledger/engagements.json": "engagements.scope",
    "ledger/mention_map.json": "doc_culture.client_facing_reports",
    "manifest:render_params": "doc_culture.outline_variety",
    "manifest:key_facts": "engagements.scope",
    "manifest:facts_refs": "engagements.scope",
    "manifest:mentions": "doc_culture.client_facing_reports",
    "manifest:participants": "doc_culture.client_facing_reports",
}

# Manifest fields that identify a document rather than describe its content.
# These carry the control: if any of them moved, the two arms are not planning
# the same corpus and no downstream comparison means anything.
IDENTITY_FIELDS = (
    "doc_id",
    "genre",
    "date",
    "authors",
    "path",
    "format",
    "engagement",
    "title",
    "rev",
    "authoring",
)


def _manifest(paths: OrgPaths) -> list[dict]:
    return [
        json.loads(line)
        for line in paths.manifest_jsonl.read_text().splitlines()
        if line.strip()
    ]


def compare(control: OrgPaths, treatment: OrgPaths) -> tuple[list[str], list[str]]:
    """(attributed differences, unattributed differences)."""
    attributed: list[str] = []
    unattributed: list[str] = []

    def note(key: str, detail: str) -> None:
        knob = ATTRIBUTION.get(key)
        (attributed if knob else unattributed).append(
            f"{detail} -> {knob}" if knob else detail
        )

    # foundation.json and every ledger, byte for byte.
    if control.foundation_json.read_bytes() != treatment.foundation_json.read_bytes():
        note("foundation.json", "foundation.json differs")

    names = sorted(
        {p.name for p in control.ledger_dir.glob("*.json")}
        | {p.name for p in treatment.ledger_dir.glob("*.json")}
    )
    for name in names:
        a, b = control.ledger_dir / name, treatment.ledger_dir / name
        if not a.is_file() or not b.is_file():
            note(f"ledger/{name}", f"ledger/{name} exists in only one arm")
        elif a.read_bytes() != b.read_bytes():
            note(f"ledger/{name}", f"ledger/{name} differs")

    # The manifest, field by field.
    ma, mb = _manifest(control), _manifest(treatment)
    if len(ma) != len(mb):
        unattributed.append(
            f"manifest length differs: {len(ma)} vs {len(mb)}. The arms are "
            "not planning the same corpus; nothing downstream is comparable."
        )
        return attributed, unattributed

    counts: dict[str, int] = {}
    for x, y in zip(ma, mb):
        if x.get("doc_id") != y.get("doc_id"):
            unattributed.append(
                f"manifest order diverged at {x.get('doc_id')} / {y.get('doc_id')}"
            )
            return attributed, unattributed
        for field in set(x) | set(y):
            if x.get(field) != y.get(field):
                counts[field] = counts.get(field, 0) + 1

    for field in sorted(counts):
        n = counts[field]
        if field in IDENTITY_FIELDS:
            unattributed.append(
                f"manifest:{field} differs in {n} entries -- this is an "
                "IDENTITY field; the arms are not the same corpus"
            )
        else:
            note(f"manifest:{field}", f"manifest:{field} differs in {n} of {len(ma)}")

    return attributed, unattributed


def arm_pairs(paths: OrgPaths) -> list:
    """Every same-genre structural pair for one arm, untruncated.

    Mirrors `metrics.compute`'s eligibility exactly (authored `batchable`
    only), because a derived document is a byte copy of its source and would
    score ~1.0 against it for reasons that have nothing to do with an author.
    Diverging from that rule here would make the two arms' numbers
    incomparable with the ones their own GENERATION-REPORTs carry.
    """
    authored = load_authored(paths)
    entries = [e for e in load_manifest(paths) if e.doc_id in authored]
    eligible = {
        e.doc_id: authored[e.doc_id] for e in entries if e.authoring == "batchable"
    }
    pairs, _ = structure.compute_pairs(
        eligible, {e.doc_id: e.genre for e in entries}, top_n=ALL_PAIRS
    )
    return pairs


def _dist(values: list[float]) -> dict:
    if not values:
        return {}
    ordered = sorted(values)

    def q(f: float) -> float:
        return ordered[min(len(ordered) - 1, int(f * len(ordered)))]

    return {
        "n": len(ordered),
        "mean": statistics.fmean(ordered),
        "p50": statistics.median(ordered),
        "p75": q(0.75),
        "p90": q(0.90),
        "max": ordered[-1],
    }


def _row(label: str, d: dict) -> str:
    if not d:
        return f"  {label:26s} (no pairs)"
    return (
        f"  {label:26s} n={d['n']:4d}  mean={d['mean']:.4f}  "
        f"p50={d['p50']:.4f}  p75={d['p75']:.4f}  p90={d['p90']:.4f}  "
        f"max={d['max']:.4f}"
    )


def report_structure(control: OrgPaths, treatment: OrgPaths) -> int:
    """Both arms' full same-genre distributions, shape and openers separately.

    Reported, never judged. This function computes no verdict and applies no
    threshold; what counts as a change is written down in
    docs/M17C-EVIDENCE-STANDARD.md before either arm was authored.
    """
    arms = {"control": arm_pairs(control), "treatment": arm_pairs(treatment)}
    for name, pairs in arms.items():
        if not pairs:
            print(
                f"{name}: no authored documents yet. Run the authoring pass "
                "for this arm before comparing."
            )
            return 1

    for limb in ("shape", "openers", "combined"):
        print(f"\n{limb}:")
        for name, pairs in arms.items():
            vals = [
                (p.shape + p.openers) / 2 if limb == "combined" else getattr(p, limb)
                for p in pairs
            ]
            print(_row(name, _dist(vals)))

    genres = sorted({p.genre for p in arms["treatment"]} | {p.genre for p in arms["control"]})
    print("\nper genre, combined:")
    for genre in genres:
        for name, pairs in arms.items():
            vals = [(p.shape + p.openers) / 2 for p in pairs if p.genre == genre]
            print(_row(f"{genre}/{name}", _dist(vals)))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--control", type=Path, required=True, help="control arm root")
    ap.add_argument("--treatment", type=Path, required=True, help="treatment arm root")
    ap.add_argument(
        "--structure",
        action="store_true",
        help="report both arms' full structural distributions (needs authored prose)",
    )
    args = ap.parse_args(argv)

    if args.structure:
        return report_structure(
            OrgPaths(root=args.control, slug=args.slug),
            OrgPaths(root=args.treatment, slug=args.slug),
        )

    control = OrgPaths(root=args.control, slug=args.slug)
    treatment = OrgPaths(root=args.treatment, slug=args.slug)
    attributed, unattributed = compare(control, treatment)

    identical = [
        f
        for f in IDENTITY_FIELDS
        if not any(u.startswith(f"manifest:{f} ") for u in unattributed)
    ]
    print(f"identity fields identical: {', '.join(identical)}")
    print(f"\nattributed differences ({len(attributed)}):")
    for line in attributed:
        print(f"  {line}")

    if unattributed:
        print(f"\nUNATTRIBUTED differences ({len(unattributed)}):")
        for line in unattributed:
            print(f"  {line}")
        print(
            "\nThe comparison is NOT controlled. Every one of the above would "
            "show up downstream as a difference between the arms and be read "
            "as the outline work doing something. Attribute it to a knob in "
            "ATTRIBUTION, or find what moved."
        )
        return 1

    print("\nControlled: every difference maps to a declared arm knob.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
