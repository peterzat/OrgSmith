# Security

## Security Review — 2026-07-16 (scope: paths)

**Summary:** M9 document-supply scan: the genre registry, the registry-driven
planner, the date-scoped author work orders, the reworked PDF renderer (the two
engagement-letter rendering fixes), and the supporting fabric/foundation/schema
changes. No BLOCKs and no WARNs. One NOTE, the PDF letterhead, carries forward
unchanged from every prior review. The M9 delta introduces no reachable
vulnerability: the only untrusted input under the airlock doctrine is model
output, which in this scope reaches a sink only in `render/pdf.py`, where every
DocIR field is HTML-escaped; the new pure stages (registry-driven planner, email
cadence, per-hire supply, behavioral finance, era names) run before any model
pass and consume only the operator's recipe plus deterministic ledgers, and
every planned path passes the sound `check_relpath` guard.

### Findings

**[NOTE] orgsmith/render/pdf.py:38,65-66 — letterhead lines rendered unescaped
(carried unchanged from prior reviews; no concrete attack vector)**

  Attack vector: none concrete. `letterhead0` and `letterhead_rest` are
  `style.letterhead_lines`, built as `(charter.name, f"www.{charter.domain}")`
  (render/styles.py:43), and interpolated raw into the HTML template under
  `Environment(autoescape=False)` (pdf.py:74): into the `@top-left` CSS
  `content` string (pdf.py:38) and the two letterhead `<div>`s (pdf.py:65-66).
  Only the recipe author controls the charter name and domain, and
  `no_remote_fetcher` (pdf.py:19-27) refuses every non-`data:` URL, so injected
  markup can neither egress nor read local files. This is the same self-owned,
  operator-controlled surface all prior reviews rated NOTE.
  Evidence: pdf.py:38 is `@top-left { content: "{{ letterhead0 }}"; ... }` and
  pdf.py:65 is `<div class="name">{{ letterhead0 }}</div>`, both under
  `_ENV = Environment(autoescape=False)` (pdf.py:74). The M9 rework of this file
  (the `_para_html` newline handling, the `_duplicates_letterhead` /
  `_norm_firm` leading-heading drop, and `firm_name` threading) left the
  letterhead interpolation untouched; every model-authored DocIR field remains
  escaped (`html.escape` at pdf.py:129,131,133,138,141,153,159-161).
  Remediation: `html.escape()` the two `<div>` letterhead lines and CSS-escape
  the `@top-left` string when building the template context. One-line change,
  no urgency.

### Reviewed Surface

- The airlock boundary in scope: `render/pdf.py` is the only scoped file that
  consumes model output (DocIR blocks). Every field that reaches HTML is passed
  through `html.escape`: heading text (pdf.py:129), paragraph text via
  `_para_html` (pdf.py:104, which escapes BEFORE inserting `<br>` for
  intra-paragraph newlines, so the newline fix adds no injection), list items
  (pdf.py:133), table header/cells (pdf.py:138,141), the signature-page fee
  (pdf.py:153), and sigblock person name/title/date (pdf.py:159-161). Heading
  `level` is clamped 1..3 (pdf.py:128). The leading-heading drop compares
  model text to the firm name and at most removes a block; it is not a sink.
- Path construction is guarded and RNG/model-free. Every planner emit path
  (`_emit_engagement`, `_emit_email`, `_emit_fiscal_year`, `_emit_firm_periodic`,
  `_emit_hire`) is built from a registry filename template filled with recipe-
  and ledger-derived values, then passed to `_add` (planner.py:163-172), which
  runs `check_relpath` and raises `SystemExit` on any problem before the path is
  kept. `check_relpath` (naming.py:38-49) rejects `..` components, absolute/empty
  components, the forbidden set `<>:"/\|?*`, control characters, and over-length
  paths; verified sound. The registry filename templates are code constants, so
  the `.format()` calls carry no format-string injection (the untrusted side can
  only supply values, never the template). `service = eng.title.split(" for ")[0]`
  reaches the kickoff/email filename unsanitized but is recipe-author-controlled
  and still filtered by `check_relpath`; `_emit_hire` additionally runs the
  person name through `sanitize_component` first. The model never controls a
  path: paths are fixed by the pure planner before authoring, and DocIR is keyed
  by `doc_id`, not by path.
- Pure pre-model stages handle only operator input. `fabric/finance.py`,
  `fabric/engagements.py`, `foundation/scaffold.py`, `docplan/registry.py`, and
  the planner run on the charter plus deterministic ledgers, before any model
  pass, so they take no untrusted input. New M9 randomness draws from its own
  named `seeds.py` streams (`docplan.email.cadence` at planner.py:333,
  `foundation.names*` at scaffold.py, `fabric.finance.expenses`). None is a
  security sink.
- `authoring/contexts.py` builds outbound work orders only; it processes no
  inbound deliverable (that is `authoring/ingest.py`, out of scope). It does
  carry the model-authored `persona` into the next batch's briefs
  (contexts.py:231), a model-to-model flow inside the operator's own trust
  domain whose downstream output is itself schema- and placeholder-validated and
  gates nothing. Consistent with prior reviews, prompt-injection here is not a
  concrete finding.
- Error and log messages in scope echo only recipe/ledger-derived ids and paths
  (planner.py:166,169-171,290-294,518-521,599; scaffold.py:321-325,368-374),
  never a secret and never raw model-controlled terminal output. The "ingest
  printer" class the prior entry tracked lives in the ingest modules, none of
  which are in this scope.
- Secrets and PII: pattern grep over all ten scoped files is clean (the three
  hits are the word "token" in prose/comments). `git log` over the changed
  modules shows only M9 feature commits, no secret-shaped diffs. `era_names.py`
  is a bundled table of era-common US given names (representative flavor data,
  not identifiable individuals); `scaffold.py` draws surnames from Faker, emails
  from the synthetic domain, and phones from the reserved undialable 555-0100..99
  block; `conftest.py` uses scripted synthetic test doubles. No real PII.
- Crash-on-hostile-recipe paths exist (e.g. a `base_revenue` small enough to
  round the calibration year to zero would divide by zero in `finance.py`'s
  Travel line; absurd knob values raise `SystemExit`) but require the operator
  to author a hostile config against their own local run. No external actor, so
  not a security finding.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-16, scope paths, commit 37e061b): M7-close scan of the
quality instrument (`review/` package, the generator record, the effort floor).
One WARN, `review/report.py`'s provenance table interpolating the self-reported
`Generator.model`/`effort` into GENERATION-REPORT.md unescaped (display
deception in a committable artifact that gates nothing); two NOTEs, the
`foundation --ingest` printer echoing deliverable-controlled ids raw and this
same pdf letterhead. Those WARN/NOTE files (`review/report.py`,
`foundation/ingest.py`) are outside the current path scope and were not
re-verified this run.*

<!-- SECURITY_META: {"date":"2026-07-16","commit":"c013c0649e09efd892eddcd0c48d6a2afc7883b6","scope":"paths","scanned_files":["orgsmith/authoring/contexts.py","orgsmith/data/era_names.py","orgsmith/docplan/planner.py","orgsmith/docplan/registry.py","orgsmith/fabric/engagements.py","orgsmith/fabric/finance.py","orgsmith/foundation/scaffold.py","orgsmith/render/pdf.py","orgsmith/schemas.py","tests/conftest.py"],"block":0,"warn":0,"note":1} -->
