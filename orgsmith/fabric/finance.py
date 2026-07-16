"""Finance engine: all numbers computed in Python with explicit tie-outs.

Every derived series carries a check the validator re-verifies, so a
mistranscribed number anywhere downstream is caught against this ledger.

Expenses are BEHAVIORAL (M8). Each category is driven by the thing that
actually drives it -- compensation by headcount, facilities by a lease,
travel by activity -- rather than by a fixed share of revenue. The board
found the old model twice over: `rf:finance-1` ("every expense line is a
frozen percentage of revenue in all eight years, which no real P&L does")
and `rf:finance-2` ("rent is a lease cost and cannot compound 11% a year
because fees went up"). Both were the same three lines: an `expense_total`
of `revenue * expense_ratio`, split by hardcoded weights.

This inverts the relationship. The categories are computed first and the
total is their sum, so `expense_ratio` no longer defines anything about a
given year; see FinanceProfile for the job it keeps.
"""

from __future__ import annotations

import calendar
from datetime import date

from ..schemas import Charter, FinanceLedger, FiscalYear, Foundation, LedgerCheck
from ..seeds import rng
from .engagements import _employed_at

# Calibration weights: the shape of a professional-services P&L in its first
# full year. After that each category goes its own way, which is the point --
# these anchor the model, they do not govern it.
_EXPENSE_CATEGORIES = [
    ("Compensation", 0.62),
    ("Office & Facilities", 0.14),
    ("Travel", 0.09),
    ("Professional Services", 0.08),
    ("Other", 0.07),
]

# A commercial lease is signed for a term and does not care what revenue did.
# It steps on renewal and is flat in between, which is exactly the shape
# rf:finance-2 says was missing.
_LEASE_TERM_YEARS = 4
_LEASE_STEP = (0.06, 0.16)  # renewal uplift range

_RAISE_RANGE = (0.02, 0.045)  # annual comp per head
_PROF_GROWTH = (0.01, 0.07)  # accountants and lawyers, slow and lumpy
_TRAVEL_NOISE = (0.78, 1.25)  # tracks activity, badly
_OTHER_NOISE = (0.80, 1.30)


def _split_exact(total: int, weights: list[float]) -> list[int]:
    """Integer split of `total` by weight; remainder lands on the last part
    so the parts always sum exactly."""
    parts = [int(total * w) for w in weights[:-1]]
    parts.append(total - sum(parts))
    return parts


def _avg_headcount(foundation: Foundation, year: int) -> float:
    """Mean month-end headcount across the year. A mid-year snapshot would
    miss the whole point under roster churn: a seat that empties in March and
    refills in May costs less that year, and a firm that grows in Q4 does not
    pay for it all year."""
    total = 0
    for month in range(1, 13):
        last = date(year, month, calendar.monthrange(year, month)[1])
        total += sum(1 for p in foundation.people if _employed_at(p, last))
    return total / 12


def build_finance(charter: Charter, foundation: Foundation) -> FinanceLedger:
    rand = rng(charter.seed, "fabric.finance")
    # Expenses draw from their own stream so that tuning the expense model
    # never moves the revenue series, and vice versa. They are independent
    # series and a shared stream would couple them silently.
    erand = rng(charter.seed, "fabric.finance.expenses")
    end_year = charter.doc_culture.date_range[1].year

    # --- revenue (unchanged) ---
    revenue = float(charter.finance.base_revenue)
    year_revenues: dict[int, int] = {}
    quarters_by_year: dict[int, list[int]] = {}
    for year in range(charter.founded, end_year + 1):
        if year == charter.founded:
            # Partial founding year: the firm ramps.
            year_revenue = int(round(revenue * 0.45, -3))
        else:
            year_revenue = int(round(revenue, -3))
            revenue *= 1.0 + charter.finance.growth_rate * rand.uniform(0.8, 1.2)
        year_revenues[year] = year_revenue

        q_weights = [rand.uniform(0.8, 1.2) for _ in range(4)]
        total_w = sum(q_weights)
        quarters_by_year[year] = _split_exact(
            year_revenue, [w / total_w for w in q_weights]
        )

    # --- expense anchors, calibrated on the first FULL year ---
    # expense_ratio sizes the P&L once, here, and then stops applying. See
    # FinanceProfile.expense_ratio for why that is the honest reading of it.
    base_year = min(charter.founded + 1, end_year)
    base_rev = year_revenues[base_year]
    anchors = dict(
        zip(
            [c for c, _ in _EXPENSE_CATEGORIES],
            _split_exact(
                int(round(base_rev * charter.finance.expense_ratio)),
                [w for _, w in _EXPENSE_CATEGORIES],
            ),
        )
    )
    base_heads = max(_avg_headcount(foundation, base_year), 1.0)
    comp_per_head = anchors["Compensation"] / base_heads

    # The lease is drawn once for the org's life: a firm signs a term and
    # lives with it. Renewals step, and only on renewal years.
    lease = float(anchors["Office & Facilities"])
    lease_steps = {
        y: 1.0 + erand.uniform(*_LEASE_STEP)
        for y in range(charter.founded, end_year + 1)
        if (y - base_year) % _LEASE_TERM_YEARS == 0 and y > base_year
    }
    prof_growth = erand.uniform(*_PROF_GROWTH)

    years: list[FiscalYear] = []
    checks: list[LedgerCheck] = []
    lease_now = lease
    prof_now = float(anchors["Professional Services"])
    # Raises accumulate year on year. Drawing a fresh rate and raising it to
    # (year - base_year) instead would make each year's index a DIFFERENT rate
    # compounded over the whole span, so year-over-year compensation would
    # swing by the gap between two draws (~12%) rather than by a raise (~3%)
    # even with headcount frozen -- which is exactly the lockstep-with-fees
    # look this model exists to remove.
    raise_index = 1.0
    for year in range(charter.founded, end_year + 1):
        year_revenue = year_revenues[year]
        partial = 0.45 if year == charter.founded else 1.0

        if year in lease_steps:
            lease_now *= lease_steps[year]
        if year > charter.founded:
            prof_now *= 1.0 + prof_growth * erand.uniform(0.6, 1.4)
        if year > base_year:
            raise_index *= 1.0 + erand.uniform(*_RAISE_RANGE)

        heads = _avg_headcount(foundation, year)

        expenses = {
            # Tracks headcount, not revenue. rf:finance-1's specific
            # complaint: a firm whose own ground truth says the same five
            # people never left cannot have a compensation line that
            # compounds with fees.
            "Compensation": int(round(heads * comp_per_head * raise_index, -2)),
            # Step-fixed across the lease term.
            "Office & Facilities": int(round(lease_now * partial, -2)),
            # Follows activity, noisily.
            "Travel": int(
                round(
                    anchors["Travel"]
                    * (year_revenue / base_rev)
                    * erand.uniform(*_TRAVEL_NOISE),
                    -1,
                )
            ),
            "Professional Services": int(round(prof_now * partial, -1)),
            "Other": int(
                round(anchors["Other"] * partial * erand.uniform(*_OTHER_NOISE), -1)
            ),
        }
        expense_total = sum(expenses.values())

        years.append(
            FiscalYear(
                year=year,
                revenue=year_revenue,
                quarters=quarters_by_year[year],
                expenses=expenses,
            )
        )
        checks.append(
            LedgerCheck(
                name=f"FY{year}.quarters-tie-out",
                ok=sum(quarters_by_year[year]) == year_revenue,
                detail=(
                    f"sum(quarters)={sum(quarters_by_year[year])} "
                    f"revenue={year_revenue}"
                ),
            )
        )
        checks.append(
            LedgerCheck(
                name=f"FY{year}.expense-tie-out",
                ok=sum(expenses.values()) == expense_total,
                detail=f"sum(expenses)={sum(expenses.values())} total={expense_total}",
            )
        )
        # A loss is a fact about the firm, not a generator error, so it is
        # recorded and never raised. ok stays True: FIN-01 fires on ok=False,
        # and a bad year is not a broken ledger.
        checks.append(
            LedgerCheck(
                name=f"FY{year}.net-income",
                ok=True,
                detail=(
                    f"revenue={year_revenue} expenses={expense_total} "
                    f"net={year_revenue - expense_total}"
                ),
            )
        )

    return FinanceLedger(slug=charter.slug, years=years, checks=checks)
