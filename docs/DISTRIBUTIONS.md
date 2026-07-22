# Distributional dashboard

Derived artifact: re-emit with `python -m orgsmith distributions`. Never edit by hand. Deterministic corpus distributions for every committed org; the mean-words and span-years aggregates are doc- and org-weighted respectively. Nothing here gates anything.

| org | people | span (yrs) | docs | derived | .eml | max thread depth | weekend | docs / person-yr | mean words |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ashcombe-advisory | 16 | 8.0 | 104 | 17 | 45 | 8 | 12% | 0.81 | 365 |
| brackenridge-civil | 9 | 9.0 | 40 | 0 | 0 | 0 | 40% | 0.49 | 699 |
| calderwood-partners | 25 | 15.0 | 218 | 35 | 38 | 1 | 17% | 0.58 | 589 |
| dev-mini | 7 | 5.0 | 23 | 0 | 0 | 0 | 35% | 0.66 | 745 |
| hollowell-ip | 10 | 8.0 | 45 | 0 | 3 | 1 | 27% | 0.56 | 691 |
| meridian-actuarial | 12 | 9.0 | 49 | 0 | 3 | 1 | 22% | 0.45 | 675 |
| northgate-staffing | 12 | 9.0 | 53 | 0 | 5 | 1 | 36% | 0.49 | 662 |
| saltmarsh-environmental | 10 | 9.0 | 40 | 0 | 0 | 0 | 25% | 0.44 | 725 |
| verdant-health | 7 | 6.0 | 31 | 0 | 0 | 0 | 29% | 0.74 | 728 |
| **fleet** | 108 | 8.7 | 603 | 52 | 94 | 8 | 22% | 0.58 | 601 |

## Reference lines (non-calibrated)

Order-of-magnitude context restated from the README's "Where that sits against a real firm", NOT measured target distributions: no reference population has been sampled, and `external-validity-program` (BACKLOG.md) stays open. Read the gap, not a score.

- **Files.** A real ten-person professional-services firm accumulates thousands to hundreds of thousands of files over a decade, most of them junk; docs/person-year here sits two to four orders of magnitude below that, deliberately (specimens, not samples; docs/SCALE.md).
- **Email.** Ten people sending even 20 messages a working day is ~400,000 messages over eight years; every corpus here is document-dominant by design, and `.eml` share plus thread depth measure mechanics, not volume.
- **Noise.** Most real files are duplicates, drafts, and dead paper. The derived column is each org's deliberate, labeled fraction of that; zero means every committed document is on purpose.
- **Weekends.** Uniformly drawn dates land on a weekend ~28.5% of the time. An org that declares a business calendar should sit well below that for genres asserting attendance; one that declares none records its chance-level fraction here.
