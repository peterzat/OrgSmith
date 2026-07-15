# CODEREVIEW

## Review — 2026-07-15 (commit: 5a59288)

**Summary:** Refresh review of the complete M6 turn, scope origin/main..HEAD
(11 commits since the prior review at 449dcdf). Focus set: 27 code/test/doc
files plus two recipes; 105 generated fixture files (dev-mini regenerated,
fernhollow-partners new) reviewed via their recipes and the org tier rather
than byte-by-byte. Code surface: the `affiliations_in_docs` knob and the
RNG-free fabric planting pass with its shared pure helpers, era-resolved
employer surfaces in render and authoring briefs, three new validator rules
(NAME-01, AFF-01/02), the name-screen module and its two generation gates,
validator read hardening, printer sanitization, the dev-mini regeneration and
its test migrations, and the fernhollow fixture. Tests green at HEAD and after
fixes (short 6 / unit 222 / org 22, unchanged), and in a fresh clone with a
fresh venv and soffice masked from PATH. Two WARNs found and fixed; both
independently re-verified by probe after the fix rather than on the fixer's
report.

**External reviewers:** None configured.

### Findings

[WARN — FIXED] orgsmith/evals/score.py:341 (and naming.py call sites) — the
printer sanitization this turn delivered was incomplete in two ways;
untrusted strings could still forge terminal output.
  Evidence: (a) the graph branch's class printer was not wrapped at all —
  `print(f"  class {name}: ...")` where `name` derives from `entity.tags` in
  a third-party `graph_expected.json` (`tag.split(":", 1)[1]`,
  score.py:196-197). `--evals-dir` is an explicitly supported CLI input
  ("score from a bare evals directory", cli.py:82-85). Probe at HEAD: a tag
  `ambiguity:<ESC>[2J<ESC>[31mPWNED` printed as
  `'  class \x1b[2J\x1b[31mPWNED: R=0.0% (0/1)'` — raw ESC to stdout, exit 0.
  (b) `strip_control(text, keep="\n\t")` preserves newline, so the same
  deception survived as line injection at the printers that WERE wrapped: an
  answers `docs` entry of `"Real Doc.docx\n\n\n\nretrieval: 17/17 (100.0%)"`
  printed a forged passing score below the real one (found by the security
  pass; score.py:274,317, and the ingest twin at ingest.py:218 via the
  `[^}]*` fact-id charset).
  Severity note: the security review rates this class NOTE (display-only,
  exit codes unchanged, skills key off exit codes) and that assessment is
  sound. It was carried as WARN on code-review grounds: the turn's stated
  deliverable was "the ingest and score failure printers strip control
  characters from untrusted strings," the gaps were oversights rather than
  judgment calls, and the remediation was mechanical. Fixing (a) without (b)
  would have landed a knowingly half-done sanitizer.
  Fix applied: the graph class printer is wrapped, and `keep=""` is passed at
  the per-problem (ingest.py:218) and per-failure (score.py:274,317,341-353)
  printers, whose lines are single-line by construction. The two schema-error
  paths (ingest.py:147, score.py:237) legitimately need newlines and stay on
  the default. Re-verified: ESC now renders U+FFFD, and the retrieval probe
  scores the injected answer wrong (16/17) instead of forging 17/17.

[WARN — FIXED] tests/conftest.py:38-43 — `build_knobbed_stages` emitted a
recipe with a duplicate YAML key, silently resolved by PyYAML. The knobbed
org is the zero-skip validator oracle, so a silent resolution there is
load-bearing.
  Evidence: dev-mini's recipe gained `min_mentions_per_person: 1` this turn
  (recipes/dev-mini/ORG-CHARTER.md:34) while KNOB_LINES still appended
  `min_mentions_per_person: 2` after the `external_people: 3` anchor. The
  generated `graph_targets` block contained the key twice and `yaml.safe_load`
  resolved it to 2 (last wins, no warning). Tests passed only because
  last-wins happened to match intent; a reordering would have silently
  weakened GRAPH-01 coverage from two mentions to one.
  Fix applied: KNOB_LINES no longer carries the key; the helper raises the
  recipe's existing line in place (`MENTIONS_FROM` -> `MENTIONS_TO`) behind an
  assert, matching the other anchors. Re-verified: the key appears exactly
  once and resolves to 2, preserving prior intent.

[NOTE] orgsmith/render/__init__.py:28-48 — `people_index`'s docstring claims
it is "shared with the EML-01 validator so header recomputation reads the
ledger exactly the way render did," but the two sides now diverge:
`run_render` passes `at=entry.date` when `affiliations_in_docs` is on
(render/__init__.py:83-88) while EML-01 calls `people_index(ctx.foundation)`
with no date (rules.py:760,770).
  Evidence: no drift today, verified — the divergence is confined to the
  `title` field, and every consumer of the shared index uses only `name` and
  `email` (eml.py:35-37; the sigblock text builder at rules.py:159).
  fernhollow-partners carries `eml: 2` with the knob on and EML-01 validates
  clean, confirming it empirically. The invariant is now narrower than the
  docstring asserts: adding any title- or org-derived eml header would make
  renderer and checker drift silently.
  Suggested fix: none required. Either narrow the docstring to the fields the
  contract actually covers, or have EML-01 pass the entry date too.

[NOTE] orgsmith/render/pdf.py:37,64 — letterhead lines rendered unescaped
(carried from prior reviews via the security scan; file unchanged in this
range, no concrete attack vector, recipe-author controlled).

Security (paths scan of the 29 changed code/test/recipe files, recorded in
SECURITY.md at commit 5a59288): 0 BLOCK / 0 WARN / 2 NOTEs. The line-injection
NOTE is folded into the first WARN above and is now remediated; SECURITY.md is
annotated accordingly so it does not record a vector that no longer exists.
The new name screen, real_firms.txt (public brands, no PII), the
era-resolution work, the AFF rules, and the airlock all verified clean; no
network, subprocess, eval/exec/pickle, or `yaml.load` sink in any scoped file;
secrets grep clean; dependencies and CI unchanged.

### Fixes Applied

- [WARN] orgsmith/evals/score.py:274,317,341-353 + orgsmith/authoring/ingest.py:218
  — wrapped the graph class printer in `strip_control` and passed `keep=""` at
  the per-failure and per-problem printers, closing both the raw-ESC and the
  newline line-injection vectors. Schema-error paths left on the default.
- [WARN] tests/conftest.py:38-50,180-184 — removed the duplicate
  `min_mentions_per_person` YAML key from the knobbed test recipe; the helper
  now raises the existing line in place behind an assert.

### Accepted Risks

None.

---
*Prior review (2026-07-15, commit 449dcdf): refresh of the complete M5 turn
(four format capabilities, four charter-gated rules, two fixtures); 0 BLOCK /
0 WARN / 2 NOTEs, both of which this turn set out to close and did, with the
residual found and fixed here.*

<!-- REVIEW_META: {"date":"2026-07-15","commit":"5a59288","reviewed_up_to":"5a59288652af7aa4f6be6c286f63724c9b36361e","base":"origin/main","tier":"refresh","block":0,"warn":2,"note":2} -->
