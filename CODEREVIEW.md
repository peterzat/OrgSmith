# CODEREVIEW

## Review — 2026-08-10 (commit: 6d6058c) — M17c results, the fleet rationale, and staleness fixes

**Review scope:** Full review (the prior entry records `block: 1`, so the
refresh conditions do not hold). Five files changed since `origin/main`, all
Markdown: `README.md`, `BACKLOG.md`, `docs/M17C-RUN-LOG.md`,
`docs/REVIEW-CALIBRATION.md`, `.claude/skills/forge-review/SKILL.md`. Reviewed
at full tier rather than light because `.claude/skills/` is product in this
repo (CLAUDE.md, "the skills ARE the product") and a SKILL.md is executed
prompt content.

**Summary:** Lands the M17c measurement and board results, adds the fleet
rationale a newcomer needs, and corrects four stale claims. The substance
checks out: every factual claim I spot-checked against the code or the
comparison output is correct, and all nine file links resolve. One BLOCK: both
in-page anchors introduced in this change are broken, one of them pointing at
the wrong section entirely and describing the target's position wrongly.

**Tests:** 16 short, 739 unit, 230 org (+27 skipped), 65 flagship (+5
skipped). All four tiers green, unchanged. No fixture touched.

**External reviewers:** None configured.

**Security:** Skipped. No code changes since the last scan (commit `c5b9994`);
`git log <meta-commit>..HEAD -- ':!*.md'` is empty and this diff is Markdown
only. Carried forward: 0 BLOCK / 0 WARN / 0 NOTE.

### Findings

**[BLOCK] `README.md:338` and `README.md:596` — both anchors introduced by this
change are broken, and one points at the wrong section and the wrong
direction.**

Two in-page links were added. Neither resolves.

1. **`README.md:596` defines no anchor.** The text is
   `**What M17c measured, and the answer is mixed.**` — a bold paragraph
   lead-in, not a Markdown heading. GitHub generates anchors from headings
   only, so `#what-m17c-measured-and-the-answer-is-mixed` does not exist.
   Verified: `grep -E "^#{1,6} .*what.m17c.measured" README.md` returns
   nothing, while the same probe finds the other two anchor targets used
   nearby.

2. **`README.md:338` points at the wrong section, and says "above" for
   something below it.** It reads:

   > All three arms are now generated and measured; [the result is
   > above](#why-we-think-the-output-is-any-good) ...

   `## Why we think the output is any good` begins at line 736. The M17c
   result is at line 596, inside `## Scale and representativeness`. So the
   link sends the reader past the content it promises, into a different
   section, and the word "above" is wrong in both senses: the target heading
   is below line 338, and so is the actual result.

Why BLOCK rather than WARN. This change exists to orient a newcomer, and both
defects are in the navigation a newcomer follows first: one link is dead, the
other is confidently wrong about where the thing it names lives. A reader who
clicks it lands in the wrong section and has no reason to suspect the link
rather than their own reading. That is worse than no link. It also repeats, in
new text, the class of defect this same session already corrected twice in this
file (the sibling-premise claim, and the exemplar described as open-ACL two
paragraphs above a table saying departmental).

Suggested fix: promote the line 596 lead-in to a real `###` heading, which is
consistent with the enclosing section's existing structure (`### What ships
today`, `### Why a fleet, and not just the best one`, `### Are they different
levels of quality?`, `### Where that sits against a real firm`, `### What is
not modeled today`), then point both references at
`#what-m17c-measured-and-the-answer-is-mixed` and change "above" to "below" at
line 338.

### Verified clean

Recorded because the diff is large and mostly assertions of fact:

- **All nine file links added resolve** (`companies/*` x4, `recipes/quillon-harbor/`,
  `docs/BASELINES.md`, `docs/M17C-EVIDENCE-STANDARD.md`, `docs/M17C-RUN-LOG.md`).
- **The two other anchors used nearby resolve**
  (`#why-we-think-the-output-is-any-good`, `#which-model-should-write-your-documents`).
- **The four staleness fixes are correct against the code**: `RULES` has 39
  entries; `validate calderwood-partners` prints "30 rules run, 9 skipped";
  `validate northgate-staffing` prints "34 rules run, 5 skipped"; the unit tier
  is 739.
- **The fleet-rationale claims check out**: `northgate-staffing` has
  `legacy_ratio 0.0` and no multi-affiliation, `brackenridge-civil` has
  `legacy_ratio 1.0`, `acl_posture` for the exemplar is `departmental`, and the
  two-vintage split (`claude-opus-5` for the exemplar, `claude-opus-4-8[1m]`
  for the other eight, one schema id) is what `state.json` records.
- **The M17c numbers match the comparison output** saved at
  `scratchpad/m17c-comparison.txt` and the board tallies match the ingested
  findings files.

**[WARN] `README.md:597` — the new heading swallows ~140 lines that are not
about M17c.**

Introduced by the BLOCK fix, and flagged by `/codefix` itself rather than
found later, which is the right call. Promoting the M17c lead-in to `###`
terminates `### What is not modeled today` at line 597, so everything from 598
to the next heading at 738 now renders under "What M17c measured" in GitHub's
outline. That range is the `mail.exempt_recipient_mentions` fleet-wide
artifact, the distribution-list residual, and the section's closing
scope-and-mechanics paragraphs. None of it concerns M17c.

Less severe than the BLOCK: every link resolves, the content is intact, and it
reads correctly top to bottom. Only the collapsed-outline view mis-nests. But
it is the same family of defect in the same newcomer-facing document, and the
fix is symmetric and one line.

Suggested fix: `README.md:639` already opens with the bold lead-in
`**One fleet-wide artifact, half closed, and be precise about which half.**`.
Promote it to `### One fleet-wide artifact, half closed, and be precise about
which half` the same way, so the mail material becomes its own sibling
subsection and the M17c heading scopes only the M17c result. Check no in-page
anchor targets the old bold text before changing it.

### Fixes Applied

`/codefix` cycle 1, verified by re-review:

- **[BLOCK]** `README.md:597` lead-in promoted to
  `### What M17c measured, and the answer is mixed`, a sibling of the other
  `###` subsections under `## Scale and representativeness`. The anchor now
  resolves.
- **[BLOCK]** `README.md:338` now reads "the result is below" and points at
  `#what-m17c-measured-and-the-answer-is-mixed`. Direction and target both
  correct: reference at 339, target at 597.
- Verified independently: a slug pass over the file resolves all 13 in-page
  anchor references, and all nine file links added by this change exist.

`/codefix` cycle 2:

- **[WARN]** `README.md:639` bold lead-in promoted to
  `### One fleet-wide artifact, half closed, and be precise about which half`,
  symmetric with cycle 1. Pre-checked, as the finding asked: no anchor anywhere
  in the repo targeted the old bold text, so nothing broke.

**Author-applied afterwards, and recorded rather than folded in silently.**
`/codefix` correctly reported that the prescribed one-line fix *moved* the
mis-nest rather than closing it: lines 662-737, the exemplar rationale and the
section's closers, then rendered under the new mail heading. It declined to
invent a fourth heading on the grounds that this "is a judgment call about
document structure rather than a defect fix", which is the right boundary for
a fixer to hold. Deciding the structure is the author's call, so I made it:
`README.md:663`'s lead-in is now
`### What we think is important about this exemplar`.

The enclosing `### What is not modeled today` had accumulated four unrelated
blocks behind one heading; that was pre-existing, and this change surfaced it
by adding anchors. Final structure under `## Scale and representativeness`:

| line | heading | scopes |
| ---: | --- | --- |
| 453 | What is not modeled today | 454-596 |
| 597 | What M17c measured, and the answer is mixed | 598-638 |
| 639 | One fleet-wide artifact, half closed... | 640-662 |
| 663 | What we think is important about this exemplar | 664-740 |

Verified after all three edits: 6 in-page references, 29 headings, **0 dead
anchors, 0 duplicate slugs**. Four tiers green and unchanged: 16 short, 739
unit, 230 org (+27 skipped), 65 flagship (+5 skipped).

### Accepted Risks

None.

---
*Prior review (2026-08-10, commit c5b9994): the sibling-premise docs
correction. One BLOCK, the correction replacing one absolute false claim with a
weaker absolute false claim in the same direction, contradicting the second
half of the finding it cited; fixed by restating the bound as briefing rather
than capability at all six sites. `/security` clean at 0/0/0, and it refreshed
the stale `ab_compare.py` line citations the review before it had carried.*

<!-- REVIEW_META: {"date":"2026-08-10","commit":"6d6058c","reviewed_up_to":"6d6058c","base":"origin/main","tier":"full","block":1,"warn":1,"note":0} -->
