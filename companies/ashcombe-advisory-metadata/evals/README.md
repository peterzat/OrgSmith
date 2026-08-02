# Golden eval suites for `ashcombe-advisory`

Emitted by `python -m orgsmith emit-evals ashcombe-advisory`. Deterministic: derived
entirely from this org's ground-truth ledgers and the rendered share. You do
not need OrgSmith source (or any model) to be graded; everything required is
in this directory.

**Relevance-label policy version 1.0.** What counts as a
required, acceptable, or never-acceptable document is a versioned contract:
see `docs/LABEL-POLICY.md` in the OrgSmith repository for the scan
semantics, the cluster canonicalization rule, and the stated limitations.

## retrieval.jsonl

One question per line: `id`, `question`, `expected_docs` (share-relative
paths), `acceptable_docs`, `tags`. Run your retrieval system over the
`companies/ashcombe-advisory/` share and write an answers file:

```json
{"suite": "retrieval",
  "answers": [
    {"id": "q:0001", "docs": ["Engagements/Client X/some-file.pdf"]}
  ]}
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
edges. Entity kinds are `person`, `org`, and `engagement`. Answers file:

```json
{"suite": "graph",
  "entities": [{"name": "Jane Q. Example", "kind": "person"}],
  "edges": [{"src": "Jane Q. Example", "dst": "Example Corp",
             "kind": "works_at"},
            {"src": "Jane Q. Example", "dst": "CFO Search",
             "kind": "participant",
             "start": "2015-08-27", "end": "2015-12-04"}]}
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
