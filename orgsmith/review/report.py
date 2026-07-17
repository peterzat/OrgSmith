"""GENERATION-REPORT.md: what the instrument saw, in one page.

A DERIVED artifact, like `evals/`, `acl.json` and PERMISSIONS.md: it is a
pure function of committed files and may be re-emitted for a frozen fixture
without touching a ledger, a manifest, or a word of authored prose.

It is written under `-metadata/`, never into the share. A report in the
share tree would be a file with no manifest entry, which MAN-01 reads as
tamper evidence, and it would skew the format-mix quota besides.

The report carries no timestamp and no run id, so re-emitting an unchanged
org rewrites identical bytes.
"""

from __future__ import annotations

from ..artifacts import load_charter, load_engagements, load_finance, load_manifest
from ..naming import strip_control
from ..paths import OrgPaths
from ..schemas import CorpusMetrics
from ..state import load_state
from .ingest import load_findings
from .metrics import (
    LONG_RATIO,
    SHORT_RATIO,
    SIMILAR_JACCARD,
    flagged_lengths,
    flagged_pairs,
    run_metrics,
)

_SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2, "note": 3}


def _cell(text: str) -> str:
    """One markdown table cell from a self-reported, untrusted string.

    Generator fields and finding summaries are model output copied verbatim
    at ingest, and this artifact PERSISTS: unlike a rejection printer that
    scrolls past, a forged row here is what a human reads later. No control
    character survives, and neither a newline nor a pipe can break the row
    and forge one.
    """
    return strip_control(text, keep="\n").replace("\n", " ").replace("|", "\\|")


def _provenance_lines(paths: OrgPaths) -> list[str]:
    state = load_state(paths)
    if not state.generators:
        # Every org authored before provenance existed lands here, and that
        # is a reportable fact, not a failure. Nothing gates on this.
        return [
            "Generator: unrecorded. This org was authored before its model "
            "and effort were recorded, or by a pass that did not report "
            "them. Self-reported when present; never verified from artifacts."
        ]
    lines = ["Generator, per batch (self-reported at ingest; not verifiable):", ""]
    lines.append("| work order | model | effort |")
    lines.append("| --- | --- | --- |")
    for wo_id in sorted(state.generators):
        gen = state.generators[wo_id]
        lines.append(f"| {wo_id} | {_cell(gen.model)} | {_cell(gen.effort)} |")
    return lines


def _length_lines(metrics: CorpusMetrics) -> list[str]:
    if not metrics.docs:
        return ["No authored documents."]
    total_words = sum(d.words for d in metrics.docs)
    mean = total_words / len(metrics.docs)
    lines = [
        f"{len(metrics.docs)} authored documents, {total_words} words, "
        f"mean {mean:.0f}.",
        "",
    ]
    flagged = flagged_lengths(metrics)
    if not flagged:
        lines.append(
            f"Every document is within {SHORT_RATIO:.0%}-{LONG_RATIO:.0%} of "
            f"the words its brief asked for."
        )
        return lines
    lines.append(
        f"Off brief (outside {SHORT_RATIO:.0%}-{LONG_RATIO:.0%} of target):"
    )
    lines.append("")
    lines.append("| doc | genre | words | target | ratio |")
    lines.append("| --- | --- | ---: | ---: | ---: |")
    for d in sorted(flagged, key=lambda d: d.ratio):
        lines.append(
            f"| {d.doc_id} | {d.genre} | {d.words} | {d.target_words} | "
            f"{d.ratio:.2f} |"
        )
    return lines


def _similarity_lines(metrics: CorpusMetrics) -> list[str]:
    flagged = flagged_pairs(metrics)
    if not flagged:
        top = metrics.similar_pairs[0].jaccard if metrics.similar_pairs else 0.0
        return [
            f"No same-genre pair reaches {SIMILAR_JACCARD} 4-gram Jaccard "
            f"(highest: {top}).",
        ]
    lines = [
        f"Same-genre pairs at or above {SIMILAR_JACCARD} 4-gram Jaccard. "
        f"High overlap is a measurement, not a verdict: real firms reuse "
        f"templates. The board judges which of these read as reuse.",
        "",
        "| doc a | doc b | genre | jaccard |",
        "| --- | --- | --- | ---: |",
    ]
    for p in flagged:
        lines.append(f"| {p.doc_a} | {p.doc_b} | {p.genre} | {p.jaccard} |")
    return lines


def _fee_coverage_lines(paths: OrgPaths) -> list[str]:
    """Lifetime engagement fees against lifetime revenue, computed with no
    model (engagement-ledger-reads-as-whole-book). The board found the firm
    overview presenting the sampled engagement ledger as the whole book while
    the financial summary posts 20-60x the fee total; this records the ratio so
    a human reads it before trusting the org. A measurement, never a gate: no
    threshold enters any test tier. Reports whether the recipe declares the
    book a sample (engagements.book_is_sample), which is the coherence knob."""
    engagements = load_engagements(paths).engagements
    finance = load_finance(paths)
    charter = load_charter(paths)
    fees = sum(
        int(f.value)
        for e in engagements
        for f in e.facts
        if f.id.endswith(".fee")
    )
    revenue = sum(y.revenue for y in finance.years)
    declared = charter.engagements.book_is_sample
    lines = [
        f"{len(engagements)} documented engagement(s), fees totalling "
        f"${fees:,}, against ${revenue:,} of lifetime revenue.",
        "",
    ]
    if revenue > 0:
        lines.append(
            f"Documented fees are {fees / revenue:.1%} of lifetime revenue."
        )
    lines.append("")
    if declared:
        lines.append(
            "The recipe declares the engagement book a sample "
            "(engagements.book_is_sample), so the firm overview presents these "
            "engagements as representative rather than complete. The gap "
            "between fees and revenue is expected and coherent."
        )
    else:
        lines.append(
            "The recipe does not declare the engagement book a sample, so the "
            "overview may present it as the firm's whole client list. A large "
            "fee/revenue gap here reads as the contradiction the board found "
            "(engagement-ledger-reads-as-whole-book)."
        )
    return lines


def _findings_lines(paths: OrgPaths) -> list[str]:
    findings = load_findings(paths)
    if not findings:
        return [
            "No board findings ingested. Run `/forge-review " + paths.slug + "` "
            "to dispatch the review board; the metrics above stand on their "
            "own without it."
        ]
    lines = [f"{len(findings)} findings from the review board.", ""]
    lines.append("| id | dimension | severity | docs | summary |")
    lines.append("| --- | --- | --- | --- | --- |")
    ordered = sorted(
        findings,
        key=lambda f: (_SEVERITY_ORDER.get(f.severity, 9), f.dimension, f.id),
    )
    for f in ordered:
        docs = ", ".join(f.docs) if f.docs else "corpus"
        summary = _cell(f.summary)
        lines.append(
            f"| {f.id} | {f.dimension} | {f.severity} | {docs} | {summary} |"
        )
    return lines


def render_report(paths: OrgPaths, metrics: CorpusMetrics) -> str:
    manifest = load_manifest(paths)
    parts: list[str] = [
        f"# Generation report: {paths.slug}",
        "",
        "Derived artifact: re-emit with `python -m orgsmith report "
        f"{paths.slug}`. Never edit by hand. Nothing here gates anything; "
        "it is what the quality instrument measured and what the review "
        "board said, for a human to read.",
        "",
        f"{len(manifest)} documents planned; "
        f"{len(metrics.docs)} carry authored prose.",
        "",
        "## Provenance",
        "",
        *_provenance_lines(paths),
        "",
        "## Length against brief",
        "",
        *_length_lines(metrics),
        "",
        "## Same-genre similarity",
        "",
        *_similarity_lines(metrics),
        "",
        "## Fee coverage",
        "",
        *_fee_coverage_lines(paths),
        "",
        "## Review board",
        "",
        *_findings_lines(paths),
        "",
    ]
    return "\n".join(parts)


def run_report(paths: OrgPaths) -> int:
    metrics = run_metrics(paths)
    text = render_report(paths, metrics)
    paths.generation_report_md.parent.mkdir(parents=True, exist_ok=True)
    paths.generation_report_md.write_text(text, encoding="utf-8")
    print(f"report: {paths.generation_report_md}")
    print(f"  metrics: {paths.corpus_metrics_json}")
    lengths, pairs = flagged_lengths(metrics), flagged_pairs(metrics)
    print(
        f"  {len(metrics.docs)} authored docs; {len(lengths)} off brief; "
        f"{len(pairs)} same-genre pairs flagged"
    )
    return 0
