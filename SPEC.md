# SPEC

## Spec — 2026-07-15 — M4: ACL overlay and visibility evals

**Goal:** Give every generated org an access-control ground truth: a
deterministic ACL derived from the org's own structure (who may read which
share documents), rendered as a human-readable PERMISSIONS.md, enforced by
validator rules, and graded through a visibility eval suite so external
permission-aware systems (search with trimming, agents with per-user
credentials) can be scored offline against a knowable answer key.

### Acceptance Criteria

- [ ] Charter gains an `acl_posture` knob (`open` default, `departmental` at
  minimum), documented in docs/RECIPE-FORMAT.md, additive: all three
  committed fixtures still load and validate clean without regeneration,
  and existing determinism and org-tier tests stay green (unchanged recipes
  regenerate byte-identical structure).
- [ ] A deterministic, offline, keyless step derives `ledger/acl.json`
  (schema `orgsmith/acl@1`) as a pure function of committed artifacts: for
  every internal person, the exact set of share documents they may read.
  Under `open`, every internal person reads every manifest document. Under
  `departmental`: engagement-folder documents are readable only by that
  engagement's internal participants plus the CEO-equivalent, financial
  summaries only by the CEO-equivalent and the workbook's author, and
  firm-level documents by everyone. Re-derivation is byte-identical
  (tested).
- [ ] `PERMISSIONS.md` is rendered into the share root alongside TOC.md for
  any org with an ACL ledger: it lists every person's access, is derived
  from `ledger/acl.json`, regenerates byte-identically, and the
  manifest/share consistency rule accepts it as a planned extra.
- [ ] An ACL validator family (>= 3 rules) runs in `orgsmith validate`:
  every ACL principal resolves to a roster member, every manifest document
  is readable by at least one person, and the recorded grants match a
  recomputation from the charter's posture (so a hand-tampered acl.json or
  PERMISSIONS.md fails). Each rule fails on a deliberately corrupted copy
  (tested), and all skip visibly on orgs generated before the ACL overlay,
  which continue to validate clean.
- [ ] `python -m orgsmith emit-evals <slug>` additionally writes
  `evals/visibility.jsonl` for orgs with an ACL ledger (one question per
  internal person: the exact set of readable share documents), skips it
  with a visible notice for orgs without one, re-emits byte-identically,
  and documents the answers contract in `evals/README.md`.
- [ ] `python -m orgsmith score <slug> --suite visibility --answers <file>`:
  answers derived from ground truth score 100%; a deliberately wrong
  answers file scores below 100% with per-question attribution; a
  malformed answers file exits non-zero with an actionable message;
  scoring works from only the `evals/` directory plus an answers file
  outside the repo (all unit-tested).
- [ ] A recipe with `acl_posture: departmental` and its generated org are
  committed under `recipes/` and `companies/`: the org validates clean
  including the ACL rules, PERMISSIONS.md is present in its share, at
  least one document is not readable by at least one internal person (the
  posture actually restricts), its visibility ground truth scores 100%,
  and the org tier covers all committed fixtures.
- [ ] From a fresh checkout, `bin/test` passes all tiers offline with all
  committed fixtures.

### Context

- Consumed from the 2026-07-15 M3-close proposal: ACL overlay,
  PERMISSIONS.md, and the visibility suite were deferred from M3 as a pair
  because visibility scoring needs the ACL to exist. v1.2.0 shipped M3
  (location policies, hard-case planting, extraction suite, ambiguity
  tags, quillbrook-appraisal fixture).
- The three committed fixtures are frozen (ledgers, manifests, charters,
  prose, rendered shares): they gain NO acl.json and NO PERMISSIONS.md
  this turn. Grandfather them with the visible-skip pattern that worked
  for mention ground truth in M2 and location policies in M3. Only the
  new fixture carries the departmental posture; `evals/` directories of
  old fixtures may be re-emitted only if their bytes are unchanged by
  this turn's changes (visibility emission must skip, not write, for
  them).
- Scope decisions this turn: `multi-affiliation-in-docs` stays in BACKLOG
  (not revived); the visibility suite grades internal people only,
  external people carry no grants; ACL covers read access only, no
  write/deny semantics until a real consumer needs them.
- Additive discipline: `orgsmith/acl@1` is a new schema in
  `orgsmith/schemas.py` (the keystone file); `acl_posture` must be
  optional-with-default on `orgsmith/charter@1`; new derivation logic must
  consume no RNG so unchanged recipes regenerate byte-identically.
- The ACL derivation and the visibility suite are oracle machinery: pure
  functions of committed files, no LLM in any automated path, and `score`
  stays decoupled (bare `evals/` directory plus an answers file). The M3
  lesson binds: bugs live in the proxy and the instructions, so validator
  recomputation checks and corruption tests in both directions are the
  spec, not decoration.
- New-fixture authoring runs through the airlock via /forge with forked
  workers; the firm name must not resemble a real firm (name-screen
  validator stays deferred in BACKLOG). If the ACL step becomes a
  pipeline stage, the org-tier completeness test must keep passing for
  the three pre-M4 fixtures whose state.json predates it.
- House practices: small committable increments with tests in the same
  increment; suite green before starting; no push or remote mutation
  without explicit user instruction.

---
*Prior spec (2026-07-14): M3 hard-case planting and extraction evals; all 9
criteria met, shipped as v1.2.0.*

<!-- SPEC_META: {"date":"2026-07-15","title":"M4: ACL overlay and visibility evals","criteria_total":8,"criteria_met":0} -->
