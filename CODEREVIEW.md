# CODEREVIEW

## Review — 2026-07-17 (commit: de60065)

**Summary:** Refresh review of the unpushed M11b arc (12 commits,
`origin/main..HEAD`): the MODEL-AB Round 2 experiment, the K>1 resume pin, the
five-org fleet generation, the flagship board pass, the retirement of the six
pre-v2.0 fixtures, and the fleet-wide re-freeze. Prior review `38d79aa` (0
BLOCK, same base), so this is a refresh; the focus set is 21 hand-written files
plus 850 generated fixture files. **No product code changed this turn** —
`orgsmith/` is untouched. `bin/test` green and unmoved: 440 passing (12 short /
356 unit / 72 org), up from 422 at turn start.

**Reviewer separation:** the turn's author is also the reviewer, so Claude's own
review was delegated to two fresh-context adversaries (test coverage, docs
accuracy) rather than self-graded. Both BLOCKs below came from those reviewers
and were independently re-verified against the ledgers before being recorded.

### Findings

**[BLOCK] README.md:211 — "five fees totalling $500,500" is false; the true
figure is $425,500.**

  Evidence: the 2021 firm overview (`d:0044`) names five engagements,
  E-2015-001 through E-2019-001, whose fees are $92,000 + $105,000 + $66,000 +
  $100,500 + $62,000 = **$425,500**. $500,500 is the *six*-engagement lifetime
  total, which includes E-2023-001 ($75,000) — an engagement dated two years
  after the overview was written. The board's own finding file states both
  numbers correctly and separately (`finance_realism.json`, `rf:fin-1`: "whose
  fees total $425,500" and "against $500,500 of lifetime engagement fees").
  BACKLOG.md:27 uses $500,500 correctly, labeled lifetime. Only the README
  conflates them.
  Why it matters beyond arithmetic: the paragraph's entire point is that the
  corpus mistakes a sampled engagement book for the whole business. Conflating
  the five-engagement subtotal with the six-engagement lifetime total commits
  that same error while accusing the corpus of it, in the repo's most-read file,
  and the ratio it feeds ($2,469,000 against the fees) is the section's
  load-bearing number.
  Suggested fix: $500,500 -> $425,500.

**[BLOCK] README.md:214 — "Four of the six reviewers found this independently"
is false; three did.**

  Evidence: searching all 28 findings across summary and evidence fields, the
  engagement-book-vs-revenue contradiction is raised by `finance_realism`
  (rf:fin-1), `narrative_consistency` (rf:narrcon-1), and `org_realism`
  (rf:orgreal-1). `cross_document_voice`, `document_plausibility`, and
  `graph_acl_naturalness` do not raise it. Independently confirmed by grepping
  the findings directory for the claim's markers.
  Why it matters: BACKLOG.md:27 makes the same claim but hedges it — "(...
  and by implication document_plausibility)". An implication is not an
  independent finding, and independent corroboration is the whole rhetorical
  weight of the sentence. The README drops the hedge and rounds three up to
  four. This is the specific claim a sceptical reader would check first, in a
  section that ends by telling them to read the board sceptically.
  Suggested fix: "Three of the six reviewers found this independently."

**[WARN] README.md:523 — northgate "growing from 7 seats to 12" is wrong; it
grows 6 to 11.**

  Evidence: `foundation.json` gives 12 people on the roster ever, with one
  departure (john.chang, 2017-07-08). Concurrent seats: 6 at 2015-01-01, 11 at
  2023-12-31, max concurrent 11. 12 is the roster-ever count, not a seat count.
  `Charter.headcount` is concurrent seats, per CLAUDE.md and the M11a spec.
  Compounding: meridian has the identical shape (12 roster, 1 departure) and is
  described correctly two lines later as "growing 6 seats to 11", so the README
  states the same kind of fact two ways within one bullet list.
  Suggested fix: "growing from 6 seats to 11".

**[WARN] README.md:206 — "passes all 29 validator rules with zero errors"
overstates what ran.**

  Evidence: `validate northgate-staffing` reports "24 rules run, 5 skipped, 0
  errors, 0 warnings". Zero errors is true; "passes all 29" is not, since 5
  never ran (knobs the recipe leaves off). Per CLAUDE.md those skips are
  legitimate and grandfathered by charter — the wording is the defect, not the
  skips.
  Suggested fix: say it passes every rule its recipe enables, with zero errors,
  or state "24 rules run, 5 skipped for knobs it leaves off, 0 errors".

**[WARN] docs/MODEL-AB.md:280 — the cost arithmetic is exact but the
mix-robustness reasoning is invalid as stated.**

  Evidence: every number verified (500,180/264,516 = 1.8909; 1.891 x 0.6 =
  1.1346; 1.891 x 0.4 = 0.7564; Sonnet 5 $3/$15 against Opus 4.8 $5/$25 is
  exactly 0.6 on both halves; intro $2/$10 exactly 0.4). But the claim "the cost
  ratio is `token_ratio * 0.6` and is robust to whatever the input/output/cache
  mix turns out to be" conflates two steps. Converting *Sonnet's own* bill to
  Opus rates is 0.6x and genuinely mix-robust. Comparing *two arms with
  different token vectors* gives `0.6 x cost_Opus(v_C)/cost_Opus(v_A)`, which
  collapses to `0.6 x token_ratio` only if the blended per-token price matches
  across arms — i.e. only if the mixes match. The mix cancels when identical; it
  is not robust to whatever it turns out to be.
  Why it matters: the doc supplies evidence the mixes differ ("made more tool
  calls, re-read more, and self-checked more" while producing 0.86x the words).
  More re-reading means proportionally more input/cache-read tokens; fewer words
  means fewer output tokens; output is the expensive component. So Sonnet's
  blended price is plausibly lower and 1.135x may be an over-estimate —
  potentially enough to weaken the headline "at standard pricing the cheaper
  model is the more expensive choice". Not resolvable from the repo: subagent
  tokens are one undifferentiated total and the run lived in gitignored
  `scratch/`. The Limits section lists five caveats and omits this one.
  Suggested fix: add equal-mix to the Limits section as an explicit assumption
  and soften "robust to whatever the mix turns out to be" to what is true.

**[WARN] tests/test_unit_evals.py:286 — `locations <= expected` is
one-directional and permits an enabled knob to produce nothing.**

  Evidence: for hollowell-ip (`signature_page_facts: 1`), if signature-page
  placement broke entirely, `locations` collapses to `{"body"}`; `{"body"} <=
  {"body","signature_page"}` is True and `"body" in locations` is True, so the
  test passes with the knob ON and its artifact missing. That is precisely what
  CLAUDE.md forbids: "a knob that is on with its artifact missing is a failure
  (tamper evidence), never a skip." Probed across all seven orgs, every one is
  exact today (hollowell `{signature_page:1, body:14}`; meridian and saltmarsh
  add `filename:1`), so `locations == expected` holds at zero cost.
  Not a regression — both retired hosts had hard_cases off, so this branch is
  new coverage — but it is loose on committed fixtures, which is where tamper
  evidence lives.
  Suggested fix: assert `locations == expected`.

### Notes

- **[NOTE] tests/test_org_regen.py:11-25** — module docstring still says the
  byte-pin is scoped to dev-mini until the fleet resets in M11, and cites
  "cindergrove's 1998 recipe". M11b *is* that reset (`PINNED = SLUGS`) and
  cindergrove was deleted in the same commit. The `_COHERENCE_EXEMPT` and
  `PINNED` comments below it were rewritten; the docstring above was missed.
- **[NOTE] tests/test_unit_evals.py:252** — "Four of the fleet's seven orgs now
  plant signature-page or filename facts"; it is three (hollowell, meridian,
  saltmarsh).
- **[NOTE] tests/test_unit_evals.py:399** — "across four orgs" contradicts its
  own enumeration, which lists five.
- **[NOTE] tests/test_unit_compat.py:16** — "already assert every contract those
  tests covered" is false by one field: the deleted test asserted
  `ocr_layer_rate == 0.0`; the synthetic assertion omits it. The contract is not
  actually uncovered (`schemas.py` rejects `ocr_layer_rate > 0` when
  `scanned_ratio == 0`, so a changed default fails `OLD_CHARTER` validation
  outright), but the claim as written is wrong.
- **[NOTE] README.md:215** — "fleet mean 0.995" is the mean of seven per-org
  means (0.9948); the per-document mean over all 225 docs is 0.9977. It sits
  beside "every one of the 225 authored documents", which implies per-document.
  The stronger claim is exactly true: 0 of 225 outside +/-25%, range
  0.7733-1.2480.
- **[NOTE] README.md:130** — "~17 MB of share" measures 16.36 MB (16,355,473
  bytes across 294 files). `du -sb` reports 16.63 MB by counting directory
  inodes, the likely source; ~16 MB is the honest round.
- **[NOTE] docs/SCALE.md:53** — cites "cindergrove-advisors ... against
  bramblewood-legal's 17.1" in present tense; both retired. Pre-existing from
  M11a, but M11b appended a new timing section to the same doc without
  reconciling it.

### Fixes Applied

All 2 BLOCK and 4 WARN fixed by `/codefix`, plus the 7 NOTEs. Tests unmoved
from baseline: 440 passing (12 short / 356 unit / 72 org).

- **[BLOCK] README.md:213** — $500,500 -> $425,500.
- **[BLOCK] README.md:215** — "Four of the six reviewers" -> **"Two of the six
  reviewers drew this contradiction independently, on different dimensions, and
  a third independently reached the premise under it."** Landed at "two", not
  the "three" this review specified. `/codefix` applied "three" as written but
  flagged that the strict reading gives two, and it was right: `rf:fin-1`
  ("contradicts the revenue on the firm's own financial summaries by roughly
  twenty-fold") and `rf:narrcon-1` ("which the finance ledger contradicts by
  roughly fortyfold") both draw the revenue contradiction; `rf:orgreal-1` never
  mentions revenue — it uses the complete-book premise for a different
  conclusion (hiring into an empty engagement book). The review's own grep
  matched it on shared vocabulary rather than on the claim. The README sentence
  is specifically about the books contradicting the paperwork, so the strict
  reading governs. Three counts were proposed for this sentence across the turn
  — four (author), three (reviewer), two (fix loop) — and only reading the three
  findings end to end settled it. Recorded because the sentence's whole purpose
  is corroboration, and it is the claim a sceptical reader checks first.
- **[WARN] README.md:207** — "passes all 29 validator rules" -> "validates
  clean: 24 rules run, 5 skipped for knobs it leaves off, 0 errors".
- **[WARN] README.md:525** — northgate "7 seats to 12" -> "6 seats to 11".
- **[WARN] docs/MODEL-AB.md** — the two steps of the cost derivation split, the
  equal-mix assumption made explicit, and a sixth Limits bullet added ("The cost
  ratio assumes the two arms' token mixes match"). The arithmetic was already
  exact; the reasoning around it was not.
- **[WARN] tests/test_unit_evals.py:286** — `locations <= expected` ->
  `locations == expected`; the failure message now names both unexpected and
  missing locations. Exact on all seven committed orgs today, so it is tight
  rather than vacuous.
- **[NOTE] tests/test_org_regen.py:11-25** — module docstring rewritten; it
  still claimed the pin was scoped to dev-mini until M11 and cited a deleted
  fixture.
- **[NOTE] tests/test_unit_evals.py** — "Four of the fleet's seven orgs" -> three
  (hollowell, meridian, saltmarsh); "across four orgs" -> five, matching its own
  enumeration.
- **[NOTE] tests/test_unit_compat.py** — `OLD_CHARTER` now asserts
  `ocr_layer_rate == 0.0`, making the docstring's "already assert every contract
  those tests covered" true directly rather than by relying on a validator
  side-effect.

Deferred, with reasons:

- **[NOTE] README.md "fleet mean 0.995"** — kept. It is the mean of seven per-org
  means (0.9948); the per-document mean is 0.9977. Both round to "every document
  within 25% of brief", which is the claim that carries weight and is exactly
  true (0 of 225 outside, range 0.7733-1.2480). Changing it would trade one
  defensible statistic for another at the cost of churn.
- **[NOTE] README.md "~17 MB"** — kept. Measures 16.36 MB; "~17" is a defensible
  round of what `du` reports, and the figure is decorative rather than
  load-bearing.
- **[NOTE] docs/SCALE.md:53** — kept. Pre-existing from M11a and outside this
  turn's diff; the retired-fixture timing example is historical context for a
  decision already made. Worth a sweep next turn, not a fix in a retirement
  commit.

### Accepted Risks

None.

---
*Prior review (2026-07-16): full-depth review of the M11a arc at `38d79aa`; 0
BLOCK, 0 WARN, 1 NOTE (`_COHERENCE_EXEMPT` could not fail when stale). That NOTE
is closed by this turn's `test_coherence_exempt_names_only_live_recipes`.*

<!-- REVIEW_META: {"date":"2026-07-17","commit":"de60065","reviewed_up_to":"de60065c1c839fdd6c8895e1bc0642e3dc0ba338","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":3} -->
