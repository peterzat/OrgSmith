# CODEREVIEW

## Review — 2026-08-10 (commit: 1c0e132) — the OCR picker split and the board-yield backlog entry

**Review scope:** Light review. Two files changed since `origin/main`, both
plain Markdown with no executed content: `README.md` (3 lines) and
`BACKLOG.md` (one appended entry). No code, no configuration, no skill file, so
the tier rule's light path applies: factual accuracy, broken references, and
secret leaks only. No test run, no security chain, no external reviewers, no
fix loop.

**Summary:** Splits the scans row of the README's picker table after finding it
mislabelled `verdant-health`, and records the board-yield-versus-corpus-size
measurement in `BACKLOG.md`. Both changes are assertions of fact and both
re-verify. One WARN, author-applied: a wiki-link convention imported from
another system that GitHub does not render.

**External reviewers:** Skipped (light review).

**Security:** Skipped. No code changes since the scan at `c5b9994`;
`git log <meta-commit>..HEAD -- ':!*.md'` is empty. Carried forward 0/0/0.

### Findings

**[WARN] `BACKLOG.md:119` — `[[board-negative-control]]` uses a wiki-link
syntax this repo does not use and GitHub does not render.**

The appended entry cross-references a sibling backlog entry as
`[[board-negative-control]]`. That is the double-bracket convention from the
agent memory-file system, not a Markdown link: GitHub renders it literally as
`[[board-negative-control]]`, so the reader sees stray brackets rather than a
reference.

Evidence: `grep -c '\[\[' BACKLOG.md` returns 1, and it is this line. Every
other cross-reference in the file uses backticks (`` `docs/SCALE.md` ``,
`` `graph_targets.alias_agreement` ``, `` `mundane-broadcast-names-a-recipient-in-the-body` ``)
or plain prose. The convention was imported from a different context by the
author rather than taken from the file it was written into.

WARN rather than BLOCK: it is cosmetic, the referenced entry is named in full
so a reader can still find it, and nothing depends on it resolving.

**Author-applied, and recorded rather than folded in silently.** The light path
has no `/codefix` step, the defect is one line in text written minutes earlier
in this same session, and shipping it would put visibly broken rendering in the
register. Changed to `` `board-negative-control` ``, matching the file's own
style.

### Verified clean

- **The picker-table correction is right.** `verdant-health` is
  `scanned_ratio 0.5, ocr_layer_rate 0.0`, and `orgsmith/schemas.py:249` defines
  the field as "fraction of those scans carrying a synthetic OCR text layer
  (the rest are image-only)", so every one of its scans is image-only. The old
  row listed it under "degraded scans with a synthetic OCR layer", which is the
  opposite of what it ships. The replacement OCR-layer row names all four orgs
  that actually have one (`brackenridge-civil` 0.5, `calderwood-partners` 0.5,
  `northgate-staffing` 0.34, `saltmarsh-environmental` 0.5); the previous row
  named two of the four.
- **All five file links added resolve.**
- **The published yield figures re-derive.** Spot-checked the two endpoints
  that carry the argument: `calderwood-partners` 168 sampled / 8 findings =
  0.048, `northgate-staffing` 51 sampled / 37 findings = 0.725. The entry
  states the per-org numbers inline so the comparison can be re-derived without
  re-running any board, which is the right call for a claim about an
  instrument.
- **The backlog entry meets the register's own gates**: specific description
  naming a what and a where, a concrete why-deferred, and four concrete revisit
  criteria rather than a history note.
- **No secret, credential, or PII** in either file; the diff is board statistics
  and prose.

### Fixes Applied

- **[WARN] `BACKLOG.md:119`** — author-applied, above.

### Accepted Risks

None.

---
*Prior review (2026-08-10, commit 6d6058c): the M17c results and fleet
rationale. One BLOCK, both in-page anchors introduced by the change being
broken, one pointing at the wrong section and calling it "above" when it was
below; and one WARN it introduced, the fix heading swallowing ~140 unrelated
lines. Both fixed over two `/codefix` cycles plus one author-applied structural
decision `/codefix` correctly declined as out of its remit.*

<!-- REVIEW_META: {"date":"2026-08-10","commit":"1c0e132","reviewed_up_to":"1c0e132","base":"origin/main","tier":"light","block":0,"warn":1,"note":0} -->
