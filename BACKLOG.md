# Backlog

Durable register of considered proposals that were deferred, scoped out, or
rejected. Read before drafting a new SPEC.md; swept at turn close.


### pdf-newline-flattening
- **The PDF renderer silently flattens `\n` inside a paragraph block while the DOCX renderer honors it as `<w:br/>`.** `render/pdf.py:90` emits `<p>{text}</p>`, and HTML collapses newlines to spaces; an author using the same convention that works in DOCX gets a smeared line in PDF. Affects the committed fixture `gladepoint-strategies` `d:0008`, whose addressee block renders as one run-on line. Validates clean because no rule checks line breaks.
- **Why deferred:** out of scope for M7 (the quality instrument); found BY the M7 board rather than planned. Fixing it re-renders a frozen fixture's committed bytes, which is its own decision.
- **Revisit criteria:** any turn that touches `render/pdf.py`, or the first fixture regeneration that would re-render an affected PDF, or a board finding that reports the same smear on a new org.
- **Origin:** spec 2026-07-16 (found by the review board during the model A/B; see docs/MODEL-AB.md finding 3).

### board-negative-control
- **The review board's false-positive rate is unmeasured: it has been calibrated on one org, one model, one run, with no negative control** (`docs/REVIEW-CALIBRATION.md`, and the README's "What this does not prove" section says so publicly). Nothing establishes how often `/forge-review` manufactures a finding against prose that is fine.
- **Why deferred:** out of scope for M8 (fabric history and date-scoped briefs). Judged lower-urgency because every one of the M7 board's 11 majors against fernhollow cites ledger-traceable evidence and is checkable by hand without the board: `rf:finance-1`'s claim that every expense line is a fixed share of revenue is confirmed in 30 seconds by reading `fabric/finance.py:12-18,48` (hardcoded `_EXPENSE_CATEGORIES` weights, split out of an `expense_total` that is itself `year_revenue * expense_ratio`). A negative control matters when findings are not self-verifying.
- **Revisit criteria:** the board is pointed at a corpus whose ground truth the reader has not already read (a new fixture, an outside org, or the M10 reference fleet); or a board finding drives expensive work and cannot be confirmed against a ledger; or `/forge-fix` is proposed, since a fix loop turns the critic into a gate and its FP rate becomes load-bearing.
- **Origin:** spec 2026-07-16 (M7 proposal, "The board has no negative control").

### charter-redump-drift
- **`run_charter` writes `charter.json` unconditionally (`orgsmith/charter.py:59`), so re-deriving a committed fixture's charter from its recipe rewrites the file with inert default fields it did not carry when generated.** Measured today, re-deriving from `recipes/<slug>/ORG-CHARTER.md`: 5 of 7 fixtures drift (torchlake-engineering +8 fields including `hard_cases` and `acl_posture`, quillbrook-appraisal +7, bramblewood-legal +6, cindergrove-advisors and gladepoint-strategies +1 each); only dev-mini and fernhollow-partners are byte-identical, because they are the two regenerated most recently. `/forge <slug>` runs `orgsmith charter <slug>` unconditionally (`.claude/skills/forge/SKILL.md:44`), so the resume path the README advertises as a headline feature ("kill the session mid-generation, re-run `/forge <slug>`") dirties a frozen fixture's committed bytes. Contrast `run_scaffold`, which is immutable-once-written (`foundation/scaffold.py:327`).
- **Why deferred:** out of scope for M8 (fabric history and date-scoped briefs). Not urgent because the drift is semantically inert (every gained field equals the default that was implicit at generation), so validation still passes and no ground truth moves; the cost is a dirty git tree on a fixture the project calls frozen, not a wrong org. The fix is a real decision, not a patch: either guard the write the way scaffold does, or accept re-dump and stop calling charter.json frozen.
- **Revisit criteria:** M8 landing, which adds at least three more inert charter fields (roster churn, expense model, era naming) and would widen the drift to 11 fields on torchlake and start dev-mini and fernhollow drifting for the first time; or any turn that makes charter.json byte-stability a test; or the first time someone resumes `/forge` on a committed fixture and has to explain the diff.
- **Origin:** spec 2026-07-16 (M7 Context flagged it as still open and uncarried; M8 Context carries it forward and this entry is where it survives turn close).
