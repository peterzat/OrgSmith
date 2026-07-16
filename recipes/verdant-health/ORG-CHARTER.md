# Verdant Health Advisory LLC — Org Charter

```yaml
slug: verdant-health
name: Verdant Health Advisory LLC
seed: 20200714
org_type: healthcare consulting
founded: 2018
domain: verdanthealthadvisory.com

headcount:
  Leadership: 1
  Advisory: 3
  Operations: 1

titles:
  Leadership: [Managing Partner]
  Advisory: [Principal, Senior Consultant, Analyst]
  Operations: [Engagement Manager]

doc_culture:
  # Recorded from a docplan run: 4 engagements, 6 fiscal years, 1 hire.
  # The smallest of the new fleet, and deliberately so: the band is 30-60
  # and something has to sit at the bottom of it.
  target_docs: 31
  date_range: [2020-01-01, 2025-12-31]
  format_mix: {docx: 17, pdf: 7, xlsx: 6, pptx: 2}
  # Consents come back from the health system as image-only scans: no OCR
  # layer at all, so an extractor gets nothing without doing the work.
  scanned_ratio: 0.5
  ocr_layer_rate: 0.0

finance:
  # 6% growth against one net new seat over six years. Measured: 24.5% ->
  # 23.6% net margin (-0.9pp); with the growth knob off it posts 32.1%.
  # The shortest span drifts least, which is why it needs the fewest hires.
  base_revenue: 1080000
  growth_rate: 0.06
  expense_ratio: 0.75

engagements:
  count: 4
  services: [Service Line Assessment, Physician Compensation Review, Ambulatory Network Study, Revenue Cycle Diagnostic]

graph_targets:
  external_orgs: 4
  external_people: 4
  min_mentions_per_person: 2
  multi_affiliations: 1
  affiliations_in_docs: true

acl_posture: open

roster_churn:
  departures: 1
  promotions: 1
  hires: 1
```

Verdant Health Advisory is a five-person healthcare consultancy founded
in 2018, working for a regional health system, an independent physician
group, and an ambulatory surgery joint venture. Its engagements are the
unglamorous middle of healthcare operations: which service lines earn
their keep, whether physician compensation survives a fair-market-value
review, and where the revenue cycle leaks.

The share is modern and mostly clean, with one deliberate exception. The
health system's contracting office prints, signs, and scans everything,
and its scanner produces images with no text layer whatsoever. Those
consents and executed statements of work are in the share as pictures of
documents, which is precisely the case an extraction pipeline cannot
bluff its way through.

Tone is measured and compliance-aware. Consultants write for an audience
that includes a general counsel, so nothing asserts a conclusion the
analysis does not support, and fair-market-value language is used
carefully rather than decoratively. Findings lead; recommendations
follow and are labeled as such. Staff use first names internally and full
names and titles with the client. One client-side contact moved from the
physician group to the health system partway through the relationship,
and documents should place her at the right employer for their date.
