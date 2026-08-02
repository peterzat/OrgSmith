# Golden eval suites for `northgate-staffing`

Emitted by `python -m orgsmith emit-evals northgate-staffing`. Deterministic: derived
entirely from this org's ground-truth ledgers. You do not need OrgSmith
source (or any model) to be graded; everything required is in this
directory.

## retrieval.jsonl

One question per line: `id`, `question`, `expected_docs` (share-relative
paths), `tags`. Run your retrieval system over the `companies/northgate-staffing/`
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

The visibility suite is graded over the whole share by nature: the question
is which documents a person may read, which every document in the corpus
answers one way or the other. It therefore contributes no documents to
`core` and is not gradable on `core` or `distractors`. Grade it on `full`.
