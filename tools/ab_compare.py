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
import itertools
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orgsmith.artifacts import load_manifest  # noqa: E402
from orgsmith.paths import OrgPaths  # noqa: E402
from orgsmith.review import structure  # noqa: E402
from orgsmith.review.corpus import (  # noqa: E402
    jaccard,
    load_authored,
    prose_text,
    shingles,
)

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


def compare(
    control: OrgPaths, treatment: OrgPaths
) -> tuple[list[str], list[str], bool]:
    """(attributed differences, unattributed differences, identity check ran).

    The third value is False on the early-return paths, where the manifests
    are too far apart for a per-entry comparison to mean anything. Callers
    must not read the absence of an identity complaint as a clean identity
    check: on those paths the fields were never compared at all.
    """
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
        return attributed, unattributed, False

    counts: dict[str, int] = {}
    for x, y in zip(ma, mb):
        if x.get("doc_id") != y.get("doc_id"):
            unattributed.append(
                f"manifest order diverged at {x.get('doc_id')} / {y.get('doc_id')}"
            )
            return attributed, unattributed, False
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

    return attributed, unattributed, True


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


def outline_of(paths: OrgPaths) -> dict[str, str]:
    """{doc_id: outline id} for every document the plan dealt a skeleton.

    Empty for a control arm, which is what makes the same-skeleton split
    below a treatment-arm analysis only.
    """
    out = {}
    for entry in _manifest(paths):
        outline = (entry.get("render_params") or {}).get("outline")
        if outline:
            out[entry["doc_id"]] = outline
    return out


def split_by_outline(pairs: list, outlines: dict[str, str]) -> tuple[list, list, list]:
    """(same skeleton, different skeleton, unknown).

    The first discriminating comparison in docs/M17C-EVIDENCE-STANDARD.md.
    Treatment pairs whose two documents were dealt the SAME outline were
    asked for the same things in the same order, exactly as every
    control-arm document of that genre was. If those still score like the
    control's pairs, the outline work relocated the convergence into groups
    of the pool size rather than reducing it, and that is the smaller claim
    the standard says must be reported instead.
    """
    same, different, unknown = [], [], []
    for pair in pairs:
        a, b = outlines.get(pair.doc_a), outlines.get(pair.doc_b)
        if a is None or b is None:
            unknown.append(pair)
        elif a == b:
            same.append(pair)
        else:
            different.append(pair)
    return same, different, unknown


def lexical_scores(paths: OrgPaths) -> list[tuple[str, str, str, float]]:
    """Same-genre 4-gram Jaccard, as (doc_a, doc_b, genre, score).

    The second discriminating comparison, and the standard calls it the most
    informative number the experiment produces: a skeleton constrains what a
    document contains, not which words it uses, so a drop here is far less
    mechanically forced than a drop in shape.

    ZEROS ARE KEPT, which is the one place this deliberately diverges from
    `metrics.compute`. That function drops non-overlapping pairs because it
    is building a reading list. Dropping them here would let the two arms'
    pair counts differ for a reason that has nothing to do with the
    treatment, and a mean over "pairs that happened to overlap at all" is
    not comparable across arms.
    """
    authored = load_authored(paths)
    entries = [e for e in load_manifest(paths) if e.doc_id in authored]
    eligible = {e.doc_id: e for e in entries if e.authoring == "batchable"}
    grams = {d: shingles(prose_text(authored[d])) for d in eligible}
    scores = []
    for a, b in itertools.combinations(sorted(grams), 2):
        if eligible[a].genre != eligible[b].genre:
            continue
        scores.append((a, b, eligible[a].genre, jaccard(grams[a], grams[b])))
    return scores


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


def noise_floor(control: list, replicate: list) -> dict:
    """How far apart two runs of the SAME arm land.

    The control replicate shares the control's recipe and seed, so its work
    orders are byte-identical and the only thing that varied is the model's
    sampling. Whatever separates these two is what a control-to-treatment gap
    has to clear before it means anything.

    Two figures, because they answer different questions and the gap between
    them is itself the diagnostic:

    - `mean`/`p50`/`p75`/`p90` -- the AGGREGATE `|delta|` per summary
      statistic. The like-for-like comparator for the treatment's own
      aggregate delta, computed by the same estimator.
    - `paired_mean`/`paired_p90` over `paired_n` -- the per-pair spread of
      `|control - replicate|` across the pair keys the two arms share. The
      arms plan the same corpus, so nearly every key exists in both.
      Summary statistics CANCEL: two runs in which every pair moved can
      report an aggregate delta of 0.0, and a floor of zero is failure
      toward significance. When the paired spread is large while the
      aggregate deltas are near zero, cancellation is hiding real
      volatility and the aggregate comparison must not be read on its own.

    One replicate pair gives one sample, not a variance. BOTH values are
    magnitudes to compare against, never significance tests, and nothing
    downstream may turn either into a threshold.
    """
    a = _dist([(p.shape + p.openers) / 2 for p in control])
    b = _dist([(p.shape + p.openers) / 2 for p in replicate])
    if not a or not b:
        return {}
    out = {k: abs(a[k] - b[k]) for k in ("mean", "p50", "p75", "p90") if k in a}
    rep = {(p.doc_a, p.doc_b): (p.shape + p.openers) / 2 for p in replicate}
    paired = _dist(
        [
            abs((p.shape + p.openers) / 2 - rep[(p.doc_a, p.doc_b)])
            for p in control
            if (p.doc_a, p.doc_b) in rep
        ]
    )
    if paired:
        out["paired_n"] = paired["n"]
        out["paired_mean"] = paired["mean"]
        out["paired_p90"] = paired["p90"]
    return out


def report_structure(
    control: OrgPaths, treatment: OrgPaths, replicate: OrgPaths | None = None
) -> int:
    """Every arm's full same-genre distribution, shape and openers separately.

    Reported, never judged. This function computes no verdict and applies no
    threshold; what counts as a change is written down in
    docs/M17C-EVIDENCE-STANDARD.md before either arm was authored.
    """
    arms = {"control": arm_pairs(control), "treatment": arm_pairs(treatment)}
    if replicate is not None:
        arms["replicate"] = arm_pairs(replicate)
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

    if "replicate" in arms:
        floor = noise_floor(arms["control"], arms["replicate"])
        print("\nnoise floor (control vs its own replicate, combined):")
        agg = {k: v for k, v in floor.items() if not k.startswith("paired_")}
        print("  aggregate: " + "  ".join(f"|d {k}|={v:.4f}" for k, v in agg.items()))
        if "paired_mean" in floor:
            print(
                f"  paired ({floor['paired_n']} shared pair keys): "
                f"mean |d|={floor['paired_mean']:.4f}  "
                f"p90 |d|={floor['paired_p90']:.4f}"
            )
        elif agg:
            print("  paired: the two arms share no pair key; NOT a measured zero")
        print(
            "  Read: a control-to-treatment gap smaller than the matching "
            "aggregate number here is indistinguishable from authoring "
            "nondeterminism. The paired figure is the per-pair movement the "
            "aggregate cancels: when it is large while the aggregate deltas "
            "are near zero, the aggregate comparison is hiding volatility and "
            "must not be read on its own. One replicate pair, so both are "
            "magnitudes to beat, not a variance or a significance test."
        )

    genres = sorted(
        {p.genre for p in arms["treatment"]} | {p.genre for p in arms["control"]}
    )
    print("\nper genre, combined:")
    for genre in genres:
        for name, pairs in arms.items():
            vals = [(p.shape + p.openers) / 2 for p in pairs if p.genre == genre]
            print(_row(f"{genre}/{name}", _dist(vals)))

    # Discriminating comparison 1: same-skeleton treatment pairs against the
    # control's pairs. The headline above is close to mechanically guaranteed;
    # this is not.
    outlines = outline_of(treatment)
    same, different, unknown = split_by_outline(arms["treatment"], outlines)
    print("\nsame-skeleton split (treatment), combined:")
    if not outlines:
        print("  treatment arm carries no outline ids; is outline_variety on?")
    else:
        combined = lambda ps: [(p.shape + p.openers) / 2 for p in ps]  # noqa: E731
        print(_row("control (all pairs)", _dist(combined(arms["control"]))))
        print(_row("treatment same skeleton", _dist(combined(same))))
        print(_row("treatment diff skeleton", _dist(combined(different))))
        if unknown:
            print(_row("treatment unassigned", _dist(combined(unknown))))
        print(
            "  Read: if 'same skeleton' sits near 'control (all pairs)', the "
            "outline work relocated convergence rather than reducing it."
        )

    # Discriminating comparison 2: the lexical axis, which no outline controls.
    print("\nlexical 4-gram Jaccard (zeros kept), same-genre:")
    lex_arms = [("control", control), ("treatment", treatment)]
    if replicate is not None:
        lex_arms.append(("replicate", replicate))
    for name, paths in lex_arms:
        print(_row(name, _dist([s for _, _, _, s in lexical_scores(paths)])))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--control", type=Path, required=True, help="control arm root")
    ap.add_argument("--treatment", type=Path, required=True, help="treatment arm root")
    ap.add_argument(
        "--replicate",
        type=Path,
        default=None,
        help="control-replicate arm root; adds the noise floor to --structure",
    )
    ap.add_argument(
        "--structure",
        action="store_true",
        help="report every arm's full structural distribution (needs authored prose)",
    )
    args = ap.parse_args(argv)

    if args.structure:
        return report_structure(
            OrgPaths(root=args.control, slug=args.slug),
            OrgPaths(root=args.treatment, slug=args.slug),
            OrgPaths(root=args.replicate, slug=args.slug) if args.replicate else None,
        )

    control = OrgPaths(root=args.control, slug=args.slug)
    treatment = OrgPaths(root=args.treatment, slug=args.slug)
    attributed, unattributed, identity_checked = compare(control, treatment)

    if identity_checked:
        identical = [
            f
            for f in IDENTITY_FIELDS
            if not any(u.startswith(f"manifest:{f} ") for u in unattributed)
        ]
        print(f"identity fields identical: {', '.join(identical)}")
    else:
        print("identity fields: NOT CHECKED (bailed before the per-entry comparison)")
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
