# CODEREVIEW

## Review — 2026-10-13 (commit: 0c231b9) — M17e: the mail-org carve-out, v2.5.0

**Review scope:** Refresh review in form, full in effect. The prior review's
commit `03f6442` is already in `origin/main`, so the focus set is the whole
range: 9 commits, 642 files (`origin/main..0c231b9`). Code read in full:
the changed parts of `orgsmith/` (schemas, fabric engagements, docplan
planner, authoring contexts, the DL-01 rule) with their callers (mention
planning, top-up and alias passes, `render/eml.py`, `acl.py`, evals
emission), `tools/mail_device.py`, and every new or changed test. The three
regenerated orgs were checked structurally against the ledgers (knobs
effective, no overview names an unfinished engagement's client, list notes
plan no recipients). Their authored prose was not re-read beyond the three
first overviews, and `/security` scanned all 616 surface files.

**Summary:** Two default-off knobs (`mail.broadcasts_address_the_list`,
`doc_culture.overview_cites_finished_work`), a DL-01 branch for the first,
the device-count tool, two re-hosted tests, the wholesale regeneration of
`ashcombe-advisory`, `hollowell-ip` and `meridian-actuarial` under the M17e
carve-out, docs, and v2.5.0. One WARN, in a new test that asserted nothing it
claimed about the knob-on brief, fixed by `/codefix` in one cycle; the suite
is unchanged. The ten NOTEs are recorded, not fixed.

**External reviewers:**
None configured.

**Built-in review:**
`/code-review high`: 10 findings, 10 kept after Step 6 (two merged into one
entry; 1 WARN, the rest NOTEs). Two details rejected after checking: that the
unit fixture's top-up actually drifts with the knob on (a direct off/on
comparison differs only in the two list notes), and that `run_authoring(on) >= 0`
would hide an ingest failure (`ingest_author_batch` asserts `== 0`).

### Findings

**[WARN, fixed] `tests/test_unit_overview_finished.py:63-83` — the brief test checks no
brief. (also claude-code)**
  Evidence: `test_the_brief_agrees_with_the_plan_and_ingests` calls
  `run_next_batch(on)` once and filters that state's work orders for
  `company_overview` briefs. Reproduced on the same fixture: the first batch
  holds 0 overview briefs (the plan's two overviews, `d:0004` with 0 client
  facts and `d:0022` with 3, are batched later), so the `for b in briefs`
  loop never runs and neither the `"confidential"`/`"has completed"` nor the
  `"no completed client engagements"` assertion executes. The trailing
  `authored_hash` check does not cover the gap either: neither the scripted
  author nor ingest reads `firm_digest` (grep of `tests/conftest.py` and
  `orgsmith/authoring/ingest.py`), so plan/digest agreement is not what that
  check tests. Net effect: the knob-on digest text in
  `orgsmith/authoring/contexts.py:356-375` (both the `finished_only` branch
  and the `book_is_sample` suffix) has no executing test, and the docstring's
  claim that a disagreement "would be an ingest rejection" is not true of the
  digest.
  Suggested fix: drive `run_next_batch` until no new batch appears (as
  `tests/test_unit_mail_broadcast.py::test_the_brief_tells_the_author_to_address_the_group`
  does) before collecting briefs, assert `briefs` is non-empty and that both
  an empty and a non-empty overview were seen, and assert each non-empty
  digest lists exactly the brief's `{{fact:...}}` client refs (the real
  agreement property). Correct the docstring's ingest claim.

**[NOTE] `orgsmith/authoring/contexts.py:88-93` — the mundane-mail genre brief
still says "Name the colleagues involved." (claude-code)** With
`broadcasts_address_the_list` on, a list note's brief has no participants,
and the appended delivery guidance (`contexts.py:452-461`) says to name a
colleague only where the note is about them. The two instructions pull
against each other. Measured with no effect: 0 of the 7 list bodies across
the three regenerated orgs name a colleague. A fix would be knob-gated, since
the genre text is in every committed brief.

**[NOTE] `orgsmith/docplan/planner.py:757-768`, `947-985`;
`tests/test_unit_mail_broadcast.py:66-80` — emptying a broadcast's
participants feeds the top-up and alias passes. (also claude-code)** The
dropped mentions lower `have` in the `min_mentions_per_person` top-up, which
can then append that person to a minutes, kickoff, status, or overview
document; with the top-up at 0, a person whose only mention was on a
broadcast and who carries an alias makes docplan exit ("cannot plant
nickname alias"). Both are loud or only move an opt-in org's plan, but
`test_only_broadcasts_change` compares only `internal_email` entries while
its docstring says every other document plans exactly as before, and
`docs/RECIPE-FORMAT.md` says "no other note moves" (true of notes only).
`exempt_recipient_mentions` has the same interaction.

**[NOTE] `orgsmith/docplan/planner.py:811-815`, `820` — the overview docstring
is stale under the knob. (also claude-code)** It still says the anchor (first
start + 30 days) is chosen "so the earliest one has a client to cite" and
that each overview names clients whose engagement has begun. With
`overview_cites_finished_work` on, the first overview is client-less by
construction (all three regenerated orgs; their authored first overviews
describe the practice and name no client, which reads fine).

**[NOTE] `orgsmith/authoring/contexts.py:343-345` — the finished-only digest
dates completed work by start year. (claude-code)** `span` is built from
`e.start.year`, so "has completed 1 client engagement(s) across 2016" can
describe an engagement that finished in 2017. End years would match the
wording.

**[NOTE] `tools/mail_device.py:54-55` — `planned_list_mentions` is zero by
construction under the knob. (also claude-code)** It counts planned mentions
of `e.participants`, which the knob empties, rather than planned mentions of
any colleague other than the author. The published zeros still hold (every
list note in the three orgs plans no mention at all, checked directly), and
the before-counts (85/46/62, 4/3/3, 39/39, 20/20, 24/24) reproduce against
`61abcbd`. The tool has no test.

**[NOTE] `orgsmith/validate/rules.py` — `overview_cites_finished_work` has no
validator rule. (also claude-code)** `broadcasts_address_the_list` got a
DL-01 branch; a knob-on manifest whose overview cites a live engagement
passes `validate`, and only the org-tier byte pin catches it for committed
orgs. The spec did not ask for a rule, and several older knobs have none.

**[NOTE] `orgsmith/schemas.py:241` — `broadcasts_address_the_list` is accepted
with `distribution_lists: 0`. (claude-code)** The knob is then inert, but the
defect it fixes cannot occur without lists, so nothing passes vacuously.
Low.

**[NOTE] `tests/test_org_evals_acceptance.py:186` — the org-tier unanswerable
test now skips on every committed org. (claude-code)** Its path is re-hosted
on a synthetic org (`tests/test_unit_evals_unanswerable.py`), each skip names
its reason, and TESTING.md records the move, so this meets CLAUDE.md's
re-host rule.

**[NOTE] `orgsmith/schemas.py:685-696` — the oversight-title check echoes a
received tree's strings raw.** From `/security`, carried and re-confirmed at
HEAD: a crafted `charter.json` can write escape sequences to the terminal
through `validate`'s traceback; `_check_scope_services` (543-548) has the
same pattern. Fix: `strip_control` on each title, or sanitize the validation
error where `validate` loads a tree.

**[NOTE] `orgsmith/review/numbers.py:44` — a 4301+ digit run in authored prose
crashes `report`.** From `/security`, carried (file outside this range).

### Verified clean

- **Freeze:** the other seven orgs differ from `61abcbd` only in
  `charter.json` (the two new fields at their defaults) and `DATA-CARD.md`;
  their ledgers, manifests, prose, work orders, and recipes are unchanged.
- **Knobs effective on the three orgs:** every list-addressed note plans no
  participant and no mention; every overview's `facts_refs` equals the
  engagements that ended before its date, and no overview's prose carries an
  unfinished engagement's client name or fact id; oversight added a senior to
  5, 2, and 3 engagements and 3 starts moved, as the write-up says.
- **Docs:** README totals reproduce (147 `.eml`, 453 fleet questions, 1,148
  default-tier tests with 31 skips, 76 flagship), CHECKSUMS.md is current,
  and `northgate-staffing` still has 2 of 2 broadcasts naming a colleague, as
  stated.

### Tests

Baseline: short 19, unit 837, org 261 passed with 31 skipped, flagship 71
passed with 5 skipped, keyless and offline, exit 0. After `/codefix`:
identical counts, exit 0. The org tier includes `PINNED = SLUGS`, so the
committed fleet still re-derives byte-identical.

### Security

`/security` over the 616-file surface since `03f6442`: 0 BLOCK, 0 WARN,
2 NOTE (both above, both carried). No secret in the scoped files, the
rendered Office and PDF files, or the range diff. The post-fix re-check of
`tests/test_unit_overview_finished.py` found nothing. SECURITY.md is updated
and uncommitted.

### Fixes Applied

- **[WARN] `tests/test_unit_overview_finished.py:61-94`** (also claude-code):
  `test_the_brief_agrees_with_the_plan_and_ingests` now drives
  `run_next_batch` until no new batch appears, asserts it found overview
  briefs including at least one with client facts and one without, and checks
  that each non-empty digest's `{{fact:...}}` ids equal the brief's fact ids.
  The docstring no longer claims an ingest rejection would catch a
  disagreement. Re-reviewed: the loop matches the one in
  `tests/test_unit_mail_broadcast.py`, and the module's 4 tests pass.

The change is uncommitted: `tests/test_unit_overview_finished.py`, plus
`CODEREVIEW.md` and `SECURITY.md`.

### Accepted Risks

None.

---
*Prior review (2026-10-13, commit 03f6442): M17d, full review; 0 BLOCK, 2 WARN
(an era shock on the expense base year, an oversight title no one can hold),
both fixed by `/codefix` with tests, and 12 NOTEs recorded.*

<!-- REVIEW_META: {"date":"2026-10-13","commit":"0c231b9","reviewed_up_to":"0c231b99047a8a62ef0d2b0757bc614cb8e020fd","base":"origin/main","tier":"refresh","block":0,"warn":1,"note":10} -->
