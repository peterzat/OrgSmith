# Backlog

Durable register of considered proposals that were deferred, scoped out, or
rejected. Read before drafting a new SPEC.md; swept at turn close.


### board-negative-control
- **The review board's false-positive rate is unmeasured: it has been calibrated on one org, one model, one run, with no negative control** (`docs/REVIEW-CALIBRATION.md`, and the README's "What this does not prove" section says so publicly). Nothing establishes how often `/forge-review` manufactures a finding against prose that is fine.
- **Why deferred:** out of scope for M8 (fabric history and date-scoped briefs). Judged lower-urgency because every one of the M7 board's 11 majors against fernhollow cites ledger-traceable evidence and is checkable by hand without the board: `rf:finance-1`'s claim that every expense line is a fixed share of revenue is confirmed in 30 seconds by reading `fabric/finance.py:12-18,48` (hardcoded `_EXPENSE_CATEGORIES` weights, split out of an `expense_total` that is itself `year_revenue * expense_ratio`). A negative control matters when findings are not self-verifying.
- **Revisit criteria:** the board is pointed at a corpus whose ground truth the reader has not already read (a new fixture, an outside org, or the M10 reference fleet); or a board finding drives expensive work and cannot be confirmed against a ledger; or `/forge-fix` is proposed, since a fix loop turns the critic into a gate and its FP rate becomes load-bearing.
- **Origin:** spec 2026-07-16 (M7 proposal, "The board has no negative control").


### dev-mini-margin-incoherent
- **`dev-mini`'s recipe posts a ~43% terminal net margin: `growth_rate` 0.12 against a roster frozen at 5 seats over 2019-2023.** Exactly the incoherence `recipe-growth-outruns-headcount` named, surviving in the one recipe that entry's fix deliberately did not touch. Measured 2026-07-16: 20.7% (FY2019) -> 43.1% (FY2023). `tests/test_org_regen.py::test_fleet_recipe_growth_headcount_and_span_describe_one_firm` exempts it by name (`_COHERENCE_EXEMPT`), so the wart is recorded rather than silently skipped.
- **Why deferred:** fixing it means lowering `growth_rate` or setting `roster_churn.hires`, either of which moves dev-mini's ledgers, breaks the byte pin (`PINNED`), and forces regenerating the tracer -- a live authoring pass the M11a spec deliberately did not spend. dev-mini is a fixture (a regression oracle) rather than a reference-fleet org, and SCALE.md keeps those two jobs separate; its finance realism buys nothing the fixture exists to provide.
- **Revisit criteria:** the next time `dev-mini` is regenerated for any other reason (an authoring-affecting change, or the M11 re-freeze if it re-authors the tracer); or the first time dev-mini's finance ledger is cited as an example of the behavioral expense model rather than used as a regression oracle; or any reader or board finding calling the margin out, since dev-mini leads the README's fleet table and is the org people browse first.
- **Origin:** spec 2026-07-16 (M11a; found by building the fleet coherence check and measuring every recipe against it).
