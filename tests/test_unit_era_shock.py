"""Unit tier: a declared era shock reaches the finance ledger (M17d,
`finance.era_shocks`).

M17c's board found quillon-harbor's 2020 prose remarking that most of the
firm still worked from kitchen tables while its FY2020 workbook made Q2 the
year's largest quarter; the exemplar had the same flat 2020. The finance
model is a smooth curve, so an era has to be declared.
"""

from __future__ import annotations

import pytest

from orgsmith.artifacts import load_finance
from orgsmith.charter import parse_charter_md

from conftest import base_recipe_text, build_pure_stages

pytestmark = pytest.mark.unit

ANCHOR = "  expense_ratio:"
SHOCK = (
    "  era_shocks:\n"
    "    - year: 2020\n"
    "      revenue: 0.8\n"
    "      travel: 0.3\n"
    "      quarters: [1.0, 0.5, 0.8, 0.95]\n"
)


def _recipe(root, block=SHOCK):
    text = base_recipe_text()
    line = next(ln for ln in text.splitlines(keepends=True) if ln.startswith(ANCHOR))
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "ORG-CHARTER.md").write_text(text.replace(line, line + block, 1))
    return dest


@pytest.fixture(scope="module")
def plain(tmp_path_factory):
    return {y.year: y for y in load_finance(build_pure_stages(tmp_path_factory.mktemp("p"))).years}


@pytest.fixture(scope="module")
def shocked(tmp_path_factory):
    root = tmp_path_factory.mktemp("s")
    _recipe(root)
    paths = build_pure_stages(root)
    return paths, {y.year: y for y in load_finance(paths).years}


def test_the_shock_year_is_scaled_and_every_other_year_is_untouched(plain, shocked):
    _, years = shocked
    assert set(years) == set(plain)
    for year in plain:
        if year == 2020:
            continue
        assert years[year].model_dump() == plain[year].model_dump(), year
    assert years[2020].revenue == int(round(plain[2020].revenue * 0.8, -3))
    # The year after is back on trend: identical to the unshocked ledger.
    assert years[2021].revenue == plain[2021].revenue


def test_the_quarter_shape_and_travel_follow_the_shock(plain, shocked):
    _, years = shocked
    q = years[2020].quarters
    assert sum(q) == years[2020].revenue
    assert q[1] == min(q), "the declared spring dip is the year's smallest quarter"
    assert years[2020].expenses["Travel"] < plain[2020].expenses["Travel"] * 0.5


def test_the_shocked_ledger_still_ties_out(shocked):
    paths, _ = shocked
    finance = load_finance(paths)
    assert all(c.ok for c in finance.checks)


def test_a_shock_outside_the_firms_years_fails_loudly(tmp_path):
    _recipe(tmp_path, SHOCK.replace("2020", "1850"))
    with pytest.raises(SystemExit, match="outside the firm's fiscal years"):
        build_pure_stages(tmp_path)


def test_a_year_declared_twice_is_rejected_at_parse(tmp_path):
    dest = _recipe(tmp_path, SHOCK + SHOCK.replace("  era_shocks:\n", ""))
    with pytest.raises(Exception, match="same year twice"):
        parse_charter_md((dest / "ORG-CHARTER.md").read_text(), "dev-mini")


def test_a_shock_on_the_expense_base_year_leaves_every_other_year_untouched(
    plain, tmp_path
):
    # dev-mini is founded 2018, so 2019 is the first full year, the one the
    # expense anchors calibrate on. The shock must not resize later years.
    _recipe(tmp_path, SHOCK.replace("2020", "2019").replace("0.8\n", "0.6\n", 1))
    years = {y.year: y for y in load_finance(build_pure_stages(tmp_path)).years}
    for year in plain:
        if year == 2019:
            continue
        assert years[year].model_dump() == plain[year].model_dump(), year
    assert years[2019].revenue == int(round(plain[2019].revenue * 0.6, -3))
    assert years[2019].expenses["Compensation"] == plain[2019].expenses["Compensation"]
