# Security

## Security Review — 2026-07-14 (scope: full)

**Summary:** Full audit of the OrgSmith package, skills, tests, and project
config. No secrets, injection, or auth issues. One defense-in-depth WARN:
manifest paths are trusted (not re-validated) when consumed by the pipeline,
so an untrusted/tampered org can direct a file write outside the share.

### Findings

**[WARN] orgsmith/render/__init__.py:59 — manifest `path` joined to the filesystem without re-validating path safety; absolute paths also bypass the build-time check**

  Attack vector: The path-safety check (`check_relpath`) runs only once, at
  docplan build time (`orgsmith/docplan/planner.py:85`). Every downstream
  consumer that joins a manifest path to the filesystem trusts it forever
  after. `render` does `target = paths.share_dir / entry.path` then
  `target.parent.mkdir(parents=True, exist_ok=True)` and writes. Because
  `pathlib` resets on an absolute right-hand side, a manifest entry with
  `path` = `/home/<user>/.config/autostart/x.docx` (or a `..`-traversal path,
  which is likewise never re-checked at consumption time) causes render to
  create/overwrite a file at that arbitrary location. `check_relpath` does not
  even reject absolute paths at build time: `"/etc/x".split("/")` yields an
  empty leading component that passes every rule (verified). The project
  README actively promotes sharing generated orgs ("shareable, regenerable");
  a user who obtains a third-party org and runs `python -m orgsmith render
  <slug>` on it gets an arbitrary-file-write primitive. The same untrusted
  manifest fed to `validate` turns `fact_01`/`file_01`/`fin_02`/`prov_01`
  (validate/rules.py) into a file-existence oracle (they `open()` the joined
  path and branch on missing-vs-unreadable).
  Not a BLOCK: the documented flow for consuming a shared org is `bin/test`
  (which runs only the read-only `validate`/`status` over the repo's own
  trusted fixtures) and `validate`, not `render`; within a single generation
  run paths are safe by construction (they come from templates and
  `sanitize_component`, never from the model deliverable or the network).
  Evidence: `render/__init__.py:59` (`paths.share_dir / entry.path` + mkdir +
  write); `naming.py:38-44` (`check_relpath` accepts absolute paths);
  `docplan/planner.py:85` (only call site of `check_relpath`);
  `validate/rules.py:157,185,206` (join + open of manifest path).
  Remediation: Re-validate on consumption. In `load_manifest`
  (`orgsmith/artifacts.py:49`) or at each join site, run `check_relpath` and
  additionally reject absolute paths and any `..` component; refuse to
  render/read entries that fail. Harden `check_relpath` itself to reject
  `os.path.isabs(relpath)` and empty components.

**[NOTE] orgsmith/render/pdf.py:118 — WeasyPrint's default URL fetcher is left enabled, a gap in the advertised "Python never touches the network" guarantee**

  Attack vector: `render_pdf` calls `HTML(string=doc_html).write_pdf(...)`
  with WeasyPrint's default fetcher, which resolves external `url()` / `<img>`
  / `@import` references (including `file:` and `http:`). Block content is
  HTML-escaped in `_blocks_to_html`, so a model deliverable cannot inject a
  resource reference; the only unescaped sink is the letterhead
  (`charter.name` / `charter.domain`, rendered raw at pdf.py:51-52), which is
  authored by the trusted recipe writer. Impact is therefore low, but the
  README and CLAUDE.md assert the package never touches the network as a
  load-bearing safety property, and this is the one bundled library that can
  egress.
  Evidence: `render/pdf.py:60` (`Environment(autoescape=False)`),
  `render/pdf.py:51-52` (unescaped `{{ letterhead0 }}`), `render/pdf.py:118`
  (`write_pdf` with default fetcher).
  Remediation: Pass a `url_fetcher` to `HTML(...)` that allows only `data:`
  URLs and raises on everything else, making the no-network guarantee
  enforced rather than incidental. Also HTML-escape the letterhead lines.

**[NOTE] .github/workflows/ci.yml:11-13 — third-party actions pinned to mutable major-version tags**

  Attack vector: `actions/checkout@v4` and `actions/setup-python@v5` are
  pinned to moving tags. A compromise of the tag would run attacker code in
  CI. These are first-party GitHub actions (low likelihood) and the workflow
  holds no secrets and uses no `pull_request_target`, so blast radius is
  small.
  Evidence: `.github/workflows/ci.yml:11,12`.
  Remediation: Pin actions to full commit SHAs for supply-chain
  defense-in-depth. Optional.

### Accepted Risks

None recorded.

---
*No prior review.*

<!-- SECURITY_META: {"date":"2026-07-14","commit":"b94d7f59a2cb6a95fea9bac10acecb9f7c285f7f","scope":"full","block":0,"warn":1,"note":2} -->
