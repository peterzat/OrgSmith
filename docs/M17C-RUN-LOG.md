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

The `author-0009` worker could not write both, said so, and chose the reading
the facts permit: it framed all six documents with **BDS as the acquirer**,
buying corporate carve-outs out of larger parents. Its own words: "If the
ledger intends the sell-side reading, the whole batch is framed the wrong way
round; the `.scope` hint is what forces the choice."

**Why this is worse than the earlier instances.** The ledger owns facts, and
prose is supposed to be replaceable around them. Here a fact *hint* reached
past the sentence it belongs in and determined the client's role in its own
transaction across six documents. Nothing rejected it, because nothing checks
that an engagement's facts agree with its name: `SCOPE-01` recomputes that the
planting matches the charter, not that the vocabulary matches the mandate. The
validator is green on an engagement whose documents describe the client doing
the opposite of what the engagement is called.

For a project whose stated hard rule is "facts are load-bearing; prose is
replaceable", this is the load-bearing part bearing the wrong load. The
remedy is the same one SCOPE-A needs (a per-kind scope profile, or an
engagement-kind field the profile can key off), and it is worth noting that
the cheapest partial mitigation is unrelated to either: **an engagement whose
name implies a side should not be dealt pipeline facts describing the other
side**, which is checkable without any new modelling.

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

The one outright **rendering defect** found so far, as opposed to a design
limitation. Reported by the `author-0011` worker about another worker's
already-ingested batch, and confirmed by inspection: `d:0021` in
`reply-wo-author-0005.json` carries four occurrences, not the one reported.

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
