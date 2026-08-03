# M17c evidence standard, fixed 2026-08-03 before either arm was authored

What would count as M17b's outline work having changed authored prose, what
would count as it not having, and what this measurement cannot settle either
way. Written and committed **before** either arm was authored, so the
conclusion cannot be chosen after the numbers exist. SPEC.md (2026-08-03)
criterion two; verifiable from git order.

Nothing in this document gates anything. No number below is a threshold, no
test tier reads any of it, and no validator rule derives from it. It is a
statement of what the authors will accept as an answer, recorded in advance.

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

## What this cannot settle, stated in advance

- **Whether the prose got better.** Both axes measure difference, not
  quality. A corpus can be more varied and worse.
- **`rf:voice-3`.** A single rhetorical move recurring across genres and
  authors, paraphrased each time, is not a pair, not a shape and not an
  n-gram. Neither axis reaches it and no keyless proxy will.
- **Run-to-run noise, and this is the sharpest limitation.** One run per arm.
  Authoring is model-nondeterministic, and **nothing here estimates how much
  two runs of the *same* arm would differ.** Without a same-arm replicate,
  any difference between the arms is confounded with ordinary sampling
  variation, and no observed gap can be called larger than noise. A third run
  (a control replicate, ~10 further batches) is what would close this; it is
  not budgeted in this turn, and every number this turn reports is therefore
  a single-sample comparison. Read accordingly, and do not quote a delta as
  an effect size.
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
