# Security

## Security Review — 2026-10-13 (scope: paths)

**Summary:** Reviewed the three paths `/codereview` named at `12b1933`, the one
commit not yet on `origin/main`: `orgsmith/docplan/planner.py`,
`tests/test_unit_mail_broadcast.py`, and `tests/test_unit_overview_finished.py`,
each read in full. The commit changes only docstrings in the first two
(planner.py:815-818, test_unit_mail_broadcast.py:67-72), and the third is
unchanged since `9dffb43`. No new finding: the planner reads no model-authored
input, every path it plans is contained, and nothing in scope adds a process,
network, or destructive filesystem sink. The two open NOTEs are in files
outside this scope and are carried without re-checking.

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
  scan (the 16 secret shapes of prior scans plus email, phone, IPv4, home or
  `/tmp/claude` path, and tailnet name, each first confirmed to fire on a
  synthetic positive) found nothing in the three files at HEAD. The same scan
  over `git log -p --follow -3` of each file (`12b1933`, `061da37`, `4fd9465`,
  `9dffb43`) hit only git `Author:` lines and `@pytest.fixture`. The mail
  subjects the planner hard-codes are generic (planner.py:703-714).

- **The planner reads no model-authored input.** Its stage requires only
  `charter`, `foundation` and `fabric` (planner.py:1586) and refuses to re-plan
  once a manifest exists (1587-1591), so no authored DocIR reaches it. The one
  model-written field among its inputs is `Person.persona`, the only field
  enrichment may fill (`orgsmith/foundation/ingest.py` merges only
  `(person_id, persona)` pairs), and the planner never reads it: its foundation
  reads are ids, names, aliases, departments, reporting lines, employment
  spans, and external names.

- **Every planned path is contained.** Each registry-driven path passes
  `check_relpath` in `_add` before it enters the plan (planner.py:207-209),
  which rejects `..`, empty or absolute components, and control or forbidden
  characters (`orgsmith/naming.py`:23-50). The `str.format` templates and the
  `getattr` attribute names are module constants in `REGISTRY`
  (`orgsmith/docplan/registry.py`:114-252), so no recipe or model text chooses
  a template or an attribute. Derived noise paths (planner.py:1150-1535) are
  built from already-checked paths plus fixed decorations, and `load_manifest`
  re-checks every `path` and `attach_path` at each load
  (`orgsmith/artifacts.py`:94-112), which is where render and validate read
  them.

- **Planner error text is terminal-safe.** Its `SystemExit` messages
  interpolate pattern-constrained ids (`p:`, `f:`, `E-`;
  `orgsmith/schemas.py`:733, 846, 858), dates, counts, code constants, or `!r`
  reprs (paths, aliases, `attach_path`). `repr` escapes ESC, C1 controls, and
  the bidi and zero-width format characters (checked on this interpreter). The
  two `print` lines name paths derived from the operator's own argv.

- **The M17e planner code is pure data handling.** The broadcast knob only
  empties a list note's `participants` after the recipient draw
  (planner.py:760-766), and the overview knob goes through the pure filter
  `overview_engagements` (`orgsmith/fabric/engagements.py`:322-326) into
  `facts_refs` ids (planner.py:829-845).

- **The list address cannot inject a header.** The planner copies
  `derive_distribution_lists`' address (a charset-limited local part at the
  recipe's `domain`, `orgsmith/acl.py`:55-61) into `render_params["dl"]`
  (planner.py:761). The eml renderer sets it as `To` on an
  `EmailMessage(policy=policy.SMTP)` (`orgsmith/render/eml.py`:134-136,
  212-216), and assigning a value that carries CR or LF raises `ValueError`
  there (checked with `\r\n` and `\n` on the venv's stdlib).

- **`validate`'s reuse of the planner's selection functions is bounded.**
  `scan_selection` and `legacy_selection` (planner.py:91-125) also run on a
  received tree (`orgsmith/validate/rules.py`:1530-1536, 1650-1659). Their
  ratios are schema-bounded to [0, 1] (`orgsmith/schemas.py`:271-273), so
  `random.sample` cannot be asked for more than its population.

- **Every test write lands under a temporary directory.** Both modules build
  from `tmp_path_factory` through `build_culture_stages` and
  `build_pure_stages`, which read the committed recipe and write only under
  their root (`tests/conftest.py`:49-78, 205-240), and the DL-01 test copies
  its org into `tmp_path` before planting (test_unit_mail_broadcast.py:115-127).
  The two modules' 9 tests pass at HEAD, and `git status` was unchanged
  afterwards.

### Considered and not filed

- **Symlinked write targets under a received tree.** `run_docplan`'s
  immutability guard is `paths.manifest_jsonl.exists()` (planner.py:1587),
  which is False for a dangling symlink, and `save_manifest`
  (`orgsmith/artifacts.py`:114-119) and `write_model`
  (`orgsmith/schemas.py`:67-69) write with `Path.write_text`, which follows
  one. Not filed, for the reasons the 2026-08-02 review gave for the same class
  (`9951200`): it needs a generation-side verb run on someone else's tree, past
  the `validate` premise the threat model supports, and every writer in the
  pipeline behaves the same.

- **`service` reaches filenames unsanitized** (planner.py:475, 527, 644),
  unlike `client`. It is the operator's own recipe text
  (`engagements.services`, `orgsmith/schemas.py`:504), and `_add`'s
  `check_relpath` keeps the result inside the share: a `/` adds a checked
  component, and `..` or a control character stops the plan.

- **The top-up pass can name a person in a document their ACL denies**
  (planner.py:952-974; BACKLOG `mention-filler-acl-seam`). This is
  ground-truth consistency, not access control: `derive_acl` reads
  `eng.internal_participants` (`orgsmith/acl.py`:115), never a manifest
  entry's participants, so the plant changes no grant.

### Coverage

- All eight dimensions were reviewed for the three scoped files, read in full.
  Helpers outside scope were read only as far as tracing a planner input or
  sink required (`orgsmith/naming.py`, `artifacts.py`, `acl.py`,
  `render/eml.py`, `foundation/ingest.py`, `fabric/engagements.py`,
  `docplan/registry.py`, `tests/conftest.py`); they were not themselves
  reviewed.
- Not attested. Authentication and authorization: no such code is in scope,
  and `acl.json` is synthetic ground truth, not an access control.
  Dependencies: no manifest is in scope and the three files add no third-party
  import; pins were not checked against a live advisory database (the review
  ran offline). Infrastructure: no configuration file is in scope.
- Git history checked for secrets: no credential-handling files in scope, so
  no per-file credential check applied; the last three commits touching each
  scoped file were scanned anyway (above).

### Accepted Risks

None.

---
*Prior review (2026-10-13, scope paths, commit 0c231b9): the 616 paths of the
M17e range (`03f6442..0c231b9`), covering the two default-off knobs, DL-01's new
check, the M17d code-review fixes, `tools/mail_device.py`, eight test modules,
the version bump, the seven frozen orgs' re-emitted charters, and the
carve-out regeneration of `ashcombe-advisory`, `hollowell-ip`, and
`meridian-actuarial`, plus a post-fix re-check of
`tests/test_unit_overview_finished.py`. No secret, real PII, dependency
movement, or new sink in `orgsmith/`, and no new finding; two NOTEs stayed
open (the oversight-title raw echo, re-confirmed then, and the unowned-number
counter's unbounded `int()`), both carried above.*

<!-- SECURITY_META: {"date":"2026-10-13","commit":"12b193317facb906d4788943f4057a137ece760e","scope":"paths","scanned_files":["orgsmith/docplan/planner.py","tests/test_unit_mail_broadcast.py","tests/test_unit_overview_finished.py"],"block":0,"warn":0,"note":2} -->
