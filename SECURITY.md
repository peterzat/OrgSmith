# Security

## Security Review — 2026-07-15 (scope: changes-only)

**Summary:** The only uncommitted change is SECURITY.md itself, the
not-yet-committed report from the 2026-07-14 audit of the M3 delta
(`9d60f44..1830a11`); no code, config, dependency, or fixture changes are
pending and nothing is staged or untracked. This review verified that
report before it enters the record: its load-bearing code citations were
re-read at HEAD and all hold, and the diff contains no secrets, no real
PII, and no reproduced secret values. No new findings. The two open NOTEs
from the prior entry were re-verified as still present at HEAD and carry
forward below.

### Findings

**[NOTE] orgsmith/evals/score.py:278 — untrusted answers-file strings
printed raw to the terminal in score failure output (carried forward from
2026-07-14; re-verified at HEAD)**

  Attack vector: The designed use of `score --answers <file>` is grading a
  third-party extractor's output, so the answers file is untrusted input.
  A malicious file embeds ANSI escape sequences in a `docs` entry that does
  not match `expected_docs`; it lands in `docs_extra` and is printed
  unsanitized in the human-readable failure report (score.py:276-279),
  letting the file manipulate the grader's terminal display, for example
  repainting the score line to show a passing result. The same class
  applies to unconstrained `id` fields from a third-party `--evals-dir`
  (score.py:281) and to the pre-existing retrieval printer
  (score.py:236-240, `extra` from the answers file).
  Evidence: `", ".join(failure["docs_extra"])` printed without escaping
  (score.py:276-279). By contrast `got_value`/`expected_value` pass through
  `!r` (score.py:269-270) and JSON mode escapes control characters via
  `json.dumps` defaults, so only the raw joins in the human-readable branch
  are exposed. Impact is bounded to display manipulation in the operator's
  terminal; no code execution or file access.
  Remediation: strip control characters (or apply `!r`) to answers-file
  and evals-dir strings in the human-readable failure printer.

**[NOTE] orgsmith/render/pdf.py:37,64 — letterhead lines still rendered
unescaped (residual from prior reviews; no current attack vector;
re-verified at HEAD)**

  Attack vector: None concrete. The letterhead is `charter.name` and
  `www.{charter.domain}`, interpolated raw into the HTML template under
  `Environment(autoescape=False)` (pdf.py:73). Only the recipe author
  controls the charter, and `no_remote_fetcher` blocks all non-`data:`
  URLs, so injected markup cannot egress or read files. The signature-page
  injection is escaped (`esc(sig_fact_text)`, pdf.py:110-111) and does not
  widen this surface.
  Remediation: `html.escape()` the letterhead lines (and CSS-escape the
  `@top-left` string) when building the template context. One-line change,
  no urgency.

### Reviewed Surface (this delta)

- Pending diff is SECURITY.md only (75 insertions, 68 deletions): the
  2026-07-14 review entry replacing the 9d60f44-era entry. Read in full.
  No credential patterns, no real names, emails, or phone numbers; the
  only identifiers are fictional fixture domains, and no secret values
  are reproduced in finding text.
- Spot-verified the report's code citations against HEAD `1830a11`:
  sig_fact validated against the engagement ledger before render
  (render/__init__.py:88-92); sigfee text HTML-escaped (pdf.py:110-111)
  while letterhead remains raw under `autoescape=False` (pdf.py:37,64,73);
  score failure printers raw-join answers-file strings (score.py:236-240,
  276-283) while values use `!r`; `surface_in_text` regex built with
  `re.escape` and standalone-token lookarounds (schemas.py:413); ingest
  rejects non-body facts in prose as placeholder, literal, or long-form
  date (authoring/ingest.py:90-126). All claims hold.
- No staged changes, no untracked files, no CI/workflow or dependency
  manifest changes in scope.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-14, scope changes-only, commit 1830a11): M3 delta
`9d60f44..1830a11` (hard-case planting, location policies, extraction
evals, quillbrook fixture); no new vulnerabilities; signature-page
injection HTML-escaped, ingest validation of model output tightened,
mention matching regex-escaped, fixture identities synthetic, secret scans
over the range clean; two NOTEs (score-printer terminal hygiene, unescaped
letterhead), both still open and carried forward above.*

<!-- SECURITY_META: {"date":"2026-07-15","commit":"1830a112d82a7ff1f9caffd07e57a6a9b9883e10","scope":"changes-only","block":0,"warn":0,"note":2} -->
