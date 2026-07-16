# Scale: how big, and why

What size should a generated org be? Three different answers, because
there are three different jobs. This document settles the targets and the
reasoning; **M7 writes them down and builds none of them.** The reference
fleet is M11 and the flagship is M12.

**Milestone numbers here follow the M8 renumbering** (SPEC.md states it
once): the roster/finance/brief work is M8, the document-supply model and
realistic lengths are M9, parallel authoring and the scale fixes are M10,
the reference fleet is M11, and the flagship is M12. Earlier drafts of this
file numbered the fleet M10 and the flagship M11.

All numbers below were measured against the committed fleet at v1.5.0
(seven orgs, 107 share files, 81 authored documents) on the development
box. Re-measure before trusting them; they are here to show the shape of
the constraints, not as constants.

## The three sizes

| tier | size | job | when |
| --- | --- | --- | --- |
| fixtures | 9-19 docs | regression oracles | now (committed) |
| reference fleet | ~360 docs total, ~30-60 per org | prove breadth | M11 |
| flagship | one org, large enough to defeat a context window | prove scale | M12 |

These are three jobs, not three points on one line. Conflating them is
what produced the contradiction this document exists to resolve: an
earlier plan carried both "fleet ≈2,000 docs" in its decision line and
≈360 in its own recipe table. Both numbers were right about different
things. **Breadth and scale are separate axes**, and one fleet cannot
carry both without being the worst of each.

## Fixtures stay small

A fixture's job is to fail loudly when a change breaks something. That
job is served by coverage of *kinds*, not volume: one legacy binary
proves the legacy path, one image-only scan proves the OCR archive, one
multi-affiliation contact proves era-correct employer resolution. A
second copy of each proves nothing new and costs the org tier on every
run, forever.

Measured cost of the org tier: **~15 ms per validated file** (~1.6 s wall
over 107 share files; `validate` alone accounts for ~9 ms/file, the rest
is the extraction and completeness suites). That is the tax every fixture
levies on every test run for the life of the project.

The budget in SPEC.md is org under ~5 s. At 15 ms/file that is roughly
**330 share files** before the tier blows its budget — about triple
today's fleet. Fixtures are cheap, but they are not free, and the tier is
the thing that must stay fast enough to run without thinking.

Note the per-org spread: cindergrove-advisors validates at 2.3 ms/file
against bramblewood-legal's 17.1. Rules skip in bulk on an org whose
documents are image-only scans and legacy binaries, because there is less
extractable text to check. A fixture's cost tracks what it proves.

## The reference fleet proves breadth

Breadth means: does the generator hold up across eras, sectors, ACL
postures, and format mixes? That is answered by *variety of recipes*, not
by document count. Six to eight orgs of 30-60 documents each (~360 total)
covers the axes with room for one deliberate oddity per org.

Disk is not the constraint. Measured: **~36 KB per modern-format
document** (84 modern-format files, 3.0 MB), which puts a 360-doc fleet
around 13 MB of share plus metadata. That is a comfortable git
repository.

The real constraint is the authoring wall, below.

## The flagship carries scale, and must be sized to actually defeat a reader

This is the part that arithmetic settles rather than intuition, and the
answer is not what the document count suggests.

A corpus is only a retrieval problem if it cannot simply be read. Measured
against the committed fleet:

| corpus | authored words | ~tokens |
| --- | ---: | ---: |
| the whole committed fleet (81 docs) | 19,083 | ~25K |
| a 360-doc reference fleet, today's lengths | 84,960 | ~113K |
| a 2,000-doc org, today's lengths | 472,000 | ~628K |
| a 2,000-doc org at realistic lengths (~800 words) | 1,600,000 | ~2.1M |

(Tokens estimated at 1.33 per word.)

Read that third row. **A 2,000-document org, at the lengths this
generator currently produces, fits inside a 1M-token context window.** An
agent could ingest the entire company and answer every question without
retrieving anything. As a test of a retrieval system it would prove
nothing, no matter how many files it contained.

The threshold is not a document count. It is total tokens against the
largest context window a caller might bring, and the honest target is to
exceed it by enough that the margin survives the next model generation.
Only the fourth row does that, and it needs **both** more documents and
longer ones.

Which makes the corpus-length finding load-bearing for scale, not just for
realism. Measured mean across all 81 authored documents at v1.5.0: **236
words**, against briefs asking 130-350 (`_TARGET_WORDS`, `contexts.py`).
Real engagement letters run 800-1500. The model was roughly hitting its
targets; the targets were wrong. Until they are raised (**M9**, the
document-supply model, where length is a per-genre property of the genre
table), a flagship would need ~8,500 documents to be a genuine retrieval
problem, and at realistic lengths it needs ~2,000. **Raising the targets is
what makes the flagship affordable**, which is why M9 precedes M12.

Two cautions on the 236 figure now that M8 has landed. First, it predates
the behavioral facts and date-scoped briefs, which give the model more true
material to write from; the regenerated `dev-mini` authored at 331 words
against the same targets, so the mean is not a fixed property of the
generator. Second, and more important, a document count is not a knob today:
the planner emits a fixed genre skeleton (`2E + 7 + pptx + eml`), so
"~2,000 documents" is M9 work before it is M12 work. See the M9 spec.

## The authoring wall is the binding constraint

Everything above is cheap except the writing. Authoring is a model pass
per batch, `BATCH_SIZE = 6` documents (`contexts.py`), and `/forge`
dispatches batches **strictly serially** — one worker at a time, each
with a fresh context.

That is deliberate and it is what makes long runs resumable: at most one
outstanding work order per stage, state derived from files, kill the
session and re-run. It is also a hard wall on wall-clock time:

- a 360-doc reference fleet: ~60 batches, serial
- a 2,000-doc flagship: ~334 batches, serial

At a few minutes per batch (not measured here; the committed fleet was
authored across sessions, so no clean per-batch timing exists) a flagship
is a multi-day, multi-session generation. Resume is not a convenience at
that size; it is the only reason it is possible at all.

This is why parallel authoring is **M10** and precedes the fleet: the wall
is the schedule. Nothing else on this page is close to binding.

## What would change these targets

- **Raising `_TARGET_WORDS` (M9)** changes every row of the token table
  and lowers the flagship's document count by ~4x. Re-measure after.
- **Parallel authoring (M10)** attacks the only binding constraint.
- **A larger context window in the wild** raises the flagship's bar. The
  target is a moving one by nature; size the margin, not the number.
- **Format mix.** The ~36 KB/doc mean hides a wide spread: scanned PDFs
  and a legacy `.ppt` dominate the fleet's bytes (one `.ppt` is 607 KB,
  larger than most orgs' entire share). A scan-heavy flagship is a disk
  question in a way a text-heavy one is not.
