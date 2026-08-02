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
from ..doctext import mask_surfaces
from ..paths import OrgPaths
from ..schemas import (
    AliasSighting,
    EvalCluster,
    EvalClusterMember,
    EvalClusters,
    EvalDiagnostics,
    ExtractionQuestion,
    GraphEntityExpected,
    GraphExpected,
    IncidentalMentions,
    RetrievalQuestion,
    ValueCollision,
    dump_json,
    surface_in_text,
)
from ..state import load_state, require_stages

# The versioned relevance-label contract these suites follow. Bump it in
# lockstep with docs/LABEL-POLICY.md whenever the meaning of required,
# acceptable, or never-acceptable changes, so a consumer holding only an
# `evals/` directory can tell which rules produced it.
LABEL_POLICY_VERSION = "1.0"

_README = """\
# Golden eval suites for `{slug}`

Emitted by `python -m orgsmith emit-evals {slug}`. Deterministic: derived
entirely from this org's ground-truth ledgers and the rendered share. You do
not need OrgSmith source (or any model) to be graded; everything required is
in this directory.

**Relevance-label policy version {policy_version}.** What counts as a
required, acceptable, or never-acceptable document is a versioned contract:
see `docs/LABEL-POLICY.md` in the OrgSmith repository for the scan
semantics, the cluster canonicalization rule, and the stated limitations.

## retrieval.jsonl

One question per line: `id`, `question`, `expected_docs` (share-relative
paths), `acceptable_docs`, `tags`. Run your retrieval system over the
`companies/{slug}/` share and write an answers file:

```json
{{"suite": "retrieval",
  "answers": [
    {{"id": "q:0001", "docs": ["Engagements/Client X/some-file.pdf"]}}
  ]}}
```

A question is correct when your doc set matches `expected_docs` exactly,
after two relaxations that can only ever help you:

- Documents listed in `acceptable_docs` are dropped from your answer before
  the comparison. These are documents whose rendered text visibly carries
  the same evidence (a colleague named in passing in a memo the plan never
  counted) but which the answer key does not require. Returning one costs
  nothing; missing one costs nothing either, because recall is measured
  against `expected_docs` alone.
- Documents that carry byte-identical evidence are canonicalized first (see
  `clusters.json`), so returning a duplicate in place of its original is
  correct.

Score: `python -m orgsmith score --suite retrieval --answers answers.json
--evals-dir <this directory>`.

### Unanswerable questions

A question with `"answerable": false` has no answer in this corpus: the
person it asks about is documented nowhere the suite counts. Its
`expected_docs` is empty and the correct response is to **abstain**, either
by omitting the question from your answers file or by returning an empty
list. Returning only `acceptable_docs` is also correct. Inventing an answer
fails with `expected abstention`.

These exist because dropping them would teach a benchmark that everything
asked has an answer, which is the opposite of what a retrieval system needs
to learn.

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
edges. Entity kinds are `person`, `org`, and `engagement`. Answers file:

```json
{{"suite": "graph",
  "entities": [{{"name": "Jane Q. Example", "kind": "person"}}],
  "edges": [{{"src": "Jane Q. Example", "dst": "Example Corp",
             "kind": "works_at"}},
            {{"src": "Jane Q. Example", "dst": "CFO Search",
             "kind": "participant",
             "start": "2015-08-27", "end": "2015-12-04"}}]}}
```

Entity names are matched case-insensitively against canonical names and
aliases. Edges are scored precision/recall after resolving names the same
way, with a per-kind recall breakdown so "who worked on what"
(`participant`) is visible separately from the org chart (`reports_to`).

`start` and `end` are optional. Omitting them scores exactly the same edge
precision and recall; supplying them earns a separate `dated_edge_credit`,
the share of your correct edges whose ground truth carries dates that you
dated correctly. An answer file with no dates at all reports no credit
rather than a zero, because not attempting is not the same as being wrong.

Entities may carry `ambiguity:<class>` tags (surname-collision,
nickname-alias, multi-affiliation); the scorer reports per-class recall
alongside the overall score when tags are present.
"""

# Appended only when the org holds equivalence clusters (an org with no
# derived byte-copies and no transmittal mail emits an empty clusters.json
# and no section).
_README_CLUSTERS = """
## clusters.json

Equivalence classes: documents that carry byte-identical evidence to a
`canonical` document. Two membership bases, both verified when the suites
were emitted rather than taken from a label:

- `byte_copy`: a derived noise file (an exact duplicate, or a copy misfiled
  into the wrong folder) whose rendered bytes hash equal to the canonical's.
- `attachment`: a transmittal email carrying the canonical document as a
  byte-identical MIME attachment.

**Scoring canonicalizes through this file.** Returning a member in place of,
or beside, its canonical is correct on retrieval and extraction: the member
literally contains the answer, so scoring it as an error would punish a
system for being right. Members occupy no rank of their own and earn no
extra credit.

Near-duplicates are deliberately **not** members: a draft, a version-chain
member, and a stale template all resemble their source without matching it,
and telling them apart is a capability under test. They stay ordinary
distractors.

An `evals/` directory with no `clusters.json` scores exactly as it did
before clusters existed: canonicalization falls back to identity.
"""

# Always emitted; the section is appended only when the scan actually saw
# something, so a clean org's README stays quiet about it.
_README_DIAGNOSTICS = """
## diagnostics.json

What a corpus-wide scan of the rendered text saw that the answer key does
**not** claim. Nothing here is ground truth, nothing here is scored, and
nothing here gates:

- `value_collisions`: an extraction question's expected surface found in
  another engagement's paperwork. Recorded so you can see it; returning it
  is still a wrong answer, because the question asks where *that*
  engagement's value lives.
- `unplanned_alias_sightings`: a registered nickname standing on its own in
  a document that plans no mention of it. Usually this means the structured
  ledger and the prose disagree about who the nickname belongs to.
- `incidental_mentions`: how far each mention question's rendered truth ran
  past the plan (how many documents the plan placed, how many more the scan
  found and made acceptable).

These are published rather than fixed because they are honest properties of
this corpus. Read them before treating a scoring loss as your system's bug.
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

Splits are a **retrieval and extraction** device.
"""

# Appended after the splits section only when the org emits a visibility
# suite, so an org without an ACL overlay never mentions one.
_README_SPLITS_VISIBILITY = """
The visibility suite is graded over the whole share by nature: the question
is which documents a person may read, which every document in the corpus
answers one way or the other. It therefore contributes no documents to
`core` and is not gradable on `core` or `distractors`. Grade it on `full`.
"""


# Derived kinds whose rendered bytes can equal their source's. Membership is
# still decided by hashing (a `misfile` of a doc whose renderer stamps a path
# would not hash equal, and must not be claimed as one); this set only says
# which kinds are worth hashing. Drafts, version-chain members, and stale
# templates are excluded by doctrine, not by hash: telling a near-duplicate
# from its final is a capability under test, so they may never be acceptable.
_BYTE_COPY_KINDS = ("exact_duplicate", "misfile")


def build_clusters(paths: OrgPaths, manifest) -> EvalClusters:
    """Equivalence classes of documents carrying byte-identical evidence.

    Two membership bases, both verified at emit time rather than trusted:

      byte_copy   a derived noise doc whose rendered file hashes equal to
                  its manifest source's. The `noise_kind` label picks the
                  candidates; the hash decides.
      attachment  a transmittal email carrying a share document as a
                  byte-identical MIME part (the M14 map, which used to be
                  unioned into gold and is an equivalence class instead).

    Membership is transitive through the canonical: a duplicate of a
    transmittal resolves to the document the transmittal carries. A member
    whose file (or whose source's file) is missing is silently no member,
    because there are no bytes to compare; MAN-01 and FILE-01 own that
    failure, and a missing file can only ever make scoring stricter."""
    from ..state import sha256_file

    by_id = {e.doc_id: e for e in manifest}
    digests: dict[str, str] = {}

    def digest(path: str) -> str | None:
        if path not in digests:
            f = paths.share_dir / path
            digests[path] = sha256_file(f) if f.is_file() else ""
        return digests[path] or None

    # member path -> (canonical path, basis, noise_kind), before transitive
    # resolution to a root canonical.
    parent: dict[str, tuple[str, str, str]] = {}

    for e in manifest:
        if e.authoring == "derived" and e.noise_kind in _BYTE_COPY_KINDS:
            source = by_id.get(e.noise_of or "")
            if source is None:
                continue
            mine, theirs = digest(e.path), digest(source.path)
            if mine is not None and mine == theirs:
                parent[e.path] = (source.path, "byte_copy", e.noise_kind)
        attach = e.render_params.get("attach_path")
        if attach and e.authoring != "derived":
            carried = str(attach)
            if _carries_bytes(paths, e.path, carried):
                parent[e.path] = (carried, "attachment", "")

    def root(path: str) -> str:
        seen = {path}
        while path in parent:
            path = parent[path][0]
            if path in seen:  # a cycle cannot happen; never loop if it does
                break
            seen.add(path)
        return path

    grouped: dict[str, list[EvalClusterMember]] = {}
    for member, (_canonical, basis, kind) in parent.items():
        grouped.setdefault(root(member), []).append(
            EvalClusterMember(path=member, basis=basis, noise_kind=kind)
        )
    clusters = [
        EvalCluster(
            canonical=canonical,
            members=sorted(members, key=lambda m: m.path),
        )
        for canonical, members in sorted(grouped.items())
    ]
    return EvalClusters(
        slug=paths.slug,
        policy_version=LABEL_POLICY_VERSION,
        clusters=clusters,
    )


def _carries_bytes(paths: OrgPaths, eml_path: str, carried: str) -> bool:
    """Whether a transmittal's MIME attachment is byte-identical to the share
    document it claims to carry. EML-03 fails the org when it is not; here a
    mismatch simply means no equivalence, so a broken attachment can never
    relax scoring."""
    from ..render.eml import eml_attachment_bytes

    message = paths.share_dir / eml_path
    source = paths.share_dir / carried
    if not message.is_file() or not source.is_file():
        return False
    return eml_attachment_bytes(message) == source.read_bytes()


def scan_corpus(paths: OrgPaths, manifest, engagements, foundation) -> dict:
    """{share-relative path: extractable text} for every entry, read through
    the one shared reader (orgsmith/doctext.py) so the answer key and the
    validator agree on what a document says. One extraction per document."""
    from ..doctext import DocText

    reader = DocText(paths, engagements, foundation)
    texts = {}
    for entry in manifest:
        if (paths.share_dir / entry.path).is_file():
            texts[entry.path] = reader.text(entry)
    return texts


def build_retrieval(
    charter, foundation, engagements, manifest, mention_map, texts=None
) -> list[RetrievalQuestion]:
    """The retrieval suite. `texts` is the rendered-text scan (scan_corpus);
    without it the suites carry no acceptable sets, which is strictly
    stricter scoring, never looser."""
    texts = texts or {}
    questions: list[tuple[str, list[str], list[str], list[str], bool]] = []

    def ask(text: str, docs, tags, acceptable=(), answerable=True) -> None:
        questions.append(
            (text, list(docs), list(tags), sorted(acceptable), answerable)
        )

    def docs_with_fact(ref: str) -> list[str]:
        # M17: a transmittal email carrying this document byte-identically is
        # NOT unioned into the required set any more. It is an equivalence
        # member instead (clusters.json), so returning either satisfies the
        # question while the required set stays the canonical answer.
        return sorted({e.path for e in manifest if ref in e.facts_refs})

    for eng in engagements.engagements:
        ask(
            f"Which documents state the fixed fee for the {eng.title} "
            f"engagement?",
            docs_with_fact(f"f:{eng.id}.fee"),
            ["fact:money", eng.id],
        )
        ask(
            f"Which documents state the start date of the {eng.title} "
            f"engagement?",
            docs_with_fact(f"f:{eng.id}.start"),
            ["fact:date", eng.id],
        )
        ask(
            f"Which documents identify the client organization of the "
            f"{eng.title} engagement?",
            docs_with_fact(f"f:{eng.id}.client"),
            ["fact:text", eng.id],
        )

    for entry in manifest:
        if entry.genre == "financial_summary":
            year = entry.render_params["year"]
            ask(
                f"Which document is the FY{year} financial summary?",
                [entry.path],
                ["workbook"],
            )
    overview_docs = sorted(
        e.path for e in manifest if e.genre == "company_overview"
    )
    if overview_docs:
        ask(
            f"Which document gives an overview of {charter.name}?",
            overview_docs,
            ["firm"],
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
        # Planned surfaces per document, for masking before an alias scan.
        planned = {}
        for record in mention_map.mentions:
            planned.setdefault(by_path.get(record.doc_id), {}).setdefault(
                record.entity, set()
            ).add(record.surface)

        def scan_hits(surface: str, required, owner: str | None = None):
            """Documents whose rendered text carries `surface` as a standalone
            token run, beyond the ones the plan placed. When `owner` is given
            the scan is an alias scan, so every other entity's planned
            surfaces are masked first: a short alias must not be credited to
            a longer planned name that contains it."""
            hits = set()
            for path, text in texts.items():
                if path in required:
                    continue
                if owner is not None:
                    others = {
                        s
                        for entity, surfaces in planned.get(path, {}).items()
                        if entity != owner
                        for s in surfaces
                    }
                    text = mask_surfaces(text, others)
                if surface_in_text(surface, text):
                    hits.add(path)
            return hits

        for person in foundation.people:
            docs = sorted(
                {
                    by_path[r.doc_id]
                    for r in mention_map.mentions
                    if r.entity == person.id and r.doc_id not in mundane_ids
                }
            )
            # Emitted even when the plan placed nothing. A roster member who
            # is named only in mundane internal mail (or nowhere at all) is
            # a real question with no answer, and dropping it taught the
            # suite that everything asked is answerable. Her mundane mail
            # becomes the acceptable set, so returning it is not an error
            # either.
            ask(
                f"Which documents mention {person.name}?",
                docs,
                ["mention:person", person.id],
                scan_hits(person.name, set(docs)),
                answerable=bool(docs),
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
                    ask(
                        f"Which documents refer to someone as “{alias}”?",
                        alias_docs,
                        ["mention:alias", person.id],
                        scan_hits(alias, set(alias_docs), owner=person.id),
                    )

    return [
        RetrievalQuestion(
            id=f"q:{i:04d}",
            question=text,
            expected_docs=docs,
            acceptable_docs=acceptable,
            answerable=answerable,
            tags=tags,
        )
        for i, (text, docs, tags, acceptable, answerable) in enumerate(
            [q for q in questions if q[1] or not q[4]], start=1
        )
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
            # M17: a transmittal attaching this document is an equivalence
            # member (clusters.json), not a unioned host. See docs_with_fact.
            hosts = sorted({e.path for e in host_entries})
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


def build_graph_expected(
    charter, foundation, graph, engagements=None
) -> GraphExpected:
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
    # M17: engagements join the contract. Participant edges used to be
    # stripped here because they point at engagement ids an answer file had
    # no way to name, which silently dropped "who worked on what" from the
    # scored graph. Naming the engagement makes them expressible.
    if engagements is not None:
        titles: dict[str, int] = {}
        for eng in engagements.engagements:
            titles[eng.title] = titles.get(eng.title, 0) + 1
        clients = {org.id: org.name for org in foundation.external_orgs}
        for eng in engagements.engagements:
            # Two engagements can share a title (the same service sold
            # twice); disambiguate by client so a canonical name is unique.
            canonical = eng.title
            aliases = [eng.id]
            if titles[eng.title] > 1:
                client = clients.get(eng.client, eng.client)
                canonical = f"{eng.title} ({client})"
                aliases.append(eng.title)
            entities.append(
                GraphEntityExpected(
                    id=eng.id,
                    canonical=canonical,
                    aliases=aliases,
                    kind="engagement",
                )
            )
        return GraphExpected(
            slug=charter.slug, entities=entities, edges=list(graph.edges)
        )

    scorable = [e for e in graph.edges if e.kind != "participant"]
    return GraphExpected(slug=charter.slug, entities=entities, edges=scorable)


def build_diagnostics(
    paths, manifest, foundation, mention_map, questions, extraction,
    clusters, texts,
) -> EvalDiagnostics:
    """What the corpus-wide scan saw that the answer key does not claim.

    Three records, none of them gold and none of them gating:

    - **Value collisions.** Every extraction question's expected surface is
      scanned corpus-wide. A hit in another engagement's paperwork (or in
      firm-level prose) is recorded, never promoted: returning it stays a
      wrong answer, because the question asks where that engagement's value
      lives. Hits inside the fact's own engagement are ordinary repetition
      and are not recorded. Hits inside a derived near-duplicate of a
      required host are explained by lineage and counted, not listed: a
      draft holds its source's fee because it was copied from it.
    - **Unplanned alias sightings.** A registered alias standing on its own
      in a document that plans no mention of it. This is the mechanical form
      of the exemplar's `Jim` residual.
    - **Incidental mentions.** How far each mention question's rendered
      truth ran past its plan.
    """
    by_path = {e.path: e for e in manifest}
    doc_paths = {e.doc_id: e.path for e in manifest}
    equivalents: dict[str, set[str]] = {}
    for cluster in clusters.clusters:
        equivalents[cluster.canonical] = {m.path for m in cluster.members}
    derived_source = {
        e.path: doc_paths.get(e.noise_of or "", "")
        for e in manifest
        if e.authoring == "derived"
    }

    collisions: list[ValueCollision] = []
    lineage_hits = 0
    for question in extraction:
        required = set(question.expected_docs)
        allowed = set(required)
        for path in required:
            allowed |= equivalents.get(path, set())
        engagements_of_fact = {
            by_path[p].engagement for p in required if p in by_path
        }
        flagged: list[str] = []
        for path, text in texts.items():
            if path in allowed or not surface_in_text(question.expected_value, text):
                continue
            entry = by_path.get(path)
            if entry is not None and entry.engagement in engagements_of_fact:
                continue  # the fact's own engagement repeating its own value
            if derived_source.get(path, "") in allowed:
                lineage_hits += 1
                continue
            flagged.append(path)
        if flagged:
            collisions.append(
                ValueCollision(
                    question=question.id,
                    fact_id=question.fact_id,
                    value=question.expected_value,
                    paths=sorted(flagged),
                )
            )

    planned: dict[str, dict[str, set[str]]] = {}
    if mention_map is not None:
        for record in mention_map.mentions:
            path = doc_paths.get(record.doc_id)
            planned.setdefault(path, {}).setdefault(record.entity, set()).add(
                record.surface
            )

    sightings: list[AliasSighting] = []
    people = list(foundation.people) + list(foundation.external_people)
    for person in people:
        for alias in getattr(person, "aliases", []):
            for path, text in sorted(texts.items()):
                here = planned.get(path, {})
                if alias in here.get(person.id, set()):
                    continue  # planned: this document may say it
                masked = mask_surfaces(
                    text,
                    {
                        s
                        for entity, surfaces in here.items()
                        if entity != person.id
                        for s in surfaces
                    },
                )
                if surface_in_text(alias, masked):
                    sightings.append(
                        AliasSighting(
                            alias=alias,
                            owner=person.id,
                            path=path,
                            lineage=derived_source.get(path, ""),
                        )
                    )

    incidental = [
        IncidentalMentions(
            question=q.id,
            entity=q.tags[1],
            surface=q.question.split("“")[1].rstrip("”?")
            if "“" in q.question
            else q.question[len("Which documents mention ") :].rstrip("?"),
            planned=len(q.expected_docs),
            incidental=len(q.acceptable_docs),
        )
        for q in questions
        if q.acceptable_docs
        and any(t.startswith("mention:") for t in q.tags)
    ]

    return EvalDiagnostics(
        slug=paths.slug,
        policy_version=LABEL_POLICY_VERSION,
        value_collisions=collisions,
        unplanned_alias_sightings=sightings,
        incidental_mentions=incidental,
        lineage_explained_value_hits=lineage_hits,
    )


def build_splits(manifest, questions, extraction) -> dict:
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

    M17: splits are a retrieval and extraction device only. They used to
    union the visibility suite's gold into `core` as well, and because
    ACL-02 guarantees every document is readable by someone, that made
    `core` the whole authored corpus on every org in the fleet: the
    advertised four-point curve was a two-point one everywhere. Visibility
    is graded over the full share by nature (the question is "what may this
    person read?", which every document answers one way or the other), so
    it no longer contributes answers here and is not gradable on the
    core/distractors splits. See docs/EVAL-SPLITS.md.

    Derived, never stored: a pure function of the manifest and the suites."""
    authored = {e.path for e in manifest if e.authoring != "derived"}
    derived = {e.path for e in manifest if e.authoring == "derived"}
    all_paths = {e.path for e in manifest}
    answer_paths: set[str] = set()
    for q in questions:
        answer_paths.update(q.expected_docs)
    for q in extraction:
        answer_paths.update(q.expected_docs)
    # Derived docs are never answers for the split curve: keep them out of
    # core so core/distractors carry only authored docs and noise appears
    # only in the noise/full splits.
    answer_paths -= derived
    return {
        "core": sorted(answer_paths),
        "distractors": sorted(answer_paths | authored),
        "noise": sorted(answer_paths | derived),
        "full": sorted(all_paths),
    }


def derive_evals(paths: OrgPaths, texts=None) -> dict[str, str]:
    """Every file `emit-evals` would write, as {filename: text}. Pure: it
    reads committed state and writes nothing.

    Split out from the writer so the EVAL-01 validator can re-derive the
    suites and compare them to what is committed. `texts` accepts a
    pre-computed rendered-text scan (the validator already holds one), so
    re-deriving during validation costs no second extraction pass."""
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

    # One extraction pass over the whole rendered corpus, shared by the
    # acceptable-set scan and the diagnostics scan.
    if texts is None:
        texts = scan_corpus(paths, manifest, engagements, foundation)
    clusters = build_clusters(paths, manifest)
    cluster_members = {
        m.path for c in clusters.clusters for m in c.members
    }
    # Acceptable sets are scanned over authored documents that are not
    # equivalence members. A derived near-duplicate holding the surface is a
    # distractor by doctrine; a cluster member is canonicalized rather than
    # dropped, and letting it be both would make "return the copy instead of
    # the original" score empty. See docs/LABEL-POLICY.md.
    authored_texts = {
        e.path: texts[e.path]
        for e in answer_manifest
        if e.path in texts and e.path not in cluster_members
    }

    questions = build_retrieval(
        charter,
        foundation,
        engagements,
        answer_manifest,
        mention_map,
        authored_texts,
    )
    extraction = build_extraction(engagements, answer_manifest)
    expected = build_graph_expected(charter, foundation, graph, engagements)
    acl = load_acl(paths)

    files: dict[str, str] = {}

    def jsonl(items) -> str:
        return (
            "\n".join(
                json.dumps(q.model_dump(mode="json"), ensure_ascii=False)
                for q in items
            )
            + "\n"
        )

    files["retrieval.jsonl"] = jsonl(questions)
    files["extraction.jsonl"] = jsonl(extraction)
    files["graph_expected.json"] = dump_json(expected)
    files["clusters.json"] = dump_json(clusters)
    diagnostics = build_diagnostics(
        paths,
        manifest,
        foundation,
        mention_map,
        questions,
        extraction,
        clusters,
        texts,
    )
    files["diagnostics.json"] = dump_json(diagnostics)

    readme = _README.format(
        slug=charter.slug, policy_version=LABEL_POLICY_VERSION
    )
    if clusters.clusters:
        readme += _README_CLUSTERS
    if (
        diagnostics.value_collisions
        or diagnostics.unplanned_alias_sightings
        or diagnostics.incidental_mentions
    ):
        readme += _README_DIAGNOSTICS
    new_tags = ("scan:ocr", "scan:image-only", "format:legacy")
    if any(t in q.tags for q in extraction for t in new_tags):
        readme += _README_FORMAT_TAGS
    visibility = []
    if acl is not None:
        visibility = build_visibility(foundation, acl)
        files["visibility.jsonl"] = jsonl(visibility)
        readme += _README_VISIBILITY

    splits = build_splits(manifest, questions, extraction)
    files["splits.json"] = (
        json.dumps(
            {"slug": charter.slug, "splits": splits},
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    readme += _README_SPLITS
    if visibility:
        readme += _README_SPLITS_VISIBILITY
    files["README.md"] = readme
    return files


def run_emit_evals(paths: OrgPaths) -> int:
    state = load_state(paths)
    # M17: render is a prerequisite. The answer key is now derived partly
    # from what the rendered files actually contain (byte-identity for the
    # equivalence clusters), not only from what the plan says they should,
    # so the share has to exist before the suites can be honest about it.
    require_stages(
        state, "charter", "foundation", "fabric", "docplan", "render"
    )

    files = derive_evals(paths)
    paths.evals_dir.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (paths.evals_dir / name).write_text(text, encoding="utf-8")

    counts = {
        name: sum(1 for line in files[name].splitlines() if line.strip())
        for name in ("retrieval.jsonl", "extraction.jsonl")
    }
    entities = len(json.loads(files["graph_expected.json"])["entities"])
    if "visibility.jsonl" not in files:
        print(
            "emit-evals: visibility suite skipped (no ledger/acl.json; "
            f"run `python -m orgsmith acl {paths.slug}`)"
        )
        visibility_note = ""
    else:
        visibility_note = (
            f", {sum(1 for line in files['visibility.jsonl'].splitlines() if line.strip())}"
            " visibility questions"
        )
    print(
        f"emit-evals: {counts['retrieval.jsonl']} retrieval questions, "
        f"{counts['extraction.jsonl']} extraction questions, "
        f"{entities} graph entities"
        f"{visibility_note} -> {paths.evals_dir}"
    )
    return 0
