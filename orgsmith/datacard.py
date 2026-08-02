"""DATA-CARD.md: what this org is, what it exercises, and what it is not.

A DERIVED artifact, like `evals/`, `acl.json`, PERMISSIONS.md, the
baselines, and GENERATION-REPORT.md: a pure function of committed files,
re-emittable for a frozen fixture without touching a ledger, a manifest, or
a word of authored prose. No timestamp, no run id, so re-emitting an
unchanged org rewrites identical bytes.

The card exists because a corpus a consumer cannot characterize is a corpus
they cannot use responsibly. Everything on it is read off committed state,
including the parts that are unflattering: the residual defects the review
board found, the fact-value disagreements the scan recorded, and how far a
keyless lexical baseline gets. A card that only carried the good numbers
would be marketing.
"""

from __future__ import annotations

import json

from .artifacts import load_acl, load_charter, load_manifest
from .naming import strip_control
from .paths import OrgPaths
from .schemas import BaselineSummary

_SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2, "note": 3}


def _cell(text: str) -> str:
    """One markdown cell from a self-reported string. Board summaries are
    model output copied verbatim at ingest and this artifact persists, so
    no control character survives and neither a newline nor a pipe can
    break the row and forge one."""
    return strip_control(text, keep="\n").replace("\n", " ").replace("|", "\\|")


# Charter fields that describe the firm rather than a capability. Excluded
# so the matrix reads as "what does this org exercise?" rather than as a
# dump of the recipe.
_NOT_A_KNOB = {
    "schema_id",
    "slug",
    "name",
    "seed",
    "org_type",
    "founded",
    "domain",
    "headcount",
    "titles",
    "narrative",
    "target_docs",
    "date_range",
    "format_mix",
    "services",
}


def _knob_rows(charter) -> list[tuple[str, str]]:
    """Every capability knob with its value, walked off the charter model
    rather than listed by hand, so a knob added to the schema appears here
    without anyone remembering to add it."""
    from pydantic import BaseModel

    rows: list[tuple[str, str]] = []

    def walk(model, prefix: str) -> None:
        for name in type(model).model_fields:
            if name in _NOT_A_KNOB:
                continue
            value = getattr(model, name)
            label = f"{prefix}{name}"
            if isinstance(value, BaseModel):
                rows.append((label, "on"))
                walk(value, f"{label}.")
            elif value is None:
                # An optional block that is off. Its sub-knobs do not exist
                # for this org, and saying "off" is more honest than
                # printing defaults it never adopted.
                rows.append((label, "off"))
            elif isinstance(value, (list, tuple, dict)):
                continue
            else:
                rows.append((label, str(value)))

    walk(charter, "")
    return rows


def _jsonl(path):
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text("utf-8").splitlines()
        if line.strip()
    ]


def _checksum_line(paths: OrgPaths) -> str | None:
    manifest = paths.root / "CHECKSUMS.md"
    if not manifest.exists():
        return None
    for line in manifest.read_text("utf-8").splitlines():
        if line.startswith(f"| {paths.slug} |"):
            return line
    return None


def render_data_card(paths: OrgPaths) -> str:
    charter = load_charter(paths)
    manifest = load_manifest(paths)
    acl = load_acl(paths)
    retrieval = _jsonl(paths.evals_dir / "retrieval.jsonl")
    extraction = _jsonl(paths.evals_dir / "extraction.jsonl")
    visibility = _jsonl(paths.evals_dir / "visibility.jsonl")

    out: list[str] = [
        f"# Data card: `{charter.slug}`",
        "",
        f"**{charter.name}** ({charter.org_type}), founded "
        f"{charter.founded}.",
        "",
        "Derived from committed state by `python -m orgsmith data-card "
        f"{charter.slug}`. Everything below is recomputed, including the "
        "parts that are unflattering.",
        "",
    ]

    # --- what it is -------------------------------------------------------
    authored = [e for e in manifest if e.authoring == "batchable"]
    static = [e for e in manifest if e.authoring == "static"]
    derived = [e for e in manifest if e.authoring == "derived"]
    culture = charter.doc_culture
    formats: dict[str, int] = {}
    for entry in manifest:
        formats[entry.format] = formats.get(entry.format, 0) + 1
    dates = sorted(e.date for e in manifest)

    out += [
        "## Corpus",
        "",
        f"- **{len(manifest)} documents**: {len(authored)} model-authored, "
        f"{len(static)} deterministic, {len(derived)} derived.",
        "- **Formats**: "
        + ", ".join(
            f"{count} `.{fmt}`" for fmt, count in sorted(formats.items())
        )
        + ".",
        f"- **Document dates**: {dates[0]} to {dates[-1]}."
        if dates
        else "- **Document dates**: none.",
        f"- **Charter window**: {culture.date_range[0]} to "
        f"{culture.date_range[1]}.",
        "",
    ]

    # --- what it exercises ------------------------------------------------
    out += [
        "## Feature matrix",
        "",
        "Every capability knob in this org's recipe, with its value. A knob "
        "that is off is off by choice, and the validator skips its rule "
        "visibly rather than passing it silently.",
        "",
        "| knob | value |",
        "| --- | --- |",
    ]
    out += [f"| `{name}` | `{value}` |" for name, value in _knob_rows(charter)]
    out.append("")

    # --- questions --------------------------------------------------------
    # The first tag is the question family; the rest are entity and
    # engagement ids, which are not families.
    families: dict[str, int] = {}
    for question in retrieval:
        if question["tags"]:
            family = question["tags"][0]
            families[family] = families.get(family, 0) + 1
    unanswerable = [q for q in retrieval if not q["answerable"]]
    acceptable = sum(len(q["acceptable_docs"]) for q in retrieval)
    difficulty: dict[str, int] = {}
    for question in extraction:
        for tag in question["tags"]:
            if tag.startswith(("scan:", "format:")):
                difficulty[tag] = difficulty.get(tag, 0) + 1
    locations: dict[str, int] = {}
    for question in extraction:
        locations[question["location"]] = (
            locations.get(question["location"], 0) + 1
        )

    out += [
        "## Questions",
        "",
        f"- **Retrieval**: {len(retrieval)} questions, of which "
        f"{len(unanswerable)} are unanswerable (correct response: abstain). "
        f"{acceptable} incidental documents are marked acceptable across the "
        "suite.",
        "- Retrieval question families: "
        + (
            ", ".join(f"`{k}` {v}" for k, v in sorted(families.items()))
            or "none"
        )
        + ".",
        f"- **Extraction**: {len(extraction)} questions. Locations: "
        + ", ".join(f"`{k}` {v}" for k, v in sorted(locations.items()))
        + ".",
        "- Extraction difficulty tags: "
        + (
            ", ".join(f"`{k}` {v}" for k, v in sorted(difficulty.items()))
            or "none (no scans, no legacy binaries)"
        )
        + ".",
        f"- **Visibility**: {len(visibility)} questions, one per internal "
        "person.",
        "",
    ]

    # --- splits -----------------------------------------------------------
    splits_path = paths.evals_dir / "splits.json"
    if splits_path.exists():
        splits = json.loads(splits_path.read_text("utf-8"))["splits"]
        gap = len(splits["distractors"]) - len(splits["core"])
        out += [
            "## Splits",
            "",
            "| split | documents |",
            "| --- | ---: |",
        ]
        out += [
            f"| `{name}` | {len(splits[name])} |"
            for name in ("core", "distractors", "noise", "full")
        ]
        out += [
            "",
            f"**Distractor gap = {gap}.** Authored documents that answer no "
            "retrieval or extraction question. A gap of zero means this org "
            "has no lexical distractors and its degradation curve is flat "
            "between `core` and `distractors`; the noise split still "
            "degrades it.",
            "",
            "Splits are a retrieval and extraction device. The visibility "
            "suite is graded over the whole share by nature and contributes "
            "no documents to `core`.",
            "",
        ]

    # --- access -----------------------------------------------------------
    if acl is not None:
        sizes = sorted(len(g.docs) for g in acl.grants)
        out += [
            "## Access control",
            "",
            f"- **Posture**: `{acl.posture}`.",
            f"- **Grants**: {len(acl.grants)}, covering "
            f"{sizes[0]} to {sizes[-1]} documents each "
            f"(median {sizes[len(sizes) // 2]}).",
            "- Grants are access *as of the end of the corpus*, so a person "
            "the roster retires mid-history holds none. That makes a "
            "departed employee a scored visibility question with an empty "
            "expected set, not a case the answer key is blind to.",
            "",
        ]

    # --- label policy and diagnostics -------------------------------------
    diagnostics_path = paths.evals_dir / "diagnostics.json"
    clusters_path = paths.evals_dir / "clusters.json"
    if diagnostics_path.exists():
        diagnostics = json.loads(diagnostics_path.read_text("utf-8"))
        clusters = (
            json.loads(clusters_path.read_text("utf-8"))["clusters"]
            if clusters_path.exists()
            else []
        )
        members = sum(len(c["members"]) for c in clusters)
        out += [
            "## Labels",
            "",
            f"- **Relevance-label policy version "
            f"{diagnostics['policy_version']}** "
            "(`docs/LABEL-POLICY.md`).",
            f"- **Equivalence clusters**: {len(clusters)}, covering "
            f"{members} documents that carry byte-identical evidence to a "
            "canonical document. Returning a member in place of its "
            "canonical is correct.",
            "",
        ]

    # --- residuals --------------------------------------------------------
    out += ["## Known residuals", ""]
    residuals: list[str] = []
    if diagnostics_path.exists():
        diagnostics = json.loads(diagnostics_path.read_text("utf-8"))
        for sighting in diagnostics["unplanned_alias_sightings"]:
            residuals.append(
                f"**Alias disagreement.** `{sighting['path']}` uses the "
                f"nickname \"{_cell(sighting['alias'])}\", which the ledger "
                f"registers to `{sighting['owner']}`, with no planned "
                "mention. The structured layer and the prose disagree and "
                "the prose reports its source faithfully."
            )
        for collision in diagnostics["value_collisions"]:
            residuals.append(
                f"**Value collision.** `{collision['fact_id']}`'s surface "
                f"\"{_cell(collision['value'])}\" also appears in "
                f"{len(collision['paths'])} document(s) outside its "
                "engagement. Returning those is still wrong; they are "
                "recorded so a scoring loss is not a mystery."
            )

    findings_dir = paths.meta_dir / "review" / "findings"
    board: list[tuple[int, str, str, str]] = []
    if findings_dir.is_dir():
        for path in sorted(findings_dir.glob("*.json")):
            data = json.loads(path.read_text("utf-8"))
            for finding in data["findings"]:
                board.append(
                    (
                        _SEVERITY_ORDER.get(finding["severity"], 9),
                        finding["severity"],
                        finding["id"],
                        finding["summary"],
                    )
                )
    if residuals:
        out += [f"- {line}" for line in residuals] + [""]
    if board:
        out += [
            f"The adversarial review board's findings against this org "
            f"({len(board)} across "
            f"{len({f.stem for f in findings_dir.glob('*.json')})} "
            "dimensions), published rather than fixed:",
            "",
            "| severity | id | finding |",
            "| --- | --- | --- |",
        ]
        out += [
            f"| {severity} | `{fid}` | {_cell(summary)} |"
            for _, severity, fid, summary in sorted(board)
        ]
        out += [
            "",
            "The board is the weakest instrument in this project: it shares "
            "blind spots with the generator, its false-positive rate is "
            "unmeasured, and it has been caught publishing a checkable "
            "falsehood. Read it sceptically.",
            "",
        ]
    if not residuals and not board:
        out += [
            "None recorded. This org has no board findings committed and its "
            "corpus-wide scan found no fact-value disagreement.",
            "",
        ]

    # --- baselines --------------------------------------------------------
    summary_path = paths.baselines_dir / "summary.json"
    if summary_path.exists():
        summary = BaselineSummary.model_validate_json(
            summary_path.read_text("utf-8")
        )
        out += [
            "## Keyless baselines",
            "",
            "Where two deliberately dumb retrievers get to. Reference "
            "points, never targets: a question family a lexical baseline "
            "aces was measuring the filename.",
            "",
            "| retriever | split | strict | R@10 | MRR | nDCG@10 |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
        out += [
            f"| {s.retriever} | {s.split} | {s.strict:.1%} | "
            f"{s.recall_at_10:.1%} | {s.mrr:.3f} | {s.ndcg_at_10:.3f} |"
            for s in summary.scores
        ]
        out.append("")

    # --- integrity --------------------------------------------------------
    checksum = _checksum_line(paths)
    if checksum:
        out += [
            "## Integrity",
            "",
            "| org | files | sha256 |",
            "| --- | ---: | --- |",
            checksum,
            "",
            "Verify with `python tools/checksums.py --check`.",
            "",
        ]

    # --- uses and non-claims ----------------------------------------------
    out += [
        "## Recommended uses",
        "",
        "- Developing and regression-testing retrieval, extraction, "
        "people-graph, and access-control-aware systems against a corpus "
        "with a computed answer key.",
        "- Measuring what a format transform costs you: the true page text "
        "of every degraded scan is archived beside it.",
        "- Publishing a reproducible benchmark. Everything here is "
        "fictional and Apache-2.0.",
        "",
        "## Non-claims",
        "",
        "- **This is a specimen, not a sample.** It is chosen to contain "
        "the shapes a system has to handle, not to reproduce a real firm's "
        "document footprint. It is two to four orders of magnitude away "
        "from one, and the engagement book is a deliberate sample of the "
        "firm's own business.",
        "- **Scoring well here does not establish scoring well on a real "
        "corpus.** Nothing in this project measures that transfer.",
        "- **The realism numbers have no validated thresholds** and nothing "
        "about prose quality gates anything, deliberately.",
        "- **The relevance labels are a documented policy, not ground "
        "truth about relevance.** `docs/LABEL-POLICY.md` states what the "
        "scan can and cannot see, including the misses.",
        "",
    ]
    return "\n".join(out) + "\n"


def run_data_card(paths: OrgPaths) -> int:
    text = render_data_card(paths)
    paths.data_card_md.parent.mkdir(parents=True, exist_ok=True)
    paths.data_card_md.write_text(text, encoding="utf-8")
    print(f"data-card: {paths.data_card_md}")
    return 0
