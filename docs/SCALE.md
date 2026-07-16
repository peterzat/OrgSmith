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
words**, against briefs asking 130-350. Real engagement letters run 800-1500.
The model was roughly hitting its targets; the targets were wrong. **M9
raised them**: length is now a per-genre property of the genre registry
(`docplan/registry.py`), with engagement letters targeting 1100 (800-1500)
and every authored genre raised off the old band. At the old lengths a
flagship would need ~8,500 documents to be a genuine retrieval problem; at
realistic lengths it needs ~2,000. **Raising the targets is what makes the
flagship affordable**, which is why M9 preceded M12.

Two facts on the 236 figure now that M9 has landed. First, only `dev-mini`
is regenerated so far: it authored at **mean 717 words** under the raised
targets (every document within 75-150% of its brief), while the six frozen
fixtures retain their pre-M9 lengths until the M11 fleet reset, so the
fleet mean is currently mixed. Second, the fixed genre skeleton is gone:
document supply is now driver-derived (the registry walks the firm's
engagements, fiscal years, and hires), so "~2,000 documents" is a recipe of
the right shape rather than a planner rewrite. `dev-mini` grew from 13 to 22
documents on the same recipe purely from the drivers.

## The authoring wall is the binding constraint

Everything above is cheap except the writing. Authoring is a model pass
per batch, `BATCH_SIZE = 6` documents (`contexts.py`). Before M10, `/forge`
dispatched those batches strictly serially, one worker at a time. **M10
lifted that to a bounded parallel window (K = 4 by default)**: several
batches are outstanding at once over disjoint document sets, the model
authoring runs concurrently, and the deterministic merge stays serial (the
CLI is still a single writer of `state.json`), so resume is unchanged.

Serial or parallel, the wall is batch-count times per-batch time, divided
by the parallel width. The batch counts:

- a 360-doc reference fleet: ~60 batches
- a 2,000-doc flagship: ~334 batches

**Per-batch timing, first measured 2026-07-16** (dev-mini regenerated
through the live `/forge` loop, Opus 4.8 at `max` effort, on the dev box;
a single run, so read it as an order of magnitude, not a constant). One
fresh-context worker authored a 3-to-5 document engagement-group batch in
**9.3 to 16.9 minutes** (batches of 4/3/5/5 docs took 9.6/9.3/13.3/16.9
min; mean ~12), roughly 2.5 to 3 minutes per document and rising with genre
length. Foundation enrichment (six personas) was a shorter pass at ~1.7 min.

The parallel window is real, not notional. Authoring the three remaining
batches (13 docs) concurrently in one message took **17.5 minutes of
wall-clock against 39.4 minutes of summed worker time (2.24x), within 4% of
the single slowest worker**: the workers overlapped rather than queued.
dev-mini's whole authoring pass ran in ~27 minutes this way versus ~49
minutes fully serial, and a pure K = 4 window would collapse a same-size
run to its slowest batch (~17 min, ~2.9x). The run also confirmed the M10
airlock end to end with live workers: three work orders outstanding at
once, disjoint, ingested out of emission order, and the org validated 23
rules with 0 errors, byte-identical in structure to the committed fixture.

Scaled at ~12 min/batch: a 360-doc fleet is ~60 batches (~12 hours serial);
a 2,000-doc flagship is ~334 batches (~2.8 days serial). At the measured
~2.2x window speedup those fall to roughly **5 hours** and **~1.3 days**; a
wider or better-balanced K = 4 window does better. Both stay multi-session,
so resume is not a convenience at that size; it is the only reason it is
possible at all. K trades directly against session budget and concurrency
limits, never against the airlock.

This is why parallel authoring is **M10** and precedes the fleet: the wall
is the schedule. Nothing else on this page is close to binding.

## What would change these targets

- **Raising `_TARGET_WORDS` (M9)** changes every row of the token table
  and lowers the flagship's document count by ~4x. Re-measure after.
- **Parallel authoring (M10, landed)** attacks the only binding
  constraint: a bounded K-wide window over the serial wall, so the wall
  now falls as ~(batch-count x per-batch time) / K. First live measurement
  (2026-07-16, above): ~12 min/batch, a 3-wide window at 2.24x. Re-measure
  at fleet scale (M11), where K = 4 runs against many more batches.
- **A larger context window in the wild** raises the flagship's bar. The
  target is a moving one by nature; size the margin, not the number.
- **Format mix.** The ~36 KB/doc mean hides a wide spread: scanned PDFs
  and a legacy `.ppt` dominate the fleet's bytes (one `.ppt` is 607 KB,
  larger than most orgs' entire share). A scan-heavy flagship is a disk
  question in a way a text-heavy one is not.
