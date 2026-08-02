"""Keyless retrieval baselines: reference points, never targets.

Two deliberately dumb retrievers answer the committed retrieval suite and
are graded by the ordinary scorer, as ordinary answer files. The baseline is
a consumer of the eval contract, not a privileged path through it.

They exist for one reason: a score means nothing without a floor. If
filename matching alone answers a question family, that family was measuring
the filename, and the data card says so. Where BM25 falls far short of
ground truth, the corpus is asking something a lexical retriever cannot do.

Pure python, offline, no key, no model, no vectors. The tokenizer is
deliberately ASCII-only (`[a-z0-9]+` over casefolded text) so a unicode
table changing between Python versions cannot move a committed number.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from .artifacts import load_engagements, load_foundation, load_manifest
from .paths import OrgPaths
from .schemas import (
    BaselineScore,
    BaselineSummary,
    RetrievalAnswers,
    write_model,
)

# BM25's standard defaults. Recorded in the emitted summary so a committed
# number can always be traced to the configuration that produced it.
K1 = 1.5
B = 0.75
TOP_K = 10
SPLITS = ("core", "distractors", "noise", "full")

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.casefold())


def _rank(scored: dict[str, float]) -> list[str]:
    """Top documents by score, ties broken by ascending path so the ranking
    is total and a re-run cannot reorder equal scores."""
    ordered = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))
    return [path for path, score in ordered[:TOP_K] if score > 0]


def filename_index(corpus: dict[str, str]):
    """Lexical overlap against the filename alone, ignoring every word of
    the document. The crudest thing that could possibly work, and on a share
    whose filenames carry client names and dates it works embarrassingly
    often, which is the point of measuring it.

    Returns a search function over a corpus indexed once, so a suite of
    questions costs one pass over the documents rather than one per
    question."""
    names = {path: set(tokenize(Path(path).name)) for path in corpus}

    def search(query: str) -> list[str]:
        terms = set(tokenize(query))
        return _rank({path: len(terms & got) for path, got in names.items()})

    return search


def bm25_index(corpus: dict[str, str]):
    """Okapi BM25 over extracted document text, hand-rolled so the tier
    stays dependency-free. Positive idf only: a term in more than half the
    corpus contributes nothing rather than a negative score."""
    counts: dict[str, dict[str, int]] = {}
    lengths: dict[str, int] = {}
    df: dict[str, int] = {}
    for path, text in corpus.items():
        terms = tokenize(text)
        lengths[path] = len(terms)
        mine: dict[str, int] = {}
        for term in terms:
            mine[term] = mine.get(term, 0) + 1
        counts[path] = mine
        for term in mine:
            df[term] = df.get(term, 0) + 1

    total = sum(lengths.values())
    n = len(counts)
    avgdl = (total / n) if n else 0.0
    idfs = {
        term: math.log(1 + (n - seen + 0.5) / (seen + 0.5))
        for term, seen in df.items()
    }
    # A term in more than half the corpus carries no signal; dropping it
    # here rather than per query keeps the inner loop honest and cheap.
    postings: dict[str, list[str]] = {}
    for path, mine in counts.items():
        for term in mine:
            if idfs[term] > 0:
                postings.setdefault(term, []).append(path)

    def search(query: str) -> list[str]:
        if not total:
            return []
        scored: dict[str, float] = {}
        for term in tokenize(query):
            idf = idfs.get(term, 0.0)
            if idf <= 0:
                continue
            for path in postings.get(term, ()):
                freq = counts[path][term]
                denominator = freq + K1 * (
                    1 - B + B * lengths[path] / avgdl
                )
                scored[path] = scored.get(path, 0.0) + (
                    idf * freq * (K1 + 1) / denominator
                )
        return _rank(scored)

    return search


RETRIEVERS = {"filename-only": filename_index, "bm25": bm25_index}


def filename_only(query: str, corpus: dict[str, str]) -> list[str]:
    """One-shot form of `filename_index`, for readers and tests."""
    return filename_index(corpus)(query)


def bm25(query: str, corpus: dict[str, str]) -> list[str]:
    """One-shot form of `bm25_index`, for readers and tests."""
    return bm25_index(corpus)(query)


def answer(retriever, questions, corpus: dict[str, str]) -> RetrievalAnswers:
    """An ordinary answers file: the baseline gets no special treatment from
    the scorer. `retriever` builds an index over the corpus (see
    RETRIEVERS)."""
    search = retriever(corpus)
    return RetrievalAnswers.model_validate(
        {
            "suite": "retrieval",
            "answers": [
                {"id": q.id, "docs": search(q.question)} for q in questions
            ],
        }
    )


def derive_baseline(paths: OrgPaths) -> BaselineSummary:
    """The summary as a pure function of committed state. Split from the
    writer so a staleness test can recompute in memory rather than copy an
    org to disk to find out whether the committed numbers still hold."""
    import json

    from .doctext import DocText
    from .evals.emit import LABEL_POLICY_VERSION
    from .evals.score import load_questions, score_retrieval

    questions = load_questions(paths.evals_dir)
    manifest = load_manifest(paths)
    reader = DocText(paths, load_engagements(paths), load_foundation(paths))
    texts = {
        entry.path: reader.text(entry)
        for entry in manifest
        if (paths.share_dir / entry.path).is_file()
    }
    splits = json.loads(
        (paths.evals_dir / "splits.json").read_text("utf-8")
    )["splits"]

    scores: list[BaselineScore] = []
    for name, retriever in RETRIEVERS.items():
        for split in SPLITS:
            # Each split is its own corpus, so document frequency and average
            # length are computed within it: a retriever searching `core` has
            # not seen the distractors.
            corpus = {p: texts[p] for p in splits[split] if p in texts}
            result = score_retrieval(
                paths.evals_dir,
                answer(retriever, questions, corpus),
                corpus=set(splits[split]),
            )
            ranked = result.ranked or {}
            macro = result.macro or {}
            scores.append(
                BaselineScore(
                    retriever=name,
                    split=split,
                    questions=result.total,
                    strict=round(result.score, 4),
                    precision=macro.get("precision", 0.0),
                    recall=macro.get("recall", 0.0),
                    f1=macro.get("f1", 0.0),
                    recall_at_5=ranked.get("recall@5", 0.0),
                    recall_at_10=ranked.get("recall@10", 0.0),
                    mrr=ranked.get("mrr", 0.0),
                    ndcg_at_10=ranked.get("ndcg@10", 0.0),
                )
            )

    return BaselineSummary(
        slug=paths.slug,
        policy_version=LABEL_POLICY_VERSION,
        config={
            "k1": K1,
            "b": B,
            "top_k": TOP_K,
            "tokenizer": "[a-z0-9]+ over casefolded text",
            "tie_break": "ascending share-relative path",
        },
        scores=scores,
    )


def run_baseline(paths: OrgPaths) -> int:
    summary = derive_baseline(paths)
    paths.baselines_dir.mkdir(parents=True, exist_ok=True)
    write_model(paths.baselines_dir / "summary.json", summary)
    best = max(summary.scores, key=lambda s: s.strict)
    print(
        f"baseline: {len(summary.scores)} scores "
        f"(best strict {best.strict:.1%}, {best.retriever} on {best.split}) "
        f"-> {paths.baselines_dir / 'summary.json'}"
    )
    return 0


_FLEET_HEADER = """\
# Retrieval baselines

Two keyless retrievers answering every committed org's retrieval suite,
graded by the ordinary scorer. Derived, never stored: regenerate with
`python -m orgsmith baseline --fleet`.

**These are reference points, not targets.** They exist so a consumer can
tell a genuinely hard question from a structurally easy one. Nothing here
gates, and no generator change should ever be made to move these numbers:
that is the Goodhart failure this project keeps out of `bin/test` by
construction.

- **filename-only**: lexical overlap between the question and the file's
  name, ignoring its contents entirely.
- **bm25**: Okapi BM25 (k1={k1}, b={b}) over extracted document text,
  hand-rolled, ASCII tokenizer `[a-z0-9]+` over casefolded text, ties broken
  by ascending path, top {top_k} documents returned.

Each split is its own corpus: document frequency and average length are
computed within the split, so a retriever searching `core` has not seen the
distractors. Ground-truth answers score 100% on all of them by construction.

Strict is the exact-set headline. A dumb retriever returning ten documents
almost never matches a required set exactly, so read the ranked columns:
they are where a lexical floor is actually visible.

"""


def _reads_the_body_pay_off(summary: BaselineSummary) -> bool:
    """Whether BM25 leads filename matching on nDCG@10 on any split here."""
    filenames = {
        s.split: s.ndcg_at_10
        for s in summary.scores
        if s.retriever == "filename-only"
    }
    return any(
        s.ndcg_at_10 > filenames.get(s.split, 0.0)
        for s in summary.scores
        if s.retriever == "bm25"
    )


def render_fleet(root: Path) -> str:
    from .distributions import committed_slugs

    lines = [_FLEET_HEADER.format(k1=K1, b=B, top_k=TOP_K)]
    summaries = {}
    for slug in committed_slugs(root):
        summary_path = (
            root / "companies" / f"{slug}-metadata" / "baselines" / "summary.json"
        )
        if summary_path.exists():
            summaries[slug] = BaselineSummary.model_validate_json(
                summary_path.read_text("utf-8")
            )

    leads = [s for s, m in summaries.items() if _reads_the_body_pay_off(m)]
    behind = [s for s in summaries if s not in leads]
    lines.append(
        "## Where reading the body pays off\n\n"
        f"BM25 leads filename matching on nDCG@10 on **{len(leads)} of "
        f"{len(summaries)}** committed orgs: "
        + (", ".join(f"`{s}`" for s in leads) or "none")
        + ".\n"
    )
    if behind:
        lines.append(
            "It falls behind on "
            + ", ".join(f"`{s}`" for s in behind)
            + ". Those are the scan-heavy orgs, where a synthetic OCR layer "
            "degrades exactly the document text BM25 reads while leaving the "
            "filenames intact. That is a property of the corpus worth "
            "knowing, not a defect in either retriever.\n"
        )

    for slug, summary in summaries.items():
        lines.append(f"## {slug}\n")
        lines.append(
            "| retriever | split | questions | strict | R@5 | R@10 | MRR | "
            "nDCG@10 |"
        )
        lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for score in summary.scores:
            lines.append(
                f"| {score.retriever} | {score.split} | {score.questions} | "
                f"{score.strict:.1%} | {score.recall_at_5:.1%} | "
                f"{score.recall_at_10:.1%} | {score.mrr:.3f} | "
                f"{score.ndcg_at_10:.3f} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def run_baseline_fleet(root: Path | None = None) -> int:
    from .distributions import committed_slugs

    root = root or Path.cwd()
    out = root / "docs" / "BASELINES.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_fleet(root), encoding="utf-8")
    print(f"baseline: {len(committed_slugs(root))} orgs -> {out}")
    return 0
