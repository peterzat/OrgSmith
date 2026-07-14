# ORG-CHARTER.md recipe format (draft)

A recipe is one directory under `recipes/<slug>/` containing `ORG-CHARTER.md`.
The file is Markdown: a fenced `yaml` block carries every structured field,
and the prose around it is the narrative brief (company character, history
hooks, tone). `python -m orgsmith charter <slug>` parses and validates the
recipe into `companies/<slug>-metadata/charter.json`.

Status: draft. Fields marked *(reserved)* are defined by the architecture
but not consumed until their milestone lands.

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

finance:
  base_revenue: 850000        # first full fiscal year, USD
  growth_rate: 0.12           # year-over-year, jittered per seed
  expense_ratio: 0.78

engagements:
  count: 3                    # client engagements the fabric stage creates

graph_targets:                # (partially reserved; M1 uses org/people counts)
  external_orgs: 3
  external_people: 3
```

Prose after the YAML block is the narrative brief. It is carried into
charter.json verbatim and given to the model during enrichment and
authoring. Write it like a briefing note: what the firm does, who its
clients are, what its documents feel like.
````

## Reserved fields (later milestones)

- `doc_culture.scanned_ratio`, `legacy_ratio`, `ocr_layer_rate`,
  `naming_style`, `it_maturity` — scan/legacy pipeline (M5).
- `graph_targets.min_mentions_per_person`, `exec_multiplier`, edge targets,
  ambiguity knobs — people-graph depth (M2/M3).
- `acl_posture`, `hard_cases` — ACL overlay and hard-case planting (M3).

## Rules

- Dict order is significant: the FIRST department listed in `headcount`
  holds the CEO-equivalent (its first title), and the largest department
  outside the CEO's staffs engagements.
- `slug` must equal the directory name; lowercase, hyphens only.
- `date_range` must start no earlier than `founded`.
- `format_mix` values must sum to `target_docs`.
- Same seed + same recipe = same org structure (ids, names, tree, numbers).
  Only model-authored prose may vary between runs.
