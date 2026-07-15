# CODEREVIEW

## Review — 2026-07-15 (commit: 449dcdf)

**Summary:** Refresh review of the complete M5 turn, scope
origin/main..HEAD (14 commits since the prior review at 50eeefa; focus:
28 code/test/doc files plus two recipes and two generated fixtures).
Code surface: the four format capabilities end to end (pptx and eml
renderers with planner genres and airlock checks, deterministic scan
planning and the raster/OCR transform with archived truth, legacy
conversion through soffice with dual verification), four new
charter-gated validator rules (EML-01, SCAN-01/02, LEG-01) plus
explicit FILE-01/PROV-01 branches, eval difficulty tags with
byte-identical re-emission, version 1.4.0, and the gladepoint/
cindergrove fixtures. Tests green at HEAD (short 5 / unit 171 / org 18)
and in a fresh clone with a fresh venv. Every new rule is
corruption-tested in both directions; the retro fixture validates with
soffice masked from PATH.

**External reviewers:** None configured.

### Findings

[NOTE] orgsmith/validate/rules.py (scan_02, leg_01) — SCAN-02's
PdfReader page-count read and LEG-01's OleFileIO stream read are not
wrapped, so a crafted artifact that passes the wrapped opens but fails
these reads crashes the validate run with a traceback instead of a
findings list.
  Evidence: scan_02 calls PdfReader on the rendered pdf outside any
  try; leg_01 opens OleFileIO after isOleFile with no except.
  Consistent with the pre-existing FACT/LOC doc_text pattern; tampering
  still cannot pass silently (the run exits nonzero either way).
  Suggested fix: none required now; if validator ergonomics on hostile
  fixtures ever matter, wrap per-doc reads and yield reader failures as
  findings the way FILE-01 does.

[NOTE] orgsmith/render/scan.py (_pdf_escape) — the OCR layer encodes
text as cp1252 with errors="replace", so a planted fact or mention
surface containing a non-cp1252 character would be written with "?" and
only caught at validation (FACT-01/MENT-01 fail on the org), not at
render time.
  Evidence: _pdf_escape encodes at rebuild, after the protected-surface
  count check, which runs on pre-encoding Python strings.
  Suggested fix: none required for current recipes (Faker en_US rosters,
  ASCII fact surfaces); if non-Latin rosters land, assert protected
  surfaces are cp1252-encodable at render time.

Security (paths scan of the 24 changed code/test/recipe files, recorded
in SECURITY.md at commit 449dcdf): 0 BLOCK / 0 WARN / 3 NOTEs — one new
(ingest rejection printer echoes deliverable-controlled strings raw to
the terminal; display-only, exit codes unaffected) and two carried
(score.py failure printers, pdf letterhead autoescape). The soffice
subprocess boundary, manifest path safety, eml header injection
surface, OCR protected spans, and the airlock all verified clean.

### Fixes Applied

None.

### Accepted Risks

None.

---
*Prior review (2026-07-15, commit 50eeefa): refresh of the M5 opening
increments (format knobs, deps, docs); no issues found; 0 BLOCK /
0 WARN.*

<!-- REVIEW_META: {"date":"2026-07-15","commit":"449dcdf","reviewed_up_to":"449dcdf112e75b73fc63fecc5cccfe1dce9910fd","base":"origin/main","tier":"refresh","block":0,"warn":0,"note":2} -->
