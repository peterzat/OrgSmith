# Model A/B: does the authoring model actually matter?

The README told people to "use the strongest model available to you." That
was folklore: plausible, repeated, never measured. This is the measurement.

**Result: the folklore was right, and the gap is not subtle.** One model
produced a corpus a blind reviewer said it "would take a deliberate effort
to catch out." The other produced one the same reviewer refused outright.
**Both validated clean under all 29 rules.**

## Setup

`ab-probe` (Halloway Reed Advisors LLC), a 5-person consultancy, 11 planned
documents / 9 authored, 2019-2022. Deliberately **not committed** — it
lives in gitignored `scratch/`, so it raises no frozen-fixture question.

The control is exact. Both arms ran the same recipe at the same seed, so
`docplan/manifest.jsonl` and every ledger are **byte-identical across
arms** (verified by `diff -r`). Same briefs, same facts, same target word
counts, same required mentions. The only variable is the model that
answered the work orders. Both arms ran the real `/forge` procedure: fresh
context per batch, one enrichment pass plus three authoring batches.

| | Arm A | Arm B |
| --- | --- | --- |
| model | `claude-opus-4-8[1m]` | `claude-haiku-4-5-20251001` |
| self-reported effort | `xhigh` | `standard` |
| board reviewer | `claude-opus-4-8`, held constant | same |

## What the deterministic side saw

| measure | Arm A | Arm B |
| --- | ---: | ---: |
| **validate** | 20 rules, **0 errors** | 20 rules, **0 errors** |
| authored docs | 9 | 9 |
| total words | 2,909 | 1,504 |
| mean words/doc | 323.2 | 167.1 |
| mean ratio to brief | **1.16** | **0.60** |
| docs off brief | **0 / 9** | **8 / 9** |
| same-genre pairs flagged | 1 (`d:0001`/`d:0008` @ 0.2833) | 0 (top pair 0.041) |

**The validator cannot tell these two corpora apart.** Identical rule
counts, zero errors, both arms. Every planted fact lands where it should,
every required name appears, every formula ties out — in a corpus a
knowledgeable reader rejects on sight. This is the clearest available proof
of the gap M7 exists to close: the 29 rules verify that documents agree
with their ledgers, and that is all they verify.

**The metric can tell them apart, decisively, for free.** Arm B writes at
60% of what its briefs asked, with 8 of 9 documents off brief; Arm A lands
at 116% with none. That is a no-model, no-token check that separates the
arms unambiguously — the cheapest quality signal in the system.

## What the board saw

Reviewers were blind: same prompt, same dimension, same reviewer model,
told nothing about the experiment.

**Arm A — 1 minor, 2 notes, 0 majors:**

> Would a knowledgeable reader believe a real firm produced this corpus?
> **Yes, and it would take a deliberate effort to catch out.** [...] The one
> thing that gives it away is the shared prose reflex above — everyone in
> this firm has the same wit — which reads less like a machine than like a
> novelist who could not stop writing good lines for characters who should
> not have them.

**Arm B — 2 majors, 2 minors:**

> **No, a knowledgeable reader would not believe a real firm produced
> this.** The corpus is too thin to survive first contact — nine documents
> totaling 1,504 words as a consultancy's entire 2019-2022 output, with an
> "EXECUTED" engagement letter running 125 words and no recipient address
> on it. [...] nobody in the firm has a personality, no engagement ever has
> a problem [...] and the seams between generation batches are visible as
> abrupt template amnesia.

The board and the metric agree, independently, in the same direction.

## Three findings worth more than the headline

**1. Low similarity is not a quality signal — it is inverted.** Arm B
scored 0.041 same-genre overlap against Arm A's 0.283, and Arm B is the
worse corpus. Read naively, "less repetition" looks like a win. It is not:
Arm A's two engagement letters share a template *because a real firm's
letters do*, and Arm B's share nothing because they are too thin to share
anything. This independently reproduces the board's calibration finding
(`docs/REVIEW-CALIBRATION.md`): **a similarity metric can only flag prose
that repeats, and is structurally blind to prose that fails to repeat where
house style requires it.** Never read a low similarity score as health.

**2. Self-reported provenance is demonstrably unreliable — as designed
for.** Arm B reported its effort as `standard` while the session it ran in
reported `xhigh`, and it skipped the `generator` stamp on its enrichment
batch entirely (3 of 4 batches recorded, versus Arm A's 4 of 4). The weaker
model partly ignored the instruction to report itself and partly reported
something else.

This is the empirical vindication of the spec's load-bearing design call.
Had any validator rule trusted the `generator` field, it would now be
enforcing a value the model made up. Provenance is a record, not an oracle,
and this is why. The system degraded exactly as intended: the missing stamp
reports "unrecorded", the unknown effort ranks as unknown rather than
below-floor, and nothing failed.

**3. The board found a real pipeline bug, in a lane no one assigned it.**
Arm B's reviewer noticed that the PDF renderer silently flattens `\n`
inside a paragraph block while the DOCX renderer honors it as `<w:br/>`.
Verified independently: `pdf.py:90` emits `<p>{text}</p>`, where HTML
collapses newlines to spaces, and python-docx does emit `<w:br/>`. It
affects the committed fixture `gladepoint-strategies` `d:0008`, a PDF whose
addressee block renders as one smeared line. It validates clean because no
rule checks line breaks. Filed to BACKLOG.md; out of scope for M7.

## Limits

- **n = 1.** One org, one model pair, one run each. Directionally
  overwhelming, statistically nothing. This establishes a default with
  evidence behind it, not an effect size.
- **The effort axis was not independently varied.** The Agent tool exposes
  a per-worker `model` but **no effort parameter**, so effort could not be
  set per arm; both inherited the session. The arms' self-reported efforts
  differ (`xhigh` vs `standard`) but that report is exactly the thing
  finding 2 shows is untrustworthy. **This is a model A/B, not a model ×
  effort A/B.** Read the title accordingly.
- **This answers the spec's open question about the floor's mechanism.**
  The harness offers no per-worker effort lever, so the authoring floor
  cannot be enforced by dispatching workers at a chosen effort. Preflight
  warning plus provenance — what `orgsmith/effort.py` and `/forge` Step 0
  actually do — is the only mechanism available, and that is now verified
  against the harness rather than assumed.
- **A stronger board reviewer judged both arms.** Using the weak model as
  its own critic was not tested, and per the "critics share the
  generator's blind spots" argument, it would likely be worse.

## Conclusion

Use the strongest model available for authoring passes. That is no longer
folklore; it is a default with a measurement behind it. Where the recipe or
budget forces a weaker model, expect a corpus at roughly 60% of brief that
still passes every deterministic check — and run `report` and the board
before believing it.
