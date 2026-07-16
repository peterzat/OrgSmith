# Generation report: dev-mini

Derived artifact: re-emit with `python -m orgsmith report dev-mini`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

22 documents planned; 17 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-4-8[1m] | max |
| wo:author:0002 | claude-opus-4-8[1m] | max |
| wo:author:0003 | claude-opus-4-8[1m] | max |
| wo:author:0004 | claude-opus-4-8[1m] | max |
| wo:foundation:0001 | claude-opus-4-8[1m] | max |

## Length against brief

17 authored documents, 12196 words, mean 717.

Every document is within 75%-150% of the words its brief asked for.

## Same-genre similarity

Same-genre pairs at or above 0.15 4-gram Jaccard. High overlap is a measurement, not a verdict: real firms reuse templates. The board judges which of these read as reuse.

| doc a | doc b | genre | jaccard |
| --- | --- | --- | ---: |
| d:0002 | d:0008 | engagement_letter | 0.355 |
| d:0008 | d:0015 | engagement_letter | 0.3103 |
| d:0002 | d:0015 | engagement_letter | 0.2808 |

## Review board

No board findings ingested. Run `/forge-review dev-mini` to dispatch the review board; the metrics above stand on their own without it.
