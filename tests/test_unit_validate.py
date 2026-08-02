"""Unit tier: the validator catches deliberate corruption."""

import shutil

import pytest

from orgsmith.assemble import run_assemble
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.validate import run_validate
from orgsmith.validate.rules import RULES

from conftest import build_pure_stages, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def org(tmp_path_factory):
    paths = build_pure_stages(tmp_path_factory.mktemp("valid-org"))
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


@pytest.fixture()
def org_copy(org, tmp_path):
    shutil.copytree(org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=org.slug)


def test_rule_catalog_v0():
    assert len(RULES) >= 6
    families = {r.id.split("-")[0] for r in RULES}
    assert {"ORG", "DATE", "FIN", "FACT", "FILE", "MAN", "PROV"} <= families


def test_pdf_layout_text_extracts_pdf_and_noops_elsewhere():
    """The FACT-01/MENT-01 layout-mode fallback: extracts real text for a pdf
    (rescuing pypdf's spurious intra-word spaces, e.g. 'Kirby-T aylor') and is a
    no-op ('') for non-pdf entries so the fallback never rescues those."""
    from conftest import REPO
    from orgsmith.validate.rules import Context

    ctx = Context.load(OrgPaths(root=REPO, slug="dev-mini"))
    pdf = next(e for e in ctx.manifest if e.format == "pdf")
    docx = next(e for e in ctx.manifest if e.format == "docx")
    assert ctx.pdf_layout_text(pdf).strip(), "layout mode extracted no text"
    assert ctx.pdf_layout_text(docx) == "", "layout fallback must no-op non-pdf"


def test_generated_org_validates_clean(org):
    assert run_validate(org) == 0


def test_deleted_rendered_file_fails(org_copy, capsys):
    manifest_doc = next(
        p for p in (org_copy.share_dir).rglob("*.docx")
    )
    manifest_doc.unlink()
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "FILE-01" in out and "MAN-01" in out


def test_changed_fact_value_fails_fact_echo(org_copy, capsys):
    ledger = org_copy.engagements_json
    text = ledger.read_text()
    # Bump the first engagement fee's surface form so no doc echoes it.
    import re

    match = re.search(r'"rendered": "\$([\d,]+)"', text)
    assert match
    corrupted = text.replace(match.group(0), '"rendered": "$999,999,999"', 1)
    ledger.write_text(corrupted)
    assert run_validate(org_copy) == 1
    assert "FACT-01" in capsys.readouterr().out


def test_stray_file_in_share_fails(org_copy, capsys):
    (org_copy.share_dir / "stray-note.txt").write_text("not planned")
    assert run_validate(org_copy) == 1
    assert "MAN-01" in capsys.readouterr().out


def test_broken_reporting_tree_fails(org_copy, capsys):
    foundation = org_copy.foundation_json
    text = foundation.read_text()
    corrupted = text.replace('"reports_to": null', '"reports_to": "p:ghost.person"', 1)
    assert corrupted != text
    foundation.write_text(corrupted)
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "ORG-01" in out or "ORG-02" in out


def test_only_filter_and_unknown_rule(org):
    assert run_validate(org, only=["ORG-01", "FIN-01"]) == 0
    with pytest.raises(SystemExit):
        run_validate(org, only=["NOPE-99"])


def test_findings_printer_neutralizes_a_smuggled_escape(org_copy, capsys):
    """SECURITY.md's carried NOTE, closed 2026-08-02.

    Validating an org tree obtained from someone else is a supported
    operation, and findings quote ledger strings pydantic does not constrain
    (`Person.reports_to` here). An ANSI escape smuggled through one used to
    reach the terminal raw, where it can rewrite or hide earlier findings.

    Sanitized at the PRINTER rather than at each interpolation site, so the
    rules that do not yet quote with `!r` are covered too, and so a rule
    added later cannot reintroduce it. `keep=""` drops the newline as well:
    otherwise a smuggled one forges a second finding line.
    """
    foundation = org_copy.foundation_json
    hostile = '"reports_to": "p:x\\u001b[2J\\u001b[31mPWNED\\nERROR FAKE-01 [x] forged"'
    text = foundation.read_text()
    corrupted = text.replace('"reports_to": null', hostile, 1)
    assert corrupted != text
    foundation.write_text(corrupted)

    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out

    assert "\x1b" not in out, "an escape sequence reached the terminal"
    assert "PWNED" in out, "content must survive; only the escape is dropped"
    # The smuggled newline forged no extra line: every printed finding line
    # starts with a severity or SKIP, and the summary is the last line.
    forged = [
        ln for ln in out.splitlines()
        if ln.startswith("ERROR FAKE-01")
    ]
    assert not forged, f"a smuggled newline forged a finding line: {forged}"


def test_findings_printer_survives_a_non_str_target(org, capsys, monkeypatch):
    """The printer must not raise on the finding it exists to report.

    Sanitizing replaced an f-string, which coerced anything; `strip_control`
    iterates its argument and so needs a `str`. Rules yield `str` targets
    today, but they build `share_dir / rel` paths constantly and one already
    wraps a target in an explicit `str(...)`, so yielding a `Path` or an `int`
    is a mistake with precedent. It must degrade to an ugly line, never to a
    traceback out of the validator's own reporting path.
    """
    import orgsmith.validate as v

    hostile = [
        {"rule": "FAKE-01", "severity": "ERROR",
         "message": "path target", "target": org.root / "companies"},
        {"rule": "FAKE-02", "severity": "ERROR",
         "message": "int target", "target": 42},
    ]
    monkeypatch.setattr(v, "collect", lambda ctx, selected=None: (hostile, []))

    assert v.run_validate(org) == 1  # printed, and the ERRORs still count
    out = capsys.readouterr().out
    assert "FAKE-01" in out and "FAKE-02" in out
    assert "[42]" in out


def test_findings_printer_neutralizes_a_bidi_override(org_copy, capsys):
    """Trojan Source (CVE-2021-42574) against the same printer.

    U+202E and the isolates are category Cf, not Cc, so the escape-only
    sanitizer passed them through and a hostile ledger string could reverse
    the remainder of the line it printed -- a tampered principal displaying
    as an untampered one. Same read-the-wrong-thing outcome the Cc pass
    exists to stop, so the sanitizer covers Cf too.
    """
    foundation = org_copy.foundation_json
    # RLO + isolates: rendered raw, these reorder the rest of the finding.
    hostile = '"reports_to": "p:x\\u202egnitcarahc\\u2066 \\u2069dedips"'
    text = foundation.read_text()
    corrupted = text.replace('"reports_to": null', hostile, 1)
    assert corrupted != text
    foundation.write_text(corrupted)

    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    for ch in ("‮", "⁦", "⁩"):
        assert ch not in out, f"a bidi format character reached the terminal: {ch!r}"
    assert "gnitcarahc" in out  # content survives, only the reordering dies


def test_strip_control_keeps_the_characters_callers_ask_to_keep():
    """Widening to Cf must not eat the whitespace `keep` exempts, which the
    report's `_cell` relies on (`keep="\\n"` before it folds newlines)."""
    from orgsmith.naming import strip_control

    assert strip_control("a\nb\tc") == "a\nb\tc"
    assert strip_control("a\nb", keep="") == "a�b"
    assert strip_control("a​b") == "a�b"


def test_json_output_is_not_mangled_by_the_printer_sanitizer(org_copy):
    """The sanitizer is on the human printer only. `--json` output is
    consumed by tooling and by several tests, so it must keep the ledger's
    bytes exactly; `json.dumps` already escapes control characters safely."""
    import json as _json

    foundation = org_copy.foundation_json
    text = foundation.read_text()
    foundation.write_text(
        text.replace('"reports_to": null', '"reports_to": "p:x\\u001b[2Jz"', 1)
    )
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_validate(org_copy, as_json=True)
    payload = _json.loads(buf.getvalue())  # parses => not corrupted
    assert any("\x1b" in f["message"] for f in payload["findings"]), (
        "json mode must preserve the raw ledger string for tooling"
    )
