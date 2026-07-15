# ORG-CHARTER.md recipe format (draft)

A recipe is one directory under `recipes/<slug>/` containing `ORG-CHARTER.md`.
The file is Markdown: a fenced `yaml` block carries every structured field,
and the prose around it is the narrative brief (company character, history
hooks, tone). `python -m orgsmith charter <slug>` parses and validates the
recipe into `companies/<slug>-metadata/charter.json`.

Maintained alongside the schema (`orgsmith/schemas.py` is authoritative).
Fields marked *(reserved)* are defined by the architecture but not
consumed until their milestone lands.

## Structure

````markdown
# <Company Name> — Org Charter

```yaml
slug: dev-mini                # must match the recipe directory name
name: Pinebrook Advisory Group LLC
seed: 20260714                # master seed; all randomness derives from it
org_type: management consulting
founded: 2018
domain: pinebrookadvisory.com # email/web domain for the roster

headcount:                    # departments and staff counts (roster size)
  Leadership: 1               # exactly one CEO-equivalent enforced (ORG-01)
  Consulting: 3
  Operations: 1

doc_culture:
  target_docs: 13
  date_range: [2019-01-01, 2023-12-31]
  format_mix: {docx: 8, pdf: 3, xlsx: 2}   # exact counts for small orgs
  # format_mix may also include pptx (briefing decks) and eml (mail
  # messages), both default 0.
  # Scan/legacy transforms, all optional and default 0 (off):
  # scanned_ratio: 0.5      # fraction of pdfs rendered as degraded scans
  # ocr_layer_rate: 0.5     # fraction of scans with a synthetic OCR text
  #                         # layer (rest are image-only); requires
  #                         # scanned_ratio > 0
  # legacy_ratio: 0.4       # fraction of office docs converted to
  #                         # .doc/.xls/.ppt (needs LibreOffice at
  #                         # generation time; see `orgsmith doctor`).
  #                         # Validation stays pure Python: text
  #                         # obligations for converted binaries are
  #                         # checked against the verified authoring
  #                         # source (DocIR), so conversion fidelity of
  #                         # the binary itself is a documented residual
  #                         # risk; workbook values are read back via
  #                         # xlrd, containers and markers via olefile.

finance:
  base_revenue: 850000        # first full fiscal year, USD
  growth_rate: 0.12           # year-over-year, jittered per seed
  expense_ratio: 0.78

engagements:
  count: 3                    # client engagements the fabric stage creates
  # services: [Facility Condition Assessment, Commissioning Support]
  #   optional service-line names for engagement titles

graph_targets:
  external_orgs: 3
  external_people: 3
  # Ambiguity knobs, all optional and default 0 (off):
  # min_mentions_per_person: 2   # docs that must name each internal person
  # surname_collisions: 1        # staff pairs sharing a last name
  # nickname_aliases: 1          # people whose nickname appears in doc text
  # multi_affiliations: 1        # external people with a mid-history employer change

# hard_cases:                    # facts planted to be hard to find (optional, default 0)
#   signature_page_facts: 1      # fees appearing ONLY on the letter's signature page
#   filename_dates: 1            # meeting dates appearing ONLY in the minutes filename

# acl_posture: departmental      # read-access ground truth (optional, default open):
#                                # open = everyone reads everything;
#                                # departmental = engagement folders restricted to
#                                # their teams + the CEO-equivalent, finance to the
#                                # CEO-equivalent + workbook author
```

Prose after the YAML block is the narrative brief. It is carried into
charter.json verbatim and given to the model during enrichment and
authoring. Write it like a briefing note: what the firm does, who its
clients are, what its documents feel like.
````

## Reserved fields (later milestones)

- `doc_culture.naming_style`, `it_maturity` — era-appropriate naming and
  document culture (fleet milestone).
- `graph_targets.exec_multiplier`, edge targets — people-graph depth
  extensions.

## Rules

- Dict order is significant: the FIRST department listed in `headcount`
  holds the CEO-equivalent (its first title), and the largest department
  outside the CEO's staffs engagements.
- `slug` must equal the directory name; lowercase, hyphens only.
- `date_range` must start no earlier than `founded`.
- `format_mix` values must sum to `target_docs`.
- Same seed + same recipe = same org structure (ids, names, tree, numbers).
  Only model-authored prose may vary between runs.

## Pre-commit checklist

Before committing a generated org as a fixture:

- Run `python -m orgsmith validate <slug>`; it must pass with SKIP lines
  only for knobs the recipe leaves off.
- Run `python -m orgsmith validate <slug> --only NAME-01` to confirm the
  name screen passes. The screen also gates the charter and scaffold
  stages, so a collision normally fails long before this point. The
  committed real-firm list (`orgsmith/data/real_firms.txt`) is a screen,
  not a guarantee: also eyeball the org name, external org names, and
  roster for real-world collisions the list does not cover.
- If NAME-01 or a generation gate fires, rename the org in the recipe or
  bump the seed. Never edit `foundation.json` or any ledger by hand.
