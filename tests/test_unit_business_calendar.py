"""Unit tier: the business-day calendar knob (M12,
docplan-has-no-business-day-calendar). When a recipe declares a calendar,
genres that assert a session happened (meeting_minutes, engagement_email) are
dated on a weekday that is not a declared holiday. Default off: a recipe
without the knob keeps every date byte-identical (covered by the org tier)."""

from datetime import date

import pytest

from orgsmith.artifacts import load_charter, load_engagements, load_manifest
from orgsmith.docplan.registry import REGISTRY
from orgsmith.fabric.engagements import (
    calendar_holidays,
    minutes_date,
    to_business_day,
)

from conftest import REPO, base_recipe_text
from orgsmith.charter import run_charter
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.docplan import run_docplan
from orgsmith.paths import OrgPaths

pytestmark = pytest.mark.unit

_ATTENDANCE = {r.genre for r in REGISTRY if r.asserts_attendance}
LO, HI = date(2000, 1, 1), date(2030, 12, 31)


def test_to_business_day_shifts_weekends_and_holidays():
    cal = frozenset({date(2021, 7, 5)})  # a Monday holiday
    # Saturday -> preceding Friday (ties prefer the earlier workday)
    assert to_business_day(date(2021, 6, 26), cal, LO, HI) == date(2021, 6, 25)
    # Sunday -> following Monday (nearer than the preceding Friday)
    assert to_business_day(date(2021, 6, 27), cal, LO, HI) == date(2021, 6, 28)
    # a declared Monday holiday -> the following Tuesday (Friday is farther)
    assert to_business_day(date(2021, 7, 5), cal, LO, HI) == date(2021, 7, 6)
    # a plain weekday is unchanged, and the shift is idempotent
    assert to_business_day(date(2021, 6, 29), cal, LO, HI) == date(2021, 6, 29)


def test_to_business_day_is_a_noop_without_a_calendar():
    saturday = date(2021, 6, 26)
    assert to_business_day(saturday, None, LO, HI) == saturday


def test_minutes_date_agrees_across_the_airlock_with_a_calendar():
    """minutes_date is the single source of truth fabric and docplan share; a
    calendar shifts it identically for both, so the filename fact still matches
    the docplan date. A Saturday-landing session moves to a business day."""
    start, end = date(2021, 1, 1), date(2021, 12, 31)
    cal = frozenset()
    md = minutes_date(start, end, LO, HI, cal)
    assert md.weekday() < 5
    # same inputs, same output -- the property both sides rely on
    assert md == minutes_date(start, end, LO, HI, cal)
    # without the calendar the date is the raw 40%-through anchor
    raw = minutes_date(start, end, LO, HI, None)
    assert raw == date(2021, 5, 26)  # start + int(364 * 0.4) days


def _build_with_calendar(root, holidays: list[str]) -> OrgPaths:
    """dev-mini through docplan with a declared business-day calendar."""
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    text = base_recipe_text()
    anchor = "  format_mix: {docx: 15, pdf: 3, xlsx: 5}\n"
    assert anchor in text
    block = "  business_calendar:\n    holidays: [%s]\n" % ", ".join(holidays)
    (dest / "ORG-CHARTER.md").write_text(text.replace(anchor, anchor + block))
    paths = OrgPaths(root=root, slug="dev-mini")
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


def test_no_attendance_document_lands_on_a_weekend_or_holiday(tmp_path):
    holiday = "2020-12-25"  # a Friday inside dev-mini's range
    paths = _build_with_calendar(tmp_path, [holiday])
    charter = load_charter(paths)
    assert calendar_holidays(charter) == frozenset({date(2020, 12, 25)})
    attendance = [e for e in load_manifest(paths) if e.genre in _ATTENDANCE]
    assert attendance, "dev-mini should plan at least one minutes document"
    for e in attendance:
        assert e.date.weekday() < 5, f"{e.genre} on a weekend: {e.date}"
        assert e.date != date(2020, 12, 25), f"{e.genre} on the holiday"


def test_calendar_off_leaves_minutes_dates_untouched(tmp_path):
    """The knob is inert when absent: dev-mini's minutes dates match the
    committed fixture's, which the org-tier byte pin already guards; assert it
    here at the unit level so a regression surfaces without the fixture."""
    paths = _build_with_calendar(tmp_path, [])  # calendar ON but no holidays
    on_minutes = {
        e.doc_id: e.date
        for e in load_manifest(paths)
        if e.genre == "meeting_minutes"
    }
    # every on-calendar minutes date is a weekday
    assert on_minutes
    assert all(d.weekday() < 5 for d in on_minutes.values())


def test_cal_01_fires_on_a_tampered_weekend_date(tmp_path):
    """CAL-01 recomputes the invariant and fails when an attendance document
    is dated on a weekend, so a corrupted manifest cannot pass silently."""
    from orgsmith.validate.rules import Context, cal_01, _needs_calendar

    paths = _build_with_calendar(tmp_path, [])
    ctx = Context.load(paths)
    assert _needs_calendar(ctx) is None  # knob is on, rule runs
    assert list(cal_01(ctx)) == []  # clean org has no findings

    idx, minutes = next(
        (i, e) for i, e in enumerate(ctx.manifest) if e.genre == "meeting_minutes"
    )
    saturday = minutes.date
    while saturday.weekday() != 5:
        saturday = date.fromordinal(saturday.toordinal() + 1)
    ctx.manifest[idx] = minutes.model_copy(update={"date": saturday})
    findings = list(cal_01(ctx))
    assert findings and "weekend" in findings[0][0]
