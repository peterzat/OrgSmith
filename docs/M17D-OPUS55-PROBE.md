# M17d Opus 5.5 probe: evidence standard, fixed 2026-10-13

What would count as Claude Opus 5.5 having changed authored prose against
Claude Opus 5, what would count as it not having, and what this measurement
cannot settle. Written and committed **before** the first probe work order is
dispatched, so the conclusion cannot be chosen after the numbers exist.
SPEC.md (2026-10-13) criterion one; verifiable from git order against the
probe arm's reply-file timestamps.

Nothing here gates. No number below is a threshold, no test tier reads this
file, and no validator rule derives from it.

## Why this probe exists

The fleet is frozen and eight of its nine orgs were authored on
`claude-opus-4-8[1m]`, the ninth (`northgate-staffing`) on `claude-opus-5`.
Whether a model-swap regeneration buys anything is a question about the
model, and the project has measured the model axis only across tiers
(`docs/MODEL-AB.md`: Opus against Haiku, then against Sonnet), never from one
Opus generation to the next. A regeneration is expensive and spends published
evidence, so it should follow a measurement rather than precede one.

## The setup

M17c left three authored arms of one recipe, `quillon-harbor`, in
`scratch/arms/`. Two of them, `alpha` and `gamma`, are the same control
configuration authored twice by `claude-opus-5` at `xhigh`, and the spread
between them is a measured noise floor. This probe adds a fourth arm,
**`delta`**: the same control configuration authored by `claude-opus-5-5` at
`xhigh`.

The control is exact by construction and checked rather than assumed:

- `delta` runs from a git worktree pinned at this document's commit, whose
  `orgsmith/` code is identical to `aef75a9`, the code `alpha` and `gamma`
  were authored and measured on. This turn's code changes land in the main
  tree and cannot reach the probe.
- The same control recipe (`scratch/arms/alpha/recipes/quillon-harbor`), the
  same seed, and the same persona enrichment: `alpha`'s enrichment work
  order is compared byte for byte against `delta`'s, and `alpha`'s ingested
  deliverable is ingested into `delta`, so `foundation.json` is
  byte-identical across all three arms.
- `tools/ab_compare.py --control alpha --treatment delta` must report zero
  differences in the deterministic artifacts.
- Every `delta` authoring work order is compared byte for byte against
  `alpha`'s same-numbered order. A difference is enumerated in the write-up,
  not assumed away.
- Same dispatch procedure as M17c: `/forge` Step 3, a K = 4 window, fresh
  context per batch, author-only workers, serial ingest by the orchestrator.

The one variable is the model that answered the work orders. Effort is held
at `xhigh`, which is what the M17c arms recorded.

## The baselines, recorded now

Measured 2026-10-13 from the files on disk, before any `delta` prose exists:

| measure | alpha | gamma | spread (the floor) |
| --- | ---: | ---: | ---: |
| structural combined, mean over 245 same-genre pairs | 0.3721 | 0.3803 | 0.0082 |
| structural shape, mean | 0.5483 | 0.5886 | 0.0403 |
| structural openers, mean | 0.1959 | 0.1720 | 0.0239 |
| lexical 4-gram Jaccard, same-genre mean | 0.0073 | 0.0077 | 0.0004 |
| unowned numbers (`tools/probe_numbers.py`), total | 0 | 18 | 18 |
| authored words, total | 39,763 | 39,761 | 2 |
| docs outside 75%-150% of brief | 0 | 0 | 0 |

The unowned-number counter was written for this probe and calibrated on the
existing arms before being pinned: it reproduces M17c's AIRLOCK-01 table
exactly (`gamma` d0014 9, d0015 3, d0016 5, d0017 1; `alpha` none).

## What counts as a change

Each axis is read as the gap between `delta` and the mean of `alpha` and
`gamma`, against the `alpha`/`gamma` spread on the same axis.

- **Structural (combined, shape, openers) and lexical.** A gap of **three
  times the spread or more** on an axis counts as Opus 5.5 having moved that
  axis. Lower is less similar. Under three times, the axis did not move
  measurably. Three, not M17c's seven-point-seven, because this is a
  decision rule written in advance rather than a ratio reported after the
  fact; it is stated here so it cannot be chosen later.
- **Unowned numbers.** The floor is a range, not a spread: two identical
  runs gave 0 and 18. A `delta` count inside **[0, 18]** is uninformative.
  Above 18 is evidence that Opus 5.5 invents more quantities; only a count
  of 0 together with a zero on the M17c treatment-arm comparison would be
  evidence of less, and this probe cannot show that.
- **Words against brief.** Moved if `delta`'s total lies outside
  39,761-39,763 by more than 5%, or if any `delta` document lands outside
  75%-150% of its brief.
- **The blind voice verdict.** Two `cross_document_voice` reviewers, fresh
  contexts, both on `claude-opus-5-5` at `xhigh`, one reading a copy of
  `alpha` and one a copy of `delta` under neutral paths, neither told that
  an experiment, a second arm, or a model difference exists. Each returns
  its findings, a 0-10 variety score, and a yes or no to "does one person
  appear to have written everything?". The categorical answers (blocker or
  none; yes or no) are the sturdier signal; the score is reported but
  carries little weight at n = 1. Re-reading `alpha` with a new reviewer
  also gives a second reading of a corpus M17c already boarded, which is
  reported beside M17c's.

## What the result licenses

- **Regeneration for the model alone is supported** only if at least one
  similarity axis moves by three times its spread **in the less-similar
  direction**, the unowned-number count does not rise above 18, words stay
  on brief, and the blind reviewer does not rate `delta` worse than `alpha`
  on the categorical answers.
- **It is not supported** if no similarity axis moves, or if the only
  movement is toward more similarity. That is a result, and it means the
  fleet's prose is not the thing a new model would fix.
- Anything in between is reported as mixed, axis by axis, with no
  headline.

## What this cannot settle

- **Opus 4.8.** Eight fleet orgs were authored on `claude-opus-4-8[1m]`. This
  compares Opus 5 against Opus 5.5. A gain here makes a gain over 4.8
  plausible; it does not measure one.
- **Quality.** Every axis measures difference, not goodness. Less similar is
  the direction the board has asked for, but nothing here shows the prose is
  better, and the blind verdict is one reader per arm.
- **Variance.** One `delta` run is one sample. A gap that clears three
  spreads clears one replicate pair's spread, not a confidence interval.
- **Reviewer affinity.** The blind reviewers run on the same model as
  `delta`'s author. A reviewer that reads its own model's prose more kindly
  would bias the verdict toward `delta`, and nothing here can separate that
  from a real difference. The similarity axes are immune to it; the verdict
  is not.
- **Cost.** Recorded per batch from the harness's own usage figures, for the
  record. Not compared, because the M17c arms' usage was not captured.

## The graders, hashed at registration

The measurements are run from the pinned worktree. These are the sha256 of
every grading script this standard names, at this commit; the write-up
re-verifies them in the worktree at measurement time.

| file | sha256 |
| --- | --- |
| `tools/ab_compare.py` | `8e5bc8db2d09e9e4da2d2627c07136c10e2556fd3a9d1bf2cfaad8c176f5c8d2` |
| `tools/probe_numbers.py` | `7a1a59a360bdc2606f42fff7783a33be95f3c58cfa0b4b2779e3f2be175b81de` |
| `orgsmith/review/structure.py` | `f10e7adfd771cacf098cd263dcf9ebb3c0bc74b8bd1ce3a6274f4c817790152e` |
| `orgsmith/review/metrics.py` | `4e08f5ba4bd8559cdae222400e02a2e8fc551f995aa440b156b252746821a657` |
| `orgsmith/review/corpus.py` | `4bca87768fb022c20d1651df0a8499db9e4b0b00bd4dc0c7162871c0f7ca5c7d` |
| `orgsmith/review/report.py` | `d6992183833e493a8e82392c096a3d060fb902317fad3d2f4530101582e16f13` |

## Amendment log

Kept because a pre-registration that is silently edited is not one. No
amendment may change what counts as evidence.

- (none yet)
