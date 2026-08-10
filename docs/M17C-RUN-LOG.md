# M17c run log: what the live arms surfaced

Observations from authoring the M17c arms, recorded as they were found.

**This is not the evidence standard and amends nothing in it.** The analysis
specification lives in `docs/M17C-EVIDENCE-STANDARD.md` and was fixed before
either arm was authored. This file is the criterion-seven record: the knobs'
first live exercise "including what went wrong". Nothing here changes what
counts as evidence, and no finding here is fixed mid-run, because changing the
generator between batches would author an arm's early documents against a
different configuration from its late ones and destroy the comparison the arms
exist to support.

## Arm tallies

| arm | authored | batches | ingest rejections |
| --- | --- | --- | --- |
| alpha (control) | 59/59 | 13 | 0 |
| beta (treatment) | in progress | | |
| gamma (control replicate) | not started | | |

Control arm finished clean: render 77/77, validate 27 rules run, 12 skipped, 0
errors, 0 warnings, report 0 off brief. `OUT-01` and `SCOPE-01` skip visibly
with their knobs off, which is the charter-grandfathering idiom rather than a
missing artifact.

## SCOPE-A: the scope profile is recipe-scoped, so seven of eight engagements get buy-side funnel vocabulary they do not fit

Found by the `author-0004` worker on the treatment arm's first batch, which
reported it rather than writing around it silently.

`ScopeProfile` is declared once per recipe and applied to every engagement:
`scope_facts_for(profile, eid, seed)` (`orgsmith/fabric/engagements.py:164`)
takes one profile and plants the same fact vocabulary under every engagement
id. `quillon-harbor`'s profile is buy-side M&A:

```yaml
scope:
  unit: acquisition targets
  pipeline: [targets screened, targets contacted, NDAs executed, offers submitted]
```

Every one of the org's eight engagements therefore carries
`f:<eid>.scope`, `f:<eid>.comparators`, and a four-stage
`f:<eid>.pipeline-*` funnel in that vocabulary. Exactly one engagement, the
Buy-Side Search for Morse PLC, has it as native language. The other seven do
not:

| engagement | why the vocabulary does not fit |
| --- | --- |
| Sell-Side Advisory | counterparties are acquirers; the seller has no "acquisition targets" |
| Fairness Opinion | has no deal funnel at all; it is a valuation opinion on one transaction |
| Growth Capital Raise | the pipeline is investors, not targets |
| Recapitalization Advisory | no target search |
| Management Buyout Advisory | the buyer is the incumbent management team |
| Carve-Out Advisory | the asset is known at the outset |
| Strategic Alternatives Review | the funnel is options, not companies |

The Fairness Opinion is the sharpest case: an engagement that by definition
has no acquisition funnel is planted with a four-stage one, so a document
citing those facts asserts something structurally false about its own
engagement.

**This is a design limitation, not a bug.** The knob does exactly what it was
built to do. The recipe comment shows its author reasoning carefully about
*plurality* ("no surface can render `1 acquisition targets`", floors above 1,
narrowest stage 3) and not at all about *kind-appropriateness*. What is
missing is that `ScopeProfile` has no per-engagement-kind variant, and
`fabric/engagements.py` has no notion of engagement kind to key one off:
the ledger's engagement records carry a name but no `kind` field.

**Why it is recorded and not fixed.** Criterion seven asks for the scope
facts whose rendered surface reads badly, and this is the answer to that
question. Fixing it needs either a per-kind profile map in the recipe or an
engagement-kind field in the fabric, both of which are their own unit of
work, and neither of which may land between two batches of the same arm.

**What it does and does not threaten.** It does not threaten the arms'
comparison: `engagements.scope` is absent from the control by construction, so
the defect exists only on the treatment side and is a property of the knob
rather than a confound between arms. It does mean the treatment arm ships
documents whose scope citations are vocabulary-mismatched on seven of eight
engagements, and any reading of the treatment arm's prose quality must know
that.

**Worker mitigation, noted so the prose is not over-credited.** The
`author-0004` worker wrote around the mismatch by choosing phrasing correct
under either reading ("we reviewed N companies against the criteria we set
with you", "we approached N of those") rather than asserting "targets". That
is a worker being careful, not the knob being right, and a worker that did not
notice would have written the mismatch straight through.

## SCOPE-B: the outline pool cycles on a fifth of all same-genre pairs, and the magnitude is now measured

The evidence standard anticipated this qualitatively and the instrument
already implements the split: `split_by_outline`
(`tools/ab_compare.py:192`) is the standard's first discriminating
comparison, and its docstring states the reading in advance. "If those still
score like the control's pairs, the outline work relocated the convergence
into groups of the pool size rather than reducing it, and that is the smaller
claim the standard says must be reported instead." Nothing below changes that
analysis. What was not known until the treatment plan existed is **how much of
the arm the split covers**, and it is a fifth:

| genre | docs | same-genre pairs | dealt the same skeleton | pool |
| --- | --- | --- | --- | --- |
| meeting_minutes | 13 | 78 | 15 | 4 |
| onboarding_record | 10 | 45 | 12 | 3 |
| status_report | 10 | 45 | 8 | 4 |
| engagement_letter | 8 | 28 | 7 | 3 |
| kickoff_memo | 8 | 28 | 4 | 4 |
| briefing_deck | 6 | 15 | 3 | 3 |
| company_overview | 4 | 6 | 1 | 3 |
| **total** | **59** | **245** | **50 (20.4%)** | |

The cause is arithmetic, not a defect: pools hold 3-4 variants and the larger
genres hold up to 13 documents, so `assign_outlines` cannot give every
same-genre pair a distinct shape and never claimed to. Its guarantee is that
no two *consecutive* same-genre documents share a skeleton, which is a
different and much weaker statement than the one a casual reader might take
from "outline variety". CLAUDE.md already warns against the stronger reading:
"'Impossible by construction' is an overclaim -- a finite pool cycles."

**The consequence for reading the result.** On the shape axis, those 50 pairs
were asked for the same sections in the same order, so they should score at or
near maximum shape similarity *by construction*. An arm-level mean over all
245 same-genre pairs therefore mixes two populations with opposite expected
behaviour, and could show the treatment arm as no better than the control, or
worse, for a reason that has nothing to do with whether the knob works. The
same-skeleton and different-skeleton subsets must be read separately, exactly
as the standard already requires of cross-batch and within-batch pairs. The
tool does this; this note records why it matters at this magnitude.

**Criterion one's pair floor is comfortably met.** The treatment arm scores
245 same-genre pairs against the required minimum of 120.

## OUT-A: skeletons that push against a genre's natural form

Reported by the `author-0002` worker, which authored six documents under four
distinct skeletons and flagged each tension rather than resolving it silently.

- **`co-history` forbids list blocks, while the same guidance asks a company
  overview to cover "service lines".** Service lines are the one thing a firm
  overview genuinely would bullet. The worker compressed them into a prose
  sentence, which reads acceptably, but this is the skeleton pushing against
  the natural form of the genre rather than varying it.
- **`or-role-table` mandates a table where the `onboarding_record` genre
  default says "2-4 short paragraphs, no sigblock".** The worker followed the
  skeleton, as briefed. A responsibilities table in an internal onboarding
  note is plausible, so this is a live tension rather than an implausible
  demand, but the skeleton and the genre default do contradict each other and
  the brief does not say which governs.
- **`target_words` counts table cells.** Two documents at a 450-word target
  carry noticeably less prose than prose-only documents at the same target,
  because the table's cells consume the budget. This is worth knowing before
  the length-against-brief metric is compared across arms: the treatment arm
  deals tables that the control arm does not, so equal `target_words` does not
  mean equal prose volume.

## OUT-B: three skeletons that could not be satisfied as briefed

Reported by the `author-0005` worker. These are the criterion-seven cases
proper: not a skeleton that merely fought the genre, but one that briefed
something unsatisfiable or something a real author would not write. Ingest
accepted all three documents, because what ingest enforces is block kinds and
order, not whether the briefed sections were reasonable to ask for.

- **A skeleton item that cannot be satisfied without breaking a hard rule.**
  `el-*`'s first item asks for "the client's inside address" while the work
  order's hard rules say "Do not invent people, organizations, addresses,
  amounts, or dates." There is no address in the ledger to place. The worker
  wrote recipient name, title and company and omitted street, city and postal
  lines, which is the closest satisfiable reading, and said so. The skeleton
  and the invention rule are in direct contradiction and nothing in the brief
  says which governs.
- **A skeleton that orders the document in a way its own genre default and its
  author's persona both contradict.** `km-owner-table` requires the workstream
  table as the *first* block. The genre default in the same guidance string
  says "Open with a short paragraph on objectives", and the briefed persona
  habit for that author is "sets context in a sentence before making any
  request". The worker followed the skeleton, as instructed, and the result is
  an internal kickoff memo that opens cold on a grid with the table's header
  row as its only orientation. The worker's own judgement, recorded: "A real
  associate would put one sentence above it."
- **A skeleton that assumes a predecessor document the plan did not create.**
  `sr-*` item four asks for "what changed in the risk picture since the last
  report" on what is the *first* status report of its engagement. The worker
  referred to "our last written update" and "the last working session" rather
  than inventing a predecessor status report. A skeleton dealt by genre does
  not know a document's position in its engagement's own sequence.

A fourth instance of the skeleton-versus-persona tension already recorded
under OUT-A: `el-*` and `km-owner-table` forbid list blocks while that
author's persona "prefers numbered lists over bullet points", resolved by
enumerating in prose.

### OUT-B1: the category behind two of these, skeletons that ask for content the airlock forbids inventing

Two of the unsatisfiable cases are the same failure at different genres, and
it is worth naming as a category because it will recur in any recipe:

| skeleton item | what it asks for | why it cannot be written |
| --- | --- | --- |
| `el-*` item 1 | the client's inside address | no address exists in any ledger; inventing one is a hard-rule violation |
| `mm-action-table` | actions, owners and **due dates** | no date fact is briefed for the doc; any literal calendar date is rejected |

Both were resolved by writing the satisfiable part and omitting the rest
(name/title/company with no street; relative dues such as "This week",
"Before the first call"). The `author-0001` worker stated the cost plainly:
"A real author would likely write real dates here; the airlock makes that
impossible."

The skeletons were written as descriptions of what these genres contain in
life. The airlock's rule is that the model never writes a value the ledger
owns. Where a genre's natural content is a value no ledger holds, the two are
irreconcilable and the skeleton loses. This is not an argument against the
airlock, which is the project's foundation; it is a statement that the outline
pools were authored without reference to what the airlock permits, and that
some pool entries are therefore unsatisfiable by construction.

### OUT-B2: a related realism cost that is not the outline knob's fault

Recorded here because it was found on this arm, though it applies to any arm.
The `author-0001` worker omitted the Date line from a kickoff memo's header,
because the memo's own date falls within two weeks of `f:E-2014-001.start` and
writing it literally risks colliding with that fact's rendered value, which
ingest rejects. All six of that batch's documents are free of literal calendar
dates for the same reason.

Real memos carry Date lines. The literal scan cannot distinguish "the document
states its own date, which is a property of the document" from "the document
transcribes a ledger value", so the safe authorial move is to omit dates
entirely. The control arm is subject to this identically, so it is not a
confound; it is a standing realism cost of the enforcement, and it is the kind
of thing a board reading either arm may report as a defect without knowing why
it is there.

### Deck shape under `bd-data-led`

The skeleton requires the quantity table as the deck's *second* block, so the
title slide carries no body of its own and the table lands directly beneath the
title; item 4 then puts a ~180-word prose paragraph on a slide. The
`author-0001` worker followed it exactly and recorded that "a real deck author
would give the table its own titled slide and cut the prose to bullets or
speaker notes". Anything else would displace the table from second position,
which the skeleton forbids.

## SCOPE-A, independently confirmed three times, and what the mismatch costs in prose

Three workers in fresh contexts reached this finding on three different
engagements without being told the others had: `author-0004` on the Sell-Side
Advisory (E-2014-001), `author-0005` on the Recapitalization Advisory
(E-2016-001), and `author-0001` again on the Sell-Side Advisory. The
`author-0001` worker put it most compactly: "In a sale, the counterparties are
buyers", and phrased around the ledger noun with "the buyer universe, which we
currently size at {scope}". That three independent readers all flagged it, and
all chose to write around it rather than through it, is the strongest evidence
in this log that the mismatch is real rather than a matter of taste.

**The finding has an accidental negative control, and it holds.** Exactly one
of the org's eight engagements is a buy-side search, the Morse PLC mandate
(E-2015-001), and it is the one engagement whose kind the scope vocabulary
actually fits. The `author-0003` worker authored that engagement's whole
six-document arc, scrutinised six skeletons closely enough to report two
unrelated stylistic tensions, and reported **no scope mismatch at all** and
"nothing in any skeleton struck me as something a real author would not
write". So the workers are not simply complaining about everything put in
front of them: the seven mismatched engagements drew complaints and the one
matched engagement did not. That asymmetry is what distinguishes a real defect
from reviewer noise, and it arrived without anyone designing for it.

The `author-0005` worker's resolution is the part worth recording, because it
shows the cost. It reached the same finding on the Recapitalization Advisory,
naming
`f:E-2016-001.scope`, `.pipeline-targets-screened` and
`.pipeline-targets-contacted` as buy-side vocabulary attached to a recap.

Its resolution is the part worth recording, because it shows the cost. The
worker made the facts cohere by writing the mandate as "a recapitalization
whose new capital funds an add-on acquisition program", which makes the target
funnel the growth plan attached to the recap and keeps all five documents
consistent. It labelled this itself: "That is an authorial reconciliation, not
a fix: if the recipe intended a pure recapitalization, the scope and pipeline
facts are attached to the wrong engagement kind."

So the mismatch does not surface as a visibly wrong sentence. It surfaces as
**invented narrative whose only job is to justify a fact the ledger planted
under the wrong engagement**. That is worse than a bad sentence for a corpus
whose value proposition is that the ledger owns the facts: the prose is now
carrying a story the ledger never authorised, generated to rescue the ledger's
own mistake. A reader auditing the corpus against the answer key would find
the numbers correct and the premise fabricated.

## MENT-A: a required mention with no sigblock forces a self-naming byline

Also from `author-0002`. Every `onboarding_record` in that batch requires the
literal surface "Heather Delacruz" while she is the sole author and the genre
forbids a sigblock. The only remaining device is a self-naming byline inside
the prose ("Prepared by Heather Delacruz, Managing Partner"). It is realistic
for an internal file note, but it is a constraint artifact rather than an
authorial choice, and it recurs across four documents by design of the briefs.
The worker varied its phrasing and position. This is the same family as the
recorded mail residual in CLAUDE.md, where a required body mention produces a
surface a real author would not have chosen, and it is recorded here for the
same reason: the mention model requires a surface without knowing what device
the genre leaves available to carry it.
