# Retrieval baselines

Two keyless retrievers answering every committed org's retrieval suite,
graded by the ordinary scorer. Derived, never stored: regenerate with
`python -m orgsmith baseline --fleet`.

**These are reference points, not targets.** They exist so a consumer can
tell a genuinely hard question from a structurally easy one. Nothing here
gates, and no generator change should ever be made to move these numbers:
that is the Goodhart failure this project keeps out of `bin/test` by
construction.

- **filename-only**: lexical overlap between the question and the file's
  name, ignoring its contents entirely.
- **bm25**: Okapi BM25 (k1=1.5, b=0.75) over extracted document text,
  hand-rolled, ASCII tokenizer `[a-z0-9]+` over casefolded text, ties broken
  by ascending path, top 10 documents returned.

Each split is its own corpus: document frequency and average length are
computed within the split, so a retriever searching `core` has not seen the
distractors. Ground-truth answers score 100% on all of them by construction.

Strict is the exact-set headline. A dumb retriever returning ten documents
almost never matches a required set exactly, so read the ranked columns:
they are where a lexical floor is actually visible.


## Where reading the body pays off

BM25 leads filename matching on nDCG@10 on **7 of 9** committed orgs: `ashcombe-advisory`, `calderwood-partners`, `dev-mini`, `hollowell-ip`, `meridian-actuarial`, `northgate-staffing`, `verdant-health`.

It falls behind on `brackenridge-civil`, `saltmarsh-environmental`. Those are the scan-heavy orgs, where a synthetic OCR layer degrades exactly the document text BM25 reads while leaving the filenames intact. That is a property of the corpus worth knowing, not a defect in either retriever.

## ashcombe-advisory

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 44 | 2.3% | 37.7% | 54.7% | 0.563 | 0.493 |
| filename-only | distractors | 44 | 2.3% | 37.7% | 54.7% | 0.563 | 0.493 |
| filename-only | noise | 44 | 0.0% | 36.7% | 49.5% | 0.539 | 0.458 |
| filename-only | full | 44 | 0.0% | 36.7% | 49.5% | 0.539 | 0.458 |
| bm25 | core | 44 | 2.3% | 56.7% | 69.4% | 0.787 | 0.734 |
| bm25 | distractors | 44 | 2.3% | 56.7% | 68.2% | 0.787 | 0.723 |
| bm25 | noise | 44 | 0.0% | 54.5% | 64.5% | 0.756 | 0.670 |
| bm25 | full | 44 | 0.0% | 54.5% | 62.7% | 0.756 | 0.658 |

## brackenridge-civil

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 34 | 2.9% | 71.0% | 71.6% | 0.853 | 0.729 |
| filename-only | distractors | 34 | 2.9% | 71.0% | 71.6% | 0.853 | 0.729 |
| filename-only | noise | 34 | 2.9% | 71.0% | 71.6% | 0.853 | 0.729 |
| filename-only | full | 34 | 2.9% | 71.0% | 71.6% | 0.853 | 0.729 |
| bm25 | core | 34 | 2.9% | 61.9% | 69.7% | 0.735 | 0.706 |
| bm25 | distractors | 34 | 2.9% | 61.9% | 69.7% | 0.735 | 0.706 |
| bm25 | noise | 34 | 2.9% | 61.9% | 69.7% | 0.735 | 0.706 |
| bm25 | full | 34 | 2.9% | 61.9% | 69.7% | 0.735 | 0.706 |

## calderwood-partners

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 108 | 0.9% | 49.7% | 65.9% | 0.679 | 0.541 |
| filename-only | distractors | 108 | 0.9% | 49.7% | 65.9% | 0.679 | 0.541 |
| filename-only | noise | 108 | 0.9% | 45.4% | 63.6% | 0.626 | 0.507 |
| filename-only | full | 108 | 0.9% | 45.4% | 63.6% | 0.626 | 0.507 |
| bm25 | core | 108 | 0.0% | 63.1% | 71.5% | 0.802 | 0.746 |
| bm25 | distractors | 108 | 0.0% | 63.1% | 71.5% | 0.802 | 0.746 |
| bm25 | noise | 108 | 0.0% | 60.3% | 69.4% | 0.787 | 0.716 |
| bm25 | full | 108 | 0.0% | 60.3% | 69.4% | 0.787 | 0.716 |

## dev-mini

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 22 | 9.1% | 68.7% | 71.8% | 0.818 | 0.729 |
| filename-only | distractors | 22 | 9.1% | 68.7% | 71.8% | 0.818 | 0.729 |
| filename-only | noise | 22 | 9.1% | 68.7% | 71.8% | 0.818 | 0.729 |
| filename-only | full | 22 | 9.1% | 68.7% | 71.8% | 0.818 | 0.729 |
| bm25 | core | 22 | 0.0% | 64.7% | 74.4% | 0.773 | 0.748 |
| bm25 | distractors | 22 | 0.0% | 64.7% | 74.4% | 0.773 | 0.748 |
| bm25 | noise | 22 | 0.0% | 64.7% | 74.4% | 0.773 | 0.748 |
| bm25 | full | 22 | 0.0% | 64.7% | 74.4% | 0.773 | 0.748 |

## hollowell-ip

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 35 | 2.9% | 46.0% | 70.7% | 0.615 | 0.583 |
| filename-only | distractors | 35 | 2.9% | 46.0% | 70.7% | 0.615 | 0.583 |
| filename-only | noise | 35 | 2.9% | 46.0% | 70.7% | 0.615 | 0.583 |
| filename-only | full | 35 | 2.9% | 46.0% | 70.7% | 0.615 | 0.583 |
| bm25 | core | 35 | 0.0% | 55.4% | 64.6% | 0.750 | 0.690 |
| bm25 | distractors | 35 | 0.0% | 55.1% | 64.7% | 0.750 | 0.691 |
| bm25 | noise | 35 | 0.0% | 55.4% | 64.6% | 0.750 | 0.690 |
| bm25 | full | 35 | 0.0% | 55.1% | 64.7% | 0.750 | 0.691 |

## meridian-actuarial

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 40 | 2.5% | 47.2% | 72.1% | 0.613 | 0.600 |
| filename-only | distractors | 40 | 2.5% | 47.2% | 72.1% | 0.613 | 0.600 |
| filename-only | noise | 40 | 2.5% | 47.2% | 72.1% | 0.613 | 0.600 |
| filename-only | full | 40 | 2.5% | 47.2% | 72.1% | 0.613 | 0.600 |
| bm25 | core | 40 | 2.5% | 53.2% | 66.7% | 0.724 | 0.700 |
| bm25 | distractors | 40 | 2.5% | 53.2% | 66.3% | 0.723 | 0.696 |
| bm25 | noise | 40 | 2.5% | 53.2% | 66.7% | 0.724 | 0.700 |
| bm25 | full | 40 | 2.5% | 53.2% | 66.3% | 0.723 | 0.696 |

## northgate-staffing

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 41 | 0.0% | 65.2% | 68.8% | 0.691 | 0.627 |
| filename-only | distractors | 41 | 0.0% | 65.2% | 68.8% | 0.691 | 0.627 |
| filename-only | noise | 41 | 0.0% | 60.6% | 66.3% | 0.653 | 0.595 |
| filename-only | full | 41 | 0.0% | 60.6% | 66.3% | 0.653 | 0.595 |
| bm25 | core | 41 | 0.0% | 56.7% | 70.7% | 0.713 | 0.693 |
| bm25 | distractors | 41 | 0.0% | 56.7% | 70.7% | 0.713 | 0.693 |
| bm25 | noise | 41 | 0.0% | 50.7% | 67.5% | 0.642 | 0.623 |
| bm25 | full | 41 | 0.0% | 50.7% | 67.5% | 0.642 | 0.623 |

## saltmarsh-environmental

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 35 | 2.9% | 65.6% | 68.6% | 0.814 | 0.679 |
| filename-only | distractors | 35 | 2.9% | 65.6% | 68.6% | 0.814 | 0.679 |
| filename-only | noise | 35 | 2.9% | 65.6% | 68.6% | 0.814 | 0.679 |
| filename-only | full | 35 | 2.9% | 65.6% | 68.6% | 0.814 | 0.679 |
| bm25 | core | 35 | 2.9% | 57.9% | 70.8% | 0.676 | 0.676 |
| bm25 | distractors | 35 | 2.9% | 57.9% | 70.8% | 0.676 | 0.676 |
| bm25 | noise | 35 | 2.9% | 57.9% | 70.8% | 0.676 | 0.676 |
| bm25 | full | 35 | 2.9% | 57.9% | 70.8% | 0.676 | 0.676 |

## verdant-health

| retriever | split | questions | strict | R@5 | R@10 | MRR | nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| filename-only | core | 26 | 3.9% | 64.3% | 72.1% | 0.750 | 0.671 |
| filename-only | distractors | 26 | 3.9% | 64.3% | 72.1% | 0.750 | 0.671 |
| filename-only | noise | 26 | 3.9% | 64.3% | 72.1% | 0.750 | 0.671 |
| filename-only | full | 26 | 3.9% | 64.3% | 72.1% | 0.750 | 0.671 |
| bm25 | core | 26 | 0.0% | 56.7% | 70.5% | 0.699 | 0.682 |
| bm25 | distractors | 26 | 0.0% | 56.7% | 70.5% | 0.699 | 0.682 |
| bm25 | noise | 26 | 0.0% | 56.7% | 70.5% | 0.699 | 0.682 |
| bm25 | full | 26 | 0.0% | 56.7% | 70.5% | 0.699 | 0.682 |

