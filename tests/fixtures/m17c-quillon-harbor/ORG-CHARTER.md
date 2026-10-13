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
  # M17c: this org exists to answer ONE question -- does the outline work
  # change authored prose? -- so the recipe is deliberately narrow where
  # breadth would only add cost.
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
  # --- THE TWO TREATMENT KNOBS, and the whole point of this recipe -------
  # M17b, both default off. `tools/ab_control.py` derives the control arm's
  # charter by stripping exactly these and `engagements.scope` below; a test
  # asserts the two charters differ in those three fields and nowhere else.
  # Do not add a knob here without deciding which arm it belongs to.
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

engagements:
  count: 8
  book_is_sample: true
  services: [Sell-Side Advisory, Buy-Side Search, Recapitalization Advisory, Management Buyout Advisory, Carve-Out Advisory, Fairness Opinion, Growth Capital Raise, Strategic Alternatives Review]
  # --- THE THIRD TREATMENT KNOB ----------------------------------------
  # M17b, default absent. A buy-side search is measured in targets and in a
  # funnel that narrows, which is exactly the quantity M17's board caught a
  # closing report inventing differently from the five documents before it
  # in its own folder. With this declared, every document that states a
  # count cites one ledger object.
  #
  # Plurality is the recipe author's job (RECIPE-FORMAT.md): every noun
  # below is plural and every range floors well above 1, so no surface can
  # render "1 acquisition targets". The funnel's narrowest stage is
  # 60 * 0.40^3 = 3 at worst.
  scope:
    unit: acquisition targets
    unit_range: [9, 16]
    comparator: comparable transactions
    comparator_range: [22, 40]
    pipeline:
      - targets screened
      - targets contacted
      - NDAs executed
      - offers submitted
    pipeline_top_range: [60, 110]
    pipeline_retention: [0.40, 0.65]

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
