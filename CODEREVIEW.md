# CODEREVIEW

## Review — 2026-10-13 (commit: 12b1933) — M17e close-out: the overclaim corrections

**Review scope:** Refresh review. Focus: 6 file(s) changed since the prior
review (commit `0c231b9`); 5 of them are in the push range
(`origin/main..12b1933`, one commit), and the sixth,
`tests/test_unit_overview_finished.py`, was already pushed at `9dffb43`. No
already-reviewed files were left to check for interactions only. The two code
changes are docstring-only (`orgsmith/docplan/planner.py:811-818`,
`tests/test_unit_mail_broadcast.py:67-72`). Every causal claim in the new
prose was checked against the committed ledgers at `61abcbd` and HEAD: the
hollowell manifests, `acl.json`, `engagements.json` and `GENERATION-REPORT.md`.

**Summary:** One commit that checks off SPEC.md and corrects three overclaims
the prior review raised. RECIPE-FORMAT, the broadcast test's docstring,
BACKLOG and README now say that the mail knobs feed the
`min_mentions_per_person` top-up, and the overview planner docstring states
the finished-work rule. The corrections are accurate in substance. Seven new
NOTEs record wording that is still imprecise, three of them caught by both
finders. 0 BLOCK, 0 WARN.

**External reviewers:**
None configured.

**Built-in review:**
`/code-review high`: 6 findings, 6 kept after Step 6 (three merged with
inline findings; all NOTEs).

### Findings

**[NOTE] `orgsmith/docplan/planner.py:815-818` — the new docstring says
"ended by its date"; the code excludes that date. (also claude-code)**
  Evidence: `overview_engagements` (`orgsmith/fabric/engagements.py:325`)
  filters on `e.end < when`. Its own docstring (line 320) and
  `docs/RECIPE-FORMAT.md` ("ENDED before its date") both say "before". Two
  lines earlier the same docstring uses "begun by its date" for the inclusive
  `e.start <= when`, so "by" reads as inclusive.
  Suggested fix: "names only engagements that ended before its date".
  High confidence; affects documentation only.

**[NOTE] `orgsmith/docplan/planner.py:811-813` — the anchor rationale is
still the knob-off one. (claude-code)** "Anchored just after the first
engagement so the earliest one has a client to cite" is false with
`overview_cites_finished_work` on. The added sentence concedes this ("usually
names none"), but it does not say whether the empty first overview is
intended. The three regenerated orgs' first overviews read fine without
clients. Moving the anchor would be a new, default-off behavior. Low.

**[NOTE] `BACKLOG.md:180` — "The hollowell instance was caused by this
turn's own mail knobs" covers more than the evidence does.**
  Evidence: `rf:graph-1` has two instances. One is Sharon Woods in `d:0005`;
  the other is Matthew Parrish in `d:0044`, as the entry's preceding sentence
  says. Only Sharon Woods' instance is caused by the mail knobs, and the entry
  verifies it: at `61abcbd` she is mentioned only in `d:0002` (list),
  `d:0025` (direct) and `d:0052` (list); at HEAD she is a participant in
  kickoff `d:0005`, which her grants exclude, and in overview `d:0007`, which
  they include. Matthew Parrish's instance predates the turn: his `d:0044`
  kickoff mention and its ACL denial are identical at `61abcbd` and HEAD
  (same doc id, same participant, the Jackson Inc kickoff absent from his
  grants under a departmental posture both times). README:735-738 is precise
  ("named her").
  Suggested fix: "Sharon Woods' half of the hollowell instance was caused by
  ...".
  High confidence on the facts.

**[NOTE] `docs/RECIPE-FORMAT.md:158` — "Both mail knobs remove planned
mentions" undercounts. (also claude-code)** The block documents three
mention knobs. `exempt_author_mentions` also drops planned mentions
(`planner.py:913`, `934-935`) and so feeds the same top-up, and hollowell
runs it on. The caveat is attached only to the last knob's entry. BACKLOG's
"any knob that removes planned mentions feeds this seam" states it correctly.
Medium.

**[NOTE] `docs/RECIPE-FORMAT.md:156-161` — "no other note moves" now sits
just above text saying that another document moves. (claude-code)** Both
statements are true only because of the switch from "note" to "document",
and a reader checking whether the knob is safe can miss it. Low.

**[NOTE] `tests/test_unit_mail_broadcast.py:66-82` — the test compares only
`internal_email`, and the docstring calls that "the mail genre". (also
claude-code)** `engagement_email` is also mail and is not compared. Neither
are the other genres outside `_TOP_UP_GENRES` (`planner.py:76-81`), which the
top-up pass cannot touch. They could all be asserted byte-identical, which
would keep a later change from moving an engagement thread unnoticed. The
org-tier pin covers this only for the committed orgs. Low.

**[NOTE] `orgsmith/docplan/planner.py:947-985` — removing mentions feeds the
top-up and alias passes, and the top-up never checks whether the person can
read the document. (claude-code; carried and narrowed from the prior
entry)** The documentation overclaim is resolved. The behavior remains: the
candidate filter checks genre, employment and existing mention, not
readability under the ACL. With the floor at 0, a person whose only mention
was dropped and who carries an alias still makes docplan exit ("cannot plant
nickname alias"). BACKLOG `mention-filler-acl-seam` records the fix (a
default-off knob) as deferred, so this is recorded, not actionable here.

**Carried from the prior entry, still present at HEAD (files unchanged since
`0c231b9`):**

- **[NOTE] `orgsmith/authoring/contexts.py:88-93`:** the mundane-mail genre
  brief still says "Name the colleagues involved", which pulls against the
  list-note guidance. Measured effect: none (0 of 7 list bodies name a
  colleague).
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

### Verified clean

- **Sharon Woods causal chain:** verified as BACKLOG and RECIPE-FORMAT state
  it. Her three pre-carve-out mentions were two list notes, emptied by
  `broadcasts_address_the_list`, and one direct note (`d:0025`), dropped by
  `exempt_recipient_mentions`. With the floor at 2, the top-up placed her in
  the earliest candidates: kickoff `d:0005` and overview `d:0007`.
- **Test docstring against test body:** each broadcast keeps path, date,
  authors and render params, exactly the tuple asserted.
- **README context:** "a third" follows the two code-caused findings listed
  before it, and `rf:graph-1` is a major on hollowell's report (line 143).

### Tests

Baseline at `12b1933`: short 19, unit 837, org 261 passed with 31 skipped,
flagship 71 passed with 5 skipped, exit 0. These are the prior review's
counts exactly. No fixes were applied, so nothing was re-run.

### Security

`/security` over the 3 surface files changed since the last scan's commit
`0c231b9` (`orgsmith/docplan/planner.py`, `tests/test_unit_mail_broadcast.py`,
`tests/test_unit_overview_finished.py`): 0 BLOCK, 0 WARN, 2 NOTE (both
carried, above). No secrets. SECURITY.md is updated and uncommitted.

### Fixes Applied

None.

### Accepted Risks

None.

---
*Prior review (2026-10-13, commit 0c231b9): M17e mail-org carve-out and
v2.5.0, refresh review; 0 BLOCK, 1 WARN (the overview brief test checked no
brief), fixed by `/codefix` and pushed at `9dffb43`, and 10 NOTEs recorded.
This commit addresses three of those NOTEs in docs.*

<!-- REVIEW_META: {"date":"2026-10-13","commit":"12b1933","reviewed_up_to":"12b193317facb906d4788943f4057a137ece760e","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":15} -->
