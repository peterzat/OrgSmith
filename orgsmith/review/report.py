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
    author_ranges,
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


def _voice_lines(paths: OrgPaths) -> list[str]:
    """Cross-document voice tics as a RANGE, not a number (M12,
    cross-document-voice). Prints each pre-registered pattern and its count so
    the reader sees exactly what was measured; the strict readings land low and
    the plain words sweep up ordinary English, and no ledger adjudicates
    between them. A measurement, never a gate."""
    from .corpus import load_authored
    from .voice import measure_voice

    tics, total = measure_voice(load_authored(paths))
    if total == 0:
        return ["No authored documents to measure."]
    lines = [
        f"Pre-registered voice patterns over {total} authored documents. This "
        f"is a RANGE across strict and loose readings, not a single count: no "
        f"ledger owns whether two sentences are the same figure, so the strict "
        f"rows disagree and the plain words sweep up ordinary English. Nothing "
        f"here gates.",
        "",
        "| pattern | reading | occurrences | docs |",
        "| --- | --- | ---: | ---: |",
    ]
    for t in tics:
        lines.append(
            f"| `{t.name}` | {_cell(t.description)} | {t.occurrences} | {t.docs} |"
        )
    return lines


def _integrity_lines(paths: OrgPaths) -> list[str]:
    """The recompute half (M15 dashboard split): validator, evals, byte pin.
    These hold exactly or the org is broken, and they say nothing about how
    real the prose reads."""
    from ..validate import collect
    from ..validate.rules import RULES, Context

    try:
        findings, skipped = collect(Context.load(paths))
    except Exception as exc:  # a half-generated org cannot recompute yet
        return [
            f"Validator recompute unavailable here ({type(exc).__name__}); "
            f"run `python -m orgsmith validate {paths.slug}` once the org "
            f"is rendered."
        ]
    errors = [f for f in findings if f["severity"] == "ERROR"]
    skip_ids = ", ".join(s["rule"] for s in skipped) or "none"
    lines = [
        f"Validator: {len(RULES) - len(skipped)} rules run, "
        f"{len(errors)} error(s), {len(findings) - len(errors)} warning(s); "
        f"skipped by charter knob: {skip_ids}.",
        "",
        f"Eval suites derive from the ledgers and score 100% by construction "
        f"(`python -m orgsmith score {paths.slug} --suite ... --answers ...` "
        f"grades an external system). Structure re-derives byte-identically "
        f"from the recipe (the org-tier byte pin).",
    ]
    if errors:
        lines += ["", "THE ORG DOES NOT VALIDATE. First findings:"]
        for f in errors[:10]:
            lines.append(f"- {f['rule']} [{f['target']}] {_cell(f['message'])}")
    return lines


def _author_lines(paths: OrgPaths) -> list[str]:
    rows = author_ranges(paths)
    if not rows:
        return ["No authored documents to measure."]
    lines = [
        "Per-author 4-gram Jaccard proxies, computed with no model: within "
        "is an author's own doc pairs, cross is their docs against every "
        "other author's, early/late is the overlap of the author's "
        "first-half shingles with their second half in date order "
        "(consistency over time). Ranges beside the tic table above, never "
        "gates: similarity is structurally blind to template collapse "
        "(docs/REVIEW-CALIBRATION.md), so this is context for the board's "
        "voice reading, not a verdict.",
        "",
        "| author | docs | within mean (min-max) | cross mean | early/late |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for r in rows:
        within = (
            "-"
            if r.within is None
            else f"{r.within[1]:.4f} ({r.within[0]:.4f}-{r.within[2]:.4f})"
        )
        cross = "-" if r.cross is None else f"{r.cross:.4f}"
        early_late = "-" if r.early_late is None else f"{r.early_late:.4f}"
        lines.append(
            f"| {r.author} | {r.docs} | {within} | {cross} | {early_late} |"
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
        # M15: the two-dashboard split. Integrity is recomputation against
        # ground truth (holds exactly or the org is broken); Realism is
        # measurement and judgment (ranges, never gates). The hard line: no
        # number appears in the other's context.
        "## Integrity dashboard",
        "",
        "Recomputation against ground truth. These hold exactly or the org "
        "is broken -- and they say nothing about how real the prose reads. "
        "No realism number appears here.",
        "",
        *_integrity_lines(paths),
        "",
        "## Realism dashboard",
        "",
        "Measurement and judgment: lengths, similarity, voice ranges, and "
        "the board's opinion. Nothing here gates, no threshold is "
        "validated, and no integrity number appears here.",
        "",
        "### Length against brief",
        "",
        *_length_lines(metrics),
        "",
        "### Same-genre similarity",
        "",
        *_similarity_lines(metrics),
        "",
        "### Fee coverage",
        "",
        *_fee_coverage_lines(paths),
        "",
        "### Cross-document voice",
        "",
        *_voice_lines(paths),
        "",
        "### Per-author similarity proxies",
        "",
        *_author_lines(paths),
        "",
        "### Review board",
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
