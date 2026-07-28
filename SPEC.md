# SPEC

## Spec — 2026-07-28 — Fit-and-finish: close and harden BYO, tidy the M16 aftermath, prune the backlog

**Goal:** Put a bow on the current body of work before any M17 flagship effort.
Close bring-your-own-token authoring (without the live-key smoke), apply the
useful hardening to the BYO path, finish the reachable M16 loose ends and make
the docs and exemplar narrative reflect current reality, and prune the backlog
of resolved entries. No committed fixture is regenerated and no new capability
line is begun; this turn only tightens and tidies what already shipped.

### Acceptance Criteria

- [x] **BYO `base_url` scheme allowlist (closes the BYO security NOTE).** Before
  any request, the driver refuses a `base_url` whose scheme is not `http` or
  `https`: `call_provider` returns `None` without opening a connection, and
  `--check` reports the provider as not-ready with a non-zero exit. Unit-tested
  for both an allowed scheme and a rejected one (for example an empty scheme or
  `file:`/`ftp:`). SECURITY.md's `base_url` NOTE is marked resolved.

- [x] **Authoring-guidance drift guard.** A short-tier test keeps the driver's
  writing-quality system prompt (`drivers/forge_external.py`) in sync with the
  authoring guidance in `.claude/skills/forge-author/SKILL.md`, failing if the
  two diverge, so the documented MVP drift risk cannot land silently. Either a
  single shared asset both read, or a pinned-in-sync assertion in the spirit of
  `test_board_dimensions_match_the_schema`.

- [x] **Backlog pruned of resolved entries.** BACKLOG.md drops the five entries
  closed by M16 (`recipe-brief-leaks-genre-spec`,
  `engagement-ledger-reads-as-whole-book`, `docplan-has-no-business-day-calendar`,
  `reporting-line-drift`, `mundane-email-author-self-names`) and the one closed
  by the BYO turn (`provider-neutral-authoring-driver`). Every still-open entry
  is retained verbatim (`board-negative-control`, `cross-document-voice`,
  `generator-fingerprinting`, `external-validity-program`, `event-simulation`,
  `state-json-mixes-execution-and-provenance`, `recipe-coherence-test-has-no-floor`,
  `concurrent-workers-share-one-scratchpad`, `packaging-and-archival`,
  `mail-audience-internal-vs-external`).

- [x] **Docs reconciled to current reality, exemplar included.** The project
  `CLAUDE.md` known-residual paragraph no longer claims the `hollowell-ip`
  `To:/Cc:` body banner is unfixed (it was fixed in v2.1.1); only the still-open
  full-name-in-body device remains, correctly scoped as needing a future
  regeneration. The README presents BYO as a first-class capability consistent
  with the exemplar-driven narrative, and no stale pre-fix claim about the
  exemplar or the mail banner survives anywhere in tree.

- [x] **README reads cleanly for a newcomer, in house voice.** The README is
  revised for first-time flow and readability (a newcomer can follow what
  OrgSmith is, how the airlock works, and how to run it without backtracking),
  and obvious AI-generated language is removed to match house style: em-dashes
  replaced with commas, periods, or parentheses; no AI-voice tics ("It's
  important to note," "Let's," "Great question"); short declarative sentences.
  Every factual claim, number, and code reference is preserved unchanged (a
  voice-and-flow edit, not a content rewrite), and the short-tier guards stay
  green (no hardcoded effort floor, pre-rename name absent). zat.env's README is
  the reference for the target voice.

- [x] **`ManifestEntry.path` constrained at the boundary (closes the standing
  security NOTE).** An absolute or `..`-bearing manifest path is refused at load
  time (`load_manifest`, or an equivalent boundary check), closing the
  path-traversal NOTE carried since before M16. Every committed manifest still
  loads and the frozen fleet re-derives byte-identical, because every committed
  path is share-relative. SECURITY.md updated. (Implemented as a boundary check,
  not a schema-id change, so `schemas/` and the schema pin are untouched.)

- [x] **No regeneration, no M17; suite green.** No committed org's ledgers,
  manifest, or authored/rendered prose is regenerated; `tests/test_org_regen.py`
  `PINNED = SLUGS` stays byte-identical; no flagship, event-simulation,
  validation-program, or other new-capability work is begun. Full `bin/test`
  (short + unit + org + flagship) passes, keyless and offline.

### Context

- **Adopted from the 2026-07-28 proposal**, the "close BYO / put a bow on it"
  direction the user chose over the M17 flagship. The proposal carried no
  backlog-sweep ops, so backlog pruning is an explicit criterion here rather than
  a mechanical sweep.

- **Frozen-fixture rule is in force; no carve-out this turn.** Committed ledgers,
  manifests, and authored/rendered prose are frozen (`CLAUDE.md`, restored as of
  M16). Every criterion here is reachable without regeneration: hardening and
  tests touch `drivers/` and `tests/`, the `ManifestEntry.path` check is a
  load-time boundary guard that all committed paths already satisfy, and the doc
  and backlog edits are prose. Any fix that would move committed bytes (the mail
  full-name-in-body device, the hollowell list-marker double-bullet) stays
  deferred to a future, user-approved regeneration turn.

- **Explicitly out of scope (the "down-the-road body of work").** The M17
  window-defeating flagship; `event-simulation`; `external-validity-program`;
  `generator-fingerprinting` defenses; the mail-audience mixed internal/external
  capability; and the BYO parallel window (K>1) and a MODEL-AB round using the
  driver. These stay in the backlog.

- **BYO closed at 7/8 by decision.** The live end-to-end run against a real
  provider key (BYO criterion 5) was intentionally not done; the documented
  manual scratch-root smoke in `docs/BYO-AUTHORING.md` remains the way to
  exercise it later. This turn treats BYO as shipped and only hardens it.

- **House practices (zat.env).** Verification over prompting; small committable
  increments with tests in the same increment; run the relevant tier after each
  change; precision over recall in review; a fit-and-finish turn still avoids
  bundling unrelated concerns into one commit. Do not reword or reorder criteria;
  check off only when verified.

---
*Prior spec (2026-07-28): bring-your-own-token authoring driver shipped
(out-of-airlock `drivers/` package, off by default); 7/8 criteria met, the live
end-to-end run against a real key intentionally skipped.*

<!-- SPEC_META: {"date":"2026-07-28","title":"Fit-and-finish: close and harden BYO, tidy the M16 aftermath, prune the backlog","criteria_total":7,"criteria_met":7} -->
