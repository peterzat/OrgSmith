# M17c run log: what the live arms surfaced

Observations from authoring the M17c arms, recorded as they were found.

**This is not the evidence standard and amends nothing in it.** The analysis
specification lives in `docs/M17C-EVIDENCE-STANDARD.md` and was fixed before
either arm was authored. This file is the criterion-seven record: the knobs'
first live exercise "including what went wrong". Nothing here changes what
counts as evidence, and no finding here is fixed mid-run, because changing the
generator between batches would author an arm's early documents against a
different configuration from its late ones and destroy the comparison the arms
exist to support.

## THE RESULT

All three arms authored, 59/59 each, 39 batches, zero ingest rejections. The
comparison below is `tools/ab_compare.py --structure` run once, as
pre-registered. Raw output is reproducible with the command in
`docs/M17C-EVIDENCE-STANDARD.md`.

### The attribution check passes

7 differences between control and treatment, every one mapping to a declared
knob, exit 0: `engagements.json` and `manifest:facts_refs`/`key_facts` (45 of
77) to `engagements.scope`; `mention_map.json`, `manifest:mentions` and
`manifest:participants` (10 of 77) to `client_facing_reports`;
`manifest:render_params` (59 of 77) to `outline_variety`. Identity fields
(`doc_id`, `genre`, `date`, `authors`, `path`, `format`, `engagement`,
`title`, `rev`, `authoring`) identical. Criterion three is closed by the
purpose-built check, not only by hand.

### Structural axis, combined (shape + openers), 245 same-genre pairs per arm

| arm | mean | p50 | p75 | p90 |
| --- | ---: | ---: | ---: | ---: |
| control | 0.3721 | 0.3752 | 0.4718 | 0.5608 |
| treatment | **0.3087** | 0.2871 | 0.4000 | 0.5133 |
| replicate | 0.3803 | 0.3636 | 0.4546 | 0.5765 |

Lower is less similar. **Control-to-treatment gap: 0.0634.**

Against the two noise measures, which answer different questions:

- **Aggregate floor 0.0082** (control mean vs replicate mean). The gap is
  **7.7x** this. Read like-for-like, mean against mean, the shift is real: two
  identical configurations produce means that differ by 0.008, and the knob
  moved the mean by 0.063.
- **Paired per-pair 0.1097 mean, 0.2158 p90.** The gap is **0.58x** this. An
  *individual pair* moves more between two identical runs than the arm-level
  mean moves between control and treatment.

Both readings are correct and they bound different claims. The arm-level shift
survives; **no individual pair's movement may be attributed to the
treatment**, because per-pair noise exceeds the whole effect. Anyone reading
the printed top-50 list pair by pair would be reading noise.

### The discriminating comparison: convergence is relocated as much as reduced

This is the split the evidence standard named in advance as the thing to
check, and it is the most important number here.

| population | n | mean |
| --- | ---: | ---: |
| control, all pairs | 245 | 0.3721 |
| treatment, **same** skeleton | 50 | **0.4019** |
| treatment, **different** skeleton | 195 | 0.2849 |

The standard's pre-written reading: "if 'same skeleton' sits near 'control
(all pairs)', the outline work relocated the convergence into groups of the
pool size rather than reducing it."

It does not merely sit near it. It sits **above** it. The 50 pairs dealt the
same skeleton are *more* alike than a typical control pair, while the 195
dealt different skeletons are less alike. So the knob buys variety between
skeleton groups and pays for it with tighter convergence inside them. SCOPE-B
predicted the 20.4% share from pool arithmetic before any prose existed; this
is what that share costs.

### The lexical axis shows nothing

| arm | mean 4-gram Jaccard |
| --- | ---: |
| control | 0.0073 |
| treatment | 0.0066 |
| replicate | 0.0077 |

The control-to-treatment difference is 0.0007; the control-to-replicate spread
is 0.0004. The gap is **1.7x** noise, on one replicate. The standard calls
this "the most informative number the experiment produces", because a skeleton
constrains what a document contains, not which words it uses, so a drop here
would be far less mechanically forced than a drop in shape.

**There is no such drop.** The outline work moves shape and does not move word
choice. Given CONF-02, where a shared skeleton drove two workers to the same
opening bullet independently, the honest statement is that this measurement
cannot show the knob helping lexically and has one concrete instance of a
shared skeleton hurting lexically.

### Per genre, and the one that did not move

Treatment is below both controls in six of seven genres. The exception:

| genre | control | treatment | replicate |
| --- | ---: | ---: | ---: |
| engagement_letter | 0.4861 | **0.4927** | 0.5257 |

`engagement_letter` treatment is *above* control, inside the control-replicate
spread, so it did not move. Its pool holds 3 variants against 8 documents,
giving 7 same-skeleton pairs of 28. Whatever the knob does elsewhere, it did
nothing measurable to the engagement letters.

### What this settles

- The outline work **does** change the shape of authored prose at the arm
  level, by an amount that clears the like-for-like noise floor 7.7x. This is
  the first evidence on real prose rather than a scripted author, and M17b's
  claim that the mechanism was unproven is now answered.
- It changes it **partly by relocation**: same-skeleton pairs end up more
  similar than control's typical pair.
- It does **not** change word choice measurably.
- It did nothing to engagement letters.
- No individual pair comparison is trustworthy at this noise level.

What it does not settle, and no doc may imply otherwise: whether any of this
made the prose *better*. Both axes measure difference, not quality. The board
is the instrument for that question and has not run.

## THE BLIND BOARD, both arms, side by side

Two `cross_document_voice` reviewers, fresh contexts, neither told that an
experiment exists, that there is another arm, or which arm it held. Paths were
the neutral `scratch/arms/alpha` and `scratch/arms/beta`;
`scratch/arms/ASSIGNMENT.txt`, which names the arms, was moved out of the
reviewable tree first.

| | control (alpha) | treatment (beta) |
| --- | ---: | ---: |
| **variety score (0-10)** | **4** | **5** |
| blocker | **1** | **0** |
| major | 5 | 6 |
| minor | 2 | 2 |
| note | 1 | 1 |
| total findings | 9 | 9 |

**The direction favours the treatment on both counts that carry weight.** The
control drew a blocker; the treatment drew none, and its reviewer said so
explicitly: "No blocker is honest here: every individual document survives a
careful read." The control's blocker was the exemplar's failure mode exactly,
two kickoff memos nine years apart by different authors, "the same memo
re-skinned" with five parallel constructions in the same order.

**How much weight this can carry: not much on its own.** One reviewer per arm,
no calibration between them, on a 0-10 scale invented for this comparison. Two
uncalibrated readers scoring one corpus could differ by a point. The
blocker/no-blocker split is the sturdier signal, because it is a categorical
judgement each reviewer made against the same rubric, but it is still n=1.

**On the headline question the board did not discriminate at all.** Both
reviewers answered the dimension's own question the same way: yes, one person
appears to have written everything. Whatever the knob moved, it did not move
that verdict.

**Both reviewers independently rejected the lexical metric, unprompted.** This
is the most valuable thing the boards produced, because two fresh contexts
reached it separately, on different arms, with no theory supplied:

- Control's reviewer: "the low lexical number is the misleading one here: this
  reads as a generator with one idea successfully paraphrasing itself... A
  firm reusing a template would repeat its governing-law clause verbatim and
  vary the deal narrative; this corpus does the opposite."
- Treatment's reviewer: "the report's lexical instrument correctly finds
  nothing... the repetitions are never verbatim... which is the signature of
  one writer regenerating from one remembered shape rather than an
  organization reusing paper."

That is convergent, independent support for the premise behind
`orgsmith/review/structure.py`: on this corpus lexical overlap is a decoy and
shape is the signal. It also locates the residual convergence at the
sentence-move level, which is `rf:voice-3` territory and, per CLAUDE.md, beyond
both the structural axis and the outline work.

**What this is not.** It is not a false-positive-rate measurement. Both arms
are generated prose of unknown quality, so a reviewer finding nine things in
each tells us nothing about how often a board manufactures a finding against
prose that is fine. `board-negative-control` in `BACKLOG.md` gains a
measurement of *discrimination between two arms* and is **not** closed by it,
exactly as SPEC criterion five requires this write-up to state.

**Residual leak, disclosed.** The skill requires passing each org's real
validator summary so reviewers do not re-litigate oracle-proven facts. Those
differ between arms (27 rules run against 29), so a reviewer with deep
knowledge of this codebase could in principle infer which arm had extra knobs
on. Neither reviewer's report shows any sign of having done so, and neither
mentions knobs, rules, or an experiment. Recorded rather than hidden.

## THE TREATMENT ARM'S FULL BOARD: 5 blockers, and the run log was corroborated from the files

Six fresh-context reviewers, none told an experiment exists, none given any
finding in this log. Merged into the arm's `GENERATION-REPORT.md`.

| dimension | blocker | major | minor | note | total |
| --- | ---: | ---: | ---: | ---: | ---: |
| cross_document_voice | 0 | 6 | 2 | 1 | 9 |
| document_plausibility | 1 | 4 | 2 | 0 | 7 |
| finance_realism | 0 | 3 | 2 | 1 | 6 |
| graph_acl_naturalness | 0 | 5 | 1 | 1 | 7 |
| narrative_consistency | 3 | 7 | 1 | 2 | 13 |
| org_realism | 1 | 4 | 2 | 1 | 8 |
| **total** | **5** | **29** | **10** | **6** | **50** |

**Three dimensions independently raised REND-01 as a blocker**, two of them
verifying it in the rendered `.docx` binaries rather than the DocIR. Counts
given: 10, 12, and 6 documents. The `document_plausibility` reviewer supplied
the denominator that matters: "The other 80 placements handle it correctly, so
it is per-batch, not systematic." It reaches an executed engagement letter
(`d:0040`: "the candidate universe, which stands today at **12 acquisition
targets carve-out situations**").

`org_realism` diagnosed why nothing caught it: "The DocIR is innocent... this
is a fact-surface defect the author could not see. The validator is green
because the fact *is* present; presence is all it checks."

**The board corroborated this log's findings without access to it.** Every
item below was found independently, from the files:

| this log | found by | as |
| --- | --- | --- |
| REND-01 | org_realism, document_plausibility, narrative_consistency | blocker x3 |
| SCOPE-D | narrative_consistency, org_realism, finance_realism, document_plausibility | blocker + majors |
| SCOPE-A | org_realism, document_plausibility | `rf:org-5`, `rf:docplaus-3` |
| OUT-B2 (dates omitted) | document_plausibility | `rf:docplaus-6` |
| OUT-C (3-slide decks) | document_plausibility | `rf:docplaus-7` |

### SCOPE-D's remedy, corrected by the board

This log proposed fixing SCOPE-D by making `unit_range` and
`pipeline_top_range` nest. The `narrative_consistency` reviewer found
something better, and it changes the recommendation:

> "Four engagements (Morse, Beck, Ingram, and Blankenship's d:0036) reconcile
> the two figures explicitly and read correctly — **so the fix is a briefing
> constraint, not a ledger change.**"

Half the engagements handled the same ledger correctly by stating the
relationship explicitly. So the ranges are usable as they stand; what is
missing is a brief that tells the author what `scope` denotes relative to the
funnel. That is cheaper than re-deriving ranges and does not disturb any
committed org. **The remedy proposed under SCOPE-D above is superseded by
this one.**

### Findings that are not about the knobs, and are not new

Two reproduce known fleet-wide defects in a brand-new recipe, which is
evidence they are generator-level rather than recipe-level:

- **The people-graph seam the README documents for the exemplar.**
  `graph_acl_naturalness` found four instances of a person given named work in
  a document their ACL denies them (`d:0033` tasks James Lawson; he holds 15
  grants, none under `Engagements/`). Survived the M17 regeneration, and now
  survives into a fresh recipe.
- **The firm has no 2020, and here the prose knows it does.** `finance_realism`
  found `d:0048` (Jun 2020) with an analyst joining "from his kitchen table, as
  most of us still are" and `d:0049` noting "a good deal of the market went
  quiet this spring", against an FY2020 workbook making Q2 2020 the year's
  *largest* quarter, +22% on Q1, travel only 12% below 2019. Sharper than the
  exemplar's version, because the authored prose references the pandemic while
  the finance model sails through it. This is `event-simulation` in
  `BACKLOG.md` arriving with better evidence than it had.

Two more worth carrying, both confirmed from two dimensions independently:

- **No partner appears in any engagement document after 2015-08-31**, and
  neither partner can *read* a post-2015 mandate, while `d:0064` has the
  Managing Partner promising "I will run the engagement myself and will be at
  every session with your directors" (she appears in 0 of 44 engagement
  documents) and `d:0066` claims "the people whose names are on the engagement
  letter are the people who do the work".
- **Four of eight engagements commence on a non-working day**: three weekends
  plus 2016-07-04, which the recipe's own `business_calendar.holidays` lists.
  The calendar is declared and the engagement start dates do not respect it.

## AIRLOCK-01: the airlock stops the model transcribing a ledger value; it does not stop the model inventing a value the ledger does not own

The most consequential finding in this log, and it is about the project rather
than the turn. Found by comparing the control arm against its own replicate,
which is precisely what the replicate was bought for, and it paid off before
the comparison was even run.

**The measurement.** Nineteen documents have now been authored in *both*
control runs. Same recipe, same seed, same manifest (verified byte-identical),
same model, same effort, same prompt. Counting distinct multi-digit integers
appearing in prose:

| doc | alpha | gamma |
| --- | ---: | ---: |
| `d0014` (briefing deck) | 0 | 9 |
| `d0015` (meeting minutes) | 0 | 3 |
| `d0016` (status report) | 0 | 5 |
| `d0017` (meeting minutes) | 0 | 1 |
| **all 19 shared docs** | **0** | **18** |

The gamma worker built an explicit, internally consistent funnel and said so:
"238 universe / 61 screened (24 first tier, 37 second) -> May 5 deck 11
approached, 0 NDAs -> ... -> Aug 31 all 61 approached, 12 NDAs, 9 meetings, 3
indications, 2 live." Its alpha counterpart wrote none. Both deliverables
passed ingest.

**Why ingest accepted both, correctly.** The literal scan rejects a value the
*ledger owns* appearing in prose. `engagements.scope` is off in the control, so
the ledger owns no funnel counts, so there is nothing for the scan to match.
The airlock's guarantee is "the model never writes a value it was not shown",
and that guarantee held perfectly here: nothing was transcribed. What is not
guaranteed is the converse, and it is the part a consumer will care about:

> **A number can enter the corpus that no ledger owns, and therefore that the
> answer key cannot check.**

For a project whose stated value proposition is that `-metadata/` is the
answer key for everything in `<slug>/`, this is a real gap. A consumer
building an extraction eval against gamma's `d:0014` finds "238" in the
document and nothing in ground truth to score it against. It is not wrong, it
is unverifiable, which in a synthetic corpus is a different and worse
category.

**Worker-level, not gradual.** Control workers were inconsistent about this by
their own report. Two refused explicitly: "`engagements.scope` is null, so no
funnel counts exist in the ledger; I wrote no quantities of my own anywhere",
and "I deliberately used no invented counts... since inventing quantities could
contradict a scope ledger." A third built the funnel above. This is a binary
choice made once per worker with large content consequences, not smooth
phrasing variance.

**Three consequences for this turn's measurement.**

1. **The noise floor may be blind to the largest real difference between the
   two control runs.** `noise_floor` compares block shape and positional
   openers. A document that grows a nine-number funnel keeps its shape. So the
   floor could read small while the two runs differ in whether documents make
   quantitative claims at all.
2. **It confounds the treatment comparison in a way the standard did not
   anticipate.** The treatment arm carries funnel numbers *by construction*,
   from `engagements.scope`. "Treatment documents cite quantities and control
   documents do not" is therefore partly the knob and partly this coin flip,
   and on this evidence the coin lands on "invent them" some of the time.
3. **It is an argument in favour of the `engagements.scope` knob that is
   independent of prose quality.** Whatever the outline work turns out to have
   done, planting funnel facts in the ledger converts an invented, unverifiable
   number into a checkable one. That is the airlock working as designed, and it
   is a better reason to want the knob than anything the structural axis will
   report.

**Not fixed here.** The arm is mid-flight and this is a generator-level
question, not a deliverable-level one. The cheap mitigation is a brief-level
prohibition on inventing quantities when no count fact is briefed; the
thorough one is an ingest check that flags multi-digit integers in prose that
match no ledger value, which would be noisy and needs design. Recorded for the
write-up and for `BACKLOG.md`.

## Criterion three, verified: the control is exact and its residue is two knobs

Checked once both arms were rendered and assembled. Byte-identical across
arms: `foundation.json`, `ledger/finance.json`, `ledger/graph.json`,
`ledger/style_specs.json`, `ledger/acl.json`, the entire share tree of file
paths, and the manifest's doc ids, genres, dates and authors. Exactly two
artifacts differ, and both differences are additive and attributable:

- **`ledger/engagements.json`**: 48 facts added, none removed, none modified,
  no non-fact field touched. 8 engagements x 6 facts (scope, comparators, four
  pipeline stages). That is `engagements.scope` and nothing else.
- **`ledger/mention_map.json`**: 10 mention entries added, none removed, **all
  ten on `status_report` documents**, each adding an external client contact
  (an `xp:` id). That is `doc_culture.client_facing_reports` exactly.

Two predictions from the spec's context section settle against evidence:

- `outline_variety` "rides the skeleton id in `render_params`, not in a new
  `ManifestEntry` field" -- **confirmed**. The manifest's doc ids, genres,
  dates and authors are identical across arms.
- `client_facing_reports` "may move ACL grants and PERMISSIONS.md" -- **it did
  not**. `acl.json` is byte-identical. Adding an external contact to a mention
  plan moved no grant. Recorded because the spec flagged it as a risk to
  watch, and watching it cost nothing.

## An anecdote about shape, which is NOT the measurement

Recorded because it is a vivid illustration and for no stronger purpose. The
comparison that settles anything is `tools/ab_compare.py` run per
`docs/M17C-EVIDENCE-STANDARD.md`, and it has not been run.

The same work order (`author-0002`, six documents) in the two arms:

- **Control replicate**: the worker wrote the five onboarding records to one
  shared shape, and said so, citing the house norm: "the five onboarding
  records share the genre's shape (heading plus four paragraphs, three closing
  with a one-line sign-off) per the project's same-genre-shares-a-shape norm;
  variety is carried in openings, content angle per hire's persona, and the
  closing next step."
- **Treatment**: the same six documents were dealt four distinct skeletons
  (`co-history`, `or-role-table` twice, `or-welcome` twice, `or-checklist`).

That the knob changes what the plan asks for is already established from the
manifest and is not in doubt. What this does not show is whether the resulting
prose is more varied in any way that matters, or whether the variety survives
the pool cycling recorded under SCOPE-B. Two workers describing their own
output are not an instrument.

## Arm tallies

| arm | authored | batches | ingest rejections | validate |
| --- | --- | --- | --- | --- |
| alpha (control) | 59/59 | 13 | 0 | 27 run, 12 skipped, 0 errors |
| beta (treatment) | 59/59 | 13 | 0 | 29 run, 10 skipped, 0 errors |
| gamma (control replicate) | in progress | | 0 so far | |

Both finished arms: render 77/77, assemble 77 docs, acl 21 grants, report 0
off brief and 0 same-genre pairs flagged by the lexical proxy.

**Both knobs' validator rules passed their first live exercise.** The arms
differ by exactly the two rules the knobs own: `SCOPE-01` and `OUT-01` skip
visibly in the control (knobs off) and execute clean in the treatment (knobs
on), which is the AFF-01/STY-01 charter-grandfathering idiom working in both
directions rather than an artifact going missing.

**Twenty-six authoring batches, zero ingest rejections.** Stated precisely,
because it is easy to over-read: the enforcement is not over-tight, and it
never rejected a deliverable a reader would call conforming. It does **not**
follow that the skeletons were good. Every finding below is a case where a
skeleton was unsatisfiable, contradicted its own genre's contract, or forced
prose a real author would not write, and ingest accepted all of them, because
what it checks is block kinds and order rather than whether the briefed
sections were sensible to ask for.

## SCOPE-A: the scope profile is recipe-scoped, so seven of eight engagements get buy-side funnel vocabulary they do not fit

Found by the `author-0004` worker on the treatment arm's first batch, which
reported it rather than writing around it silently.

`ScopeProfile` is declared once per recipe and applied to every engagement:
`scope_facts_for(profile, eid, seed)` (`orgsmith/fabric/engagements.py:164`)
takes one profile and plants the same fact vocabulary under every engagement
id. `quillon-harbor`'s profile is buy-side M&A:

```yaml
scope:
  unit: acquisition targets
  pipeline: [targets screened, targets contacted, NDAs executed, offers submitted]
```

Every one of the org's eight engagements therefore carries
`f:<eid>.scope`, `f:<eid>.comparators`, and a four-stage
`f:<eid>.pipeline-*` funnel in that vocabulary. Exactly one engagement, the
Buy-Side Search for Morse PLC, has it as native language. The other seven do
not:

| engagement | why the vocabulary does not fit |
| --- | --- |
| Sell-Side Advisory | counterparties are acquirers; the seller has no "acquisition targets" |
| Fairness Opinion | has no deal funnel at all; it is a valuation opinion on one transaction |
| Growth Capital Raise | the pipeline is investors, not targets |
| Recapitalization Advisory | no target search |
| Management Buyout Advisory | the buyer is the incumbent management team |
| Carve-Out Advisory | the asset is known at the outset |
| Strategic Alternatives Review | the funnel is options, not companies |

The Fairness Opinion is the sharpest case: an engagement that by definition
has no acquisition funnel is planted with a four-stage one, so a document
citing those facts asserts something structurally false about its own
engagement.

**This is a design limitation, not a bug.** The knob does exactly what it was
built to do. The recipe comment shows its author reasoning carefully about
*plurality* ("no surface can render `1 acquisition targets`", floors above 1,
narrowest stage 3) and not at all about *kind-appropriateness*. What is
missing is that `ScopeProfile` has no per-engagement-kind variant, and
`fabric/engagements.py` has no notion of engagement kind to key one off:
the ledger's engagement records carry a name but no `kind` field.

**Why it is recorded and not fixed.** Criterion seven asks for the scope
facts whose rendered surface reads badly, and this is the answer to that
question. Fixing it needs either a per-kind profile map in the recipe or an
engagement-kind field in the fabric, both of which are their own unit of
work, and neither of which may land between two batches of the same arm.

**What it does and does not threaten.** It does not threaten the arms'
comparison: `engagements.scope` is absent from the control by construction, so
the defect exists only on the treatment side and is a property of the knob
rather than a confound between arms. It does mean the treatment arm ships
documents whose scope citations are vocabulary-mismatched on seven of eight
engagements, and any reading of the treatment arm's prose quality must know
that.

**Worker mitigation, noted so the prose is not over-credited.** The
`author-0004` worker wrote around the mismatch by choosing phrasing correct
under either reading ("we reviewed N companies against the criteria we set
with you", "we approached N of those") rather than asserting "targets". That
is a worker being careful, not the knob being right, and a worker that did not
notice would have written the mismatch straight through.

## SCOPE-B: the outline pool cycles on a fifth of all same-genre pairs, and the magnitude is now measured

The evidence standard anticipated this qualitatively and the instrument
already implements the split: `split_by_outline`
(`tools/ab_compare.py:192`) is the standard's first discriminating
comparison, and its docstring states the reading in advance. "If those still
score like the control's pairs, the outline work relocated the convergence
into groups of the pool size rather than reducing it, and that is the smaller
claim the standard says must be reported instead." Nothing below changes that
analysis. What was not known until the treatment plan existed is **how much of
the arm the split covers**, and it is a fifth:

| genre | docs | same-genre pairs | dealt the same skeleton | pool |
| --- | --- | --- | --- | --- |
| meeting_minutes | 13 | 78 | 15 | 4 |
| onboarding_record | 10 | 45 | 12 | 3 |
| status_report | 10 | 45 | 8 | 4 |
| engagement_letter | 8 | 28 | 7 | 3 |
| kickoff_memo | 8 | 28 | 4 | 4 |
| briefing_deck | 6 | 15 | 3 | 3 |
| company_overview | 4 | 6 | 1 | 3 |
| **total** | **59** | **245** | **50 (20.4%)** | |

The cause is arithmetic, not a defect: pools hold 3-4 variants and the larger
genres hold up to 13 documents, so `assign_outlines` cannot give every
same-genre pair a distinct shape and never claimed to. Its guarantee is that
no two *consecutive* same-genre documents share a skeleton, which is a
different and much weaker statement than the one a casual reader might take
from "outline variety". CLAUDE.md already warns against the stronger reading:
"'Impossible by construction' is an overclaim -- a finite pool cycles."

**The consequence for reading the result.** On the shape axis, those 50 pairs
were asked for the same sections in the same order, so they should score at or
near maximum shape similarity *by construction*. An arm-level mean over all
245 same-genre pairs therefore mixes two populations with opposite expected
behaviour, and could show the treatment arm as no better than the control, or
worse, for a reason that has nothing to do with whether the knob works. The
same-skeleton and different-skeleton subsets must be read separately, exactly
as the standard already requires of cross-batch and within-batch pairs. The
tool does this; this note records why it matters at this magnitude.

**Criterion one's pair floor is comfortably met.** The treatment arm scores
245 same-genre pairs against the required minimum of 120.

## OUT-A: skeletons that push against a genre's natural form

Reported by the `author-0002` worker, which authored six documents under four
distinct skeletons and flagged each tension rather than resolving it silently.

- **`co-history` forbids list blocks, while the same guidance asks a company
  overview to cover "service lines".** Service lines are the one thing a firm
  overview genuinely would bullet. The worker compressed them into a prose
  sentence, which reads acceptably, but this is the skeleton pushing against
  the natural form of the genre rather than varying it.
- **`or-role-table` mandates a table where the `onboarding_record` genre
  default says "2-4 short paragraphs, no sigblock".** The worker followed the
  skeleton, as briefed. A responsibilities table in an internal onboarding
  note is plausible, so this is a live tension rather than an implausible
  demand, but the skeleton and the genre default do contradict each other and
  the brief does not say which governs.
- **`target_words` counts table cells.** Two documents at a 450-word target
  carry noticeably less prose than prose-only documents at the same target,
  because the table's cells consume the budget. This is worth knowing before
  the length-against-brief metric is compared across arms: the treatment arm
  deals tables that the control arm does not, so equal `target_words` does not
  mean equal prose volume.

## SCOPE-C: the mismatch is not cosmetic, it silently decides what an engagement IS

This is the escalation of SCOPE-A and the most consequential finding in this
log. Earlier instances cost a phrasing choice in one document. This one set
the interpretation of an entire six-document engagement arc.

The engagement is **Carve-Out Advisory for Browning, Duffy and Santos**
(E-2019-001), and its sole client contact is BDS's VP Finance. Its scope facts
are `f:E-2019-001.scope` hinted "count of acquisition targets", plus targets
screened, targets contacted, and NDAs executed. Those are buy-side search
facts.

The fleet's own naming convention settles what the engagement should mean.
Every engagement in this org is "`<mandate type>` for `<client>`": Sell-Side
Advisory for Armstrong, Silva and Dyer; Buy-Side Search for Morse PLC;
Management Buyout Advisory for Blankenship Inc. In each, the client is the
party doing the named thing. "Carve-Out Advisory for BDS" therefore reads as
**BDS divesting a unit**, which is a sell-side posture, and a seller does not
screen and contact acquisition targets.

The `author-0009` worker could not write both and said so: "If the ledger
intends the sell-side reading, the whole batch is framed the wrong way round;
the `.scope` hint is what forces the choice." It reported having framed all six
documents with BDS as the acquirer.

**Corrected against the authored text, 2026-08-10.** This entry originally
repeated that self-report as fact. Checking the shipped DocIR does not support
it at that strength. Counting framing vocabulary in the carve-out documents
across all three arms:

| doc | alpha (control) | gamma (replicate) | beta (treatment) |
| --- | --- | --- | --- |
| `d0040` letter | separat:5 | divest:2, seller:2, disposal:1, separat:3 | seller:1, separat:2 |
| `d0045` status | separat:1, **acquir:3** | seller:1, separat:2 | seller:1, separat:3 |

The treatment arm reads as separation/sell-side, much like the controls, and
the one document with heavy acquisition vocabulary is in the **control** arm.
So the mismatch did not flip the engagement's framing in the delivered prose,
and the strong form of this finding is withdrawn.

**What survives, and it is narrower.** The funnel is still described as the
firm screening and contacting candidates, which is buy-side *activity*
attached to a mandate whose name implies the other side, and the worker did
have to choose a reading in order to write at all. That is a real cost of the
mismatch. It is a strain visible to a careful reader, not a corpus asserting
the opposite of its own engagement name.

**Why the correction matters more than the finding.** The self-report was
confident, specific, and wrong about its own output. Worker reports are
evidence about what a worker *believed it was doing*, and this log leans on
them heavily. Every finding here that rests only on a worker's description of
its own text should be read at that discount until checked against the DocIR,
which is cheap and was not done before this entry was first written.

## OUT-C: skeletons that contradict their own genre's stated contract

Also from `author-0009`, and distinct from OUT-B because these are not
unsatisfiable, they are satisfiable and wrong.

- **A skeleton that produces a document below its genre's stated floor.** The
  `briefing_deck` default says "4-6 slides total" and "each slide is one
  heading block followed by one list block of 3-5 tight bullets". The
  skeleton's six items yield exactly **three slides**, and it puts the
  quantities table second, so the title slide carries no bullets and the
  audience's first content is a bare numbers table. The genre states a floor;
  the skeleton breaches it; ingest checks neither.
- **Minutes with no action items.** `mm-*` as dealt to `d:0044` contains no
  action-item block at all (attendees / session narrative / unresolved), while
  the genre default calls for "a table or list of action items with owners"
  and the same skeleton forbids tables. The worker carried ownership inside
  the unresolved paragraph rather than adding an unbriefed block, and flagged
  minutes recording no action list as the least realistic artifact it
  produced.
- **A risk register forced out of tabular form.** `sr-*` forbids tables while
  asking for risks "each with its owner and its trigger". A real risk register
  is a table. Rendered as a list of `Risk. Owner: X. Trigger: Y.` items.

The pattern across OUT-A, OUT-B and OUT-C is one thing: **the outline pools
were written independently of the genre defaults, the persona style specs, and
the airlock's rules, and nothing reconciles them.** Where they disagree the
brief tells the worker the skeleton wins, so the skeleton wins even when it is
the wrong call. That is a fixable authoring-brief problem rather than an
argument against outline variety, but it is not fixed today and every
treatment-arm document was authored under it.

## CONF-02: a worker independently drafted a sibling's bullet verbatim, then deleted it because it had read the sibling

This is the single most important caveat in this log for reading the
treatment arm's numbers, and it upgrades CONF-01 from "a confound exists" to
"the confound is actively suppressing the thing being measured".

The `author-0007` worker was dealt four skeletons that already had an authored
sibling in this arm. It read each before writing, and reported what it then
did (emphasis added):

> "d0016 in particular was near-isomorphic to d:0036's brief; I deliberately
> avoided its meta-labelled paragraph openers, its 'It rests on... It rests
> on...' anaphora, its 'Prepared by X' sign-off... Same for d0015's 'The first
> item was... The second item was...' and **d0014's opening bullet, which was
> verbatim the bullet I had first drafted for d:0034**."

Two documents, different authors, different batches, dealt the same skeleton
(`bd-bulleted`), produced **the identical opening bullet independently**. The
second one shipped different text only because its author had read the first.

What this establishes, and it is not what the turn set out to test:

1. **Same-skeleton pairs converge lexically, not merely structurally.** The
   outline knob constrains what a document contains; the evidence standard
   says a skeleton "constrains what a document contains, not which words it
   uses", and treats the lexical axis as the more informative one for exactly
   that reason. Here the shared skeleton drove two authors to the same words.
   That is the convergence mechanism operating one level deeper than the knob
   was designed to address.
2. **The treatment arm's measured convergence understates what the knob alone
   produces.** Workers are reading siblings and actively de-duplicating
   against them. Every such deletion removes an instance of exactly the
   convergence the structural and lexical axes are trying to detect. The arm's
   numbers are therefore biased *favourably*, by an unmeasured amount, through
   a mechanism that is not the treatment.
3. **The bias is not symmetric between arms in any way this run can quantify.**
   Control workers de-duplicated too (one cut shared six-grams among its own
   documents from 34 to 3). But the treatment arm has same-skeleton siblings,
   which are *more* obviously worth checking against and were explicitly
   sought out here, so there is no basis for assuming the two arms were
   de-duplicated to the same degree. This does not invalidate the comparison;
   it means a small treatment-favourable gap cannot be distinguished from
   differential de-duplication, and the write-up must say so.

Nothing here is fixable within this run, and it should not be fixed by
instructing workers to stop reading siblings: that would trade a measurement
confound for worse prose, and the airlock does not forbid the reads. The
honest handling is to report it as a bound on the claim.

## OUT-E: the anti-repetition guarantee is intra-genre, and the measurement is too, so cross-genre shape convergence is invisible to both

Found by the `author-0012` worker, and it identifies a blind spot shared by
the knob and the instrument that scores it.

That batch held two documents, `d:0060` (`onboarding_record`) and `d:0066`
(`company_overview`). They were dealt **structurally identical skeletons**:
item 1 a paragraph, item 2 a table, item 3 a paragraph, each carrying the same
"NO list block of any kind, anywhere" prohibition. Both were authored by the
same person. The worker's own summary: "this batch contributes zero shape
variety on its own."

This is not a bug in `assign_outlines`, which promises only that no two
*consecutive same-genre* documents share a skeleton. Two different genres may
be dealt structurally identical shapes, and nothing prevents it.

**The part that matters for this experiment**: `orgsmith/review/structure.py`
scores **same-genre pairs**. A pair like `d:0060`/`d:0066` is cross-genre, so
it is not scored at all. If the outline pools happen to converge on a common
shape across genres, the structural axis cannot see it, in either arm. So
neither "the treatment arm improved" nor "the treatment arm did not" can be
claimed about cross-genre shape on this measurement, and the write-up must not
imply otherwise.

Worth stating plainly because it cuts against the knob's own framing: an
outline pool that reduces intra-genre repetition while quietly reusing the
same three-block shape across genres would score as a success on the axis this
turn is measuring, and a reader browsing the share would still see one shape
everywhere. Nothing in this run establishes that this happened. It establishes
that the measurement could not tell us if it had.

## SCOPE-D: the scope profile's own quantities do not nest, independent of engagement kind

Found by the `author-0010` worker authoring the Fairness Opinion, and
confirmed against the charter. This one is not about vocabulary fit; it is an
internal incoherence in the profile that would exist even on a buy-side
mandate where every noun is right.

```yaml
unit_range:         [9, 16]     # f:<eid>.scope       -> "N acquisition targets"
comparator_range:   [22, 40]    # f:<eid>.comparators
pipeline_top_range: [60, 110]   # f:<eid>.pipeline-targets-screened
pipeline_retention: [0.40, 0.65]
```

`scope` yields 9-16 "acquisition targets" while the funnel *head* yields
60-110 "targets screened", and the funnel then narrows from there (the recipe
comment computes its worst-case narrowest stage as `60 * 0.40^3 = 3`).
**Nothing defines the relationship between `scope` and any pipeline stage.**
`scope` is not the universe (it is far smaller than the screened count), not
the head of the funnel, and not obviously any of its stages.

A document that cites both invites the reader to nest them, and the numbers do
not support any nesting the prose might imply. The `author-0010` worker
handled this correctly and deliberately: it "wrote no 'of which' arithmetic
linking `.scope` to any pipeline stage", and cited only the stages its
engagement position allowed. That is a worker navigating around an
under-specified ledger, and a worker that *did* write the natural "we screened
91 targets, of which 15 remain in scope" sentence would have produced a
document whose arithmetic no ledger backs.

The recipe's own comment shows the gap: it reasons carefully about **plurality
floors** ("no surface can render `1 acquisition targets`") and not at all about
whether the quantities are mutually consistent. Two facts can each be
individually valid and jointly meaningless, and no validator rule reads a pair.

## CONF-01: cross-batch sibling reading, self-reported, and what it does and does not threaten

The `author-0010` worker volunteered this without being asked, which is worth
recording in itself:

> "Before drafting I read one sibling reply in this arm
> (`reply-wo-author-0001.json`) to learn the deliverable JSON conventions, and
> grepped sibling files for governing-law phrasing. If this arm is measuring
> inter-worker convergence, that read is a confound worth knowing about; I
> wrote my own prose and did not copy phrasing."

This is the third independently observed instance of cross-batch sibling
reading in this project, after the two recorded in
`docs/M17C-EVIDENCE-STANDARD.md`, and the first that names the confound it
creates before anyone asked. It is also the live evidence behind the README
correction made this turn: a worker is *briefed* only its own batch, but the
arm's DocIR sits on disk and nothing forbids reading it.

**What it threatens:** any claim about a document's absolute independence
from its siblings, and therefore any absolute reading of either arm's
convergence numbers.

**What it does not threaten:** the between-arm comparison. Control-arm workers
did the same thing (one reported reading an earlier batch's ingested reply to
avoid repeating its section names), so both arms carry the property, and the
evidence standard's second amendment already narrowed the claim on exactly
this ground before either arm was finished. This entry adds a third data point
and a clean self-report, not a new problem.

## REND-01: a doubled noun in ingested prose, and ingest cannot see it

The one outright **rendering defect**, as opposed to a design limitation, and
on measurement it is systemic rather than the one-off it was first reported
as. Raised by the `author-0011` worker about another worker's batch, then
measured across the whole treatment arm by resolving every count fact's
rendered noun and checking the words that follow its placeholder.

**Eleven occurrences across eight documents**, all ingested, all validated
clean, all rendered:

| doc | placeholder renders as | author then wrote |
| --- | --- | --- |
| `d0012` | 40 comparable transactions | comparable transactions |
| `d0020` | 15 acquisition targets | candidate targets |
| `d0021` | 15 acquisition targets | targets |
| `d0022` | 15 acquisition targets | acquisition targets |
| `d0022` | 25 comparable transactions | comparable transactions |
| `d0024` | 15 acquisition targets | targets |
| `d0024` | 25 comparable transactions | transactions close |
| `d0038` | 13 acquisition targets | acquisition targets |
| `d0038` | 33 comparable transactions | comparable transactions |
| `d0045` | 26 comparable transactions | comparable transactions |
| `d0046` | 64 targets screened | candidates screened |

So the corpus ships sentences reading "40 comparable transactions comparable
transactions" and "15 acquisition targets acquisition targets". This is not a
subtle infelicity; it is visibly broken English in a corpus whose selling
point is that it reads like a real firm wrote it.

**A compound instance worth quoting**, from `d0045`, which fails three ways in
one sentence and is the single clearest artifact this run produced:

> "Of the `{{scope}}` candidates in the approved universe, `{{screened}}` have
> been screened against the criteria agreed with `{{client}}` at kickoff, and
> `{{contacted}}` of the survivors have..."

resolving to:

> "Of the **12 acquisition targets** candidates in the approved universe,
> **64 targets screened** have been screened ... and **32 targets contacted**
> of the survivors have..."

Three doubled nouns, and an arithmetic impossibility on top: 64 screened out
of a universe of 12. That last part is **SCOPE-D arriving in shipped prose**,
and the hazard is live in **ten documents** that cite `scope` and
`pipeline-targets-screened` together (`d0008`, `d0012`, `d0016`, `d0024`,
`d0036`, `d0038`, `d0045`, `d0055`, `d0062`, `d0068`).

Earlier detail, retained: `d:0021` alone carries four occurrences, not the one
originally reported.

`render_count` renders a count fact as "`<n> <noun>`", so
`f:E-2016-001.scope` resolves to "15 acquisition targets". The author then
wrote a noun after the placeholder:

| authored | renders as |
| --- | --- |
| `scoped that program at {{...scope}} candidate targets` | 15 acquisition targets candidate targets |
| `an acquisition program scoped at {{...scope}} targets` | 15 acquisition targets targets |
| `The program remains scoped at {{...scope}} acquisition targets` | 15 acquisition targets acquisition targets |
| `remains scoped at {{...scope}} targets` | 15 acquisition targets targets |

**Ingest accepted all four**, and it is right that it cannot catch them with
its current rules: the placeholder is correct, briefed, and unduplicated, and
the literal scan looks for ledger *values* in prose, not for a noun that
duplicates the one the placeholder will supply. The defect exists only in the
resolved surface, which nothing reads at ingest time.

This is a fact-surface trap the knob created: a count fact whose rendering
carries its own noun invites an author to supply the noun too, and the more
the vocabulary mismatches the engagement (SCOPE-A), the more an author
reaches for a corrective noun of its own. Both instances here are on
E-2016-001, the recapitalization that drew the vocabulary complaint.

A `{{fact:...}}`-adjacent duplicate-noun check at ingest is mechanical and
cheap, and would have caught all four. Recorded, not fixed: the arm is
mid-flight.

## OUT-D: the outline/genre contract has exactly one enforced intersection, and it is guarded by a comment

The `author-0011` worker raised a structural concern worth chasing down: if a
`meeting_minutes` outline ever forbade both `list` and `table`, the genre
check and the outline check would deadlock and the document would be
unsatisfiable. I checked it rather than assuming either way.

`_check_doc` hard-requires blocks for exactly three genres
(`orgsmith/authoring/ingest.py:220,224,229`):

- `engagement_letter requires a sigblock`
- `meeting_minutes requires an attendee/action list or table`
- `briefing_deck requires at least 2 heading blocks (slides)`

Six shipped outlines forbid both `list` and `table`: `km-risk-first`,
`km-narrative`, `sr-narrative`, `el-terms-first`, `or-welcome`, `co-history`.
Cross-referencing the two lists, **no deadlock exists today**:

- The four in `kickoff_memo`, `status_report`, `onboarding_record` and
  `company_overview` have no hard block requirement to collide with.
- `el-terms-first` is in the one genre that does, but its requirement is a
  *sigblock*, which no outline forbids.
- No `meeting_minutes` variant forbids `list` at all, and the registry says
  why in a comment at `orgsmith/docplan/registry.py:448`: "No variant forbids
  `list`: MENT-01 reads the attendee names".

So the guard is real and deliberate. **It is also only a comment.** Nothing
tests that a future `mm-*` variant cannot forbid `list`, and the failure it
would produce is an unsatisfiable brief discovered live, mid-run, at whatever
scale the run happens to be. The registry already distinguishes a directive
("a suggestion an author can drift from") from a forbidden block, and this is
the place where that distinction becomes load-bearing across two files that
do not know about each other. A test asserting that no outline forbids every
form its genre's hard check accepts is a few lines and would make the comment
enforceable.

Related, and it explains OUT-C's deck finding: the `briefing_deck` hard check
is "at least 2 heading blocks", while the genre's stated shape is "4-6 slides
total". The three-slide deck the skeleton produced clears the enforced floor
and breaches the advisory one, which is exactly what the registry's
directive-versus-forbids distinction predicts. The genre's stated shape is not
a contract.

## OUT-B: three skeletons that could not be satisfied as briefed

Reported by the `author-0005` worker. These are the criterion-seven cases
proper: not a skeleton that merely fought the genre, but one that briefed
something unsatisfiable or something a real author would not write. Ingest
accepted all three documents, because what ingest enforces is block kinds and
order, not whether the briefed sections were reasonable to ask for.

- **A skeleton item that cannot be satisfied without breaking a hard rule.**
  `el-*`'s first item asks for "the client's inside address" while the work
  order's hard rules say "Do not invent people, organizations, addresses,
  amounts, or dates." There is no address in the ledger to place. The worker
  wrote recipient name, title and company and omitted street, city and postal
  lines, which is the closest satisfiable reading, and said so. The skeleton
  and the invention rule are in direct contradiction and nothing in the brief
  says which governs.
- **A skeleton that orders the document in a way its own genre default and its
  author's persona both contradict.** `km-owner-table` requires the workstream
  table as the *first* block. The genre default in the same guidance string
  says "Open with a short paragraph on objectives", and the briefed persona
  habit for that author is "sets context in a sentence before making any
  request". The worker followed the skeleton, as instructed, and the result is
  an internal kickoff memo that opens cold on a grid with the table's header
  row as its only orientation. The worker's own judgement, recorded: "A real
  associate would put one sentence above it."
- **A skeleton that assumes a predecessor document the plan did not create.**
  `sr-*` item four asks for "what changed in the risk picture since the last
  report" on what is the *first* status report of its engagement. The worker
  referred to "our last written update" and "the last working session" rather
  than inventing a predecessor status report. A skeleton dealt by genre does
  not know a document's position in its engagement's own sequence.

A fourth instance of the skeleton-versus-persona tension already recorded
under OUT-A: `el-*` and `km-owner-table` forbid list blocks while that
author's persona "prefers numbered lists over bullet points", resolved by
enumerating in prose.

### OUT-A1: the persona-versus-structure tension is NOT created by the outline knob

Recorded to stop OUT-A being over-read, and found on the arm that has no
skeletons at all. A control-replicate worker authoring the fairness opinion
reported: "three docs carry the author habit 'avoids lists entirely' while
their genre guidance requires a list block (kickoff memo) or strict slide
lists (deck); I let genre structure govern and expressed the habit as
prose-heavy sections elsewhere."

That is the same conflict OUT-A attributes to skeletons, occurring with
`outline_variety` off, between the **persona style spec and the genre default**.
The M16 style layer and the genre registry already disagreed with each other;
the outline pools add a third voice to an argument that was already running.

So the honest reading of OUT-A is narrower than it first appears: the
skeletons did not introduce persona-structure conflict, they added to it. What
the skeletons *did* introduce, and what has no pre-existing analogue in the
control, is the OUT-B class, briefs that cannot be satisfied at all, and the
OUT-C class, briefs that breach their own genre's stated contract. Those two
are properly charged to the knob. The persona tension is not, and the
write-up must not bill it that way.

### OUT-B1: the category behind two of these, skeletons that ask for content the airlock forbids inventing

Two of the unsatisfiable cases are the same failure at different genres, and
it is worth naming as a category because it will recur in any recipe:

| skeleton item | what it asks for | why it cannot be written |
| --- | --- | --- |
| `el-*` item 1 | the client's inside address | no address exists in any ledger; inventing one is a hard-rule violation |
| `mm-action-table` | actions, owners and **due dates** | no date fact is briefed for the doc; any literal calendar date is rejected |

Both were resolved by writing the satisfiable part and omitting the rest
(name/title/company with no street; relative dues such as "This week",
"Before the first call"). The `author-0001` worker stated the cost plainly:
"A real author would likely write real dates here; the airlock makes that
impossible."

The skeletons were written as descriptions of what these genres contain in
life. The airlock's rule is that the model never writes a value the ledger
owns. Where a genre's natural content is a value no ledger holds, the two are
irreconcilable and the skeleton loses. This is not an argument against the
airlock, which is the project's foundation; it is a statement that the outline
pools were authored without reference to what the airlock permits, and that
some pool entries are therefore unsatisfiable by construction.

### OUT-B2: a related realism cost that is not the outline knob's fault

Recorded here because it was found on this arm, though it applies to any arm.
The `author-0001` worker omitted the Date line from a kickoff memo's header,
because the memo's own date falls within two weeks of `f:E-2014-001.start` and
writing it literally risks colliding with that fact's rendered value, which
ingest rejects. All six of that batch's documents are free of literal calendar
dates for the same reason.

Real memos carry Date lines. The literal scan cannot distinguish "the document
states its own date, which is a property of the document" from "the document
transcribes a ledger value", so the safe authorial move is to omit dates
entirely. The control arm is subject to this identically, so it is not a
confound; it is a standing realism cost of the enforcement, and it is the kind
of thing a board reading either arm may report as a defect without knowing why
it is there.

### Deck shape under `bd-data-led`

The skeleton requires the quantity table as the deck's *second* block, so the
title slide carries no body of its own and the table lands directly beneath the
title; item 4 then puts a ~180-word prose paragraph on a slide. The
`author-0001` worker followed it exactly and recorded that "a real deck author
would give the table its own titled slide and cut the prose to bullets or
speaker notes". Anything else would displace the table from second position,
which the skeleton forbids.

## SCOPE-A, independently confirmed three times, and what the mismatch costs in prose

Three workers in fresh contexts reached this finding on three different
engagements without being told the others had: `author-0004` on the Sell-Side
Advisory (E-2014-001), `author-0005` on the Recapitalization Advisory
(E-2016-001), and `author-0001` again on the Sell-Side Advisory. The
`author-0001` worker put it most compactly: "In a sale, the counterparties are
buyers", and phrased around the ledger noun with "the buyer universe, which we
currently size at {scope}". That three independent readers all flagged it, and
all chose to write around it rather than through it, is the strongest evidence
in this log that the mismatch is real rather than a matter of taste.

**The finding has an accidental negative control, and it holds.** Exactly one
of the org's eight engagements is a buy-side search, the Morse PLC mandate
(E-2015-001), and it is the one engagement whose kind the scope vocabulary
actually fits. The `author-0003` worker authored that engagement's whole
six-document arc, scrutinised six skeletons closely enough to report two
unrelated stylistic tensions, and reported **no scope mismatch at all** and
"nothing in any skeleton struck me as something a real author would not
write". So the workers are not simply complaining about everything put in
front of them: the seven mismatched engagements drew complaints and the one
matched engagement did not. That asymmetry is what distinguishes a real defect
from reviewer noise, and it arrived without anyone designing for it.

The `author-0005` worker's resolution is the part worth recording, because it
shows the cost. It reached the same finding on the Recapitalization Advisory,
naming
`f:E-2016-001.scope`, `.pipeline-targets-screened` and
`.pipeline-targets-contacted` as buy-side vocabulary attached to a recap.

Its resolution is the part worth recording, because it shows the cost. The
worker made the facts cohere by writing the mandate as "a recapitalization
whose new capital funds an add-on acquisition program", which makes the target
funnel the growth plan attached to the recap and keeps all five documents
consistent. It labelled this itself: "That is an authorial reconciliation, not
a fix: if the recipe intended a pure recapitalization, the scope and pipeline
facts are attached to the wrong engagement kind."

So the mismatch does not surface as a visibly wrong sentence. It surfaces as
**invented narrative whose only job is to justify a fact the ledger planted
under the wrong engagement**. That is worse than a bad sentence for a corpus
whose value proposition is that the ledger owns the facts: the prose is now
carrying a story the ledger never authorised, generated to rescue the ledger's
own mistake. A reader auditing the corpus against the answer key would find
the numbers correct and the premise fabricated.

## MENT-A: a required mention with no sigblock forces a self-naming byline

Also from `author-0002`. Every `onboarding_record` in that batch requires the
literal surface "Heather Delacruz" while she is the sole author and the genre
forbids a sigblock. The only remaining device is a self-naming byline inside
the prose ("Prepared by Heather Delacruz, Managing Partner"). It is realistic
for an internal file note, but it is a constraint artifact rather than an
authorial choice, and it recurs across four documents by design of the briefs.
The worker varied its phrasing and position. This is the same family as the
recorded mail residual in CLAUDE.md, where a required body mention produces a
surface a real author would not have chosen, and it is recorded here for the
same reason: the mention model requires a surface without knowing what device
the genre leaves available to carry it.

## Disposition, 2026-10-13 (M17d)

Added after the fact, and changes nothing above: every finding in this log
stands as recorded. This is where each one went, so none is lost in a log
nobody re-reads.

| finding | disposition |
| --- | --- |
| REND-01, a count placeholder followed by its own noun | **closed** for the repeated-noun case: ingest rejects it and the brief says the placeholder renders its noun (`8c69f89`); replayed over `beta`, the check flags exactly the eleven listed above. A different noun after a count stays open as BACKLOG `count-placeholder-followed-by-another-noun` |
| SCOPE-A and SCOPE-C, one vocabulary for every engagement | **closed** by `engagements.scope_by_service` (`3f7edbb`), adopted by the tenth org |
| SCOPE-D, scope and funnel counts that do not nest | **closed** two ways: the brief forbids relating them (`8c69f89`), and the tenth org's recipe ranges every unit above its funnel's top |
| SCOPE-B, the outline pool cycles | open, inside BACKLOG `cross-document-voice` |
| OUT-A to OUT-E, skeletons against their genre | open, BACKLOG `outline-skeletons-against-their-genre` |
| MENT-A, the self-naming byline | open, BACKLOG `mention-without-a-device` |
| AIRLOCK-01, invented quantities | **measured** in `report` (`ab207cd`); prevention open, BACKLOG `airlock-permits-invented-quantities` |
| engagements starting on weekends and a declared holiday | **closed** by `business_calendar.engagement_starts` (`882062f`) |
| no partner on any engagement after 2015 | **closed** by `engagements.oversight_titles` (`cb65b2f`) |
| the firm has no 2020 | **closed** as a capability by `finance.era_shocks` (`29fd739`); BACKLOG `exemplar-has-no-2020` records that its second-org criterion fired |
| the people-graph seam | open, BACKLOG `mention-filler-acl-seam` |
| CONF-01 and CONF-02, sibling reading | recorded in BACKLOG `cross-document-voice` at M17c |
