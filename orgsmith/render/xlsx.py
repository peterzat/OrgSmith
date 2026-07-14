""".xlsx renderer: xlsxwriter with real formulas AND cached values.

Every formula is written via write_formula(..., value=<ledger number>) so
raw readers (no recalculation) see correct values and Excel recomputes to
the identical number. Formula vocabulary is restricted to SUM and cell
arithmetic so tests can re-evaluate every committed workbook.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell

from ..schemas import Charter, FinanceLedger, ManifestEntry
from .provenance import MARKER_NAME
from .styles import StylePack


def render_financial_summary(
    entry: ManifestEntry,
    charter: Charter,
    finance: FinanceLedger,
    style: StylePack,
    author_name: str,
    target: Path,
) -> None:
    year = int(entry.render_params["year"])
    fy = next(y for y in finance.years if y.year == year)

    target.parent.mkdir(parents=True, exist_ok=True)
    book = xlsxwriter.Workbook(str(target))
    book.set_properties(
        {
            "title": entry.title,
            "author": author_name,
            "company": charter.name,
            "created": datetime(entry.date.year, entry.date.month, entry.date.day,
                                9, 0, 0),
        }
    )
    book.set_custom_property(MARKER_NAME, "true")

    accent = f"#{style.accent_hex}"
    fmt_title = book.add_format({"bold": True, "font_size": 14,
                                 "font_color": accent})
    fmt_head = book.add_format({"bold": True, "bottom": 1})
    fmt_money = book.add_format({"num_format": "#,##0"})
    fmt_total = book.add_format({"num_format": "#,##0", "bold": True, "top": 1})

    sheet = book.add_worksheet("Summary")
    sheet.set_column(0, 0, 28)
    sheet.set_column(1, 5, 13)

    sheet.write(0, 0, f"{entry.title} — {charter.name}", fmt_title)

    # Revenue by quarter: row 2 header, row 3 values + SUM total.
    sheet.write_row(2, 0, ["Revenue", "Q1", "Q2", "Q3", "Q4", "FY Total"], fmt_head)
    sheet.write(3, 0, "Consulting revenue")
    for i, amount in enumerate(fy.quarters):
        sheet.write_number(3, 1 + i, amount, fmt_money)
    q_range = xl_range(3, 1, 3, 4)
    sheet.write_formula(3, 5, f"=SUM({q_range})", fmt_total, fy.revenue)

    # Expenses by category, annual.
    exp_head_row = 5
    sheet.write_row(exp_head_row, 0, ["Expenses (FY)", "", "", "", "", "Amount"],
                    fmt_head)
    row = exp_head_row + 1
    first_exp_row = row
    for category, amount in fy.expenses.items():
        sheet.write(row, 0, category)
        sheet.write_number(row, 5, amount, fmt_money)
        row += 1
    exp_range = xl_range(first_exp_row, 5, row - 1, 5)
    expenses_total = sum(fy.expenses.values())
    sheet.write(row, 0, "Total expenses")
    sheet.write_formula(row, 5, f"=SUM({exp_range})", fmt_total, expenses_total)

    # Net income = revenue total - expense total.
    net_row = row + 2
    rev_cell = xl_rowcol_to_cell(3, 5)
    exp_cell = xl_rowcol_to_cell(row, 5)
    sheet.write(net_row, 0, "Net income")
    sheet.write_formula(
        net_row, 5, f"={rev_cell}-{exp_cell}", fmt_total,
        fy.revenue - expenses_total,
    )
    book.close()
