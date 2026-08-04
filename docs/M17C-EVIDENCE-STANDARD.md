# M17c evidence standard, fixed 2026-08-03, amended during the run

What would count as M17b's outline work having changed authored prose, what
would count as it not having, and what this measurement cannot settle either
way. The analysis specification below was written and committed **before**
either arm was authored, so the conclusion cannot be chosen after the numbers
exist. SPEC.md (2026-08-03) criterion two; verifiable from git order.

Nothing in this document gates anything. No number below is a threshold, no
test tier reads any of it, and no validator rule derives from it. It is a
statement of what the authors will accept as an answer, recorded in advance.

## Amendment log

Kept because a pre-registration that is silently edited is not one. Every
entry is dated against the state of the run, and **no amendment has changed
what counts as evidence**: the three comparisons below are as first written.
Amendments so far either tighten the control or narrow what may be claimed.

- **2026-08-03, before any authoring.** Persona enrichment shared across arms
  rather than run per arm (closes a confound). A third arm added, the control
  replicate, with `noise_floor` as its instrument.
- **2026-08-04, control arm at 19/59 authored, no comparison run.** The
  within-batch convergence caveat, and the instruction to report cross-batch
  and within-batch pairs separately rather than pooled. Narrows the claim.
- **2026-08-04, control arm at 30/59, no comparison run.** The finding that
  the "never sees a sibling" premise is false. Narrows the claim and corrects
  a diagnosis; changes no analysis.
- **2026-08-04.** `noise_floor` gained a paired per-pair spread after review
  found the aggregate form could report zero noise on runs where every pair
  moved. A correction to an instrument, not to the standard.

## The setup

One recipe, `quillon-harbor`, generated twice. The control arm strips
`doc_culture.outline_variety`, `doc_culture.client_facing_reports` and
`engagements.scope`; the treatment arm turns all three on. Everything else
is identical, including the per-author style and voice layer, which is on in
both arms so that this measures the outline work rather than the M16 work.

`tools/ab_compare.py` verifies the control before any prose is read: every
difference between the arms' deterministic artifacts must map to one of those
three knobs. Measured at planning time: 59 authored documents per arm, **245
same-genre pairs**, across all seven genres that carry an outline pool.

**Persona enrichment is run once and shared, not run per arm.** Enrichment is
a model pass that writes persona prose into `foundation.json`, and every
authoring worker reads it. Run separately per arm it would differ by model
nondeterminism, so each arm's authors would be told different things about the
same people, and that difference would sit inside the measured gap. The two
arms' enrichment work orders were verified byte-identical before the pass ran
(the knobs do not reach it), so one deliverable was ingested into all arms and
`foundation.json` is byte-identical across them.

**A third arm: a control replicate.** Same recipe and the same seed as the
control, authored a second time. Its only difference from the control is the
model's own sampling, so the spread between control and replicate is a direct
estimate of authoring nondeterminism. This is what lets the turn say whether a
control-to-treatment gap is larger than run-to-run noise, and it supersedes
the limitation recorded below, which was written when the turn budgeted two
arms. Note what it does and does not bound: it is one replicate pair, so it
gives a noise *sample*, not a variance estimate with a confidence interval.

## The primary comparison, and why it is the weakest one

The structural axis (`orgsmith/review/structure.py`) over every one of the
245 same-genre pairs, shape and openers reported separately, control against
treatment.

**Expected direction:** treatment scores lower. **And a drop here is weak
evidence,** which is the most important sentence in this document. The
treatment arm deals each document one of 3-4 skeletons and ingest enforces
what each skeleton forbids, so a lower block-shape similarity is close to
mechanically guaranteed. Measuring it confirms the plumbing ran. It does not
show that anyone wrote differently.

So the primary comparison is reported first and trusted least. If it does
*not* drop, something is broken, and that is the one strong thing it can say.

## The comparisons that actually discriminate

**1. Same-skeleton pairs in the treatment arm, against all pairs in the
control arm.** Take the treatment pairs whose two documents were dealt the
*same* outline id. Those documents were asked for the same things in the same
order, exactly as every control-arm document of that genre was.

- If they score **materially lower** than the control's pairs, the corpus
  diverged for reasons the skeleton did not force. That is the outline work
  changing prose.
- If they score **about the same**, the honest reading is that the outline
  work relocated the convergence rather than reducing it: documents now
  converge in groups of the pool size instead of all together. That is a
  smaller win than "cross-document voice is fixed", and it must be reported
  as the smaller win.

**2. The lexical axis across arms.** Same-genre 4-gram Jaccard
(`review/metrics.py`), which no outline directly controls. A skeleton
constrains what a document contains, not which words it uses. A drop here is
therefore much less mechanically forced than a drop in shape, and is the
single most informative number this experiment produces.

**3. The board, on both arms, blind.** Six dimensions on the treatment arm;
the voice dimension on both arms with neither dispatch told which arm it read
or that a second arm exists. Recorded side by side.

## An interpretive caveat, recorded mid-run before any numbers existed

**Workers suppress convergence within their own batch, and that is not the
knob.** A batch hands one worker several documents at once, so unlike the
cross-batch case it *can* see its siblings. Observed live on the control arm:
one worker reported cutting shared six-grams among its own six documents from
34 to 3 by rewriting passages it noticed repeating, and another reported
deliberately giving two same-genre minutes different shapes. Both arms get
this for free, so it does not bias the comparison between them, but it does
mean neither arm's absolute variety is attributable to the outline work, and
a same-batch pair is not independent of a cross-batch pair.

Two consequences for reading the result. Same-genre pairs whose documents came
from one batch have already been de-duplicated by a human-like editor; pairs
spanning batches have not. And because batches are engagement-grouped rather
than random, that split is not evenly distributed across genres. If the
analysis wants a clean read, the comparison to trust is cross-batch pairs,
and the within-batch ones should be reported separately rather than pooled.
Recorded here, before the numbers exist, so the split cannot be chosen later
to suit them.

**And the premise behind that split turns out to be wrong, which is a larger
finding than this turn.** README.md states three times that a worker "never
sees a sibling" (lines 398, 422, 680) and that "nothing in the pipeline holds
two authored documents at once" (line 680). Both are false, and checkably so:

- `BATCH_SIZE = 6` (`orgsmith/authoring/contexts.py:31`). One worker is handed
  up to six documents and authors them together. Observed batch sizes on this
  run: 6, 6, 6, 1, 5, 6. Holding two authored documents at once is not an
  accident, it is the unit of work.
- Workers also read **across** batches. A control-arm worker reported reading
  an already-ingested reply from an earlier batch specifically to avoid
  repeating its section names, openings and closings. Nothing in
  `.claude/skills/forge-author/SKILL.md` grants or forbids this; the committed
  org's DocIR is simply on disk and readable.
- README.md line 638 already says so, listing "sibling documents" among what a
  batch reads when it accounts for token cost. The document contradicts itself
  about its own central mechanism.

This does not damage the comparison: both arms have the property equally. It
does change the diagnosis the comparison is testing. `BACKLOG.md`'s
`cross-document-voice` attributes per-genre convergence to authors who cannot
self-check because they never see a sibling. They can, within a batch always
and across batches sometimes, and they demonstrably do (one worker cut shared
six-grams among its own documents from 34 to 3). So convergence survives
*despite* partial sibling awareness, which makes it a harder problem than the
stated diagnosis, not an easier one.

Correcting README.md and the BACKLOG entry is docs work for this turn's close
(criterion ten). Recorded here first because it was found mid-run and the
finding is independent of how the numbers land.

## What this cannot settle, stated in advance

- **Whether the prose got better.** Both axes measure difference, not
  quality. A corpus can be more varied and worse.
- **`rf:voice-3`.** A single rhetorical move recurring across genres and
  authors, paraphrased each time, is not a pair, not a shape and not an
  n-gram. Neither axis reaches it and no keyless proxy will.
- **Run-to-run noise, now bounded rather than unbounded.** This limitation was
  written when the turn budgeted two arms, and the control replicate described
  above answers it in part: the control-to-replicate spread is a measured
  sample of authoring nondeterminism, and a control-to-treatment gap smaller
  than it means nothing. What the replicate still does not buy is a variance
  estimate. One replicate pair gives one number, not a distribution, so
  "larger than the noise sample we drew" is the strongest available claim and
  a delta must still not be quoted as an effect size.
- **A false-positive rate for the board.** Boarding both arms blind measures
  whether the board can *discriminate* two corpora. It does not measure how
  often the board manufactures a finding against prose that is fine, because
  neither arm is known-good prose. `board-negative-control` stays open.
- **Generalization past this recipe.** One org, one sector, one model, one
  seed.

## The null result is a result

If the discriminating comparisons come back flat, this turn's finding is that
`outline_variety` changes what documents contain without changing how they
read, and the M18 flagship should not carry it on that basis. That conclusion
gets written into the README with the same prominence as a positive one would
get. Nothing in the spec requires the outline work to have helped, and a turn
that saves the flagship from carrying an ineffective knob has paid for
itself.
