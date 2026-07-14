"""Unit tier: capability probe reflects this environment."""

import pytest

from orgsmith.doctor import probe

pytestmark = pytest.mark.unit


def test_probe_finds_required_capabilities():
    results, ok = probe()
    assert ok, f"required capabilities missing: {results}"
    assert results["weasyprint"] == "ok"
    assert "soffice" in results  # recorded either way
