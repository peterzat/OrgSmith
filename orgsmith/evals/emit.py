"""emit-evals: deterministic golden suites derived from ground truth.

The oracle for external systems. Every question is a pure function of the
ledgers and manifest: the generator planted the facts and mentions, so it
knows exactly which documents answer what. No model is involved, ever.
"""

from __future__ import annotations

import json

from ..artifacts import (
    load_charter,
    load_engagements,
    load_foundation,
    load_graph,
    load_manifest,
    load_mention_map,
)
from ..paths import OrgPaths
from ..schemas import (
    GraphEntityExpected,
    GraphExpected,
    RetrievalQuestion,
    dump_json,
    write_model,
)
from ..state import load_state, require_stages

_README = """\
# Golden eval suites for `{slug}`

Emitted by `python -m orgsmith emit-evals {slug}`. Deterministic: derived
entirely from this org's ground-truth ledgers. You do not need OrgSmith
source (or any model) to be graded; everything required is in this
directory.

## retrieval.jsonl

One question per line: `id`, `question`, `expected_docs` (share-relative
paths), `tags`. Run your retrieval system over the `companies/{slug}/`
share and write an answers file:

```json
{{"suite": "retrieval",
  "answers": [
    {{"id": "q:0001", "docs": ["Engagements/Client X/some-file.pdf"]}}
  ]}}
```

A question is correct when your doc set exactly matches `expected_docs`.
Score: `python -m orgsmith score --suite retrieval --answers answers.json
--evals-dir <this directory>`.

## graph_expected.json

Canonical entities (with `aliases`: any alias earns full credit) and typed
edges. Answers file:

```json
{{"suite": "graph",
  "entities": [{{"name": "Jane Q. Example", "kind": "person"}}],
  "edges": [{{"src": "Jane Q. Example", "dst": "Example Corp",
             "kind": "works_at"}}]}}
```

Entity names are matched case-insensitively against canonical names and
aliases. Edges are scored precision/recall after resolving names the same
way.
"""


def build_retrieval(
    charter, foundation, engagements, manifest, mention_map
) -> list[RetrievalQuestion]:
    questions: list[tuple[str, list[str], list[str]]] = []

    def docs_with_fact(ref: str) -> list[str]:
        return sorted(e.path for e in manifest if ref in e.facts_refs)

    for eng in engagements.engagements:
        questions.append(
            (
                f"Which documents state the fixed fee for the {eng.title} "
                f"engagement?",
                docs_with_fact(f"f:{eng.id}.fee"),
                ["fact:money", eng.id],
            )
        )
        questions.append(
            (
                f"Which documents state the start date of the {eng.title} "
                f"engagement?",
                docs_with_fact(f"f:{eng.id}.start"),
                ["fact:date", eng.id],
            )
        )
        questions.append(
            (
                f"Which documents identify the client organization of the "
                f"{eng.title} engagement?",
                docs_with_fact(f"f:{eng.id}.client"),
                ["fact:text", eng.id],
            )
        )

    for entry in manifest:
        if entry.genre == "financial_summary":
            year = entry.render_params["year"]
            questions.append(
                (
                    f"Which document is the FY{year} financial summary?",
                    [entry.path],
                    ["workbook"],
                )
            )
    overview_docs = sorted(
        e.path for e in manifest if e.genre == "company_overview"
    )
    if overview_docs:
        questions.append(
            (
                f"Which document gives an overview of {charter.name}?",
                overview_docs,
                ["firm"],
            )
        )

    if mention_map is not None:
        by_path = {e.doc_id: e.path for e in manifest}
        for person in foundation.people:
            docs = sorted(
                {
                    by_path[r.doc_id]
                    for r in mention_map.mentions
                    if r.entity == person.id
                }
            )
            if docs:
                questions.append(
                    (
                        f"Which documents mention {person.name}?",
                        docs,
                        ["mention:person", person.id],
                    )
                )
            for alias in person.aliases:
                alias_docs = sorted(
                    {
                        by_path[r.doc_id]
                        for r in mention_map.mentions
                        if r.entity == person.id and r.surface == alias
                    }
                )
                if alias_docs:
                    questions.append(
                        (
                            f"Which documents refer to someone as "
                            f"“{alias}”?",
                            alias_docs,
                            ["mention:alias", person.id],
                        )
                    )

    return [
        RetrievalQuestion(
            id=f"q:{i:04d}", question=text, expected_docs=docs, tags=tags
        )
        for i, (text, docs, tags) in enumerate(questions, start=1)
        if docs
    ]


def build_graph_expected(charter, foundation, graph) -> GraphExpected:
    entities: list[GraphEntityExpected] = []
    entities.append(
        GraphEntityExpected(
            id=f"x:{charter.slug}", canonical=charter.name, kind="org"
        )
    )
    for p in foundation.people:
        entities.append(
            GraphEntityExpected(
                id=p.id,
                canonical=p.name,
                aliases=sorted(set(p.aliases) | {p.email}),
                kind="person",
            )
        )
    for org in foundation.external_orgs:
        entities.append(
            GraphEntityExpected(id=org.id, canonical=org.name, kind="org")
        )
    for xp in foundation.external_people:
        entities.append(
            GraphEntityExpected(
                id=xp.id, canonical=xp.name, aliases=[xp.email], kind="person"
            )
        )
    # Only entity-to-entity edges belong in the scoring contract:
    # participant edges point at engagement ids, which an external system
    # answering in entity names cannot express. They remain ground truth in
    # ledger/graph.json.
    scorable = [e for e in graph.edges if e.kind != "participant"]
    return GraphExpected(slug=charter.slug, entities=entities, edges=scorable)


def run_emit_evals(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "charter", "foundation", "fabric", "docplan")

    charter = load_charter(paths)
    foundation = load_foundation(paths)
    engagements = load_engagements(paths)
    graph = load_graph(paths)
    manifest = load_manifest(paths)
    mention_map = load_mention_map(paths)

    questions = build_retrieval(
        charter, foundation, engagements, manifest, mention_map
    )
    expected = build_graph_expected(charter, foundation, graph)

    paths.evals_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(q.model_dump(mode="json"), ensure_ascii=False)
        for q in questions
    ]
    (paths.evals_dir / "retrieval.jsonl").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    write_model(paths.evals_dir / "graph_expected.json", expected)
    (paths.evals_dir / "README.md").write_text(
        _README.format(slug=charter.slug), encoding="utf-8"
    )
    print(
        f"emit-evals: {len(questions)} retrieval questions, "
        f"{len(expected.entities)} graph entities -> {paths.evals_dir}"
    )
    return 0
