# CODEREVIEW

## Review — 2026-10-13 (commit: 9045bae) — M17e close-out: the four tightened claims

**Review scope:** Refresh review. Focus: 4 file(s) changed since the prior
review (commit `12b1933`): `BACKLOG.md`, `docs/RECIPE-FORMAT.md`,
`orgsmith/docplan/planner.py`, `tests/test_unit_mail_broadcast.py`. The push
range (`origin/main..9045bae`) is one commit, and the focus set is the whole
range, so no already-reviewed files were left to check for interactions only.
Both code changes are docstring-only (`orgsmith/docplan/planner.py:811-818`,
`tests/test_unit_mail_broadcast.py:67-72`). Each rewritten claim was checked
against the planner code and against hollowell's committed manifest,
`acl.json` and `engagements.json` at `61abcbd` and HEAD.

**Summary:** One commit that answers five of the prior review's NOTEs in
prose. The planner docstring now states the strict "ended before" rule and
qualifies the anchor rationale, RECIPE-FORMAT names all three
mention-dropping mail knobs and scopes "no other note moves" to mail, the
test docstring names the genre it checks, and BACKLOG attributes only Sharon
Woods' half of hollowell's `rf:graph-1` to the mail knobs. All five
corrections are accurate in substance. Both finders independently found two
remaining imprecisions: `d:0044` is not identical at `61abcbd`, and the
nickname-alias pass is a second path by which a dropped mention moves another
document. 0 BLOCK, 0 WARN.

**External reviewers:**
None configured.

**Built-in review:**
`/code-review high`: 6 findings, 6 kept after Step 6 (two merged with inline
findings, two matching carried NOTEs; all NOTEs).

### Findings

**[NOTE] `BACKLOG.md:180` — "its Matthew Parrish half, `d:0044`, is
identical at `61abcbd`" is true of his mention, not of the document. (also
claude-code)**
  Evidence: at `61abcbd` the `d:0044` participants are `p:ashley.williams`,
  `p:kelly.snyder`, `xp:cynthia.hunter`, `p:matthew.parrish`. At HEAD they
  also include `p:mary.bradley`, with a matching mention, because the M17e
  regeneration added her to engagement `E-2024-001`'s
  `internal_participants` (`companies/hollowell-ip-metadata/ledger/engagements.json`).
  The part of the claim that matters holds at both revisions: Matthew Parrish
  is a top-up participant of `d:0044` (appended last) and has exactly two
  mentions (`d:0039`, `d:0044`), and his `acl.json` grants exclude the
  Jackson Inc kickoff. Sharon Woods' grants exclude `d:0005` at both
  revisions too.
  Suggested fix: "(his `d:0044` mention and its ACL denial are identical at
  `61abcbd` and predate the turn)".
  High confidence on the facts; affects documentation only.

**[NOTE] `docs/RECIPE-FORMAT.md:156-164` — the nickname-alias pass is a
second path by which a dropped mention moves a document, and it can move a
mail note. (also claude-code)**
  Evidence: `plan_mentions` (`orgsmith/docplan/planner.py:977-990`) plants
  each alias on `hosts[0]` of the person's mentioning documents, with meeting
  minutes first and then by date. If an aliased person appears in no minutes
  and their earliest mention is a broadcast, turning
  `broadcasts_address_the_list` on drops that mention and the plant moves to
  the next host. That host can be another internal note or an engagement
  thread ("no other mail note moves" fails), and the move happens whatever
  `min_mentions_per_person` is set to. The new text names only the top-up
  path, and only with the floor on. `ashcombe-advisory` and `hollowell-ip`
  both run `nickname_aliases: 1`. Not observed: every alias in the committed
  fleet is hosted on `meeting_minutes`.
  Suggested fix: add the alias re-host to the caveat, or qualify "no other
  mail note moves" as holding when no aliased person's first host is a
  broadcast.
  Medium confidence that it is reachable; documentation only.

**[NOTE] `tests/test_unit_mail_broadcast.py:67-72` — the exact equality on
every other internal note does not exercise the alias path. (claude-code)**
The fixture is `dev-mini` with no nickname aliases, so "no later note moves"
holds for this fixture and is asserted only there. A fixture with
`nickname_aliases: 1`, as two of the three mail-knob orgs run, is where the
re-host above would show. Low.

**[NOTE] `docs/RECIPE-FORMAT.md:161-164` — the top-up does not always find
another document. (claude-code)** When no `_TOP_UP_GENRES` document is dated
inside the person's employment window, `plan_mentions` raises `SystemExit`
("cannot reach min_mentions_per_person", `planner.py:970-975`) instead of
relocating the mention. The failure is loud, so nothing ships wrong, but a
recipe author reading the comment expects a relocation. Low.

**[NOTE] `tests/test_unit_mail_broadcast.py:66-82` — only `internal_email`
is compared. (claude-code; carried from the prior entry)** The docstring now
states this correctly. The coverage gap remains: the top-up cannot touch
`engagement_email`, `engagement_letter`, `briefing_deck` or any other genre
outside `_TOP_UP_GENRES` (`planner.py:76-81`), so they could be asserted
byte-identical at no cost. The org-tier pin covers this only for the
committed orgs. Low.

**[NOTE] `orgsmith/docplan/planner.py:811-818` — the anchor rationale is
qualified but its intent with the knob on is still unstated. (claude-code;
carried and narrowed from the prior entry)** "(without the M17e knob below)"
and "the earliest overview usually names none" are both accurate. The
docstring still does not say whether the empty first overview is intended or
whether the anchor should move to the first end date when the knob is on.
Moving it would be a new, default-off behavior. Low.

**[NOTE] `orgsmith/docplan/planner.py:947-985` — removing mentions feeds the
top-up and alias passes, and the top-up never checks whether the person can
read the document. (carried)** The candidate filter checks genre, employment
and existing mention, not readability under the ACL. With the floor at 0, a
person whose only mention was dropped and who carries an alias still makes
docplan exit ("cannot plant nickname alias"). BACKLOG
`mention-filler-acl-seam` records the fix (a default-off knob) as deferred.

**Carried from earlier entries, still present at HEAD (files unchanged since
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

### Resolved since the prior entry

- `planner.py` "ended by its date" now reads "ended before its date",
  matching `overview_engagements` (`e.end < when`,
  `orgsmith/fabric/engagements.py:325`).
- RECIPE-FORMAT "Both mail knobs remove planned mentions" now names all
  three knobs, including `exempt_author_mentions` (`planner.py:913`,
  `935-936`).
- RECIPE-FORMAT "no other note moves" is now "no other mail note moves",
  next to an explicit statement that a non-mail document can move. The top-up
  never touches a mail genre (`_TOP_UP_GENRES`), so that half is exact; the
  alias half is the NOTE above.
- The broadcast test docstring now says "Documents other than internal
  mail", matching the `x.genre == "internal_email"` branch.
- BACKLOG and SPEC attribute only half of hollowell's `rf:graph-1` to the
  mail knobs. The Sharon Woods chain re-verified: three mail mentions at
  `61abcbd` (`d:0002`, `d:0025`, `d:0052`), and `d:0005` plus `d:0007` at
  HEAD.

### Tests

Baseline at `9045bae`: short 19, unit 837, org 261 passed with 31 skipped,
flagship 71 passed with 5 skipped, exit 0. These are the prior review's
counts exactly. No fixes were applied, so nothing was re-run.

### Security

`/security` over the 2 surface files changed since the last scan's commit
`12b1933` (`orgsmith/docplan/planner.py`, `tests/test_unit_mail_broadcast.py`):
0 BLOCK, 0 WARN, 2 NOTE (both carried, above). No secrets. SECURITY.md is
updated and uncommitted.

### Fixes Applied

None.

### Accepted Risks

None.

---
*Prior review (2026-10-13, commit 12b1933): M17e close-out SPEC check-off and
three overclaim corrections, refresh review; 0 BLOCK, 0 WARN, 15 NOTEs (seven
new wording imprecisions, eight carried). Commit `9045bae` resolves five of
the seven new ones in prose.*

<!-- REVIEW_META: {"date":"2026-10-13","commit":"9045bae","reviewed_up_to":"9045bae5af8f0f0b60a9a4f6f29efe4a41c413ff","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":15} -->
