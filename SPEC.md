# SPEC

## Spec — 2026-07-28 — Bring-your-own-token authoring mode (provider-neutral driver)

**Goal:** Ship an optional, off-by-default authoring mode that drives OrgSmith's
two model passes (foundation persona enrichment and document authoring) through a
user-supplied provider token (OpenAI, Anthropic, Google, OpenRouter, or any
OpenAI-compatible endpoint including free-tier and local models) instead of the
ambient Claude Code harness. This is the deferred `provider-neutral-authoring-driver`
backlog item: the first non-skill implementation of the
`WorkOrder -> AuthorAdapter -> Deliverable` interface the README already blesses,
and it lets the model passes run on free-subscription or bring-your-own tokens
rather than consuming Claude Code usage.

### Acceptance Criteria

- [x] **Off by default, opt-in, airlock preserved.** With no provider configured
  (`ORGSMITH_AUTHOR_PROVIDER` unset and no `~/.config/orgsmith/providers.env`),
  BYO mode is inert: `python -m drivers.forge_external --check` prints the
  off-by-default explanation and exits 0, and `/forge` runs today's forked-worker
  path unchanged. No file under `orgsmith/` gains provider, key, or network code;
  all of it lives in the new top-level `drivers/` package. `bin/test short` stays
  green, including `test_no_tier_reads_a_model_api_key`, the schema pin, and the
  product-name check. A shipped `drivers/providers.env.example` has every provider
  line commented; `providers.env` is gitignored.

- [x] **Provider registry and selection.** `drivers/config.py` registers `openai`,
  `anthropic`, `google`, and `openrouter` as named providers plus a generic
  OpenAI-compatible `local` entry whose base_url is user-set. Every provider's
  base_url and model id are overridable by env, so any other OpenAI-compatible
  endpoint (xAI, DeepSeek, Mistral, Together, Groq, Ollama, LM Studio) works by
  config alone with no code change. The active provider is chosen by
  `ORGSMITH_AUTHOR_PROVIDER` or `--provider`; unset resolves to none (the off
  gate). `--check` lists the selected provider, base_url, model, effort, config
  path, and whether the key is present (presence only, never the value), and exits
  non-zero when a provider is selected but its key or base_url is missing.

- [x] **Adapters fail open.** `call_provider` reaches the OpenAI Chat Completions
  and Anthropic Messages shapes over stdlib HTTP (no new runtime dependency) and
  fails open: any missing key, connection error, non-2xx response, or
  empty/malformed body logs one line to stderr and returns `None` without raising.
  Verified offline with mocked HTTP for both shapes.

- [x] **The driver produces valid deliverables for both passes, with a bounded
  repair loop.** `drive_work_order` feeds the self-contained WorkOrder JSON
  verbatim (no ledger fact value ever appears in the prompt), extracts the
  deliverable JSON from the model reply tolerating code fences and surrounding
  prose, validates it against the matching pydantic schema (`EnrichmentDeliverable`
  for foundation, `AuthoringDeliverable` for author) via `orgsmith.schemas`, and
  stamps a truthful `generator={model,effort}`. A `None` adapter result is a hard
  stop with a clear message, never a silent skip. On an `orgsmith ... --ingest`
  rejection the driver re-prompts the model with the rejection text and retries up
  to `--max-retries` (default 2), then fails loudly; a failed ingest leaves the
  batch outstanding for a clean resume.

- [ ] **Standalone end-to-end loop.** `python -m drivers.forge_external <slug>`
  generates an org with zero Claude Code dependency: foundation enrichment, then
  the serial authoring loop (`--next-batch` -> drive -> `--ingest` -> render until
  `all batchable docs authored`), then assemble/acl/validate/report. It resumes
  through the same `state.json` + serial-`--ingest` discipline `/forge` uses, and
  when no provider is configured it prints the pointer and exits 0 having mutated
  nothing.

- [x] **`/forge` BYO branch.** `.claude/skills/forge/SKILL.md` gains a BYO branch:
  Step 0 detects a configured provider (via the driver `--check`) and reports the
  provider/model pair in place of the ambient model line; when set, the model
  passes delegate to `python -m drivers.forge_external <slug>`; when unset, the
  forked-worker path is byte-for-byte unchanged. The serial single-writer
  `--ingest` discipline is kept.

- [x] **Offline, keyless tests and fleet safety.** `tests/test_unit_driver.py`
  (marker `unit`) covers config load and selection, prompt assembly with no fact
  leak, deliverable extraction and schema validation, generator stamping, the
  bounded repair loop, per-shape graceful degradation, and `--check` in all three
  states, entirely offline with mocked HTTP and subprocess; the file contains none
  of the literal strings `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `CLAUDE_API_KEY`.
  Full `bin/test` (short + unit + org + flagship) stays green, keyless and offline.
  No new randomness stream and no schema-id bump; the frozen fleet still loads,
  validates, and re-derives byte-identical (`test_org_regen.py` `PINNED = SLUGS`
  and the schema pin unaffected).

- [x] **Docs, README highlight, backlog closure.** `docs/BYO-AUTHORING.md`
  documents the config surface, provider table, selection, `--check`, the
  standalone run, the `/forge` mode, generator/effort semantics, the
  fail-open-vs-hard-stop contract, the manual scratch-root smoke recipe (never
  authoring into a frozen fixture), and the key-storage security note. `README.md`
  highlights the capability, leading with the headline benefit: driving authoring
  on free-tier or free-subscription provider tokens (free Gemini/OpenRouter tiers
  or a local model at zero API cost) or a user's own BYO key, instead of consuming
  Claude Code harness usage. `BACKLOG.md`'s `provider-neutral-authoring-driver`
  entry is closed.

### Context

- **Adopted from plan** `~/.claude/plans/let-s-add-a-bring-your-own-token-snug-mitten.md`.
  Read it for the full file-by-file design, the adapter interface, and the
  MVP/follow-up split. It supersedes the M16-close proposal's headline M17-flagship
  direction; the flagship remains a live future direction (README + git history),
  not lost.

- **Airlock positioning (the load-bearing constraint).** The airlock rule
  (CLAUDE.md:10-14) constrains code inside `orgsmith/`. The driver lives in a new
  top-level `drivers/` package, outside that boundary, so it may import `urllib`,
  read API keys, and call providers. Verified against the enforcement tests:
  `test_no_tier_reads_a_model_api_key` (test_short.py:261-271) scans only
  `orgsmith/` and `tests/` for the three literal key names, so driver code is free
  in `drivers/` but any driver test under `tests/` must avoid those literals
  (reference `PROVIDERS["openai"].key_env` and a synthetic `ORGSMITH_TEST_KEY`
  provider instead). The banned-network-import scan (test_short.py:149-161) covers
  only `orgsmith/review`. The dependency is one-way: the driver imports the pure
  `orgsmith.schemas`; nothing in `orgsmith/` imports `drivers`.

- **No schema change.** `AuthoringDeliverable.generator` /
  `EnrichmentDeliverable.generator` are already optional and recorded by
  `author --ingest` (schemas.py:996-1030). The driver stamps the real
  provider/model truthfully. `--ingest` is side-effect-free on rejection, so it
  doubles as the repair-loop validator: a rejected batch stays outstanding.

- **Self-contained WorkOrders.** The authoring WorkOrder carries the full
  hard-rules `instructions` block, `narrative`, and per-doc `guidance`
  (`orgsmith/authoring/contexts.py`), so the driver's own prompt scaffolding is
  small: a writing-quality system prompt distilled from `forge-author/SKILL.md`
  plus an "emit pure JSON" instruction. Accepted MVP drift risk: the distilled
  prompt is driver-owned; a shared prompt asset both skill and driver read is a
  follow-up.

- **Packaging.** `pyproject.toml` adds `drivers` to
  `[tool.setuptools.packages.find]` (currently `include = ["orgsmith*"]`) so
  `python -m drivers.forge_external` runs and `tests/` can `import drivers.*`; an
  optional `orgsmith-author` console entry point may be added. Stdlib-only, no new
  runtime dependency. `unit` is an existing pytest marker.

- **Exercised proof (manual, non-CI).** To prove the driver end to end needs a
  real key and costs money, so it is a documented manual smoke against a gitignored
  scratch root with the `dev-mini` recipe, never against a frozen fixture. Not a
  gating criterion.

- **House practices (zat.env).** Verification over prompting: the acceptance
  criteria are the contract. Small committable increments with tests in the same
  increment; run the relevant tier after each functional change. If two
  consecutive fix attempts fail, revert and re-evaluate. Never weaken a test to
  accommodate a regression. Precision over recall in any review. Do not remove,
  reword, or reorder acceptance criteria; only check them off when verified.

- **Execution (user directed autonomous implementation + push).** Implement in the
  plan's staged increments, committing each with its tests; update the README
  highlight last; then push. The final push triggers the pre-push `/codereview`
  gate; run it when it blocks.

- **Turn closed 2026-07-28 (7/8), user decision.** Criterion 5's live
  end-to-end run against a real provider key was consciously skipped, not
  attempted: it needs a paid credential and cannot run in CI. Everything up to
  the live provider call is unit-tested; the documented manual scratch-root
  smoke (`docs/BYO-AUTHORING.md`) remains the way to close it. Shipped and
  pushed (`4fdce04`, `cf9ee69`, `856489a`); codereview + security clean
  (0 BLOCK, 0 WARN, 1 defense-in-depth NOTE).

---
*Prior spec (2026-07-23): M16 — regenerated the eight-org fleet under the realism
wave's knobs, re-froze (`PINNED = SLUGS` fleet-wide), and cut the v2.1.0 release;
12/12 criteria met.*

### Proposal (2026-07-28)

**What happened.** Bring-your-own-token authoring shipped (`4fdce04`, `cf9ee69`,
`856489a`), closing the deferred `provider-neutral-authoring-driver` backlog item. A
new out-of-airlock `drivers/` package drives OrgSmith's two model passes through a
configured provider (OpenAI, Anthropic, Google, OpenRouter, or any
OpenAI-compatible/local endpoint): a config/registry, two stdlib-HTTP adapters
(fail-open), a WorkOrder -> provider -> Deliverable loop with generator stamping and a
bounded repair loop, a standalone generation loop, a `--check` preflight, and a
`/forge` BYO branch. Off by default; the airlock is untouched (`orgsmith/` unchanged,
the one-way dependency enforced by a new short-tier test). Codereview and security
clean (0 BLOCK, 0 WARN, 1 defense-in-depth NOTE). 7/8 criteria: the live end-to-end
run against a real key was consciously skipped (CI stays keyless), so the driver is
proven up to the provider call but never exercised end to end against a real model.

**Questions and directions.**
- **Close the BYO loop for real.** The one open criterion: run the driver end to end
  on a scratch `dev-mini` against a free or local provider (a free Gemini/OpenRouter
  tier, or Ollama), confirm it produces a valid org, and record the result. Small and
  concrete, and it converts "proven up to the call" into "proven." Open question: does
  a non-Claude model actually satisfy ingest's placeholder/mention/hard-case checks,
  and how many repair rounds does it take?
- **M17, the window-defeating flagship.** Still the big roadmap item, deferred again
  this turn. BYO now makes it cheaper: the ~2,000-document org could author on a
  cheaper or free provider. What recipe shape and cost envelope, and does the driver's
  serial loop need a parallel window (K>1) first?
- **BYO hardening follow-ups.** The security NOTE (an `http(s)`-only scheme allowlist
  on `base_url`); a shared authoring-prompt asset both the skill and driver read, with
  a drift test; a MODEL-AB round using the driver to vary the model independent of the
  harness.
- **Carried from M16.** The mail full-name-in-body device (meridian/ashcombe) and
  `board-negative-control` (still no measured board false-positive rate).

<!-- SPEC_META: {"date":"2026-07-28","title":"Bring-your-own-token authoring mode (provider-neutral driver)","criteria_total":8,"criteria_met":7} -->
