# Calderwood Partners LLC — Org Charter

```yaml
slug: calderwood-partners
name: Calderwood Partners LLC
seed: 20120411
org_type: management consulting
founded: 2007
domain: calderwoodpartners.com

headcount:
  Leadership: 1
  Advisory: 8
  Operations: 2

titles:
  Leadership: [Managing Principal]
  Advisory: [Principal, Senior Engagement Manager, Engagement Manager, Senior Consultant, Consultant, Senior Associate, Associate, Research Associate]
  Operations: [Director of Operations, Office Manager]

doc_culture:
  # The M12 pilot: larger than any fleet org and every M12 knob on. Recorded
  # from a docplan run: 215 documents (165 authored + 15 static workbooks + 35
  # derived noise) across 22 engagements, 15 fiscal years, 9 hires.
  target_docs: 215
  date_range: [2008-01-01, 2022-12-31]
  format_mix: {docx: 150, pdf: 40, xlsx: 15, pptx: 8, eml: 30}
  scanned_ratio: 0.3
  ocr_layer_rate: 0.5
  # Every meeting and thread lands on a business day (M12). A handful of
  # declared holidays across the span; weekends are always excluded.
  business_calendar:
    holidays: [2009-07-03, 2011-12-26, 2013-11-28, 2015-07-03, 2017-12-25, 2019-11-28, 2021-07-05]
  # A real share is mostly junk: exact duplicates and draft versions of
  # authored documents, derived with no model pass (M12).
  noise:
    duplicates: 15
    drafts: 20
  # The brief bans the template constructions the board found, and each
  # author draws a voice register (M12).
  voice_diversify: true

finance:
  # 7% growth against twelve net new seats over fifteen years. Measured:
  # 20.5% -> 13.9% net margin, a coherent professional-services band (the
  # coherence test's 40% ceiling is the thing a runaway margin would breach).
  base_revenue: 2600000
  growth_rate: 0.07
  expense_ratio: 0.80

engagements:
  count: 22
  # The engagement ledger is a representative sample of the book, not the
  # whole business (M12): the firm overview presents it as illustrative and
  # the financial summaries post the larger revenue.
  book_is_sample: true
  services: [Operating Model Redesign, Cost Transformation, Growth Strategy, Post-Merger Integration, Pricing Strategy, Supply Chain Review, Digital Operating Model, Organization Design, Market Entry Assessment, Working Capital Program, Procurement Transformation, Commercial Due Diligence, Sales Effectiveness, Footprint Rationalization, Shared Services Design, Customer Retention Program, Portfolio Strategy, Capital Allocation Review, Service Delivery Redesign, Channel Strategy, Back-Office Automation, Margin Recovery Program]

graph_targets:
  external_orgs: 12
  external_people: 14
  min_mentions_per_person: 2
  surname_collisions: 1
  nickname_aliases: 1

hard_cases:
  signature_page_facts: 1
  filename_dates: 1

acl_posture: departmental

roster_churn:
  departures: 2
  promotions: 3
  hires: 12
```

Calderwood Partners is a general management consulting firm founded in
2007, advising mid-market industrial and services companies on operating
model, cost, and growth. It is the largest organization OrgSmith ships and
the one built to exercise the full M12 stack at once: a business-day
calendar, an engagement book presented as a sample rather than the whole
firm, machine-derived noise, and an authoring brief that pushes against the
house voice.

Its documents are the ordinary paper trail of a consulting engagement.
Engagement letters set scope, fees, and terms. Kickoff memos frame the
first weeks of work. Working sessions produce minutes; the client executive
gets periodic status reports; a briefing deck lands partway through. Between
formal deliverables the team and the client exchange short emails about data
requests and scheduling, and a live thread runs a day or two between
replies.

The firm's own writing is plain and businesslike, and deliberately varied:
different hands write differently, engagements are described as
representative examples of a broader book rather than as the firm's entire
client list, and no two memos are built from the same template. Two staff
members share a surname and the writing treats it as unremarkable. The
overview is careful never to claim the documented engagements are the whole
business, because they are a sample of it.
