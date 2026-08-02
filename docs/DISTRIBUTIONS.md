# Distributional dashboard

Derived artifact: re-emit with `python -m orgsmith distributions`. Never edit by hand. Deterministic corpus distributions for every committed org; the mean-words and span-years aggregates are doc- and org-weighted respectively. Nothing here gates anything.

| org | people | span (yrs) | docs | derived | .eml | max thread depth | weekend | docs / person-yr | mean words |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ashcombe-advisory | 16 | 8.0 | 104 | 17 | 45 | 8 | 12% | 0.81 | 367 |
| brackenridge-civil | 9 | 9.0 | 40 | 0 | 0 | 0 | 30% | 0.49 | 641 |
| calderwood-partners | 25 | 15.0 | 218 | 35 | 38 | 1 | 17% | 0.58 | 593 |
| dev-mini | 7 | 5.0 | 23 | 0 | 0 | 0 | 35% | 0.66 | 745 |
| hollowell-ip | 10 | 8.0 | 64 | 0 | 22 | 5 | 16% | 0.80 | 481 |
| meridian-actuarial | 12 | 9.0 | 72 | 0 | 26 | 5 | 14% | 0.67 | 460 |
| northgate-staffing | 12 | 9.0 | 76 | 13 | 16 | 4 | 24% | 0.70 | 571 |
| saltmarsh-environmental | 10 | 9.0 | 40 | 0 | 0 | 0 | 18% | 0.44 | 659 |
| verdant-health | 7 | 6.0 | 31 | 0 | 0 | 0 | 19% | 0.74 | 697 |
| **fleet** | 108 | 8.7 | 668 | 65 | 147 | 8 | 18% | 0.64 | 547 |

## Realism wave: before / after (M15 frozen fleet → M16 regenerated)

The `before` column is the M15-committed baseline (`WAVE_BASELINE_M15`, git 82a23b4), captured before any org was regenerated; `after` is derived live from the current fleet. The wave turned on a business-day calendar (which pulls weekend-dated meetings and mail down), real mail threads on the demonstrators (which raises `.eml` and, being short, lowers mean words), and the noise suite on the exemplar and the two large orgs (which raises `derived`). Fee/revenue prose posture also moved but is not a distribution: every regenerated overview now declares its engagement book a sample, so documented fees reading as ~1-3% of revenue no longer contradict the prose. Per-author voice ranges are per-org, in each `GENERATION-REPORT.md`; `cross-document-voice` stays the standing hard problem, measured never gated.

| org | weekend | .eml | derived (noise) | mean words |
| --- | --- | ---: | ---: | ---: |
| ashcombe-advisory | 11% → 12% | 42 → 45 | 0 → 17 | 365 → 367 |
| brackenridge-civil | 40% → 30% | 0 → 0 | 0 → 0 | 699 → 641 |
| calderwood-partners | 17% → 17% | 38 → 38 | 35 → 35 | 589 → 593 |
| dev-mini | 36% → 35% | 0 → 0 | 0 → 0 | 717 → 745 |
| hollowell-ip | 27% → 16% | 3 → 22 | 0 → 0 | 691 → 481 |
| meridian-actuarial | 22% → 14% | 3 → 26 | 0 → 0 | 675 → 460 |
| northgate-staffing | 36% → 24% | 5 → 16 | 0 → 13 | 662 → 571 |
| saltmarsh-environmental | 25% → 18% | 0 → 0 | 0 → 0 | 725 → 659 |
| verdant-health | 29% → 19% | 0 → 0 | 0 → 0 | 728 → 697 |
| **fleet** | 22% → 18% | 91 → 147 | 35 → 65 | 606 → 547 |

## Reference lines (non-calibrated)

Order-of-magnitude context restated from the README's "Where that sits against a real firm", NOT measured target distributions: no reference population has been sampled, and `external-validity-program` (BACKLOG.md) stays open. Read the gap, not a score.

- **Files.** A real ten-person professional-services firm accumulates thousands to hundreds of thousands of files over a decade, most of them junk; docs/person-year here sits two to four orders of magnitude below that, deliberately (specimens, not samples; docs/SCALE.md).
- **Email.** Ten people sending even 20 messages a working day is ~400,000 messages over eight years; every corpus here is document-dominant by design, and `.eml` share plus thread depth measure mechanics, not volume.
- **Noise.** Most real files are duplicates, drafts, and dead paper. The derived column is each org's deliberate, labeled fraction of that; zero means every committed document is on purpose.
- **Weekends.** Uniformly drawn dates land on a weekend ~28.5% of the time. An org that declares a business calendar should sit well below that for genres asserting attendance; one that declares none records its chance-level fraction here.
