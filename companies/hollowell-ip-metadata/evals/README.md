# Golden eval suites for `hollowell-ip`

Emitted by `python -m orgsmith emit-evals hollowell-ip`. Deterministic: derived
entirely from this org's ground-truth ledgers. You do not need OrgSmith
source (or any model) to be graded; everything required is in this
directory.

## retrieval.jsonl

One question per line: `id`, `question`, `expected_docs` (share-relative
paths), `tags`. Run your retrieval system over the `companies/hollowell-ip/`
share and write an answers file:

```json
{"suite": "retrieval",
  "answers": [
    {"id": "q:0001", "docs": ["Engagements/Client X/some-file.pdf"]}
  ]}
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
{"suite": "extraction",
  "answers": [
    {"id": "xq:0001", "value": "$105,000",
      "docs": ["Engagements/Client X/some-file.pdf"]}
  ]}
```

A question is correct when `value` equals `expected_value` exactly
(surrounding whitespace ignored) and `docs` exactly matches
`expected_docs`. Score: `python -m orgsmith score --suite extraction
--answers answers.json --evals-dir <this directory>`.

## graph_expected.json

Canonical entities (with `aliases`: any alias earns full credit) and typed
edges. Answers file:

```json
{"suite": "graph",
  "entities": [{"name": "Jane Q. Example", "kind": "person"}],
  "edges": [{"src": "Jane Q. Example", "dst": "Example Corp",
             "kind": "works_at"}]}
```

Entity names are matched case-insensitively against canonical names and
aliases. Edges are scored precision/recall after resolving names the same
way. Entities may carry `ambiguity:<class>` tags (surname-collision,
nickname-alias, multi-affiliation); the scorer reports per-class recall
alongside the overall score when tags are present.

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
