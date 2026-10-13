"""Unit tier: engagements start on a business day when the recipe says so
(M17d, `business_calendar.engagement_starts`).

M17c found four of quillon-harbor's eight engagements commencing on a
non-working day, three weekends plus 2016-07-04, a holiday its own recipe
declares: the calendar governed meeting dates and never the engagement's
own start.
"""

from __future__ import annotations

import json
import shutil
from datetime import date

import pytest

from orgsmith.artifacts import load_engagements
from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.paths import OrgPaths
from orgsmith.validate import run_validate

from conftest import base_recipe_text, build_pure_stages

pytestmark = pytest.mark.unit

ANCHOR = "  format_mix: {docx: 15, pdf: 3, xlsx: 5}\n"


def _build(root, holidays, starts_on: bool) -> OrgPaths:
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    text = base_recipe_text()
    assert ANCHOR in text
    block = "  business_calendar:\n    holidays: [%s]\n" % ", ".join(holidays)
    if starts_on:
        block += "    engagement_starts: true\n"
    (dest / "ORG-CHARTER.md").write_text(text.replace(ANCHOR, ANCHOR + block))
    paths = OrgPaths(root=root, slug="dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(paths) == 0
    return paths


def _starts(paths):
    return {e.id: e.start for e in load_engagements(paths).engagements}


@pytest.fixture(scope="module")
def raw_starts(tmp_path_factory):
    """Where dev-mini's engagements start with no calendar shift."""
    return _starts(build_pure_stages(tmp_path_factory.mktemp("raw")))


def test_every_start_lands_on_a_business_day(tmp_path, raw_starts):
    # Declare every raw start a holiday, so the knob has to move all of them.
    holidays = sorted(d.isoformat() for d in raw_starts.values())
    paths = _build(tmp_path, holidays, starts_on=True)
    starts = _starts(paths)
    declared = {date.fromisoformat(h) for h in holidays}
    for eid, start in starts.items():
        assert start.weekday() < 5, f"{eid} starts on a weekend: {start}"
        assert start not in declared, f"{eid} starts on a declared holiday"
        assert abs((start - raw_starts[eid]).days) <= 7, "shifted to the nearest business day"
    # The `start` fact every letter cites moved with the engagement.
    for eng in load_engagements(paths).engagements:
        fact = next(f for f in eng.facts if f.id == f"f:{eng.id}.start")
        assert fact.value == eng.start.isoformat()


def test_the_knob_off_keeps_the_raw_starts(tmp_path, raw_starts):
    holidays = sorted(d.isoformat() for d in raw_starts.values())
    paths = _build(tmp_path, holidays, starts_on=False)
    assert _starts(paths) == raw_starts


def _cal01(paths, capsys):
    capsys.readouterr()
    run_validate(paths, as_json=True)
    report = json.loads(capsys.readouterr().out)
    return [f for f in report["findings"] if f["rule"] == "CAL-01"]


def _tamper_first_start_to_a_saturday(paths):
    ledger = json.loads(paths.engagements_json.read_text())
    eng = ledger["engagements"][0]
    start = date.fromisoformat(eng["start"])
    saturday = start.fromordinal(start.toordinal() + (5 - start.weekday()) % 7)
    eng["start"] = saturday.isoformat()
    paths.engagements_json.write_text(json.dumps(ledger, indent=2))
    return eng["id"]


def test_cal_01_catches_a_weekend_start_when_the_knob_is_on(tmp_path, capsys):
    paths = _build(tmp_path, [], starts_on=True)
    assert not _cal01(paths, capsys)
    eid = _tamper_first_start_to_a_saturday(paths)
    findings = _cal01(paths, capsys)
    assert any("engagement starts" in f["message"] and f["target"] == eid for f in findings)


def test_cal_01_ignores_engagement_starts_when_the_knob_is_off(tmp_path, capsys):
    paths = _build(tmp_path, [], starts_on=False)
    _tamper_first_start_to_a_saturday(paths)
    assert not [f for f in _cal01(paths, capsys) if "engagement starts" in f["message"]]
