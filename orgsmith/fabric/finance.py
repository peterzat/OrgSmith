"""Finance engine: all numbers computed in Python with explicit tie-outs.

Every derived series carries a check the validator re-verifies, so a
mistranscribed number anywhere downstream is caught against this ledger.
"""

from __future__ import annotations

from ..schemas import Charter, FinanceLedger, FiscalYear, LedgerCheck
from ..seeds import rng

_EXPENSE_CATEGORIES = [
    ("Compensation", 0.62),
    ("Office & Facilities", 0.14),
    ("Travel", 0.09),
    ("Professional Services", 0.08),
    ("Other", 0.07),
]


def _split_exact(total: int, weights: list[float]) -> list[int]:
    """Integer split of `total` by weight; remainder lands on the last part
    so the parts always sum exactly."""
    parts = [int(total * w) for w in weights[:-1]]
    parts.append(total - sum(parts))
    return parts


def build_finance(charter: Charter) -> FinanceLedger:
    rand = rng(charter.seed, "fabric.finance")
    end_year = charter.doc_culture.date_range[1].year

    years: list[FiscalYear] = []
    checks: list[LedgerCheck] = []
    revenue = float(charter.finance.base_revenue)
    for year in range(charter.founded, end_year + 1):
        if year == charter.founded:
            # Partial founding year: the firm ramps.
            year_revenue = int(round(revenue * 0.45, -3))
        else:
            year_revenue = int(round(revenue, -3))
            revenue *= 1.0 + charter.finance.growth_rate * rand.uniform(0.8, 1.2)

        q_weights = [rand.uniform(0.8, 1.2) for _ in range(4)]
        total_w = sum(q_weights)
        quarters = _split_exact(year_revenue, [w / total_w for w in q_weights])

        expense_total = int(round(year_revenue * charter.finance.expense_ratio))
        cat_names = [c for c, _ in _EXPENSE_CATEGORIES]
        cat_weights = [w for _, w in _EXPENSE_CATEGORIES]
        cat_values = _split_exact(expense_total, cat_weights)
        expenses = dict(zip(cat_names, cat_values))

        years.append(
            FiscalYear(
                year=year, revenue=year_revenue, quarters=quarters, expenses=expenses
            )
        )
        checks.append(
            LedgerCheck(
                name=f"FY{year}.quarters-tie-out",
                ok=sum(quarters) == year_revenue,
                detail=f"sum(quarters)={sum(quarters)} revenue={year_revenue}",
            )
        )
        checks.append(
            LedgerCheck(
                name=f"FY{year}.expense-tie-out",
                ok=sum(expenses.values()) == expense_total,
                detail=f"sum(expenses)={sum(expenses.values())} total={expense_total}",
            )
        )

    return FinanceLedger(slug=charter.slug, years=years, checks=checks)
