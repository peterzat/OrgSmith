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

Never author into `companies/<slug>`: the committed fleet is frozen.

## Security

API keys live only in `~/.config/orgsmith/providers.env` (outside the repo) or
your shell environment. The driver reads the key at call time and never prints
its value; `--check` reports presence only. In BYO mode the work-order prose is
sent to the third-party provider you selected, exactly as it would be to the
Claude Code harness; work orders carry no ledger fact values by construction
(only `{{fact:...}}` placeholders), so amounts, dates, and client names are
never transmitted.
