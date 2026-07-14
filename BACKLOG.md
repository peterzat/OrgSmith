# Backlog

Durable register of considered proposals that were deferred, scoped out, or
rejected. Read before drafting a new SPEC.md; swept at turn close.

### regenerate-dev-mini-mentions
- **One-line description** of the proposal: regenerate the committed
  `companies/dev-mini` org so it carries mention ground truth
  (mention_map.json, manifest mentions) instead of being grandfathered
  past the MENT/GRAPH validator rules.
- **Why deferred:** the manifest is immutable and the authored prose is
  keyed to it; regeneration means re-authoring all 11 batchable documents,
  which M2 scoped out to protect the v1 fixture.
- **Revisit criteria:** a migration verb lands, or the M7 fleet turn
  regenerates all committed orgs anyway.
- **Origin:** spec 2026-07-14 (M2).

### multi-affiliation-in-docs
- **One-line description** of the proposal: have multi-affiliation external
  people appear in rendered documents under BOTH employers (era-appropriate
  per doc date), not only in ledger/graph.json edges, so works_at
  reconciliation-by-recency is exercised by the corpus itself.
- **Why deferred:** requires affiliation-aware participant selection in
  fabric across engagement windows; M2 scoped multi-affiliation to ground
  truth records.
- **Revisit criteria:** a recipe plants engagements on both sides of an
  affiliation boundary (fleet recipes), or M3 ambiguity tagging lands.
- **Origin:** spec 2026-07-14 (M2).

### name-screen-validator
- **One-line description** of the proposal: a name-screen check (validator
  rule plus review-checklist item) that flags generated company and person
  names colliding with real firms before an org is committed.
- **Why deferred:** the plan schedules it alongside fleet recipe authoring;
  needs a screening heuristic or source list designed first.
- **Revisit criteria:** before authoring the six-recipe fleet (M7), or the
  first real-name collision report against a committed fixture.
- **Origin:** plan we-re-making-a-plan-virtual-sedgewick.

### mention-ambiguity-tags
- **One-line description** of the proposal: tag mention_map records with
  planted-ambiguity classes (surname-collision, nickname-only, cross-org
  duplicate) so eval suites can score disambiguation specifically rather
  than only retrieval.
- **Why deferred:** failure-mode tagging is M3 hard-case engineering's
  contract (same schema change wave as key_facts.location policies).
- **Revisit criteria:** the M3 hard-case turn opens the manifest/mention
  schema for location policies.
- **Origin:** spec 2026-07-14 (M2).
