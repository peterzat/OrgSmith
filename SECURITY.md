# Security

## Security Review — 2026-07-15 (scope: paths)

**Summary:** M6-close scan of the pre-fleet hardening turn (range
449dcdf..5a59288): the new name-screen module and its three enforcement
points, the RNG-free affiliation planting pass and the AFF/NAME validator
families, era-resolved employer surfaces in render and authoring briefs,
the validator read hardening, and the two regenerated/new recipe charters.
The prior entry's two printer NOTEs are remediated for the escape-sequence
vector they described; one NOTE replaces them for the residual (the fix
keeps `\n`, so forged-line injection still reaches the terminal, verified
by probe at HEAD). The pdf letterhead NOTE carries forward unchanged. No
BLOCKs, no WARNs.

### Findings

**[NOTE — REMEDIATED 2026-07-15 in the same review cycle, commit 5a59288+]
orgsmith/naming.py:52-59, orgsmith/authoring/ingest.py:218,
orgsmith/evals/score.py:274,317 — the control-character fix preserves
newlines, so untrusted strings can still inject forged lines into failure
output**

  Remediation applied: the per-problem printer (ingest.py:218) and the
  per-failure printers (score.py:274,317) now pass `keep=""`, so an
  embedded newline can no longer forge a standalone line; the two
  schema-error paths (ingest.py:147, score.py:237) legitimately need
  newlines and stay on the default. The concurrent code review found and
  fixed a third, related path the scan did not reach: the graph class
  printer (score.py:341-353) echoed `--evals-dir` ambiguity tags entirely
  unsanitized, verified by probe (`ambiguity:<ESC>[2J<ESC>[31mPWNED`
  reached stdout raw); it is now wrapped with `keep=""` as well. Both
  probes re-run clean at the fix, and the retrieval probe now scores the
  injected answer as wrong (16/17) rather than printing a forged 17/17.
  The original finding text follows, unedited.

  Attack vector: `strip_control(text, keep="\n\t")` replaces category-Cc
  characters (ESC included) but deliberately keeps newline, and the
  untrusted strings these printers echo can carry newlines. The deception
  the remediated NOTE described (make the terminal show a passing result)
  therefore survives in a different encoding: line injection instead of
  cursor control. The true summary prints first in both tools, so padding
  the injected string with newlines scrolls it off-screen and leaves the
  forgery as the last thing on the operator's terminal.
  - `score --answers <file>`: grading a third-party extractor's output is
    the designed use (score.py:1-5), so the answers file is untrusted.
    Doc strings pass only `.strip()` (leading/trailing, score.py:73,132)
    and land in `missing`/`extra`/`docs_missing`/`docs_extra`, which the
    failure printers join and print.
  - `author --ingest <file>`: fact ids are extracted with charset `[^}]*`
    (ingest.py:31), which matches newline in Python, and land in the
    "unbriefed fact ids used" problem string; `DocIR.doc_id` is likewise
    an unconstrained str.
  Evidence: probes at HEAD. An answers file whose `docs` entry is
  `"Real Doc.docx\n\n\n\nretrieval: 17/17 (100.0%)"`, scored against
  `companies/dev-mini-metadata/evals`, prints the forged
  `retrieval: 17/17 (100.0%)` on its own line while the real score is
  0/17. A deliverable carrying
  `{{fact:x\n\n\ningest: merged 4 docs; 0 batchable docs remaining}}`
  prints that forged success line beneath the rejection listing.
  Impact is display-only and unchanged from the prior entry: exit codes
  stay 1 (ingest) and 0 (score, what a wrong answer earns), no DocIR is
  written, and skill automation keys off exit codes, so only a human
  reading the terminal can be misled. The schema-error paths
  (ingest.py:148-151, score.py:237-240) legitimately need newlines and are
  unaffected: pydantic escapes control characters inside its value reprs
  (re-verified at HEAD).
  Remediation: pass `keep=""` at the per-problem and per-failure printers,
  whose lines are single-line by construction; leave the two schema-error
  paths on the default. This closes the class rather than one encoding of
  it.

**[NOTE] orgsmith/render/pdf.py:37,64 — letterhead lines rendered
unescaped (residual from prior reviews; no current attack vector; file
unchanged in this range, verified by empty diff; outside this run's path
scope)**

  Attack vector: none concrete. The letterhead is `charter.name` and
  `www.{charter.domain}`, interpolated raw into the HTML template under
  `Environment(autoescape=False)` (pdf.py:73). Only the recipe author
  controls the charter, and `no_remote_fetcher` blocks all non-`data:`
  URLs, so injected markup cannot egress or read files.
  Remediation: `html.escape()` the letterhead lines (and CSS-escape the
  `@top-left` string) when building the template context. One-line
  change, no urgency.

### Reviewed Surface

- Name screen (new, `orgsmith/namescreen.py`): pure stdlib, offline, no
  network or subprocess. `load_firms` reads a package-relative constant
  (namescreen.py:19) and no caller passes a user-controlled path.
  Findings interpolate charter and foundation names through `!r`
  (namescreen.py:121,127,141-151), so the validator printer cannot be
  driven by them. Both generation gates fire before their artifact is
  written (charter.py:51-59, scaffold.py:336-344), each tested for the
  write-not-happening half. NAME-01 is a brand-collision screen, not a
  security boundary; its "screen, not a guarantee" limit is documented at
  namescreen.py:6-9 and real_firms.txt:12 and is the recipe author's risk
  to carry.
- `orgsmith/data/real_firms.txt`: ~220 public corporate brands, no
  contact details, no private individuals. The eponymous entries (Morgan
  Stanley, Edward Jones) are a deliberate, documented curation choice
  (real_firms.txt:9-11) and person matching is exact-equality
  (namescreen.py:100-102), so committed rosters do not over-fire. Not
  PII.
- Airlock intact and unchanged by this turn: `_brief_summary` still
  withholds fee and dates (contexts.py:112-120). The new
  `_brief_person(at=)` (contexts.py:123-137) and `people_index(at=)`
  (render/__init__.py:28-48) only re-resolve WHICH external employer name
  appears on a brief's dept line or a sigblock; the client name is
  already a `text` fact by design, and ingest's literal-value rejection
  deliberately covers money and date only (ingest.py:184-191) because the
  mention contract requires verbatim names. No new value leaks into a
  work order.
- Path safety: `docir_path` joins a deliverable-controlled `doc_id`
  (ingest.py:34-35), but ids absent from the work order force rejection
  before the write loop (ingest.py:161-163, 213-219), so writes stay
  inside work-order ids; `match_outstanding` still resolves the work
  order from state, never from the deliverable's id string. Re-verified,
  unchanged in this range.
- Validator read hardening (the SPEC criterion): SCAN-02's page-count
  read (rules.py:986-993) and LEG-01's `isOleFile`/`OleFileIO` reads
  (rules.py:1042-1064) now convert reader failures into findings instead
  of tracebacks. Both fail closed; a crafted artifact cannot pass
  silently.
- AFF-01/AFF-02 recompute the plan from charter plus foundation and catch
  `affiliation_plan`'s SystemExit into a finding rather than aborting the
  run (rules.py:766-774). Their inputs are repo-controlled ledgers: a
  tamperer already needs repository write access, so no privilege
  boundary is crossed. Both skip only on the charter knob
  (rules.py:753-757), per the M4 grandfathering lesson; NAME-01 has no
  grandfather.
- `charter.py` parses recipes with `yaml.safe_load` (charter.py:26); no
  arbitrary-object construction. Recipes are repo-controlled.
- Grep over all 29 scoped files finds no network, subprocess, `eval`,
  `exec`, `pickle`, or `yaml.load` sink; the LibreOffice call remains the
  package's only subprocess and is untouched in this range.
- `strip_control` neutralizes category Cc but not Cf, so bidi overrides
  (U+202E and kin) survive. Left as scoped, not a finding: they can
  reorder glyphs within a line but cannot erase or forge one, and
  terminal bidi support is rare enough that no concrete deception is
  demonstrable.
- Secrets and PII: pattern grep over all 29 scoped files plus
  `git log -p --follow` over the new files (namescreen.py,
  real_firms.txt, the fernhollow charter): clean. The only "token" hits
  are the words "model tokens" and "name tokens". Both charters are
  fictional firms with no personal names or contact details; fixture
  rosters remain Faker-synthetic. No scoped file handles credentials.
- Dependencies: requirements.txt, requirements-dev.txt and .github/ are
  unchanged in this range (verified by empty diff); pyproject.toml's only
  change is the version reconcile to 1.5.0, now pinned to
  `orgsmith.__version__` by a short-tier test (test_short.py:53-61).
  Pinning is still enforced for every requirement (test_short.py:42-50).
  Offline review, no live vulnerability database query.

### Accepted Risks

None recorded.

---
*Prior review (2026-07-15, scope paths, commit 449dcdf): M5-close scan of
the document-formats surface (pptx/eml/scan/legacy render, the LibreOffice
subprocess boundary, the new validator families parsing untrusted fixture
bytes, authoring contexts and ingest); no BLOCKs or WARNs, one new NOTE
(ingest rejection printer echoing deliverable-controlled strings raw to
the terminal) and two carried; it fulfilled the M5-opening entry's
deferred scan of the untrusted-parse surface.*

<!-- SECURITY_META: {"date":"2026-07-15","commit":"5a59288652af7aa4f6be6c286f63724c9b36361e","scope":"paths","scanned_files":["orgsmith/__init__.py","orgsmith/authoring/contexts.py","orgsmith/authoring/ingest.py","orgsmith/charter.py","orgsmith/data/real_firms.txt","orgsmith/docplan/planner.py","orgsmith/evals/score.py","orgsmith/fabric/engagements.py","orgsmith/fabric/graph.py","orgsmith/foundation/scaffold.py","orgsmith/namescreen.py","orgsmith/naming.py","orgsmith/render/__init__.py","orgsmith/schemas.py","orgsmith/validate/rules.py","pyproject.toml","recipes/dev-mini/ORG-CHARTER.md","recipes/fernhollow-partners/ORG-CHARTER.md","tests/conftest.py","tests/test_org_fleet.py","tests/test_short.py","tests/test_unit_affiliation_docs.py","tests/test_unit_airlock.py","tests/test_unit_compat.py","tests/test_unit_evals.py","tests/test_unit_legacy.py","tests/test_unit_namescreen.py","tests/test_unit_scan_validate.py","tests/test_unit_validate_graph.py"],"block":0,"warn":0,"note":2,"remediated":1} -->
