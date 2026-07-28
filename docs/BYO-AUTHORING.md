# Bring-your-own-token authoring

OrgSmith normally authors through the ambient Claude Code session: `/forge`
forks `forge-author` workers and whatever model the session runs is what
writes the prose. Bring-your-own-token (BYO) mode is an optional, off-by-default
alternative that drives the same pipeline through a provider you configure,
OpenAI, Anthropic, Google, OpenRouter, or any OpenAI-compatible endpoint
(including free-tier and local models).

Two reasons to use it:

- **Run the model passes on free or your-own tokens.** A free-tier Gemini or
  OpenRouter key, or a local model through Ollama/LM Studio, authors a corpus
  at little or no cost and without consuming Claude Code usage. Bring a paid
  key when you want a specific frontier model.
- **Reproduce a corpus without the harness.** An outside researcher can
  regenerate an org with a documented, scriptable authoring path, so the model
  identity is a config value rather than a property of one harness. This is the
  first non-skill implementation of OrgSmith's published
  `WorkOrder -> AuthorAdapter -> Deliverable` interface.

The airlock is untouched. `orgsmith/` still never calls a model or the network.
The driver lives in the top-level `drivers/` package, outside the airlock, and
drives the same deterministic CLI verbs (`--emit-context`/`--next-batch`,
`--ingest`) the skills drive. It imports only the pure `orgsmith.schemas`;
nothing in `orgsmith/` imports it.

## Quick start

```bash
# 1. Copy the template outside the repo and fill in one provider.
mkdir -p ~/.config/orgsmith
cp drivers/providers.env.example ~/.config/orgsmith/providers.env
$EDITOR ~/.config/orgsmith/providers.env

# 2. Confirm what is configured (spends no token).
python -m drivers.forge_external --check

# 3. Generate an org end to end via the configured provider.
python -m drivers.forge_external dev-mini
```

`python -m drivers.forge_external` with nothing configured is inert: it prints
a pointer and exits 0. `/forge` behaves exactly as before when no provider is
set.

## Configuration

Configuration is environment variables, optionally seeded from an `.env`-style
file at `~/.config/orgsmith/providers.env` (override the path with
`ORGSMITH_PROVIDERS_ENV`). A value already exported in your shell wins over the
file. The real file lives outside the repository so a key can never be
committed; `providers.env` is also gitignored. The committed template is
`drivers/providers.env.example`, with every line commented so cloning turns
nothing on.

| Variable | Meaning |
| --- | --- |
| `ORGSMITH_AUTHOR_PROVIDER` | Active provider: `openai`, `anthropic`, `google`, `openrouter`, `local`. Unset = BYO mode off. |
| `ORGSMITH_AUTHOR_EFFORT` | Stamped into the `generator` record (default `high`). Advisory for non-Claude providers. |
| `ORGSMITH_AUTHOR_MODEL` | Optional global model override (else the per-provider default). |

## Providers

| name | shape | default base_url | key env | key required |
| --- | --- | --- | --- | --- |
| `openai` | OpenAI Chat Completions | `https://api.openai.com/v1` | `OPENAI_API_KEY` | yes |
| `anthropic` | Anthropic Messages | `https://api.anthropic.com/v1` | `ANTHROPIC_API_KEY` | yes |
| `google` | OpenAI Chat Completions | `.../v1beta/openai` | `GOOGLE_API_KEY` | yes |
| `openrouter` | OpenAI Chat Completions | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | yes |
| `local` | OpenAI Chat Completions | (set `ORGSMITH_LOCAL_BASE_URL`) | `ORGSMITH_LOCAL_API_KEY` | no |

Two HTTP shapes cover every provider. Each provider's base_url and model are
overridable (`ORGSMITH_<NAME>_BASE_URL`, `ORGSMITH_<NAME>_MODEL`), so any other
OpenAI-compatible host (xAI, DeepSeek, Mistral, Together, Groq, a local
Ollama/LM Studio/vLLM server) works through the generic `local` entry by config
alone, with no code change. Default model ids are a convenience only; `--check`
prints the effective model, so a stale default is visible before a token is
spent. Reasoning models that reject `max_tokens` (OpenAI o-series) are best
reached through a gateway or the `local` entry.

## Model choice

OrgSmith's authoring is strict. Every fact briefed for a document must appear as
a `{{fact:...}}` placeholder, and every briefed name must appear verbatim, or
`--ingest` rejects the batch. Holding that discipline is harder than writing
plausible prose, so the model you pick matters more here than the provider does.
**Use the strong tier of whichever provider you choose, not the cheap or fast
one.** `--check` prints the effective model before you spend a token.

Measured on a live `dev-mini` run (OpenAI is the only provider tested directly):

| model | result |
| --- | --- |
| OpenAI `gpt-4o` | failed: omitted required placeholders and a mention; the repair loop could not fix it within the default 2 retries, so the run hard-stopped |
| OpenAI `gpt-4.1` | succeeded: every batch ingested after one repair round, and the org validated clean (0 errors) |

So the OpenAI and OpenRouter defaults are `gpt-4.1`, not `gpt-4o`. The
recommendations for the other providers are by analogy (the strong tier of each
family), not separately measured:

- **Anthropic:** `claude-sonnet-5` or Opus. The committed fleet is authored on
  Opus, and MODEL-AB Round 2 showed Sonnet is a capable author.
- **Google:** `gemini-2.5-pro`, not `gemini-2.5-flash`. The cheap tier will miss
  the placeholder discipline the way `gpt-4o` did.
- **OpenRouter:** route to a frontier model (`openai/gpt-4.1`,
  `anthropic/claude-sonnet-5`, `google/gemini-2.5-pro`); a cheap or small routed
  model fails the same way.
- **local:** use the largest, strongest instruction-following model your
  hardware runs. Small local models (7-14B) will not hold the discipline; a
  frontier model behind an OpenAI-compatible gateway is the more reliable path.

Two things help a borderline model: raise `--max-retries` (each retry re-prompts
with the exact validator rejection), and pay for the strongest model before
paying for retries (a model that cannot place placeholders in two or three
rounds usually will not in five). Even a model that validates clean may run
short of its length brief (`gpt-4.1` did on `dev-mini`: every authored doc came
in off brief). That is a realism gap, not an integrity failure, and it is the
same axis the README's model-choice section measures for the Claude family.

## How the driver runs

`python -m drivers.forge_external <slug>` runs the full pipeline with no Claude
Code dependency:

1. The pure, model-free stages: `charter`, `foundation --scaffold`, `fabric`,
   `docplan` (idempotent; a resume re-runs them harmlessly).
2. **Foundation enrichment** (one model pass): emit the context work order,
   author personas, ingest.
3. **Authoring** (serial loop): `author --next-batch` -> author the batch ->
   `author --ingest` -> `render`, repeating until every batchable doc is
   authored.
4. The pure closing stages: `render`, `assemble`, `acl`, `validate`, `report`.

Flags: `--provider NAME` (override the selection for one run), `--root DIR`,
`--only enrich|author` (restrict which model pass runs; the pure stages always
run), `--max-retries N` (default 2), `--timeout SECONDS`, `--dry-run`.

Resume works the same way `/forge` resumes: state is file-derived in
`state.json`, and the serial `--ingest` is a single-writer merge, so a killed
run is safe to re-run.

### Generator provenance

Each deliverable is stamped with a truthful `generator` record,
`{"model": "<provider>:<model>", "effort": "<effort>"}`, which `report`
surfaces in `GENERATION-REPORT.md`. As always, the record is a note for a
human, never a validator oracle.

### Failure semantics

- **Adapters fail open.** A missing key, connection error, non-2xx response, or
  empty/malformed body logs one line to stderr and returns nothing. The adapter
  never raises for an operational failure.
- **The driver loop is fail-loud.** When the adapter returns nothing, or a
  deliverable is still rejected after `--max-retries`, the run stops with a
  clear message and a non-zero exit. A missing document breaks the pipeline,
  unlike a missing review finding, so the driver does not silently skip.

## Verify end to end (manual, needs a real key)

CI stays keyless and offline; the unit tests mock the network. To exercise the
driver against a real provider without touching a frozen fixture, author into a
gitignored scratch root:

```bash
mkdir -p scratch/byo/recipes
cp -r recipes/dev-mini scratch/byo/recipes/dev-mini
ORGSMITH_AUTHOR_PROVIDER=openai OPENAI_API_KEY=sk-... \
  python -m drivers.forge_external dev-mini --root scratch/byo
python -m orgsmith validate dev-mini --root scratch/byo
```

This path has been run: on `gpt-4.1` the scratch `dev-mini` generated end to end
and validated clean (0 errors), resuming correctly even across a mid-run model
switch. See [Model choice](#model-choice) for how different models fared.

Never author into `companies/<slug>`: the committed fleet is frozen.

## Security

API keys live only in `~/.config/orgsmith/providers.env` (outside the repo) or
your shell environment. The driver reads the key at call time and never prints
its value; `--check` reports presence only. In BYO mode the work-order prose is
sent to the third-party provider you selected, exactly as it would be to the
Claude Code harness; work orders carry no ledger fact values by construction
(only `{{fact:...}}` placeholders), so amounts, dates, and client names are
never transmitted.
