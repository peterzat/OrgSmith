"""emit-evals: deterministic golden suites derived from ground truth.

The oracle for external systems. Every question is a pure function of the
ledgers and manifest: the generator planted the facts and mentions, so it
knows exactly which documents answer what. No model is involved, ever.
"""

from __future__ import annotations

import json

from ..artifacts import (
    load_acl,
    load_charter,
    load_engagements,
    load_foundation,
    load_graph,
    load_manifest,
    load_mention_map,
)
from ..paths import OrgPaths
from ..schemas import (
    ExtractionQuestion,
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

## extraction.jsonl

One planted fact per line: `id`, `fact_id`, `question`, `expected_value`
(the exact surface form as rendered in the corpus), `expected_docs`, and
`location`: where the surface lives. `body` is ordinary document text;
`signature_page` means only the final page of the pdf; `filename` means
only the document's filename, never its text. Extract each value and cite
the documents it came from:

```json
{{"suite": "extraction",
  "answers": [
    {{"id": "xq:0001", "value": "$105,000",
      "docs": ["Engagements/Client X/some-file.pdf"]}}
  ]}}
```

A question is correct when `value` equals `expected_value` exactly
(surrounding whitespace ignored) and `docs` exactly matches
`expected_docs`. Score: `python -m orgsmith score --suite extraction
--answers answers.json --evals-dir <this directory>`.

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
way. Entities may carry `ambiguity:<class>` tags (surname-collision,
nickname-alias, multi-affiliation); the scorer reports per-class recall
alongside the overall score when tags are present.
"""

# Appended only when extraction questions carry difficulty tags, so
# pre-M5 orgs (no scans, no legacy binaries) re-emit byte-identical
# README files.
_README_FORMAT_TAGS = """
## Difficulty tags on extraction questions

Extraction questions may carry tags describing where their expected
documents live: `scan:ocr` (a degraded raster scan whose extractable
text is a synthetic OCR layer, with OCR-style corruptions outside the
planted surfaces), `scan:image-only` (a scan with no text layer at all;
the value exists only as pixels, and the org's `-metadata/scans/`
directory archives the true page text), and `format:legacy` (a pre-2007
`.doc`/`.xls`/`.ppt` binary).
"""

# Appended only when the org has an ACL overlay (ledger/acl.json), so
# pre-ACL orgs re-emit byte-identical README files.
_README_VISIBILITY = """
## visibility.jsonl

One question per internal person: the exact set of share documents that
person may read, per the org's access-control ground truth (see
PERMISSIONS.md in the share root). Answers file:

```json
{"suite": "visibility",
  "answers": [
    {"id": "vq:0001", "docs": ["Firm/Firm Overview 2021 v3.docx"]}
  ]}
```

A question is correct when your doc set exactly matches `expected_docs`.
Score: `python -m orgsmith score --suite visibility --answers answers.json
--evals-dir <this directory>`.
"""

_README_SPLITS = """
## splits.json

Four nested corpus splits for a retrieval degradation curve. A split is the
set of documents your system searches; the answer key never changes, so
recall stays perfect while precision falls as the corpus grows.

- `core`: only the documents that answer some question.
- `distractors`: core plus real authored documents that are not answers.
- `noise`: core plus derived noise (duplicates and drafts of authored docs).
- `full`: the whole corpus (distractors and noise together).

Run your system against each split's document list, then grade with
`python -m orgsmith score --suite retrieval --split <name> --answers
answers.json --evals-dir <this directory>`. Ground-truth answers score 100%
on every split by construction, because every expected answer is in `core`,
which every split contains. That is the sanity check that the split machinery
did not drop an answer, not a claim about any system.
"""


def _attachment_map(manifest) -> dict[str, list[str]]:
    """{attached-source path: [transmittal email paths]} (M14). A transmittal
    email carries a rendered share document byte-identically, so wherever that
    document is an expected answer the transmittal is an equally valid source.
    Derived from the manifest, so pre-M14 orgs get an empty map."""
    out: dict[str, list[str]] = {}
    for e in manifest:
        ap = e.render_params.get("attach_path")
        if ap and e.authoring != "derived":
            out.setdefault(str(ap), []).append(e.path)
    return out


def build_retrieval(
    charter, foundation, engagements, manifest, mention_map
) -> list[RetrievalQuestion]:
    questions: list[tuple[str, list[str], list[str]]] = []

    attach_map = _attachment_map(manifest)

    def docs_with_fact(ref: str) -> list[str]:
        hosts = {e.path for e in manifest if ref in e.facts_refs}
        # M14: a transmittal email carries its source byte-identically, so it
        # is an equally valid place to find that source's facts.
        for src in list(hosts):
            hosts.update(attach_map.get(src, ()))
        return sorted(hosts)

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
        # M14: mundane internal mail names colleagues (a validated mention, for
        # the graph) but is distractor traffic, not a document ABOUT the
        # person. Excluding it from the mention retrieval answers keeps it a
        # genuine retrieval distractor rather than a core answer. (Visibility
        # still counts it: a readable doc is a visibility answer, exactly.)
        mundane_ids = {
            e.doc_id for e in manifest if e.genre == "internal_email"
        }
        for person in foundation.people:
            docs = sorted(
                {
                    by_path[r.doc_id]
                    for r in mention_map.mentions
                    if r.entity == person.id and r.doc_id not in mundane_ids
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
                        if r.entity == person.id
                        and r.surface == alias
                        and r.doc_id not in mundane_ids
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


_EXTRACTION_TEMPLATES = {
    "fee": "What is the fixed fee for the {title} engagement?",
    "start": "On what date did the {title} engagement start?",
    "client": "Which organization is the client of the {title} engagement?",
    "minutes-date": (
        "On what date was the working session for the {title} engagement "
        "held?"
    ),
}


def _difficulty_tags(entries) -> list[str]:
    """Where the expected docs live, when that makes extraction harder:
    a synthetic OCR layer, pixels only, or a pre-2007 binary. Derived from
    the manifest at emit time, so pre-M5 orgs (no scan flags, no legacy
    formats) gain no tags and re-emit byte-identically."""
    from ..schemas import BASE_FORMAT

    scanned = [e for e in entries if e.render_params.get("scan") == 1]
    tags = []
    if any(e.render_params.get("ocr_layer") == 1 for e in scanned):
        tags.append("scan:ocr")
    if any(not e.render_params.get("ocr_layer") for e in scanned):
        tags.append("scan:image-only")
    if any(e.format in BASE_FORMAT for e in entries):
        tags.append("format:legacy")
    return tags


def build_extraction(engagements, manifest) -> list[ExtractionQuestion]:
    """One question per planted, hosted fact. Hosts come from facts_refs
    (body facts) or key_facts (which also carry filename-only facts that
    never enter facts_refs); pre-key_facts manifests still work through
    facts_refs alone."""
    attach_map = _attachment_map(manifest)
    questions: list[ExtractionQuestion] = []
    serial = 0
    for eng in engagements.engagements:
        for fact in eng.facts:
            host_entries = [
                e
                for e in manifest
                if fact.id in e.facts_refs
                or any(k.fact_id == fact.id for k in e.key_facts)
            ]
            host_paths = {e.path for e in host_entries}
            # M14: a transmittal attaches its source byte-identically, so it
            # is an equally valid host for that source's facts.
            for src in list(host_paths):
                host_paths.update(attach_map.get(src, ()))
            hosts = sorted(host_paths)
            if not hosts:
                continue
            suffix = fact.id.rsplit(".", 1)[-1]
            template = _EXTRACTION_TEMPLATES.get(suffix)
            text = (
                template.format(title=eng.title)
                if template
                else f"What is the value of the planted fact {fact.id}?"
            )
            serial += 1
            questions.append(
                ExtractionQuestion(
                    id=f"xq:{serial:04d}",
                    fact_id=fact.id,
                    question=text,
                    expected_value=fact.rendered,
                    expected_docs=hosts,
                    location=fact.location_policy,
                    tags=[f"fact:{fact.kind}", eng.id]
                    + _difficulty_tags(host_entries),
                )
            )
    return questions


def build_visibility(foundation, acl) -> list[RetrievalQuestion]:
    """One doc-set question per internal person, roster order. Reuses the
    retrieval question shape so the answers contract stays uniform."""
    people = {p.id: p for p in foundation.people}
    return [
        RetrievalQuestion(
            id=f"vq:{i:04d}",
            question=(
                f"Which documents in the share may "
                f"{people[grant.person].name} read?"
            ),
            expected_docs=list(grant.docs),
            tags=["visibility", grant.person],
        )
        for i, grant in enumerate(acl.grants, start=1)
    ]


def _ambiguity_tags(foundation) -> dict[str, list[str]]:
    """entity id -> sorted ambiguity:<class> tags, derived from ledgers."""
    surnames: dict[str, list[str]] = {}
    for p in foundation.people:
        surnames.setdefault(p.name.split()[-1], []).append(p.id)
    collided = {
        pid for ids in surnames.values() if len(ids) > 1 for pid in ids
    }
    tags: dict[str, list[str]] = {}
    for p in foundation.people:
        mine = []
        if p.id in collided:
            mine.append("ambiguity:surname-collision")
        if p.aliases:
            mine.append("ambiguity:nickname-alias")
        if mine:
            tags[p.id] = sorted(mine)
    for xp in foundation.external_people:
        if len(xp.affiliations) > 1:
            tags[xp.id] = ["ambiguity:multi-affiliation"]
    return tags


def build_graph_expected(charter, foundation, graph) -> GraphExpected:
    ambiguity = _ambiguity_tags(foundation)
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
                tags=ambiguity.get(p.id, []),
            )
        )
    for org in foundation.external_orgs:
        entities.append(
            GraphEntityExpected(id=org.id, canonical=org.name, kind="org")
        )
    for xp in foundation.external_people:
        entities.append(
            GraphEntityExpected(
                id=xp.id,
                canonical=xp.name,
                aliases=[xp.email],
                kind="person",
                tags=ambiguity.get(xp.id, []),
            )
        )
    # Only entity-to-entity edges belong in the scoring contract:
    # participant edges point at engagement ids, which an external system
    # answering in entity names cannot express. They remain ground truth in
    # ledger/graph.json.
    scorable = [e for e in graph.edges if e.kind != "participant"]
    return GraphExpected(slug=charter.slug, entities=entities, edges=scorable)


def build_splits(manifest, questions, extraction, visibility) -> dict:
    """Nested corpus splits for a retrieval degradation curve (M12,
    external-validity-program). A split is the set of documents a system
    searches; the answer key is unchanged, so a system's recall stays perfect
    while precision falls as the corpus grows. Ground truth scores 100% on
    every split because every expected answer lives in `core`, which every
    split contains.

    Four distinct corpora, not one cumulative chain, so a consumer can
    attribute degradation to real distractors versus derived noise:
      core         answer-bearing documents only
      distractors  core + real authored documents that are not answers
      noise        core + derived noise (duplicates and drafts)
      full         the whole corpus (distractors and noise together)

    Derived, never stored: a pure function of the manifest and the suites."""
    authored = {e.path for e in manifest if e.authoring != "derived"}
    derived = {e.path for e in manifest if e.authoring == "derived"}
    all_paths = {e.path for e in manifest}
    answer_paths: set[str] = set()
    for q in questions:
        answer_paths.update(q.expected_docs)
    for q in extraction:
        answer_paths.update(q.expected_docs)
    for q in visibility:
        answer_paths.update(q.expected_docs)
    # A noise document can be ACL-grantable (it sits in the share), so the
    # visibility suite may name it. It is still never an answer for the split
    # curve: keep derived docs out of core so core/distractors carry only
    # authored docs and noise appears only in the noise/full splits.
    answer_paths -= derived
    return {
        "core": sorted(answer_paths),
        "distractors": sorted(answer_paths | authored),
        "noise": sorted(answer_paths | derived),
        "full": sorted(all_paths),
    }


def run_emit_evals(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "charter", "foundation", "fabric", "docplan")

    charter = load_charter(paths)
    foundation = load_foundation(paths)
    engagements = load_engagements(paths)
    graph = load_graph(paths)
    manifest = load_manifest(paths)
    mention_map = load_mention_map(paths)

    # Derived noise documents (M12) are never ground-truth answers: they carry
    # no facts or mentions of their own and a retrieval system should not be
    # rewarded for returning a draft. The suites answer over authored docs
    # only; the noise files are the corpus the +noise split adds around them.
    answer_manifest = [e for e in manifest if e.authoring != "derived"]

    questions = build_retrieval(
        charter, foundation, engagements, answer_manifest, mention_map
    )
    extraction = build_extraction(engagements, answer_manifest)
    expected = build_graph_expected(charter, foundation, graph)
    acl = load_acl(paths)

    paths.evals_dir.mkdir(parents=True, exist_ok=True)

    def write_jsonl(name: str, items) -> None:
        lines = [
            json.dumps(q.model_dump(mode="json"), ensure_ascii=False)
            for q in items
        ]
        (paths.evals_dir / name).write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    write_jsonl("retrieval.jsonl", questions)
    write_jsonl("extraction.jsonl", extraction)
    write_model(paths.evals_dir / "graph_expected.json", expected)

    readme = _README.format(slug=charter.slug)
    new_tags = ("scan:ocr", "scan:image-only", "format:legacy")
    if any(t in q.tags for q in extraction for t in new_tags):
        readme += _README_FORMAT_TAGS
    visibility_note = ""
    visibility = []
    if acl is not None:
        visibility = build_visibility(foundation, acl)
        write_jsonl("visibility.jsonl", visibility)
        readme += _README_VISIBILITY
        visibility_note = f", {len(visibility)} visibility questions"
    else:
        print(
            "emit-evals: visibility suite skipped (no ledger/acl.json; "
            f"run `python -m orgsmith acl {charter.slug}`)"
        )

    splits = build_splits(manifest, questions, extraction, visibility)
    (paths.evals_dir / "splits.json").write_text(
        json.dumps(
            {"slug": charter.slug, "splits": splits}, indent=2, ensure_ascii=False
        )
        + "\n",
        encoding="utf-8",
    )
    readme += _README_SPLITS
    (paths.evals_dir / "README.md").write_text(readme, encoding="utf-8")
    print(
        f"emit-evals: {len(questions)} retrieval questions, "
        f"{len(extraction)} extraction questions, "
        f"{len(expected.entities)} graph entities"
        f"{visibility_note} -> {paths.evals_dir}"
    )
    return 0
