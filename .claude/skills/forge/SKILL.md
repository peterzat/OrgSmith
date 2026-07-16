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

## Step 3 — authoring loop (model passes, a parallel window of workers)

Author in a bounded parallel window: up to **K = 4** batches in flight at
once (lower it when the session is tight on budget; K = 1 reproduces the old
serial loop exactly). Several batches are outstanding at the same time; each
covers a disjoint set of documents, so the workers never collide. The
deterministic merge stays serial and is YOURS, not the workers': you run
every `--ingest`, one at a time, so concurrent batches can never race on
`state.json`. The expensive part (the model authoring) is what parallelizes.

**On entry and on resume, drain what is already outstanding first.**
`PY -m orgsmith status <slug> --json` lists `author_batches`: work orders a
prior session dispatched but never ingested. Re-dispatch a worker for each
(Step 3b) before emitting anything new. Re-authoring an outstanding batch is
safe: its deliverable ingests against the same still-outstanding order, so
nothing is lost or duplicated. Resume truth is these files, never memory of
an earlier run.

Repeat until `author: done`:

1. **Fill the window (a).** While fewer than K batches are outstanding and
   work remains, run `PY -m orgsmith author <slug> --next-batch`. Each call
   writes a fresh work order disjoint from every outstanding one and prints
   its path. Instead of a path it prints `all batchable docs authored`
   (the stage is done) or `N batch(es) outstanding, awaiting ingest` (the
   window is full or nothing fresh remains) — either way, stop filling.
2. **Dispatch the window concurrently (b).** Spawn one forge-author worker
   per fresh work-order path, all in a SINGLE message (multiple Agent calls
   in one turn) so they author in parallel, each in a fresh context. Tell
   each worker to AUTHOR ONLY: write its reply file, stamp the generator,
   and report the reply path; it must NOT ingest.
3. **Ingest serially (c).** For each reply path a worker reports, run
   `PY -m orgsmith author <slug> --ingest <reply>` yourself, one at a time.
   If an ingest is rejected, hand the rejection output to a fresh worker to
   fix that one batch (at most twice); if still rejected, stop and show it.
4. **Render.** After a round of ingests, run `PY -m orgsmith render <slug>`
   (idempotent; it skips docs whose content basis is unchanged) so the org
   stays browsable early and errors surface near their cause.
5. Refill the window and continue until `--next-batch` reports done.

Why you ingest and the workers do not: `--ingest` is a read-modify-write of
`state.json`. Run serially by one process (you) it is deterministic and
race-free; run by concurrent workers it would clobber sibling updates. This
is the airlock holding under parallelism — the CLI stays a lock-free
single-writer state machine and all the concurrency lives here in the skill.

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

Before opening a new authoring window, if the session feels close to its
context or usage limits, let the outstanding batches ingest, run render, and
tell the user to re-run `/forge <slug>` in a fresh session; Step 3's resume
drain picks up exactly where this session stopped (`status --json` still
lists any batch that was dispatched but not yet ingested). Shrinking K also
lowers the per-window cost without losing resumability.
