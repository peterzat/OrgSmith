# Security

## Security Review — 2026-10-13 (scope: paths)

**Summary:** Reviewed the two paths `/codereview` named at `9045bae`, the one
commit not yet on `origin/main`: `orgsmith/docplan/planner.py` and
`tests/test_unit_mail_broadcast.py`, each read in full. Since the last scan
(`12b1933`) both changed only in docstrings (planner.py:813-818,
test_unit_mail_broadcast.py:69-70). No new finding: the planner reads no
model-authored input, every path it plans is contained, and neither file adds
a process, network, or destructive filesystem sink. The two open NOTEs are in
files outside this scope and are carried without re-checking.

### Findings

**[NOTE] orgsmith/schemas.py:685-696 — the oversight-title check echoes a received tree's strings raw, so a crafted `charter.json` can write escape sequences to the terminal through `validate`'s traceback (carried from the 2026-10-13 scan, not re-checked)**

  Confidence (at that scan): high that the bytes reach the terminal
  (reproduced); low that the check adds exposure, since a crafted tree
  reaches the terminal another way.
  Attack vector: validating an org tree obtained from someone else is a
  supported operation (`orgsmith/validate/__init__.py`:69). `validate` loads
  the tree's `charter.json` in `Context.load` (`orgsmith/validate/rules.py`:47-50)
  with no handler, and `main` (`orgsmith/cli.py`:163) does not catch what it
  raises. An `oversight_titles` entry that matches no `titles` list and no
  generic fallback fails the check, which joins the unknown strings into its
  `ValueError` unescaped (line 695). pydantic copies that message into the
  `ValidationError`, and the traceback writes it to stderr, past the
  `strip_control` printer that sanitizes findings. The run still exits 1, so
  automation sees the failure, but an operator reading the terminal can be
  shown a cleared screen and a forged clean result line.
  Evidence: reproduced at that scan on a scratch copy of committed `dev-mini`:
  one `oversight_titles` entry carrying `ESC[2J`, `ESC[H`, and a forged
  `validate: ... 0 errors, 0 warnings` line put both raw ESC bytes on stderr.
  `_check_scope_services` joins `scope_by_service` keys the same way (lines
  543-548). Line references are as of `0c231b9`; the file is unchanged since.
  Remediation: locally, pass each unknown title through
  `strip_control(t, keep="")` before the join at line 695, and do the same at
  line 548. The class-level fix is to catch `ValidationError` where `validate`
  loads a received tree and print it through `strip_control`, as ingest already
  does (`orgsmith/authoring/ingest.py`:396-399).

**[NOTE] orgsmith/review/numbers.py:44 — a digit run over 4300 characters in authored prose crashes `report` (carried from the 2026-10-13 scan, not re-checked)**

  Confidence (at that scan): high that it crashes; security impact low.
  Attack vector: DocIR prose is model-controlled, the input the airlock treats
  as untrusted, and no schema or ingest check bounds a digit run that no ledger
  owns. `report` reaches `numbers_in`, whose `\d+` matches the whole run, and
  `int()` raises `ValueError` under Python 3.10.12's 4300-digit conversion
  limit. Nothing catches it, so `report`, the BYO driver's closing loop, and
  `/forge-review` Step 0 fail loudly. `validate` never calls the counter.
  Evidence: reproduced at that scan, in memory, against `quillon-harbor`
  `d0003`. `tools/probe_numbers.py`:43 has the identical line. Line references
  are as of `03f6442`; the file is unchanged since.
  Remediation: in `orgsmith/review/numbers.py` only, skip or cap a match longer
  than about 18 digits before `int()`, with a unit test on a 5000-digit run.
  Leave `tools/probe_numbers.py` alone: its sha256 is pinned by the
  pre-registration (`docs/M17D-OPUS55-PROBE.md`).

### Verified this turn

- **No secret and no real PII, at HEAD or in recent history.** A 21-pattern
  scan (16 secret shapes plus email, phone, IPv4, home or `/tmp/claude` path,
  and tailnet name), each first confirmed to fire on a synthetic positive and
  to stay quiet on a benign line, found nothing in the two files at HEAD. The
  same scan over the added and removed lines of `git log -p --follow -3` for
  each file (`9045bae`, `12b1933`, `061da37` for the planner; `9045bae`,
  `12b1933`, `4fd9465` for the test) also found nothing. The mail subjects the
  planner hard-codes are generic (planner.py:703-714).

- **The planner reads no model-authored input.** Its stage requires only
  `charter`, `foundation` and `fabric` (planner.py:1586) and refuses to
  re-plan once a manifest exists (1587-1591), so no authored DocIR reaches it.
  The one model-written field among its inputs is `Person.persona`
  (`orgsmith/schemas.py`:742), the only field foundation ingest merges
  (`orgsmith/foundation/ingest.py`:71-73), and the file never reads it, an
  engagement `summary`, or any DocIR. Aliases come from the scaffold's
  nickname pool (`orgsmith/foundation/scaffold.py`:508-530) and client names
  from its seeded Faker draw (185-191), not from the model.

- **Every planned path is contained.** `_add` runs `check_relpath` on each
  registry-driven path before it enters the plan (planner.py:207-209). That
  check rejects over-length paths, empty or absolute components, `..`, both
  separators and the other forbidden characters, C0 controls, and trailing
  dots (`orgsmith/naming.py`:23-51). The `str.format` templates and the
  `getattr` attribute names are literals in `REGISTRY`
  (`orgsmith/docplan/registry.py`:114), so recipe text reaches a template
  only as an argument, never as the template. Derived noise paths
  (planner.py:1150-1535) skip `_add` but are built from checked paths plus
  fixed decorations, and `load_manifest` re-checks every `path` and
  `attach_path` at each load (`orgsmith/artifacts.py`:94-111), which is where
  render and validate read them. The planner itself joins no planned path to
  the filesystem.

- **Planner error text is terminal-safe.** Its `SystemExit` messages
  interpolate pattern-constrained ids (`p:`, `f:`, `E-`;
  `orgsmith/schemas.py`:733, 846, 858), dates, counts, code constants, or
  `!r` reprs (paths, aliases, `attach_path`). The unsafe-path message (209)
  formats a list, whose `str` is the repr of each problem string. `repr`
  escapes ESC, DEL, C1 controls, U+202E, U+2066 and U+200B on this
  interpreter (checked this turn). The two `print` lines (1590, 1616-1619)
  name paths derived from the operator's own argv.

- **The M17e planner code is pure data handling.** The broadcast knob only
  empties a list note's `participants` after the recipient draw
  (planner.py:760-766). The overview knob filters through
  `overview_engagements` (`orgsmith/fabric/engagements.py`:312-326), a list
  comprehension over the ledger, into `f:<E-id>.client` refs
  (planner.py:829-845).

- **The list address cannot inject a header.** `derive_distribution_lists`
  builds the address from a charset-limited local part (`orgsmith/acl.py`:55)
  at the recipe's `domain` (61). The planner copies it into
  `render_params["dl"]` (planner.py:761), and the eml renderer sets it as `To`
  (`orgsmith/render/eml.py`:136) on an `EmailMessage(policy=policy.SMTP)`
  (212, 216). Assigning a header value that carries `\r\n`, `\n` or `\r`
  raises `ValueError` there (re-checked this turn on the venv's Python
  3.10.12).

- **`validate`'s reuse of the planner's selection functions is bounded.**
  `scan_selection` and `legacy_selection` (planner.py:91-125) also run on a
  received tree (`orgsmith/validate/rules.py`:1530-1550, 1650-1667). Their
  ratios are schema-bounded to [0, 1] (`orgsmith/schemas.py`:271-273), so
  `random.sample` is never asked for more than its population. New this
  turn: `scan_selection` passes the received charter's `seed` to `rng`, whose
  `derive_seed` formats it with an f-string (`orgsmith/seeds.py`:14), and
  Python 3.10.12 refuses to format an int over 4300 digits. That path is
  unreachable: pydantic 2.13.4 rejects such an int when `charter.json` is
  parsed (4300 digits parse and format; 4301 and 5000 raise
  `ValidationError`), so the tree fails to load before any rule runs.

- **Every test write lands under a temporary directory.** The module's
  fixtures build from `tmp_path_factory` (test_unit_mail_broadcast.py:39-46)
  through `build_culture_stages`, which writes the knobbed recipe under its
  root and runs the pure stages there (`tests/conftest.py`:205-240).
  `run_enrichment` ingests a scripted test-double persona set, not a model
  reply (`tests/conftest.py`:323-337, 478-491), and the DL-01 test copies its
  org into `tmp_path` before planting (test_unit_mail_broadcast.py:115-127).
  The module's 5 tests pass at HEAD, and `git status --porcelain` was
  identical before and after the run.

### Considered and not filed

- **Symlinked write targets under a received tree.** `run_docplan`'s
  immutability guard is `paths.manifest_jsonl.exists()` (planner.py:1587),
  which is False for a dangling symlink, and `save_manifest`
  (`orgsmith/artifacts.py`:114-119) and `write_model` write with
  `Path.write_text`, which follows one. Not filed, for the reasons the
  2026-08-02 review gave for the same class (`9951200`): it needs a
  generation-side verb run on someone else's tree, past the `validate`
  premise the threat model supports, and every writer in the pipeline behaves
  the same.

- **`check_relpath` rejects only C0 controls.** DEL, C1 controls, and the
  bidi and zero-width format characters (U+202E, U+2066, U+200B) pass it
  (checked this turn), so a planned path could carry one. Not filed for this
  scope: every planned path component is operator recipe text (`service`), a
  scaffold-generated name, a date, or a code constant, and the planner prints
  paths only through `repr`. The helper itself (`orgsmith/naming.py`) is
  outside this scope.

- **`service` reaches filenames unsanitized** (planner.py:475, 527, 644),
  unlike `client`. It is the operator's own recipe text
  (`engagements.services`, `orgsmith/schemas.py`:504), and `_add`'s
  `check_relpath` keeps the result inside the share: a `/` adds a checked
  component, and `..` or a C0 control stops the plan.

- **The top-up pass can name a person in a document their ACL denies**
  (planner.py:952-974; BACKLOG `mention-filler-acl-seam`). This is
  ground-truth consistency, not access control: `derive_acl` reads
  `eng.internal_participants` (`orgsmith/acl.py`:115), never a manifest
  entry's participants, so the plant changes no grant.

### Coverage

- All eight dimensions were reviewed for the two scoped files, read in full.
  Helpers outside scope were read only as far as tracing a planner input or
  sink required (`orgsmith/naming.py`, `artifacts.py`, `acl.py`,
  `render/eml.py`, `seeds.py`, `foundation/ingest.py`,
  `foundation/scaffold.py`, `fabric/engagements.py`, `docplan/registry.py`,
  the two `validate/rules.py` call sites, the `schemas.py` models the planner
  reads, and `tests/conftest.py`); they were not themselves reviewed.
- Not attested. Authentication and authorization: no such code is in scope,
  and `acl.json` is synthetic ground truth, not an access control.
  Dependencies: no manifest is in scope, and neither file imports a
  third-party package other than `pytest`; pins were not checked against an
  advisory database. Infrastructure: no configuration file is in scope.
- Git history checked for secrets: no credential-handling files in scope, so
  no per-file credential check applied; the last three commits touching each
  scoped file were scanned anyway (above).

### Accepted Risks

None.

---
*Prior review (2026-10-13, scope paths, commit 12b1933): the three paths
`/codereview` named at `12b1933` (`orgsmith/docplan/planner.py`,
`tests/test_unit_mail_broadcast.py`, `tests/test_unit_overview_finished.py`),
each read in full; that commit changed only docstrings in the first two, and
the third was unchanged since `9dffb43`. No secret, real PII, or new sink, and
no new finding: the planner was shown to read no model-authored input and to
plan only contained paths. Two NOTEs stayed open (the oversight-title raw echo
and the unowned-number counter's unbounded `int()`), both carried above.*

<!-- SECURITY_META: {"date":"2026-10-13","commit":"9045bae5af8f0f0b60a9a4f6f29efe4a41c413ff","scope":"paths","scanned_files":["orgsmith/docplan/planner.py","tests/test_unit_mail_broadcast.py"],"block":0,"warn":0,"note":2} -->
