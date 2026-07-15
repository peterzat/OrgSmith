# SPEC

## Spec — 2026-07-15 — M4: ACL overlay and visibility evals

**Goal:** Give every generated org an access-control ground truth: a
deterministic ACL derived from the org's own structure (who may read which
share documents), rendered as a human-readable PERMISSIONS.md, enforced by
validator rules, and graded through a visibility eval suite so external
permission-aware systems (search with trimming, agents with per-user
credentials) can be scored offline against a knowable answer key.

### Acceptance Criteria

- [x] Charter gains an `acl_posture` knob (`open` default, `departmental` at
  minimum), documented in docs/RECIPE-FORMAT.md, additive: all three
  committed fixtures still load and validate clean without regeneration,
  and existing determinism and org-tier tests stay green (unchanged recipes
  regenerate byte-identical structure).
- [x] A deterministic, offline, keyless step derives `ledger/acl.json`
  (schema `orgsmith/acl@1`) as a pure function of committed artifacts: for
  every internal person, the exact set of share documents they may read.
  Under `open`, every internal person reads every manifest document. Under
  `departmental`: engagement-folder documents are readable only by that
  engagement's internal participants plus the CEO-equivalent, financial
  summaries only by the CEO-equivalent and the workbook's author, and
  firm-level documents by everyone. Re-derivation is byte-identical
  (tested).
- [x] `PERMISSIONS.md` is rendered into the share root alongside TOC.md for
  any org with an ACL ledger: it lists every person's access, is derived
  from `ledger/acl.json`, regenerates byte-identically, and the
  manifest/share consistency rule accepts it as a planned extra.
- [x] An ACL validator family (>= 3 rules) runs in `orgsmith validate`:
  every ACL principal resolves to a roster member, every manifest document
  is readable by at least one person, and the recorded grants match a
  recomputation from the charter's posture (so a hand-tampered acl.json or
  PERMISSIONS.md fails). Each rule fails on a deliberately corrupted copy
  (tested), and all skip visibly on orgs generated before the ACL overlay,
  which continue to validate clean.
- [x] `python -m orgsmith emit-evals <slug>` additionally writes
  `evals/visibility.jsonl` for orgs with an ACL ledger (one question per
  internal person: the exact set of readable share documents), skips it
  with a visible notice for orgs without one, re-emits byte-identically,
  and documents the answers contract in `evals/README.md`.
- [x] `python -m orgsmith score <slug> --suite visibility --answers <file>`:
  answers derived from ground truth score 100%; a deliberately wrong
  answers file scores below 100% with per-question attribution; a
  malformed answers file exits non-zero with an actionable message;
  scoring works from only the `evals/` directory plus an answers file
  outside the repo (all unit-tested).
- [x] A recipe with `acl_posture: departmental` and its generated org are
  committed under `recipes/` and `companies/`: the org validates clean
  including the ACL rules, PERMISSIONS.md is present in its share, at
  least one document is not readable by at least one internal person (the
  posture actually restricts), its visibility ground truth scores 100%,
  and the org tier covers all committed fixtures.
- [x] From a fresh checkout, `bin/test` passes all tiers offline with all
  committed fixtures.

### Context

- Consumed from the 2026-07-15 M3-close proposal (ACL + PERMISSIONS.md +
  visibility deferred from M3 as a pair). Shipped same-day as v1.3.0.
- Review hardening beyond the criteria: validate fails loudly (not skips)
  when a non-open posture has no acl.json, and MAN-01 whitelists
  PERMISSIONS.md only when an ACL ledger exists.

---
*Prior spec (2026-07-15): M3 hard-case planting and extraction evals; all
9 criteria met, shipped as v1.2.0.*

### Proposal (2026-07-15, M4 close)

**What happened.** M4 completed same-day and shipped as v1.3.0 (11
commits): the acl_posture knob, orgsmith/acl@1 derivation with a
PERMISSIONS.md twin in the share, a 3-rule ACL validator family, the
visibility eval suite on the shared doc-set contract, and the
bramblewood-legal fixture (departmental posture; grants from 11 docs down
to 3; visibility ground truth 5/5). The review cycle found and fixed two
WARNs, one surfaced by the chained security scan. Lessons:

- Both WARNs lived in the validator's trust model, not the data: acl_03
  rendered PERMISSIONS.md from the untrusted ledger (crash on tampering),
  and the grandfather skip keyed on file absence, so stripping acl.json
  from a restricted org silently disabled the ACL family. Grandfathering
  by absence needs a second signal (here, the charter posture) to tell
  "predates the feature" from "stripped by a tamperer".
- Emit-time conditionality (the README's visibility section exists only
  when the suite does) is what kept pre-M4 fixtures byte-identical on
  re-emission; "derive, don't store" keeps paying.
- The milestone rhythm is stable: knob, derivation, validator family,
  eval suite, fixture. Four fixtures now cover the default, ambiguity,
  hard-case, and ACL postures.

**Questions and directions for the next turn:**

- The fork in the roadmap: formats next (pptx, eml mail archives,
  scanned/OCR pdfs, legacy .doc/.xls/.ppt, which needs LibreOffice that
  `doctor` currently reports absent) or the six-org fleet (M7). A fleet
  turn fires the revisit criteria of `name-screen-validator` and
  `regenerate-dev-mini-mentions`, and could fold
  `multi-affiliation-in-docs` into its recipes.
- Fixture strategy: four committed fixtures and growing one per turn.
  Decide whether the fleet replaces them or extends them, and whether
  pre-M4 fixtures should ever gain ACL/mention artifacts via a migration
  verb instead of regeneration.
- The adversarial review board (roadmap item) remains unscheduled.

### Revisit candidates

- `multi-affiliation-in-docs`: its revisit criterion (M3 ambiguity tagging
  landed) fired at the M3 close and still holds; the fabric work would
  ride a fleet turn naturally.

<!-- SPEC_META: {"date":"2026-07-15","title":"M4: ACL overlay and visibility evals","criteria_total":8,"criteria_met":8} -->
