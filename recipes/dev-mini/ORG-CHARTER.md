# Pinebrook Advisory Group LLC — Org Charter

```yaml
slug: dev-mini
name: Pinebrook Advisory Group LLC
seed: 20260714
org_type: management consulting
founded: 2018
domain: pinebrookadvisory.com

headcount:
  Leadership: 1
  Consulting: 3
  Operations: 1

titles:
  Leadership: [Managing Partner]
  Consulting: [Principal Consultant, Senior Consultant, Analyst]
  Operations: [Office Manager]

doc_culture:
  # target_docs and the docx/pdf/xlsx buckets are advisory as of M9: the
  # genre registry derives the real supply from the firm's engagements,
  # fiscal years, and hires. These record what that comes to for this recipe
  # (23 documents). pptx/eml stay load-bearing (this firm produces neither).
  target_docs: 23
  date_range: [2019-01-01, 2023-12-31]
  format_mix: {docx: 15, pdf: 3, xlsx: 5}
  # Persona voice v2 (M15). The tracer is the voice proof bed: each person
  # carries a structured style spec in the ledgers and every brief carries
  # per-author guidance derived from it. Noise stays off deliberately -- a
  # regression oracle should exercise the bare pipeline, and the noise kinds
  # are proven on ashcombe-advisory instead.
  style_specs: true

finance:
  # Retuned in M15 under the wave carve-out. The old 0.12 against a roster
  # frozen at five seats compounded to a 43.1% terminal net margin, which no
  # professional-services firm posts (BACKLOG dev-mini-margin-incoherent).
  # Fees now grow at a rate one added seat can carry: FY2019-2023 lands at
  # 19-23%, flat rather than climbing, inside the fleet's own 20-26% band.
  base_revenue: 850000
  growth_rate: 0.07
  expense_ratio: 0.80

roster_churn:
  # The seat that makes the growth coherent: a firm billing more every year
  # hires somebody.
  hires: 1

engagements:
  count: 3

graph_targets:
  external_orgs: 3
  min_mentions_per_person: 1
  external_people: 3
```

Pinebrook Advisory Group is a small management consultancy serving
mid-market operating companies, five people at the start of the window and
six by the end. The firm takes on a handful of engagements a year:
operational reviews, pricing studies, and post-acquisition integration
support. Its documents are lean and practical: engagement letters on firm
letterhead, kickoff memos, meeting minutes that name every attendee, and
status reports written for a client executive who skims. The Managing
Partner signs everything that leaves the building. Tone is plain American
business English, first names inside the firm, full names and titles when a
client is on the page.
