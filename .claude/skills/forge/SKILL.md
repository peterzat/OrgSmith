---
name: forge
description: Generate a synthetic org from a recipe. Usage /forge <slug> (e.g. /forge dev-mini). Runs the OrgSmith pipeline end to end, dispatching authoring batches to forked forge-author workers. Resumable; safe to re-run after an interrupted or killed session.
---

# /forge — orchestrate one org generation

You are the generation orchestrator. You run deterministic stages as shell
commands and hand model work to forked workers. Keep only status summaries
in your context; never read rendered documents or full ledgers into this
conversation (that is what workers and validators are for).

`PY` below means the project venv python: `.venv/bin/python`.

## Step 0 — orient (always, including on resume)

1. `PY -m orgsmith doctor <slug>` — capability probe. Stop and report if
   required capabilities are missing.
2. `PY -m orgsmith status <slug> --json` — this tells you exactly where a
   previous session stopped. Resume state is file-derived; never rely on
   conversation memory of earlier runs.

## Step 1 — pure stages (Bash, in order, each idempotent)

```
PY -m orgsmith charter <slug>
PY -m orgsmith foundation <slug> --scaffold
PY -m orgsmith fabric <slug>
PY -m orgsmith docplan <slug>
```

## Step 2 — foundation enrichment (model pass)

Skip if status shows `foundation_enrich: done`.

1. `PY -m orgsmith foundation <slug> --emit-context` — prints the work
   order path.
2. Spawn a forked worker (Agent tool, fresh context) with this prompt:
   "Read <work-order-path> and follow the instructions in
   .claude/skills/forge-author/SKILL.md for an enrichment work order in
   the repo at <repo-root>. Org slug: <slug>."
3. The worker ingests its own deliverable. Confirm with
   `PY -m orgsmith status <slug> --json`.

## Step 3 — authoring loop (model passes, one worker per batch)

Repeat until `author: done`:

1. `PY -m orgsmith author <slug> --next-batch` — prints the work order
   path (re-running returns the same order until it is ingested).
2. Spawn a forked forge-author worker as in Step 2 (fresh context per
   batch; that is the token discipline that lets large orgs span
   sessions).
3. After each successful ingest: `PY -m orgsmith render <slug>` so the
   org is browsable early and errors surface near their cause.

If a worker reports a rejected deliverable twice for the same batch, stop
and show the rejection output; do not loop further.

## Step 4 — finish

```
PY -m orgsmith render <slug>
PY -m orgsmith assemble <slug>
PY -m orgsmith acl <slug>
PY -m orgsmith validate <slug>
```

Report the validate summary. If validate fails, show the failing rules and
stop; never edit ledgers or rendered files by hand.

## Budget awareness

Before each authoring batch, if the session feels close to its context or
usage limits, finish the current batch, run render, and tell the user to
re-run `/forge <slug>` in a fresh session; Step 0 picks up exactly where
this session stopped.
