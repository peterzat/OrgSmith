# Eval splits: distractors, noise, and the degradation curve

`emit-evals` derives four nested corpus splits into `evals/splits.json`. A
split is the set of documents a retrieval system searches. The answer key
never changes across splits, so a system's recall stays perfect while its
precision falls as the corpus grows. Running one suite across all four splits
yields a degradation curve rather than a single headline number
(`BACKLOG.md`: `external-validity-program`).

The splits are derived, never stored: `evals/` is a derived artifact and is
re-emitted from the ledgers and manifest, so a frozen fixture gains splits
without regeneration.

## The four splits

| split | corpus | what it adds |
| --- | --- | --- |
| `core` | documents that answer some question | nothing; the minimal corpus |
| `distractors` | core + real authored documents that are not answers | genuine but irrelevant documents |
| `noise` | core + derived noise (duplicates and drafts) | machine-derived junk |
| `full` | the whole corpus | distractors and noise together |

They are four distinct corpora, not one cumulative chain, so a consumer can
attribute a precision drop to real distractors versus derived noise
separately: `distractors` and `noise` both extend `core`, and `full` is the
union of both.

## Distractor versus noise

The two categories are different kinds of hard, and the split names keep them
apart:

- A **distractor** is a real authored document that a real firm produced and
  that is simply not the answer to this question: another engagement's status
  report, a different year's financial summary, an unrelated onboarding
  record. It is deliberate, coherent, and on-topic enough to be plausibly
  retrieved. Distractors test whether a system can tell relevant from
  merely-similar.

- **Noise** is a derived document with no independent content: an exact
  byte-duplicate or a near-duplicate draft of an authored document, produced
  by the noise model with no model pass (`docs/RECIPE-FORMAT.md`,
  `doc_culture.noise`). Noise tests whether a system is fooled by redundancy:
  an exact duplicate collapses on a hash, but a draft near-duplicate does not,
  and a system that returns the draft alongside the final has lost precision.

Every noise document is labeled in the manifest with its source
(`authoring: derived`, `render_params.noise_of`), so authored and derived
words stay separable and the `core`/`distractors` splits can exclude noise
while the `noise`/`full` splits include it.

## Grading a split

```bash
python -m orgsmith score --suite retrieval --split noise \
    --answers my_answers.json --evals-dir evals/
```

Ground-truth answers score 100% on every split by construction, because every
expected answer lives in `core`, which every split contains. That is the
sanity check that the split machinery did not drop an answer; it is not a
claim about any system. A question whose expected answers are not all present
in a split is not gradable there and is skipped for that split.

`--split` does not apply to the graph suite, which grades entities and edges
rather than a document corpus.
