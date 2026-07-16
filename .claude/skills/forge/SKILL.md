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
   required capabilities are missing. If the recipe sets a
   `legacy_ratio > 0` and doctor reports `soffice absent`, stop BEFORE
   any generation and tell the user to install LibreOffice (install
   command in CLAUDE.md, Environment section); render would otherwise
   fail mid-pipeline at the first legacy document.
2. **Report the authoring pair before spending a token.** Doctor's
   `effort` line prints the session effort against the documented
   authoring floor and warns when you are below it. State to the user, in
   one line: the exact model id you are running as (you know it from your
   own context; doctor cannot see it) and the effort doctor printed.

   If doctor warned that effort is below the floor, STOP and ask whether
   to continue. Content quality tracks the model and effort, nothing
   downstream can detect a weak authoring pass from the artifacts, and a
   regenerated org is expensive. This is the only moment the choice is
   free.

   Both halves are self-reported and recorded per batch, never verified:
   see `orgsmith/effort.py` for what the harness does and does not expose.
3. `PY -m orgsmith status <slug> --json` — this tells you exactly where a
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
PY -m orgsmith report <slug>
```

Report the validate summary. If validate fails, show the failing rules and
stop; never edit ledgers or rendered files by hand. A NAME-01 finding (a
generated name collides with a real firm) blocks committing the org: fix
the recipe name or bump the seed and regenerate, never the ledger.

`report` writes GENERATION-REPORT.md (derived, under `-metadata/`): the
per-batch generator record, each document's length against the words its
brief asked for, and same-genre similarity. It gates nothing. Read the
summary line; a corpus far off brief or a high same-genre pair is worth a
look before the org is committed.

## Step 5 — the board (optional, model passes)

`validate` proves the documents agree with the ledgers. It says nothing
about whether the prose reads like a real firm wrote it. For that, run
`/forge-review <slug>`, which dispatches fresh-context reviewers and
merges their findings into the same report. It is read-only and never
gates; skip it for a throwaway org.

## Budget awareness

Before each authoring batch, if the session feels close to its context or
usage limits, finish the current batch, run render, and tell the user to
re-run `/forge <slug>` in a fresh session; Step 0 picks up exactly where
this session stopped.
