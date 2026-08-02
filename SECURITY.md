# Security

## Security Review — 2026-08-02 (scope: paths)

**Summary:** Reviewed the fifteen in-airlock files carrying the M17
answer-key turn (~2,400 added lines since the last baseline `9927e03`): the
new baselines, data cards, doc-text reader, cluster/diagnostics emitters,
ranked scorer, alias-agreement ingest gates, and the EVAL-01/MENT-03 rules.
No secret, no injection path, no PII. One NOTE: the `validate` plain-text
output is the last untrusted-string-to-terminal path in the tree that does
not pass through `strip_control`, unlike every other verb.

### Findings

```
[NOTE] orgsmith/validate/rules.py:332,579,616,707,812-813,956,1031,1352 —
validate findings interpolate unconstrained ledger strings and third-party
parser exception text, and the plain-text printer emits them raw.
  Attack vector: an operator validates an org directory obtained from
    someone else (`python -m orgsmith validate <slug>`, or `validate
    companies/<slug>`). A hostile `ledger/finance.json` (`LedgerCheck.name`
    / `.detail`), `ledger/graph.json` (`GraphEdge.src` / `.dst`),
    `ledger/acl.json` (`AclGrant.person`), or `foundation.json`
    (`Person.reports_to`) embeds an ANSI escape sequence; the rule quotes it
    into a finding message and `validate/__init__.py:69` prints
    `f"{severity} {rule} [{target}] {message}"` with no neutralization. The
    escape can rewrite or hide earlier findings on the terminal, which is
    exactly the outcome `strip_control` was introduced to prevent.
  Evidence: the four models above declare bare `str` fields
    (schemas.py:520,525,608-610,674-676,682-684), so pydantic constrains
    nothing. The rule messages interpolate them without `!r` (contrast
    acl_02's `{doc!r}` at rules.py:973, which repr-escapes correctly).
    `orgsmith/validate/__init__.py` imports no sanitizer, while
    `foundation/ingest.py:68`, `authoring/ingest.py:365`,
    `evals/score.py:553,607,652`, `review/ingest.py:121`, `airlock.py:89`
    and `datacard.py:34` all route untrusted text through `strip_control`
    with the same stated rationale.
  Remediation: wrap the two plain-text prints in
    `orgsmith/validate/__init__.py` in `strip_control(..., keep="")`, one
    finding per line, matching the score-failure printer. Optionally align
    `naming.check_filename`'s control test (`ord(ch) < 32`, naming.py:27)
    with `strip_control`'s `unicodedata.category(ch) == "Cc"` so DEL and the
    C1 range cannot ride in a manifest path either; that half is narrow
    (UTF-8 terminals generally do not decode U+009B as CSI) and is
    hardening, not the finding.
```

Severity is NOTE rather than WARN deliberately: the reachable input is an
org tree the operator chose to trust enough to validate, and the supported
third-party ingress points (`score --evals-dir`, `--answers`) are already
guarded.

### Verified this turn

- **The one model-output-to-filesystem sink is still triple-guarded.**
  `authoring/ingest.py:373` writes only after (a) `DocIR.doc_id`'s
  `^d:\d{4}$` pattern at parse (schemas.py:943), (b) the work-order
  membership check, which returns non-zero before the write loop
  (ingest.py:298-300, 358-366), and (c) `doc_id_filename`'s own
  `check_filename` (naming.py:70-84). No new sink was added: `evals/`,
  `baselines/`, and `DATA-CARD.md` all write fixed filenames under
  `OrgPaths`-derived directories (emit.py:1030, baselines.py:221,
  datacard.py:427).
- **Manifest-derived path joins remain contained.** `load_manifest`
  re-checks `entry.path` AND `render_params["attach_path"]` with
  `check_relpath` at every load (artifacts.py:99-109), so the new
  `_carries_bytes` read (emit.py:367-369) and `build_clusters`'
  `share_dir / path` hashing (emit.py:307-309) cannot escape the share.
  `docplan`'s derived-noise paths bypass `_add`'s check but are built from
  already-checked source paths plus constant decorations
  (planner.py:896-962), and are re-checked on the next load.
- **The new third-party-input path is clean.** `score --evals-dir` only
  reads; every failure line that echoes answer-file or evals-dir content is
  `strip_control(..., keep="")`-wrapped (score.py:553,607,652), values are
  additionally repr-escaped, and the one loop left unwrapped
  (score.py:637-641) interpolates a `Literal`-constrained edge kind.
- **Model output that persists is neutralized before it renders.** Board
  summaries are the only free-text model output reaching a committed
  markdown artifact; `datacard._cell` (datacard.py:29-34) strips control
  characters and escapes newline and pipe, so a summary cannot forge a table
  row. `ReviewFinding.id` and `.severity` are pattern/`Literal`-constrained
  (schemas.py:1352-1361) and are written only after
  `ReviewFindings.model_validate_json` (review/ingest.py:80).
- **No command injection, no network, no new dependency.** The only
  subprocess in scope is `tools/checksums.py:35`, fixed argv, no
  `shell=True`, slugs from a hardcoded list. Nothing in scope imports
  `urllib`/`requests`/`socket`; the BM25 baseline is hand-rolled to avoid
  adding one (baselines.py:71-121). Every new regex escapes its needle
  (`re.escape` in schemas.py:905, emit.py:395, ingest.py:52,133) or is
  bounded and anchored (ingest.py:42-45, eml.py:27-29), so no ReDoS.
- **Considered and not flagged: persona prose re-entering a later prompt.**
  `foundation --ingest` merges model-authored `persona` text
  (foundation/ingest.py:71-74) which `authoring/contexts.py:373` later
  carries into work-order briefs, so one model pass writes context for the
  next. This is deliberate and documented, and the downstream deliverable is
  still gated by the deterministic ingest checks (placeholders, mentions,
  hard-case locations, literal-value rejection) plus the validators, so a
  steered author cannot forge a ledger fact. No actionable defect.
- **No secret, in tree or history.** Pattern scan across the last three
  commits touching each of the fifteen files is clean; none of them reads a
  credential or an environment variable. No email address, phone number, or
  real-person name appears in any of them.

### Accepted Risks

None.

---
*Prior review (2026-07-28, scope paths, commit 9927e03): re-review of the
three out-of-airlock BYO driver files (`drivers/config.py`,
`drivers/providers.py`, `drivers/forge_external.py`) over the delta since
`cf9ee69`. Confirmed the new `base_url` http(s) scheme allowlist is enforced
at the request sink and closes the prior standing NOTE, that keys are read
from the environment and never logged, and that subprocess use is fixed-argv
with model output validated before disk. 0 BLOCK / 0 WARN / 0 NOTE.*

<!-- SECURITY_META: {"date":"2026-08-02","commit":"6bd7d776091bd9f026581fae91633052b8f509ff","scope":"paths","scanned_files":["orgsmith/authoring/ingest.py","orgsmith/baselines.py","orgsmith/cli.py","orgsmith/datacard.py","orgsmith/docplan/planner.py","orgsmith/doctext.py","orgsmith/doctor.py","orgsmith/evals/emit.py","orgsmith/evals/score.py","orgsmith/foundation/ingest.py","orgsmith/paths.py","orgsmith/render/eml.py","orgsmith/schemas.py","orgsmith/validate/rules.py","tools/checksums.py"],"block":0,"warn":0,"note":1} -->
