---
name: forge-review
description: Adversarial review board for a generated org. Usage /forge-review <slug> (e.g. /forge-review fernhollow-partners). Dispatches fresh-context reviewers across six quality dimensions and merges their findings into GENERATION-REPORT.md. Read-only; never edits ledgers, prose, or rendered files.
---

# /forge-review — the board

You are the review board's chair. The 29-rule validator already proves the
documents agree with their ledgers. Your board answers the one question
nothing else in this repo asks: **does this read like a real firm wrote
it?**

`PY` below means the project venv python: `.venv/bin/python`.

## What the board is and is not

- **Read-only. Absolutely.** You and your reviewers never edit a ledger, a
  manifest, a DocIR file, a rendered document, or `state.json`. The only
  write is `review --ingest`, which merges findings after validating them.
  A committed fixture's prose is frozen; findings are how you say
  something is wrong, not a licence to fix it.
- **It gates nothing.** No finding fails a build, blocks a commit, or
  feeds a validator rule. It is a report for a human.
- **It is a critic, and critics are weak.** A critic shares blind spots
  with the generator that produced the text. That is why the deterministic
  metrics in `report` exist alongside you, and why your scope is exactly
  what no proxy reaches. Do not re-derive what the metrics already
  measured.

## Precision over recall

An empty board report is a valid, good outcome. Say nothing rather than
manufacture a finding to fill a template. A reviewer that reports six
findings because six feels like the right number is worse than useless: it
buries the real one and teaches the reader to skim.

Every finding must name evidence a human can check in seconds — a doc id
and a quoted phrase. "The tone feels generic" is not a finding. "d:0001
and d:0008 both open 'We are pleased to confirm'" is.

## Step 0 — the deterministic picture first

Run these and read the output BEFORE dispatching anyone:

```
PY -m orgsmith validate <slug>
PY -m orgsmith report <slug>
PY -m orgsmith review <slug> --sample
```

- `validate` output is what reviewers must NOT re-litigate. If it is
  green, every planted fact, mention, header, formula and ACL grant is
  already proven correct. A reviewer claiming "the fee is missing from the
  letter" is contradicting an oracle and is wrong.
- `report` prints GENERATION-REPORT.md: lengths against brief, same-genre
  similarity, and the per-batch generator record.
- `review --sample` writes the reading list to
  `companies/<slug>-metadata/review/sample.json`.

If validate FAILS, stop. Fix the org first; a board reading a broken org
wastes its findings on symptoms of the break.

## Step 1 — dispatch the six dimensions

Spawn one fresh-context worker per dimension (Agent tool, in parallel).
Fresh context per reviewer is the point: a reviewer that has watched you
reason about the org inherits your blind spots.

| dimension | the question |
| --- | --- |
| `org_realism` | Do these people, titles, departments and engagements look like a firm of this size and type? |
| `finance_realism` | Are the revenue, fees and expense shapes plausible for this headcount, sector and era? |
| `narrative_consistency` | Does anything contradict the firm's own history, or postdate the document's date (tools, idioms, events)? |
| `document_plausibility` | Would this genre, in this year, really look like this — structure, length, register, what is left unsaid? |
| `graph_acl_naturalness` | Do the who-knows-whom and who-can-read-what patterns look organic, or assembled? |
| `cross_document_voice` | Did one person write everything? |

`cross_document_voice` is the reason this board exists. Nothing in the
pipeline holds two authored documents at once: every document is written
by a fresh worker that has never seen a sibling. No author can self-check
it, and the n-gram metric only catches literal reuse — two documents can
share zero 4-grams and still be visibly the same writer, with the same
paragraph shapes and the same rhetorical moves. Give that reviewer the
whole sample.

Worker prompt, per dimension:

> Review the org `<slug>` in the repo at `<repo-root>` on the
> `<dimension>` dimension only. Follow
> `.claude/skills/forge-reviewer/SKILL.md` exactly. The validator output
> for this org is:
>
> ```
> <paste the validate summary from Step 0>
> ```

## Step 2 — merge and report

Each worker ingests its own findings. When all six are done:

```
PY -m orgsmith report <slug>
```

This rewrites GENERATION-REPORT.md with the findings table under
**Review board**.

## Step 3 — report to the user

Give the user: the count by severity, the findings you judge worth acting
on, and your own read of whether the board is telling them something the
metrics did not. If the board found nothing, say so plainly — that is a
result, not a failure.

Do not act on the findings. Fixing prose is a separate turn with a
separate spec, and for a committed fixture it is not permitted at all.
