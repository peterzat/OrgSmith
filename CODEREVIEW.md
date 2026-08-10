# CODEREVIEW

## Review — 2026-08-10 (commit: c5b9994) — the sibling-premise docs correction

**Review scope:** Full review (the prior entry records `block: 1`, so the
refresh conditions do not hold). Three files changed since `origin/main`, all
Markdown: `README.md`, `BACKLOG.md`,
`.claude/skills/forge-review/SKILL.md`. Reviewed at full tier rather than
light because `.claude/skills/` is product in this repo (CLAUDE.md, "the
skills ARE the product"), and a SKILL.md is executed prompt content rather
than prose a reader merely reads.

**Summary:** Removes the "never sees a sibling" mechanism claim from the four
README spots, the BACKLOG `cross-document-voice` entry, and the forge-review
board prompt, ahead of the SPEC criterion-ten docs reconciliation, on the
grounds that the repo is pausing mid-turn. The direction is right and the
`BATCH_SIZE` half is exact. One BLOCK: the replacement text asserts a fresh
absolute in the same direction as the claim it removes, contradicting the
second half of the very finding it cites.

**Tests:** 16 short, 739 unit, 230 org (+27 skipped), 65 flagship (+5
skipped). All four tiers green, unchanged from the pre-edit baseline. No
fixture touched; `PINNED = SLUGS` green.

**External reviewers:** None configured.

**Security:** `/security` run on the five files changed since the prior scan
(`9dcc15c`): the two `ab_*` tools and their three test modules. Zero findings
(0 BLOCK / 0 WARN / 0 NOTE). It also refreshed the stale `ab_compare.py` line
citations this review's predecessor deliberately carried (257, 262 → 449,
454; the referenced code is unmodified) and closed the in-place-overwrite
footgun as fixed.

### Findings

**[BLOCK] `README.md:398,422,681,1096`, `BACKLOG.md:103`,
`.claude/skills/forge-review/SKILL.md:79` — the correction replaces one
absolute false claim with a weaker absolute false claim in the same
direction.**

The source finding this commit cites (`docs/M17C-EVIDENCE-STANDARD.md:129-145`)
records two facts. The edit encodes the first and contradicts the second.

1. Within a batch, a worker holds up to six documents. `BATCH_SIZE = 6`
   (`orgsmith/authoring/contexts.py:31`), applied as `batch[:BATCH_SIZE]`
   (`:493`), so it is a cap and "up to six" is exact. Correctly stated.
2. Across batches: "Workers also read **across** batches. A control-arm worker
   reported reading an already-ingested reply from an earlier batch
   specifically to avoid repeating its section names, openings and closings.
   Nothing in `.claude/skills/forge-author/SKILL.md` grants or forbids this;
   the committed org's DocIR is simply on disk and readable."

Verified independently: `grep -n "sibling\|corpus\|other documents"
.claude/skills/forge-author/SKILL.md` returns nothing. There is no
prohibition. A worker's view is bounded by what its brief supplies, not by
anything the pipeline enforces.

The new text asserts the negation of (2) in six places:

- `README.md:398` — "and never the rest of the corpus"
- `README.md:422` — "no authoring worker sees more than its own batch"
- `README.md:681` — "It never sees the rest of the corpus"
- `README.md:1096` — "since a worker sees only its own batch"
- `.claude/skills/forge-review/SKILL.md:79` — "and never the rest of the corpus"
- `BACKLOG.md:103` — "What no author sees is the corpus"

The BACKLOG bullet is self-contradictory within itself: it says workers "read
across batches too" and then "what no author sees is the corpus", four
sentences apart.

Why BLOCK rather than WARN. This commit exists for one purpose, to remove a
false mechanism claim from the documents a reader actually reaches, and its
own message cites cross-batch reading as the evidence. Shipping it with a
fresh absolute in the same direction reinstates the defect at one remove and
makes the next reader's correction harder, because the text will now look
recently audited. The `SKILL.md` copy is the operational one: it would again
prime every `cross_document_voice` reviewer with a mechanism description that
the project's own evidence document contradicts, which is the specific harm
the commit was written to stop.

Suggested fix: state the bound as **briefing**, not capability. A worker is
briefed its own batch, up to six documents; the rest of the corpus's DocIR is
on disk, and has been read across batches at least once, but nothing briefs it
and nothing requires it, so any cross-batch self-check is incidental rather
than systematic. The "at corpus scale" framing already used at `README.md:678`
and `:1095` is the defensible one and should carry: no worker reviews the
whole corpus, whatever it may read alongside its brief.

### Fixes Applied

`/codefix`, verified by re-review of all six sites:

- **[BLOCK]** The bound is restated as **briefing** rather than capability
  everywhere. `README.md:397` "is briefed its own batch, up to six documents,
  and nothing briefs it on the rest of the corpus"; `:422` "no authoring
  worker is briefed beyond its own batch"; `:1101` "is briefed only its own
  batch". `README.md:679` carries the full nuance, since it is the passage
  that justifies the board: the DocIR is on disk and has been read across
  batches at least once, but nothing briefs a worker on it and nothing
  requires the check, so a cross-batch self-check is incidental rather than
  systematic, and no worker reviews the whole corpus.
- **[BLOCK]** `BACKLOG.md:103`'s internal contradiction is resolved: "What no
  author reviews is the corpus", followed by the briefing/requirement
  distinction, so the bullet's own "workers read across batches too" no longer
  contradicts its conclusion four sentences later.
- **[BLOCK]** `.claude/skills/forge-review/SKILL.md:78` rewritten, the
  operational site: a `cross_document_voice` reviewer is now primed with the
  briefing bound and the on-disk caveat, ending on "no worker reviews the
  whole corpus".

Re-review confirms no site retains an absolute claim about what a worker
*can* see. Two surviving greps for the old phrasing are correct in context and
were left alone: `BACKLOG.md:103` quotes "they never see a sibling" in order to
refute it in the next sentence, and `README.md:664`'s "the model never sees a
value it is placing" is the airlock, an unrelated and true claim.

Tests after the fix: 16 short, 739 unit, 230 org (+27 skipped), 65 flagship
(+5 skipped). Identical to baseline, no regression.

### Accepted Risks

None.

---
*Prior review (2026-08-04, commit 836a1dd): the M17c replicate arm and noise
floor. One BLOCK, `noise_floor` comparing distribution summaries where a
paired per-pair comparison was available, which could report zero noise on
runs where every pair moved and so failed toward significance. Fixed by
reporting both an aggregate delta and a paired spread, verified against the
finding's own demonstration case, plus an author-applied amendment log in the
evidence standard. `SECURITY.md`'s stale `ab_compare.py` line citations were
carried for the next `/security` pass rather than hand-edited.*

<!-- REVIEW_META: {"date":"2026-08-10","commit":"c5b9994","reviewed_up_to":"c5b9994","base":"origin/main","tier":"full","block":1,"warn":0,"note":0,"resolved":true} -->
