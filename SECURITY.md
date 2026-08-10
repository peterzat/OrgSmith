# Security

## Security Review — 2026-08-10 (scope: paths)

**Summary:** Reviewed the five M17c A/B files at `c5b9994`: the two tools and
their three unit modules, including the replicate arm, `noise_floor`, the
lexical axis, and the same-skeleton split that landed since the last pass. No
secret, no PII, no new dependency, and still no process, network, or
environment sink of any kind. Every one of the 28 `print` calls in the two
tools was enumerated and traced: each emits a hardcoded literal, an operator's
own argv, a schema-constrained field, or a formatted number. Zero findings.

Two things changed against the prior entry's record. The in-place-overwrite
footgun it filed under "considered and not filed" is now closed by a guard in
`main()` with a test behind it, so it is dropped rather than carried. And the
stale line citations `CODEREVIEW.md` flagged (the referenced code was
unmodified; only the numbers moved) are refreshed below, which is the reason
they were left for this pass rather than hand-edited outside a scan.

### Findings

No security issues identified.

### Verified this turn

- **No sink of any kind, including in the new code.** Grepped all five files
  for `subprocess`, `os.system`, `popen`, `eval`, `exec`, `pickle`, `marshal`,
  `shutil`, `__import__`, `importlib`, `socket`, `requests`, `urllib`,
  `httpx`, `http.client`, `os.environ`, `getenv`, `tempfile`, `chmod`, and
  `symlink`: zero hits. YAML handling is `yaml.safe_load` / `yaml.safe_dump`
  only (`tools/ab_control.py`:56, 67); `yaml.load` appears nowhere in scope.
  The only production write is one `mkdir` plus one `write_text`
  (`tools/ab_control.py`:110-111); every test write is under `tmp_path`. The
  new `--replicate` root (`tools/ab_compare.py`:414-419) is read-only, exactly
  as `--control` and `--treatment` are.

- **No model output reaches an output or a decision.** The dimension worth
  checking hardest, and the one this range genuinely extended.
  `lexical_scores` (`tools/ab_compare.py`:216-240) is a new consumer of
  authored prose: it runs `prose_text` through `shingles`
  (`orgsmith/review/corpus.py`:48-74) and reduces each pair to a `jaccard`
  float. At the printer (`tools/ab_compare.py`:405) the doc ids and genre are
  discarded by the comprehension and only the float reaches `_dist`, so no
  authored token survives. `arm_pairs` is unchanged: `compute_pairs` still
  reduces a pair to two ids, a `Genre` literal, and two floats
  (`orgsmith/review/structure.py`:156-186). `noise_floor`
  (`tools/ab_compare.py`:271-315) is arithmetic over those floats, keyed on
  `(doc_a, doc_b)` tuples from a pydantic-validated `StructurePair`, and emits
  only numbers. The two regexes prose passes through are linear
  (`orgsmith/review/corpus.py`:30-31), so no ReDoS on model-controlled text.

- **`outline_of` reads raw manifest JSON but nothing it reads is printed.**
  `tools/ab_compare.py`:179-190 pulls `render_params.outline` through
  `json.loads` rather than the pydantic path. The value is used only for
  equality in `split_by_outline` (line 206-212) and never interpolated
  anywhere, so bypassing validation costs nothing at a printer.

- **Nothing attacker-influenceable reaches a printer.** Re-traced every
  interpolated value across all 28 `print` calls. `name` is an arm key literal
  (`"control"` / `"treatment"` / `"replicate"`, line 327-329); `genre` (line
  377) is the `Genre` literal on `StructurePair` (`orgsmith/schemas.py`:869,
  1531); the identity headline (line 444) joins `IDENTITY_FIELDS` constants;
  the ledger `name` (lines 115-124) comes from `ledger_dir.glob("*.json")`,
  and every ledger filename the pipeline writes is a hardcoded literal in
  `orgsmith/paths.py`:57-81; `doc_id` (line 139) carries `^d:\d{4}$`
  (`orgsmith/schemas.py`:912). `tools/ab_control.py`:112 echoes `dest`, which
  is the operator's own `--root` and `slug`. Everything else is a literal or a
  `:.4f` / `:4d` format.

- **No threshold, so no security-relevant decision to subvert.** `ALL_PAIRS`,
  `_dist`, and both `noise_floor` figures feed `print` only; `report_structure`
  returns nonzero solely for the empty-corpus case (line 336). Consistent with
  `structure.py`'s "MEASURE, NEVER GATE", which this run reconfirms the tools
  honor across the new replicate and lexical paths.

- **No secret, in tree or in history.** Pattern scan across all five files and
  across `git log -p --follow -5` for each is clean; the only `token` hits are
  the phrase "spends a model token" in a commit message body. No email
  address, phone number, or real-person name in any of them.

- **No dependency movement.** `9dcc15c..HEAD` touches only these five files
  plus `BACKLOG.md`, `CODEREVIEW.md`, `README.md`, `SECURITY.md`,
  `docs/M17C-EVIDENCE-STANDARD.md`, and one skill file. `requirements.txt`,
  `requirements.lock`, `pyproject.toml`, the Dockerfile, and CI are untouched
  (verified by `git diff --name-only` over that set: zero). `tools/` is still
  not packaged (`pyproject.toml`:51-55 includes `orgsmith*` and `drivers*`
  only), so the generically named `tools` namespace package the tests import
  exists at test time only and cannot collide on an install. The repo root
  still has no top-level `.py`, so `sys.path.insert(0, ...)`
  (`tools/ab_compare.py`:35, `tools/ab_control.py`:30, `tests/conftest.py`:24)
  shadows no stdlib module.

- **Suite state.** The three scoped modules run 19 tests green at `c5b9994`,
  confirming the code traced above is the code that runs.

### Closed since the prior entry

- **`ab_control.py --root .` overwriting its own source.** The prior entry
  recorded this as a footgun. It is now guarded: `dest` is computed before the
  strip and `src.resolve() == dest.resolve()` exits non-zero before any write
  (`tools/ab_control.py`:93-100), with `test_deriving_in_place_is_an_error`
  (`tests/test_unit_ab_control.py`:137-158) asserting the treatment recipe
  survives byte-for-byte. `resolve()` normalizes symlinked components on both
  sides, so an aliased destination is caught too. Dropped rather than carried.

### Considered and not filed

- **The two printers bypass `strip_control`.** Carried from the prior entry
  with refreshed citations; the referenced code is unmodified and only the
  line numbers moved. `orgsmith/naming.py`:87-105 is the house sanitizer for
  untrusted strings bound for a terminal. `ab_compare.py` is a later caller
  and does not use it. Not filed because there is no reachable path: as traced
  above, every string it prints is a hardcoded ledger filename, a `^d:\d{4}$`
  doc id, a manifest key, a `Genre` literal, or an arm-name constant, and the
  tool takes arm roots the operator generated rather than a received tree the
  way `validate` does (`orgsmith/cli.py`:62). Recorded rather than dropped
  because the gap is one usage change away from mattering: the manifest field
  names counted at `tools/ab_compare.py`:142-144 are raw `json.loads` keys, so
  pointing this tool at a third-party tree would make ledger filenames,
  manifest keys, and doc ids attacker-chosen at once, and `print(f"  {line}")`
  (now `tools/ab_compare.py`:449, 454) would emit them raw.

- **Path composition from the `slug` argument.** Both tools build
  `<root>/recipes/<slug>/...` and `<root>/companies/<slug>...` with no
  validation of `slug` (`tools/ab_control.py`:89, 93; `OrgPaths`,
  `orgsmith/paths.py`:18-28), so a `../` traverses. Not filed: `slug` is a
  positional CLI argument supplied by the operator running the command, so the
  only party it lets out of the tree is the party who already chose the path,
  and the shipped CLI composes identically at `org_paths(args.slug, args.root)`
  (`orgsmith/cli.py`:159, 206). A repo-wide property, not something these
  files introduce.

- **Dimensions this run does not attest.** Authentication and authorization:
  no auth code exists in scope, and the `acl.json` these tools compare is
  synthetic ground truth about a fictional org rather than an access control
  that guards anything. Dependency, supply chain, and infrastructure: no
  dependency manifest, CI config, or Dockerfile is in the file list, and none
  changed in this range.

### Accepted Risks

None.

---
*Prior review (2026-08-03, scope paths, commit 9dcc15c): the four M17c A/B
files as they stood before the replicate arm. No secret, no PII, no new
dependency, no sink, and no model-authored text reaching an output or a
decision. Zero findings, with three items considered and not filed: the
`strip_control` bypass in the new printers, `slug` path composition as a
repo-wide property, and the in-place-derive footgun that this entry records as
closed.*

<!-- SECURITY_META: {"date":"2026-08-10","commit":"c5b9994bfbff3bbb9aab38154b353bd2d72ed907","scope":"paths","scanned_files":["tests/test_unit_ab_compare.py","tests/test_unit_ab_control.py","tests/test_unit_ab_discriminating.py","tools/ab_compare.py","tools/ab_control.py"],"block":0,"warn":0,"note":0} -->
