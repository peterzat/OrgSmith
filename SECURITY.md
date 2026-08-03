# Security

## Security Review — 2026-08-03 (scope: paths)

**Summary:** Reviewed the four M17c A/B files at `9dcc15c`: the control-arm
derivation tool, the arm-comparison tool, and their two unit modules. No
secret, no PII, no new dependency, and no process, network, or environment
sink of any kind. Every string these tools print reaches the terminal from a
hardcoded literal or a schema-constrained field in their documented operating
mode, and no model-authored text reaches an output or a decision. Zero
findings.

The one thing worth writing down is a divergence rather than a defect. These
are the first printers added since `strip_control` became the house sanitizer
for terminal-bound strings, and neither uses it. That costs nothing today
because nothing attacker-influenceable reaches their `print` calls; it is
recorded below so a future decision to point `ab_compare.py` at a tree the
operator did not generate starts from it rather than rediscovering it.

### Findings

No security issues identified.

### Verified this turn

- **No sink of any kind.** Neither tool imports `subprocess`, `os.system`,
  `eval`, `exec`, `pickle`, `shutil`, or a network library, and neither reads
  an environment variable; grepped across all four files. YAML handling is
  `yaml.safe_load` / `yaml.safe_dump` only (`tools/ab_control.py`:56, 67);
  `yaml.load` appears nowhere in scope. The only writes are one `mkdir` and one
  `write_text` (`tools/ab_control.py`:102-103).

- **Nothing attacker-influenceable reaches a printer.** Traced each
  interpolated value in `compare()`. `name` (`tools/ab_compare.py`:108-110)
  comes from `ledger_dir.glob("*.json")`, and every ledger filename the
  pipeline writes is a hardcoded literal in `orgsmith/paths.py`:57-81; nothing
  anywhere derives a ledger filename from content (verified by grepping every
  `ledger_dir` reference in `orgsmith/`). `doc_id`
  (`tools/ab_compare.py`:125) and the manifest field names (lines 128-140) come
  from `json.loads` over `manifest.jsonl`, which the planner writes from
  `ManifestEntry`, whose `doc_id` carries `^d:\d{4}$`
  (`orgsmith/schemas.py`:912). In `report_structure` the only non-numeric value
  printed is `genre` (`tools/ab_compare.py`:223), which is the `Genre` literal
  (`orgsmith/schemas.py`:869) on `StructurePair`
  (`orgsmith/schemas.py`:1531), reached through a pydantic-validated
  `load_manifest`. Getting a chosen string into any of these requires a
  hand-tampered tree; see below.

- **No model output reaches an output or a decision.** The dimension worth
  checking hardest, given the airlock. `arm_pairs`
  (`tools/ab_compare.py`:145-162) is the only path touching authored prose:
  `load_authored` parses each DocIR through `model_validate_json`
  (`orgsmith/review/corpus.py`:95), and `compute_pairs` reduces a pair to
  `StructurePair(doc_a, doc_b, genre, shape, openers)`
  (`orgsmith/review/structure.py`:156-186), which is two ids, a literal, and
  two floats. No authored sentence survives into `_dist`, `_row`, or any
  print. Symmetrically, nothing untrusted enters a prompt: the control recipe
  `ab_control.py` writes is derived from the committed, operator-authored
  `recipes/quillon-harbor/ORG-CHARTER.md`, and the narrative brief that every
  authoring batch carries is copied byte-for-byte rather than re-emitted
  (`tools/ab_control.py`:68).

- **No threshold, so no security-relevant decision to subvert.** `ALL_PAIRS`
  and `_dist` feed `print` only; `report_structure` returns nonzero solely for
  the empty-corpus case. Consistent with `structure.py`'s "MEASURE, NEVER
  GATE", which this run confirms the tools honor.

- **No secret, in tree or in history.** Pattern scan across all four files and
  across `git log -p` for each is clean. No email address, phone number, or
  real-person name appears in any of them, nor in the new
  `recipes/quillon-harbor/ORG-CHARTER.md` that `ab_control.py` reads into every
  authoring brief.

- **No dependency movement.** `71ce014..HEAD` touches only these four files,
  `BACKLOG.md`, `SPEC.md`, `docs/M17C-EVIDENCE-STANDARD.md`, and the new
  recipe. `requirements.txt`, `requirements.lock`, `pyproject.toml`, the
  Dockerfile, and CI are untouched, and `pyyaml` was already a runtime
  dependency. `tools/` is not packaged (`pyproject.toml` includes `orgsmith*`
  and `drivers*` only), so the generically named `tools` namespace package the
  tests import exists at test time only and cannot collide on an install. The
  repo root has no top-level `.py`, so the `sys.path.insert(0, ...)` both tools
  perform shadows no stdlib module.

### Considered and not filed

- **The two new printers bypass `strip_control`.** `orgsmith/naming.py`:87-105
  is the house sanitizer for "untrusted strings bound for a terminal", widened
  to Unicode category Cf in the last entry precisely so one change would cover
  every later caller. `ab_compare.py` is a later caller and does not use it.
  Not filed because there is no reachable path: as traced above, every string
  it prints is a hardcoded ledger filename, a `^d:\d{4}$` doc id, a schema key,
  or a `Genre` literal, and the tool takes two arm roots the operator generated
  rather than a received tree the way `validate` does ("slug or
  companies/<slug> path", `orgsmith/cli.py`:62). Recorded rather than dropped
  because the gap is one usage change away from mattering: pointing this tool
  at a third-party tree would make ledger filenames, manifest keys, and doc ids
  attacker-chosen at once, and `print(f"  {line}")`
  (`tools/ab_compare.py`:257, 262) would emit them raw.

- **Path composition from the `slug` argument.** Both tools build
  `<root>/recipes/<slug>/...` and `<root>/companies/<slug>...` with no
  validation of `slug` (`tools/ab_control.py`:89, 101; `OrgPaths`,
  `orgsmith/paths.py`:18-28), so a `../` traverses. Not filed: `slug` is a
  positional CLI argument supplied by the operator running the command, so the
  only party it lets out of the tree is the party who already chose the path,
  and the shipped CLI composes identically at `org_paths(args.slug, args.root)`
  (`orgsmith/cli.py`:159, 206). A repo-wide property, not something these files
  introduce.

- **`ab_control.py --root .` overwrites its own source.** `dest`
  (`tools/ab_control.py`:101) resolves to the same path as `src` (line 89) when
  `--root` and `--source-root` coincide, so that invocation replaces the
  committed treatment recipe with the control version; the "already a control
  arm" guard (lines 94-99) only fires on a second run. Recorded as a footgun
  rather than filed: it crosses no privilege boundary, needs the operator's own
  command, and is recoverable from git. Same class as the symlinked-write
  property the prior entry recorded repo-wide, which this `write_text` shares.

- **Dimensions this run does not attest.** Authentication and authorization:
  no auth code exists in scope, and the `acl.json` these tools compare is
  synthetic ground truth about a fictional org rather than an access control
  that guards anything. Dependency, supply chain, and infrastructure: no
  dependency manifest, CI config, or Dockerfile is in the file list, and none
  changed in this range.

### Accepted Risks

None.

---
*Prior review (2026-08-02, scope paths, commit f0aacdc): the eight in-airlock
files of the M17b turn plus the two standing-NOTE closures. No secret, no
injection path, no PII, no new dependency. Two NOTEs on one theme, both fixed
before that entry was committed: `strip_control` widened from Unicode category
Cc to Cc plus Cf, so the validate printer and `review.report._cell` neutralize
bidi overrides as well as escapes, and `_integrity_lines` routed a finding's
target through `_cell` beside its message. 0 open findings.*

<!-- SECURITY_META: {"date":"2026-08-03","commit":"9dcc15c9ce962814391d90e5b6c5e0199512724b","scope":"paths","scanned_files":["tests/test_unit_ab_control.py","tests/test_unit_ab_structure.py","tools/ab_compare.py","tools/ab_control.py"],"block":0,"warn":0,"note":0} -->
