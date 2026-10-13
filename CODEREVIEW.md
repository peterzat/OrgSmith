# CODEREVIEW

## Review — 2026-10-13 (commit: 316e183) — the d:0044 claim and the alias pass

**Review scope:** Light review. The push range (`origin/main..316e183`) is one
commit touching two plain documentation files, `BACKLOG.md` and
`docs/RECIPE-FORMAT.md`; `codereview-marker surface` lists no files. No test
run, security scan, external reviewer, built-in review or fix loop, per the
light tier. Both claims were checked against hollowell's committed
`mention_map.json`, `manifest.jsonl` and `acl.json` at `61abcbd` and HEAD,
against `plan_mentions` (`orgsmith/docplan/planner.py:908-990`), and against
every committed org's aliases.

**Summary:** The commit answers the prior review's two documentation NOTEs.
Both new claims are accurate: Matthew Parrish's `d:0044` mention and its ACL
denial are identical at `61abcbd`, and all five committed aliases sit in
meeting minutes. Two residual imprecisions in RECIPE-FORMAT, both NOTEs.
0 BLOCK, 0 WARN.

**External reviewers:**
Skipped (light review).

**Built-in review:**
Skipped (light review).

### Findings

**[NOTE] `docs/RECIPE-FORMAT.md:156-157` — "The recipient draw still runs,
so no other mail note moves" is still unqualified, and the new sentence at
line 166-167 says the nickname pass "may be another mail note".**
  Evidence: the two sentences describe different mechanisms. The first is
  about the `mrand` stream (`planner.py:746-767`: the draw runs before
  `participants = []`, so later notes draw the same recipients). The second
  is about the alias re-host. Each is true in its own scope, but read in
  sequence in one comment they contradict as written.
  Suggested fix: "so the draw moves no other mail note", or append "(the
  nickname pass below aside)".
  Medium confidence that a reader trips on it; documentation only.

**[NOTE] `docs/RECIPE-FORMAT.md:164-169` — the alias can also move without
its first host losing a mention, through the top-up.**
  Evidence: `_TOP_UP_GENRES` includes `meeting_minutes`
  (`planner.py:76-81`), and the alias host sort prefers minutes
  (`planner.py:978-980`). With `min_mentions_per_person` on, a mail knob that
  drops any of an aliased person's mentions can push them below the floor; if
  the top-up then adds them to meeting minutes, the alias leaves its earlier
  host, which is a mail note when the person had no minutes mention. The new
  sentence states a sufficient condition and does not claim to be
  exhaustive, so it is not wrong. Not observed: the fleet's five aliases
  (`ashcombe-advisory` `d:0023`, `calderwood-partners` `d:0040`,
  `hollowell-ip` `d:0033`, `northgate-staffing` `d:0007`, `quillon-harbor`
  `d:0015`) are all on `meeting_minutes`.
  Suggested fix: none needed unless the caveat is meant to be complete; then
  "an aliased person whose first host changes".
  Low confidence it matters; documentation only.

**Carried from the prior entry, still present at HEAD (files unchanged by
this commit):**

- **[NOTE] `tests/test_unit_mail_broadcast.py:67-72`:** the equality on every
  other internal note runs on `dev-mini`, which has no nickname aliases, so
  it does not exercise the alias path.
- **[NOTE] `docs/RECIPE-FORMAT.md:161-164`:** the top-up does not always find
  another document. With no `_TOP_UP_GENRES` document inside the person's
  employment window, `plan_mentions` exits ("cannot reach
  min_mentions_per_person", `planner.py:970-975`).
- **[NOTE] `tests/test_unit_mail_broadcast.py:66-82`:** only
  `internal_email` is compared; genres outside `_TOP_UP_GENRES` could be
  asserted byte-identical at no cost.
- **[NOTE] `orgsmith/docplan/planner.py:811-818`:** the anchor rationale does
  not say whether the empty first overview is intended with the knob on.
- **[NOTE] `orgsmith/docplan/planner.py:947-985`:** the top-up never checks
  whether the person can read the document (BACKLOG
  `mention-filler-acl-seam`). With the floor at 0, an aliased person whose
  only mention is dropped makes docplan exit ("cannot plant nickname alias").
- **[NOTE] `orgsmith/authoring/contexts.py:88-93`:** the mundane-mail genre
  brief says "Name the colleagues involved", against the list-note guidance.
  Measured effect: none (0 of 7 list bodies name a colleague).
- **[NOTE] `orgsmith/authoring/contexts.py:343-345`:** the finished-only
  digest dates completed work by start year.
- **[NOTE] `tools/mail_device.py:54-55`:** `planned_list_mentions` is zero by
  construction under the knob. The tool has no test.
- **[NOTE] `orgsmith/validate/rules.py`:** `overview_cites_finished_work` has
  no validator rule.
- **[NOTE] `orgsmith/schemas.py:241`:** `broadcasts_address_the_list` is
  accepted with `distribution_lists: 0`, where it is inert.
- **[NOTE] `tests/test_org_evals_acceptance.py:186`:** the org-tier
  unanswerable test skips on every committed org. It is re-hosted on a
  synthetic org, which meets the re-host rule.
- **[NOTE] `orgsmith/schemas.py:685-696`:** the oversight-title check echoes
  a received tree's strings raw (security, carried).
- **[NOTE] `orgsmith/review/numbers.py:44`:** a run of 4301 or more digits in
  authored prose crashes `report` (security, carried).

### Resolved since the prior entry

- `BACKLOG.md:180` now reads "his `d:0044` mention and its ACL denial are
  identical at `61abcbd`". Verified: his `d:0044` surface is "Matthew
  Parrish" at both revisions, his only mentions are `d:0039` and `d:0044` at
  both, and his `acl.json` grants (12 documents) exclude
  `Engagements/Jackson Inc/2024.04.12 - Kickoff Memo - Trademark
  Clearance.docx` at both. `61abcbd` is the M17d close, so "predates the
  turn" holds.
- `docs/RECIPE-FORMAT.md:164-169` names the alias re-host and marks it
  unobserved. Accurate per `planner.py:977-990` and the fleet check above;
  the two residuals are the NOTEs above.

### Tests

Not run (light review). The prior review's baseline at `9045bae` stands:
short 19, unit 837, org 261 passed with 31 skipped, flagship 71 passed with
5 skipped. This commit touches no code or test file.

### Security

Not run (light review). No secrets or credentials in the changed prose.
SECURITY.md is unchanged (last scan `9045bae`: 0 BLOCK, 0 WARN, 2 NOTE).

### Fixes Applied

None.

### Accepted Risks

None.

---
*Prior review (2026-10-13, commit 9045bae): refresh review of the four
tightened M17e close-out claims; 0 BLOCK, 0 WARN, 15 NOTEs (seven new or
narrowed, eight carried). Commit `316e183` resolves its `d:0044` and
alias-pass NOTEs.*

<!-- REVIEW_META: {"date":"2026-10-13","commit":"316e183","reviewed_up_to":"316e183fa1b6651376d32f275f4ccc12d936a86a","base":"origin/main","tier":"light","block":0,"warn":0,"note":15} -->
