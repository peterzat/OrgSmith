# Meridian Actuarial Advisors LLC — Org Charter

```yaml
slug: meridian-actuarial
name: Meridian Actuarial Advisors LLC
seed: 20160518
org_type: actuarial consulting
founded: 2014
domain: meridianactuarial.com

headcount:
  Leadership: 1
  Consulting: 4
  Operations: 1

titles:
  Leadership: [Managing Actuary]
  Consulting: [Consulting Actuary, Senior Analyst, Actuarial Analyst, Actuarial Associate]
  Operations: [Practice Manager]

doc_culture:
  # M17e carve-out (approved 2026-10-13): this org is regenerated once to
  # close the mail-mention device, adopting the M17d and M17e knobs below.
  # Recorded from a docplan run: 6 engagements, 9 fiscal years, 5 hires.
  # M16 raises eml above the engagement count so the data-and-assumptions
  # back-and-forth with the client's staff runs as real threads.
  target_docs: 62
  date_range: [2016-01-01, 2024-12-31]
  format_mix: {docx: 26, pdf: 10, xlsx: 9, pptx: 2, eml: 22}
  # M16: valuation review calls and engagement mail land on business days.
  business_calendar:
    holidays: [2016-05-30, 2017-07-04, 2018-09-03, 2019-11-28, 2020-12-25, 2021-05-31, 2022-07-04, 2023-09-04, 2024-11-28]
    # M17d: engagement starts land on business days too.
    engagement_starts: true
  # M16: a mail demonstrator for the fleet. Short emails about data files and
  # assumptions run as threads; a little mundane internal traffic fills the
  # mailbox, and its authors are exempt from naming themselves in the body.
  mail:
    business_hours: [8, 18]
    max_thread_depth: 5
    mundane_emails: 4
    distribution_lists: 1
    exempt_author_mentions: true
    # M17e: both halves of the mail-mention device closed. A recipient is
    # named by the To/Cc header, and a list broadcast names no one.
    exempt_recipient_mentions: true
    broadcasts_address_the_list: true
  # M16: the voice layer, fleet-wide.
  style_specs: true
  voice_diversify: true
  # M17e: an overview names finished engagements only; live work is confidential.
  overview_cites_finished_work: true

finance:
  # 10% growth against five net new seats: the fastest grower in the fleet,
  # and the one that most needs the roster to keep up. Measured: 26.7% ->
  # 26.2% net margin (-0.5pp); with the growth knob off it posts 51.4%.
  base_revenue: 1400000
  growth_rate: 0.10
  expense_ratio: 0.75
  # M17e (M17d knob): a declared 2020 for an actuarial consultancy: valuations are statutory and kept coming, a spring slowdown aside, and site visits stopped.
  era_shocks:
    - year: 2020
      revenue: 0.95
      travel: 0.25
      quarters: [1.05, 0.85, 0.95, 1.0]

engagements:
  count: 6
  # M17d: a senior sits on every engagement one can cover.
  oversight_titles: [Consulting Actuary, Managing Actuary]
  # M16: the engagement ledger is a representative sample, not the whole book.
  book_is_sample: true
  services: [Pension Valuation, Reserve Adequacy Review, Experience Study, Retiree Medical Valuation, Funding Policy Study, Reinsurance Pricing Review]

graph_targets:
  external_orgs: 6
  external_people: 6
  min_mentions_per_person: 2
  surname_collisions: 1

hard_cases:
  signature_page_facts: 1
  filename_dates: 1

acl_posture: departmental

roster_churn:
  departures: 1
  promotions: 2
  hires: 5
```

Meridian Actuarial Advisors is a consulting actuarial practice founded in
2014, serving public pension boards, a mid-sized life insurer, and two
multiemployer benefit funds. It is the fastest-growing firm in this
fleet: it starts at six seats and opens five more over nine years,
because that is what a book of work compounding at ten percent a year
actually requires.

Its work carries the discipline of a regulated opinion: precise about
scope, data reliance, and the standards a piece of work is performed
under, plain and undecorated, and careful to separate what the data show
from what was assumed. Between formal deliverables, the actuaries and the
client's staff exchange short emails about data files and assumptions.

Tone is careful and heavily qualified, because an actuary who overstates
a number is exposed. Writing distinguishes measurement from judgment
explicitly: what the data show, what was assumed, and what the actuary
concludes are three different paragraphs. Two staff members share a
surname, and documents that name both should not disambiguate them for
the reader; the firm's own writing treats it as unremarkable, which is
the point.
