# Security

## Security Review — 2026-10-13 (scope: paths)

**Summary:** Reviewed the 263 files of the M17d range (`aef75a9..03f6442`,
31 commits) at `03f6442`: the BYO driver's effort and output-limit changes,
the state lock, the board digest, the REND-01 ingest check, the
unowned-number counter, the five generator knobs, the skill edits, the nine
re-emitted charters, the version bump, and the tenth org `quillon-harbor`
(131 metadata JSON files and 79 rendered files). No secret in tree or
history, no real PII, no dependency movement, and no new process, network,
or filesystem sink in `orgsmith/`. One NOTE: the new unowned-number counter
hands an unbounded digit run to `int()`, so a deliverable that passes
ingest can crash `report`.

**Post-fix re-check (same day):** the four files `/codefix` changed for the
code review's two WARNs: `orgsmith/fabric/finance.py`, `orgsmith/schemas.py`,
`tests/test_unit_era_shock.py`, and `tests/test_unit_oversight.py`. No finding
was open in them, so none is resolved. The finance fix is arithmetic only: the
expense anchors calibrate on the base year's pre-shock revenue, no seed draw
moves (committed `dev-mini` re-derives byte-identical with the knob off), and
a shock can no longer zero the Travel divisor (a 0.0001 revenue shock on the
base year builds clean in memory). The new tests write only under `tmp_path`
or parse in memory, and the two modules run 13 tests green. Secrets,
sanitization, AI-specific risk, data exposure, PII, and infrastructure were
checked for the four files; they hold no auth code and no dependency
manifest, and none handles credentials, so no history check applied. One new
NOTE: the oversight-title check echoes a received tree's strings raw into an
uncaught exception. Lines cited in that NOTE are in the post-fix working
tree; the earlier items cite `03f6442`, and the fix moves
`orgsmith/schemas.py` past line 663 down by 12.

### Findings

**[NOTE] orgsmith/review/numbers.py:44 — a digit run over 4300 characters in authored prose crashes `report`**

  Confidence: high that it crashes; security impact low.
  Attack vector: DocIR prose is model-controlled, the input the airlock
  treats as untrusted. `Block.text`, `items`, `header`, and `rows` carry no
  length or digit bound (`orgsmith/schemas.py`:1107-1115), and none of
  ingest's checks (block shape, placeholders, signers, the literal-value
  check, REND-01, hard cases, outline, mentions) bounds a number that no
  ledger owns, so a deliverable whose paragraph holds a run of 4301 or more
  digits ingests clean. `report` then reaches `render_report`,
  `unowned_lines` (`orgsmith/review/report.py`:437), and `numbers_in`,
  where `_NUMBER`'s `\d+` (line 33) matches the whole run and `int()`
  (line 44) raises `ValueError` under Python 3.10.12's 4300-digit
  conversion limit. Nothing catches it: `report` exits with a traceback and
  GENERATION-REPORT.md cannot be regenerated for that org; in BYO mode the
  closing loop raises `DriverError` at `report` once `validate` passes
  (`drivers/forge_external.py`:314-325); `/forge-review` Step 0 fails at
  the same call. `validate` never calls the counter, so validating a
  received tree is unaffected. No compliant author writes such a number,
  and the only effect is a loud failure of a measurement stage, hence NOTE.
  Evidence: reproduced in memory against committed `quillon-harbor`
  `d0003`, writing nothing. With a 4301-digit run appended to one paragraph
  the DocIR still validates, and `numbers_in(prose_text(doc))` raises
  `ValueError: Exceeds the limit (4300) for integer string conversion`.
  `tools/probe_numbers.py`:43 has the identical line.
  Remediation: in `orgsmith/review/numbers.py` only, bound the conversion
  before `int()` (skip a match longer than, say, 18 digits, or count it as
  one unowned value keyed by its string), and add a unit test with a
  5000-digit run. Leave `tools/probe_numbers.py` alone: its sha256 is pinned
  by the pre-registration (`docs/M17D-OPUS55-PROBE.md`:142) and the probe it
  graded is finished. The parity test compares the two counters only on six
  short samples (`tests/test_unit_numbers.py`:18-25, 38-40), so a length
  bound keeps it green.

**[NOTE] orgsmith/schemas.py:670-675 — the new oversight-title check echoes a received tree's strings raw, so a crafted `charter.json` can write escape sequences to the terminal through `validate`'s traceback**

  Confidence: high that the bytes reach the terminal (reproduced); low that
  the fix adds exposure, since a crafted tree already reaches the terminal
  another way.
  Attack vector: validating an org tree obtained from someone else is a
  supported operation (`orgsmith/validate/__init__.py`:69-70). `validate`
  loads the tree's `charter.json` in `Context.load`
  (`orgsmith/validate/rules.py`:47-50) with no handler, and neither `main`
  (`orgsmith/cli.py`:163) nor `orgsmith/__main__.py` catches what it raises.
  An `oversight_titles` entry that matches no `titles` list and no generic
  fallback fails the new check, which joins the unknown strings into its
  `ValueError` unescaped (line 674). pydantic copies that message verbatim
  into the `ValidationError`, and Python's traceback writes it to stderr,
  past the `strip_control` printer that sanitizes findings. The run still
  exits 1, so automation sees the failure, but an operator reading the
  terminal can be shown a cleared screen and a forged clean result line.
  Recipes are not a vector: on the `charter` stage the same message echoes
  the operator's own `ORG-CHARTER.md`, and no skill has a model write one.
  Evidence: reproduced on a scratch copy of committed `dev-mini`, writing
  nothing in the repo. With one `oversight_titles` entry carrying `ESC[2J`,
  `ESC[H`, and the text `validate: 40 rules run, 0 skipped, 0 findings`,
  `python -m orgsmith validate dev-mini --root <copy>` exits 1 with both raw
  ESC bytes on stderr; the unmodified copy validates clean. The earlier item
  "Validator output for received trees stays sanitized" holds for findings
  only. The class predates the fix: `_check_scope_services` joins
  `scope_by_service` keys the same way (line 527), and an unexpected charter
  key carrying the same bytes reaches stderr raw through pydantic's location
  line (also reproduced), which no change to a validator can reach. Both raw
  joins depart from the convention a prior review recorded for `docir_path`,
  now `doc_id_filename`'s `{doc_id!r}` (`orgsmith/naming.py`:83): `repr()`
  escapes control characters, "so even an uncaught raise cannot drive the
  terminal".
  Remediation: in this file, pass each unknown title through
  `strip_control(t, keep="")` before the join, and do the same at line 527.
  `orgsmith/naming.py` imports nothing from the package, so there is no
  cycle, and the new test's match string stays valid. The class-level fix is
  outside this post-fix scope: catch `ValidationError` where `validate` loads
  a received tree and print it through `strip_control`, as ingest already
  does (`orgsmith/authoring/ingest.py`:396-399).

### Verified this turn

- **No secret, in tree or in history.** A pattern scan (OpenAI, Anthropic,
  OpenRouter, Google, AWS, GitHub, Slack, private-key, bearer, JWT,
  key-assignment, and credential-in-URL shapes, first confirmed to fire on
  synthetic positives) over all 184 scoped text files at HEAD, the full
  `aef75a9..03f6442` diff, the XML parts of all 69 rendered OOXML files, and
  the pypdf-extracted text of all 8 PDFs: zero hits. `git log -p --follow -3`
  of the four driver files and `tests/test_unit_driver.py`: zero hits.
  `drivers/providers.env.example` ships commented placeholders only
  (`sk-...`, `sk-ant-...`); no env, key, or PEM file is tracked;
  `providers.env` and `drivers/providers.env` stay ignored (`.gitignore`:20-21).
  Test keys are stubs (`"sk-ant"`, `"sk-test"`) behind a fixture that clears
  every provider variable and points at an absent config file
  (`tests/test_unit_driver.py`:37-55).

- **Key handling is unchanged by the driver edits.** The range adds
  `output_config.effort` to the Anthropic body, validated against
  `EFFORT_ORDER` before any request (`drivers/config.py`:258-265), per-provider
  output caps, a 600 s timeout, and truncation detection
  (`drivers/providers.py`:143-145, 178-180). `--check` still prints key
  presence only (`drivers/forge_external.py`:371-372); every new log line
  carries a provider name, a cap, or a reason string; and the driver
  overwrites any model-supplied `generator` stamp with its own
  (`drivers/forge_external.py`:213-216).

- **The airlock holds.** Beyond intra-package imports, the new `orgsmith/`
  code adds only `hashlib`, `re`, `os`, `fcntl`, `contextlib`, and
  `pathlib`. A grep of all 35 scoped Python files for
  process, network, `eval`/`exec`, pickle, unsafe YAML, and destructive
  filesystem calls finds only the driver's existing `urlopen`
  (`drivers/providers.py`:44), outside `orgsmith/` by design. The new
  skill-command test only calls `parse_args` on argv extracted from the
  skills and never executes a command (`tests/test_short.py`:351-360).

- **The new consumers of model text are linear and print nothing raw.**
  REND-01's `_FOLLOWING_WORD` is an anchored `.match()` with no nested
  quantifier (`orgsmith/authoring/ingest.py`:246), and its rejection message
  interpolates only `[A-Za-z'-]` words and ledger values, printed through
  `strip_control` (`orgsmith/authoring/ingest.py`:487). `numbers.py`'s
  `_NUMBER` backtracks at most one `,ddd` group per start, so there is no
  ReDoS, and `unowned_lines` writes only `^d:\d{4}$` doc ids, counts, and
  integers into GENERATION-REPORT.md.

- **The state lock has no lock file to race.** `state_lock` takes `flock`
  on the org's metadata directory itself, opened `O_RDONLY`
  (`orgsmith/state.py`:174-176), so there is nothing to pre-create, symlink,
  or leave in a committed tree, and the kernel releases the lock when its
  holder exits.

- **The board digest is not self-certifying.** The chair keeps the Step 0
  digest in its own context and passes it to `--verify-digest`
  (`.claude/skills/forge-review/SKILL.md`:60-62, 111-119); fresh-context
  reviewers never see it and cannot rewrite it. Entries are keyed on
  resolved paths (`orgsmith/review/digest.py`:52), so replacing a covered
  file with a symlink into `review/` or anywhere else changes the digest. A
  symlink that resolves outside the repo root raises in `relative_to`
  (lines 45, 52) and exits non-zero, which the skill treats as a failure,
  and Python 3.10's `rglob` does not descend symlinked directories.

- **Validator output for received trees stays sanitized.** CAL-01's new
  half and OVR-01 interpolate dates, `^E-\d{4}-\d{3}$` engagement ids, and
  `^p:[a-z0-9.\-]+$` person ids (`orgsmith/schemas.py`:700, 825), and
  `validate` prints every finding field through `strip_control`
  (`orgsmith/validate/__init__.py`:89-97).

- **Recipe inputs to the new knobs are bounded.** `EraShock` holds revenue
  in (0, 2], travel in [0, 2], and four positive quarter weights
  (`orgsmith/schemas.py`:342-365); shock years are unique (387-392) and must
  fall in the firm's fiscal span (`orgsmith/fabric/finance.py`:84-90); and
  `scope_by_service` keys must be declared services
  (`orgsmith/schemas.py`:521-529).

- **The rendered corpus carries no active content and no host detail.** The
  69 OOXML files have no `vbaProject`, no OLE embedding, no
  `TargetMode="External"` relationship, and no local path. Their only
  non-namespace URL is the Apple plist DTD inside the seven decks'
  `ppt/printerSettings/printerSettings1.bin`, which is byte-identical
  (sha256 `d7768f87...`) to python-pptx's shipped template. Every file
  carries `OrgSmithSynthetic=true` in `docProps/custom.xml`, and the core
  properties name synthetic personas only. The 8 PDFs have no
  `/JavaScript`, `/JS`, `/OpenAction`, `/AA`, `/Launch`, `/URI`,
  `/EmbeddedFile`, `/XFA`, `/RichMedia`, or `/AcroForm`; their metadata is
  a persona, `Creator OrgSmith`, and `Producer WeasyPrint 69.0`. The 10
  workbooks hold only `SUM` and subtraction formulas over cell references,
  no DDE or external link, and no shared string starting with `=`, `+`,
  `-`, or `@`. Filenames add only commas and one pair of parentheses to
  `/._ -`, and no path component starts with `-`.

- **No real PII and no injection-shaped text.** Across 39,582 strings in the
  131 metadata JSON files there is no control, bidi, or zero-width
  character, no markup, and no URL. Emails sit only at synthetic firm and
  client domains (`quillonharbor.com`, `morseplc.com`, and the like), phones
  only in the reserved 555-01xx block, and no home path, `/tmp/claude` path,
  IP address, or tailnet name appears anywhere in scope. The 91
  model-authored files (DocIR, author replies, review replies, merged
  findings) contain no instruction-shaped phrasing, and the 19 author work
  orders share one fixed `instructions` template that differs only in the
  work-order id. `state.json` records `claude-opus-5-5` at `xhigh` and empty
  `probes`. The `authors` field (`pyproject.toml`:19) is deliberate
  authorship metadata, as prior reviews recorded.

- **No dependency movement.** `pyproject.toml` and `requirements.lock`
  change only version strings, and every pin is identical to `aef75a9`.
  `requirements.txt`, `requirements-dev.txt`, the Dockerfile, `.github/`,
  `bin/`, and `hooks/` are untouched in the range. The nine existing
  `charter.json` files gain only inert defaults (`engagement_starts: false`,
  `era_shocks: []`, `oversight_titles: []`, `scope_by_service: {}`).

- **Every test write lands under `tmp_path`.** That includes
  `tests/test_flagship_plant_defects.py`, which digests the committed
  `calderwood-partners` before and after the plant run and asserts it
  unchanged (lines 36, 43). The seven security-relevant modules
  (`test_short`, `test_unit_state_lock`, `test_unit_review_digest`,
  `test_unit_numbers`, `test_unit_count_noun`, `test_unit_driver`,
  `test_unit_paths`) run 148 tests green at `03f6442`, so the code traced
  above is the code that runs.

### Considered and not filed

- **The lock waits without a timeout.** `fcntl.flock(fd, fcntl.LOCK_EX)`
  blocks indefinitely (`orgsmith/state.py`:176). A stopped holder (Ctrl-Z)
  stalls every other state writer silently, and with the metadata directory
  at 0775 any local account able to read it could do the same. Not filed: a
  crashed holder releases automatically, and on this single-user box the
  only party that can hold the lock is the operator.

- **The digest does not cover the code that computes it.** A reviewer that
  edited `orgsmith/review/digest.py` could make `--verify-digest` pass over
  a ledger edit. Not filed: the check targets a well-meaning reviewer that
  "fixed" a sentence (its own docstring), `git status` shows any edit under
  `orgsmith/`, and `PINNED = SLUGS` fails on any change to a committed
  org's ledgers or prose.

- **`base_url` is echoed.** `--check` and `--dry-run` print the full base URL
  (`drivers/forge_external.py`:365, 467-473), so a URL carrying a credential
  would reach stdout and, under `/forge` Step 0.5, the agent's transcript.
  Not filed: urllib cannot authenticate with userinfo (without a port it
  raises `InvalidURL`; with one, a hostname containing `@` cannot resolve),
  so no working configuration carries a credential there, and keys travel
  only in headers.

- **Synthetic names can coincide with real ones.** Faker
  surname-and-suffix clients ("Morse PLC", "Hamilton PLC") and personas are
  generic, and the 248-entry real-firm screen behind NAME-01
  (`orgsmith/data/real_firms.txt`) passes all eight clients. Company names
  are not personal data, and prior fixture reviews treat the convention the
  same way.

- **Path composition from `slug`** in `tools/plant_defects.py` and
  `tools/probe_numbers.py`, as the prior entry recorded for the A/B tools:
  operator-supplied argv and a repo-wide property. `plant_defects.py` also
  refuses an existing destination (lines 117-118) and an `--out` equal to
  the source root (lines 153-154), and `copytree`'s default
  `symlinks=False` makes every planted write land on a regular-file copy.

### Coverage

- All eight dimensions were reviewed for the 263 scoped files.
- Not attested. Authentication and authorization: no such code is in
  scope, and `acl.json` and `evals/visibility.jsonl` are synthetic ground
  truth, not access controls. Dependency advisories: the pins were not
  checked against a live vulnerability database (the review ran offline);
  no pin moved in the range, so the range adds no dependency exposure.
  `orgsmith/render/` is outside the scope list and unchanged in the range,
  including the WeasyPrint fetcher that serves only `data:` URIs
  (`orgsmith/render/pdf.py`:19-26), fixed after the 2026-07-14 review. The
  range's Markdown files (README, BACKLOG, SPEC, TESTING, `docs/`, the data
  cards, GENERATION-REPORT.md, TOC.md, PERMISSIONS.md, and both recipe
  `ORG-CHARTER.md` files) are outside the scope list and were not reviewed.
- Git history checked for secrets: `drivers/config.py`,
  `drivers/forge_external.py`, `drivers/providers.py`,
  `drivers/providers.env.example`, and `tests/test_unit_driver.py`
  (`git log -p --follow -3` each), plus the full `aef75a9..03f6442` diff.

### Accepted Risks

None.

---
*Prior review (2026-08-10, scope paths, commit c5b9994): the five M17c A/B
tool and test files, including the replicate arm and the lexical axis. No
secret, PII, dependency change, or sink, and no model-authored text reaching
an output or a decision; zero findings, with the in-place-overwrite footgun
recorded as closed and the `strip_control` bypass in the A/B printers and
`slug` path composition considered and not filed.*

<!-- SECURITY_META: {"date":"2026-10-13","commit":"03f6442553c9989f3cdb0742af2c3639d5d74c13","scope":"paths","scanned_files":[".claude/skills/forge-author/SKILL.md",".claude/skills/forge-review/SKILL.md",".claude/skills/forge-reviewer/SKILL.md",".claude/skills/forge/SKILL.md","CLAUDE.md","companies/ashcombe-advisory-metadata/charter.json","companies/brackenridge-civil-metadata/charter.json","companies/calderwood-partners-metadata/charter.json","companies/dev-mini-metadata/charter.json","companies/hollowell-ip-metadata/charter.json","companies/meridian-actuarial-metadata/charter.json","companies/northgate-staffing-metadata/charter.json","companies/quillon-harbor-metadata/baselines/summary.json","companies/quillon-harbor-metadata/charter.json","companies/quillon-harbor-metadata/docir/d0002.json","companies/quillon-harbor-metadata/docir/d0003.json","companies/quillon-harbor-metadata/docir/d0004.json","companies/quillon-harbor-metadata/docir/d0005.json","companies/quillon-harbor-metadata/docir/d0006.json","companies/quillon-harbor-metadata/docir/d0007.json","companies/quillon-harbor-metadata/docir/d0008.json","companies/quillon-harbor-metadata/docir/d0010.json","companies/quillon-harbor-metadata/docir/d0011.json","companies/quillon-harbor-metadata/docir/d0012.json","companies/quillon-harbor-metadata/docir/d0013.json","companies/quillon-harbor-metadata/docir/d0014.json","companies/quillon-harbor-metadata/docir/d0015.json","companies/quillon-harbor-metadata/docir/d0016.json","companies/quillon-harbor-metadata/docir/d0017.json","companies/quillon-harbor-metadata/docir/d0019.json","companies/quillon-harbor-metadata/docir/d0020.json","companies/quillon-harbor-metadata/docir/d0021.json","companies/quillon-harbor-metadata/docir/d0022.json","companies/quillon-harbor-metadata/docir/d0023.json","companies/quillon-harbor-metadata/docir/d0024.json","companies/quillon-harbor-metadata/docir/d0026.json","companies/quillon-harbor-metadata/docir/d0027.json","companies/quillon-harbor-metadata/docir/d0028.json","companies/quillon-harbor-metadata/docir/d0029.json","companies/quillon-harbor-metadata/docir/d0030.json","companies/quillon-harbor-metadata/docir/d0032.json","companies/quillon-harbor-metadata/docir/d0033.json","companies/quillon-harbor-metadata/docir/d0034.json","companies/quillon-harbor-metadata/docir/d0035.json","companies/quillon-harbor-metadata/docir/d0036.json","companies/quillon-harbor-metadata/docir/d0037.json","companies/quillon-harbor-metadata/docir/d0038.json","companies/quillon-harbor-metadata/docir/d0040.json","companies/quillon-harbor-metadata/docir/d0041.json","companies/quillon-harbor-metadata/docir/d0042.json","companies/quillon-harbor-metadata/docir/d0043.json","companies/quillon-harbor-metadata/docir/d0044.json","companies/quillon-harbor-metadata/docir/d0045.json","companies/quillon-harbor-metadata/docir/d0046.json","companies/quillon-harbor-metadata/docir/d0048.json","companies/quillon-harbor-metadata/docir/d0049.json","companies/quillon-harbor-metadata/docir/d0051.json","companies/quillon-harbor-metadata/docir/d0052.json","companies/quillon-harbor-metadata/docir/d0053.json","companies/quillon-harbor-metadata/docir/d0054.json","companies/quillon-harbor-metadata/docir/d0055.json","companies/quillon-harbor-metadata/docir/d0056.json","companies/quillon-harbor-metadata/docir/d0058.json","companies/quillon-harbor-metadata/docir/d0059.json","companies/quillon-harbor-metadata/docir/d0060.json","companies/quillon-harbor-metadata/docir/d0061.json","companies/quillon-harbor-metadata/docir/d0062.json","companies/quillon-harbor-metadata/docir/d0064.json","companies/quillon-harbor-metadata/docir/d0065.json","companies/quillon-harbor-metadata/docir/d0066.json","companies/quillon-harbor-metadata/docir/d0067.json","companies/quillon-harbor-metadata/docir/d0068.json","companies/quillon-harbor-metadata/docir/d0069.json","companies/quillon-harbor-metadata/docplan/manifest.jsonl","companies/quillon-harbor-metadata/evals/clusters.json","companies/quillon-harbor-metadata/evals/diagnostics.json","companies/quillon-harbor-metadata/evals/extraction.jsonl","companies/quillon-harbor-metadata/evals/graph_expected.json","companies/quillon-harbor-metadata/evals/retrieval.jsonl","companies/quillon-harbor-metadata/evals/splits.json","companies/quillon-harbor-metadata/evals/visibility.jsonl","companies/quillon-harbor-metadata/foundation.json","companies/quillon-harbor-metadata/ledger/acl.json","companies/quillon-harbor-metadata/ledger/engagements.json","companies/quillon-harbor-metadata/ledger/finance.json","companies/quillon-harbor-metadata/ledger/graph.json","companies/quillon-harbor-metadata/ledger/mention_map.json","companies/quillon-harbor-metadata/ledger/style_specs.json","companies/quillon-harbor-metadata/review/findings/cross_document_voice.json","companies/quillon-harbor-metadata/review/findings/document_plausibility.json","companies/quillon-harbor-metadata/review/findings/finance_realism.json","companies/quillon-harbor-metadata/review/findings/graph_acl_naturalness.json","companies/quillon-harbor-metadata/review/findings/narrative_consistency.json","companies/quillon-harbor-metadata/review/findings/org_realism.json","companies/quillon-harbor-metadata/review/metrics.json","companies/quillon-harbor-metadata/review/reply-cross_document_voice.json","companies/quillon-harbor-metadata/review/reply-document_plausibility.json","companies/quillon-harbor-metadata/review/reply-finance_realism.json","companies/quillon-harbor-metadata/review/reply-graph_acl_naturalness.json","companies/quillon-harbor-metadata/review/reply-narrative_consistency.json","companies/quillon-harbor-metadata/review/reply-org_realism.json","companies/quillon-harbor-metadata/review/sample.json","companies/quillon-harbor-metadata/state.json","companies/quillon-harbor-metadata/workorders/author-0001.json","companies/quillon-harbor-metadata/workorders/author-0002.json","companies/quillon-harbor-metadata/workorders/author-0003.json","companies/quillon-harbor-metadata/workorders/author-0004.json","companies/quillon-harbor-metadata/workorders/author-0005.json","companies/quillon-harbor-metadata/workorders/author-0006.json","companies/quillon-harbor-metadata/workorders/author-0007.json","companies/quillon-harbor-metadata/workorders/author-0008.json","companies/quillon-harbor-metadata/workorders/author-0009.json","companies/quillon-harbor-metadata/workorders/author-0010.json","companies/quillon-harbor-metadata/workorders/author-0011.json","companies/quillon-harbor-metadata/workorders/author-0012.json","companies/quillon-harbor-metadata/workorders/author-0013.json","companies/quillon-harbor-metadata/workorders/author-0014.json","companies/quillon-harbor-metadata/workorders/author-0015.json","companies/quillon-harbor-metadata/workorders/author-0016.json","companies/quillon-harbor-metadata/workorders/author-0017.json","companies/quillon-harbor-metadata/workorders/author-0018.json","companies/quillon-harbor-metadata/workorders/author-0019.json","companies/quillon-harbor-metadata/workorders/foundation-0001.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0001.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0002.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0003.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0004.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0005.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0006.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0007.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0008.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0009.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0010.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0011.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0012.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0013.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0014.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0015.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0016.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0017.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0018.json","companies/quillon-harbor-metadata/workorders/reply-wo-author-0019.json","companies/quillon-harbor-metadata/workorders/reply-wo-foundation-0001.json","companies/quillon-harbor/Engagements/Armstrong, Silva and Dyer/2014.07.01 - Engagement Letter - Armstrong, Silva and Dyer - EXECUTED.pdf","companies/quillon-harbor/Engagements/Armstrong, Silva and Dyer/2014.07.14 - Kickoff Memo - Sell-Side Advisory.docx","companies/quillon-harbor/Engagements/Armstrong, Silva and Dyer/2014.09.12 - Briefing Deck - Armstrong, Silva and Dyer.pptx","companies/quillon-harbor/Engagements/Armstrong, Silva and Dyer/2014.11.14 - Status Report - Armstrong, Silva and Dyer v2 FINAL.docx","companies/quillon-harbor/Engagements/Armstrong, Silva and Dyer/2015.03.14 - Status Report - Armstrong, Silva and Dyer v2 FINAL.docx","companies/quillon-harbor/Engagements/Armstrong, Silva and Dyer/Meeting Minutes 2014-10-20 - Armstrong, Silva and Dyer.docx","companies/quillon-harbor/Engagements/Armstrong, Silva and Dyer/Meeting Minutes 2015-01-19 - Armstrong, Silva and Dyer.docx","companies/quillon-harbor/Engagements/Beck, Martin and Dawson/2022.07.26 - Engagement Letter - Beck, Martin and Dawson - EXECUTED.pdf","companies/quillon-harbor/Engagements/Beck, Martin and Dawson/2022.08.08 - Kickoff Memo - Growth Capital Raise.docx","companies/quillon-harbor/Engagements/Beck, Martin and Dawson/2022.10.16 - Status Report - Beck, Martin and Dawson v2 FINAL.docx","companies/quillon-harbor/Engagements/Beck, Martin and Dawson/Meeting Minutes 2022-09-30 - Beck, Martin and Dawson.docx","companies/quillon-harbor/Engagements/Blankenship Inc/2018.03.23 - Engagement Letter - Blankenship Inc - EXECUTED.pdf","companies/quillon-harbor/Engagements/Blankenship Inc/2018.04.05 - Kickoff Memo - Management Buyout Advisory (copy).docx","companies/quillon-harbor/Engagements/Blankenship Inc/2018.04.05 - Kickoff Memo - Management Buyout Advisory.docx","companies/quillon-harbor/Engagements/Blankenship Inc/2018.06.08 - Briefing Deck - Blankenship Inc.pptx","companies/quillon-harbor/Engagements/Blankenship Inc/2018.08.15 - Status Report - Blankenship Inc v2 FINAL.docx","companies/quillon-harbor/Engagements/Blankenship Inc/2018.12.13 - Status Report - Blankenship Inc v2 FINAL.docx","companies/quillon-harbor/Engagements/Blankenship Inc/Meeting Minutes 2018-07-19 - Blankenship Inc.docx","companies/quillon-harbor/Engagements/Blankenship Inc/Meeting Minutes 2018-10-17 - Blankenship Inc.docx","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/2019.05.03 - Engagement Letter - Browning, Duffy and Santos - EXECUTED.pdf","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/2019.05.16 - Kickoff Memo - Carve-Out Advisory.docx","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/2019.06.25 - Briefing Deck - Browning, Duffy and Santos.pptx","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/2019.08.08 - Status Report - Browning, Duffy and Santos v2 FINAL - DRAFT.docx","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/2019.08.08 - Status Report - Browning, Duffy and Santos v2 FINAL.docx","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/Copy of 2017.02.19 - Onboarding - Amanda Thomas.docx","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/Meeting Minutes 2019-07-22 - Browning, Duffy and Santos.docx","companies/quillon-harbor/Engagements/Browning, Duffy and Santos/Meeting Minutes 2019-10-18 - Browning, Duffy and Santos.docx","companies/quillon-harbor/Engagements/Hamilton PLC/2021.08.03 - Engagement Letter - Hamilton PLC - EXECUTED.pdf","companies/quillon-harbor/Engagements/Hamilton PLC/2021.08.16 - Kickoff Memo - Fairness Opinion.docx","companies/quillon-harbor/Engagements/Hamilton PLC/2021.09.19 - Briefing Deck - Hamilton PLC.pptx","companies/quillon-harbor/Engagements/Hamilton PLC/2021.10.26 - Status Report - Hamilton PLC v2 FINAL.docx","companies/quillon-harbor/Engagements/Hamilton PLC/Meeting Minutes 2021-10-11 - Hamilton PLC.docx","companies/quillon-harbor/Engagements/Hamilton PLC/Meeting Minutes 2021-10-11 - Hamilton PLC_old.docx","companies/quillon-harbor/Engagements/Ingram, Bowers and Roth/2023.06.09 - Engagement Letter - Ingram, Bowers and Roth - EXECUTED.pdf","companies/quillon-harbor/Engagements/Ingram, Bowers and Roth/2023.06.22 - Kickoff Memo - Strategic Alternatives Review.docx","companies/quillon-harbor/Engagements/Ingram, Bowers and Roth/2023.09.17 - Status Report - Ingram, Bowers and Roth v2 FINAL.docx","companies/quillon-harbor/Engagements/Ingram, Bowers and Roth/Meeting Minutes 2023-08-30 - Ingram, Bowers and Roth.docx","companies/quillon-harbor/Engagements/Ingram, Bowers and Roth/Meeting Minutes 2023-11-28 - Ingram, Bowers and Roth.docx","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/2016.06.25 - Engagement Letter - Lawson, Keller and Owens - EXECUTED.pdf","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/2016.07.08 - Kickoff Memo - Recapitalization Advisory.docx","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/2016.08.05 - Briefing Deck - Lawson, Keller and Owens.pptx","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/2016.09.06 - Status Report - Lawson, Keller and Owens v2 FINAL - v1.docx","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/2016.09.06 - Status Report - Lawson, Keller and Owens v2 FINAL - v2.docx","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/2016.09.06 - Status Report - Lawson, Keller and Owens v2 FINAL.docx","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/Archive/.gitkeep","companies/quillon-harbor/Engagements/Lawson, Keller and Owens/Meeting Minutes 2016-08-24 - Lawson, Keller and Owens.docx","companies/quillon-harbor/Engagements/Morse PLC/2015.03.10 - Engagement Letter - Morse PLC - EXECUTED.pdf","companies/quillon-harbor/Engagements/Morse PLC/2015.03.23 - Kickoff Memo - Buy-Side Search.docx","companies/quillon-harbor/Engagements/Morse PLC/2015.05.05 - Briefing Deck - Morse PLC DO NOT USE.pptx","companies/quillon-harbor/Engagements/Morse PLC/2015.05.05 - Briefing Deck - Morse PLC.pptx","companies/quillon-harbor/Engagements/Morse PLC/2015.06.20 - Status Report - Morse PLC v2 FINAL.docx","companies/quillon-harbor/Engagements/Morse PLC/Meeting Minutes 2015-06-02 - Morse PLC.docx","companies/quillon-harbor/Engagements/Morse PLC/Meeting Minutes 2015-08-31 - Morse PLC.docx","companies/quillon-harbor/Finance/FY2013 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2014 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2015 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2016 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2017 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2018 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2019 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2020 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2021 Financial Summary.xlsx","companies/quillon-harbor/Finance/FY2022 Financial Summary.xlsx","companies/quillon-harbor/Firm/Backup/.gitkeep","companies/quillon-harbor/Firm/Firm Overview 2014 v3.docx","companies/quillon-harbor/Firm/Firm Overview 2017 v3.docx","companies/quillon-harbor/Firm/Firm Overview 2020 v3.docx","companies/quillon-harbor/Firm/Firm Overview 2023 v3.docx","companies/quillon-harbor/People/2014.08.21 - Onboarding - Melissa Jacobson.docx","companies/quillon-harbor/People/2016.05.16 - Onboarding - Justin Gonzalez.docx","companies/quillon-harbor/People/2017.02.19 - Onboarding - Amanda Thomas.docx","companies/quillon-harbor/People/2017.02.23 - Onboarding - Kelly Brown.docx","companies/quillon-harbor/People/2017.04.14 - Onboarding - Angela Cole.docx","companies/quillon-harbor/People/2018.01.10 - Onboarding - James Lawson.docx","companies/quillon-harbor/People/2019.06.03 - Onboarding - Michael Duffy.docx","companies/quillon-harbor/People/2020.06.04 - Onboarding - John Bauer.docx","companies/quillon-harbor/People/2021.11.18 - Onboarding - Kimberly Harris.docx","companies/quillon-harbor/People/2022.08.18 - Onboarding - Nancy Burgess.docx","companies/quillon-harbor/Templates/Kickoff Memo Template OLD.docx","companies/saltmarsh-environmental-metadata/charter.json","companies/verdant-health-metadata/charter.json","drivers/config.py","drivers/forge_external.py","drivers/providers.env.example","drivers/providers.py","orgsmith/__init__.py","orgsmith/authoring/contexts.py","orgsmith/authoring/ingest.py","orgsmith/cli.py","orgsmith/docplan/planner.py","orgsmith/fabric/engagements.py","orgsmith/fabric/finance.py","orgsmith/review/digest.py","orgsmith/review/numbers.py","orgsmith/review/report.py","orgsmith/schemas.py","orgsmith/state.py","orgsmith/validate/rules.py","pyproject.toml","requirements.lock","schemas/charter@1.json","tests/conftest.py","tests/test_flagship_plant_defects.py","tests/test_org_datacard.py","tests/test_short.py","tests/test_unit_ab_control.py","tests/test_unit_count_noun.py","tests/test_unit_driver.py","tests/test_unit_engagement_starts.py","tests/test_unit_era_shock.py","tests/test_unit_numbers.py","tests/test_unit_oversight.py","tests/test_unit_paths.py","tests/test_unit_review_digest.py","tests/test_unit_scope_by_service.py","tests/test_unit_scope_facts.py","tests/test_unit_state_lock.py","tools/checksums.py","tools/plant_defects.py","tools/probe_numbers.py"],"block":0,"warn":0,"note":2} -->
