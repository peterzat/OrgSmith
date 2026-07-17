# Model A/B: does the authoring model actually matter?

The README told people to "use the strongest model available to you." That
was folklore: plausible, repeated, never measured. This is the measurement.

**Result: the folklore was right, and the gap is not subtle.** One model
produced a corpus a blind reviewer said it "would take a deliberate effort
to catch out." The other produced one the same reviewer refused outright.
**Both validated clean under all 29 rules.**

Two experiments live in this document. The first (2026-07-16, below) is
Opus against Haiku on pre-M9 briefs, and it established that the axis is
real. The second ([Round 2](#round-2-opus-against-sonnet-2026-07-17)) is
Opus against Sonnet on current briefs, run because the first does not
license a conclusion about a mid-tier model, and because the cost case for
one deserved a number rather than an intuition. **Round 2's headline is
that the cost case failed before the quality case did: Sonnet used 1.89x
the tokens for identical work, which at standard pricing makes it more
expensive than Opus, not less.**

## Setup

`ab-probe` (Halloway Reed Advisors LLC), a 5-person consultancy, 11 planned
documents / 9 authored, 2019-2022. Deliberately **not committed** — it
lives in gitignored `scratch/`, so it raises no frozen-fixture question.

The control is exact. Both arms ran the same recipe at the same seed, so
`docplan/manifest.jsonl` and every ledger are **byte-identical across
arms** (verified by `diff -r`). Same briefs, same facts, same target word
counts, same required mentions. The only variable is the model that
answered the work orders. Both arms ran the real `/forge` procedure: fresh
context per batch, one enrichment pass plus three authoring batches.

| | Arm A | Arm B |
| --- | --- | --- |
| model | `claude-opus-4-8[1m]` | `claude-haiku-4-5-20251001` |
| self-reported effort | `xhigh` | `standard` |
| board reviewer | `claude-opus-4-8`, held constant | same |

## What the deterministic side saw

| measure | Arm A | Arm B |
| --- | ---: | ---: |
| **validate** | 20 rules, **0 errors** | 20 rules, **0 errors** |
| authored docs | 9 | 9 |
| total words | 2,909 | 1,504 |
| mean words/doc | 323.2 | 167.1 |
| mean ratio to brief | **1.16** | **0.60** |
| docs off brief | **0 / 9** | **8 / 9** |
| same-genre pairs flagged | 1 (`d:0001`/`d:0008` @ 0.2833) | 0 (top pair 0.041) |

**The validator cannot tell these two corpora apart.** Identical rule
counts, zero errors, both arms. Every planted fact lands where it should,
every required name appears, every formula ties out — in a corpus a
knowledgeable reader rejects on sight. This is the clearest available proof
of the gap M7 exists to close: the 29 rules verify that documents agree
with their ledgers, and that is all they verify.

**The metric can tell them apart, decisively, for free.** Arm B writes at
60% of what its briefs asked, with 8 of 9 documents off brief; Arm A lands
at 116% with none. That is a no-model, no-token check that separates the
arms unambiguously — the cheapest quality signal in the system.

## What the board saw

Reviewers were blind: same prompt, same dimension, same reviewer model,
told nothing about the experiment.

**Arm A — 1 minor, 2 notes, 0 majors:**

> Would a knowledgeable reader believe a real firm produced this corpus?
> **Yes, and it would take a deliberate effort to catch out.** [...] The one
> thing that gives it away is the shared prose reflex above — everyone in
> this firm has the same wit — which reads less like a machine than like a
> novelist who could not stop writing good lines for characters who should
> not have them.

**Arm B — 2 majors, 2 minors:**

> **No, a knowledgeable reader would not believe a real firm produced
> this.** The corpus is too thin to survive first contact — nine documents
> totaling 1,504 words as a consultancy's entire 2019-2022 output, with an
> "EXECUTED" engagement letter running 125 words and no recipient address
> on it. [...] nobody in the firm has a personality, no engagement ever has
> a problem [...] and the seams between generation batches are visible as
> abrupt template amnesia.

The board and the metric agree, independently, in the same direction.

## Three findings worth more than the headline

**1. Low similarity is not a quality signal — it is inverted.** Arm B
scored 0.041 same-genre overlap against Arm A's 0.283, and Arm B is the
worse corpus. Read naively, "less repetition" looks like a win. It is not:
Arm A's two engagement letters share a template *because a real firm's
letters do*, and Arm B's share nothing because they are too thin to share
anything. This independently reproduces the board's calibration finding
(`docs/REVIEW-CALIBRATION.md`): **a similarity metric can only flag prose
that repeats, and is structurally blind to prose that fails to repeat where
house style requires it.** Never read a low similarity score as health.

**2. Self-reported provenance is demonstrably unreliable — as designed
for.** Arm B reported its effort as `standard` while the session it ran in
reported `xhigh`, and it skipped the `generator` stamp on its enrichment
batch entirely (3 of 4 batches recorded, versus Arm A's 4 of 4). The weaker
model partly ignored the instruction to report itself and partly reported
something else.

This is the empirical vindication of the spec's load-bearing design call.
Had any validator rule trusted the `generator` field, it would now be
enforcing a value the model made up. Provenance is a record, not an oracle,
and this is why. The system degraded exactly as intended: the missing stamp
reports "unrecorded", the unknown effort ranks as unknown rather than
below-floor, and nothing failed.

**3. The board found a real pipeline bug, in a lane no one assigned it.**
Arm B's reviewer noticed that the PDF renderer silently flattens `\n`
inside a paragraph block while the DOCX renderer honors it as `<w:br/>`.
Verified independently: `pdf.py:90` emits `<p>{text}</p>`, where HTML
collapses newlines to spaces, and python-docx does emit `<w:br/>`. It
affects the committed fixture `gladepoint-strategies` `d:0008`, a PDF whose
addressee block renders as one smeared line. It validates clean because no
rule checks line breaks. Filed to BACKLOG.md; out of scope for M7.

## Limits

- **n = 1.** One org, one model pair, one run each. Directionally
  overwhelming, statistically nothing. This establishes a default with
  evidence behind it, not an effect size.
- **The effort axis was not independently varied.** The Agent tool exposes
  a per-worker `model` but **no effort parameter**, so effort could not be
  set per arm; both inherited the session. The arms' self-reported efforts
  differ (`xhigh` vs `standard`) but that report is exactly the thing
  finding 2 shows is untrustworthy. **This is a model A/B, not a model ×
  effort A/B.** Read the title accordingly.
- **This answers the spec's open question about the floor's mechanism.**
  The harness offers no per-worker effort lever, so the authoring floor
  cannot be enforced by dispatching workers at a chosen effort. Preflight
  warning plus provenance — what `orgsmith/effort.py` and `/forge` Step 0
  actually do — is the only mechanism available, and that is now verified
  against the harness rather than assumed.
- **A stronger board reviewer judged both arms.** Using the weak model as
  its own critic was not tested, and per the "critics share the
  generator's blind spots" argument, it would likely be worse.

## Conclusion

Use the strongest model available for authoring passes. That is no longer
folklore; it is a default with a measurement behind it. Where the recipe or
budget forces a weaker model, expect a corpus at roughly 60% of brief that
still passes every deterministic check — and run `report` and the board
before believing it.

---

# Round 2: Opus against Sonnet (2026-07-17)

Round 1 tested Opus against Haiku. Haiku is a small, fast, cheap model, and
nobody was surprised it wrote thin documents. That result establishes the
axis is real and large. It says nothing about where a strong mid-tier model
sits on it, and Sonnet 5 is priced 40% below Opus 4.8, so "Opus is overkill
for placing prose around placeholders" was a live hypothesis worth a
measurement rather than a dismissal.

**Result: use Opus, but not for the reason expected. Sonnet's prose is
mildly thinner (0.853 of brief against Opus's 0.967). Sonnet's cost is the
thing that failed: it burned 1.89x the tokens for byte-identical work,
which more than eats a 0.6x per-token price.**

## Why Round 1's numbers could not be the control

Round 1's Arm A landed at 1.16 of brief. That number cannot be compared to
anything measured today. `git merge-base --is-ancestor a9ec852 18aa4f2`
confirms the Round 1 experiment predates "M9: per-genre word targets live
in the registry, raised to real lengths." Arm A was writing against briefs
asking 130-350 words; the registry now asks 1,100 for an engagement letter,
850, 750, 650. The briefs roughly tripled underneath the measurement.

This cuts both ways, and the second direction is why the experiment was
worth running at all: Haiku's 0.60 was measured on the *easy* briefs. The
1,100-word clause-bearing engagement letter is exactly where a mid-tier
model would be expected to diverge from a frontier one, and no prior
measurement had put any model against it. So Round 2 is a **fresh two-arm
run**, Opus control included, on current briefs.

## Setup

`ab-probe-v2` (Calderwood Pace Consulting LLC), a management consultancy
that grows from 5 seats to 8 across 2018-2023. 28 planned documents: 22
model-authored plus 6 deterministic workbooks. Gitignored `scratch/`, so it
raises no frozen-fixture question. Chosen over reusing Round 1's `ab-probe`
for external validity: it exercises the v2.0 stack (roster growth,
behavioral finance) and the fleet's real genre mix including a briefing
deck and an email thread, which `ab-probe` had no instance of. Its recipe
is coherent by the fleet's own check (24.8% terminal net margin, inside the
fleet's 20.0-26.2% band).

The control is exact, and was verified rather than assumed before any token
was spent. Both arms ran the same recipe at the same seed. `diff -r` reports
`charter.json`, `foundation.json`, every ledger, and `docplan/manifest.jsonl`
byte-identical across arms, and `--next-batch` produced the **same five
batches over the same 22 document ids** in both. Same briefs, same facts,
same target word counts, same required mentions. The only variable is the
model that answered the work orders.

Both arms ran the real airlock: work orders emitted by the CLI, authored by
fresh-context `forge-author` workers, ingested serially by the orchestrator.
Each arm used its own model for **both** the enrichment pass and all five
authoring batches, which is what a real fleet run would do.

| | Arm A (control) | Arm C |
| --- | --- | --- |
| model | `claude-opus-4-8[1m]` | `claude-sonnet-5` |
| self-reported effort | `xhigh` | `xhigh` |
| board reviewer | `claude-opus-4-8`, held constant | same |

The decision rule was **pre-registered before results were read**, per this
project's rule that nothing post-hoc gates: Sonnet wins only on validate
clean AND mean ratio >= 0.90 AND within 10% of control AND
docs-off-brief not materially worse AND no board majors it does not also
raise against Opus. Ambiguous resolves to Opus, because the fleet gets
byte-pinned and ties go to the incumbent.

## What the deterministic side saw

| measure | Arm A (Opus) | Arm C (Sonnet) |
| --- | ---: | ---: |
| **validate** | 24 rules, **0 errors** | 24 rules, **0 errors** |
| ingest rejections | 0 | 0 |
| authored docs | 22 | 22 |
| total words | 14,463 | 12,481 |
| mean words/doc | 657.4 | 567.3 |
| **mean ratio to brief** | **0.967** | **0.853** |
| docs off brief | **0 / 22** | **4 / 22** |
| same-genre pairs flagged | 0 | 0 |

**The validator still cannot tell them apart**, now on briefs three times
longer than Round 1's. Identical rule counts, zero errors, zero warnings,
both arms. Neither arm's deliverables were rejected at ingest, so the
airlock's lints (missing placeholders, invented people, literal values
where a placeholder belongs) did not separate them either. This is Round
1's central finding, reproduced against a harder target.

**The metric can, and it localizes the gap to the genres that matter:**

| genre | Opus | Sonnet |
| --- | ---: | ---: |
| engagement_letter | 1.08 | 0.85 |
| status_report | 0.98 | 0.76 |
| meeting_minutes | 0.95 | 0.79 |
| briefing_deck | 0.96 | 0.84 |
| kickoff_memo | 0.95 | 0.89 |
| company_overview | 0.97 | 0.95 |
| engagement_email | 1.03 | 0.91 |
| onboarding_record | 0.89 | 0.92 |

Sonnet is under target on seven of eight genres, and the gap is widest on
the engagement letter and the status report. That is the predicted failure
mode confirmed: the longer and more structured the genre, the further
Sonnet falls short. It is not a collapse. Round 1's Haiku wrote at 0.60
with 8 of 9 documents off brief; Sonnet writes at 0.853 with 4 of 22 off.
A reader would call Sonnet's corpus slightly terse, not fake.

## The cost result, which is the actual finding

The premise of the experiment was that Sonnet is meaningfully cheaper.
Measured over the same 22 documents and one enrichment pass:

| | Arm A (Opus) | Arm C (Sonnet) |
| --- | ---: | ---: |
| subagent tokens | 264,516 | **500,180** |
| ratio | 1.00x | **1.891x** |
| slowest batch wall-clock | 5.7 min | 11.0 min |

**Sonnet spent 1.89x the tokens to produce 0.86x the words.** It made more
tool calls, re-read more, and self-checked more.

Sonnet 5 is priced at exactly 0.6x Opus 4.8 on **both** halves ($3/$15 per
MTok against $5/$25), and cache reads scale ~0.1x for both, so the cost
ratio is `token_ratio * 0.6` and is robust to whatever the input/output/cache
mix turns out to be:

| pricing | arithmetic | result |
| --- | --- | --- |
| standard ($3/$15) | 1.891 x 0.6 | Sonnet costs **13% more** than Opus |
| introductory ($2/$10, through 2026-08-31) | 1.891 x 0.4 | Sonnet costs **24% less** |

At standard pricing the cheaper model is the more expensive choice for this
workload. The introductory window is the only regime where Sonnet saves
anything, and it saves 24% while writing 12% thinner. For a fleet that is
byte-pinned and lives for years, that is not a trade worth making.

The transferable lesson is not about Sonnet. It is that **a per-token price
is not a cost**, and for an agentic authoring workload the token multiplier
can move further than the price does. Any future model comparison here
should measure tokens spent, not quote a rate card.

## What the board saw, and did not see

Four blind reviewers, `claude-opus-4-8` held constant, told nothing about
the experiment, reading arms renamed `arm-1` / `arm-2` with every model
identifier scrubbed from the trees (workorders removed, `state.json`
`generators` emptied, `GENERATION-REPORT.md` re-derived, verified by grep).
Two dimensions per arm: `document_plausibility` and `cross_document_voice`.

**The board rejected both arms, on both dimensions, and did not discriminate
between them.** Both plausibility reviewers answered "no, a knowledgeable
reader would not believe a real firm produced this." Both voice reviewers
answered "yes, one person wrote everything." The majors landed on the same
targets in both arms: a corpus-wide antithesis tic ("X, not Y") at roughly
one per 105-124 words across every author, engagement letters whose
governing-law clause names no state, all three letters countersigned the
same day they were dated, no address anywhere, and a 2017-2022 span in
which COVID does not exist while FY2020 revenue grows 10.5% and travel
spend rises 12% at a firm whose model is walking plant floors.

For the model decision this is a null result: the board is not a lever,
because it fails Opus too. Every one of those findings is a **generator**
finding, not a Sonnet finding. They are logged where they belong (BACKLOG,
and the M11b flagship board pass), not here.

## Findings worth more than the headline

**1. The board manufactured a false finding, and it is now on the record.**
One reviewer reported that "arm-1 and arm-2 render byte-identical Firm
Overview prose" and flagged it as a possible experiment defect. This is
verifiably false: all 22 authored DocIRs differ between arms, and the two
Firm Overviews are not remotely alike (Opus opens "Calderwood Pace is a
management consultancy for mid-market manufacturers. We are small, on
purpose."; Sonnet opens "Calderwood Pace Consulting serves mid-market
manufacturers. We advise on operations, and on the numbers operations
produce..."). The reviewer even attributed a Sonnet sentence to the Opus
arm. This is the first measured instance of the board asserting a checkable
falsehood, and it is exactly what BACKLOG `board-negative-control` says is
unmeasured. It cost nothing to catch here because the claim was
ledger-checkable in one `diff`. A board finding that is *not* self-verifying
deserves the same scepticism and has no such cheap check.

**2. The cause was a harness error, which is its own lesson.** The four
reviewers ran concurrently and shared one session scratchpad, so one
reviewer's extracted document text appeared in another's working directory.
The arm-1 reviewer noticed the stray files and said so. Per-arm verdicts are
sound (each reviewer read its own share directory), but the cross-arm claim
was contaminated. **A board dispatched over more than one org at a time
needs per-reviewer scratch isolation**; `/forge-review` is per-slug and does
not hit this today.

**3. Both boards flagged that the corpus narrates its own generation spec.**
The Firm Overview recites the document genres as firm philosophy ("Kickoff
memos set out what the team will do in the first thirty days... Meeting
minutes record what was decided, not what was merely discussed"). That is
the recipe's own narrative brief, faithfully turned into prose. It is not a
probe artifact: the committed `meridian-actuarial` recipe describes its
document genres the same way. Logged to BACKLOG as
`recipe-brief-leaks-genre-spec`.

## Limits

- **n = 1**, one org, one run per arm. Same limit Round 1 has. Directionally
  clear, statistically nothing.
- **The token ratio is one workload's.** 1.89x is measured on 22 documents
  of professional-services prose with this brief shape. It is not a general
  Sonnet-vs-Opus constant, and it is the number most likely to move.
- **The effort axis was still not independently varied.** The Agent tool
  exposes a per-worker `model` but no effort parameter, so both arms
  inherited the session's `xhigh`. Both arms self-reported `xhigh`, which
  Round 1 finding 2 shows is exactly the kind of report not to trust. This
  is a model A/B, not a model x effort A/B.
- **Enrichment diverges before authoring.** Each arm's personas are written
  by its own model and feed the authoring briefs, so the control is exact at
  the ledger and manifest, not at every byte of every work order. That is
  inherent to the design and Round 1 shares it: writing good personas is
  part of what is being measured.
- **The board's false-positive rate is still unmeasured.** Finding 1 is one
  instance, not a rate.

## Conclusion

Use Opus for the fleet. Sonnet 5 is a capable authoring model and the gap in
prose quality is real but modest, roughly 12% thinner with the deficit
concentrated in the longest genres. The decision does not rest on that. It
rests on Sonnet spending 1.89x the tokens, which erases a 0.6x per-token
price and leaves it more expensive at standard rates. There is no version of
this trade that is worth a byte-pinned fleet.

The general rule this adds to Round 1's: **measure tokens, not rate cards,
and re-measure the control whenever the briefs change.** Round 1's headline
number was invalidated by an unrelated milestone raising word targets, and
nothing flagged it. Round 2's numbers will be invalidated the same way the
next time the genre registry moves.
