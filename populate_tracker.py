"""
Populate (or refresh) the Obligations and Actions tabs of AuditTracker.xlsx
with the canonical content from tracker_data.py, following Tracker Guide v2.

What it does:
  - Adds an "Obligation Level" column (Enduring / Periodic / Monitoring, Part 1)
    to the Obligations sheet if it is not already there, with a dropdown.
  - Replaces the rows in Obligations with the full OB-A1..A12 + OB-L1..L7 set.
  - Replaces the rows in Actions with A-001..A-009, attaching the Section 151
    note where the Part 9 gateway applies.
  - Re-applies the Risk / Status / Level dropdowns.
  - Runs validate_obligation() over every row and prints any warnings so you can
    see at a glance whether the register meets the Part 5 "mature tracker" bar.

It does NOT touch the Intelligence sheet or your scraper ledger. The Dashboard
is left to build_dashboard.py. Close the workbook in Excel before running.
"""

from __future__ import annotations

import sys

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from audit_logic import action_coverage_warnings, validate_obligation
from sheet_format import format_data_sheet
from tracker_data import (
    ACTION_COLUMNS,
    ACTIONS,
    OBLIGATION_COLUMNS,
    OBLIGATION_LEVELS,
    OBLIGATIONS,
)

WORKBOOK = "AuditTracker.xlsx"


def _clear_data_rows(ws):
    """Delete everything below the header row."""
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)


def _ensure_headers(ws, columns):
    """Make sure row 1 matches the wanted column list, in order."""
    for idx, name in enumerate(columns, start=1):
        ws.cell(row=1, column=idx, value=name)


def _header_index(ws, name):
    for c in range(1, ws.max_column + 1):
        if ws.cell(1, c).value == name:
            return c
    return None


def _actions_by_obligation():
    """Reverse the Parent Obligation ID link so each obligation lists its actions."""
    mapping: dict[str, list[str]] = {}
    for ac in ACTIONS:
        parent = ac.get("Parent Obligation ID")
        if parent:
            mapping.setdefault(parent, []).append(ac["Action ID"])
    return {k: ", ".join(sorted(v)) for k, v in mapping.items()}


def write_obligations(ws):
    _ensure_headers(ws, OBLIGATION_COLUMNS)
    _clear_data_rows(ws)
    linked = _actions_by_obligation()
    for ob in OBLIGATIONS:
        row = dict(ob)
        row["Linked Actions"] = linked.get(ob["Obligation ID"], "")
        ws.append([row.get(col, "") for col in OBLIGATION_COLUMNS])

    # Re-running this script would otherwise stack a fresh copy of each dropdown
    # on top of the previous run's, leaving stale ranges behind after a column
    # move. Clear them first so only the ones added below survive.
    ws.data_validations.dataValidation = []

    # Re-apply dropdowns on the right columns (recomputed, so they stay correct
    # even though Obligation Level was appended).
    risk_col = get_column_letter(_header_index(ws, "Risk Rating"))
    status_col = get_column_letter(_header_index(ws, "Status"))
    level_col = get_column_letter(_header_index(ws, "Obligation Level"))

    risk_dv = DataValidation(type="list", formula1='"High,Medium,Low"', allow_blank=True)
    status_dv = DataValidation(
        type="list",
        formula1='"Not started,In progress,Complete,Blocked,Ongoing"',
        allow_blank=True,
    )
    level_dv = DataValidation(
        type="list", formula1=f'"{",".join(OBLIGATION_LEVELS)}"', allow_blank=True
    )
    for dv, col in ((risk_dv, risk_col), (status_dv, status_col), (level_dv, level_col)):
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}500")

    # Widen the new column a touch.
    ws.column_dimensions[level_col].width = 14


def write_actions(ws):
    _ensure_headers(ws, ACTION_COLUMNS)
    _clear_data_rows(ws)
    for ac in ACTIONS:
        ws.append([ac.get(col, "") for col in ACTION_COLUMNS])

    status_dv = DataValidation(
        type="list",
        formula1='"Not started,In progress,Complete,Blocked,Cancelled"',
        allow_blank=True,
    )
    ws.add_data_validation(status_dv)
    status_dv.add("G2:G1000")


def _read_rows(ws):
    headers = [c.value for c in ws[1]]
    return [
        dict(zip(headers, row))
        for row in ws.iter_rows(min_row=2, values_only=True)
        if any(row)
    ]


def report_validation(ws):
    issues = 0
    print("\nValidation against Guide Parts 5, 10 and 13 (role / maturity check):")
    for record in _read_rows(ws):
        warnings = validate_obligation(record)
        for w in warnings:
            print(f"  - {w}")
            issues += 1
    if issues == 0:
        print("  All obligations pass: owners recognised, dates/evidence present.")
    else:
        print(f"  {issues} item(s) to tidy (expected for trigger-pending rows like OB-L6).")


def report_action_coverage(ob_ws, ac_ws):
    """Policy 4/6: every live obligation must carry at least one action row."""
    warnings = action_coverage_warnings(_read_rows(ob_ws), _read_rows(ac_ws))
    print("\nAction coverage (every live obligation needs an executable action):")
    if not warnings:
        print("  Full coverage: every live obligation has at least one action row.")
        return
    for w in warnings:
        print(f"  - {w}")
    print(f"  {len(warnings)} obligation(s) without an action — the suggested "
          f"actions above can be pasted into the Actions tab and refined.")


def main():
    try:
        wb = load_workbook(WORKBOOK)
    except FileNotFoundError:
        print(f"'{WORKBOOK}' not found. Run setup_tracker.py first.")
        sys.exit(1)
    except PermissionError:
        print(f"Cannot open '{WORKBOOK}'. It is probably open in Excel. Close it and run again.")
        sys.exit(1)

    write_obligations(wb["Obligations"])
    write_actions(wb["Actions"])

    # Rows were just rewritten, so the table treatment has to go back on.
    format_data_sheet(wb["Obligations"])
    format_data_sheet(wb["Actions"])
    if "Intelligence" in wb.sheetnames:
        format_data_sheet(wb["Intelligence"])

    try:
        wb.save(WORKBOOK)
    except PermissionError:
        print(f"Cannot save '{WORKBOOK}'. Close it in Excel and run again.")
        sys.exit(1)

    print(f"Wrote {len(OBLIGATIONS)} obligations and {len(ACTIONS)} actions to {WORKBOOK}.")
    report_validation(wb["Obligations"])
    report_action_coverage(wb["Obligations"], wb["Actions"])
    print("\nNow run run_build_dashboard.bat to refresh the Dashboard.")


if __name__ == "__main__":
    main()
