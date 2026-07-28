"""M15: the distributional dashboard.

Deterministic corpus distributions per committed org plus a fleet
aggregate, written to docs/DISTRIBUTIONS.md. Reference lines are
NON-CALIBRATED context: they restate the README's own order-of-magnitude
prose about real firms, not measured target distributions
(`external-validity-program` in BACKLOG.md stays open), and no number here
gates anything.

Committed against the still-frozen fleet before the wave's regenerations,
so M16's deltas are visible in git history. Carries no timestamp: re-running
against unchanged orgs rewrites identical bytes.
"""

from __future__ import annotations

from pathlib import Path

from .artifacts import load_charter, load_foundation, load_manifest
from .paths import OrgPaths
from .review.corpus import load_authored, prose_text, word_count

# The M15-committed frozen-fleet baseline (git 82a23b4), captured BEFORE the
# M13-M16 realism wave regenerated the fleet under the wave's knobs. Frozen
# here as constants so M16's effect is a committed before/after diff rather
# than a claim (SPEC M16, "the wave's deltas are visible in git"). Per org:
# (docs, derived, eml, weekend_frac, mean_words); plus the fleet aggregate.
WAVE_BASELINE_M15 = {
    "ashcombe-advisory": (87, 0, 42, 0.11, 365),
    "brackenridge-civil": (40, 0, 0, 0.40, 699),
    "calderwood-partners": (218, 35, 38, 0.17, 589),
    "dev-mini": (22, 0, 0, 0.36, 717),
    "hollowell-ip": (45, 0, 3, 0.27, 691),
    "meridian-actuarial": (49, 0, 3, 0.22, 675),
    "northgate-staffing": (53, 0, 5, 0.36, 662),
    "saltmarsh-environmental": (40, 0, 0, 0.25, 725),
    "verdant-health": (31, 0, 0, 0.29, 728),
    "**fleet**": (585, 35, 91, 0.22, 606),
}


def committed_slugs(root: Path) -> list[str]:
    """Every org that is committed beside its recipe, sorted."""
    slugs = []
    for meta in sorted((root / "companies").glob("*-metadata")):
        slug = meta.name[: -len("-metadata")]
        if (root / "recipes" / slug).is_dir() and (
            meta / "charter.json"
        ).exists():
            slugs.append(slug)
    return slugs


def org_distributions(paths: OrgPaths) -> dict:
    """One org's distribution row, a pure function of its committed files."""
    charter = load_charter(paths)
    foundation = load_foundation(paths)
    manifest = load_manifest(paths)
    authored = load_authored(paths)
    start, end = charter.doc_culture.date_range
    span_years = (end - start).days / 365.25
    people = len(foundation.people)
    total = len(manifest)
    derived = sum(1 for e in manifest if e.authoring == "derived")
    emails = [e for e in manifest if e.format == "eml"]
    words = [word_count(prose_text(d)) for d in authored.values()]
    weekend = sum(1 for e in manifest if e.date.weekday() >= 5)
    depth: dict[str, int] = {}
    for e in emails:
        key = e.engagement or e.doc_id
        depth[key] = max(
            depth.get(key, 0), int(e.render_params.get("thread_pos", 0)) + 1
        )
    return {
        "slug": charter.slug,
        "people": people,
        "span_years": span_years,
        "docs": total,
        "derived": derived,
        "eml": len(emails),
        "max_thread_depth": max(depth.values(), default=0),
        "weekend_frac": (weekend / total) if total else 0.0,
        "docs_per_person_year": (
            total / (people * span_years) if people and span_years else 0.0
        ),
        "mean_words": (sum(words) / len(words)) if words else 0.0,
    }


def _row(d: dict) -> str:
    return (
        f"| {d['slug']} | {d['people']} | {d['span_years']:.1f} | "
        f"{d['docs']} | {d['derived']} | {d['eml']} | "
        f"{d['max_thread_depth']} | {d['weekend_frac']:.0%} | "
        f"{d['docs_per_person_year']:.2f} | {d['mean_words']:.0f} |"
    )


def _delta(before: float, after: float, pct: bool = False) -> str:
    if pct:
        return f"{before:.0%} → {after:.0%}"
    return f"{before:.0f} → {after:.0f}"


def _wave_before_after(rows: list[dict]) -> list[str]:
    """The M15 frozen baseline against the current derivation, per org, on the
    metrics the realism wave moved. `before` is the WAVE_BASELINE_M15 constant;
    `after` is computed live, so this stays a committed diff, not a claim."""
    out = [
        "## Realism wave: before / after (M15 frozen fleet → M16 regenerated)",
        "",
        "The `before` column is the M15-committed baseline "
        "(`WAVE_BASELINE_M15`, git 82a23b4), captured before any org was "
        "regenerated; `after` is derived live from the current fleet. The wave "
        "turned on a business-day calendar (which pulls weekend-dated meetings "
        "and mail down), real mail threads on the demonstrators (which raises "
        "`.eml` and, being short, lowers mean words), and the noise suite on "
        "the exemplar and the two large orgs (which raises `derived`). "
        "Fee/revenue prose posture also moved but is not a distribution: every "
        "regenerated overview now declares its engagement book a sample, so "
        "documented fees reading as ~1-3% of revenue no longer contradict the "
        "prose. Per-author voice ranges are per-org, in each "
        "`GENERATION-REPORT.md`; `cross-document-voice` stays the standing hard "
        "problem, measured never gated.",
        "",
        "| org | weekend | .eml | derived (noise) | mean words |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    by_slug = {d["slug"]: d for d in rows}
    for slug, base in WAVE_BASELINE_M15.items():
        now = by_slug.get(slug)
        if now is None:
            continue
        b_docs, b_derived, b_eml, b_wknd, b_words = base
        out.append(
            f"| {slug} | {_delta(b_wknd, now['weekend_frac'], pct=True)} | "
            f"{_delta(b_eml, now['eml'])} | "
            f"{_delta(b_derived, now['derived'])} | "
            f"{_delta(b_words, now['mean_words'])} |"
        )
    out.append("")
    return out


def render_distributions(root: Path) -> str:
    rows = [
        org_distributions(OrgPaths(root=root, slug=slug))
        for slug in committed_slugs(root)
    ]
    total_docs = sum(d["docs"] for d in rows)
    total_person_years = sum(d["people"] * d["span_years"] for d in rows)
    agg = {
        "slug": "**fleet**",
        "people": sum(d["people"] for d in rows),
        "span_years": sum(d["span_years"] for d in rows) / max(len(rows), 1),
        "docs": total_docs,
        "derived": sum(d["derived"] for d in rows),
        "eml": sum(d["eml"] for d in rows),
        "max_thread_depth": max(
            (d["max_thread_depth"] for d in rows), default=0
        ),
        "weekend_frac": (
            sum(d["weekend_frac"] * d["docs"] for d in rows) / total_docs
            if total_docs
            else 0.0
        ),
        "docs_per_person_year": (
            total_docs / total_person_years if total_person_years else 0.0
        ),
        "mean_words": (
            sum(d["mean_words"] * d["docs"] for d in rows) / total_docs
            if total_docs
            else 0.0
        ),
    }
    lines = [
        "# Distributional dashboard",
        "",
        "Derived artifact: re-emit with `python -m orgsmith "
        "distributions`. Never edit by hand. Deterministic corpus "
        "distributions for every committed org; the mean-words and "
        "span-years aggregates are doc- and org-weighted respectively. "
        "Nothing here gates anything.",
        "",
        "| org | people | span (yrs) | docs | derived | .eml | max thread "
        "depth | weekend | docs / person-yr | mean words |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | "
        "---: |",
        *[_row(d) for d in rows],
        _row(agg),
        "",
        *_wave_before_after(rows + [agg]),
        "## Reference lines (non-calibrated)",
        "",
        "Order-of-magnitude context restated from the README's \"Where that "
        "sits against a real firm\", NOT measured target distributions: no "
        "reference population has been sampled, and "
        "`external-validity-program` (BACKLOG.md) stays open. Read the gap, "
        "not a score.",
        "",
        "- **Files.** A real ten-person professional-services firm "
        "accumulates thousands to hundreds of thousands of files over a "
        "decade, most of them junk; docs/person-year here sits two to four "
        "orders of magnitude below that, deliberately (specimens, not "
        "samples; docs/SCALE.md).",
        "- **Email.** Ten people sending even 20 messages a working day is "
        "~400,000 messages over eight years; every corpus here is "
        "document-dominant by design, and `.eml` share plus thread depth "
        "measure mechanics, not volume.",
        "- **Noise.** Most real files are duplicates, drafts, and dead "
        "paper. The derived column is each org's deliberate, labeled "
        "fraction of that; zero means every committed document is on "
        "purpose.",
        "- **Weekends.** Uniformly drawn dates land on a weekend ~28.5% of "
        "the time. An org that declares a business calendar should sit "
        "well below that for genres asserting attendance; one that "
        "declares none records its chance-level fraction here.",
        "",
    ]
    return "\n".join(lines)


def run_distributions(root: Path | None = None) -> int:
    root = root or Path.cwd()
    out = root / "docs" / "DISTRIBUTIONS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_distributions(root), encoding="utf-8")
    print(f"distributions: {len(committed_slugs(root))} orgs -> {out}")
    return 0
