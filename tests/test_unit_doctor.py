"""Unit tier: capability probe reflects this environment."""

import pytest

from orgsmith.doctor import probe, run_doctor
from orgsmith.effort import (
    AUTHORING_EFFORT_FLOOR,
    effort_report,
    meets_floor,
    session_effort,
)

pytestmark = pytest.mark.unit


def test_probe_finds_required_capabilities():
    results, ok = probe()
    assert ok, f"required capabilities missing: {results}"
    assert results["weasyprint"] == "ok"
    assert "soffice" in results  # recorded either way


# --- the authoring effort floor ---------------------------------------------


def test_floor_is_a_known_effort_level():
    from orgsmith.effort import EFFORT_ORDER

    assert AUTHORING_EFFORT_FLOOR in EFFORT_ORDER


@pytest.mark.parametrize(
    "effort,expected",
    [
        ("low", False),
        ("medium", False),
        ("high", True),
        ("xhigh", True),
        ("max", True),
    ],
)
def test_effort_is_ranked_against_the_floor(monkeypatch, effort, expected):
    monkeypatch.setenv("CLAUDE_EFFORT", effort)
    assert session_effort() == effort
    assert meets_floor(effort) is expected


@pytest.mark.parametrize("value", ["", "   ", "turbo", "HIGHEST"])
def test_unknown_or_absent_effort_is_unknown_not_below_floor(monkeypatch, value):
    """An unreported effort is a gap in what we can see, not evidence of a
    low setting. Treating it as a failure would train users to ignore the
    warning."""
    monkeypatch.setenv("CLAUDE_EFFORT", value)
    assert meets_floor(session_effort()) is None
    _, ok = effort_report()
    assert ok is True


def test_effort_is_case_and_whitespace_tolerant(monkeypatch):
    monkeypatch.setenv("CLAUDE_EFFORT", "  XHigh \n")
    assert session_effort() == "xhigh"
    assert meets_floor(session_effort()) is True


def test_effort_absent_from_environment_is_unknown(monkeypatch):
    monkeypatch.delenv("CLAUDE_EFFORT", raising=False)
    assert session_effort() is None
    line, ok = effort_report()
    assert ok is True
    assert "unreported" in line


def test_below_floor_warns_without_failing_the_run(monkeypatch, capsys):
    """The floor is advisory: authoring is still the user's call, and the
    exit code stays keyed to capabilities, not to effort."""
    monkeypatch.setenv("CLAUDE_EFFORT", "low")
    assert run_doctor() == 0
    out = capsys.readouterr().out
    assert "BELOW the authoring floor" in out
    assert "WARNING" in out


def test_doctor_reports_effort_before_any_authoring(monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_EFFORT", "xhigh")
    assert run_doctor() == 0
    assert "effort" in capsys.readouterr().out


def test_effort_is_never_recorded_in_probes(monkeypatch, tmp_path):
    """Probes describe what the machine can do. Re-probing a frozen fixture
    must not rewrite its state.json with the effort of whoever ran doctor;
    the authoritative record is the per-batch generator, set at ingest."""
    from conftest import build_pure_stages
    from orgsmith.state import load_state

    monkeypatch.setenv("CLAUDE_EFFORT", "low")
    paths = build_pure_stages(tmp_path / "probe")
    assert run_doctor(paths) == 0
    probes = load_state(paths).probes
    assert probes
    assert "effort" not in probes
    assert not any("low" == v for v in probes.values())
