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
  # Recorded from a docplan run: 6 engagements, 11 fiscal years, 5 hires,
  # yielding 54 authored + 9 static, plus 13 derived noise files.
  # The email-leaning firm of the fleet: search runs on correspondence.
  target_docs: 63
  date_range: [2015-01-01, 2023-12-31]
  format_mix: {docx: 24, pdf: 10, xlsx: 8, pptx: 2, eml: 10}
  # M17: the exemplar demonstrates the headline surface. A newcomer is
  # told to read this org, and it used to leave every difficulty knob
  # off: no scans, no hard cases, no threads, an ACL under which
  # everyone read everything. Each knob below is proven on another
  # fleet org; what is new here is that they are on together.
  #
  # Signed agreements come back as scans: half the pdfs, and a third of
  # those keep a synthetic OCR layer, so the org carries BOTH hard
  # cases -- a scan you can extract badly and a scan you cannot extract
  # at all, whose true page text is archived as ground truth. Legacy
  # binaries stay off: a firm founded in 2013 producing pre-2007 .doc
  # files would be era-wrong.
  scanned_ratio: 0.5
  ocr_layer_rate: 0.34
  # M17: search runs on correspondence, so this is the org where mail
  # threads belong. Mundane internal traffic is what finally gives the
  # split curve a real distractor gap: documents that answer nothing.
  mail:
    business_hours: [8, 18]
    max_thread_depth: 4
    mundane_emails: 5
    attachments: 1
    distribution_lists: 1
    exempt_author_mentions: true
    exempt_recipient_mentions: true
  # M16: minuted sessions and engagement mail land on business days. The
  # board found this firm's Saturday 2016-05-28 and 2023-07-04 client
  # sessions; a declared holiday per year (plus the always-excluded
  # weekends) is why they no longer occur.
  business_calendar:
    holidays: [2015-05-25, 2016-07-04, 2017-09-04, 2018-11-22, 2019-12-25, 2020-05-25, 2021-07-05, 2022-09-05, 2023-07-04, 2023-11-23]
  # M16: the voice layer, fleet-wide. Each person carries a structured style
  # spec and the brief bans the template constructions the board named.
  style_specs: true
  voice_diversify: true
  # M16: the exemplar finally carries organizational noise -- a real share is
  # mostly junk. Derived with no model pass: exact copies, drafts, diverging
  # version chains, one misfile, a dead template, empty directories, and
  # decorated junk filenames.
  noise:
    duplicates: 2
    drafts: 2
    version_chains: 2
    misfiled: 1
    stale_templates: 1
    empty_dirs: 2
    filename_variety: true

finance:
  # 10% growth against five net new seats. Measured: 20.1% -> 22.4% net
  # margin (+2.3pp); with the growth knob off it posts 49.6%.
  base_revenue: 1250000
  growth_rate: 0.10
  expense_ratio: 0.77

engagements:
  count: 6
  # M16: the engagement ledger is a representative sample, not the whole book.
  # Closes the board's finding that the overview claimed five engagements were
  # "the whole business" while the financials post ~40x the fee total.
  book_is_sample: true
  services: [CFO Search, VP Engineering Search, Board Director Search, Head of Operations Search, General Counsel Search, Compensation Benchmarking]

graph_targets:
  external_orgs: 6
  external_people: 6
  min_mentions_per_person: 2
  surname_collisions: 1
  nickname_aliases: 1
  # M17: the nickname is the exemplar's published residual. The ledger
  # registered "Jim" to one James while the other James's persona claimed
  # it, so the firm overview called the wrong man Jim and no fact check
  # could see it. With this on, ingest rejects a persona that claims
  # somebody else's registered nickname and rejects authored prose that
  # uses one where the plan placed no mention; MENT-03 enforces the same
  # on committed state. The collision is now impossible by construction.
  alias_agreement: true

# M17: a fee that lives ONLY on the signature page of the engagement
# letter, and a meeting date that lives ONLY in the minutes filename.
# Both are proven on meridian-actuarial; the exemplar carries them so the
# org a newcomer reads actually poses the hard cases the README advertises.
hard_cases:
  signature_page_facts: 1
  filename_dates: 1

# M17: was `open`, under which 11 people read all 66 documents and the one
# departed person read none -- a visibility suite with nothing to discriminate.
# Departmental scopes reads to the matter team plus the CEO-equivalent, so
# "which documents may this person read?" becomes a real question.
acl_posture: departmental

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
