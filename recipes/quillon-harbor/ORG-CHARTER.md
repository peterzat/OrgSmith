# Quillon Harbor Advisors LLC — Org Charter

```yaml
slug: quillon-harbor
name: Quillon Harbor Advisors LLC
seed: 20260803
org_type: mergers and acquisitions advisory
founded: 2012
domain: quillonharbor.com

headcount:
  Leadership: 1
  Advisory: 9
  Operations: 2

titles:
  Leadership: [Managing Partner]
  Advisory: [Partner, Director, Vice President, Associate, Analyst]
  Operations: [Chief of Staff, Compliance Manager]

doc_culture:
  # Recorded from a docplan run: 8 engagements, 12 fiscal years, 8 hires,
  # yielding 59 authored + 10 static, plus 8 derived noise files.
  # Advisory per RECIPE-FORMAT.md; document supply is registry-derived.
  target_docs: 69
  date_range: [2014-01-01, 2023-12-31]
  format_mix: {docx: 45, pdf: 8, xlsx: 10, pptx: 6, eml: 0}
  # M17d: the tenth fleet org, and a LABELLED FOLLOW-UP to M17c's treatment
  # arm with a changed treatment. M17c generated this recipe three times to
  # answer one question (does the outline work change authored prose?) and
  # declined to commit any arm over a doubled-noun rendering defect and a
  # scope vocabulary that fit one engagement in eight. This version carries
  # the fixes for both, plus three more M17c findings (engagement starts off
  # the calendar, no partner on engagements, a firm with no 2020), and is
  # committed. Its numbers are NOT a second draw on M17c's pre-registration:
  # the treatment changed, so nothing here re-measures that experiment. The
  # M17c recipe as it ran is frozen at tests/fixtures/m17c-quillon-harbor/.
  #
  # The scoping notes below are M17c's and still describe this recipe: it
  # stays deliberately narrow where breadth would only add cost.
  #
  # No mail block. Only seven genres carry outline pools
  # (`registry.OUTLINES`: kickoff_memo, status_report, engagement_letter,
  # meeting_minutes, briefing_deck, onboarding_record, company_overview),
  # and no mail genre is among them. Threads would add authored documents,
  # authoring batches, and the published recipient-mention device while
  # contributing exactly zero documents to the measurement. Mail mechanics
  # are already demonstrated on three fleet orgs.
  #
  # No scans and no legacy binaries either: both act on the RENDERED
  # artifact, not on the authored text the structural axis reads, so they
  # would cost render time and buy the experiment nothing. Their absence
  # here is a scoping choice, not a gap -- five fleet orgs carry them.
  #
  # Noise stays on and is free: it is derived with no model pass, and
  # `metrics.compute` already excludes derived documents from the
  # structural pairs (a byte copy would score ~1.0 against its source for
  # reasons that have nothing to do with an author).
  noise:
    duplicates: 2
    drafts: 2
    version_chains: 1
    misfiled: 1
    stale_templates: 1
    empty_dirs: 2
    filename_variety: true
  # M16 fleet-standard voice layer. IDENTICAL IN BOTH ARMS: the experiment
  # varies the outline knobs only, so the per-person style layer has to be
  # on in the control too or the comparison measures two changes at once.
  style_specs: true
  voice_diversify: true
  business_calendar:
    holidays: [2014-11-27, 2015-05-25, 2016-07-04, 2017-09-04, 2018-11-22, 2019-12-25, 2020-05-25, 2021-07-05, 2022-09-05, 2023-11-23]
    # M17d: M17c had four of eight engagements start on a weekend or on
    # 2016-07-04, which the list above declares.
    engagement_starts: true
  # M17b's two outline-side knobs, on as in M17c's treatment arm.
  outline_variety: true
  client_facing_reports: true

finance:
  # An M&A boutique bills far more per head than the fleet's consultancies.
  # Tuned against the coherence check
  # (test_fleet_recipe_growth_headcount_and_span_describe_one_firm), which
  # caps the terminal net margin at 40%: this lands at 22.6% over a 17-24%
  # trail, inside the fleet's own 20.0-26.2% band rather than merely under
  # the ceiling.
  #
  # Measured while tuning, and worth recording because it is not obvious:
  # `expense_ratio` barely moves the terminal margin here. Since M8,
  # compensation tracks the roster rather than a share of fees, so at eight
  # hires the comp line dominates and 0.775/0.78/0.785 all returned 17.1%.
  # The live levers are `growth_rate` against `roster_churn.hires`. Sweeping
  # them: (0.075, 6) -> 25.3%, (0.085, 6) -> 31.5%, (0.095, 7) -> 34.5%,
  # (0.085, 8) -> 25.9%, (0.080, 8) -> 22.6%.
  base_revenue: 3200000
  growth_rate: 0.080
  expense_ratio: 0.78
  # M17d: a declared 2020. M17c's prose had analysts working from kitchen
  # tables in June 2020 beside a workbook whose Q2 was the year's best
  # quarter. Deal activity stalled in the spring and recovered by year end;
  # nobody flew. The trend underneath is untouched, so 2021 is back on it.
  era_shocks:
    - year: 2020
      revenue: 0.82
      travel: 0.3
      quarters: [1.05, 0.55, 0.85, 1.0]

engagements:
  count: 8
  book_is_sample: true
  services: [Sell-Side Advisory, Buy-Side Search, Recapitalization Advisory, Management Buyout Advisory, Carve-Out Advisory, Fairness Opinion, Growth Capital Raise, Strategic Alternatives Review]
  # M17d: Partners and the Managing Partner oversee the work. M17c's board
  # found no partner on any engagement document after 2015.
  oversight_titles: [Partner, Managing Partner]
  # M17b, then M17d. Every document that states a count cites one ledger
  # object, which is what stops a closing report inventing a different
  # number from the documents before it in its own folder.
  #
  # The recipe-wide profile now applies only to the Buy-Side Search; every
  # other service has its own (scope_by_service below), because M17c
  # planted acquisition-target vocabulary on all eight engagements (SCOPE-A).
  #
  # Every profile's unit is the UNIVERSE its funnel is drawn from, with a
  # range that floors above the funnel's top, so the nesting a reader infers
  # ("of the 180 on the list, 85 were contacted") is true by construction.
  # M17c's unit was a 9-16 shortlist beside a 60-110 screen, which no
  # nesting fits (SCOPE-D); briefs now also forbid relating the two.
  #
  # Plurality is the recipe author's job (RECIPE-FORMAT.md): every noun is
  # plural and every range floors well above 1. The narrowest funnel stage
  # stays at 2 or more: 60 * 0.40^3 = 3.8 here, and the worst case below
  # is the capital raise's 30 * 0.30^2 = 2.7.
  scope:
    unit: candidate companies
    unit_range: [140, 220]
    comparator: comparable transactions
    comparator_range: [22, 40]
    pipeline:
      - targets screened
      - targets contacted
      - NDAs executed
      - offers submitted
    pipeline_top_range: [60, 110]
    pipeline_retention: [0.40, 0.65]
  scope_by_service:
    Sell-Side Advisory:
      unit: prospective buyers
      unit_range: [120, 180]
      comparator: comparable transactions
      comparator_range: [22, 40]
      pipeline: [buyers contacted, NDAs executed, indications received, final bids]
      pipeline_top_range: [60, 110]
      pipeline_retention: [0.40, 0.65]
    Carve-Out Advisory:
      unit: prospective buyers
      unit_range: [90, 140]
      comparator: comparable carve-outs
      comparator_range: [12, 24]
      pipeline: [buyers contacted, NDAs executed, indications received, final bids]
      pipeline_top_range: [45, 80]
      pipeline_retention: [0.40, 0.65]
    Recapitalization Advisory:
      unit: financing sources
      unit_range: [30, 50]
      comparator: comparable financings
      comparator_range: [10, 20]
      pipeline: [lenders approached, term sheets received]
      pipeline_top_range: [12, 20]
      pipeline_retention: [0.25, 0.45]
    Management Buyout Advisory:
      unit: financing sources
      unit_range: [25, 40]
      comparator: comparable buyouts
      comparator_range: [10, 20]
      pipeline: [lenders approached, term sheets received]
      pipeline_top_range: [10, 18]
      pipeline_retention: [0.30, 0.50]
    Growth Capital Raise:
      unit: prospective investors
      unit_range: [70, 120]
      comparator: precedent raises
      comparator_range: [10, 20]
      pipeline: [investors approached, investors in diligence, term sheets received]
      pipeline_top_range: [30, 60]
      pipeline_retention: [0.30, 0.50]
    Strategic Alternatives Review:
      unit: strategic options
      unit_range: [4, 7]
      comparator: comparable companies
      comparator_range: [12, 25]
    # A fairness opinion is a valuation read on one transaction: no funnel,
    # no universe. M17c planted a four-stage acquisition funnel on one.
    Fairness Opinion: null

graph_targets:
  external_orgs: 8
  external_people: 8
  min_mentions_per_person: 2
  surname_collisions: 1
  nickname_aliases: 1
  alias_agreement: true

acl_posture: departmental

roster_churn:
  departures: 1
  promotions: 3
  hires: 8
```

Quillon Harbor Advisors is a lower-middle-market mergers and acquisitions
advisory founded in 2012. It runs sell-side processes for founder-owned
industrial and business-services companies, buy-side search programs for
private-equity platforms consolidating a sector, and the occasional
fairness opinion for a board that needs an independent read.

The firm's work is a funnel, and its documents are the record of that
funnel narrowing. A buy-side search opens with a universe of candidate
targets, screens it, contacts what survives, executes NDAs with the
willing, and ends with a handful of offers. Every one of those numbers
moves week to week, every document states some of them, and a document
that reports a stage the calendar says has not happened yet is simply
wrong. This is a firm whose prose is full of quantities.

Tone is precise and unhurried, with the particular carefulness of people
who write things a board will read and a lawyer may later quote. Partners
write to owners who are selling a company they founded, so the register is
warm without being familiar. Analysts write the underlying material and
their drafts read younger: more enumeration, more hedging, more numbers
per sentence. Deal teams are small and the same three or four names recur
across a mandate. Confidentiality is a habit rather than a policy: targets
are described by sector and revenue band in anything that circulates, and
named only where the document is already privileged.
