# Security

## Security Review — 2026-08-02 (scope: paths)

**Summary:** Reviewed the eight files named for this run at `f0aacdc`, which
is the previous baseline `e35e6eb` plus the two standing-NOTE closures (the
`validate` printer sanitizer and the `count_noun` guard) and the M17b fix
pass. No secret, no injection path into a filesystem or process sink, no PII,
no new dependency. Two NOTEs, both on the same theme and both new: the
sanitizer the last entry closed its carried NOTE with neutralizes control
characters but not the Unicode format characters that reorder a terminal line,
and the persisted integrity dashboard escapes a finding's message but not its
target.

Neither is a regression. The printer fix does what it claimed against the
attack it was written for (ANSI escapes, smuggled newlines), and it now also
covers the raw third-party parser text that `fin_02` and `file_01` quote,
which no per-rule `!r` would have caught. These are the next layer down.

**Both were FIXED before this entry was committed** (user instruction: clear
the notes before pushing), so this file records zero open findings.
`strip_control` now neutralizes Unicode category Cf as well as Cc, which
covers the validate printer, `review.report._cell` and every later caller at
once; `_integrity_lines` now routes a finding's target through `_cell` beside
its message. Measured first: no Cf character appears anywhere in the repo, so
the widening moved no committed byte, and the org and flagship tiers are
unchanged. Three tests added (bidi override neutralized, `keep` still
honored, non-`str` target survives).

Reviewed at `f0aacdc` plus the uncommitted `str()` coercion the concurrent
code-review pass added to the same printer. Line numbers are cited against the
working tree. The coercion changes neither finding: `str()` is the identity on
the `str` values both concern, and `strip_control` still handles category Cc
only.

### Findings

```
[NOTE, FIXED] orgsmith/naming.py:91-94, reached via orgsmith/validate/__init__.py:87-98
— the finding printer neutralizes control characters but not the bidi format
characters that visually reorder the line it prints.
  Attack vector: the same operation the printer fix was written for. An
    operator validates an org tree obtained from someone else (`validate`
    takes "slug or companies/<slug> path", cli.py:62). A hostile
    `ledger/finance.json` (`LedgerCheck.name` / `.detail`), `ledger/graph.json`
    (`GraphEdge.src` / `.dst`), `ledger/acl.json` (`AclGrant.person`),
    `foundation.json` (`Person.reports_to`), or a manifest `path` embeds
    U+202E RIGHT-TO-LEFT OVERRIDE or a bidi isolate. It survives pydantic,
    survives the printer, and reaches the terminal, where it reverses the
    remainder of the finding line. That is the same read-the-wrong-thing
    outcome as an ANSI escape by a different mechanism (Trojan Source,
    CVE-2021-42574): a tampered path or principal can be made to display as
    an untampered one.
  Evidence: `strip_control` neutralizes a character only when
    `unicodedata.category(ch) == "Cc"` (naming.py:92). U+202E, U+2066-U+2069
    and U+200B are category Cf and pass through unchanged; measured directly,
    and measured again through the printer's own expression on a
    `LedgerCheck` carrying one. The four models above declare bare `str`
    fields (schemas.py:633, 715-718, 786-788, 795), and the messages that
    quote them interpolate raw rather than with `!r` (rules.py:332, 579, 616,
    623, 626, 707, 812-813, 956). `repr()` does escape Cf, which is exactly
    why the `!r` sites (rules.py:973, 1140-1146, 1158, 1047-1064) are already
    clean. `check_relpath` admits the character in a manifest path as well
    (naming.py:23-50: NFC-stable, not in FORBIDDEN_CHARS, ord >= 32), so
    `entry.path`, the most common finding target, can carry one; verified.
    `review/report.py:48` (`_cell`) calls the same sanitizer and inherits the
    same gap on the artifact that persists.
  Remediation: widen the neutralization in `strip_control` to the bidi
    controls, either by treating category Cf as control or by naming
    U+202A-U+202E, U+2066-U+2069 and U+200E/U+200F explicitly. One change
    covers the validate printer, `_cell`, and every other caller, which is
    the same argument that put the last fix at the printer rather than at
    each interpolation site.
```

```
[NOTE, FIXED] orgsmith/review/report.py:310 — the integrity dashboard escapes a
finding's message but not its target, and a MAN-01 target is a raw filesystem
name.
  Attack vector: the same hostile org tree, one verb further on (`report
    <slug>`, cli.py:107; CLAUDE.md lists GENERATION-REPORT.md among the
    derived artifacts that "may always be re-emitted"). The tree
    carries a file in the share that the manifest does not list, named with an
    embedded newline. `man_01` yields that name verbatim as the finding target
    (rules.py:739-740, from `share_dir.rglob("*")` with no name validation:
    `check_relpath` guards manifest entries, not strays). `_integrity_lines`
    then writes `f"- {f['rule']} [{f['target']}] {_cell(f['message'])}"` into
    GENERATION-REPORT.md, so the newline forges a second list item whose text
    the attacker chose. A `|` in the same position breaks a row wherever this
    pattern is reused in a table.
  Evidence: report.py:310 is the one place a finding field reaches the
    persisted report unescaped; the message beside it goes through `_cell`,
    whose own docstring gives the reason ("this artifact PERSISTS: unlike a
    rejection printer that scrolls past, a forged row here is what a human
    reads later", report.py:39-48). Confirmed that a share file can carry a
    newline in its name and that `rglob` + `relative_to` hand it through
    intact. The producer, `collect` (validate/__init__.py:17-33), returns
    findings unsanitized by design: the consumer sanitizes, and this consumer
    half does.
  Remediation: `_cell(f['target'])`. Note the sink is outside this run's file
    list; the producer is inside it, which is how it surfaced.
```

### Verified this turn

- **The printer fix holds against what it was written for.** All four finding
  fields and both skip fields route through `strip_control(..., keep="")`
  (`orgsmith/validate/__init__.py`:87-98), so ESC (U+001B), the C1 CSI
  (U+009B) and a
  smuggled newline are all neutralized; measured. It also covers the two
  raw-text classes no per-rule `!r` would have reached: third-party parser
  exception text (`xlrd` at rules.py:616, every native reader at 707) and
  workbook cell values read back off an attacker-supplied `.xlsx`
  (rules.py:623, 626). The `--json` branch is safe for a different reason than
  the file records: `json.dumps` there runs with the default
  `ensure_ascii=True`, so control characters and bidi controls alike are
  emitted as `\uXXXX` literals.
- **The two new rules do not widen the raw-string surface.** SCOPE-01's new
  branches quote through `!r` (rules.py:1158) or interpolate `Fact.id` values
  that satisfy `^f:[A-Za-z0-9.\-]+$` (rules.py:1121; schemas.py:741).
  Confirmed that pydantic v2's `pattern` anchors fully here: a trailing
  newline is rejected, so the `$`-before-final-newline bypass does not apply.
- **No path traversal anywhere in scope.** `entry.path` and
  `render_params["attach_path"]` are re-checked by `check_relpath` at every
  manifest load (artifacts.py:99-109), the planner re-checks before planning
  one (planner.py:205-207), and `DocIR.doc_id` carries `^d:\d{4}$` at parse
  (schemas.py:1055). The eval writer's filenames are eight hardcoded literals
  (emit.py:1010-1058), never derived from ledger content.
- **No new sink of any kind.** None of the eight files imports `subprocess`,
  `os.system`, `eval`, `pickle`, a network library, or reads an environment
  variable. `requirements.txt`, `requirements.lock`, the Dockerfile and CI are
  untouched in `e35e6eb..HEAD`, which changed only these files, two other test
  files, and docs.
- **The outline work removes a trust step rather than adding one.**
  `outline_for` resolves the skeleton from the hardcoded registry pool by id
  (contexts.py:182-196; registry.py:592-596), so a tampered
  `render_params["outline"]` selects nothing rather than injecting brief text,
  and the brief cannot drift from what OUT-01 recomputes against. Every string
  the new guidance emits comes from `OUTLINES`, not from the manifest.
- **No new model-output-into-prompt path.** `persona` remains the only
  model-authored field carried into a later brief (contexts.py:467), which
  prior reviews considered and did not flag; the deliverable it steers is
  still gated by the deterministic ingest checks before any write. The new
  `_fact_hint` noun comes from the recipe, not from the ledger or the model
  (contexts.py:166-170).
- **No secret, in tree or history.** Pattern scan across all eight files and
  across the last three commits touching each is clean; the only hits are the
  word "token" in prose. No email address, phone number, or real-person name
  appears in any of them.

### Considered and not filed

- **Symlinked write targets under an untrusted org root.**
  `run_emit_evals` writes with `Path.write_text` (emit.py:1075), which follows
  a symlink, so an `evals/README.md` symlinked to a dotfile inside a received
  org tree would be overwritten with partly attacker-influenced text. Not
  filed for two reasons: the premise is running a generation-side verb on
  someone else's tree, which is a long step past the `validate` premise the
  threat model actually supports, and the property is repo-wide rather than
  specific to anything in scope (every `write_model`, `save_manifest` and
  render sink behaves the same). Recorded so a future decision to support
  third-party trees more broadly starts from it rather than rediscovering it.
- **Symlinks on the read side.** `man_01`'s `rglob`/`is_file` and every
  `share_dir / entry.path` join follow symlinks, so a hostile tree can point
  the validator at files outside it. No finding echoes document text, the one
  rule that echoes parsed content is `fin_02` (five cells of a "Summary"
  sheet, rules.py:618-626), and the output goes to the operator's own terminal
  with no channel back. Below the reporting bar.
- **Validator crashes on tampered non-string types.** `fin_02` does
  `int(e.render_params["year"])` (rules.py:597) with no guard, so a manifest
  tampered to `"year": "x"` raises instead of yielding a finding, the same
  shape as the SCOPE-01 `TypeError` the code review fixed. Robustness in a
  local offline CLI with no disclosure or privilege consequence, and the
  project has already classified this class that way.
- **Third-party parsers on hostile files.** Unchanged from the prior
  assessment except that the threat model has widened: with a received org
  tree in scope, an XXE or decompression-bomb payload no longer needs
  committed-fixture write access. Still not filed, because parser-config
  certainty across python-docx, openpyxl, python-pptx, pypdf, pikepdf, xlrd
  and olefile is under the 80% bar without reading each one's parser setup,
  which is outside this run's file list, and the airlock blocks any
  external-DTD network fetch. Worth its own scoped pass if validating
  third-party trees becomes a documented feature rather than a supported
  accident.
- **Dependency, supply-chain and infrastructure dimensions** were out of scope
  for this path-scoped run: no dependency manifest, CI config or Dockerfile is
  in the file list, and none changed in this range.

### Accepted Risks

None.

---
*Prior review (2026-08-02, scope paths, commit e35e6eb): the fourteen
in-airlock files of the M17b batch-boundary turn (scope facts, per-document
skeletons, the client-facing-report override, the structural axis, SCOPE-01
and OUT-01, the ingest outline gate). No secret, no injection path, no PII;
0 BLOCK / 0 WARN / 0 NOTE, the entry having closed the carried `validate`
plain-text printer NOTE at the printer and the `count_noun` IndexError as
robustness.*

<!-- SECURITY_META: {"date":"2026-08-02","commit":"f0aacdca02396f413ba07f9d164583bf5576c18b","scope":"paths","scanned_files":["orgsmith/authoring/contexts.py","orgsmith/docplan/planner.py","orgsmith/docplan/registry.py","orgsmith/evals/emit.py","orgsmith/schemas.py","orgsmith/validate/__init__.py","orgsmith/validate/rules.py","tests/test_unit_validate.py"],"block":0,"warn":0,"note":0} -->
