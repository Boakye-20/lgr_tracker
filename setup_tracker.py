"""
Run this ONCE to create the tracker workbook.

It builds AuditTracker.xlsx with four sheets:
    Intelligence  - the auto-updated feed of new legislation and guidance
    Obligations   - what NCC must do (you maintain this by hand)
    Actions       - what has been done against each obligation (you maintain this)
    Dashboard     - live counts and charts that update themselves

After running this once, you never run it again unless you want to start over.
From then on you run update_intelligence.py weekly and build_report.py monthly.
"""

from __future__ import annotations

import os

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# ---- where the workbook should be created -----------------------------------
# Change this to wherever you want the file. Leaving it as the current folder
# is fine; you can move the file afterwards.
OUTPUT_PATH = "AuditTracker.xlsx"

# Nottingham City Council brand-ish colours for headers
HEADER_FILL = PatternFill("solid", fgColor="00205B")  # deep blue
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE_FONT = Font(color="00205B", bold=True, size=16)
SUBTLE = Font(color="666666", italic=True, size=9)


def _style_header(ws, headers, freeze=True):
    for col_index, heading in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_index, value=heading)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 28
    if freeze:
        ws.freeze_panes = "A2"


def _set_widths(ws, widths):
    for col_index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(col_index)].width = width


def build_intelligence(ws):
    # Matched column sits between Material and Theme so an auditor can see
    # immediately WHY an item was flagged, not just that it was.
    # e.g. Material=Yes, Matched="Local, Audit"
    # Action Signal must stay LAST — the scraper appends rows positionally and
    # flags obligation-language items there (see update_intelligence.py).
    headers = [
        "Date Found", "Title", "Source", "Category", "Published",
        "Material", "Matched", "Theme", "URL", "Reviewed", "Notes", "Hash",
        "Action Signal",
    ]
    _style_header(ws, headers)
    _set_widths(ws, [12, 60, 14, 18, 12, 10, 20, 26, 50, 10, 30, 34, 26])

    # Reviewed dropdown (now column J, not I, because Matched was inserted)
    reviewed_validation = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    ws.add_data_validation(reviewed_validation)
    reviewed_validation.add("J2:J2000")

    # Hide the Hash column (now column L)
    ws.column_dimensions["L"].hidden = True


def build_obligations(ws):
    # Column layout and seed content come from tracker_data.py so a fresh build
    # and a live refresh (populate_tracker.py) never drift apart.
    from tracker_data import OBLIGATION_COLUMNS, OBLIGATION_LEVELS, OBLIGATIONS

    headers = list(OBLIGATION_COLUMNS)
    _style_header(ws, headers)
    _set_widths(ws, [13, 50, 30, 22, 18, 12, 13, 14, 30, 30, 16, 13, 30, 14])

    # Find the dropdown columns by name so they stay correct even though
    # "Obligation Level" is appended after Notes.
    risk_col = get_column_letter(headers.index("Risk Rating") + 1)
    status_col = get_column_letter(headers.index("Status") + 1)
    level_col = get_column_letter(headers.index("Obligation Level") + 1)

    risk_validation = DataValidation(type="list", formula1='"High,Medium,Low"', allow_blank=True)
    status_validation = DataValidation(
        type="list", formula1='"Not started,In progress,Complete,Blocked,Ongoing"', allow_blank=True
    )
    level_validation = DataValidation(
        type="list", formula1=f'"{",".join(OBLIGATION_LEVELS)}"', allow_blank=True
    )
    for dv, col in (
        (risk_validation, risk_col),
        (status_validation, status_col),
        (level_validation, level_col),
    ):
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}500")

    # Seed the full OB-A1..A11 + OB-L1..L6 obligation set (Guide Part 7).
    for ob in OBLIGATIONS:
        ws.append([ob.get(col, "") for col in OBLIGATION_COLUMNS])


def build_actions(ws):
    headers = [
        "Action ID", "Parent Obligation ID", "Action", "Owner",
        "Start Date", "Due Date", "Status", "Percent Complete",
        "Evidence Link", "Notes",
    ]
    _style_header(ws, headers)
    _set_widths(ws, [12, 18, 50, 18, 12, 12, 14, 14, 40, 30])

    status_validation = DataValidation(
        type="list", formula1='"Not started,In progress,Complete,Blocked,Cancelled"', allow_blank=True
    )
    ws.add_data_validation(status_validation)
    status_validation.add("G2:G1000")


def build_dashboard(ws, obligations_ws_name="Obligations", intel_ws_name="Intelligence"):
    ws.sheet_view.showGridLines = False
    ws["B2"] = "NCC Audit Reform and LGR Obligations Tracker"
    ws["B2"].font = TITLE_FONT
    ws["B3"] = "Live summary. Figures update automatically when you open the file."
    ws["B3"].font = SUBTLE

    # Summary counts driven by formulas so they always reflect the live data
    ws["B5"] = "Obligations by status"
    ws["B5"].font = Font(bold=True, size=12, color="00205B")

    statuses = ["Not started", "In progress", "Complete", "Blocked", "Ongoing"]
    ws["B6"] = "Status"
    ws["C6"] = "Count"
    ws["B6"].font = Font(bold=True)
    ws["C6"].font = Font(bold=True)
    for i, status in enumerate(statuses, start=7):
        ws[f"B{i}"] = status
        ws[f"C{i}"] = f'=COUNTIF({obligations_ws_name}!H:H,"{status}")'

    # Obligations by risk
    ws["E5"] = "Obligations by risk"
    ws["E5"].font = Font(bold=True, size=12, color="00205B")
    risks = ["High", "Medium", "Low"]
    ws["E6"] = "Risk"
    ws["F6"] = "Count"
    ws["E6"].font = Font(bold=True)
    ws["F6"].font = Font(bold=True)
    for i, risk in enumerate(risks, start=7):
        ws[f"E{i}"] = risk
        ws[f"F{i}"] = f'=COUNTIF({obligations_ws_name}!F:F,"{risk}")'

    # Intelligence headline numbers
    ws["B15"] = "Intelligence feed"
    ws["B15"].font = Font(bold=True, size=12, color="00205B")
    ws["B16"] = "Total items captured"
    ws["C16"] = f'=COUNTA({intel_ws_name}!B:B)-1'
    ws["B17"] = "Flagged Material = Yes"
    ws["C17"] = f'=COUNTIF({intel_ws_name}!F:F,"Yes")'
    ws["B18"] = "Awaiting review"
    ws["C18"] = f'=COUNTIF({intel_ws_name}!I:I,"")-1-COUNTIF({intel_ws_name}!I:I,"No")'

    # Status bar chart
    status_chart = BarChart()
    status_chart.title = "Obligations by status"
    status_chart.height = 7
    status_chart.width = 12
    data = Reference(ws, min_col=3, min_row=6, max_row=11)
    cats = Reference(ws, min_col=2, min_row=7, max_row=11)
    status_chart.add_data(data, titles_from_data=True)
    status_chart.set_categories(cats)
    status_chart.legend = None
    ws.add_chart(status_chart, "B21")

    # Risk pie chart
    risk_chart = PieChart()
    risk_chart.title = "Obligations by risk"
    risk_chart.height = 7
    risk_chart.width = 12
    rdata = Reference(ws, min_col=6, min_row=6, max_row=9)
    rcats = Reference(ws, min_col=5, min_row=7, max_row=9)
    risk_chart.add_data(rdata, titles_from_data=True)
    risk_chart.set_categories(rcats)
    ws.add_chart(risk_chart, "E21")

    _set_widths(ws, [3, 26, 10, 3, 12, 10])


def main():
    if os.path.exists(OUTPUT_PATH):
        print(f"'{OUTPUT_PATH}' already exists. Delete or rename it first if you really want to rebuild from scratch.")
        return

    wb = Workbook()
    intel = wb.active
    intel.title = "Intelligence"
    build_intelligence(intel)

    build_obligations(wb.create_sheet("Obligations"))
    build_actions(wb.create_sheet("Actions"))
    build_dashboard(wb.create_sheet("Dashboard"))

    # Put Dashboard first so it is what people see when they open the file
    wb.move_sheet("Dashboard", -(len(wb.sheetnames) - 1))

    wb.save(OUTPUT_PATH)
    print(f"Created '{OUTPUT_PATH}' with sheets: {wb.sheetnames}")
    print("Five seed obligations added. Open the file and assign owners and target dates.")


if __name__ == "__main__":
    main()
