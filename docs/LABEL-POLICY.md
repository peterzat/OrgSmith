# Relevance-label policy

**Version 1.0.** Every emitted `evals/README.md` cites the version it was
produced under, and so do `clusters.json` and `diagnostics.json`. Bump the
version whenever the meaning of required, acceptable, or never-acceptable
changes; the constant lives at `LABEL_POLICY_VERSION` in
`orgsmith/evals/emit.py`.

This document says what it means for a document to be a right answer. It
exists because the answer key used to derive relevance from what the
generator *planned* to plant, and a corpus can only be a benchmark if the
key describes what the rendered documents actually contain.

## Three labels

**Required** (`expected_docs`). The canonical answer set, from planned fact
placements and planned mentions. Recall is measured against required and
nothing else, so nothing below can ever lower a system's recall.

**Acceptable** (`acceptable_docs`). Documents whose rendered text visibly
carries the same evidence, which the plan did not place. Returning one is
never penalized; missing one costs nothing. They are dropped from an answer
before it is compared to the required set.

**Irrelevant.** Everything else. Returning one counts against precision, as
it should.

Byte-identical evidence is handled separately, by canonicalization rather
than by acceptance: see *Equivalence clusters* below.

## How acceptable documents are derived

Only mention and alias questions carry them, and only from a scan of
rendered text.

- The scan runs over **extractable text** as the shared reader
  (`orgsmith/doctext.py`) produces it: the same text the validator holds
  documents to. For an `.eml` that includes the `To`/`Cc` display names,
  because a recipient's name legitimately lives in the transport headers.
  For an image-only scan it is the archived true page text.
- A hit is a **word-boundary** match (`surface_in_text`), so `Jen` does not
  match inside `Jennifer` and a possessive or a trailing comma still
  matches.
- For a **person** question the scanned surface is the canonical full name.
  For an **alias** question it is the exact alias token, and every *other*
  entity's planned surfaces in that document are masked out first, so an
  alias standing inside a longer planned name is credited to the longer
  name.
- The scan runs over **authored documents that are not equivalence
  members**. A derived document is never acceptable (below), and a cluster
  member is canonicalized rather than dropped, so listing it as acceptable
  as well would make "return the copy instead of the original" score as an
  empty answer.
- Documents already required for that question are excluded, so the two
  sets never overlap.

Mundane internal email stays out of the **required** mention gold, because
it is distractor traffic rather than a document about the person. It can
still become acceptable, which is the point: it visibly names them.

## Equivalence clusters

`clusters.json` groups documents that carry byte-identical evidence to a
canonical document. Scoring maps the returned set through it: a member
*satisfies* a requirement for its canonical, so returning a copy in place
of its original, or beside it, is correct.

The required set is never rewritten. Membership is directional (a
transmittal carries the memo's bytes; the memo does not carry the
transmittal's covering note), so a document that is required in its own
right has to be returned in its own right. Where a transmittal states a
fact itself, it and the document it carries are two required documents, and
returning only one of them is a miss.

Two membership bases, both **verified at emit time, never taken from a
label**:

- `byte_copy`: a derived noise file (`exact_duplicate` or `misfile`) whose
  rendered file hashes equal to its manifest source's.
- `attachment`: a transmittal email carrying the canonical document as a
  byte-identical MIME part.

Membership is transitive through the canonical, so a duplicate of a
transmittal resolves to the document the transmittal carries.

Canonicalization runs **before** acceptable documents are dropped, and a
cluster member is never also listed as acceptable. Keeping the two
mechanisms disjoint is what makes "return the duplicate instead of the
original" correct rather than empty.

An `evals/` directory with no `clusters.json` canonicalizes by identity, so
a directory emitted before clusters existed scores exactly as it did.

## Never acceptable

**Near-duplicates.** A `draft`, a `version` chain member, and a
`stale_template` all resemble their source without matching it.
Distinguishing them is a capability under test, so they stay ordinary
distractors even when they contain the surface. This is doctrine, not an
artifact of the hash: a near-duplicate that happened to hash equal would
still not qualify, because its kind excludes it from the candidate set.

**Value collisions.** A document holding an extraction question's expected
surface, in another engagement's paperwork, is a wrong answer. The question
asks where *that* engagement's value lives, and a coincidence of surface is
exactly the failure an extractor should not be rewarded for. Collisions are
recorded in `diagnostics.json` so they are visible rather than mysterious.

**Anything a scan found for an extraction question.** Extraction has no
acceptance path at all. Its `expected_docs` are the planted hosts, and a
scan hit outside them is either a value collision (recorded, still wrong) or
lineage from a derived copy (counted, still not an answer). `acceptable_docs`
therefore exists on retrieval questions only.

## Fact-value consistency

Every extraction question's `expected_value` is scanned corpus-wide when the
suites are emitted. Hits are classified:

- inside the fact's own engagement: ordinary repetition, not recorded;
- inside a required host or an equivalence member of one: the answer itself;
- inside a derived near-duplicate of a required host: explained by lineage
  and counted in `lineage_explained_value_hits`, not listed, because a draft
  holds its source's fee for a reason that is not a defect;
- anywhere else: recorded as a value collision.

Nothing found by this scan is ever added to gold, and nothing found by it
ever makes a wrong answer right.

## Stated limitations

These are real misses, documented rather than hidden. Each one can only make
scoring *stricter* than the rendered truth, never looser, because acceptable
sets exist to relax scoring and a missed hit simply does not relax it.

- **OCR-corrupted incidental names.** A degraded scan's synthetic OCR layer
  corrupts text outside the planted surfaces. A name incidentally mentioned
  in such a document may not survive the corruption, so the scan will not
  see it.
- **Surname-only and first-name-only references.** The scan looks for the
  canonical full name or a registered alias. "Fuentes said so" is a real
  reference to a person and is not found. Scanning for surnames alone would
  collide across a roster that deliberately plants surname collisions.
- **Workbooks are not scanned for prose.** `.xlsx`/`.xls` expose no
  extractable prose in this pipeline; they are checked cell-by-cell against
  the finance ledger instead.
- **Scanning is not entity resolution.** A word-boundary string match is not
  a claim that the document is *about* that person, or that the string
  refers to the person the ledger registered it to. That is precisely why a
  hit becomes acceptable rather than required.
- **Equivalence members are not scanned.** A transmittal email's own body
  is skipped, because the email is a cluster member of the document it
  carries. An incidental mention appearing *only* inside a transmittal's
  covering note is therefore not found. The narrow case it costs: the
  email's planned recipients are already required mentions, so what is lost
  is an unplanned name in a covering note.
- **Legacy binaries are read through their DocIR.** `.doc`/`.ppt` text
  obligations run against the fact-resolved authoring source rather than a
  binary-format parser, so the scan sees what the verified modern
  intermediate rendered.

## What is recorded rather than fixed

`diagnostics.json` carries value collisions, unplanned alias sightings, and
incidental-mention counts. None of it is ground truth, none of it is scored,
and none of it gates a validator rule. It exists so that a disagreement
between the structured ledgers and the rendered prose is published rather
than silent. The exemplar's `Jim` residual, where the ledger registers a
nickname to one person while another person's prose claims it, appears there
mechanically.

The `graph_targets.alias_agreement` recipe knob turns that disagreement into
a hard failure at ingest, with the validator twin `MENT-03` enforcing it on
committed state. It defaults off, so an org that has not adopted the
discipline records the sighting instead.
