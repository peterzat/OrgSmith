# Northgate Talent Partners LLC — Org Charter

```yaml
slug: northgate-staffing
name: Northgate Talent Partners LLC
seed: 20150210
org_type: executive search
founded: 2013
domain: northgatetalent.com

headcount:
  Leadership: 1
  Search: 4
  Operations: 1

titles:
  Leadership: [Managing Director]
  Search: [Principal, Senior Consultant, Research Consultant, Research Associate]
  Operations: [Office Manager]

doc_culture:
  # Recorded from a docplan run: 6 engagements, 9 fiscal years, 5 hires.
  # The email-leaning firm of the fleet: search runs on correspondence.
  target_docs: 53
  date_range: [2015-01-01, 2023-12-31]
  format_mix: {docx: 24, pdf: 10, xlsx: 8, pptx: 2, eml: 5}

finance:
  # 10% growth against five net new seats. Measured: 20.1% -> 22.4% net
  # margin (+2.3pp); with the growth knob off it posts 49.6%.
  base_revenue: 1250000
  growth_rate: 0.10
  expense_ratio: 0.77

engagements:
  count: 6
  services: [CFO Search, VP Engineering Search, Board Director Search, Head of Operations Search, General Counsel Search, Compensation Benchmarking]

graph_targets:
  external_orgs: 6
  external_people: 6
  min_mentions_per_person: 2
  surname_collisions: 1
  nickname_aliases: 1

acl_posture: open

roster_churn:
  departures: 1
  promotions: 2
  hires: 5
```

Northgate Talent Partners is a retained executive search firm founded in
2013, placing senior operators and board directors at mid-market
companies and one regional health system. Search is a correspondence
business: the firm's real work product is a long thread of candidate
conversations, and the formal documents are the scaffolding around it.

That shape is the point of this recipe. More of the share is email than
anywhere else in the fleet: engagement confirmations, candidate slate
updates, scheduling, and the careful note that goes out when a finalist
withdraws. The formal artifacts are there too, and they matter: a
retained search agreement with its fee schedule, a position specification
per search, a candidate slate summary, and the quarterly numbers.

Tone is warm but professional, and more conversational than the rest of
this fleet, because a search consultant is managing two anxious parties
at once. Consultants use first names with clients they have known for
years and full names when writing about a candidate. Discretion is
constant: candidates are described by their current role rather than
named in anything that circulates widely. Two people on the roster share
a surname, and one goes by a nickname in internal notes.
