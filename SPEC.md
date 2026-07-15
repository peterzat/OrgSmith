# SPEC

## Spec — 2026-07-15 — M5: document formats (pptx, eml, scanned, legacy)

**Goal:** Make generated corpora stop looking uniformly clean and modern.
Four recipe-dialable format capabilities land: presentation decks (.pptx),
mail messages (.eml), scanned-and-degraded pdfs with synthetic OCR text
layers, and pre-2007 legacy office binaries (.doc/.xls/.ppt) converted via
LibreOffice at generation time only. Each follows the milestone rhythm:
knob, deterministic derivation, validator enforcement, eval integration,
committed fixture.

### Acceptance Criteria

- [x] Recipe knobs land additively: `format_mix` gains `pptx` and `eml`
  counts, `doc_culture` gains `scanned_ratio`, `legacy_ratio`, and
  `ocr_layer_rate` (0..1; `ocr_layer_rate > 0` with `scanned_ratio == 0`
  is a charter error, tested), all documented in docs/RECIPE-FORMAT.md and
  defaulting to off: the four committed fixtures load and validate clean
  without regeneration, and unchanged recipes regenerate byte-identical
  structure (determinism and org tiers stay green).
- [ ] .pptx end to end: a deck genre is planned per engagement when
  `format_mix.pptx > 0` (demanding more decks than engagements exist fails
  at docplan with an actionable message), authored through the airlock,
  and the rendered .pptx opens in python-pptx, carries the synthetic
  provenance marker, and echoes its planted facts and planned mentions in
  extractable text (fact/mention rules cover pptx; corruption-tested).
- [ ] .eml end to end: an email genre is planned when `format_mix.eml > 0`;
  the rendered .eml parses with the stdlib email module, carries a
  synthetic marker header, renders byte-identically on re-render, echoes
  planted facts and mentions in its body, and a validator rule fails when
  From/To/Date/Subject/Message-ID do not recompute exactly from ledger
  data (corruption-tested).
- [ ] Scan planning is deterministic: with `scanned_ratio` on, docplan
  marks the oldest pdf docs as scanned and assigns OCR layers per
  `ocr_layer_rate` from a new seed stream; planning twice from the same
  recipe yields identical flags; scanned docs keep their .pdf paths; a doc
  hosting a signature_page fact is never image-only (all tested).
- [ ] Scan rendering holds: a scanned doc's pages are raster images;
  degradation is seeded and reproducible per doc; an OCR-layer doc exposes
  extractable text in which every planted fact and mention surface appears
  verbatim while at least one synthetic OCR corruption exists outside
  those protected spans; an image-only doc exposes no extractable text;
  the true per-page text is archived under the org's metadata; the
  provenance marker survives the rebuild (all tested).
- [ ] Scan validation never goes silent: validator rules verify scanned
  docs are image pdfs whose OCR-layer presence matches the plan, and that
  text obligations for image-only docs hold against the archived page
  text; each rule fails a deliberately corrupted copy in both directions;
  the rules skip visibly only when the charter's scan knobs are off, and
  fail when knobs are on but scan artifacts are missing.
- [ ] Legacy end to end: with `legacy_ratio` on, docplan deterministically
  assigns legacy formats and extensions (oldest office docs first); render
  converts verified modern intermediates via LibreOffice and exits with an
  actionable message when soffice is absent; every rendered legacy file
  opens via pure-Python OLE reading with the expected container type and
  carries a verifiable synthetic-provenance marker (validator rules,
  corruption-tested); .xls financial summaries still tie to the finance
  ledger, or financial summaries are excluded from legacy selection with
  the exclusion documented.
- [ ] Validation is CI-safe: `orgsmith validate` on an org containing all
  new formats passes with soffice masked from PATH (tested), and
  FILE-01/PROV-01 have explicit branches for every supported format so an
  unknown format produces a finding or loud error, never a silent pass or
  a crash (tested).
- [ ] Evals ride along: retrieval, extraction, and visibility suites emit
  and score over orgs containing the new formats; extraction questions
  carry `scan:ocr`, `scan:image-only`, and `format:legacy` tags when their
  expected docs have those properties; all four committed pre-M5 fixtures
  re-emit their evals byte-identically (tested).
- [ ] A modern fixture is committed: an org whose mix includes pptx and
  eml documents, generated through the airlock; it validates clean, its
  extraction ground truth scores 100%, and the org tier covers it.
- [ ] A retro fixture is committed: an org founded around 1995 with docs
  1998-2004, scan and legacy knobs on, containing at least one image-only
  scan, one OCR-layer scan, one .doc, one .xls, and one .ppt; it validates
  clean with soffice absent, and its extraction ground truth scores 100%.
- [ ] From a fresh checkout, `bin/test` passes all tiers offline with all
  committed fixtures (CI configuration unchanged: no LibreOffice).

### Context

- Adopted from `~/.claude/plans/we-want-the-next-parsed-scroll.md`; read it
  for the full design (selection rules, renderer sketches, marker
  strategy, increment order, risks). Key constraints:
- Trust boundary: soffice is generation-only. All validation-time reading
  is pure Python (python-pptx, stdlib email, olefile, xlrd, pypdf).
  New pinned deps: python-pptx, pypdfium2, Pillow, numpy, olefile, xlrd.
  The generation box needs `libreoffice-writer/-calc/-impress` installed
  (user action, in progress); `doctor` must show `soffice ok` before the
  legacy increments and the retro fixture.
- The OCR layer is synthetic and deterministic: we own the text layer, and
  corruptions (l/1, O/0, rn/m) may only touch prose outside planted fact
  and mention surfaces, which is what keeps FACT/MENT/LOC rules honest on
  scanned docs. No tesseract anywhere.
- Spike early (before building the scan pipeline out): confirm pypdf can
  extract the invisible text layer verbatim; fallbacks are in the plan.
- M4's grandfathering lesson binds all new rules: skip only when the
  CHARTER says the feature is off; fail when knobs are on but artifacts
  are missing or stripped.
- Additive discipline: no schema-id bumps; new fields default off; scan
  and OCR selection draw only from NEW seed streams so unchanged recipes
  regenerate byte-identically. Rendered binaries (including soffice
  output and JPEG degradation) are not byte-stable across environments
  and never were; the byte-identity contract covers pure stages only.
- Era naming (`naming_style`, `it_maturity`) stays reserved for the fleet
  turn: the retro org keeps modern Faker names, documented as a known
  anachronism.
- Both fixture names must not resemble real firms (the name-screen
  validator remains deferred in BACKLOG; apply the informal screen).
- Fixture authoring runs through /forge with forked workers; the turn is
  the largest yet (~2x M4) and both forge and this spec are resumable
  across sessions. House practices: small committable increments with
  tests in the same increment; no push or remote mutation without
  explicit user instruction.

---
*Prior spec (2026-07-15): M4 ACL overlay and visibility evals; all 8
criteria met, shipped as v1.3.0.*

<!-- SPEC_META: {"date":"2026-07-15","title":"M5: document formats (pptx, eml, scanned, legacy)","criteria_total":12,"criteria_met":1} -->
