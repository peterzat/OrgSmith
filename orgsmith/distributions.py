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
