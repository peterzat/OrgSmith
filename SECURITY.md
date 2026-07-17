# Security

## Security Review — 2026-07-17 (scope: paths)

**Summary:** M11b scan of the turn's changed surface: ~850 newly committed
model-generated fixture files across five new synthetic orgs
(brackenridge-civil, saltmarsh-environmental, hollowell-ip, northgate-staffing,
verdant-health), the eight changed test modules, and two skill files. No
product code changed. No BLOCK, no WARN, no NOTE. The fixture corpus is the
whole point of this pass: it publishes wholesale to a public GitHub repo, so
it was scanned as untrusted output rather than trusted input. **The two screens
the fixtures depend on were verified by execution, not by reading:** NAME-01
and PROV-01 were run in isolation against each new org and each reports
`2 rules run, 0 skipped, 0 errors`.

### Findings

No security issues identified in the reviewed scope.

### Reviewed Surface

- **NAME-01 and PROV-01 held, confirmed affirmatively rather than by absence
  from a skip list.** Both are `ERROR` rules carrying no `available=` gate
  (rules.py:1097, rules.py:1141), so neither can grandfather itself off. Run in
  isolation per org (`validate <slug> --only NAME-01,PROV-01`), all five report
  `2 rules run, 0 skipped, 0 errors`; the full validator reports 0 errors for
  each, and the rules absent from every SKIP line are exactly the ones that
  matter here. Their coverage was read rather than assumed, because "the rule
  passed" is only worth what the rule reads. NAME-01 (`name_01`,
  rules.py:307-314) screens the charter name and domain plus, via
  `screen_foundation`, external orgs and **all** people, internal and external
  (namescreen.py:145). I initially suspected a real gap here — engagement
  client names looked like they might live outside the screen — and refuted it:
  clients resolve from `foundation.external_orgs`, which is screened. Screening
  all 48 org/client display names against `real_firms.txt` independently
  (exact, token-subset, and domain-key matching) returns no collision, so the
  screen is not merely passing, it is passing on names that genuinely do not
  collide. PROV-01 dispatches a marker checker per format and yields a finding
  for any format whose checker is unknown (rules.py:1085-1090), so no format
  can silently pass; MAN-01 (manifest and share tree 1:1) also passed, which is
  what makes marker coverage total across the rendered tree rather than
  merely broad.
- **No secrets in the new fixtures.** All 535 newly added files were decoded to
  text in their native formats (OOXML parts unzipped, OLE streams read via
  olefile, PDFs via pypdf, .eml/.json/.jsonl/.md read directly) and scanned for
  AWS/Anthropic/OpenAI/GitHub/Slack/Google/Stripe keys, JWTs, private-key
  blocks, bearer tokens, `password|api_key|secret|token=` assignments,
  connection strings, SSNs, and credit-card numbers: **zero hits**. A
  `git log -p` sweep over `38d79aa..HEAD` for `companies/`, `tests/`, and
  `.claude/` is likewise clean, so nothing secret-shaped was committed and
  later removed.
- **No real PII.** Every email domain in the corpus maps to a synthetic org or
  one of its synthetic clients (`hollowellpatent.com`, `northgatetalent.com`,
  `esparzalamb.com`, ...); no real-world domain appears. Every phone number
  falls in the reserved fictional 555-01xx block (312/303/206/212/415/617
  area codes). Every URL in the corpus is an inert XML namespace declaration
  (openxmlformats.org, purl.org Dublin Core, w3.org) emitted by python-docx /
  python-pptx, not a live reference. One email-shaped string (`lk2ig.hf`) was
  chased down and proved to be an artifact of my own scanner concatenating
  utf16 and latin1 decodes of the same OLE bytes; it exists in no file and
  does not reproduce.
- **Nothing in the committed binaries can execute.** The 28 OLE containers
  (.doc/.xls/.ppt) hold only standard streams — `WordDocument`, `Workbook`,
  `PowerPoint Document`, `1Table`, `Pictures`, `SummaryInformation`,
  `CompObj`, `Ole`, `Current User` — with **no** `Macros`, `_VBA_PROJECT`,
  `ObjectPool`, or `Ole10Native` storage. The 114 OOXML zips contain no
  `vbaProject.bin` / `vbaData.xml` / macrosheet part, no `TargetMode="External"`
  relationship, and no `ddeLink`/`DDEAUTO`/`attachedTemplate`/`oleObject` in any
  XML part. All 25 PDFs were parsed structurally rather than byte-grepped:
  every catalog contains only `/Pages`, `/Type` (and `/Outlines`), with no
  `/OpenAction`, `/AA`, `/Names`, `/JavaScript`, `/AcroForm`, `/EmbeddedFiles`,
  `/Launch`, or `/RichMedia`, and no page-level `/AA` or `/Annots`. Two byte
  scans fired and both were my own false positives, recorded because the next
  reviewer will hit them too: `/JS` and `/AA` appear inside Flate-compressed
  content streams (verified by dumping the surrounding bytes), and `/ObjStm` is
  benign compressed-object storage that never belonged in a danger list. The 8
  .eml files are single-part `text/plain` with no attachments and no `Received`
  headers, so they carry no routing data or IPs. All 767 files under
  `companies/` are mode `100644`; nothing is executable.
- **A `<!DOCTYPE` hit in three .pptx files is inert.** It is an Apple plist DTD
  reference (`http://www.apple.com/DTDs/PropertyList-1.0.dtd`) embedded inside
  `ppt/printerSettings/printerSettings1.bin`, an opaque print-ticket blob that
  no XML part references and that no consumer parses as XML; no XML part in any
  fixture contains `<!DOCTYPE`, `<!ENTITY`, or `SYSTEM`. So it is not an XXE
  vector. It was worth chasing anyway, because a print-settings blob is exactly
  where generation-box identity would leak: it was searched for host, user,
  path, and printer-queue strings and carries none.
- **The rendering toolchain leaks no generation-box identity.** Every OOXML
  `dc:creator` and `cp:lastModifiedBy` across the 114 documents is a roster
  persona (`Tammy Parks`, `James Weiss`, ...), and every `Company` is one of the
  synthetic orgs. No `peter`, `zatloukal`, `/home/` path, or hostname appears
  anywhere in document metadata. `Application: Microsoft Macintosh Word` is
  python-docx's template default, and `dc:description: generated by python-docx`
  is left intact, so the toolchain is disclosed rather than disguised.
- **No model-facing text or unrendered facts escaped into the rendered tree.**
  All 175 newly added rendered files were scanned for leftover
  `{{fact:...}}` placeholders and for model/vendor names: **zero hits**. The 751
  `{{fact:` occurrences and all `claude` strings live exclusively under
  `*-metadata/` (`docir/*.json`, `state.json`, `GENERATION-REPORT.md`,
  `reply-*.json`), which is the documented architecture — the model writes
  placeholders, render substitutes them, and the generator stamp is a
  provenance record. This is the airlock's fact-discipline holding at the
  output boundary, checked at the boundary rather than inferred from FACT-01
  passing. The corpus is also free of injection-shaped text ("ignore previous
  instructions", "system prompt", role tags, "as an AI language model"), which
  matters because these fixtures are published for downstream RAG and indexing
  and would otherwise be an injection vector against their consumers.
- **The changed tests introduce no unsafe file handling and weaken no screen.**
  No `tarfile`/`zipfile`/`shutil.unpack_archive` extraction exists in any of the
  eight modules, so there is no zip-slip surface; no `subprocess`, `eval`,
  `exec`, `pickle`, `yaml.load`, `os.system`, or XML parser appears; no network
  or model client is imported, so the airlock holds in test. All writes land
  under `tmp_path`. The one path built from fixture data
  (`test_unit_legacy.py:263`, `(paths.share_dir / entry.path)`) reads a
  repo-controlled manifest into a `tmp_path` copytree and is unchanged in shape.
  The diff moves in the safe direction: `test_org_regen.py:127` widens `PINNED`
  to all seven committed orgs and shrinks `_COHERENCE_EXEMPT` to `{dev-mini}`,
  and `test_org_fleet.py:110` **removes** a skip-if-metadata-absent guard in
  favour of asserting the charter knob — closing a grandfather-by-absence hole
  exactly as CLAUDE.md's "skip visibly only when the knob is off" rule requires.
  The three deleted `test_unit_compat.py` cases lost their subject (their orgs
  are gone from `companies/` and `recipes/`); the deletion is forced, not
  elective.
- **The two skill diffs change no trust boundary.** `forge-review/SKILL.md` is a
  slug rename inside a description. `forge/SKILL.md:94-109` adds a scratch-file
  namespacing instruction for concurrent workers; it grants no new capability
  and its "never trust a scratch file you did not just write" guidance is
  hygiene in the right direction. Skills are operator-authored and in-repo, the
  established trust domain.
- **Not re-verified, and named rather than implied:** the M9 `render/pdf.py`
  letterhead NOTE (recipe-author-controlled interpolation under
  `autoescape=False`) is against unchanged code outside this path scope and
  **carries forward open**. No product code under `orgsmith/` changed this turn,
  so the M11a airlock conclusions (`ingest.py`, `schemas.py`, `acl.py`,
  `charter.py`, `scaffold.py`) stand unre-examined by design. Dependency
  manifests are unchanged and out of scope. Sanity check: `bin/test` is green
  across all tiers (12 short, 356 unit, 72 org).

### Accepted Risks

None recorded.

---
*Prior review (2026-07-16, scope paths, commit 38d79aa): M11a scan of the ACL
overlay, the hardened inbound airlock, the guarded charter write, roster
growth, and five test modules; 0 BLOCK / 0 WARN / 0 NOTE. It closed the M10
`docir_path` traversal NOTE and verified the closure by execution against
traversal, absolute-path, NUL, and trailing-newline payloads at both the schema
and the sink. It carried forward the M9 `render/pdf.py` letterhead NOTE, which
remains open against unchanged out-of-scope code.*

<!-- SECURITY_META: {"date":"2026-07-17","commit":"de60065c1c839fdd6c8895e1bc0642e3dc0ba338","scope":"paths","scanned_files":[".claude/skills/forge-review/SKILL.md",".claude/skills/forge/SKILL.md","companies/brackenridge-civil-metadata/**","companies/brackenridge-civil/**","companies/hollowell-ip-metadata/**","companies/hollowell-ip/**","companies/northgate-staffing-metadata/**","companies/northgate-staffing/**","companies/saltmarsh-environmental-metadata/**","companies/saltmarsh-environmental/**","companies/verdant-health-metadata/**","companies/verdant-health/**","tests/test_org_fleet.py","tests/test_org_regen.py","tests/test_unit_affiliation_docs.py","tests/test_unit_compat.py","tests/test_unit_evals.py","tests/test_unit_evals_formats.py","tests/test_unit_legacy.py","tests/test_unit_resume.py"],"block":0,"warn":0,"note":0} -->
